from lib.imports.default import *
import time

def call(**kwargs):
   start = time.time()
   temp = kwargs;
   end = time.time()
   print(end - start)
   return temp