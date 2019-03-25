from lib.imports.default import *
import time

permissions = "developer"

def _fib(n):
   return _fib(n - 1) + _fib(n - 2) if n > 1 else n

def call(**kwargs):
   start = time.time()
   timed_fib = _fib(int(kwargs["size"]))
   end = time.time()
   print(end - start)
   return timed_fib