from lib.imports.default import *
import lib.permissions.users.list as users_list
import lib.permissions.apis.list as apis_list
import lib.permissions.users.get as get_user

def call(**kwargs):
   manager = Manager()

   uid = manager.get_user_uid()
   user = get_user.call(uid=uid)

   if user is None or len(user['applications']) == 0:
      return HttpResponseForbidden()

   output = {
      'apis': apis_list.call(**kwargs),
      'users': users_list.call(**kwargs),
   }

   return output
