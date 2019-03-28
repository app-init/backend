"""
This script converts date strings into datetime objects.
"""

from lib.imports.default import *

def to_date(date_string):
   from datetime import datetime
   from pytz import timezone
   import pytz

   if isinstance(date_string, str):
      try:
         date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%f")
      except ValueError:
         date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
   else:
      date = date_string

   return Manager.local_to_utc(date, 'US/Eastern')

def convert(db_name, collection, field):
   manager = Manager()
   db = manager.db(db_name)

   cursor = db[collection].find()

   for document in cursor:
      if field in document:
         datestring = document[field]

         date = to_date(datestring)

         update = {}
         update[field] = date

         db[collection].update(
            {
               "_id": document["_id"],
            },
            {
               "$set": update,
            }
         )

def call(**kwargs):
   convert('support-exceptions', 'comments', 'created')
   convert('support-exceptions', 'se', 'duration')
   convert('findsbr', 'comments', 'created')
