from lib.imports.default import *

permissions = ["admin", "jobAdmin"]

def call(**kwargs):
   manager = Manager()
   db = manager.db("jobs")

   db.alerts.update({"refresh": False}, { "$set": { "refresh": True } })