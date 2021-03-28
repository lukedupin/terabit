from django.http import HttpResponse
from django.conf import settings
from website.helpers.util import xstr, xint, xfloat, xbool

import json, re, math

class JsonApiFile:
    def __init__(self, file):
        self.file = file

    def __str__(self):
        return str(self.file)

    def data(self):
        # Load data
        by = bytes()
        for chunk in self.file.chunks(chunk_size=0x100000):
            by += chunk

        return by


#Value conversion
def convertData( key, typ, raw, default ):
    val = None
    err = "Unknown type for %s" % key

    if issubclass( typ, str ):
        val = xstr( raw, default )
        err = None if val is not None else "Couldn't parse %s as string" % key
    elif issubclass( typ, bool ):
        val = xbool( raw, none=default, undefined=default)
        err = None if val is not None else "Couldn't parse %s as bool" % key
    elif issubclass( typ, int ):
        val = xint( raw, default )
        err = None if val is not None else "Couldn't parse %s as int" % key
    elif issubclass( typ, float ):
        val = xfloat( raw, default )
        err = None if val is not None else "Couldn't parse %s as float" % key
    elif issubclass( typ, dict ) or issubclass( typ, list ):
        contains = tuple() if default is None else default
        err = None
        try:
            #Testing cases mostly, we already have a dict of data
            if isinstance(raw, dict):
                return (raw, None)

            #Convert the string
            val = json.loads( raw )
            if val is None:
                return ( None, "Error, couldn't load valid json for %s" % key )

            #If json, check for contain keys, if the format is invalid, quit
            if len(contains) > 0 and not all(k in val for k in contains):
                missing = []
                for k in contains:
                    if k not in val:
                        missing.append( k )
                        val = None

                if len(missing) > 0:
                    err = "Invalid %s format. Required %s missing %s" % ( key, contains, missing)

        except json.decoder.JSONDecodeError as e:
            return ( None, "Error processing json object %s [%s]" % (key, str(e)) )

    return ( val, err )

#Internal function which runs the assignment action
def pullArgs( kwargs, req_args, request_args, req_dict, missing ):
    for x in request_args:
        if len(x) < 2:
            return "Invalid json value, must have at least key and type"

        #Pull my info out
        key = x[0]
        type = x[1]
        default = None if len(x) == 2 else x[2]

        #Don't allow args that already exist to be overwritten!
        if key in kwargs:
            req_args[key] = kwargs[key]
            continue

        #Parse the key
        val, err = convertData( key, type, req_dict[key], default) if key in req_dict else (default, None)
        if err is not None:
            return err

        #Store the data
        if val is not None:
            kwargs[key] = req_args[key] = val
        elif missing is not None:
            missing.append( key )
        else:
            kwargs[key] = None

    return None

# Request args wrapper class
#class __exportReqArgs:
#    def __init__(self, auth=None, sess_req=[], sess_opt=[], get_req=[], get_opt=[], post_req=[], post_opt=[] ):
#        def _args( args ):
#            return args if isinstance( args, tuple) or isinstance( args, list ) else (args,)
#
#        self.auth = auth
#        self.sess_req = _args( sess_req )
#        self.get_req = _args( get_req )
#        self.post_req = _args( post_req )
#
#        self.sess_opt = _args( sess_opt )
#        self.get_opt = _args( get_opt )
#        self.post_opt = _args( post_opt )
#
#    def __call__(self, *args, **kwargs):
#        def wrapper( *args, ** kwargs):
#            return self
#        return wrapper


#Request args wrapper class
class reqArgs:
    def __init__(self, auth=None, sess_req=[], sess_opt=[], get_req=[], get_opt=[], post_req=[], post_opt=[], file_req=[], file_opt=[], files=None ):
        def _args( args ):
            return args if isinstance( args, tuple) or isinstance( args, list ) else (args,)

        self.auth = auth
        self.sess_req = _args( sess_req )
        self.get_req = _args( get_req )
        self.post_req = _args( post_req )
        self.file_req = file_req

        self.sess_opt = _args( sess_opt )
        self.get_opt = _args( get_opt )
        self.post_opt = _args( post_opt )
        self.file_opt = file_opt

        self.files = files

    def __call__(self, func):
        def wrapper( *args, **kwargs ):
            #Get my request object
            request = kwargs['request'] if 'request' in kwargs else args[0]

            # If we don't have a request, or json_api is False/None just call the function directly
            if request is None or 'json_api' in kwargs and not kwargs['json_api']:
                return func(*args, **kwargs)

            request.POST = json.loads( request.body.decode('utf-8'))

            #print(kwargs)
            #print( request.POST )
            #print( request.GET )
            #print( request.body.decode('utf-8') )

            req_args = {}
            get_missing = []
            post_missing = []
            sess_missing = []
            file_missing = []
            #print(request.POST)

            #Required args
            err = pullArgs( kwargs, req_args, self.sess_req, request.session, sess_missing )
            if err is not None:
                return errResponse( request, err )
            err = pullArgs( kwargs, req_args, self.post_req, request.POST, post_missing )
            if err is not None:
                return errResponse( request, err )
            err = pullArgs( kwargs, req_args, self.get_req, request.GET, get_missing )
            if err is not None:
                return errResponse( request, err )

            #Optional args, no missing accumulation
            err = pullArgs( kwargs, req_args, self.sess_opt, request.session, None )
            if err is not None:
                return errResponse( request, err )
            err = pullArgs( kwargs, req_args, self.post_opt, request.POST, None )
            if err is not None:
                return errResponse( request, err )
            err = pullArgs( kwargs, req_args, self.get_opt, request.GET, None )
            if err is not None:
                return errResponse( request, err )

            # Files are simple, just check if they exist, the type is always a string filename
            if request.method == 'POST':
                for file in self.file_req:
                    if file in request.FILES:
                        kwargs[file] = JsonApiFile( request.FILES[file] )
                    else:
                        file_missing.append(file)

                for file in self.file_opt:
                    if file in request.FILES:
                        kwargs[file] = JsonApiFile( request.FILES[file] )
                    else:
                        kwargs[file] = None

                # If we have a "files" then load it, but skip all listed files
                if self.files is not None:
                    skip = self.file_req + self.file_opt
                    kwargs[self.files] = []

                    # Attempt to keep the order of files
                    file_keys = list(request.FILES.keys())
                    file_keys.sort()
                    for file in file_keys:
                        if file not in skip:
                            kwargs[self.files].append( JsonApiFile( request.FILES[file] ))
            else:
                file_missing = self.file_req

            #Are we good?
            if (len(get_missing) + len(post_missing)) + len(sess_missing) + len(file_missing) > 0:
                return errResponse( request, 'Missing required argument(s): GET%s POST%s SESS%s FILE%s' % (str(get_missing), str(post_missing), str(sess_missing), str(file_missing)))

            #Store all args into the requested args hash
            kwargs['req_args'] = req_args

            #Auth check?
            if self.auth is not None:
                #True for check authentication with default system auth
                if isinstance( self.auth, bool ):
                    if self.auth:
                        if not request.user.is_authenticated():
                            return errResponse( request, "Not logged in")

                #Custom user authentication, we just just need a true/false
                elif hasattr( self.auth, '__call__'):
                    if not self.auth( *args, **kwargs ):
                        return errResponse( request, "Not logged in")

                #Not sure what we were pass, default to system authentication
                else:
                    print("Unknown auth type, running default authentication to be safe")
                    if not request.user.is_authenticated():
                        return errResponse( request, "Not logged in")

            return func( *args, **kwargs)
        return wrapper


# Export the reqArgs
#if settings.EXPORT_API:
#    reqArgs = __exportReqArgs
#else:
#    reqArgs = __baseReqArgs


# Json response
def jsonResponse( request, objs={} ):
    objs['successful'] = True

    # If we have no request, then just return the objects
    if request is None:
        return objs

    callback = request.GET['callback'] if 'callback' in request.GET else None
    return rawResponse( json.dumps( objs ), status=200, content='application/json', callback=callback )


# Return an error response
def errResponse( request, reason, code="", extra={} ):
    print( reason )
    objs = { 'successful': False, 'reason': reason, 'code': code }
    objs.update( extra )

    # If we have no request, then just return the objects
    if request is None:
        return objs

    callback = request.GET['callback'] if 'callback' in request.GET else None
    return rawResponse( json.dumps( objs ), status=201, content='application/json', callback=callback )


# Raw response Info
def rawResponse( objs, status, content, callback=None ):
    if callback:
        return HttpResponse( "%s(%s)" % (callback, objs),
                             status=status, content_type=content )
    else:
        return HttpResponse( objs, status=status, content_type=content )
