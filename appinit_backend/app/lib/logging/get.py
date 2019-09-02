from appinit_backend.lib.imports import *
import json

admin = True

def call(*args, **kwargs):
   manager = Manager()
   db = manager.db('logging')

   pipeline = []
   pipeline.append({ "$match" : kwargs })

   kwargs['_id'] = ObjectId(kwargs['id'])
   del kwargs['id']

   output = []
   for log in db.logs.aggregate( pipeline ):
      # remove the list of parent modules
      del log['parent_modules']
      log['request']['kwargs'] = json.loads(log['request']['kwargs'])
      output.append(log)

   if not output:
      return {}

   return output[0]
