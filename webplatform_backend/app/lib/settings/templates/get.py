from lib.imports.default import *
import lib.settings.templates.parse_cursor as parse_cursor

def call(**kwargs):
   manager = Manager()
   db = manager.db('webplatform')

   output = None
   if "name" in kwargs:
      output = db.templates.find_one(
         {
            'name': kwargs['name'],
         }
      )

   if "id" in kwargs:
      output = db.templates.find_one(
         {
            '_id': ObjectId(kwargs['id']),
         }
      )

   return parse_cursor.call(output)
