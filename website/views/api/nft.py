from django.conf import settings
from django.db.models import F, Q
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt

from website.models import Land, Nft, Human
from website.helpers.json_api import reqArgs, jsonResponse, errResponse
from website.helpers import util, s3, geo, fcm

import json, datetime, time, re, pytz, uuid


@csrf_exempt
@reqArgs(sess_opt=[('usr', dict)],
         post_req=[
             ('human_uid', str),
         ],
         )
def list_( request, usr, human_uid, *args, **kwargs ):
    if (human := Human.getByUid(human_uid)) is None:
        return errResponse( request, "Not a valid user")

    return jsonResponse( request, { 'nfts': [x.toJson() for x in human.nft_set.order_by('created_on')] })


@csrf_exempt
@reqArgs(sess_opt=[('usr', dict)],
         post_req=[
             ('human_uids', list),
         ],
         )
def bulk_list( request, usr, human_uids, *args, **kwargs ):
    human_ids = [int(human.id) for human in Human.objects.filter(uid__in=human_uids)]

    return jsonResponse( request, { 'nfts': [x.toJson() for x in Nft.objects.filter(human_id__in=human_ids).order_by('created_on').select_related('human', 'land')] })


@csrf_exempt
@reqArgs(sess_req=[('usr', dict)],
         post_req=[
             ('address', str),
             ('name', str),
             ('desc', str),
             ('url', str),
             ('img', str),
             ('listing_url', str),
         ],
         post_opt=[
             ('story', str),
         ])
def create( request, usr, address, name, desc, url, img, listing_url, story, *args, **kwargs ):
    if (human := Human.getById(usr['id'])) is None:
        return errResponse( request, "Please login first")

    try:
        nft = Nft.objects.create(
            human=human,
            address=address,
            name=name,
            desc=desc,
            img=img,
            url=url,
            listing_url=listing_url,
            story=story,
        )

    except IntegrityError:
        return errResponse( request, "Duplicate key")

    return jsonResponse( request, nft.toJson() )


@csrf_exempt
@reqArgs(sess_req=[('usr', dict)],
         post_req=[
             ('nfts', list),
         ])
def resync( request, usr, nfts, *args, **kwargs ):
    if (human := Human.getById(usr['id'])) is None:
        return errResponse( request, "Please login first")

    # Get a list of NFTs
    kill_list = {util.xstr(nft.address): nft for nft in human.nft_set.all()}

    # List of Nfts
    result = []
    for nft in nfts:
        # Update them remove from the kill list
        update = None
        if nft['address'] in kill_list:
            update = kill_list[nft['address']]
            del kill_list[nft['address']]

        else:
            update = Nft.getByAddress(nft['address'])

        # Do an update?
        if update is not None:
            update.human = human
            update.name = nft['name']
            update.desc = nft['desc']
            update.img = nft['img']
            update.url = nft['url']
            update.listing_url = nft['listing_url']
            update.save()

            result.append( update.toJson() )

        else:
            x = Nft.objects.create(
                human=human,
                address=nft['address'],
                name=nft['name'],
                desc=nft['desc'],
                img=nft['img'],
                url=nft['url'],
                listing_url=nft['listing_url'],
            )
            result.append( x.toJson() )

    # Delete anything left in the kill list
    #for key in kill_list.keys(): kill_list[key].delete()

    # Update the nft count
    human.nft_count = len(result)
    human.save()

    return jsonResponse( request, { 'nfts': result })


@csrf_exempt
@reqArgs(sess_opt=[('usr', dict)],
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