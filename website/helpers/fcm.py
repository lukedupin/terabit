from pyfcm import FCMNotification
from django.conf import settings

from website.helpers import util


def send_push_message(reg_id, title, msg):
    push_service = FCMNotification(api_key=settings.FCM_API_KEY)
    if isinstance(reg_id, list):
        if len(reg_id) > 0:
            push_service.notify_multiple_devices(registration_ids=reg_id, message_title=title, message_body=msg, sound='Default')
    else:
        push_service.notify_single_device(registration_id=reg_id, message_title=title, message_body=msg, sound='Default')


def find_invalid_push_tokens(devices):
    push_service = FCMNotification(api_key=settings.FCM_API_KEY)

    # Pull the tokens, and then query
    tokens = [util.xstr(x.push_token) for x in devices if x.isPushTokenValid()]
    lookup = {x: True for x in push_service.clean_registration_ids( tokens )}

    # What is missing?
    invalid = []
    for dev in devices:
        if util.xstr(dev.push_token) not in lookup:
            invalid.append( dev )

    return invalid
