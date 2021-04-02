from django.db import models
from django.contrib import admin

from website.models.human import Human

from website.helpers import util

import math, uuid


class State(models.Model):
    # define my models
    id                  = models.AutoField(primary_key=True)

    name                = models.CharField(db_index=True, max_length=64, default="", blank=True)
    uid                 = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)

    updated_on          = models.DateTimeField(auto_now=True)
    created_on          = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'website'

    #Returns a friendly name for the admin interface
    def __str__(self):
        return self.name

    @staticmethod
    def getById( id ):
        try:
            return State.objects.get(id=util.xint(id))
        except State.DoesNotExist:
            return None

    @staticmethod
    def getByName( name ):
        try:
            return State.objects.get(name=util.xstr(name))
        except State.DoesNotExist:
            return None

    #Convert my data to json
    def toJson(self):
        return {
            'uid':      util.xstr(self.uid),
            'name':     util.xstr(self.name),
            'updated_on': util.timeToUnix(self.updated_on),
            'created_on': util.timeToUnix(self.created_on),
        }

    @staticmethod
    def customAdmin( idx=0 ):
        class StateAdmin(admin.ModelAdmin):
            pass

        return ( StateAdmin, None )[idx]
