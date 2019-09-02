from appinit_backend.lib.imports import *
import appinit_backend.app.lib.settings.templates.get as get_template
from appinit_backend.app.lib.settings.templates.parse_cursor import get_name

def call(**kwargs):
   manager = Manager()
   db = manager.db('appinit')

   template = {
      '_id': ObjectId(),
      'title': kwargs['title'],
      'description': kwargs['description'],
      'inputType': kwargs['inputType'],
      'application': kwargs['application'],
      'section': kwargs['section'],
      'isDynamic': kwargs['isDynamic'],
      'isGlobal': kwargs['isGlobal'],
      'name': get_name(kwargs['title'])
   }

   if kwargs['isDynamic']:
      if "api" in kwargs:
         template['api'] = kwargs['api']
      else:
         template['db'] = kwargs['db']
         template['collection'] = kwargs['collection']
         template['key'] = kwargs['key']

   if 'values' in kwargs:
      template['values'] = kwargs['values']

   if 'inputProps' in kwargs:
      template['inputProps'] = kwargs['inputProps']

   if 'permissions' in kwargs:
      template['permissions'] = kwargs['permissions']

   if 'isMulti' in kwargs:
      template['isMulti'] = kwargs['isMulti']

   db.settings_templates.insert(template)

   return get_template.call(name=template['name'])
