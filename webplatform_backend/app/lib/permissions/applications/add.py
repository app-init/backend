from lib.imports.default import *
import lib.permissions.applications.get as get_application
import lib.permissions.users.add as add_user


def call(**kwargs):
   manager = Manager()
   db = manager.db("webplatform")

   cursor = db.permissions.find_one({
      "application": kwargs["application"],
      "uid": kwargs["uid"],
   })

   if cursor is None:
      add_user.call(uid=kwargs["uid"], application=kwargs["application"])

   db.permissions.update(
      {
         "application": kwargs["application"],
         "uid": kwargs["uid"]
      },
      {
         "$push": {
            "permissions": kwargs["permission"]
         }
      }
   )

   return get_application.call(application=kwargs["application"])