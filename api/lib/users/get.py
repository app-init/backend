from lib.imports.default import *
import lib.notifications.get as get_notifications
import lib.users.permissions.list as get_permissions
import lib.users.picture as get_picture
import lib.users.token.renew as renew_token
import lib.settings.get as get_settings

def call(*args, exclude=[], **kwargs):
   manager = Manager()

   output = {}

   user = None
   if 'kerberos' in kwargs:
      user = kerberos(manager, kwargs['kerberos'])

   if user != None:
      output['kerberos'] = user

      title = user['rhatJobTitle'].lower()
      output['isManager'] = "manager" in title or "supervisor" in title

      if "ldap" in user:
         output['ldap'] = user['ldap']

      output['uid'] = user['uid']

      if "bugzilla" in user and "token" in user['bugzilla']:
         output['bugzilla'] = user['bugzilla']

      output['sessions'] = manager.get_all_sessions(kwargs['kerberos'])
      # output['notifications'] = get_notifications.call(uid=user)
      output['permissions'] = get_permissions.call(uid=kwargs['kerberos'])
      output['settings'] = get_settings.call(uid=kwargs['kerberos'], output="uid")
      output['token'] = user['token']

      email = output['uid'] + "@redhat.com"
      if 'picture' in user:
         output['picture'] = user['picture']
      else:
         output['picture'] = get_picture.call(email=email)

      return output

   return output

def kerberos(manager, uid):
   db = manager.db("cache")
   cursor = db.users.find_one({"uid": uid})
   if cursor != None:
      cursor['id'] = cursor['_id']
      del cursor['_id']
      if "token" not in cursor:
         cursor['token'] = renew_token.call(uid=uid)
   else:
      user = manager.ldap_lookup(uid)

      user["cacheTime"] = datetime.datetime.utcnow()
      user["token"] = renew_token.call(uid=uid)
      user['picture'] = get_picture.call(email=user['mail'])

      db.users.insert(new_user)

      return new_user

   return cursor
