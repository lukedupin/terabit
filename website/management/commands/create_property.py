from django.core.management.base import BaseCommand
from django.core.cache import caches

from website.models import Human, Land
from website.helpers import geo, util

import datetime, pytz

class Command(BaseCommand):
    help = 'Load up past captures and calculat encounters'

    # Run the command
    def handle(self, *args, **options):
        human = Human.objects.all().first()

        lat = 37.7749
        lng = -122.4194
        status = 0

        for x in range(20):
            dlng = lng
            for y in range(20):
                Land.objects.create(
                    human=human,
                    lat=lat,
                    lng=dlng,
                    status=status + 1
                )
                status = (status + 1) % 3
                dlng = geo.distanceBearing(lat, dlng, 1000, 90)[1]

            lat, lng = geo.distanceBearing(lat, lng, 1000, 0)
