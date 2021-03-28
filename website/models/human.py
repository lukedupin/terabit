from django import forms
from django.db import models
from django.contrib import admin
from django.utils.html import escape
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.conf import settings

from website.models.common import CreateWidget, adminEmailHtml, FriendshipEnum
from website.models import common
from website.helpers import util

import math, uuid, re, nested_admin

class Human(models.Model):
    GENDER_MALE     = 1
    GENDER_FEMALE   = 2
    GENDER_CHOICES = (
        (GENDER_MALE, "Male"),
        (GENDER_FEMALE, "Female"),
    )
    DEFAULT_GENDER = GENDER_MALE

    TYPE_NORMAL     = 1
    TYPE_PRO        = 2
    TYPE_PRO_PLUS   = 3
    TYPE_SUPER      = 4
    TYPE_CHOICES = (
        (TYPE_NORMAL, "Normal"),
        (TYPE_PRO, "Pro"),
        (TYPE_PRO_PLUS, "Pro+"),
        (TYPE_SUPER, "Super"),
    )
    DEFAULT_TYPE = TYPE_NORMAL

    # define my models
    id              = models.AutoField(primary_key=True)

    # Used to login
    uid             = models.UUIDField(default=uuid.uuid4, editable=False)
    session         = models.UUIDField(default=uuid.uuid4, editable=False)
    type            = models.IntegerField(choices=TYPE_CHOICES, default=DEFAULT_TYPE)

    username        = models.CharField(max_length=64)
    username_unique = models.CharField(max_length=64, unique=True)
    phone_number    = models.CharField(max_length=16, unique=True)
    desc            = models.TextField(null=True, default="", blank=True)
    email           = models.EmailField(max_length=64, unique=True)
    real_name       = models.CharField(max_length=64, help_text="Full real name")
    age             = models.IntegerField(default=0)
    gender          = models.IntegerField(choices=GENDER_CHOICES, default=DEFAULT_GENDER)
    height          = models.IntegerField(default=0, help_text="Inches")
    weight          = models.IntegerField(default=0, help_text="Lbs")
    profile_image   = models.CharField(max_length=96, null=True, default=None, blank=True)

    blocked         = models.BooleanField(default=False)
    moderator       = models.BooleanField(default=False, db_index=True)

    login_count     = models.IntegerField(default=1, help_text="Number of times this radius started the app")
    debug           = models.IntegerField(default=0, help_text="A number larger than zero will enabled debugging")

    lat             = models.FloatField(default=0, help_text="Center of interest for a radius")
    lng             = models.FloatField(default=0, help_text="Center of interest for a radius")

    updated_on      = models.DateTimeField(auto_now=True)
    created_on      = models.DateTimeField(auto_now_add=True)


    class Meta:
        app_label = 'website'


    #Returns a friendly name for the admin interface
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


    def getPrivacy(self):
        from website.models.human_privacy import HumanPrivacy

        # Get the privacy!
        if (privacy := HumanPrivacy.getById( self.id )) is None:
            privacy = HumanPrivacy.objects.create( human_id=self.id )

        return privacy


    def profile_tag(self):
        return mark_safe('<img src="%s" style="width:120px;height:120px;" />' % escape(self.getProfileUrl()))
    profile_tag.short_description = 'Profile Image'


    # Return the user's primary device
    def getPrimaryDevice(self):
        from website.models import Device

        # Create a device to?
        for acc in self.devicegroupaccess_set.all():
            for dev in Device.objects.filter(device_group=acc.device_group):
                return dev

        return None

    def save(self, *args, **kwargs):
        self.username_unique = self.username.lower()
        return super(Human, self).save(*args, **kwargs)

    #Convert my data to json
    def toJsonFull(self):
        return {
            'uid':              util.xstr(self.uid),
            'profile_image':    self.getProfileUrl(),
            'type':             self.get_type_display(),
            'username':         util.xstr(self.username),
            'desc':             util.xstr(self.desc),
            'email':            util.xstr(self.email),
            'phone_number':     util.xstr(self.phone_number),
            'real_name':        util.xstr(self.real_name),
            'age':              util.xint(self.age),
            'gender':           self.get_gender_display(),
            'height':           util.xint(self.height),
            'weight':           util.xint(self.weight),
            'login_count':      util.xint(self.login_count),
            'debug':            util.xint(self.debug),
            'lat':              util.xfloat(self.lat),
            'lng':              util.xfloat( self.lng ),
            'created_on':       util.timeToUnix( self.created_on ),
        }

    def toJson(self, privacy_code=FriendshipEnum.FOLLOWING ):
        privacy_lookup = common.privacyLookup( privacy_code )
        privacy = self.getPrivacy()
        return {
            'uid':              util.xstr(self.uid),
            'profile_image':    self.getProfileUrl(),
            'type':             self.get_type_display(),
            'username':         util.xstr(self.username),

            #Bio privacy
            'desc':             util.xstr(self.desc) if privacy.bio in privacy_lookup else "",

            # Real name privacy
            'real_name':        util.xstr(self.real_name) if privacy.real_name in privacy_lookup else "",

            # Body dimensions privacy
            'age':              util.xint(self.age) if privacy.body_dimensions in privacy_lookup else 0,
            'gender':           self.get_gender_display() if privacy.body_dimensions else "",
            'height':           util.xint(self.height) if privacy.body_dimensions else 0,
            'weight':           util.xint(self.weight) if privacy.body_dimensions else 0,
        }


    @staticmethod
    def customAdmin( idx=0 ):
        from website.models import Capture, RaceTeam, Friendship, FriendshipModifier

        class CaptureForm(forms.ModelForm):
            view_kml_capture = forms.Field(label='View KML file')
            view_csv_capture = forms.Field(label='View CSV file')

            class Meta:
                model = Capture
                exclude = []

            def __init__(self, *args, **kwargs):
                super(CaptureForm, self).__init__(*args, **kwargs)
                self.fields['view_kml_capture'] = CreateWidget(
                    self.viewCourseKmlHtml,
                    label='View KML file',
                    required=False,
                    instance=self.instance)
                self.fields['view_csv_capture'] = CreateWidget(
                    self.viewCourseCsvHtml,
                    label='View KML file',
                    required=False,
                    instance=self.instance)

            def viewCourseKmlHtml(self, name, value, attrs, obj):
                if obj is None:
                    return mark_safe('ERR: Invalid object')
                assert isinstance(obj, Capture)
                return mark_safe('<a href="/view_capture/%s/kml/">View Kml</a>' % obj.uid)

            def viewCourseCsvHtml(self, name, value, attrs, obj):
                if obj is None:
                    return mark_safe('ERR: Invalid object')
                assert isinstance(obj, Capture)
                return mark_safe('<a href="/view_capture/%s/csv/">View Csv</a>' % obj.uid)

        class CaptureInline(nested_admin.NestedTabularInline):
            fields = ('start_ts', 'finish_ts', 'dist', 'elv_gain', 'elv_drop', 'time_stopped', 'battery_usage', 'view_kml_capture', 'view_csv_capture')
            readonly_fields = ('start_ts', 'finish_ts', 'dist', 'elv_gain', 'elv_drop', 'time_stopped', 'battery_usage')
            model = Capture
            form = CaptureForm
            extra = 0

            def battery_usage(self, obj):
                return 0
                #return "%d : %d and %d" % (obj.devicepoint_set.count(), min, max)
                #return int(points[count-1].battery) - int(points[0].battery)

        class FollowingInline(nested_admin.NestedTabularInline):
            model = Friendship
            verbose_name = "Following"
            verbose_name_plural = "Following"
            fk_name = 'source'
            extra = 0

        class FollowerInline(nested_admin.NestedTabularInline):
            model = Friendship
            verbose_name = "Follower"
            verbose_name_plural = "Followers"
            fk_name = 'target'
            extra = 0

        class MyFriendshipModifierInline(nested_admin.NestedTabularInline):
            model = FriendshipModifier
            verbose_name = "My Outstanding modifiers"
            verbose_name_plural = "My Outstanding modifiers"
            fk_name = 'source'
            extra = 0

        class TheirFriendshipModifierInline(nested_admin.NestedTabularInline):
            model = FriendshipModifier
            verbose_name = "Their outstanding modifiers"
            verbose_name_plural = "Their outstanding modifiers"
            fk_name = 'target'
            extra = 0

        class RaceTeamInline(nested_admin.NestedTabularInline):
            model = RaceTeam
            extra = 0
            # TODO Fix the captures to be view only clickable
            #inlines = (CaptureInline, )

        class HumanForm(forms.ModelForm):
            view_kml_capture = forms.Field(label='View Kml file')

            class Meta:
                model = Human
                exclude = []

            def __init__(self, *args, **kwargs):
                super(HumanForm, self).__init__(*args, **kwargs)
                self.fields['view_kml_capture'] = CreateWidget(
                    self.viewCourseKmlHtml,
                    label='View KML file',
                    required=False,
                    instance=self.instance)

            def viewCourseKmlHtml(self, name, value, attrs, obj):
                if obj is None:
                    return mark_safe('ERR: Invalid object')
                assert isinstance(obj, Human)
                return mark_safe( '<a href="/view_human/%s/kml/">View Kml</a>' % obj.uid)

        class HumanAdmin(nested_admin.NestedModelAdmin):
            fields = ('username', 'type', 'moderator', 'blocked', 'desc', 'phone_number', 'email', 'real_name', 'age', 'gender', 'height', 'weight', 'debug', 'uid', 'profile_tag', 'view_kml_capture')
            readonly_fields = ('uid', 'session', 'username_unique', 'profile_tag')
            # TODO Fix the captures to be view only clickable
            inlines = (RaceTeamInline, FollowerInline, FollowingInline, MyFriendshipModifierInline, TheirFriendshipModifierInline)
            #inlines = (CaptureInline, RaceTeamInline)
            search_fields = ('username', 'real_name', 'email', 'phone_number')
            form = HumanForm

        return ( HumanAdmin, None )[idx]

