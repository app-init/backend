#!/bin/python3.5

import sys

# preventing __pycache__ from being created
sys.dont_write_bytecode = True

from flask import Flask, redirect, jsonify, make_response, send_file, request, g
from querystring_parser import parser
import urllib

import simplejson, os, traceback

sys.stdout = open("/home/cee-tools/logs/debug.log", "a+")

from werkzeug.contrib.fixers import ProxyFix

sys.path.append("/home/cee-tools/api/")
sys.path.append("/home/cee-tools/apps/")

from application.views import saml
from application.views.lib import debug, setup, dispatch
from application.middleware import token, json
from application.views.lib.responses import HttpResponse, HttpResponseBadRequest, HttpResponseInternalServerError
from application.views.lib.jsonify import convert
from application.views.lib.timezone import check_user_timezone

from lib.utils.modules import Modules
from lib.utils.db import Manager
from lib.utils.config import Settings

settings = Settings(path="/home/cee-tools/", verify=False)
modules = Modules(settings)
manager = modules.manager

app = Flask(__name__)
# app.debug = True
app.wsgi_app = ProxyFix(app.wsgi_app)
app.use_x_sendfile = True

@app.before_request
def token_middleware():
   manager.set_hostname(request.host)

   session = token.process_request(request)

   if session != None:
      manager.set_user_uid(session.uid)

   g.settings = settings
   g.session = session

@app.route("/metadata")
def metadata():
   protocol = request.headers['X-Forwarded-Proto']
   port = request.headers['X-Nginx-Port']
   host = request.headers['Host'].split(":")[0]

   if "X-Nodejs" in request.headers:
      if "0.0.0.0" in host:
         host = host.replace("0.0.0.0:8080", "localhost")
         if "X-Nodejs-Host" in request.headers:
            host = request.headers['X-Nodejs-Host']

   if port in host:
      base = (protocol, host)
      url = '%s://%s/callback/' % base
   else:
      base = (protocol, host, port)
      url = '%s://%s:%s/callback/' % base

   if len(request.args) > 0:
      is_config = request.args.get("config", False)
      if is_config:
         config_file = open(settings.get_config("flask")['saml-settings'] + "/settings.json")
         config = simplejson.load(config_file)
         config['sp']['assertionConsumerService']['url'] = url
         config_file.close()

         config_file = open(settings.get_config("flask")['saml-settings'] + "/advanced_settings.json")
         advanced_config = simplejson.load(config_file)
         config_file.close()

         return HttpResponse(simplejson.dumps({"config": config, "advanced": advanced_config}, indent=2))

   return saml.metadata(request)

@app.route("/api/<path:path>", methods=['POST', 'GET'])
def api(path):
   isFile = False
   module_path = ".".join([_f for _f in path.replace("-", "_").split("/") if _f])

   if request.method == "POST":
      if "cee-tools-request" in request.headers and \
         request.data != b'':

         kwargs = simplejson.loads(request.data)

         if 'token' in kwargs:
            del kwargs['token']
      else:
         kwargs = dict()

         for key, value in request.json.items():
            if key == 'token':
               continue

            kwargs[key] = value
   else:
      kwargs = dict()
      if len(request.args) > 0:
         url = request.full_path.split("?")[1:]
         kwargs = parser.parse("&".join(url))

         q = urllib.parse.urlparse(request.full_path)
         request_args = urllib.parse.parse_qs(q.query)

         for key, value in request_args.items():
            if key == 'token':
               continue

            if len(value) == 1:
               kwargs[key] = value[0]
            else:
               kwargs[key] = value

   args = (
      request,
      module_path,
      isFile
   )

   response = None

   try:
      response = dispatch.handle_response(*args, **kwargs)
   except Exception as e:
      print(traceback.format_exc())
      log = {
         "module": None,
         "data": None,
         "error": {
            'type': 'exception',
            'exception_type': type(e).__name__,
            'stack_trace': traceback.format_exc(),
            'exception': e,
            'permissions': list(g.session.permissions),
            'request': {
               'headers': dict(request.headers),
               'data': {
                  'form': request.form,
                  'args': request.args,
                  'data': request.data,
               },
               'kwargs': simplejson.dumps(kwargs, default=convert, encoding="utf-8"),
               'cookies': request.cookies,
            }
         },
      }

      response = HttpResponseInternalServerError(simplejson.dumps({"message": "Server encountered an error. Admin has been notified of this error."}))
      dispatch.logging(request, response, module_path, log, **kwargs)

      if settings.get_instance() == "devel":
         response = None

   return response

@app.route("/upload", methods=['POST', 'PUT'])
def upload():
   isFile = False
   module_path = "files.add"

   files = request.files.getlist('files')

   form_data = request.form.get('data')
   if  form_data != None:
      form_data =  simplejson.loads(form_data)

   if len(files) == 0 and 'url' not in form_data:
      return HttpResponseBadRequest(simplejson.dumps({"message": "Did not POST a file"}))

   kwargs = form_data
   kwargs['uid'] = g.session.uid
   kwargs['files'] = files

   args = (
      request,
      module_path,
      isFile
   )
   return dispatch.handle_response(*args, **kwargs)

@app.route("/download/<string:file_id>", methods=['GET'])
def download(file_id):
   isFile = True
   module_path = "files.download"
   args = (
      request,
      module_path,
      isFile
   )
   return dispatch.handle_response(*args, id=file_id)

@app.route("/callback/", methods=['POST', 'GET'])
def saml_auth():
   if request.method == 'GET':
      return saml.get(request)
   else:
      return saml.post(request)

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=8080)
