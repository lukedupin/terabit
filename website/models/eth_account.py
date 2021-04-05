from django import forms
from django.db import models
from django.contrib import admin
from django.utils.html import escape
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.conf import settings

from website.models import Human

from website.helpers import util

import math, uuid, re, nested_admin

class EthAccount(models.Model):
    # define my models
    id              = models.AutoField(primary_key=True)

    human               = models.ForeignKey(Human, on_delete=models.CASCADE)

    # Used to login
    uid             = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)

    address         = models.CharField(max_length=128)

    updated_on      = models.DateTimeField(auto_now=True)
    created_on      = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'website'

    def __str__(self):
        return self.address

    @staticmethod
    def getById( id ):
        try:
            return EthAccount.objects.get(id=util.xint(id))
        except EthAccount.DoesNotExist:
            return None

    @staticmethod
    def getByUid( uid ):
        try:
            return EthAccount.objects.get(uid=util.xstr(uid))
        except EthAccount.DoesNotExist:
            return None
        except ValidationError:
            return None
        except EthAccount.MultipleObjectsReturned:
            return None

    @staticmethod
    def getByAddress( uid ):
        try:
            return EthAccount.objects.get(address=util.xstr(uid).lower())
        except EthAccount.DoesNotExist:
            return None
        except ValidationError:
            return None
        except EthAccount.MultipleObjectsReturned:
            return None

    def toJson(self):
        return {
            'uid':      util.xstr(self.uid),
            'address':  util.xstr(self.address),
        }

    @staticmethod
    def customAdmin( idx=0 ):
        class EthAccountAdmin(nested_admin.NestedModelAdmin):
            pass

        return ( EthAccountAdmin, None )[idx]

