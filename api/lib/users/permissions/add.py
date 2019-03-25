from lib.imports.default import *

permissions = "admin"
action = "add"

def call(*args, **kwargs):
   manager = Manager()
   permissions = manager.sessions.set_permissions(kwargs['uid'], kwargs['permission'])
   output = {
      "uid": kwargs['uid'],
      "permissions": permissions,
   }

   return output