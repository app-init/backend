from lib.imports.default import *
import requests

requests.packages.urllib3.disable_warnings()

def call(**kwargs):
   manager = Manager()
   db = manager.db("cee-tools")

   base_url = "https://10.8.80.28/pp-admin/api/latest/"
   headers = {
      'Accept': 'application/json'
   }

   request_kwargs = {
      "headers": headers,
      "verify": False
   }

   response = requests.get(base_url + 'products/?all', **request_kwargs).json()
   return response
