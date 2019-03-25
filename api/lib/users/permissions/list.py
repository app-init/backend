from lib.imports.default import *
action = "get"

def call(*args, **kwargs):
   manager = Manager()
   db = manager.db('cee-tools')

   if "edit" in kwargs:
      output = {
         "permissions": _get_all_permissions(),
         "raw": {}
      }

      #add an application name here
      cursor = db.permissions.find()
      for i in cursor:
         permissions = {
            "permissions": {},
         }

         for j in sorted(output['permissions']):
            if j in i['permissions']:
               permissions['permissions'][j] = True
            else:
               permissions['permissions'][j] = False

         output['raw'][i['uid']] = permissions

      return output

   elif "uid" in kwargs:
      permissions = {}

      apps = manager.sessions.list_applications()
      apps.append({"name": "system"})
      for app in apps:

         if app['name'] != "system":
            list_name = app['module_base'].split("_")
            camel_case = ''.join([list_name[x].title() for x in range(1, len(list_name))])
            name = list_name[0] + camel_case
         else:
            name = app['name']

         permissions[name] = {}

         all_permissions = db.permissions.find({"application": app['name']}).distinct("permissions")

         user_permissions = db.permissions.find_one({"uid": kwargs['uid'], "application": app['name']})

         if user_permissions != None:
            all_true = False
            if user_permissions['application'] == app['name']:
               all_true = "admin" in user_permissions['permissions']

            for p in user_permissions['permissions']:
               key = 'is_' + p
               if all_true:
                  permissions[name][key] = True
               elif p in all_permissions:
                  permissions[name][key] = True
               else:
                  permissions[name][key] = False

      return permissions
   else:
      #TODO need to work on this some more not really sure what to do here
      return {"permissions": __get_all_permissions()}

def __get_all_permissions():
   manager = Manager()
   db = manager.db("cee-tools")

   #
   # pipeline = [
   #    #add a match for an application here
   #    { "$unwind": "$permissions" },
   #    { "$group":
   #       {
   #          "_id": "all",
   #          "permissions": {"$addToSet": "$permissions"},
   #       }
   #    },
   # ]
   #
   # cursor = db.permissions.aggregate(pipeline)
   # if cursor != None:
   #    for i in cursor:
   #       return sorted(i['permissions'])
   # else:
   #    return []