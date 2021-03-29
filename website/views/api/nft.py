from django.conf import settings
from django.db.models import F, Q
from django.views.decorators.csrf import csrf_exempt

from website.models import Land, Nft
from website.helpers.json_api import reqArgs, jsonResponse, errResponse
from website.helpers import util, s3, geo, fcm

import json, datetime, time, re, pytz, uuid


@csrf_exempt
@reqArgs(sess_req=[('usr', dict)],
         post_req=[
             ('lat', float),
             ('lng', float),
             ('radius', float),
             ('offset', int),
             ('count', int),
         ],
         )
def search_proximity( request, usr, lat, lng, radius, offset, count, *args, **kwargs ):
    # Cap some numbers
    if count > 100:
        count = 100
    if count <= 20:
        count = 20

    if offset < 0:
        offset = 0

    if radius > 15000:
        radius = 15000

    box = geo.GeoBox.box( lat, lng, radius )

    # Get all land
    land_ids = []
    dist_lookup = {}
    for land in Land.objects.filter(lng__range=(box.Left, box.Right),
                                    lat__range=(box.Bottom, box.Top)):
        land_ids.append( int(land.id) )
        dist_lookup[int(land.id)] = geo.distance( land.lat, land.lng, lat, lng )

    # Get and sort all the nfts
    nfts = [x for x in Nft.objects.filter(land_id__in=land_ids).select_related('land')]
    nfts.sort(key=lambda x: dist_lookup[x.land_id] )

    # Cap the result
    count += offset
    return jsonResponse( request, { 'nfts': [x.toJson() for x in nfts[offset:count]] })