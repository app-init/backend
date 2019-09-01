from lib.imports.default import *

def call(**kwargs):
   manager = Manager()
   return manager.get_route()