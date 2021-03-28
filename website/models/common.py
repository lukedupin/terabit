from django import forms
from django.utils.safestring import mark_safe
from website.helpers import util, geo
import re, uuid


def adminEmailHtml(email, name='email_widget'):
    return mark_safe("""
<script>
function %s_Func()
{
    var copyText = document.getElementById("%s");
    copyText.style.display = "inline";
    copyText.select();
    copyText.setSelectionRange(0, 99999);
    document.execCommand("copy");
    copyText.style.display = "none";
    document.getElementById("%s_button").value = "Copied email"
}
</script>
<input type="text" id="%s" value="%s" style="display:none;">
<input type="button" id="%s_button" onclick="%s_Func()" value="Copy email address(es)">
""" % (name, name, name, name, email, name, name))


def cleanName(name):
    name = re.sub("^[ \t]*", "", util.xstr(name))
    name = re.sub("[^a-zA-Z0-9_. -]", "", name)
    if len(name) <= 0:
        return None

    return name


def cleanEmail(email):
    email = re.sub("[^@a-z0-9_.-]", "", util.xstr(email).lower())
    if re.search("[a-z0-9_+-]+@[a-z0-9_-]+[.][a-z]+", email) is None:
        return None

    return email


def cleanPhoneNumber(phone_number):
    phone_number = re.sub("[^0-9]", "", util.xstr(phone_number).lower())
    phone_number = re.sub("^1", "", phone_number)
    return phone_number if len(phone_number) == 10 else None


class CustomWidget(forms.Widget):
    def __init__(self, callback, instance=None, *args, **kwargs):
        super( CustomWidget, self ).__init__( *args, **kwargs )
        self._callback = callback
        self._instance = instance

    def render(self, name, value, attrs=None, renderer=None):
        return self._callback( name, value, attrs, self._instance )


class CreateWidget(forms.Field):
    def __init__(self, callback, instance=None, *args, **kwargs):
        super( CreateWidget, self ).__init__( *args, **kwargs )
        self.widget = CustomWidget( callback, instance )


# Take a single privacy code and return all the valid codes based on access
def privacyLookup( privacy_code ):
    # The viewer is an inner circle
    if privacy_code == FriendshipEnum.INNER_CIRCLE:
        return (FriendshipEnum.FOLLOWING, FriendshipEnum.FRIEND, FriendshipEnum.INNER_CIRCLE)

    # The viewer is friends
    elif privacy_code == FriendshipEnum.FRIEND:
        return (FriendshipEnum.FOLLOWING, FriendshipEnum.FRIEND)

    else:
        return (FriendshipEnum.FOLLOWING,)


# Need this because you can't serialize lambda
def empty_array():
    return []


def default_auth_code():
    return str(uuid.uuid4()).upper()[:5]


def is_uuid_valid(uuid_to_test, version=4):
    try:
        uuid_obj = uuid.UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test


# Grab the sequence info
def create_sequence( items ):
    count = 0
    singles = []
    ranges = []
    min_seq = -1
    max_seq = -1
    for dp in items:
        count += 1
        cur = int(dp.seq)

        if min_seq < 0:
            min_seq = max_seq = cur
            continue

        # Is this entry in sequence?
        if max_seq + 1 == cur:
            max_seq = cur
            continue

        # Is this a single or a range?
        if min_seq == max_seq:
            singles.append(min_seq)
        else:
            ranges.append({'min': min_seq, 'max': max_seq})
        min_seq = max_seq = cur

    # Clean up the last entry
    if min_seq >= 0:
        if min_seq == max_seq:
            singles.append(min_seq)
        else:
            ranges.append({'min': min_seq, 'max': max_seq})

    return {'count': count, 'singles': singles, 'ranges': ranges }


def outside_zones( zones, pt ):
    for zone, box in zones:
        if box.contains(pt.lat, pt.lng) and \
           zone.radius >= geo.distance(pt.lat, pt.lng, zone.lat, zone.lng):
            return False

    return True


class MemberRole:
    # User type
    ADMIN        = 1
    MEMBER       = 2
    MODERATOR    = 3
    CHOICES = (
        (ADMIN, "Admin"),
        (MEMBER, "Member"),
        (MODERATOR, "Moderator"),
    )
    DEFAULT = MEMBER

    @staticmethod
    def fromStr( acc ):
        acc = util.xstr( acc ).replace('_', ' ').lower()
        for p in MemberRole.CHOICES:
            if p[1].lower() == acc:
                return p[0]

        return -1

    @staticmethod
    def fromCode( code ):
        code = util.xint( code )
        for p in MemberRole.CHOICES:
            if p[0].lower() == code:
                return p[1]

        return None


class Visibility:
    PUBLIC       = 1
    FRIENDS      = 2
    INCOGNITO    = 3
    CHOICES = (
        (PUBLIC, "Public"),
        (FRIENDS, "Friends"),
        (INCOGNITO, "Incognito"),
    )
    DEFAULT = FRIENDS

    @staticmethod
    def fromStr(vis):
        vis = util.xstr(vis).lower()
        for p in Visibility.CHOICES:
            if p[1].lower() == vis:
                return p[0]

        return -1

    @staticmethod
    def fromCode(code):
        code = util.xint(code)
        for p in Visibility.CHOICES:
            if p[0].lower() == code:
                return p[1]

        return None


class FriendshipEnum:
    FOLLOWING    = 1 # This is following also
    FRIEND       = 2
    INNER_CIRCLE = 3
    CHOICES = (
        (FOLLOWING, "Following"),
        (FRIEND, "Friend"),
        (INNER_CIRCLE, "Inner Circle"),
    )
    DEFAULT = FRIEND

    @staticmethod
    def fromStr(vis):
        vis = util.xstr(vis).lower()
        for p in FriendshipEnum.CHOICES:
            if p[1].lower() == vis:
                return p[0]

        return -1

    @staticmethod
    def fromCode(code):
        code = util.xint(code)
        for p in FriendshipEnum.CHOICES:
            if p[0].lower() == code:
                return p[1]

        return None