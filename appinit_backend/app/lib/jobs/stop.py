from lib.imports.default import *
permissions = ["admin", "jobAdmin"]

def call(**kwargs):
   manager = Manager()
   db = manager.db("jobs")

   db.alerts.update({"keep_running": True }, { "$set": { "keep_running": False } })