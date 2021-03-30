from django import forms
from django.db import models
from django.contrib import admin
from django.utils.html import escape
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.conf import settings

from website.helpers import util

import math, uuid, re, nested_admin

class Human(models.Model):
    TYPE_NORMAL     = 1
    TYPE_CHOICES = (
        (TYPE_NORMAL, "Normal"),
    )
    DEFAULT_TYPE = TYPE_NORMAL

    # define my models
    id              = models.AutoField(primary_key=True)

    # Used to login
    uid             = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)
    session         = models.UUIDField(default=uuid.uuid4, editable=False)
    type            = models.IntegerField(choices=TYPE_CHOICES, default=DEFAULT_TYPE)

    username        = models.CharField(max_length=64)
    username_unique = models.CharField(max_length=64, unique=True)
    password        = models.CharField(max_length=64)

    bio             = models.TextField(null=True, default="", blank=True)
    phone_number    = models.CharField(max_length=16, unique=True)
    email           = models.EmailField(max_length=64, unique=True)
    real_name       = models.CharField(max_length=64, help_text="Full real name")
    profile_image   = models.CharField(max_length=96, null=True, default=None, blank=True)
    nft_count       = models.IntegerField(default=0)

    blocked         = models.BooleanField(default=False)

    updated_on      = models.DateTimeField(auto_now=True)
    created_on      = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'website'

    def __str__(self):
        return self.username

    @staticmethod
    def getById( id ):
        try:
            return Human.objects.get(id=util.xint(id))
        except Human.DoesNotExist:
            return None

    @staticmethod
    def getByUid( uid ):
        try:
            return Human.objects.get(uid=util.xstr(uid))
        except Human.DoesNotExist:
            return None
        except ValidationError:
            return None
        except Human.MultipleObjectsReturned:
            return None

    @staticmethod
    def getByUsername( username ):
        try:
            return Human.objects.get(username_unique=util.xstr(username).lower())
        except Human.DoesNotExist:
            return None
        except Human.MultipleObjectsReturned:
            return None

    @staticmethod
    def getBySession( uid, sess ):
        try:
            return Human.objects.get(uid=util.xstr(uid), session=util.xstr(sess))
        except Human.DoesNotExist:
            return None
        except ValidationError:
            return None
        except Human.MultipleObjectsReturned:
            return None

    @staticmethod
    def getByEmail( email ):
        try:
            return Human.objects.get(email=util.xstr(email).lower())
        except Human.DoesNotExist:
            return None
        except Human.MultipleObjectsReturned:
            return None

    @staticmethod
    def getByPhoneNumber( phone_number ):
        try:
            return Human.objects.get(phone_number=util.xstr(phone_number).lower())
        except Human.DoesNotExist:
            return None
        except Human.MultipleObjectsReturned:
            return None

    def getProfileUrl(self):
        if util.xstr(self.profile_image) != "":
            profile_image = util.xstr(self.profile_image)
        else:
            profile_image = 'profiles/avatar_%03d.png' % (util.xint(self.id) % 143)

        return "https://%s.%s.%s/%s" % (settings.S3_ACCESS['BUCKET'],
                                        settings.S3_ACCESS['REGION'],
                                        settings.S3_ACCESS['HOST'],
                                        profile_image)

    def profile_tag(self):
        return mark_safe('<img src="%s" style="width:120px;height:120px;" />' % escape(self.getProfileUrl()))
    profile_tag.short_description = 'Profile Image'

    def save(self, *args, **kwargs):
        self.username_unique = self.username.lower()
        return super(Human, self).save(*args, **kwargs)

    def toJson(self):
        return {
            'uid':              util.xstr(self.uid),
            'profile_image':    self.getProfileUrl(),
            'type':             self.get_type_display(),
            'username':         util.xstr(self.username),

            'bio':              util.xstr(self.bio),
            'real_name':        util.xstr(self.real_name),
            'nft_count':        util.xint(self.nft_count),
        }

    @staticmethod
    def customAdmin( idx=0 ):
        class HumanAdmin(nested_admin.NestedModelAdmin):
            fields = ('username', 'type', 'blocked', 'bio', 'phone_number', 'email', 'real_name', 'nft_count', 'uid', 'profile_tag')
            readonly_fields = ('uid', 'session', 'username_unique', 'profile_tag')
            search_fields = ('username', 'real_name', 'email', 'phone_number')

        return ( HumanAdmin, None )[idx]

