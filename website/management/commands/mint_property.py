from django.core.management.base import BaseCommand
from django.core.cache import caches

from website.models import Human, Land, State
from website.helpers import geo, util

import datetime, pytz, sys, os, json, time, requests

class Command(BaseCommand):
    help = 'Load up past captures and calculat encounters'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str)

    # Run the command
    def handle(self, *args, **options):
        js = json.loads( open(options['path']).read())

        if (human := Human.getByUsername( js['username'] )) is None:
            print("We need a human to attach all this land to!")
            return

        if (state := State.getByName(js['state_name'])) is None:
            print(f"Creating state: {js['state_name']}")
            state = State.objects.create(name=js['state_name'])

        # Define the names
        lat, lng, name, mode = [js[x] for x in ('lat', 'lng', 'name', 'mode')]
        points = []

        # Skip!?
        skip = {}
        if 'skip' in js:
            for s in js['skip']:
                skip[s] = True

        # Kill other land
        killed = 0
        for kill in Land.objects.filter(name=name, human=human):
            killed += 1
            kill.delete()
        print("Killed: %d" % killed)

        if mode == "grid":
            row, col = [js[x] for x in ('row', 'col')]
            if row & 1 != 1 or col & 1 != 1:
                print("Please make sure row/col are both odd numbers")
                return

            cur_lat, cur_lng = lat, lng
            for _ in range(int(row / 2)):
                cur_lat, cur_lng = geo.distanceBearing( cur_lat, cur_lng, 1000, 180 )

            for _ in range(int(col / 2)):
                cur_lat, cur_lng = geo.distanceBearing( cur_lat, cur_lng, 1000, 90 )

            # Build!
            for _c in range(col):
                tmp_lng = cur_lng
                for _r in range(row):
                    # Skip?
                    rc = f"{_r},{_c}"
                    if rc in skip:
                        print("Skipping %s" % rc)
                        continue

                    points.append( Land(
                        human=human,
                        state=state,
                        status=Land.STATUS_FOR_SALE,
                        name=name,
                        lat=cur_lat,
                        lng=tmp_lng,
                    ))
                    cur_lat, tmp_lng = geo.distanceBearing(cur_lat, tmp_lng, 1000, 270)
                cur_lat, cur_lng = geo.distanceBearing(cur_lat, cur_lng, 1000, 0)


        elif mode in ("up", 'down', 'left', 'right'):
            # Get the direction we are going to move
            dir = 0
            if mode == 'down':
                dir = 180
            elif mode == 'left':
                dir = 90
            elif mode == 'right':
                dir = 270

            dist = js['dist']

            # Start at the start, and behing creating land
            cur_lat, cur_lng = lat, lng
            while geo.distance( lat, lng, cur_lat, cur_lng ) < dist:
                points.append( Land(
                    human=human,
                    state=state,
                    status=Land.STATUS_FOR_SALE,
                    name=name,
                    lat=cur_lat,
                    lng=cur_lng,
                ))

                cur_lat, cur_lng = geo.distanceBearing( cur_lat, cur_lng, 1000, dir )

        else:
            print("Invalid mode, it can be either: vert or horz, up, down, left, right")
            return

        # Ensure this is valid
        lat_bounds = [lat, lat]
        lng_bounds = [lng, lng]
        for point in points:
            if lat_bounds[0] > point.lat:
                lat_bounds[0] = point.lat
            if lat_bounds[1] < point.lat:
                lat_bounds[1] = point.lat

            if lng_bounds[0] > point.lng:
                lng_bounds[0] = point.lng
            if lng_bounds[1] < point.lng:
                lng_bounds[1] = point.lng

        # Update my points
        #lat_bounds[0], _ = geo.distanceBearing( lat_bounds[0], (lng_bounds[0] + lng_bounds[1]) / 2, 1200, 180 )
        #lat_bounds[1], _ = geo.distanceBearing( lat_bounds[1], (lng_bounds[0] + lng_bounds[1]) / 2, 1200, 0 )
        #_, lng_bounds[0] = geo.distanceBearing( (lat_bounds[0] + lat_bounds[1]) / 2, lng_bounds[0], 1200, 270 )
        #_, lng_bounds[1] = geo.distanceBearing( (lat_bounds[0] + lat_bounds[1]) / 2, lng_bounds[1], 1200, 90 )

        # Kill anything that is over water
        if js['check_water']:
            for i in reversed(range(len(points))):
                point = points[i]
                url = "https://api.onwater.io/api/v1/results/%f,%f" % (point.lat, point.lng)
                result = json.loads(requests.get(url).content)
                if 'water' not in result:
                    print("WTF No water")

                elif result['water']:
                    print("Removing %d" % i)
                    points.pop(i)
                else:
                    print("x")

                time.sleep(2)

        # Remove anything that overlaps
        overlap_count = 0
        for overlap in Land.objects.filter(lat__gte=lat_bounds[0],
                                           lat__lte=lat_bounds[1],
                                           lng__gte=lng_bounds[0],
                                           lng__lte=lng_bounds[1]):
            for i in reversed(range(len(points))):
                point = points[i]
                if geo.distance( point.lat, point.lng, overlap.lat, overlap.lng ) <= 1005:
                    overlap_count += 1
                    points.pop(i)

        # Save it!
        print( "Overlap: %d" % overlap_count )
        print( "Saving: %d points" % len(points) )
        Land.objects.bulk_create( points )