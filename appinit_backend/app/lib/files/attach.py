from appinit_backend.lib.imports import *
from appinit_backend.app.lib.files import edit as files_edit

def call(**kwargs):
   kwargs["isAttach"] = True

   if "id" in kwargs:
      return files_edit.call(**kwargs)
   elif "ids" in kwargs and type(kwargs["ids"]) is list:
      output = []
      for _id in kwargs["ids"]:
         kwargs["id"] = _id
         output.append(files_edit(**kwargs))
      return output