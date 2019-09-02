from flask import g
from appinit_backend.lib.imports import *
import re

def call(**kwargs):
   manager = Manager()
   session = Session()
   db = manager.db("appinit")

   q = {}

   if "uid" in kwargs:
      if kwargs['uid']:
         q['uid'] = kwargs['uid']
   else:
      if "permissions" not in kwargs:
         q['uid'] = session.get_uid()

   if "name" in kwargs:
      q['name'] = kwargs['name']

   if "application" in kwargs:
      q['application'] = kwargs['application']

   if "permissions" in kwargs:
      q['permissions'] = kwargs['permissions']

   output = {}
   cursor = db.settings.find(q)
   for i in cursor:
      if i is None:
         continue

      setting = manager.parse_cursor_object(i)

      app = setting['application']
      name = setting['name']
      uid = setting['uid']
      value = setting['value']

      if app not in output:
         output[app] = {}

      if name not in output[app]:
         output[app][name] = {
            "uids": {
               "ids": [uid],
               "data": {
               }
            },
            "values": {
               "ids": [],
               "data": {
               }
            },
         }
         if type(value) is dict:
            for k, v in value.items():
               output[app][name]['values']['data'][k] = [uid]

            output[app][name]['values']['ids'] = list(value.keys())
            output[app][name]['uids']['data'][uid] = list(value.keys())

         elif type(value) is list:
            for v in value:
               output[app][name]['values']['data'][v] = [uid]

            output[app][name]['values']['ids'] = value
            output[app][name]['uids']['data'][uid] = value

         elif type(value) is bool:
            output[app][name]['values']['data'][str(value)] = [uid]
            output[app][name]['values']['ids'].append(value)
            output[app][name]['uids']['data'][uid] = value
         else:
            output[app][name]['values']['data'][value] = [uid]
            output[app][name]['values']['ids'].append(value)
            output[app][name]['uids']['data'][uid] = value


      app_setting = output[app][name]

      if uid not in app_setting['uids']['ids']:
         app_setting['uids']['ids'].append(uid)

      if type(value) is dict:
         if uid not in app_setting['uids']:
            output[app][name]['uids']['data'][uid] = list(value.keys())

         for k, v in value.items():
            if k not in app_setting['values']['ids']:
               app_setting['values']['ids'].append(k)

            if k not in app_setting['values']['data']:
               app_setting['values']['data'][k] = [uid]
            else:
               if uid not in app_setting['values']['data'][k]:
                  app_setting['values']['data'][k].append(uid)

      elif type(value) is list:
         if uid not in app_setting['uids']:
            output[app][name]['uids']['data'][uid] = value

         for v in value:
            if v not in app_setting['values']['ids']:
               app_setting['values']['ids'].append(v)

            if v not in app_setting['values']['data']:
               app_setting['values']['data'][v] = [uid]
            else:
               if uid not in app_setting['values']['data'][v]:
                  app_setting['values']['data'][v].append(uid)

      elif type(value) is bool:
         value = str(value)
         if uid not in app_setting['uids']:
            app_setting['uids']['data'][uid] = value

         if value not in app_setting['values']['ids']:
            app_setting['values']['ids'].append(value)

         if value not in app_setting['values']['data']:
            app_setting['values']['data'][value] = [uid]
         else:
            if uid not in app_setting['values']['data'][value]:
               app_setting['values']['data'][value].append(uid)

      else:
         if uid not in app_setting['uids']:
            app_setting['uids']['data'][uid] = value

         if value not in app_setting['values']['ids']:
            app_setting['values']['ids'].append(value)

         if value not in app_setting['values']['data']:
            app_setting['values']['data'][value] = [uid]
         else:
            if uid not in app_setting['values']['data'][value]:
               app_setting['values']['data'][value].append(uid)

      output[app][name] = app_setting

   if "output" in kwargs:
      output_key = kwargs['output']

      if output_key == "application" and "application" in kwargs:
         return output[kwargs['application']]

      elif output_key == "name" and "application" in kwargs:
         return output[kwargs['application']][kwargs['name']]

      # elif output_key == "value" and "application" in kwargs and "name" in kwargs and "value" in kwargs:
      elif output_key == "value" and "application" in kwargs and "name" in kwargs:
         uids = []

         if len(output) == 0:
            return {"uids": uids}

         values = output[kwargs['application']][kwargs['name']]['values']['data']

         if "value" not in kwargs:
            return {"values": list(values.keys())}

         for k, v in values.items():
            for uid in v:
               if str(k).lower() in str(kwargs['value']).lower():
                  if uid not in uids:
                     uids.append(uid)

         return {"uids": uids}

      elif output_key == "uid":
         new_output = {}
         for app, settings in output.items():
            if app not in new_output:
               new_output[app] = {}

            for name, setting in settings.items():
               if name not in new_output[app]:
                  new_output[app][name] = list(output[app][name]['values']['data'].keys())

         if "application" in kwargs and "name" in kwargs and "value" in kwargs:
            try:
               return output[kwargs['application']][kwargs['name']]['values']['data'][str(kwargs['value'])]
            except KeyError:
               return []

         elif "application" in kwargs and "name" in kwargs and "value" not in kwargs and "uid" not in kwargs:
            return output[kwargs['application']][kwargs['name']]['uids']

         elif "application" in kwargs and "name" in kwargs and "value" not in kwargs and "uid" in kwargs:
            if kwargs['application'] not in output:
               return {}

            return {"value": output[kwargs['application']][kwargs['name']]['uids']['data'][uid]}

         else:
            return new_output

   return output
