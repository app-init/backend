from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

from flask import Flask, render_template, session, request
app = Flask(__name__)

server = pywsgi.WSGIServer(('127.0.0.1', 3001), app,
    handler_class=WebSocketHandler)

if __name__ == '__main__':
   server.serve_forever()

# import os
# import gevent.socket
# import redis.connection
# redis.connection.socket = gevent.socket
# os.environ.update(DJANGO_SETTINGS_MODULE='pk.settings.settings')
# from ws4redis.uwsgi_runserver import uWSGIWebsocketServer
# application = uWSGIWebsocketServer()
