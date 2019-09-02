from appinit_backend.lib.imports import *
from . import meta


def call(**kwargs):
   from gridfs import GridFS
   from requests import head
   from datetime import datetime

   manager = Manager()
   db = manager.db("files")
   fs = GridFS(db)

   allowed = False
   excluded = False
   if "allowed" in kwargs:
      allowed = kwargs["allowed"]
   elif "allow_filter" in kwargs:
      allowed = kwargs["allow_filter"]
   elif "excluded" in kwargs:
      excluded = kwargs["excluded"]
   elif "exclude_filter" in kwargs:
      excluded = kwargs["exclude_filter"]


   isAttached = False
   if "isAttached" in kwargs and type(kwargs["isAttached"]) is bool:
      isAttached = kwargs["isAttached"]

   def _check_type(ftype):
      if allowed:
         if type(allowed) is list and ftype not in allowed:
            return str(ftype) + " is not an allowed file type."
         elif type(allowed) is str and allowed not in ftype:
            return str(ftype) + " is not an allowed file type."
      elif excluded:
         if type(excluded) is list and ftype in excluded:
            return str(ftype) + " is an excluded file type."
         elif type(excluded) is str and excluded in ftype:
            return str(ftype) + " is an excluded file type."
      return None

   def _read_chunk(file_obj, size):
      while True:
         data = file_obj.read(size)
         if not data:
            break

         yield data

   def _url(url):
      # TODO remove verify=False, and set up requests to verify url
      head_data = head(url, verify=False).headers
      meta_data = {
         # "size": int(head_data["Content-Length"]),
         "type": head_data["Content-Type"],
         "uid": kwargs["uid"],
         "filename": url,
         "isAttached": isAttached,
         "url": True,
         "_id": ObjectId(),
         "uploadDate": datetime.now(),
         "attached": {
            "db": kwargs['db'],
            "collection": kwargs['collection'],
            "key": kwargs['key'],
            "id": kwargs['id'],
            "object": kwargs['objectType'],
         }
      }
      check = _check_type(meta_data["type"])
      if check is not None:
         return check

      db.fs.files.insert(meta_data)

      return meta.call(id=meta_data["_id"])

   def _file(uploaded):
      meta_data = {
        "filename": uploaded.filename,
      #   "size": uploaded.content_length,
        "contentType": uploaded.mimetype,
        "uid": kwargs["uid"],
        "_id": ObjectId(),
        "isAttached": isAttached,
        "attached": {
            "db": kwargs['db'],
            "collection": kwargs['collection'],
            "key": kwargs['key'],
            "id": kwargs['id'],
            "objectType": kwargs['objectType'],
        }
      }
      check = _check_type(meta_data["contentType"])
      if check is not None:
         return check

      f = fs.new_file(**meta_data)

      for chunk in _read_chunk(uploaded, 1024):
         f.write(chunk)

      f.close()
      return meta.call(id=meta_data["_id"])

   output = []
   if "files" in kwargs:
      for f in kwargs["files"]:
         output.append(_file(f))

   if "url" in kwargs:
      # try:
      output.append(_url(kwargs["url"]))
      # except Exception:
      #    pass
   elif "urls" in kwargs:
      for url in kwargs["urls"]:
         try:
            output.append(_url(url))
         except Exception:
            pass

   if not len(output):
      return False
   elif len(output) == 1:
      return output[0]
   else:
      return output