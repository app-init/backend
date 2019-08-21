from lib.imports.default import *

def call(**kwargs):
   session = Session()
   return session.get_user()