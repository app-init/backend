from lib.imports.default import *
import lib.permissions.apis.get as get_api


def call(**kwargs):
   manager = Manager()
   db = manager.db("cee-tools")

   if "id" in kwargs:
      if "safe_name" in kwargs:
         del kwargs["safe_name"]

      cursor = db.permissions.find_one({"module": kwargs["module"]})

      if cursor == None:
         module = {
            "module": kwargs['module'],
            "application": kwargs['application'],
            "permissions": kwargs['permissions']
         }
         db.permissions.insert(module)
         return module

      else:
         cursor = manager.parse_cursor_object(cursor)
         document = {}

         if "permissions" in kwargs and kwargs["permissions"] != cursor["permissions"]:
            document["permissions"] = kwargs["permissions"]
         else:
            document["permissions"] = cursor["permissions"]

         db.permissions.update({"module": kwargs["module"]}, {"$set": document})

      # every api has this added as an attribute
      # it reinitializes the change
      # Modules.reinit()
      return get_api.call(id=kwargs["module"])