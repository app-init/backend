from appinit_backend.lib.imports import *
import appinit_backend.app.lib.permissions.users.get as get_user


def call(**kwargs):
   manager = Manager()
   db = manager.db("appinit")

   document = {
      "_id": ObjectId(),
      "uid": kwargs['uid'],
      "permissions": [],
      "route": kwargs['route'],
   }
   db.permissions.insert(document)

   return get_user.call(uid=kwargs['uid'])