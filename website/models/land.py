from django.db import models
from django.contrib import admin

from website.models.human import Human

from website.helpers import util

import math, uuid


class Land(models.Model):
    STATUS_UNMINTED     = 1
    STATUS_CLAIMED      = 2
    STATUS_FOR_SALE     = 3
    STATUS_CHOICES = (
        (STATUS_UNMINTED,   "Unminted"),
        (STATUS_CLAIMED,    "Claimed"),
        (STATUS_FOR_SALE,   "For sale"),
    )
    DEFAULT_STATUS = STATUS_UNMINTED

    # define my models
    id                  = models.AutoField(primary_key=True)
    human               = models.ForeignKey(Human, on_delete=models.CASCADE)

    name                = models.CharField(max_length=64, default="", blank=True)
    uid                 = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)
    desc                = models.TextField(null=True, default="", blank=True)

    lat                 = models.FloatField(db_index=True, default=0, help_text='Latitude')
    lng                 = models.FloatField(db_index=True, default=0, help_text='Longitude')
    elv                 = models.FloatField(default=0, help_text='Elevation')
    status              = models.IntegerField(choices=STATUS_CHOICES, default=DEFAULT_STATUS)

    nft_count           = models.IntegerField(default=0)

    updated_on          = models.DateTimeField(auto_now=True)
    created_on          = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'website'

    #Returns a friendly name for the admin interface
    def __str__(self):
        return "%.4f, %.4f" % (self.lat, self.lng)

    @staticmethod
    def getById( id ):
        try:
            return Land.objects.get(id=util.xint(id))
        except Land.DoesNotExist:
            return None

    #Convert my data to json
    def toJson(self):
        return {
            'uid':      util.xstr(self.uid),
            'name':     util.xstr(self.name),
            'desc':     util.xstr(self.desc),
            'lat':      util.xfloat(self.lat),
            'lng':      util.xfloat(self.lng),
            'elv':      util.xfloat(self.elv),
            'status':   self.get_status_display(),
            'nft_count': util.xint(self.nft_count),
            'updated_on': util.timeToUnix(self.updated_on),
            'created_on': util.timeToUnix(self.created_on),
        }

    @staticmethod
    def customAdmin( idx=0 ):
        class LandAdmin(admin.ModelAdmin):
            list_display = ('status', 'lat', 'lng', 'name')

        return ( LandAdmin, None )[idx]
