from flask import make_response, redirect, g
from urllib.parse import urlparse

from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.settings import OneLogin_Saml2_Settings
from onelogin.saml2.utils import OneLogin_Saml2_Utils
from onelogin.saml2.constants import OneLogin_Saml2_Constants

import json

from views.lib.responses import *
# from lib.utils.config import Settings
# from lib.utils.db import Manager
# settings, modules = setup.imports()
# manager = modules.manager()

def prepare_saml_request(request):
   url_data = urlparse(request.url)
   return {
      'http_host': request.host,
      'script_name': request.path,
      'server_port': request.headers['X-Nginx-Port'],
      'get_data': request.args.copy(),
      'post_data': request.form.copy()
   }

def get_certs(settings):
   output = {
      "x509cert": "",
      "privateKey": ""
   }
   instance = settings.get_instance()

   if instance != "prod":
      return output

   certs_path = settings.get_config("flask")['saml-certs']
   certs_files = [
      "%s/sp.crt" % certs_path,
      "%s/sp.key" % certs_path,
   ]

   for path in certs_files:
      with open(path) as target:
         file_data = ""
         for line in target:
            if "END" in line or "BEGIN" in line:
               continue

            file_data += line.strip()

         if ".crt" in path:
            output['x509cert'] = file_data
         else:
            output['privateKey'] = file_data

   return output

def setup_auth(request):
   settings = Settings()
   saml_config_file = open(settings.get_config("flask")['saml-settings'] + "/settings.json")
   saml_config = son.load(saml_config_file)
   saml_config_file.close()

   check = request.form.get("SAMLResponse", None)

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
      if port == "443":
         base = (protocol, host)
         url = '%s://%s/callback/' % base
      else:
         base = (protocol, host, port)
         url = '%s://%s:%s/callback/' % base

   saml_config['sp']['assertionConsumerService']['url'] = url

   for key, value in get_certs(settings).items():
      saml_config['sp'][key] = value

   req = prepare_saml_request(request)
   auth = OneLogin_Saml2_Auth(req, saml_config)

   saml_settings = auth.get_settings()
   metadata = saml_settings.get_sp_metadata()
   errors = saml_settings.validate_metadata(metadata)
   if len(errors) > 0:
       print("Error found on Metadata: %s" % (', '.join(errors)))

   return auth

def get(request):
   manager = Manager()
   settings = Settings()
   cookies = request.cookies

   protocol = request.headers['X-Forwarded-Proto']
   host = request.headers['HOST'].split(":")[0]
   port = request.headers['X-Nginx-Port']

   flask_settings = settings.get_config("flask")

   if "login" in cookies or "default-user" in flask_settings:
      if port != 443 or port != 80:
         base = (protocol, host, port)
         return_to = "%s://%s:%s/" % base
         return_to_url = request.args.get('q', False)
      else:
         base = (protocol, host)
         return_to = "%s://%s/" % base
         return_to_url = request.args.get('q', False)

      if return_to_url:
         return_to = return_to_url

      response = redirect(return_to)

      if "default-user" in flask_settings:
         uid = flask_settings['default-user']
         response.set_cookie("login", uid, max_age=86400)
      else:
         uid = cookies['login']

      data = {
         "uid": uid,
         "is_auth": True,
         "redirect": False,
      }

      uid = data['uid']
      data['user'] = manager.saml_auth(uid)
      ip = request.remote_addr

      session = manager.get_session(ip=ip, uid=uid)

      return response

   if "X-Nodejs" in request.headers:
      if "0.0.0.0" in host:
         host = request.headers['X-Nodejs-Host']

   if port != 443 or port != 80:
      base = (protocol, host, port)
      q = request.args.get('q', '%s://%s:%s/' % base)

      return_to = "%s://%s:%s/callback/" % base + "?q=%s" % (q)

      auth = setup_auth(request)
      response = auth.login(return_to=return_to)

      return redirect(response)

   else:
      base = (protocol, host)
      q = request.args.get('q', '%s://%s/' % base)

      return_to = "%s://%s/callback/" % base + "?q=%s" % (q)

      auth = setup_auth(request)
      response = auth.login(return_to=return_to)

      return redirect(response)

def metadata(request):
   auth = setup_auth(request)

   auth_settings = auth.get_settings()
   metadata = auth_settings.get_sp_metadata()

   errors = auth_settings.validate_metadata(metadata)

   if len(errors) == 0:
      resp = make_response(metadata, 200)
      resp.headers['Content-Type'] = 'text/xml'
   else:
      resp = make_response(', '.join(errors), 500)

   return resp

def post(request):
   manager = Manager()
   auth = setup_auth(request)
   auth.process_response()

   is_auth = auth.is_authenticated()
   response = auth.get_attributes()

   data = {}
   for key, value in response.items():
      if isinstance(value, list):
         if len(value) > 1:
            data[key] = value
         else:
            data[key] = value[0]
      else:
         data[key] = value

   if is_auth:
      uid = data['uid']
      data['user'] = manager.saml_auth(uid)
      ip = request.remote_addr

      session = manager.get_session(ip=ip, uid=uid)

      return_to = "/"
      if "RelayState" in request.form:
         return_to = request.form['RelayState']

      response = redirect(return_to)
      response.set_cookie("login", uid, max_age=86400)
      return response
   else:
      return HttpResponseUnauthorized(simplejson.dumps({"message": "Error authenticated contact application admin."}))
