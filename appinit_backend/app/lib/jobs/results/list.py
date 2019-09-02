from appinit_backend.lib.imports import *

permissions = "developer"

def call(**kwargs):

   manager = Manager()

   db = manager.db("jobs")

   if "id" in kwargs:

      cursor = db.results.find({ "job_id": ObjectId(kwargs["id"]) })
      output = []

      for i in cursor:
         output.append(manager.parse_cursor_object(i))

      return output