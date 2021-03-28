from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.cache import caches

from website.helpers import util, geo, encounter
from website.helpers.json_api import reqArgs, jsonResponse, errResponse

from website.cache.cache import storeUserPosition, retrieveUserPosition, beginProcessingPoints, retrieveProcessedPoints, humanList, storeUserCapture, retrieveUserCapture
from website.cache import race_event_cache, position
from website.models import Activity, DevicePoint, Device, Capture, Friendship, Human, BlackoutZone, Encounter, EncounterCount
from website.models.common import Visibility, FriendshipEnum

import json, datetime, time, re, pytz


@csrf_exempt
@reqArgs( sess_req=[('usr', dict),
                    ],
          post_req=[
              ('device_uid', str),
              ('activity', str),
              ('positions', list),
              ('visibility', str),
          ],
          post_opt=[
              ('capture_uid', str),
              ('capture_dist', int),
              ('capture_start_ts', int),
              ('capture_finish_ts', int),
              ('capture_elv_gain', int),
              ('capture_elv_drop', int),
              ('capture_max_spd', float),
              ('capture_time_stopped', int),
          ]
          )
def store( request, usr, capture_uid, device_uid, activity, positions, visibility,
           capture_dist, capture_start_ts, capture_finish_ts,
           capture_elv_gain=None, capture_elv_drop=None, capture_max_spd=None, capture_time_stopped=None,
           *args, **kwargs ):
    return micro_service_save_points( request, usr, capture_uid, device_uid, activity, positions, visibility,
                                      capture_dist, capture_start_ts, capture_finish_ts,
                                      capture_elv_gain, capture_elv_drop, capture_max_spd, capture_time_stopped )


@csrf_exempt
@reqArgs( sess_req=[('usr', dict),
                    ],
          post_req=[
              ('device_uid', str),
              ('activity', str),
              ('positions', list),
              ('visibility', str),
          ],
            post_opt=[
                ('capture_uid', str),
            ]
          )
def backfill( request, usr, capture_uid, device_uid, activity, positions, visibility, *args, **kwargs ):
    return save_points( request, False, usr, capture_uid, device_uid, activity, positions, visibility )


# Run the actual save points logic
def micro_service_save_points(   request, usr, capture_uid, device_uid, activity, positions, visibility,
                                 capture_dist=None, capture_start_ts=None, capture_finish_ts=None,
                                 capture_elv_gain=None, capture_elv_drop=None, capture_max_spd=None, capture_time_stopped=None ):

    # Store the points, if this fails with null, cache is missing, do normal store
    info, err = position.storePoints( usr, capture_uid, activity, positions, visibility,
                                      capture_dist,
                                      capture_start_ts, capture_finish_ts,
                                      capture_elv_gain, capture_elv_drop,
                                      capture_max_spd, capture_time_stopped )
    if info is None and err is None:
        return save_points(request, True, usr, capture_uid, device_uid, activity,
                           positions, visibility,
                           capture_dist, capture_start_ts, capture_finish_ts,
                           capture_elv_gain, capture_elv_drop, capture_max_spd,
                           capture_time_stopped)

    # We had a cache miss
    if err is not None:
        # Load the cache for this user
        position.storeInit(usr, visibility, capture_uid, device_uid )

        # Attempt to store from the recovery
        info, err = position.storePoints(usr, capture_uid, activity, positions,
                                         visibility,
                                         capture_dist,
                                         capture_start_ts, capture_finish_ts,
                                         capture_elv_gain, capture_elv_drop,
                                         capture_max_spd, capture_time_stopped)
        if info is None or err is not None:
            return save_points(request, True, usr, capture_uid, device_uid,
                               activity,
                               positions, visibility,
                               capture_dist, capture_start_ts,
                               capture_finish_ts,
                               capture_elv_gain, capture_elv_drop,
                               capture_max_spd,
                               capture_time_stopped)

    # Remove invalid points
    for idx in reversed(range(len(positions))):
        if info['valid'][idx] == 0:
            del positions[idx]

    # Is there any data left?
    if len(positions) <= 0:
        return jsonResponse( request, {'count': 0, 'singles': [], 'ranges': [] } )

    # Is my activity id invalid?
    if info['activity_id'] <= 0:
        info['activity_id'] = position.storeActivity( usr['uid'], activity )

    # Iterate through all the points
    points = []
    sequence = []
    for pos in positions:
        p = DevicePoint(
            device_id=info['device_id'],
            activity_id=info['activity_id'],
            capture_id=info['capture']['id'] if info['capture']['id'] > 0 else None,
            lat=util.xfloat(pos['lat']),
            lng=util.xfloat(pos['lng']),
            elv=util.xfloat(pos['elv']),
            spd=util.xfloat(pos['spd']),
            dist=util.xfloat(pos['dist']),
            seq=util.xint(pos['seq']),
            battery=util.xint(pos['battery']),
            head=util.xfloat(pos['head']),
            timestamp=util.unixToTime( pos['ts'] ) )

        # Store the sequence
        sequence.append( p.seq )

        points.append(p)
        if len(points) >= 128:
            DevicePoint.objects.bulk_create( points )
            points = []

    # Clean up insertion
    if len(points) > 0:
        DevicePoint.objects.bulk_create( points )

    # Update the capture?
    if 'uid' in info['capture'] and util.xstr( info['capture']['uid']) != "":
        if (vis_enum := Visibility.fromStr(visibility)) < 0:
            return None, "Invalid visibility: %s" % visibility

        cap = info['capture']

        # Create my cache update
        cap_keys = ('dist', 'elv_gain', 'elv_drop', 'max_spd', 'time_stopped')
        cap_hash = {key: cap[key] for key in cap_keys}
        cap_hash['start_ts'] = util.unixToTime(cap['start_ts'])
        cap_hash['finish_ts'] = util.unixToTime(cap['finish_ts'])
        cap_hash['visibility'] = vis_enum

        # If the visibility is different, we need to change any encounters that point to me
        if info['visibility_changed']:
            Encounter.objects.filter( source_id=cap['id'] ).update(visibility=vis_enum)

        # run the encounter logic now
        encounter_count, media_update_on = encounter.exec_encounters( cap, positions )
        if encounter_count > 0:
            cap_hash['encounter_count'] = cap['encounter_count'] + encounter_count
            cap_hash['media_update_on'] = media_update_on

        # Save the capture with just an update, don't overwrite all fields
        Capture.objects.filter(id=cap['id']).update( **cap_hash )

    return jsonResponse( request, {'count': len(positions), 'singles': sequence, 'ranges': [] } )


# Run the actual save points logic
def save_points( request, save_cache, usr, capture_uid, device_uid, activity, positions, visibility,
                 capture_dist=None, capture_start_ts=None, capture_finish_ts=None,
                 capture_elv_gain=None, capture_elv_drop=None, capture_max_spd=None, capture_time_stopped=None ):
    vis_enum = Visibility.fromStr(visibility)
    if vis_enum < 0:
        return errResponse( request, "Invalid visibility: %s" % visibility )

    # Setup my bulk call
    use_bulk = False
    if 'default' in settings.DATABASES:
        use_bulk = (settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql')

    # Ensure there are data points
    if len(positions) <= 0:
        return errResponse( request, "No data points found to store")

    # Is the activity empty?
    activity = Activity.cleanName( activity )
    if not Activity.isNameValid( activity ):
        return errResponse( request, "Invalid activity type.")

    # Handle activity
    act = Activity.getByName(activity)
    if act is None:
        act = Activity.objects.create(name=activity, desc="")

    # Ensure this device is registered
    device = Device.getByUid(device_uid)
    if device is None:
        print("Couldn't find device: %s" % device_uid)
        return errResponse( request, "Couldn't find device")
    device_id = int(device.id)

    # Handle pull the capture
    capture = None
    if util.xstr(capture_uid) != "":
        # Grab the capture
        if (capture := Capture.getByUid(capture_uid)) is None:
            return errResponse(request, "Couldn't find capture")

        if not capture.isOwnedBy( usr['id'] ):
            return errResponse( request, "No access to this capture" )

    # If the user doesn't want to store any points, then quit out now
    if vis_enum == Visibility.INCOGNITO and capture is None:
        return jsonResponse( request, {'count': 0, 'singles': [], 'ranges': [] } )

    # Sort the positions
    positions.sort(key=lambda x: util.xint(x['ts']))
    db_pos = [x.toJson() for x in DevicePoint.objects.filter(
        capture=capture,
        device_id=device_id,
        timestamp__gte=util.unixToTime( positions[0]['ts'] ),
        timestamp__lte=util.unixToTime( positions[-1]['ts'] ))]
    db_pos.sort(key=lambda x: util.xint(x['ts']))

    # Delete any duplicates
    pos_idx = 1
    while pos_idx < len(positions):
        if positions[pos_idx-1]['ts'] == positions[pos_idx]['ts']:
            del positions[pos_idx-1]
        else:
            pos_idx += 1

    # Delete any already existing entries
    pos_idx = 0
    db_idx = 0
    while pos_idx < len(positions) and db_idx < len(db_pos):
        if 'ts' not in positions[pos_idx]:
            return errResponse(request, "Invalid point struct, missing: ts")

        # Move the DB points forward
        if db_pos[db_idx]['ts'] < positions[pos_idx]['ts']:
            db_idx += 1
            continue

        # Delete any points that already exist
        if db_pos[db_idx]['ts'] == positions[pos_idx]['ts'] and \
           db_pos[db_idx]['seq'] == positions[pos_idx]['seq']:
            del positions[pos_idx]
        else:
            pos_idx += 1

    # Is everything overlapping?
    if len(positions) <= 0:
        return jsonResponse( request, {'count': 0, 'singles': [], 'ranges': [] } )


    # Iterate through all the points
    points = []
    dataset = []
    sequence = []
    newest_ts = None
    for pos in positions:
        for key in ['lat', 'lng', 'elv', 'spd', 'dist', 'seq', 'battery', 'head', 'ts']:
            if key not in pos:
                return errResponse(request, "Invalid point struct, missing: %s" % key)
        p = DevicePoint(
            device_id=device_id,
            activity=act,
            capture=capture,
            lat=util.xfloat(pos['lat']),
            lng=util.xfloat(pos['lng']),
            elv=util.xfloat(pos['elv']),
            spd=util.xfloat(pos['spd']),
            dist=util.xfloat(pos['dist']),
            seq=util.xint(pos['seq']),
            battery=util.xint(pos['battery']),
            head=util.xfloat(pos['head']),
            timestamp=util.unixToTime( pos['ts'] ) )
        dataset.append( p.toJson() )

        # Store the sequence
        sequence.append( p.seq )

        # Get the newest timestamp
        if newest_ts is None or newest_ts < p.timestamp:
            newest_ts = p.timestamp

        # Ideal method, much faster
        if use_bulk:
            points.append(p)
            if len(points) >= 128:
                DevicePoint.objects.bulk_create( points )
                # for entry in DevicePoint.objects.bulk_create(points):
                    # dataset.append( { 'id': int(entry.id), **entry.toJson()})
                points = []

        # Slow, but only postgres can handle id returns on bulk inserts
        else:
            p.save()
            # id = util.xint(p.id)
            # dataset.append( {'id': id, **p.toJson()} )

    # Clean up insertion
    if len(points) > 0:
        DevicePoint.objects.bulk_create( points )
        # for entry in DevicePoint.objects.bulk_create(points):
            # dataset.append( { 'id': int(entry.id), **entry.toJson()})

    # Update the capture?
    if capture is not None:
        # Update the finish timestamp if there is something newer, don't allow future
        if newest_ts is not None and (capture.finish_ts is None or capture.finish_ts < newest_ts):
            if newest_ts <= util.timeNow():
                capture.finish_ts = newest_ts
            else:
                capture.finish_ts = util.timeNow()

        # If the visibility is different, we need to change any encounters that point to me
        if capture.visibility != vis_enum:
            capture.visibility = vis_enum
            for enc in Encounter.objects.filter( source_id=capture.id ):
                enc.visibility = vis_enum
                enc.save()

        # Update the capture
        if capture_dist is not None:
            capture.dist = capture_dist
        else:
            capture.calculateDistance()
        if capture_start_ts is not None:
            capture.start_ts = util.unixToTime(capture_start_ts)
        if capture_finish_ts is not None:
            capture.finish_ts = util.unixToTime(capture_finish_ts)
        if capture_elv_gain is not None:
            capture.elv_gain = capture_elv_gain
        if capture_elv_drop is not None:
            capture.elv_drop = capture_elv_drop
        if capture_max_spd is not None:
            capture.max_spd = capture_max_spd
        if capture_time_stopped is not None:
            capture.time_stopped = capture_time_stopped

        # run the encounter logic now
        cap_hash = {
            'id': util.xint(capture.id),
            'human_id': util.xint(capture.human_id),
            'visibility_code': util.xint(capture.visibility),
        }
        encounter_count, media_update_on = encounter.exec_encounters(cap_hash, positions )
        if encounter_count > 0:
            capture.encounter_count += encounter_count
            capture.media_update_on = media_update_on
        capture.save()

        # Save the capture into cache
        if save_cache:
            storeUserCapture( usr['id'], capture.toJson() )

    # Calculate the users positions based on the courses
    if save_cache:
        # Grab all zones
        zones = []
        for x in BlackoutZone.objects.filter(human_id=usr['id']):
            zones.append( (x, geo.GeoBox.box( x.lat, x.lng, x.radius)) )

        # Delete out points that are inside the blackout zone of the user
        if len(zones) > 0:
            for i in reversed(range(0, len(dataset) - 1)):
                for zone, box in zones:
                    if box.contains(dataset[i]['lat'], dataset[i]['lng']) and \
                       zone.radius >= geo.distance(dataset[i]['lat'], dataset[i]['lng'], zone.lat, zone.lng):
                        del dataset[i]
                        break

        # Store the cache points
        if len(dataset) > 0:
            storeUserPosition( usr['id'], dataset, 8 )

    return jsonResponse( request, {'count': len(positions), 'singles': sequence, 'ranges': [] } )


@csrf_exempt
@reqArgs( sess_req=[('usr', dict),
                    ],
          post_req=[
              ('capture_uid', str),
              ('positions', list),
              ('visibility', str),
          ],
          )
def detect_encounters(request, usr, capture_uid, positions, visibility, *args, **kwargs ):
    if (vis := Visibility.fromStr(visibility)) < 0:
        return errResponse( request, "Invalid visibility" )

    # Ensure this capture is registered
    if (capture := Capture.getByUid(capture_uid)) is None:
        return errResponse( request, "Couldn't find capture")

    # Ensure the points are valid
    for pos in positions:
        for key in ['lat', 'lng', 'ts']:
            if key not in pos:
                return errResponse( request, "Invalid point structure")

    # run the encounter logic now
    cap_hash = {
        'id': util.xint(capture.id),
        'human_id': util.xint(capture.human_id),
        'visibility_code': util.xint(capture.visibility),
    }
    encounter_count, media_update_on = encounter.exec_encounters(cap_hash, positions )
    if encounter_count > 0:
        capture.encounter_count += encounter_count
        capture.media_update_on = media_update_on
        capture.save()

    return jsonResponse( request, {} )


@csrf_exempt
@reqArgs( sess_opt=[('usr', dict)],
          post_req=[
              ('lat', float),
              ('lng', float),
              ('area', float),
            ],
          post_opt=[
              ('human_uid', str),
          ]
          )
def retrieve_everyone( request, usr, lat, lng, area, human_uid, *args, **kwargs ):
    requester_uid = util.xstr(usr['uid']) if usr is not None else ""
    if (result := position.retrieveEveryone( requester_uid, human_uid, lat, lng, area)) is not None:
        return jsonResponse( request, result )

    print("Running slow old method")
    cap = {}
    if util.xstr(human_uid) != "":
        human = Human.getByUid(human_uid)
        if human is not None:
            cap = retrieveUserCapture( human.id )

    # grab recent points from this radius
    entries = []
    for human in humanList():
        points = retrieveUserPosition( human['id'] )
        if len(points) <= 0:
            continue

        #Store the results
        entries.append( {'human_uid': human['uid'],
                         'username': human['username'],
                         'points': points[:8] } )

    #Update the cache
    return jsonResponse( request, {'entries': entries, 'capture': cap} )


@csrf_exempt
@reqArgs( sess_opt=[('usr', dict)],
          post_req=[
              ('race_event_uid', str),
            ],
          post_opt=[
              ('human_uid', str),
          ])
def retrieve_race_event( request, usr, race_event_uid, human_uid, *args, **kwargs ):
    requester_uid = util.xstr(usr['uid']) if usr is not None else ""
    if (result := position.retrieveRaceTeam( requester_uid, human_uid, race_event_uid)) is not None:
        return jsonResponse( request, result )

    print("Running slow old method")
    cap = {}
    if human_uid is not None:
        human = Human.getByUid(human_uid)
        if human is not None:
            cap = retrieveUserCapture( human.id )

    # grab recent points from this radius
    entries = []
    for race_team in race_event_cache.raceTeamList( race_event_uid ):
        points = retrieveUserPosition( race_team['human_id'] )
        if len(points) <= 0:
            continue

        entries.append( {'human_uid': race_team['human_uid'],
                         'username': race_team.human['name'],
                         'analysis': [],
                         'points': points[:8] } )

    #Update the cache
    return jsonResponse( request, {'entries': entries, 'capture': cap} )


#@csrf_exempt
#@reqArgs( sess_req=[('usr', dict),
#                    ],
#          )
#def retrieve_friends( request, usr, *args, **kwargs ):
#    # grab recent points from this radius
#    result = []
#    for f in Friendship.objects.filter(source_id=usr['id']):
#        points = retrieveUserPosition( f.target_id )
#        if len(points) <= 0:
#            continue
#
#        #for i in range(1, len(points)):
#        #    if points[i - 1]['ts'] >= points[i]['ts']:
#        #        print("Invalid order")
#
#        # Get the analysis
#        analysis = []
#        #if len(points) > 0:
#        #    analysis = [x.toJson() for x in Analysis.objects.filter(capture=cap)]
#
#        #Store the results
#        result.append( {'radius_uid': str(f.target.uid), 'analysis': [], 'points': points[:8] } )
#
#    #Update the cache
#    return jsonResponse( request, {'entries': result} )


@csrf_exempt
@reqArgs( sess_req=[('usr', dict),
                    ],
          post_req=[
              ('human_uid', str),
            ]
          )
def retrieve_captures( request, usr, human_uid, *args, **kwargs ):
    if (human := Human.getByUid(human_uid)) is None:
        return errResponse( request, "Couldn't find radius")

    # check if we have access
    if not Friendship.getByConnection(target_id=human.id, source_id=usr['id'], friendship=(FriendshipEnum.INNER_CIRCLE, FriendshipEnum.FRIEND)):
        return errResponse(request, "You don't have access to download these captures")

    # grab recent points from this radius
    entries = []
    for cap in human.capture_set.filter(completed=False):
        points = [p.toJson() for p in cap.devicepoint_set.order_by('-timestamp')[:8]]

        #Get the analysis
        analysis = []
        if len(points) > 0:
            pass#analysis = [x.toJson() for x in Analysis.objects.filter(capture=cap)]

        #Store the results
        entries.append( {'capture_uid': str(cap.uid), 'analysis': analysis, 'points': points } )

    #Update the cache
    return jsonResponse( request, {'entries': entries} )


#@csrf_exempt
#@reqArgs( sess_req=[('usr', dict)],
#          post_req=[
#              ('human_uid', str),
#            ]
#          )
#def retrieve_user( request, usr, human_uid, *args, **kwargs ):
#    if (human := Human.getByUid(human_uid)) is None:
#        return errResponse( request, "Couldn't find radius")
#
#    # check if we have access
#    if not Friendship.getByConnection(target_id=human.id, source_id=usr['id'], friendship=(FriendshipEnum.INNER_CIRCLE, FriendshipEnum.FRIEND)):
#        return errResponse(request, "You don't have access to download this users info")
#
#    # grab recent points from this radius
#    devices = []
#    for dev in human.device_set.all():
#        points = [p.toJson() for p in DevicePoint.objects.filter(device_id=dev.id).order_by('-timestamp')[:8]]
#        devices.append( {'device_uid': str(dev.uid), 'points': points[:8] } )
#
#    #Update the cache
#    return jsonResponse( request, {'devices': devices} )
