from lib.imports.default import *
from operator import itemgetter

def call(**kwargs):
   manager = Manager()
   db = manager.db("cee-tools")

   cursor = db.apis.find({})
   output = []
   modules = []

   for i in cursor:
      if i['type'] == "module":
         i['safe_name'] = i['module'].replace('.', '-')
         modules.append(i['module'])
         output.append(manager.parse_cursor_object(i))

   cursor = db.permissions.find({"module": {"$in": modules}})
   for i in cursor:
      for idx, j in enumerate(output):
         if i['module'] == j['module']:
            print(j['module'])
            j['permissions'] = i['permissions']
            output[idx] = j

   return sorted(output, key=itemgetter('application'))
