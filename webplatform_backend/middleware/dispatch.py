from flask import make_response, send_file, g, Response

import traceback, json, time, bson, os

# from views import setup

# from lib.utils.config import Settings
# from lib.utils.db import Manager
from lib.utils.modules import Modules
#
# settings = Settings(path="/home/cee-tools/", verify=False, instance=os.environ['CEE_TOOLS_INSTANCE'])
# manager = modules.manager

from webplatform_backend.lib.responses import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseInternalServerError
from webplatform_backend.middleware.json import convert, convert_keys
from webplatform_backend.middleware.timezone import check_user_timezone

from webplatform_cli.lib.db import Manager

def handle_response(session_mgr, modules, request, module_path, isFile, **kwargs):
   session = session_mgr.get()
   if not session:
      return HttpResponseUnauthorized(json.dumps({"message": "Unauthorized to api. Either authenticate with saml or send an api token"}))

   check_user_timezone(session, request)

   devel = "WEBPLATFORM_DEVEL" in os.environ
   # manager.set_user_uid(session.uid)
   # manager.set_permissions(session.permissions)

   result = check_errors(session_mgr, modules, request, module_path, **kwargs)

   response = None

   if result['error'] == None:
      c = result['data']

      if (isFile):
         response = Response(c.read(), mimetype=c.content_type)
         response.headers['Content-Length'] = c.length
         response.headers['Content-Disposition'] = "attachment; filename=%s" % c.filename
      else:
         response_data = json.dumps(c, default=convert, ensure_ascii=False).encode("utf-8")
         response = HttpResponse(response_data)

   elif result['error']['type'] == "forbidden":
      response = HttpResponseForbidden()

   elif result['error']['type'] == "bad-request":
      response = result['error']['response']

   elif result['error']['type'] == "module-exist":
      response = HttpResponseBadRequest(json.dumps({"message": "api module doesn't exist"}))

   elif result['error']['type'] == "exception":
      if devel:
         if result['error']['exception_type'] == "KeyError":
            response = HttpResponse(json.dumps({"message": "Invalid parameters"}))
         else:
            response = HttpResponse(json.dumps({"message": "Server encountered an error. Admin has been notified of this error."}))
      else:
         raise result['error']['exception']

   else:
      response = HttpResponse(json.dumps({"message": "Server encountered an error. Admin has been notified of this error."}))

   if result['error'] != None and "response" in result['error']:
       del result['error']['response']

   logging(session_mgr, request, response, module_path, result, **kwargs)
   return response

def check_errors(session_mgr, modules, request, module_path, **kwargs):
   session = session_mgr.get() 
   output = {
      "module": None,
      "error": None,
      "data": None,
   }

   all_modules = modules.get_all_modules()
   if module_path not in all_modules.keys():
      output['module'] = None
      output['error'] = {"type": "module-exist"}
      return output

   # module_path + 'call'
   module_data = modules.get(module_path, data=True)

   module = module_data['obj']
   output['module'] = module

   access = modules.check_permissions(module_data, session_mgr.get_permissions())
   if not access:
      output['error'] = {"type": "forbidden"}
      return output

   try:
      data = module.call(**kwargs)

      if isinstance(data, HttpResponseBadRequest):
         output['error'] = {"type": "bad-request", "response": data}

      elif isinstance(data, HttpResponseForbidden):
         output['error'] = {"type": "forbidden", "response": data}

      output['data'] = data

      # else:
      #    data = HttpResponseForbidden()
      #    output['error'] = {"type": "forbidden"}

   except Exception as e:
      print(traceback.format_exc())
      output['error'] = {
         'type': 'exception',
         'exception_type': type(e).__name__,
         'stack_trace': traceback.format_exc(),
         'exception': e,
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
      }

   return output

def logging(session_mgr, request, response, module_path, result, **kwargs):
   manager = Manager()
   session = session_mgr.get()
   # get list of parent module chains not including the full path of this one
   parent_modules = []
   module_chain = module_path.split('.')
   temp_parent_chain = module_chain[0]
   for module_name in module_chain[1:]:
      parent_modules.append(temp_parent_chain)
      temp_parent_chain += '.' + module_name

   # do not log if the API call is part of the logging API (search, etc)
   if 'logging' in parent_modules:
      return

   # convert(request.headers)

   log = {
      'timestamp': Manager.get_current_time(),
      'path': module_path,
      'parent_modules': parent_modules,
      'uid': session.uid,
      'source_ip': request.remote_addr,
      'method': request.method,
      # don't yet know whether a module exists to get an action from
      'action': None,
      # permissions is represented as a set, so convert it to a list
      # else the database can't encode it
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
      },
      'response': {
         'status': response.status,
         'headers': dict(response.headers),
         'data': response.get_data()
      }
   }

   if result['module'] is not None:
      log['action'] = getattr(result['module'], 'action', None)

   if result['error'] is not None:
      # the actual exception, if present, can't and shouldn't be encoded into mongo
      # create a copy of result[error] with exception field explicitly left out
      log['failure'] = { key: result['error'][key] for key in result['error'] if key != 'exception' }

   # set up db
   db = manager.db("logging")
   db.logs.insert_one(log)
