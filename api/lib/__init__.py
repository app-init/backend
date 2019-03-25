# from .utils.config import Settings
# import os, sys, imp
#
#
# controller_path = os.path.dirname(os.path.realpath(__file__))
# base_path = os.path.abspath(os.path.join(controller_path, '../../'))
#
# instance = os.environ.get("CEE_TOOLS_INSTANCE", "devel")
# settings = Settings(base_path, verify=False, instance=instance)
#
# apps_path = settings.get_config("nginx")['apps']
# print(apps_path)
# if apps_path not in sys.path:
#    sys.path.append(apps_path)
#
# import bzcompliance
# import support_exceptions.api as se
#
# __all__ = [
#    'se',
#    'bzcompliance'
# ]
#
# files = os.listdir(apps_path)
# for f in files:
#    path = apps_path + "/" + f
#
#    if not os.path.islink(path) and not os.path.isfile(path):
#       if f == 'support-exceptions' or f == 'release-planning':
#          continue
      #    module_name = 'se'
      # elif f == 'release-planning':
      #    module_name = 'rp'
      # else:
      #    module_name = f
      #
      # print(module_name)
      # if os.path.exists(path + "/api/__init__.py"):
      #    module = imp.find_module(module_name)
      #    imp.load_module(module)
