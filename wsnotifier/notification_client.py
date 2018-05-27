#!/usr/bin/env python
#
# Author: Sreejith Kesavan <sreejithemk@gmail.com>
#
# Description: Gevent based Asynchronous WebSocket Server with HTTP forwarder APIs


import datetime
import requests
import logging
import ssl

from wsnotifier import constants

log = logging.getLogger(__name__)


def post_alert(
        msg_id,
        msg_type,
        message,
        show_time=datetime.datetime.now().isoformat(),
        end_time=datetime.datetime.now().isoformat(),
        interval=60 * 60 * 24, notification_url=constants.DEFAULT_NOTIFICATION_SERVICE_URL):
    message = {
        'id': msg_id,
        'type': msg_type,
        'message': message,
        'show_time': show_time,
        'end_time': end_time,
        'interval': interval
    }
    resp = None
    default_context = ssl._create_default_https_context
    ssl._create_default_https_context = ssl._create_unverified_context
    try:

        resp = requests.post(notification_url, json=message, verify=False)
    except Exception as e:
        log.exception("Posting Notification failed {}".format(str(e)))
        return False
    finally:
        ssl._create_default_https_context = default_context

    if resp and resp.status_code == requests.codes.ok:
        log.info('Posting message was successful with response code: {}'.format(
            resp.status_code))
        return True
    else:
        log.info('Could not post message with response code: {}'.format(
            resp.status_code))
        return False


def remove_alert(msg_id, notification_url=constants.DEFAULT_NOTIFICATION_SERVICE_URL):
    message = {
        'id': msg_id,
    }

    resp = requests.delete(notification_url, json=message)

    if resp.status_code == requests.codes.ok:
        log.info('Message removed successfully')
        return True
    else:
        log.info('Removing message was unsuccessful')
        return False


if __name__ == '__main__':
    import time
    post_alert('unique-message-id', 'important', 'important message')
