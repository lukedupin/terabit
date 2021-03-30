from django.db import models
from django.contrib import admin

from website.models.human import Human
from website.models.land import Land

from website.helpers import util

import math, uuid


class Nft(models.Model):
    # define my models
    id                  = models.AutoField(primary_key=True)
    human               = models.ForeignKey(Human, on_delete=models.CASCADE)
    land                = models.ForeignKey(Land, default=None, null=True, blank=True, on_delete=models.CASCADE)

    name                = models.CharField(max_length=64)
    uid                 = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)
    desc                = models.TextField(null=True, default="", blank=True)

    url                 = models.URLField(default="", null=True, blank=True)

    updated_on          = models.DateTimeField(auto_now=True)
    created_on          = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'website'

    def __str__(self):
        return self.name

    @staticmethod
    def getById( id ):
        try:
            return Nft.objects.get(id=util.xint(id))
        except Nft.DoesNotExist:
            return None

    #Convert my data to json
    def toJson(self):
        return {
            'uid':          util.xstr(self.uid),
            'human_uid':    util.xstr(self.human.uid),
            'land_uid':     util.xstr(self.land.uid) if util.xint(self.land_id) > 0 else "",
            'name':         util.xstr(self.name),
            'desc':         util.xstr(self.desc),
            'url':          util.xstr(self.url),
            'updated_on':   util.timeToUnix(self.updated_on),
            'created_on':   util.timeToUnix(self.created_on),
        }

    @staticmethod
    def customAdmin( idx=0 ):
        class NtfAdmin(admin.ModelAdmin):
            pass

        return ( NtfAdmin, None )[idx]
