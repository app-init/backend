from appinit_backend.lib.imports import *
from appinit_backend.lib.notifications import email
from appinit_backend.app.lib.files import meta


def call(action, fid, **kwargs):
   manager = Manager()
   title = None
   body = None
   users = set()

   if fid is None:
      raise Exception
   meta = meta.call(id=fid)
   users.add(meta["uid"])
   if action == "remove":
      title = "Removed unassigned file '%s'" % meta["filename"]
      body = """The file '%s' has not been assigned to an object \
                in %s days and therefore it has been been removed. We're sorry for any \
                inconvience.""" % (meta["filename"], kwargs["days"])
   elif action == "warning":
      title = "File removal warning"
      body = """Warning: the file '<a href="%s/files/%s/">%s</a>' has still not been assigned to an object \
                  in %s days. If this file is not assigned in %s days it will be removed. Please finish the
                  form where you uploaded this file if you wish to keep it \
                  uploaded.""" % (manager.get_hostname(), fid, meta["filename"], kwargs["days"], kwargs["days_till_remove"])

   email.call("Files", title, users, body)