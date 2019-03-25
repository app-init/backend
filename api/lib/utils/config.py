try:
   import simplejson
except:
   import json as simplejson

import os, sys, getpass, re

class BaseConfigError(Exception):
   def __init__(self, key, value, config):
      self.key = key
      self.value = value
      self.config = config

class InvalidConfig(BaseConfigError):
   def __str__(self):
      return str('Invalid config syntax in "%s" on "%s" with "%s" value.' % (self.config, self.key, self.value))

class FileDoesNotExist(BaseConfigError):
   def __str__(self):
      return str('File does not exist "%s". Check config in "%s" on "%s".' % (self.value, self.config, self.key))

class Settings(object):
   __base_path = None
   __object = None
   __instance = None
   __services = None
   __config = None
   __config_paths = None

   def __new__(cls, *args, **kwargs):
      if Settings.__object is None:
         Settings.__object = object.__new__(cls)
         Settings.__object.__set_class(*args, **kwargs)

      return Settings.__object

   def __init__(self, path=None, verify=None, instance="devel"):
      self.setup()

   def __set_class(self, path, verify, instance):
      if path is None:
         path = Settings.__base_path
      else:
         Settings.__base_path = path

      if verify == None:
         self.verify = True
      else:
         self.verify = False

      Settings.__base_path = path
      Settings.__instance = instance

      Settings.__config_paths = self.__find_configs(instance)
      Settings.__services = self.__services

      Settings.__config = {}
      self.__load()
      self.setup()

   def setup(self):
      self.__config_paths = Settings.__config_paths
      self.__config = Settings.__config
      self.__services = Settings.__services
      self.__instance = Settings.__instance
      self.__bath_path = Settings.__base_path

   def get_actions(self, service):
      actions = {
         "start": {
            "default": True,
         },
         "restart": {
            "default": True,
         },
         "stop": {
            "default": True,
         },
         "update": {
            "default": True
         }
      }

      path = "%s/setup/instances/common/%s/actions" % (self.__base_path, service)

      try:
         for i in os.listdir(path):
            regex = re.compile("(.+)?\.+")
            match = regex.search(i)

            if match != None and len(match.groups()) > 0:
               a = match.groups()[0]
               actions[a] = {
                  'default': False,
                  'cmd': "sh /home/container/actions/%s" % i
               }
         return actions

      except OSError:
         return actions


   def get_service(self, service=None):
      if service != None:
         found = False
         for i in self.__services:
            if service == i:
               found = True

         if not found:
            if service in self.__config.keys():
               return [i for i in self.__config[service].keys() if i != "multiple"]
         else:
            return service
      return self.__services

   def __find_configs(self, instance):
      path = "%s/setup/instances/%s" % (self.__base_path, self.__instance)

      # try:
      services = [i for i in os.listdir(path) if "settings" not in i and "common" not in i]
      # except OSError:
      #    print("Instance doesn't exist")
      #    sys.exit()

      configs = {}
      for i in services:
         service = i.split("_")

         if len(service) > 1:
            if service[0] not in configs.keys():
               configs[service[0]] = {
                  service[1]: "%s/settings/%s.json" % (path, i),
                  'multiple': True,
               }
            else:
               configs[service[0]][service[1]] = "%s/settings/%s.json" % (path, i)

         else:
            configs[service[0]] = "%s/settings/%s.json" % (path, i)

      self.__services = services

      return configs

   def __load(self):
      for i in list(self.__config_paths.keys()):
         path = self.__config_paths[i]
         if isinstance(path, dict):
            self.__config[i] = {}
            for j in list(path.keys()):
               if j != "multiple":
                  self.__config[i][j] = self.__load_config(path[j])
               else:
                  self.__config[i][j] = True

         if isinstance(path, str):
            self.__config[i] = self.__load_config(path)

      path = "%s/setup/instances/%s/settings/" % (self.__base_path, self.__instance)
      for i in os.listdir(path):
         if "_" not in i and i[0] != ".":
            config = i.split(".json")[0]
            if config not in self.__config.keys():
               self.__config[config] = self.__load_config(path + i)

   def __load_config(self, path):
      try:
         with open(path) as target:
            try:
               return simplejson.load(target)

            except:
               return {"error": "JSON parsing error"}

      except IOError:
         return {"error": "Failed to load file"}

   def get_num_cores(self, config_type=None, get_range=False):
      configs = self.get_config()

      cores = {}
      for service, config_value in configs.items():
         if "num_cores" in config_value.keys():
            cores[service] = config_value['num_cores']
         else:
            cores[service] = 0

      num_cores = self.__set_num_cores(cores)

      if config_type == None:
         output = {}
         for key, value in num_cores.items():
            if get_range:
               output[key] = value['str']
            else:
               output[key] = value['int']

         return output

      else:
         if get_range:
            output = num_cores[config_type]['str']
            if output == "0-0":
               return None
            else:
               return output
         else:
            return num_cores[config_type]['int']

   def __set_num_cores(self, cores):
      output = {}

      start = 0
      for service, value in cores.items():
         output[service] = {
            "int": value,
         }

         if value != 0:
            if value == 1:
               output[service]["str"] = "%d" % (start)
            else:
               output[service]["str"] = "%d-%d" % (start, value + start - 1)
            start += value
         else:
            output[service]["str"] = "0-0"

      return output

   def get_config(self, config_type=None):
      output = {}

      if config_type is not None and config_type in list(self.__config.keys()):
         if "multiple" in self.__config[config_type]:

            for config_key, config in self.__config[config_type].items():
               if config_key != "multiple":

                  output[config_key] = {}
                  for key, value in list(config.items()):
                     output[config_key][key] = value

                     # if (isinstance(value, str) and value[0] == "/") or (isinstance(value, dict) and config_type != "mongodb"):
                     if (isinstance(value, str) and value[0] == "/") or (isinstance(value, dict)):
                        output_key, output_value = self.__process_config(key, value, config_type)
                        output[config_key][output_key] = output_value

                     # if config_type == "mongodb":
                     #    config = self.__process_mongodb_config(value)
                     #    output[config_key][key] = config
         else:
            for key, value in list(self.__config[config_type].items()):
               output[key] = value

               # if (isinstance(value, str) and value[0] == "/") or (isinstance(value, dict) and config_type != "mongodb"):
               if (isinstance(value, str) and value[0] == "/") or (isinstance(value, dict)):
                  output_key, output_value = self.__process_config(key, value, config_type)
                  output[output_key] = output_value

               # if config_type == "mongodb":
               #    config = self.__process_mongodb_config(value)
               #    output[key] = config

         return output

      else:
         for config_type in list(self.__config.keys()):
            tmp = {}

            if "multiple" in self.__config[config_type]:
               for config_key, config in self.__config[config_type].items():
                  if config_key != "multiple":
                     tmp[config_key] = {}
                     for key, value in list(config.items()):
                        tmp[config_key][key] = value
#
                        # if (isinstance(value, str) and value[0] == "/") or (isinstance(value, dict) and config_type != "mongodb"):
                        if (isinstance(value, str) and value[0] == "/") or (isinstance(value, dict)):
                           output_key, output_value = self.__process_config(key, value, config_type)
                           tmp[config_key][output_key] = output_value

                        # if config_type == "mongodb":
                        #    config = self.__process_mongodb_config(value)
                        #    tmp[config_key][key] = config

            else:
               for key, value in list(self.__config[config_type].items()):
                  tmp[key] = value

                  # if (isinstance(value, str) and value[0] == "/") or (isinstance(value, dict) and config_type != "mongodb"):
                  if (isinstance(value, str) and value[0] == "/") or (isinstance(value, dict)):
                     output_key, output_value = self.__process_config(key, value, config_type)
                     tmp[output_key] = output_value

                  # if config_type == "mongodb":
                  #    config = self.__process_mongodb_config(value)
                  #    tmp[key] = config

            output[config_type] = tmp

            # else:
            #    for key, value in list(self.__config[config_type].items()):
            #       tmp[key] = value
            #
            #       if (isinstance(value, str) and value[0] == "/") or (isinstance(value, dict) and config_type != "mongodb"):
            #          output_key, output_value = self.__process_config(key, value, config_type)
            #          tmp[output_key] = output_value
            #
            #       if config_type == "mongodb":
            #          config = self.__process_mongodb_config(value)
            #          tmp[key] = config
            #
            #       output[config_type] = tmp
            #
         return output

      return self.__config

   def __process_mongodb_config(self, config):
      output = {}
      if type(config) is dict:
         for section_key, section_value in list(config.items()):
            output[section_key] = section_value

            if isinstance(section_value, str) and section_value[0:1] != "/" and "/" in section_value:
               output[section_key] = os.path.join(self.__base_path, section_value)

            if isinstance(section_value, dict):
               tmp = {}
               for value_key, value in list(section_value.items()):
                  tmp[value_key] = value

                  if isinstance(value, str) and value[0:1] != "/" and "/" in value:
                     tmp[value_key] = os.path.join(self.__base_path, value)

               output[section_key] = tmp
      else:
         return config

      return output

   def __process_config(self, key, value, config_type):
      if isinstance(value, str):
         value = {
            "abs": True,
            "path": value
         }

      if "environ" in value:
         key = value['environ'].upper()

      if isinstance(value, list):
         parsed_path = []

         for i in value:
            path = os.path.abspath(os.path.join(self.__base_path, i))
            parsed_path.append(path)

            if self.verify:
               if value.get("verify") in (None, True) and not os.path.exists(path) and "pid" not in path and ("log" not in path and "debug" not in path):
                  try:
                     raise FileDoesNotExist(key, path, config_type)

                  except FileDoesNotExist as e:
                     print(e.value)
                     sys.exit()

         output_value = " ".join(parsed_path)

      elif "rel" in value or "abs" in value:
         output_value = value['path']

         path = None

         if "rel" in value:
            if len(output_value) > 1:
               path = os.path.abspath(os.path.join(self.__base_path, output_value))

            else:
               path = os.path.abspath(self.__base_path)

         else:
            path = os.path.abspath(output_value)

            if self.verify:
               if value.get("verify") in (None, True) and not os.path.exists(path) and "pid" not in path:
                  try:
                     raise FileDoesNotExist(key, path, config_type)

                  except FileDoesNotExist as e:
                     print(e)
                     sys.exit()

         output_value = path

         value = output_value

      return key, value

   def get_environ_set(self, **kwargs):
      environ = {}

      if 'environ' in kwargs and isinstance(kwargs['environ'], dict):
         environ = kwargs['environ']

      for config_type in list(self.__config_paths.keys()):
         for key, value in list(self.__config[config_type].items()):
            base_key = "CEE_TOOLS_" + config_type.upper() + "_" + key.replace("-", "_").upper()

            if (isinstance(value, str) and value[0] == "/") or (isinstance(value, dict) and config_type != "mongodb"):
               environ_key, environ_value = self.__process_config(base_key, value, self.__config_paths[config_type])
               environ[environ_key] = environ_value

            else:
               if isinstance(value, list):
                  environ[base_key] = str(" ".join(value))

               elif config_type == "nodejs" and key == "port":
                  environ[base_key] = str(value)

               else:
                  environ_key = "CEE_TOOLS_" + config_type.upper() + "_"  + key.replace("-", "_").upper()
                  environ[base_key] = str(value)

      return environ

   def get_instance(self):
      return self.__instance

   def get_path(self):
      return self.__base_path
