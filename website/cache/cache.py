from django.core.cache import cache, caches

from website.cache import DEFAULT_TIMEOUT
from website.models import Human
from website.helpers import util

import json, random


def accessCodeKey( code ):
    return "accses_code_%s" % code


# Get the access code
def accessCode( code ):
    key = accessCodeKey( code )
    json = cache.get( key )
    if json is None:
        return None

    return json


# Store the access code
def storeAccessCode( code, radius_uid ):
    key = accessCodeKey( code )
    cache.set( key, radius_uid )

    return True


# Delete the access code?
def deleteAccessCode( code ):
    key = accessCodeKey( code )
    cache.delete( key )


#Store the user's broadcast info
def storeRecoveryAccessCode( human_uid, code ):
    cache.set( 'recovery_access_%s' % human_uid, code, DEFAULT_TIMEOUT )


# Find the code?
def execRecoveryAccessCode( human_uid ):
    key = 'recovery_access_%s' % human_uid
    code = cache.get( key )
    cache.delete( key )

    return code

# Generate a nonce for a given user
def generateNonce( addr ):
    key = 'nonce_%s' % addr
    nonce = '0x'
    for _ in range(4):
        nonce += '%08X' % random.randint(0, 0xFFFFFFFF)
    cache.set(key, nonce, 10) # Very short amount of time

    return nonce

# Get teh nonce
def takeNonce( addr ):
    key = 'nonce_%s' % addr
    nonce = cache.get( key )
    if nonce is not None:
        cache.delete( key )

    return nonce
