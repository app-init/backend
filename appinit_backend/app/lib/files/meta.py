from appinit_backend.lib.imports import *

def call(**kwargs):
   import gridfs

   manager = Manager()
   db = manager.db("files")
   exclude = {
      "md5": False,
      "chunkSize": False,
      "length": False
   }

   if "id" in kwargs:
      kwargs["_id"] = kwargs["id"]
      del kwargs["id"]

   for key, value in kwargs.items():
      try:
         oid = ObjectId(value)
         kwargs[key] = oid
      except Exception:
         kwargs[key] = value

   cursor = db.fs.files.find_one(kwargs, exclude)
   return manager.parse_cursor_object(cursor)