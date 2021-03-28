from django.db import models
from django.contrib import admin

from website.models.device import Device
from website.models.activity import Activity
from website.models.capture import Capture

from website.helpers import util

import math


class DevicePoint(models.Model):
    # define my models
    id                  = models.AutoField(primary_key=True)
    device              = models.ForeignKey(Device, on_delete=models.CASCADE)
    activity            = models.ForeignKey(Activity, on_delete=models.CASCADE)

    # What is this data point associated to? Can be both, or neither
    capture             = models.ForeignKey(Capture, null=True, default=None, on_delete=models.SET_DEFAULT)

    lat                 = models.FloatField(default=0, help_text='Latitude')
    lng                 = models.FloatField(default=0, help_text='Longitude')
    elv                 = models.FloatField(default=0, help_text='Elevation')
    spd                 = models.FloatField(default=0, help_text='Speed')
    dist                = models.FloatField(default=0, help_text='Distance from last point')
    seq                 = models.IntegerField(default=0, help_text='Sequence of this point in the capture')
    battery             = models.IntegerField(default=0, help_text='Battery level of device')
    head                = models.IntegerField(default=0, help_text='Heading of movement')

    timestamp           = models.DateTimeField()

    class Meta:
        app_label = 'website'

    #Returns a friendly name for the admin interface
    def __str__(self):
        return "%.4f, %.4f" % (self.lat, self.lng)

    @staticmethod
    def getById( id ):
        try:
            return DevicePoint.objects.get(id=util.xint(id))
        except DevicePoint.DoesNotExist:
            return None

    #Convert my data to json
    def toJson(self):
        return {'lat':      float(self.lat),
                'lng':      float(self.lng),
                'elv':      float(self.elv),
                'spd':      float(self.spd),
                'dist':     float(self.dist),
                'seq':      int(self.seq),
                'battery':  int(self.battery),
                'head':     float(self.head),
                'ts':       util.timeToUnix(self.timestamp),
                }

    #Convert my data to json
    def toMinJson(self):
        return {'lat':      float(self.lat),
                'lng':      float(self.lng),
                'elv':      float(self.elv),
                'spd':      float(self.spd),
                'ts':       util.timeToUnix(self.timestamp),
                }

    @staticmethod
    def customAdmin( idx=0 ):
        class DevicePointAdmin(admin.ModelAdmin):
            pass

        return ( DevicePointAdmin, None )[idx]
