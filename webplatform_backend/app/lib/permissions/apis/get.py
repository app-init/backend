from lib.imports.default import *

def call(**kwargs):
   manager = Manager()
   db = manager.db("cee-tools")

   cursor = db.permissions.find_one({"module": kwargs["id"]})
   module = manager.parse_cursor_object(cursor)

   if "permissions" not in module:
      module['permissions'] = []
      
   return module
