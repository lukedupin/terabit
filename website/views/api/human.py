from django.db import models
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from website.cache import cache
from website.helpers.json_api import reqArgs, jsonResponse, errResponse
from website.models import Activity, Capture, Human, Friendship, Device, common, DeviceGroup, DeviceGroupAccess, Group, RaceEvent, GroupAccess, FriendshipModifier
from website.models.common import FriendshipEnum
from website.helpers import util, geo, s3

import uuid, random, re, os


# generate the access code
def gen_access_code():
    code = ""
    while len(code) < 5:
        value = random.randint(1, 10)
        if value < 10:
            code += "%d" % value

    return code


def reset_push_tokens( human ):
    for dev in Device.objects.filter(human=human):
        dev.push_token = None
        dev.save()

    if (dev := human.getPrimaryDevice()) is not None:
        dev.push_token = None
        dev.save()


@csrf_exempt
@reqArgs( post_req=[ ('username', str),
                     ('email', str),
                     ('phone_number', str),
                     ],
          post_opt=[ ('lat', float),
                     ('lng', float),
                     ('desc', str),
                     ('real_name', str),
                     ('create_device', bool),
                     ('device_name', str),
                     ('push_token', str)
                     ],
        )
def create( request, username, email, phone_number, real_name, create_device,
            desc, lat, lng, device_name, push_token, *args, **kwargs ):
    username = common.cleanName(username)
    if username is None:
        return errResponse(request, "Username cannot be empty")
    if Human.getByUsername( username ) is not None:
        return errResponse( request, "User already exists")

    email = common.cleanEmail(email)
    if email is None:
        return errResponse(request, "Invalid Email")
    if Human.getByEmail( email ) is not None:
        return errResponse( request, "Email already exists")

    phone_number = common.cleanPhoneNumber(phone_number)
    if phone_number is None:
        return errResponse(request, "Phone number must be 10 digits")
    if Human.getByPhoneNumber( phone_number ) is not None:
        return errResponse( request, "Phone number already exists")

    # If no real name was give, just use the username again
    if real_name is None:
        real_name = username

    # Create the human object
    human = Human.objects.create( username=util.xstr( username ),
                                  desc=util.xstr( desc ),
                                  email=util.xstr(email),
                                  phone_number=util.xstr(phone_number),
                                  real_name=util.xstr(real_name),
                                  session=uuid.uuid4(),
                                  lat=util.xfloat(lat),
                                  lng=util.xfloat(lng) )

    # Create a device to?
    device = {}
    if util.xbool(create_device):
        if util.xstr(device_name) == "":
            device_name = "%s's Device" % username
        device_group = DeviceGroup.objects.create(name="%s's Device group" % username)
        DeviceGroupAccess.objects.create( human=human, device_group=device_group )

        device = Device.objects.create( device_group=device_group,
                                        human=human,
                                        name=device_name,
                                        category=Device.CATEGORY_CELL_PHONE,
                                        push_token=push_token ).toJson()

    # Reset the human list
    cache.clearHumanList()

    # Load the user session data
    js_usr = human.toJsonFull()
    request.session['usr'] = { 'id': int(human.id), **js_usr }
    return jsonResponse( request, {'session': str(human.session),
                                   'human': js_usr,
                                   'device': device } )


@csrf_exempt
@reqArgs( sess_req=[('usr', dict)] )
def is_online(request, usr, *args, **kwargs):
    return jsonResponse( request, {} )


@csrf_exempt
@reqArgs( post_req=[
              ('human_uid', str),
              ('session', str),
          ],
          post_opt=[
              ('cell_type', str),
              ('device_uid', str),
          ]
        )
def auth( request, human_uid, session, cell_type, device_uid, *args, **kwargs ):
    if (human := Human.getByUid(human_uid)) is None:
        return errResponse( request, "Couldn't find user", "NOT_FOUND")
    if util.xstr(human.session) != util.xstr(session):
        return errResponse( request, "Invalid session key", "INVALID_SESSION")

    # Is the account blocked?
    if human.blocked:
        return errResponse( request, "Account blocked")

    # Load the user session data
    js_usr = human.toJsonFull()
    request.session['usr'] = { 'id': int(human.id), **js_usr }

    # Is the user wanting to assign a device type?
    if cell_type is not None and device_uid is not None:
        if (cat := Device.getCategoryFromStr( cell_type )) < 0:
            return errResponse( request, "Invalid category code")

        # Should we event update?
        if (device := Device.getByUid( device_uid)) is not None and \
           device.human_id == human.id and device.category != cat:
            device.category = cat
            device.save()

    return jsonResponse( request, js_usr )


@csrf_exempt
@reqArgs( sess_req=[],
          post_req=[
              ('human_uid', str),
              ('session', str),
          ],)
def invalidate_auth( request, human_uid, session, *args, **kwargs ):
    if (human := Human.getBySession(human_uid, session)) is None:
        return errResponse( request, "Couldn't find you?" )

    # Reset the push token
    reset_push_tokens( human )

    # Is the account blocked?
    if human.blocked:
        return errResponse( request, "Account blocked")

    # Create a new session token, that no one knows
    human.session = str(uuid.uuid4())
    human.save()

    return jsonResponse( request, {} )

@csrf_exempt
@reqArgs( sess_req=[],
          post_req=[ ('phone_number', str),
          ],
          )
def generate_recovery_phone_number_auth( request, phone_number, *args, **kwargs ):
    if (human := Human.getByPhoneNumber( phone_number )) is None:
        return errResponse( request, "Couldn't find you?" )

    # Is the account blocked?
    if human.blocked:
        return errResponse( request, "Account blocked")

    # generate the access code
    code = gen_access_code()
    cache.storeRecoveryAccessCode( human.uid, code )

    # Send a text
    if util.sendSms("%s Radius account recovery code" % code, phone_number ) is None:
        return errResponse( request, "Error texting. Try email")
    print("Access code: %s" % code )

    return jsonResponse( request, {} )

@csrf_exempt
@reqArgs( post_req=[ ('phone_number', str),
                     ('access_code', str),
          ],
        )
def recovery_phone_number_auth( request, phone_number, access_code, *args, **kwargs ):
    human = Human.getByPhoneNumber(phone_number)
    if human is None:
        return errResponse( request, "Couldn't find user")

    # Is the account blocked?
    if human.blocked:
        return errResponse( request, "Account blocked")

    # Confirm the access code exists
    code = cache.execRecoveryAccessCode( human.uid )
    if code is None or code != re.sub('[^0-9]', '', access_code):
        print("Invalid access code: %s != %s" % (code, access_code))
        return errResponse( request, "No valid access code found")

    # if this is the first login, increment their login count
    human.session = uuid.uuid4()
    human.save()

    reset_push_tokens( human )

    # Create a device to?
    device = human.getPrimaryDevice()
    device_js = device.toJson() if device is not None else {}

    # Load the user session data
    js_usr = human.toJsonFull()
    request.session['usr'] = { 'id': int(human.id), **js_usr }
    return jsonResponse( request, {'session': str(human.session),
                                   'human': js_usr,
                                   'device': device_js } )

@csrf_exempt
@reqArgs( sess_req=[],
          post_req=[ ('email', str),
          ],
          )
def generate_recovery_email_auth( request, email, *args, **kwargs ):
    human = Human.getByEmail( email )
    if human is None:
        return errResponse( request, "Couldn't find you?" )

    # Is the account blocked?
    if human.blocked:
        return errResponse( request, "Account blocked")

    # generate the access code
    code = gen_access_code()
    cache.storeRecoveryAccessCode( human.uid, code )
    util.sendEmail( email, "Radius account recovery", "Please use this code to recover your account:\n\n%s" % code )
    print("Access code: %s" % code )

    return jsonResponse( request, {} )


@csrf_exempt
@reqArgs( post_req=[ ('email', str),
                     ('access_code', str),
          ],
        )
def recovery_email_auth( request, email, access_code, *args, **kwargs ):
    human = Human.getByEmail(email)
    if human is None:
        return errResponse( request, "Couldn't find user")

    # Is the account blocked?
    if human.blocked:
        return errResponse( request, "Account blocked")

    # Confirm the access code exists
    code = cache.execRecoveryAccessCode( human.uid )
    if code is None or code != re.sub('[^0-9]', '', access_code):
        print("Invalid access code: %s != %s" % (code, access_code))
        return errResponse( request, "No valid access code found")

    # if this is the first login, increment their login count
    human.session = uuid.uuid4()
    human.save()

    reset_push_tokens( human )

    # Create a device to?
    device = human.getPrimaryDevice()
    device_js = device.toJson() if device is not None else {}

    # Load the user session data
    js_usr = human.toJsonFull()
    request.session['usr'] = { 'id': int(human.id), **js_usr }
    return jsonResponse( request, {'session': str(human.session),
                                   'human': js_usr,
                                   'device': device_js } )


@csrf_exempt
@reqArgs( sess_opt=[('usr', dict)],
          post_opt=[ ('username', str),
                     ('email', str),
                     ('phone_number', str),
                     ]
          )
def is_unique( request, usr, username, email, phone_number, *args, **kwargs ):
    result = { 'username': False, 'username_invalid': False,
               'email': False, 'email_invalid': False,
               'phone_number': False, 'phone_number_invalid': False }

    if username is not None:
        if (username := common.cleanName(username)) is not None:
            if usr is not None and 'username' in usr and usr['username'].lower() == util.xstr(username).lower():
                result['username'] = True
            else:
                result['username'] = Human.getByUsername( username ) is None
        else:
            result['username_invalid'] = True

    if email is not None:
        if (email := common.cleanEmail(email)) is not None:
            if usr is not None and 'email' in usr and usr['email'].lower() == util.xstr(email).lower():
                result['email'] = True
            else:
                result['email'] = Human.getByEmail( email ) is None
        else:
            result['email_invalid'] = True

    if phone_number is not None:
        if (phone_number := common.cleanPhoneNumber(phone_number)) is not None:
            if usr is not None and 'phone_number' in usr and usr['phone_number'].lower() == util.xstr(phone_number):
                result['phone_number'] = True
            else:
                result['phone_number'] = Human.getByPhoneNumber( phone_number) is None
        else:
            result['phone_number_invalid'] = True

    return jsonResponse( request, result )


@csrf_exempt
@reqArgs( sess_req=[('usr', dict)],
          post_opt=[
              ('username', str),
              ('desc', str),
              ('real_name', str),
              ('email', str),
              ('phone_number', str),
          ]
        )
def modify( request, usr, username, desc, real_name, email, phone_number, *args, **kwargs ):
    # Load up the user info
    human = Human.getById(usr['id'])
    if human is None:
        return errResponse( request, "Couldn't find a valid user, even though you're logged in...")

    # Is the account blocked?
    if human.blocked:
        return errResponse( request, "Account blocked")

    if username is not None:
        username = common.cleanName(username)
        if human.username != username:
            if Human.getByUsername(username) is not None:
                return errResponse( request, "Username must be unique")
            human.username = username

    if desc is not None:
        human.desc = desc

    if real_name is not None:
        human.real_name = real_name

    if email is not None:
        email = common.cleanEmail(email)
        if human.email != email:
            if email is None or human.getByEmail(email) is not None:
                return errResponse( request, "Email must be unique")
            human.email = email

    if phone_number is not None:
        phone_number = common.cleanPhoneNumber(phone_number)
        if human.phone_number != phone_number:
            if phone_number is None:
                return errResponse(request, "Phone number must be 10 digits")
            if human.getByPhoneNumber(phone_number) is not None:
                return errResponse(request, "Phone number must be unique")
            human.phone_number = phone_number

    # Save out the objects
    human.save()

    return jsonResponse( request, human.toJsonFull() )


@csrf_exempt
@reqArgs( sess_req=[('usr', dict)],
          post_req=[ ('human_uid', str),
              ],
          )
def summary( request, usr, human_uid, *args, **kwargs ):
    if util.xstr(human_uid) == "":
        human_uid = usr['uid']
    if (human := Human.getByUid(human_uid)) is None:
        return errResponse( request, "Couldn't find you?" )

    # Friendship modifier
    friendship_modifier = {}
    if (mod := FriendshipModifier.getByConnection( human.id, usr['id'])) is not None:
        if mod.modifier == FriendshipModifier.MODIFIER_BLOCKED:
            return errResponse( request, "Account blocked")
        friendship_modifier = mod.toJson()

    # Is the account blocked?
    if human.blocked:
        return errResponse( request, "Account blocked")

    # Get the friendship code
    friendship = {}
    friendship_code = FriendshipEnum.FOLLOWING
    if human.id == usr['id']:
        friendship_code = FriendshipEnum.INNER_CIRCLE # I am the same as inner circle, everything!

    elif (friend := Friendship.getByConnection(target_id=human.id, source_id=usr['id'])) is not None:
        friendship = friend.toJson()
        friendship_code = friend.friendship
    privacy_lookup = common.privacyLookup( friendship_code )
    human_privacy = human.getPrivacy()

    # Calc the capture related summary
    capture_count = util.xint( human.capture_set.count() )
    total_dist = util.xfloat( human.capture_set.aggregate(models.Sum('dist'))['dist__sum'])
    group_count = util.xint( human.groupaccess_set.count() )

    # Get the number of friends and followers that I have
    followers_count = Friendship.objects.filter(target_id=human.id).count()
    following_count = Friendship.objects.filter(source_id=human.id).count()
    friend_request_count = FriendshipModifier.objects.filter(target_id=usr['id'], modifier=FriendshipModifier.MODIFIER_FRIEND_REQUEST).count()

    # Pull The user's captures
    captures = []
    if human_privacy.captures in privacy_lookup:
        captures = [x.toJson() for x in human.capture_set.order_by('-start_ts')]

    # Pull the user's groups
    if human_privacy.groups in privacy_lookup:
        grp_ids = [int(x.group_id) for x in human.groupaccess_set.all()]
    else: # Mutual only
        group_lookup = {int(x.group_id) for x in GroupAccess.objects.filter(human_id=usr['id'])}
        grp_ids = [int(x.group_id) for x in human.groupaccess_set.all() if x.group_id in group_lookup]
    grp_type = (Group.TYPE_PUBLIC, Group.TYPE_PRIVATE)
    groups = [x.toJson(False) for x in Group.objects.filter(id__in=grp_ids, type__in=grp_type)]

    # Pull the user's friends
    if human_privacy.friends in privacy_lookup:
        friend_ids = [int(x.target_id) for x in Friendship.objects.filter(source_id=usr['id'])]
    else: # Mutual only
        friend_lookup = {int(x.target_id): True for x in Friendship.objects.filter(source_id=human.id)}
        friend_ids = [int(x.target_id) for x in Friendship.objects.filter(source_id=usr['id']) if x.target_id in friend_lookup]
    friends = [x.toJson() for x in Human.objects.filter(id__in=friend_ids)]

    # Pull the user's posts
    group_posts = []
    if human_privacy.group_posts in privacy_lookup:
        group_posts = [x.toJson() for x in human.grouppost_set.order_by('-timestamp')]

    # get all the user events
    events = []
    if human_privacy.events in privacy_lookup:
        event_ids = [int(x.race_event_id) for x in human.raceteam_set.all()]
        events = [x.toJson() for x in RaceEvent.objects.filter(id__in=event_ids).order_by('-start_ts') if util.timeToUnix(x.start_ts) > (365 * 24 * 3600 * 1000)]

    return jsonResponse( request, {
        "human": human.toJson( friendship_code ),
        "human_privacy": human_privacy.toJson(),
        "group_count": group_count,
        "capture_count": capture_count,
        "total_dist": total_dist,

        "following_count": following_count,
        "followers_count": followers_count,
        "friend_request_count": friend_request_count,

        "friendship": friendship,
        "friendship_modifier": friendship_modifier,

        "captures": captures,
        "groups": groups,
        "friends": friends,
        "group_posts": group_posts,
        "events": events,

        "activity_count": capture_count, # TODO Remove this, its for legacy after 2.1
        "friend_count": followers_count, # TODO Remove this, its for legacy after 2.1.0
    } )

# TODO This should only give toJson() not toJsonFull(), Either remove or reduce access
@csrf_exempt
@reqArgs( sess_req=[('usr', dict)],
          post_req=[('human_uid', str),
                    ]
          )
def desc( request, usr, human_uid, *args, **kwargs ):
    human = Human.getByUid(human_uid)
    if human is None:
        return errResponse(request, "Couldn't find human")

    # Is the account blocked?
    if human.blocked:
        return errResponse( request, "Account blocked")

    # Check access
    if human.id != usr['id'] and \
       Friendship.getByConnection(target_id=human.id,
                                  source_id=usr['id'],
                                  friendship=(FriendshipEnum.INNER_CIRCLE, FriendshipEnum.FRIEND)) is None:
            return errResponse( request, "You don't have access" )

    return jsonResponse( request, human.toJsonFull() )


# TODO This needs to be checking friendship model info
@csrf_exempt
@reqArgs( sess_opt=[('usr', dict)],
          post_req=[('human_uids', list),
                    ]
          )
def bulk_desc( request, usr, human_uids, *args, **kwargs ):
    #friend_ids = [usr['id']]
    #friend_ids += [int(x.target_id) for x in Friendship.objects.filter(source_id=usr['id'], friendship__in=(FriendshipEnum.FRIEND, FriendshipEnum.INNER_CIRCLE))]

    resp = []
    unique = {}
    for uid in human_uids:
        if uid in unique:
            continue
        unique[uid] = True

        # Grab human
        human = None
        if uid == "self" and usr is not None:
            human = Human.getById(usr['id'])
        if human is None:
            human = Human.getByUid(uid)

        # Only allow uids that I have access to
        #print("WARN: human.id not in friends, but allowing download!")
        if human is None:# or human.id not in ~:
            continue

        # Is the account blocked?
        if human.blocked:
            continue

        resp.append( human.toJson() )

    return jsonResponse( request, { "humans": resp })


@csrf_exempt
@reqArgs( sess_req=[('usr', dict)],
          file_req=["img"]
          )
def profile_image( request, usr, img, *args, **kwargs ):
    if (human := Human.getById(usr['id'])) is None:
        return errResponse( request, "Couldn't get user")

    # Is the account blocked?
    if human.blocked:
        return errResponse( request, "Account blocked")

    # Upload to S3
    uid = str(uuid.uuid4())
    filename = "profiles/%s.jpg" % uid
    if not s3.put_data( img.data(), "upload/"+ filename):
        return errResponse( request, "Couldn't upload to S3")

    # Store the profile!
    human.profile_image = filename
    human.save()

    return jsonResponse( request, { "uid": uid, "profile_image": human.getProfileUrl() })


@csrf_exempt
@reqArgs( sess_req=[('usr', dict)],
          )
def alert_count( request, usr, *args, **kwargs ):
    # Friendship requests
    friend_requests = FriendshipModifier.objects.filter(target_id=usr['id'], modifier=FriendshipModifier.MODIFIER_FRIEND_REQUEST).count()

    return jsonResponse( request, { "friend_requests": friend_requests })

