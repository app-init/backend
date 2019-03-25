from lib.imports.default import *

action = "remove"

def call(**kwargs):
   manager = Manager()
   db = manager.db("settings")

   template_id = ObjectId(kwargs['id'])

   db.settings.remove({"t_id": template_id})
   db.templates.remove({"_id": template_id})

   return True
