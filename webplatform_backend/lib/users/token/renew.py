from lib.imports.default import *
from flask import g

def call(**kwargs):
   manager = Manager()
   db = manager.db("cache")

   uid = kwargs['uid']

   if g.session != None and g.session.uid == uid and manager.sessions.validate(g.session.token, uid):
      new_token = manager.sessions.token()

      db.users.update({"uid": uid}, {"$set": { "token": new_token }})

      return new_token
   else:
      return HttpResponseForbidden()
