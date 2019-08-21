from lib.imports.default import *

permissions = "jobAdmin"

def call(**kwargs):
   print("Recovering jobs...")
   manager = Manager()
   db = manager.db("jobs")

   rids = db.runners.distinct("_id")

   cursor = db.scheduled.find({ "status": { "$in": ["queued", "running"] }, "rid" : { "$nin": rids } })
   ids = []
   for i in cursor:
      print("\tJob:", i["_id"])
      ids.append(i["_id"])

   db.scheduled.update(
      { "_id": { "$in": ids } },
      { "$set": {
            "status": "waiting",
         }
      },
      multi=True
   )