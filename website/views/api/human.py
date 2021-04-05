from django.db import models
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from website.cache import cache
from website.helpers.json_api import reqArgs, jsonResponse, errResponse
from website.models import common, Human, EthAccount
from website.helpers import util, geo, s3

import uuid, random, re, os, subprocess


@csrf_exempt
@reqArgs( post_req=[
              ('public_key', str),
          ],
        )
def generate_nonce( request, public_key, *args, **kwargs ):
    nonce = cache.generateNonce( public_key)

    return jsonResponse( request, { 'nonce': nonce } )


@csrf_exempt
@reqArgs( post_req=[
    ('public_key', str),
    ('signature', str),
],
)
def auth_by_nonce( request, public_key, signature, *args, **kwargs ):
    nonce = cache.takeNonce( public_key )
    cmd = f'{settings.BASE_DIR}/website/libs/node_auth/sig_valid.js'
    result = subprocess.run(('/usr/bin/node', cmd, public_key, nonce, signature))
    if result.returncode != 0:
        return errResponse( request, "Invalid signature")

    # Okay we have a user, how great! Do they exist
    if (eth := EthAccount.getByAddress( public_key )) is None:
        uid = uuid.uuid4()
        human = Human.objects.create(
            username=f'usr_{uid}',
            username_unique=uid,
        )

        eth = EthAccount.objects.create(
            human=human,
            address=util.xstr(public_key).lower(),
        )

    # Store teh session
    usr = {'id': int(human.id), **eth.human.toJson()}
    request.session['usr'] = usr

    return jsonResponse( request, desc( None, usr ) )


@csrf_exempt
@reqArgs( sess_req=[('usr', dict)] )
def invalidate_auth( request, usr, *args, **kwargs ):
    del request.session['usr']

    return jsonResponse( request, {} )


@csrf_exempt
@reqArgs( sess_req=[('usr', dict)],
          )
def desc( request, usr, *args, **kwargs ):
    if (human := Human.getById( usr['id'])) is None:
        return errResponse(request, "Couldn't find human")

    return jsonResponse( request, {
        "human": human.toJson(),
        "addresses": [str(x.address) for x in human.ethaccount_set.all()],
        "nfts": [x.toJson() for x in human.nft_set.order_by('name')],
    })


@csrf_exempt
@reqArgs( sess_opt=[('usr', dict)],
          post_opt=[('username', str)
                    ]
          )
def is_unique( request, usr, username, *args, **kwargs ):
    result = { 'username': False, 'username_invalid': False }

    if username is not None:
        if (username := common.cleanName(username)) is not None:
            if usr is not None and 'username' in usr and usr['username'].lower() == util.xstr(username).lower():
                result['username'] = True
            else:
                result['username'] = Human.getByUsername( username ) is None
        else:
            result['username_invalid'] = True

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