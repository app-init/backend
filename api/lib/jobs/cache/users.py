from lib.imports.default import *
from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES, SUBTREE

import lib.users.token.renew as renew_token
import lib.users.picture as get_picture

def call(**kwargs):
   manager = Manager()
   db = manager.db("cache")

   server = Server("ldap.corp.redhat.com",use_ssl=True,get_info=ALL)
   connect = Connection(server, raise_exceptions=True, auto_bind=True)

   base_dn = "ou=users,dc=redhat,dc=com"

   search_filter = "(uid=*)"
   kwargs = {
      "search_base": base_dn,
      "search_filter": search_filter,
      "search_scope": SUBTREE,
      "paged_size": 5,
      "attributes": ALL_ATTRIBUTES,
   }

   output = []

   connect.search(**kwargs)
   output.append(parse_results(connect.entries))

   cookie = connect.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
   kwargs['paged_cookie'] = cookie

   while cookie:
      connect.search(**kwargs)
      output.append(parse_results(connect.entries))

      cookie = connect.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
      kwargs['paged_cookie'] = cookie

   return True

def parse_results(results):
   manager = Manager()
   db = manager.db("cache")

   output = []

   for i in results:
      data = simplejson.loads(i.entry_to_json())['attributes']

      if "givenName" not in data or "mail" not in data:
         continue

      user = {}
      for key, value in data.items():
         if len(value) == 1 and isinstance(value, list):
            user[key] = value[0]
         else:
            user[key] = value

      if "rhatNickName" in i:
         user["irc"] = user['rhatNickName']
      else:
         user['irc'] = None

      # data['fullName'] = "%s %s" % (data['first'], data['last'])

      user["cacheTime"] = datetime.datetime.utcnow()
      user['picture'] = get_picture.call(email=user['mail'])

      output.append(user)
      cached_user = db.users.find_one({"uid": user['uid']})
      if cached_user:
         if "token" not in cached_user:
            user['token'] = manager.sessions.token()

         db.users.update({"uid": user['uid']}, {"$set": user})
      else:
         user['token'] = manager.sessions.token()
         db.users.insert(user)

   return output
