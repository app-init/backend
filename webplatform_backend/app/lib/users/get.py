from lib.imports.default import *
from webplatform_auth.lib.session import SessionManager

def call(**kwargs):
   session_mgr = SessionManager()
   return session_mgr.get_user()