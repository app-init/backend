from appinit_backend.lib.imports import *

def call(**kwargs):
   manager = Manager()
   db = manager.db("appinit")
   
   session = Session()
   settings = Settings()
   permission_mgr = PermissionManager(session.get())

   modules = Modules(settings, manager)
   uid = session.get_uid()

   cursor = db.settings_templates.find()

   output = {}
   route_titles = {}
   for t in cursor:
      section = t['section']
      route = t['route']

      if "permissions" in t:
         permissions = permission_mgr.get_route(route=route)
         check = [p for p in permissions if p in t['permissions'] or p == "admin"]

         if len(check) == 0:
            continue

      # TODO handle if template is global
      if section not in output:
         output[section] = {}

      if route not in output[section]:
         route_titles[route] = manager.get_route(route=route)
         output[section][route] = []

      setting = {
         "route": route,
         "type": t['inputType'],
         "name": t['name'],
         "id": t['_id'],
         "title": t['title'],
         "description": t['description'],
         "inputProps": None,
      }

      if "isMulti" in t:
         setting['isMulti'] = t['isMulti']

      if "inputProps" in t:
         setting['inputProps'] = t['inputProps']

      if t['isDynamic']:
         if "api" in t:
            setting['values'] = modules.call(t['api'])
         else:
            setting['values'] = __dynamic(t)
      else:
         if setting['type'] in ["radio", "checkBox", "select"]:
            setting['values'] = t['values']

      output[section][route].append(setting)

   return {"settings": output, "routeTitles": route_titles}

def __dynamic(template):
   manager = Manager()
   db = manager.db(template['db'])

   pipeline = [
      {
         "$project": {
            "_id": 1,
            template['key']: 1,
         }
      },
      {
         "$group": {
            "_id": "_id",
            "values": {
               "$addToSet": "$" + template['key']
            }
         }
      }
   ]

   cursor = db[template['collection']].aggregate(pipeline)
   for i in cursor:
      return i['values']
