#!/usr/bin/env python
#
# Author: Sreejith Kesavan <sreejithemk@gmail.com>
#
# Description: Gevent based Asynchronous WebSocket Server with HTTP APIs.


import os
import json
import gevent
import argparse
import logging
import logging.handlers
import datetime
import dateutil.parser

from flask import Flask, request
from flask_sockets import Sockets
from wsnotifier import constants

app = Flask(__name__)
sockets = Sockets(app)

log = logging.getLogger(__name__)


class Notifications(object):

    def __new__(cls):
        if '_notifications_instance' not in cls.__dict__:
            cls._notifications_instance = object.__new__(cls)
            cls._notifications_instance.init()
        return cls._notifications_instance

    def init(self):
        self.messages = {}

    def add_message(self, message):
        self.messages[message.id] = message

    def remove_message(self, msg_id):
        try:
            log.info('Removing Message with id {}'.format(msg_id))
            del self.messages[msg_id]
        except ValueError:
            pass

    def get_messages(self):
        while True:
            gevent.sleep(0.1)
            for message_id, message in self.messages.iteritems():
                yield message


notifications = Notifications()


class DisplayType:

    NO_DISPLAY = 0
    DISPLAY = 1


class Message(object):
    """Creating an alert message. Message should contain type and message content."""

    def __init__(
            self, msg_id, msg_type, message, show_time=datetime.datetime.now(),
            end_time=datetime.datetime.now(), interval=datetime.timedelta(1)):
        """The show_time, end_time and interval are optional parameters based on requirements.
        show_time will be the first time to display, so should hold a value as (start + interval).
        But if show_time has been mentioned then, end_time is mandatory"""
        self.id = msg_id
        self.type = msg_type
        self.message = message
        self.show_time = show_time
        self.end_time = end_time
        self.interval = interval

    def to_be_displayed(self):
        if self.show_time > self.end_time:
            log.info(
                'Show time greater than end time, do not show and pop the message')
            return DisplayType.NO_DISPLAY
        elif datetime.datetime.now() >= self.show_time:
            log.info('Current time greater than equal to show time, '
                     'show message and update show time')
            self.show_time += self.interval
            return DisplayType.DISPLAY

    @property
    def json(self):
        return json.dumps(
            {
                'id': self.id,
                'type': self.type,
                'message': self.message
            }
        )


class Notifier(object):
    """Interface for registering and updating WebSocket clients."""

    def __init__(self):
        self.clients = []
        self.notifications = Notifications()

    def __iter_data(self):
        for message in self.notifications.get_messages():
            to_show = message.to_be_displayed()
            if to_show == DisplayType.DISPLAY:
                log.info('Showing the message: {}'.format(message.message))
                yield message
            elif to_show == DisplayType.NO_DISPLAY:
                log.info('Popping the message: {}'.format(message.message))
                self.notifications.remove_message(message.id)

    def register(self, client):
        """Register a WebSocket connection for Redis updates."""
        self.clients.append(client)
        log.info('Registering socket {}'.format(client))
        log.info('Number of registered Clients: {}'.format(len(self.clients)))

    def remove_client(self, client):
        log.info("Removing client [{}] from the list".format(client))
        self.clients.remove(client)

    def send(self, client, data):
        """Send given data to the registered client.
        Automatically discards invalid connections."""
        log.info('Send --> Number of registered Clients: {}'.format(len(self.clients)))
        try:
            log.info('Sending data to socket {}'.format(client))

            if data.type == constants.notification_type.SCHEDULE:
                delta = data.end_time - data.show_time
                data.message = data.message.format(delta.days)
            client.send(data.json)
        except Exception:
            self.clients.remove(client)

    def run(self):
        """Listens for new messages in Redis, and sends them to clients."""
        for data in self.__iter_data():
            for client in self.clients:
                gevent.spawn(self.send, client, data)

    def start(self):
        """Start the gevent thread. Iterate over the data and send messages"""
        return gevent.spawn(self.run)


def define_routes(notifier):
    """Defines all the routes for the application"""

    @sockets.route('/alerts')
    def register_for_alerts(ws):
        notifier.register(ws)
        while not ws.closed:
            # The below receive call is important to get an event when socket is closed.
            message = ws.receive()
            gevent.sleep(0.1)

        notifier.remove_client(ws)
        log.info('Connection closed for Socket: {}'.format(ws))

    @app.route('/alerts', methods=['POST'])
    def add_message():
        _message = json.loads(request.data)
        message = Message(
            _message['id'], _message['type'], _message['message'],
            show_time=dateutil.parser.parse(_message.get(
                'show_time', datetime.datetime.now().isoformat())),
            end_time=dateutil.parser.parse(_message.get(
                'end_time', datetime.datetime.now().isoformat())),
            interval=datetime.timedelta(
                seconds=_message.get('interval', 60 * 60 * 24))
        )
        notifications.add_message(message)
        return json.dumps({'status': 'success'})

    @app.route('/alerts', methods=['DELETE'])
    def remove_message():
        _message = json.loads(request.data)
        notifications.remove_message(_message['id'])
        return json.dumps({'status': 'success'})


def setup_logging(log_level=None, logs_path=None):
    # Create directory if not present
    log_dir = os.path.dirname(logs_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    format = '%(name)s: %(asctime)s %(levelname)s  %(message)s'
    level = getattr(logging, log_level or 'INFO')
    maxBytes = 1024 * 1024
    backupCount = 5

    loghandler = logging.handlers.RotatingFileHandler(
        logs_path, maxBytes=maxBytes, backupCount=backupCount)
    formatter = logging.Formatter(format)
    loghandler.setFormatter(formatter)

    rootlogger = logging.getLogger()
    rootlogger.setLevel(level)
    rootlogger.addHandler(loghandler)


def get_app(logs_path=None, log_level=None):
    notifier = Notifier()
    notifier.start()

    define_routes(notifier)
    setup_logging(log_level=log_level, logs_path=logs_path)
    return app


def run(host='0.0.0.0', port=1729, logs_path='notifier.log', log_level='INFO'):
    notifier = Notifier()
    notifier.start()

    define_routes(notifier)
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler

    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    port = port or args.port
    log_level = log_level or args.log_level
    logs_path = os.path.abspath(logs_path or args.logs_path)
    setup_logging(log_level=log_level, logs_path=logs_path)

    log.info("Starting wsnotifier on ws://{}:{} and http://{}:{}".format(host, port, host, port))

    server = pywsgi.WSGIServer((host, port), app, handler_class=WebSocketHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.warning('Interrupted. Stopping wsnotifier')


if __name__ == "__main__":
    import os

    logs_dir = os.path.join(os.path.expanduser('~/wsnotifier'), 'logs')
    run(log_level='INFO', logs_path=logs_dir + constants.NOTIFIER_LOG_FILE)
