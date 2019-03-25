from lib.imports.default import *
import lib.jobs.interval.display as display

permissions = "developer"

def call(**kwargs):
   manager = Manager()

   db = manager.db("jobs")

   output = []
   cursor = None

   if "uid" in kwargs:
      permissions = manager.sessions.get_permissions(kwargs["uid"])
      if "jobAdmin" in permissions and "admin" in kwargs and kwargs["admin"]:
         if "status" not in kwargs or kwargs["status"] == "all":
            cursor = db.scheduled.find({ "admin": True })
         else:
            cursor = db.scheduled.find({ "admin": True, "status": kwargs["status"]})
      else:
         if "status" not in kwargs or kwargs["status"] == "all":
            cursor = db.scheduled.find({"uid": kwargs["uid"]})
         else:
            cursor = db.scheduled.find({
               "uid": kwargs["uid"],
               "status": kwargs["status"]
            })
   else:
      cursor = db.scheduled.find()

   for i in cursor:
      job = manager.parse_cursor_object(i)
      if "interval" in job:
         job["displayInterval"] = display.call(**job["interval"])
      else:
         job["displayInterval"] = "N/A"
      output.append(job)

   return output