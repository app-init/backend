"""
This script converts the timestamp field in logs and run_time, start_time and finish_time fields in jobs from seconds to a utc datetime object
"""
from lib.utils.db import Manager

def is_number(data):
   return isinstance(data, int) or isinstance(data, float)

def timestamp_to_datetime(ts):
   from datetime import datetime

   date = datetime.fromtimestamp(ts)
   return Manager.local_to_utc(date, 'US/Eastern')

def convert(database, collection, fields):
   manager = Manager()
   db = manager.db(database)

   cursor = db[collection].find()

   for document in cursor:
      update = {}
      for field in fields:
         if field not in document:
            continue

         if is_number(document[field]):
            update[field] = timestamp_to_datetime(document[field])
      if len(update.keys()) > 0:
         db[collection].update(
            {
               "_id": document["_id"]
            },
            {
               "$set": update
            }
         )

def call(**kwargs):
   convert('logging', 'logs', ['timestamp'])
   convert('jobs', 'results', ['start_time', 'run_time', 'finish_time'])
   convert('jobs', 'scheduled', ['run_time'])
   convert('support-exceptions', 'se', ['lastUpdated'])
