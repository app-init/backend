from lib.imports.default import *
import requests

requests.packages.urllib3.disable_warnings()

def call(**kwargs):
   manager = Manager()
   db = manager.db("release-planning")

   base_url = "https://10.8.80.28/pp-admin/api/latest/"
   headers = {
      'Accept': 'application/json'
   }

   request_kwargs = {
      "headers": headers,
      "verify": False
   }

   response = requests.get(base_url + 'releases/?all', **request_kwargs).json()

   for release in response:
      db.cache.update({"id": release['id'], "type": "release"}, {"$set": release}, upsert=True)

   return {"data": response}
