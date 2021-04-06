from django.core.management.base import BaseCommand
from django.core.cache import caches

from website.models import Human, Land, State
from website.helpers import geo, util

import datetime, pytz, sys, os, json

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

        if mode == "grid":
            row, col = [js[x] for x in ('row', 'col')]
            if row & 1 != 1 or col & 1 != 1:
                print("Please make sure row/col are both odd numbers")
                return

            cur_lat, cur_lng = lat, lng
            for _ in range(int(row / 2)):
                cur_lat, cur_lng = geo.distanceBearing( cur_lat, cur_lng, 1000, 180 )

            for _ in range(int(col / 2)):
                cur_lat, cur_lng = geo.distanceBearing( cur_lat, cur_lng, 1000, 270 )

            # Build!
            for _c in range(col):
                tmp_lng = cur_lng
                for _r in range(row):
                    Land.objects.create(
                        human=human,
                        state=state,
                        name=name,
                        lat=cur_lat,
                        lng=tmp_lng,
                    )
                    cur_lat, tmp_lng = geo.distanceBearing(cur_lat, tmp_lng, 1000, 90)
                cur_lat, cur_lng = geo.distanceBearing(cur_lat, cur_lng, 1000, 0)


        elif mode in ("up", 'down', 'left', 'right'):
            # Get the direction we are going to move
            dir = 0
            if mode == 'down':
                dir = 180
            elif mode == 'left':
                dir = 270
            elif mode == 'right':
                dir = 90

            dist = js['dist']

            # Start at the start, and behing creating land
            cur_lat, cur_lng = lat, lng
            while geo.distance( lat, lng, cur_lat, cur_lng ) < dist:
                Land.objects.create(
                    human=human,
                    state=state,
                    name=name,
                    lat=cur_lat,
                    lng=cur_lng,
                )

                cur_lat, cur_lng = geo.distanceBearing( cur_lat, cur_lng, 1000, dir )

        else:
            print("Invalid mode, it can be either: vert or horz, up, down, left, right")
            return