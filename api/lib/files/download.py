from lib.imports.default import *
#
def call(**kwargs):
   import gridfs

   manager = Manager()
   db = manager.db("files")
   fs = gridfs.GridFS(db)

   return fs.get(ObjectId(kwargs["id"]))