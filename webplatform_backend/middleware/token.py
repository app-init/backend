# from lib.utils.db import Manager
from flask import g
from lib.utils.modules import Modules
from lib.utils.config import Settings
from querystring_parser import parser
import simplejson, os

settings = Settings(path="/home/cee-tools/", verify=False, instance=os.environ['CEE_TOOLS_INSTANCE'])
modules = Modules(settings)
manager = modules.manager

def process_request(request):
   ip = request.remote_addr

   if "login" not in request.cookies and "Cee-Tools-Request" not in request.headers:
      return handle_api(manager, request)
   else:
      return handle_fronend_api(manager, request)

def handle_fronend_api(manager, request):
   uid = request.cookies.get('login', False)

   if not uid:
      return None

   ip = request.remote_addr

   session = manager.get_session(uid=uid, ip=ip)

   return session

def handle_api(manager, request):
   token = None
   session = None
   if request.headers.get("token", False):
      token = request.headers.get('token')

   elif request.method == "POST":
      if request.data != b'':
         if b'SAML' not in request.data:
            data = simplejson.loads(request.data)
            if "token" in data:
               token = data['token']
      else:
         token = request.form.get("token")

   elif request.method == "GET":
      url = request.full_path.split("?")[1:]
      args = parser.parse("&".join(url))
      token = args.get("token", None)

   if token != None:
      db = manager.db("cee-tools")
      user = db.users.find_one({"token": token})

      if user != None:
         uid = user['uid']
         check = manager.validate_session(uid, token)

         if check:
            session = manager.get_session(uid=uid, ip=request.remote_addr)

   return session
