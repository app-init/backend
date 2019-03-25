from lib.imports.default import *
import lib.files.meta as meta


meta_schema = [
   "md5",
   "chunkSize",
   "length",
   "size",
   "filename",
   "type",
   "_id",
   "author",
   "uploadDate",
   "isAttached",
]

internal = True

def call(**kwargs):

   manager = Manager()
   db = manager.db("files")

   if "token" in kwargs:
      del kwargs["token"]

   if "id" in kwargs:
      file_id = ObjectId(kwargs["id"])
      del kwargs["id"]

      new_data = {}
      for (key, value) in kwargs.items():
         if key not in meta_schema:
            try:
               oid = ObjectId(value)
               new_data[key] = oid
            except Exception:
               new_data[key] = value

      db.fs.files.update(
         { "_id": file_id },
         { "$set": new_data }
      )

      return meta.call(id=file_id)