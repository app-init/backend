from bson.objectid import ObjectId
from datetime import datetime, timedelta
import binascii, os

class Session(object):
   def __init__(self, db):
      self.db = db
      self.apps = self.list_applications()

   def __parse_cursor(self, obj):
      class Object(object):
         pass

      output = Object()

      for key, value in obj.items():
         if key == '_id':
            continue
         else:
            setattr(output, key, value)

      setattr(output, "permissions", self.get_permissions(obj['uid']))

      return output

   def set_session(self, uid, ip):
      now = datetime.now()
      doc = {
         "_id": ObjectId(),
         "ip": ip,
         "uid": uid,
         "expires": now + timedelta(hours=24),
         "token": self.token(),
      }

      self.db.sessions.insert(doc)

      return self.__parse_cursor(doc)

   def get_session(self, ip=None, uid=None, token=None):
      if token != None:
         session = self.db.sessions.find_one({"token": token, "ip": ip})

      elif uid != None and ip != None:
         session = self.db.sessions.find_one({"uid": uid, "ip": ip})

      elif uid != None and ip == None:
         sessions = []
         cursor = self.db.sessions.find({"uid": uid})
         for i in cursor:
            i['permissions'] = self.get_permissions(uid)
            sessions.append(i)

         return sessions

      else:
         session = None

      if session == None:
         return self.set_session(uid, ip)

      return self.__parse_cursor(session)

   def get_permissions(self, uid):
      cursor = self.db.permissions.find({"uid": uid})

      if cursor == None:
         cursor = self.__set_default_permissions(self, uid)

      output = {}
      for i in cursor:
         output[i['application']] = i['permissions']

      return output

   def __set_default_user_permissions(self, uid):
      documents = [
         {
            "name": "system",
            "permissions": [],
            "uid": uid
         }
      ]
      for app in self.apps:
         d = {
            "permissions": [],
            "application": app['name'],
            "uid": uid
         }
         documents.append(d)

      self.db.permissions.insert(documents)
      return documents

   # really don't need this method right now but it might come in handy at some point
   def update(self, uid, ip):
      now = datetime.now()

      update = {
         "expires": now + timedelta(hours=24),
         "token": self.token(),
      }

      self.db.sessions.update({"uid": uid, "ip": ip}, {"$set": update})

      return self.get(uid=uid, ip=ip)

   def validate(self, uid, token):
      user = self.db.users.find_one({"uid": uid})
      if user is None or "token" not in user:
         return True

      return user['token'] == token

   def token(self, n=8):
      return binascii.hexlify(os.urandom(n)).decode('UTF-8')

   def list_applications(self):
      return [
         {
            "name": "support-exceptions",
            "module_base": "se",
            "permissions": [],
         },
         {
            "name": "dashboards",
            "module_base": "dashboards",
            "permissions": [],
         },
         {
            "name": "bzcompliance",
            "module_base": "bzcompliance",
            "permissions": [],
         },
         {
            "name": "findsbr",
            "module_base": "findsbr",
            "permissions": [],
         },
         {
            "name": "release-planning",
            "module_base": "release_planning",
            "permissions": [],
         },
         {
            "name": "api-info",
            "module_base": "api_info",
            "permissions": [],
         },
         {
            "name": "jobs",
            "module_base": "jobs",
            "permissions": [],
         },
      ]
