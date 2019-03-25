from lib.imports.default import *
from lib.utils.businessdays import is_stale, get_stale_date

def call(**kwargs):
   manager = Manager()

   db = manager.db("support-exceptions")
   cursor = db.se.find()
   for se in cursor:
      if 'lastUpdated' in se:
         stale = is_stale(se, get_stale_date())

         db.se.update(
            {
               "_id": se["_id"],
            },
            {
               "$set": {
                  "isStale": stale,
               }
            }
         )
