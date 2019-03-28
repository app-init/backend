from lib.imports.default import *

permissions = "developer"

def call(**kwargs):
   manager = Manager()

   db = manager.db("jobs")

   if "id" in kwargs:
      cursor = db.results.find_one({ "_id": ObjectId(kwargs["id"])})
      return manager.parse_cursor_object(cursor)