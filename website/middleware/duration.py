import time


class DurationMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        now = time.time()
        response = self.get_response( request )
        duration = time.time() - now

        # Add the header.
        print(" **Duration: %dms" % int(duration * 1000))
        return response
