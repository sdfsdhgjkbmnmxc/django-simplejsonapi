# -*- coding: utf-8 -*-
from multiprocessing import get_logger
from optparse import make_option
import SimpleHTTPServer
import SocketServer
import datetime
import os
import signal
import time
import traceback

from django import db
from django.core.mail import mail_admins
from django.core.management.base import NoArgsCommand
from django.utils import simplejson

from simplejsonapi import ACTIONS_DICT
from simplejsonapi.errors import JsonApiError
from simplejsonapi.models import JsonApiLastResponse


logger = get_logger()


class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('--host', dest='host', default='127.0.0.1',),
        make_option('--port', dest='port', default=5656, type='int'),
    )

    def handle_noargs(self, host, port, **options):
        logger = get_logger()
        server = ApiServer((host, port), ApiHandler)
        logger.info('api server started at host %s and port %s', host, port)
        while True:
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                active_children = server.active_children
                if active_children:
                    for child in active_children:
                        os.kill(child, signal.SIGINT)
                server.server_close()
                logger.info('Keyboard interrupt.')
                return
            except Exception, e:
                exc_text = traceback.format_exc()
                logger.error('%s', e)
                mail_admins('error in %s' % __name__, exc_text)


class ApiServer(SocketServer.ForkingMixIn, SocketServer.TCPServer):
    allow_reuse_address = True
    request_queue_size = 20
    max_children = 16


class ApiHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        return self.api_handle('{}')

    def do_POST(self):
        length = int(self.headers.getheader('content-length'))
        request_input = self.rfile.read(length)
        self.rfile.close()
        return self.api_handle(request_input)

    def api_handle(self, request_input):
        content = jshandle(request_input)
        self.send_response(200)
        self.send_header("Content - type", 'text/html')
        self.send_header("Content - Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


TIME_FORMAT = '%0.4f'

def jshandle(jsrequest):
    request_uid = None
    transaction_id = str(abs(hash(datetime.datetime.now())))[:7]
    try:
        logger.info('api request [%s]: %s', transaction_id, jsrequest)

        start = time.time()
        db.reset_queries()

        pyrequest = parse_json(jsrequest)

        action = pyrequest.pop('action', None)
        params = pyrequest.pop('params', {}) or {}
        request_uid = pyrequest.pop('request_uid', None)
        if request_uid:
            try:
                lr, created = JsonApiLastResponse.objects.get_or_create(request_uid=request_uid)
            except:
                raise JsonApiError('BAD_REQUEST_UID',
                    'Invalid or not unique request_uid: %s' % request_uid)
            else:
                if not created:
                    raise JsonApiError('BAD_REQUEST_UID',
                        'Not unique request_uid: %s' % request_uid)

        if action not in ACTIONS_DICT:
            raise JsonApiError('UNKNOWN_ACTION', repr(action))

        try:
            pyresponse = {
                'result': ACTIONS_DICT[action](**params),
                '_time': TIME_FORMAT % (time.time() - start),
            }
        except Exception, e:
            raise JsonApiError('SYSTEM_ERROR', repr(e))

    except JsonApiError, e:
        pyresponse = {
            'error': e.error,
            'details': e.details,
            '_time': TIME_FORMAT % (time.time() - start),
        }
    except Exception, e:
        logger.error('System error: %s', traceback.format_exc())
        mail_admins('Opossum api error at %s' % start, '\n'.join([
            jsrequest,
            traceback.format_exc()
        ]))
        pyresponse = {
            'error': 'SYSTEM_ERROR',
            'details': unicode(e),
            '_time': TIME_FORMAT % (time.time() - start),
        }
    jsresponse = compose_json(pyresponse)
    logger.info('api response [%s]: %s', transaction_id, jsresponse)

    if request_uid:
        lr.jsrequest = jsrequest
        lr.jsresponse = jsresponse
        lr.save()

    return jsresponse


def parse_json(s):
    try:
        return simplejson.loads(s)
    except Exception, e:
        raise JsonApiError('PARSE_JSON_ERROR', unicode(e))


def compose_json(data):
    try:
        return simplejson.dumps(data)
    except Exception, e:
        logger.error('compose_json(%r) error: %s', data, traceback.format_exc())
        return (
            '''{'''
            '''"error": "%s",'''
            '''"details": "Can\'t compose JSON (%s): %r"'''
            '''}'''
        ) % ('SYSTEM_ERROR', e.__class__.__name__, data)
