def imports():
   from lib.utils.config import Settings
   import os

   settings = Settings(path="/home/cee-tools/", verify=False, instance=os.environ['CEE_TOOLS_INSTANCE'])

   from lib.utils.modules_2 import Modules
   modules = Modules(settings)

   return settings, modules
