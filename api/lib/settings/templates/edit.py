from lib.imports.default import *
import lib.settings.templates.get as get_template
from lib.settings.templates.parse_cursor import get_name

def call(**kwargs):
   manager = Manager()
   db = manager.db('settings')

   name = kwargs['name']
   id = kwargs['id']

   del kwargs['name']
   del kwargs['id']

   template = get_template.call(name=name)

   for key, value in kwargs.items():
      updates = {
         "$set": {
            key: value,
         }
      }

      if key == 'title':
         new_name = get_name(kwargs['title'])
         name = new_name
         updates['$set']['name'] = new_name

      db.templates.update(
         {
            "_id": ObjectId(id),
         },
         updates
      )

   return get_template.call(name=name)
