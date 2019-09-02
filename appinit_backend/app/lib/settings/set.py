from appinit_backend.lib.imports import *
import appinit_backend.app.lib.settings.templates.get as get_template

def call(**kwargs):
   manager = Manager()
   session = Session()
   db = manager.db("appinit")
   uid = session.get_uid()

   name = kwargs['name']
   template = get_template.call(name=name)
   temp_id = ObjectId(template['id'])

   app = template['application']
   value = kwargs['value']

   update = {
      "value": value,
   }

   if "permissions" in template:
      update['permissions'] = template['permissions']

   query = {
      "uid": uid,
      "application": app,
      "name": name,
      "t_id": temp_id
   }

   cursor = db.settings.find_one(query)
   if cursor == None:
      query['value'] = value

      if "permissions" in template:
         query['permissions'] = template['permissions']

      db.settings.insert(query)
   else:

      db.settings.update(query, {"$set": update})
