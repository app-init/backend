from lib.imports.default import *

def call(*args, **kwargs):
   manager = Manager()
   db = manager.db("cache")

   if "manager" in kwargs:
      cursor = manager.get_direct_reports(kwargs['manager'])
   else:
      cursor = db.users.find({})

   users = []
   for i in cursor:
      if "displayName" not in i:
         continue

      user = {
         "uid": i['uid'],
         "irc": i['irc'],
         "list": i['sn'],
         "first": i['displayName'],
         "email": i['mail']
      }

      if "format_name" in kwargs:
         name = i['cn'].split(" ")
         user['fullName'] = "%s, %s" % (name[1], name[0])
         # user['fullName'] = "%s, %s" % (user['givenName'], user['sn'])

      users.append(user)

   return users
