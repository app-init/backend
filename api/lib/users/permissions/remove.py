from lib.imports.default import *

permissions = "admin"
action = "remove"

def call(*args, **kwargs):
   manager = Manager()
   permissions = manager.sessions.remove_permission(kwargs['uid'], kwargs['permission'])
   output = {
      "uid": kwargs['uid'],
      "permissions": permissions,
   }

   return output