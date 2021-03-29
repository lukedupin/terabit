from django.conf import settings
from django.db.models import F, Q
from django.views.decorators.csrf import csrf_exempt

from website.models import Land, Nft
from website.helpers.json_api import reqArgs, jsonResponse, errResponse
from website.helpers import util, s3, geo, fcm

import json, datetime, time, re, pytz, uuid


@csrf_exempt
@reqArgs(sess_opt=[('usr', dict)],
         post_req=[
             ('lat', float),
             ('lng', float),
             ('radius', float),
         ],
         )
def search_proximity( request, usr, lat, lng, radius, *args, **kwargs ):
    if radius > 30000:
        return errResponse( request, "Search area too large" )

    # Get all land, note, this method might might give you answers that are outside the radius
    box = geo.GeoBox.box( lat, lng, radius )
    lands = [x.toJson() for x in Land.objects.filter(lng__range=(box.Left, box.Right),
                                                     lat__range=(box.Bottom, box.Top))]

    return jsonResponse( request, { 'lands': lands })