from lib.imports.default import *

def call(**kwargs):
   manager = Manager()
   settings = Settings()
   modules = Modules(settings=settings)
   db = manager.db("webplatform")
   uid = manager.get_user_uid()

   cursor = db.templates.find()

   output = {}
   app_titles = {}
   for t in cursor:
      section = t['section']
      app = t['application']

      if "permissions" in t:
         permissions = manager.get_permissions(app=app)
         check = [p for p in permissions if p in t['permissions'] or p == "admin"]

         if len(check) == 0:
            continue

      # TODO handle if template is global
      if section not in output:
         output[section] = {}

      if app not in output[section]:
         app_titles[app] = manager.get_application(app=app)
         output[section][app] = []

      setting = {
         "application": app,
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

      output[section][app].append(setting)

   return {"settings": output, "appTitles": app_titles}

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
