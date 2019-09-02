from appinit_backend.lib.imports import *
import appinit_backend.app.lib.permissions.users.get as get_user


def call(**kwargs):
   manager = Manager()
   db = manager.db("appinit")

   if 'routes' in kwargs:
      old_user = get_user.call(uid=kwargs['id'])
      for route in kwargs['routes']:
         # print (application, kwargs['permissions_obj'][application])
         new_permissions = kwargs['permissions_obj'][route]
         if route in old_user['permissions_obj']:
            db.permissions.update({"_id": ObjectId(old_user['permissions_ids'][route])},
               {"$set" : {"permissions": new_permissions}})
         else:
            document = {
               "_id": ObjectId(),
               "uid": kwargs['id'],
               "permissions": new_permissions,
               "route": route,
            }
            db.permissions.insert(document)
      return get_user.call(uid=kwargs['id'])