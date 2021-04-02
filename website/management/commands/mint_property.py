from django.core.management.base import BaseCommand
from django.core.cache import caches

from website.models import Human, Land, State
from website.helpers import geo, util

import datetime, pytz, sys, os

class Command(BaseCommand):
    help = 'Load up past captures and calculat encounters'

    def add_arguments(self, parser):
        parser.add_argument('human_uid', type=str)
        parser.add_argument('path_file', type=str)

    # Run the command
    def handle(self, *args, **options):
        if (human := Human.getByUid( options['human_uid'] )) is None:
            print("We need a human to attach all this land to!")
            return

        count = 0
        points = []
        handle = open(options['path_file'], "r")

        # Read all the data in the file, loading up props
        for line in handle.readlines():
            name, lat, lng = line.rstrip().split(',')

            if (state := State.getByName(name)) is None:
                print(f"Creating state: {name}")
                state = State.objects.create(
                    name=name,
                )

            # Add the land, we'll create in bulk for speed
            points.append( Land(
                human=human,
                state=state,
                lat=lat,
                lng=lng,
            ))
            if len(points) >= 1024:
                count += len(points)
                Land.objects.bulk_create( points )
                points = []
                print(count)

        if len(points) > 0:
            count += len(points)
            Land.objects.bulk_create( points )
            points = []

        print("")
        print(f"Minted {count} plots of land")