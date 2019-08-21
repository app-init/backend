from lib.imports.default import *
import time

def call(**kwargs):
   start = time.time()
   temp = {
      "test": "dict",
      "apple": "orange",
   }
   end = time.time()
   print(end - start)
   return temp