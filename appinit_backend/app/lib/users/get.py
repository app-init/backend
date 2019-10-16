from appinit_backend.lib.imports import *
from appinit_backend.app.lib.settings import get as get_settings
from datetime import datetime

def call(**kwargs):
   session = Session()
   modules = Modules()
   settings = Settings()

   manager = Manager()
   db = manager.db('appinit')

   user = session.get_user()

   if not user['metadata'] or user['update']:
      user_module = settings.get_variable('user-module')

      if user_module:
         get_user = modules.get(user_module)

         if get_user:
            user['metadata'] = get_user.call(uid=user['uid'])
            
            now = datetime.utcnow()
            user['metadata']['lastUpdated'] = now
            user['metadata']['uid'] = session.get_uid()

            db.users.update({"uid": session.get_uid()}, user['metadata'], upsert=True)

   del user['update']
      
   settings = get_settings.call(uid=session.get_uid(), output="uid")
   user['settings'] = settings

   return user