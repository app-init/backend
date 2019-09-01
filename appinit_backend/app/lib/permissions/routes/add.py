from lib.imports.default import *
import lib.permissions.routes.get as get_route
import lib.permissions.users.add as add_user


def call(**kwargs):
   manager = Manager()
   db = manager.db("appinit")

   cursor = db.permissions.find_one({
      "route": kwargs["route"],
      "uid": kwargs["uid"],
   })

   if cursor is None:
      add_user.call(uid=kwargs["uid"], route=kwargs["route"])

   db.permissions.update(
      {
         "route": kwargs["route"],
         "uid": kwargs["uid"]
      },
      {
         "$push": {
            "permission": kwargs["permission"]
         }
      }
   )

   return get_route.call(route=kwargs["route"])