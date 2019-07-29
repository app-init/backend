#!/bin/python3.5

import sys

# preventing __pycache__ from being created
sys.dont_write_bytecode = True

from flask import Flask, redirect, jsonify, make_response, send_file, request, g
from querystring_parser import parser
import urllib, json, os, traceback

# sys.stdout = open("/home/cee-tools/logs/debug.log", "a+")

from werkzeug.contrib.fixers import ProxyFix

# sys.path.append("/home/cee-tools/api/")
# sys.path.append("/home/cee-tools/apps/")

controller_path = os.path.dirname(os.path.realpath(__file__))
base_path = os.path.abspath(os.path.join(controller_path))

if base_path not in sys.path:
   sys.path.append(base_path)

from webplatform_backend.lib.responses import HttpResponse, HttpResponseBadRequest, HttpResponseInternalServerError

from webplatform_backend.middleware import dispatch
from webplatform_backend.middleware.json import convert, convert_keys
from webplatform_backend.middleware.timezone import check_user_timezone

from webplatform_auth.middleware import token
from webplatform_auth.lib import SessionManager

from lib.utils.modules import Modules

from webplatform_cli.lib.config import Settings
from webplatform_cli.lib.db import Manager

manager = Manager()
settings = Settings(path=base_path, verify=False)
session_mgr = SessionManager(manager)

modules = Modules(settings, manager)

app = Flask(__name__)
# app.debug = True
app.wsgi_app = ProxyFix(app.wsgi_app)
app.use_x_sendfile = True

@app.before_request
def token_middleware():
   token.process_request(session_mgr, request=request)

@app.route("/api/<path:path>", methods=['POST', 'GET'])
def api(path):
   session = session_mgr.get()

   print('start', session)

   isFile = False
   module_path = ".".join([_f for _f in path.replace("-", "_").split("/") if _f])

   if request.method == "POST":
      if "webplatform-request" in request.headers and \
         request.data != b'':

         kwargs = json.loads(request.data)

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
      session_mgr,
      modules,
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
            'permissions': list(session_mgr.get_permissions()),
            'request': {
               'headers': dict(request.headers),
               'data': {
                  'form': request.form,
                  'args': request.args,
                  'data': request.data,
               },
               'kwargs': json.dumps(kwargs, default=convert, ensure_ascii=False).encode("utf-8"),
               'cookies': request.cookies,
            }
         },
      }

      response = HttpResponseInternalServerError(json.dumps({"message": "Server encountered an error. Admin has been notified of this error."}))
      dispatch.logging(session_mgr, request, response, module_path, log, **kwargs)

      if "WEBPLATFORM_DEVEL" in os.environ:
         response = None

   return response

@app.route("/upload", methods=['POST', 'PUT'])
def upload():
   isFile = False
   module_path = "files.add"

   files = request.files.getlist('files')

   form_data = request.form.get('data')
   if  form_data != None:
      form_data =  json.loads(form_data)

   if len(files) == 0 and 'url' not in form_data:
      return HttpResponseBadRequest(json.dumps({"message": "Did not POST a file"}))

   kwargs = form_data
   kwargs['uid'] = session_mgr.get().uid
   kwargs['files'] = files

   args = (
      session_mgr,
      modules,
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
      session_mgr,
      modules,
      request,
      module_path,
      isFile
   )
   return dispatch.handle_response(*args, id=file_id)

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=8080)
