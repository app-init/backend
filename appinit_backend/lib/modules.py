from bson.objectid import ObjectId
# from lib.permissions.apis import list as apiList
import os, inspect, imp, datetime, copy, sys
import importlib

class Modules(object):
   __modules = {}

   __instance = None

   base_path = None
   db = None
   manager = None
   settings = None

   def __new__(cls, *args, **kwargs):
      if Modules.__instance is None:
         Modules.__instance = object.__new__(cls)
         Modules.__instance.__set_class(*args, **kwargs)

      return Modules.__instance

   def __init__(self, settings, manager):
      self.setup(manager)

   def setup(self, manager):
      self.base_path = Modules.base_path
      self.db = Modules.db
      self.settings = Modules.settings
      self.manager = manager

   def __set_class(self, settings, manager):
      Modules.settings = settings
      Modules.base_path = os.path.abspath(os.path.join(os.path.realpath(__file__), "../../"))
      Modules.manager = manager
      Modules.db = Modules.manager.db("appinit")
      Modules.db.apis.remove({})
      self.__init_modules()

   def check_modules(self):
      db = self.manager.db("appinit")
      apis = db.apis.count()

      if apis == 0:
         return True
      else:
         reinit = db.apis.find_one({"name": "findNewModules"})
         if reinit != None:
            db.apis.remove({"name": "findNewModules"})
            return True

      return False

   # THIS SHOULDN'T BE NESSARY
   # method is only used in scheduler
   def _reinit(self):
      self.__modules = {}
      self.__init_modules(self.base_path)
      self.__modules = self.__set_permissions(self.__modules)

   # Jobs scheduler is the only place this method is used.
   def call(self, path=None, module=None, *args, **kwargs):
      if path != None:
         obj = self.get(path)
      elif module != None:
         obj = module
      else:
         raise Exception("A 'path' or 'module' wasn't passed in.")

      if "init" in kwargs:
         init = kwargs['init']
         del kwargs['init']

         if isinstance(init, list):
            obj = obj(*init)

         elif isinstance(init, dict):
            obj = obj(**init)

         else:
            raise Exception

         func = getattr(obj, kwargs['method'], None)
         del kwargs['method']

         if func == None:
            raise Exception

         return func(**kwargs)

      if "method" in kwargs:
         func = getattr(obj, kwargs['method'], None)
         del kwargs['method']

         if func == None:
            raise Exception

         return func(**kwargs)

      return obj.call(*args, **kwargs)

   def get(self, module, data=False, init=None, set_modules=False, imported={}):
      db = self.manager.db("appinit")

      obj = db.apis.find_one({"module": module})
      permissions = db.permissions.find_one({"module": module})

      if obj == None:
         # init in case a new module has been added
         # this is more useful for development
         # it will get called on production if the user requests an api that doesn't exist
         # requst should take longer but that's okay IMO
         self.__init_modules()
         obj = db.apis.find_one({"module": module})
         permissions = db.permissions.find_one({"module": module})

         if obj == None:
            return None
         else:
            pass
      else:
         obj['obj'] = imp.load_source(module, obj['path'])

      if module == "appinit.lib.db.Manager" and self.manager != None:
         return self.manager

      elif module == "appinit.lib.config.Settings":
         return self.settings

      if permissions == None:
         obj['permissions'] = []
      else:
         obj['permissions'] = permissions

      if data:
         return obj
      else:
         return obj['obj']

   def get_all_modules(self):
      db = self.manager.db("appinit")
      cursor = db.apis.find()

      output = {}
      for api in cursor:
         output[api['module']] = api

      return output

   def __ignore(self, name):
      ignore = [".pyc", ".json", ".txt", "__init__.py", ".md"]

      ignore_modules = ["compliance", "base", "websockets"]

      for i in ignore:
         if i in name:
            return True

      for i in ignore_modules:
         if name == i:
            return True

      if name.startswith('.') or name in inspect.getfile(inspect.currentframe()):
         return True

      return False

   def __find_modules(self, path, key=None, routes=False):
      files = os.listdir(path)
      if key == None:
         base_key = ""
      else:
         base_key = ".".join(key)

      for f in files:
         if self.__ignore(f):
            continue

         file_path = path + "/" + f

         if os.path.isfile(file_path):
            if len(base_key) > 1:
               m_name = base_key + "." + f.replace(".py", "")
            else:
               m_name = base_key + f.replace(".py", "")

            module = {
               "path": file_path,
               "route": self.__get_route(m_name),
               "internal": False,
               "type": "module",
               "child": [],
               "action": None,
               "module": m_name
            }

            self.__add_module(module)

         else:
            if len(base_key) > 1:
               f_name = base_key + "." + f
            else:
               f_name = base_key + f

            self.__find_modules(file_path, key=f_name.split("."))

   def __init_modules(self):
      routes = self.settings.get_variable("route-configs")
      
      for route in routes:
         path = route['api']['path']
         name = route['api']['name']

         if path not in sys.path:
            sys.path.append(path)
         
         spec = importlib.util.spec_from_file_location(name, path + '__init__.py')
         module_obj = importlib.util.module_from_spec(spec)
         spec.loader.exec_module(module_obj)

         sys.modules[name] = module_obj

         self.__find_modules(path)

      self.__find_modules(self.base_path)
      self.__setup_modules()

   def __setup_modules(self):
      cursor = self.db.apis.find()

      for m in cursor:
         if m['type'] != "module":
            continue

         m_name = m['module']
         path = m['path']
         module = m
         route = self.__get_route(m_name)
         del module['_id']

         spec = importlib.util.spec_from_file_location(m_name, path)
         module_obj = importlib.util.module_from_spec(spec)
         spec.loader.exec_module(module_obj)

         if getattr(module_obj, "action", None) != None:
            module['action'] = module_obj.action

         if getattr(module_obj, "internal", None) != None:
            if module_obj.internal:
               module['internal'] = True

         check_members = module_obj
         for name, obj in inspect.getmembers(check_members):
            if inspect.isbuiltin(obj) \
               or name == 'api' \
               or name[0] == "_" \
               or name in ["ISTERMINAL", "ISNONTERMINAL", "ISEOF", "convert", "make_response", "jsonify"]:
               continue

            elif inspect.isroutine(obj):
               c_name = m_name + "." + name

               parent_module_routine = {
                  "type": "method",
                  "route": route,
                  "parent": m_name,
                  "internal": module['internal'],
                  "action": module['action'],
                  "module": c_name,
                  "name": name,
                  "path": path,
               }

               self.__add_module(parent_module_routine)

               module['child'].append({"name": c_name, "type": "method"})

            elif inspect.ismodule(obj):
               member_path = False
               try:

                  member_path = obj.__file__.replace(self.base_path, "")[1:]
                  member_path = member_path.replace("/", ".")

                  if "python" in member_path:
                     member_path = False
                  else:
                     member_path = member_path.replace(".py", "")

               except Exception as e:
                  pass

               if not member_path:
                  continue

               module['child'].append({"name": member_path, "type": "module"})

         module['child'] = list({v['name']:v for v in module['child']}.values())

         self.__add_module(module)

   def __add_module(self, module):
      self.db.apis.update({"module": module['module']}, {"$set": module}, upsert=True)

   def __get_route(self, module=None):
      return self.manager.get_route(module=module)

   def __get_permissions(self, module):
      db = self.manager.db("appinit")

      cursor = db.permissions.find({"module": module})

      if cursor.count() == 0:
         return []
      else:
         try:
            return cursor[0]['permissions']
         except:
            print(cursor)
            sys.exit()

   def check_permissions(self, module, permissions):
      route = module['route']

      # print(path, app, module['permissions'], permissions)
      # when api requested has no permissions
      if len(module['permissions']) == 0:
         return True

      # user has no application permissions but requested api HAS permissions set
      if not(route in permissions) and len(module['permissions']) > 0:
         return False

      # user as admin permissions on requested api
      if "admin" in permissions[route]:
         return True

      # check if user has requested api permissions
      for i in set(permissions[route]):
         for j in module['permissions']:
            if i == j:
               return True

      return False
