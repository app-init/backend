from appinit_backend.lib.imports import *
import appinit_backend.app.lib.settings.set as set_setting

def call(**kwargs):
   settings = kwargs['settings']

   for setting in settings:
      set_setting.call(name=setting['name'], value=setting['value'])
