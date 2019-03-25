from lib.imports.default import *

def call(**kwargs):
   modules = {}

   manager = Manager()
   db = manager.db("cee-tools")

   cursor = db.apis.find()
   for i in cursor:
      if ".call" not in i['module'] and i['type'] == "module":
         modules[i['module']] = i

   exclude = ["call"]
   output = {
      "modules": {}
   }

   if "exclude" in kwargs:
      for i in kwargs['exclude']:
         for key, value in modules.items():
            if i not in key and value['type'] == "module":
               output['modules'][key] = value

   elif "check_permissions" in kwargs:
      all_modules = {}
      permissions = kwargs['check_permissions']
      for module, value in modules.items():
         if value['type'] == 'module':
            if len(value['permissions']) > 0:
               for i in permissions:
                  if i in value['permissions']:
                     all_modules[module] = value

            elif not value['internal']:
               remove_child = []
               for child, child_value in value['child'].items():
                  if child_value['internal']:
                     remove_child.append(child)

               for i in remove_child:
                  del value['child'][i]

               all_modules[module] = value

            elif not value['internal'] and len(value['permissions']) == 0:
               if module == "release_planning.products.add":
                  print(value)
               all_modules[module] = value

      output['modules'] = all_modules
   else:
      output['modules'] = modules

   return output