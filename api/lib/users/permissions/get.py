from lib.imports.default import *

permissions = "admin"
action = "get"

def call(application, **kwargs):
   manager = Manager()
   db = manager.db('cee-tools')

   permission = None

   if "permission" in kwargs:
      permission = kwargs['permission']
   elif len(args) > 0:
      permission = args[0]
   else:
      return None

   pipeline = [
      #add a match for an application here
      { "$match": {"application": application}},
      { "$unwind": "$permissions" },
      { "$group":
         {
            "_id": "$permissions",
            "uids": {
               "$addToSet": "$uid",
            },
         }
      },
      { "$match":
         {
            "_id": permission,
         }
      },
   ]
   cursor = db.permissions.aggregate(pipeline)

   if cursor != None:
      for i in cursor:
         return i['uids']

   return None