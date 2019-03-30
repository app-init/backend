from webplatform_cli.lib.db import dbManager
from lib.utils.sessions import Session

class BaseUser:
   def __init__(self, uid):
      self.manager = dbManager()
      self.sessions = Sessions(self.manager.db("webplatform"))

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
