from appinit_backend.lib.imports import *

def call(**kwargs):
   session = Session()
   modules = Modules()
   settings = Settings()

   user = session.get_user()
   user_module = settings.get_variable('user-module')

   if user_module:
      get_user = modules.get(user_module)

      if get_user:
         user['metadata'] = get_user.call(uid=user['uid'])

   return user