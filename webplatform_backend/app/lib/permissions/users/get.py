from lib.imports.default import *

def call(**kwargs):
   manager = Manager()
   db = manager.db("webplatform")

   pipeline = [
      {
         "$match": {
            "uid": kwargs['uid'],
         },
      },
      {
         "$group": {
            "_id": "$uid",
            "permissions_list": {
               "$addToSet": {
                  "application": "$application", "permissions": "$permissions", "permission_id": "$_id",
               },
            },
            "applications": {
               "$addToSet":
                  "$application",
            }
         },
      },
   ]

   cursor = db.permissions.aggregate(pipeline)

   output = []
   for i in cursor:
      permissions_obj = {}
      permissions_ids = {}
      for permission in i['permissions_list']:
         if "application" in permission:
            permissions_obj[permission['application']] = permission['permissions']
            permissions_ids[permission['application']] = permission['permission_id']

      i['permissions_obj'] = permissions_obj
      i['permissions_ids'] = permissions_ids
      del i['permissions_list']
      output.append(manager.parse_cursor_object(i))

   if len(output) == 0:
      return None

   return output[0]