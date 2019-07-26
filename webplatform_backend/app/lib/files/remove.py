from lib.imports.default import *
import lib.files.meta as meta

action = "remove"

def call(**kwargs):
   if "id" in kwargs:
      file_obj = meta.call(id=kwargs['id'])
      if not file_obj['isAttached']:
         __remove(kwargs['id'])

   elif "ids" in kwargs and type(kwargs["ids"]) is list:
      for fid in kwargs["ids"]:
         file_obj = meta.call(id=fid)
         if not meta.call['isAttached']:
            __remove(fid)

   return True

def __remove(file_id):
   import gridfs

   manager = Manager()
   db = manager.db("files")
   fs = gridfs.GridFS(db)

   fs.delete(ObjectId(file_id))