from appinit_backend.lib.imports import *

permissions = "developer"

def call(**kwargs):
   manager = Manager()

   db = manager.db("jobs")

   if "id" in kwargs:
      db.stopped.insert({
         "job_id": ObjectId(kwargs["id"]),
         "remove": True
      })