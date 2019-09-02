from appinit_backend.lib.imports import *
from appinit_backend.app.lib.files import notify as files_notify

def call(**kwargs):
   from io import StringIO
   from gridfs import GridFS
   from datetime import datetime
   from dateutil.relativedelta import relativedelta

   if "remove_days" not in kwargs:
      kwargs["remove_days"] = 7
   if "warning_days" not in kwargs:
      kwargs["warning_days"] = 3

   manager = Manager()
   db = manager.db("files")
   fs = GridFS(db)
   output = StringIO()

   today = datetime.now()
   days_till_remove = int(kwargs["remove_days"]) - int(kwargs["warning_days"])
   warning = today + relativedelta(days=-int(kwargs["warning_days"]))
   remove = today + relativedelta(days=-int(kwargs["remove_days"]))

   cursor = db.fs.files.find({ "assigned": False, "uploadDate": { "$lte": remove } })
   print("Removing", cursor.count(), "files...", file=output)
   for f in cursor:
      print("\tFile", f["_id"], "owned by", f["uid"], file=output)
      files_notify.call("remove", f["_id"], days=kwargs["remove_days"])
      fs.delete(ObjectId(f["_id"]))

   cursor = db.fs.files.find({ "assigned": False, "uploadDate": { "$lte": warning } })
   print("Warning", cursor.count(), "files...", file=output)
   for f in cursor:
      print("\tFile", f["_id"], "owened by", f["uid"], file=output)
      files_notify.call("warning", f["_id"], days=kwargs["warning_days"], days_till_remove=days_till_remove)

   out = output.getvalue()
   output.close()
   return out