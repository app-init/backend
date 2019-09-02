from appinit_backend.lib.imports import *

def call(**kwargs):
   import gridfs

   manager = Manager()
   db = manager.db("files")
   output = []
   query = {}
   exclude = {
      "md5": False,
      "chunkSize": False,
      "length": False
   }

   if "ids" in kwargs and type(ids) is list:
      ids = []
      for i in kwargs["ids"]:
         ids.append(ObjectId(i))
      del kwargs["ids"]
      query["_id"] = { "$in": ids }

   if "uid" in kwargs:
      query["uid"] = kwargs["uid"]
      del kwargs["uid"]

   for key, value in kwargs.items():
      try:
         oid = ObjectId(value)
         query[key] = oid
      except Exception:
         query[key] = value

   cursor = db.fs.files.find(query, exclude)
   for i in cursor:
      if not i['isAttached']:
         output.append(manager.parse_cursor_object(i))
   return output