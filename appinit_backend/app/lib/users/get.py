from appinit_backend.lib.imports import *

def call(**kwargs):
   session = Session()
   return session.get_user()