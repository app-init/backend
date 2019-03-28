from lib.imports.default import *
import lib.permissions.users.get as get_user


def call(**kwargs):
   manager = Manager()
   db = manager.db("cee-tools")

   if 'applications' in kwargs:
      old_user = get_user.call(uid=kwargs['id'])
      for application in kwargs['applications']:
         # print (application, kwargs['permissions_obj'][application])
         new_permissions = kwargs['permissions_obj'][application]
         if application in old_user['permissions_obj']:
            db.permissions.update({"_id": ObjectId(old_user['permissions_ids'][application])},
               {"$set" : {"permissions": new_permissions}})
         else:
            document = {
               "_id": ObjectId(),
               "uid": kwargs['id'],
               "permissions": new_permissions,
               "application": application,
            }
            db.permissions.insert(document)
      return get_user.call(uid=kwargs['id'])