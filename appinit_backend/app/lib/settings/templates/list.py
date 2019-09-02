from appinit_backend.lib.imports import *
import appinit_backend.app.lib.settings.templates.parse_cursor as parse_cursor

def call(**kwargs):
   manager = Manager()
   db = manager.db('appinit')

   cursor = db.settings_templates.find()

   output = [template for template in cursor]
   return [parse_cursor.call(template) for template in output]
