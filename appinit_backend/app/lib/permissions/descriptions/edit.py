from lib.imports.default import *
import lib.permissions.routes.get as get_route


def call(**kwargs):
   manager = Manager()
   db = manager.db("webplatform")

   permission = kwargs["permission"]
   route = kwargs["route"]
   description = kwargs["description"]

   db.permissions.update(
      {
         "pid": permission,
         "route": route,
      },
      {
         "$set": {
            "description": description,
         }
      },
      upsert=True
   )

   return get_route.call(route=route)