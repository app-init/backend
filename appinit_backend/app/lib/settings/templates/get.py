from appinit_backend.lib.imports import *
import appinit_backend.app.lib.settings.templates.parse_cursor as parse_cursor

def call(**kwargs):
   manager = Manager()
   db = manager.db('appinit')

   output = None
   if "name" in kwargs:
      output = db.settings_templates.find_one(
         {
            'name': kwargs['name'],
         }
      )

   if "id" in kwargs:
      output = db.settings_templates.find_one(
         {
            '_id': ObjectId(kwargs['id']),
         }
      )

   return parse_cursor.call(output)
