from lib.imports.default import *

def call(**kwargs):
   manager = Manager()
   db = manager.db("cache")

   if "text" not in kwargs:
      return []

   cursor = db.users.find({"$text": {"$search": kwargs['text']}}, {"score": {"$meta": "textScore"}, "uid": 1, "cn": 1, "picture": 1})
   # results = cursor.skip(kwargs['offset']).limit(kwargs['limit']).sort([("score", {"$meta":"textScore"})])
   results = cursor.sort([("score", {"$meta":"textScore"})])

   output = []
   for i in results:
      if "manager" in i and kwargs['text'] in i['manager']:
         continue

      output.append(i)

   return output
