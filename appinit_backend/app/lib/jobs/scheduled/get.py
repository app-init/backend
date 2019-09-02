from appinit_backend.lib.imports import *
from appinit_backend.app.lib.jobs.interval import display

permissions = "developer"

def call(**kwargs):
   manager = Manager()

   db = manager.db("jobs")

   if "id" in kwargs:
      cursor = db.scheduled.find_one({"_id": ObjectId(kwargs["id"])})

      if "interval" in cursor:
         cursor["displayInterval"] = display.call(**cursor["interval"])
      else:
         cursor["displayInterval"] = "N/A"

      return manager.parse_cursor_object(cursor)

   elif "name" in kwargs:
      cursor = db.scheduled.find_one({"name": kwargs["name"]})

      if cursor == None:
         return cursor

      if "interval" in cursor:
         cursor["displayInterval"] = display.call(**cursor["interval"])
      else:
         cursor["displayInterval"] = "N/A"

      return manager.parse_cursor_object(cursor)