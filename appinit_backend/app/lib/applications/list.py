from appinit_backend.lib.imports import *

def call(**kwargs):
   manager = Manager()
   return manager.get_route()