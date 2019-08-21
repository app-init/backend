from lib.imports.default import *
import lib.permissions.descriptions.get as get_description

def call(**kwargs):
   manager = Manager()
   db = manager.db("webplatform")
   uid = manager.get_user_uid()
   user = db.permissions.find_one({
      "uid": uid,
      "application": kwargs["application"],
   })

   def is_system_admin(uid):
      data = db.permissions.find_one({
         "uid": uid,
         "application": "system",
      })

      if data is None or 'admin' not in data['permissions']:
         return False

      return True

   if not is_system_admin(uid):
      if user is None or 'admin' not in user['permissions']:
         return HttpResponseForbidden()

   pipeline = [
      {
         "$match": {
            "pid": {
               "$exists": False,
            }
         }
      },
      {
         "$group": {
            "_id": "$application",
            "users": {
               "$push": {
                  "permissions": "$permissions",
                  "uid": "$uid"
               }
            }
         }
      }
   ]

   cursor = db.permissions.aggregate(pipeline)

   applications = [app for app in cursor if app["_id"] == kwargs["application"]]
   output = []

   for app in applications:
      result = {}

      for user in app["users"]:
         if "permissions" not in user:
            print(user)
         for perm in user["permissions"]:
            if perm not in result:
               # result[perm] = []
               result[perm] = { 'users': [] }

            result[perm]['users'].append(user["uid"])

      for perm in result:
         result[perm]['description'] = get_description.call(permission=perm, application=kwargs["application"])

      output.append(result)

   if len(output) == 0:
      return []

   return output[0]
