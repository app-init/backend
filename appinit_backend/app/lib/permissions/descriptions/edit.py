from lib.imports.default import *
import lib.permissions.applications.get as get_application


def call(**kwargs):
   manager = Manager()
   db = manager.db("webplatform")

   permission = kwargs["permission"]
   application = kwargs["application"]
   description = kwargs["description"]

   db.permissions.update(
      {
         "pid": permission,
         "application": application,
      },
      {
         "$set": {
            "description": description,
         }
      },
      upsert=True
   )

   return get_application.call(application=application)