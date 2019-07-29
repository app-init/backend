from lib.imports.default import *

def call(**kwargs):
   manager = Manager()
   db = manager.db("webplatform")

   permission = kwargs["permission"]
   application = kwargs["application"]

   cursor = db.permissions.find_one(
      {
         "pid": permission,
         "application": application,
      }
   )

   if cursor is None:
      return None

   return cursor["description"]