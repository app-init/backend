from lib.imports.default import *
import lib.se.get as get_se


def call(**kwargs):
   manager = Manager()
   db = manager.db("support-exceptions")

   cursor = db.se.find({}).distinct("se_id")
   for se_id in cursor:
      get_se.call(id=se_id)
   return True