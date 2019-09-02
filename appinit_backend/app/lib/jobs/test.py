from appinit_backend.lib.imports import *
import random, time

permissions = "developer"

def call(**kwargs):
   manager = Manager()
   db = manager.db("test")
   start = time.time()

   limit = 1000
   a = [i for i in range(0, limit)]
   # index = random.randint(0, limit)
   # print("Running test with", index)
   _ids = []
   for i in range(0, limit):
      doc = {
         "_id": ObjectId(),
         "value": i
      }
      db.test.insert(doc)
      _ids.append(doc['_id'])

   for i in _ids:
      db.test.remove({"_id": i})
   end = time.time()
   print(end - start)
   return end - start