import os

from django.conf import settings
from website.libs.posix_spawner import posix_spawn

# Run a manager command forked 
def runManager( cmd ):
    # Run my posix lib hook
    #print( settings.BASE_DIR )
    run = 'cd %s; /usr/bin/python3 manage.py %s' % (settings.BASE_DIR, cmd)
    posix_spawn( '/usr/bin/sh', ['-c', run])
