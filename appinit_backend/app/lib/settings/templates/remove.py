from appinit_backend.lib.imports import *

action = "remove"

def call(**kwargs):
   manager = Manager()
   db = manager.db("appinit")

   template_id = ObjectId(kwargs['id'])

   db.settings.remove({"t_id": template_id})
   db.settings_templates.remove({"_id": template_id})

   return True
