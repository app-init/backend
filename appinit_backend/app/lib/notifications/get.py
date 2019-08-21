from lib.imports.default import *

def call(*args, **kwargs):
   manager = Manager()
   db = manager.db("cee-tools")

   uid = kwargs['uid']

   cursor = db.notifications.find({"$or":[ {"to": { "$exists": uid }}, {"cc": { "$exists": uid }}] })

   output = []
   for i in cursor:
      temp = {}
      for key, value in list(i.items()):
         temp[key] = value
      output.append(temp)

   return output