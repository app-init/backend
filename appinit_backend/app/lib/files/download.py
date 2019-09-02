from appinit_backend.lib.imports import *

def call(**kwargs):
   import gridfs

   manager = Manager()
   db = manager.db("files")
   fs = gridfs.GridFS(db)

   return fs.get(ObjectId(kwargs["id"]))