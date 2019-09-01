from lib.imports.default import *

def call(**kwargs):
   manager = Manager()
   db = manager.db("appinit")

   cursor = db.permissions.distinct("uid")

   # output = cursor
   # for i in cursor:
   #    output.append(manager.parse_cursor_object(i))

   return sorted(cursor)