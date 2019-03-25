from ldap3 import Server, Connection, AUTH_SIMPLE, ALL, ALL_ATTRIBUTES, SUBTREE
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import binascii, os, simplejson, hashlib

from lib.utils.config import Settings
from lib.utils.sessions import Session

class Manager(object):
   __instance = None

   mongo_client = None
   host = None
   config = None
   settings = None
   db_host = None
   db_port = None
   ldap_server = "ldap.corp.redhat.com"
   sessions = None

   __db = None

   def __new__(cls, *args, **kwargs):
      if Manager.__instance is None:
         Manager.__instance = object.__new__(cls)
         Manager.__instance.__set_class()

      return Manager.__instance

   def __init__(self, db=None, new_client=False):
      self.setup(db)


   def __set_class(self):
      Manager.settings = Settings()
      Manager.config = Manager.settings.get_config("mongodb")

      Manager.db_host = Manager.settings.get_config("mongodb")['host']
      Manager.db_port = Manager.settings.get_config("mongodb")['port']

      # Manager.db_host = "mowens.hq.gsslab.rdu.redhat.com"
      # Manager.db_port = 27217

      # print('Should only see this on first request')
      Manager.mongo_client = MongoClient(Manager.db_host, Manager.db_port, connect=False)
      Manager.ldap_server = Manager.ldap_server

      Manager.sessions = Session(Manager.mongo_client["cee-tools"])

   def setup(self, db):
      self.mongo_client = Manager.mongo_client
      self.host = Manager.host
      self.config = Manager.config
      self.ldap_server = Manager.ldap_server
      self.settings = Manager.settings
      self.sessions = Manager.sessions

      if db != None:
         self.__db = Manager.mongo_client[db]
      else:
         self.__db = Manager.mongo_client["cee-tools"]

   def db(self, db=None):
      if db == None:
         return self.__db
      else:
         return self.mongo_client[db]

   def new_connection(self):
      self.mongo_client = MongoClient(self.host, self.port)

   def drop_database(self, db):
      self.mongo_client.drop_database(db)

   def login(self, username, password, login_type=None, uid=None):
      output = {}

      if login_type == "bugzilla":
         response = self.bugzilla_api.login(username, password)

         if uid == None:
            return None

         self.add_bugzilla_user(uid, response)

         return response

      if login_type == "kerberos":
         is_login, user = self.ldap_auth(username, password)

         output['uid'] = user['uid'][0]
         output['auth'] = is_login

         if is_login:
            pass
            #self.users.remove_bugzilla_token(user['uid'][0])

         return output

   def ldap_lookup(self, look_up):
      #user_dn = "uid=" + look_up + ",ou=users,dc=redhat,dc=com"
      base_dn = "dc=redhat,dc=com"

      search_filter = "(uid={})".format(look_up)

      server = Server("ldap.corp.redhat.com",use_ssl=True,get_info=ALL)
      connect = Connection(server, raise_exceptions=True)

      #try:
      connect.bind()

      kwargs = {
         "search_base": base_dn,
         "search_filter": search_filter,
         "search_scope": SUBTREE,
         "attributes": ALL_ATTRIBUTES,
      }

      connect.search(**kwargs)
      result = simplejson.loads(connect.entries[0].entry_to_json())['attributes']
      output = {}
      for key, value in list(result.items()):
         if len(value) == 1 and isinstance(value, list):
            output[key] = value[0]
         else:
            output[key] = value

      return output

   def ldap_search(self, search_filter, base_dn=None):
      server = Server("ldap.corp.redhat.com",use_ssl=True,get_info=ALL)
      connect = Connection(server, raise_exceptions=True)
      connect.bind()

      if base_dn == None:
         base_dn = "dc=redhat,dc=com"

      kwargs = {
         "search_base": base_dn,
         "search_filter": search_filter,
         "search_scope": SUBTREE,
         "attributes": ALL_ATTRIBUTES,
      }

      connect.search(**kwargs)

      output = []
      for i in range(0, len(connect.entries)):
         entry = connect.entries[i]
         result = simplejson.loads(entry.entry_to_json())['attributes']
         output.append(result)

      return output

   def saml_auth(self, uid):
      result = self.ldap_lookup(uid)

      return result

   def ldap_auth(self, username, password):
      user_dn = "uid=" + username + ",ou=users,dc=redhat,dc=com"
      base_dn = "dc=redhat,dc=com"

      search_filter = "(uid={})".format(username)

      server = Server("ldap.corp.redhat.com",use_ssl=True,get_info=ALL)
      connect = Connection(server, raise_exceptions=True, authentication=AUTH_SIMPLE, user=user_dn, password=password)

      try:
         connect.bind()

         kwargs = {
            "search_base": base_dn,
            "search_filter": search_filter,
            "search_scope": SUBTREE,
            "attributes": ALL_ATTRIBUTES,
         }

         connect.search(**kwargs)
         result = simplejson.loads(connect.entries[0].entry_to_json())['attributes']

         self.add_kerberos(result)
         return True, result

      except :
         connect.unbind()
         return False, None

   def get_direct_reports(self, manager):
      base_dn = "ou=users,dc=redhat,dc=com"
      lookup = "uid=%s,%s" % (manager, base_dn)
      search_filter = "(manager={})".format(lookup)
      manager = self.ldap_search(search_filter)

      return manager
      #shouldn't need to do this
      #self.sessions.set_permissions(document['uid'], init=True)

   def get_picture_url(self, email):
      email = email.encode('utf-8')
      return "https://secure.gravatar.com/avatar/" + hashlib.md5(email).hexdigest() + "?s=100&d=identicon"

   def add_bugzilla_user(self, uid, data):
      self.__db.users.update({"uid": uid}, {"$set": { "bugzilla": data} })

   def remove_bugzilla_token(self, uid):
      self.__db.users.update({"uid": uid}, {"$unset": { "bugzilla.token": 1 } })

   def set_hostname(self, hostname):
      self.host = hostname
      Manager.host = hostname
      return hostname

   def get_hostname(self):
      return self.host

   def get_http_port(self):
      return self.http_port

   def set_user_uid(self, uid):
      self.user_uid = uid

   def get_user_uid(self):
      return self.user_uid

   def set_permissions(self, permissions):
      self.permissions = permissions

   def get_permissions(self, app=None):
      if app == None:
         return self.permissions
      else:
         if app in self.permissions:
            return self.permissions[app]
         else:
            return []

   def get_session(self, **kwargs):
      return self.sessions.get_session(**kwargs)

   def get_all_sessions(self, uid):
      return self.sessions.get_session(uid=uid)

   def validate_session(self, *args):
      return self.sessions.validate(*args)

   def get_application(self, module=None, app=None):
      applications = [
         {
            "name": "support-exceptions",
            "title": "Support Exceptions",
            "module_base": "se",
            "permissions": [],
         },
         {
            "name": "dashboards",
            "title": "Dashboards",
            "module_base": "dashboards",
            "permissions": [],
         },
         {
            "name": "bzcompliance",
            "title": "Bugzilla Compliance",
            "module_base": "bzcompliance",
            "permissions": [],
         },
         {
            "name": "findsbr",
            "title": "FindSbr",
            "module_base": "findsbr",
            "permissions": [],
         },
         {
            "name": "release-planning",
            "title": "Release Planning",
            "module_base": "rp",
            "permissions": [],
         },
         {
            "name": "api-info",
            "title": "Api Info",
            "module_base": "api_info",
            "permissions": [],
         },
         {
            "name": "jobs",
            "title": "Job Runner",
            "module_base": "jobs",
            "permissions": [],
         },
      ]

      if app is not None:
         for a in applications:
            if a['name'] == app:
               return a['title']

         return None
      else:
         if module == None:
            return applications

         for app in applications:
            if app['module_base'] == module.split(".")[0]:
               return app['name']

         return "system"

   def parse_cursor_object(self, cursor):
      if cursor == None or cursor == "":
         return

      if "_id" in cursor.keys():
         _id = cursor['_id']
         del cursor['_id']
         cursor['id'] = _id

      return cursor

   @staticmethod
   def get_current_time():
      return datetime.utcnow()

   @staticmethod
   def get_formatted_time():
      return Manager.get_current_time().isoformat()

   @staticmethod
   def timestamp_to_datetime(ts):
      return datetime.utcfromtimestamp(ts)

   @staticmethod
   def local_to_utc(date, local_tz):
      from datetime import datetime
      from pytz import timezone
      import pytz
      tz = timezone(local_tz)
      aware = tz.localize(date)
      return pytz.utc.normalize(aware)

   @staticmethod
   def local_timestamp_to_datetime(ts):
      from datetime import datetime
      date = datetime.fromtimestamp(ts)

      return Manager.local_to_utc(date, 'US/Eastern')

   def utc_to_local(date, tz):
      import pytz
      local_tz = pytz.timezone(tz)
      local_date = date.replace(tzinfo=pytz.utc).astimezone(local_tz)
      return local_tz.normalize(local_date)
