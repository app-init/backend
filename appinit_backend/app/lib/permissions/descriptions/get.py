from appinit_backend.lib.imports import *

def call(**kwargs):
   manager = Manager()
   db = manager.db("appinit")

   cursor = db.permissions.find_one(
      {
         "pid": kwargs['permission'],
         "route": kwargs['route'],
      }
   )

   if cursor is None:
      return None

   return cursor["description"]