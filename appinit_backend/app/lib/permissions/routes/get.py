from lib.imports.default import *
import lib.permissions.descriptions.get as get_description

def call(**kwargs):
   manager = Manager()
   db = manager.db("appinit")
   uid = manager.get_user_uid()
   user = db.permissions.find_one({
      "uid": uid,
      "route": kwargs["route"],
   })

   def is_system_admin(uid):
      data = db.permissions.find_one({
         "uid": uid,
         "route": "system",
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
            "_id": "$route",
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

   routes = [route for route in cursor if route["_id"] == kwargs["route"]]
   output = []

   for route in routes:
      result = {}

      for user in route["users"]:
         if "permissions" not in user:
            print(user)
         for perm in user["permissions"]:
            if perm not in result:
               # result[perm] = []
               result[perm] = { 'users': [] }

            result[perm]['users'].append(user["uid"])

      for perm in result:
         result[perm]['description'] = get_description.call(permission=perm, route=kwargs["application"])

      output.append(result)

   if len(output) == 0:
      return []

   return output[0]