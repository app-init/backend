from appinit_backend.lib.imports import *
import appinit_backend.app.lib.permissions.descriptions.get as get_description


def call(**kwargs):
   manager = Manager()
   db = manager.db("webplatform")

   permission = kwargs["permission"]
   application = kwargs["application"]
   description = kwargs["description"]

   document = {
      "_id": ObjectId(),
      "pid": permission,
      "application": application,
      "description": description,
   }

   db.permissions.insert(document)

   return get_description.call(application=application, permission=permission)