#!/usr/bin/env python
#
# Author: Sreejith Kesavan <sreejithemk@gmail.com>
#
# Description: Gevent based Asynchronous WebSocket Server with HTTP APIs.


def enum(**enums):
    return type('Enum', (), enums)


NOTIFIER_LOG_FILE = 'wsnotifier.log'
notification_type = enum(
    ERROR="error",
    WARNING="warning",
    INFO="info",
    SCHEDULE="scheduled"
)
DEFAULT_NOTIFICATION_SERVICE_URL = 'http://localhost:1729/alerts'
