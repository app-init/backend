from lib.imports.default import *
import lib.permissions.users.get as get_user


def call(**kwargs):
   manager = Manager()
   db = manager.db("cee-tools")
   uid = manager.get_user_uid()
   user = get_user.call(uid=uid)
   user_permissions = user["permissions_obj"]

   cursor = db.permissions.aggregate([
      {
         "$group": {
            "_id": "$application",
            "permissions": {
               "$push": "$permissions"
            }
         }
      }
   ])

   output = {}

   def is_system_admin(uid):
      data = db.permissions.find_one({
         "uid": uid,
         "application": "system",
      })

      if data is None or 'admin' not in data['permissions']:
         return False

      return True

   is_sys_admin = is_system_admin(uid)

   for app in cursor:
      app_name = app["_id"]

      # not listing app permissions if user is not a sysadmin and
      # does not have admin privileges to the app
      if not is_sys_admin:
         if app_name not in user_permissions or 'admin' not in user_permissions[app_name]:
            continue

      # if app_name not in user_permissions or 'admin' not in user_permissions[app_name]:
      #    continue

      result = set()

      for permissions in app["permissions"]:
         for perm in permissions:
            result.add(perm)

      output[app_name] = result

   return output