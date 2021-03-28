from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache

from website.helpers.json_api import reqArgs, jsonResponse, errResponse

def current_version():
    return { 'major': 3, 'minor': 0 }


@csrf_exempt
@reqArgs( post_req=[ ('major', int),
                     ('minor', int),
          ],
        )
def compat( request, major, minor, *args, **kwargs ):
    if major != 3:
        return errResponse(request, "Incompatible version")

    return jsonResponse( request, current_version() )


@csrf_exempt
@reqArgs(post_opt=[
    ('dog', str),
        ],
         )
def current(request, dog, *args, **kwargs):
    print( dog )
    return jsonResponse(request, current_version() )

