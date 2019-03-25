from lib.imports.default import *

def call(**kwargs):
   manager = Manager()
   db = manager.db("cee-tools")
   cache_cursor = db.cache.find_one({"name": "bugzilla-products-cache"})

   for product in cache_cursor['data']:
      db.products.update({"name": product['name']}, {"$set": product}, upsert=True)
