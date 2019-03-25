from lib.imports.default import *
import simplejson

admin = True

def call(*args, **kwargs):
   manager = Manager()
   db = manager.db('logging')

   # create the proper dictionary for the time limits for a mongo query
   time_limits = {}


   if 'start' in kwargs:
      start = Manager.timestamp_to_datetime(kwargs['start'])
      time_limits['$gte'] = start
      del kwargs['start']

   if 'end' in kwargs:
      end = Manager.timestamp_to_datetime(kwargs['end'])
      time_limits['$lte'] = end
      del kwargs['end']

   maximum = None
   if 'limit' in kwargs:
      maximum = kwargs['limit']
      del kwargs['limit']

   if 'failuresOnly' in kwargs:
      kwargs['failure'] = { "$exists" : True }
      del kwargs['failuresOnly']

   # module path comes in as "module", which can either be the exact path or any valid
   # parent module. This needs a $or in kwargs to work right.
   if 'module' in kwargs:
      kwargs['$or'] = [
         { 'path': kwargs['module'] },
         { 'parent_modules': kwargs['module'] }
      ]
      del kwargs['module']

   # if time limits weren't set, this prevents kwargs['timestamp'] = {}
   if time_limits:
      kwargs['timestamp'] = time_limits

   pipeline = []

   pipeline.append({ "$match" : kwargs })
   # would like to exclude the parent_modules field but Mongo
   # does not currently support arbitrary field exclusions in
   # an aggregation

   # sort by timestamp in descending order (so more recent logs appear first)
   pipeline.append({ "$sort" : { 'timestamp': -1 } })

   if maximum is not None:
      pipeline.append({ "$limit" : maximum })

   output = []
   for log in db.logs.aggregate( pipeline ):
      # remove the list of parent modules
      del log['parent_modules']

      output.append(log)

   return output
