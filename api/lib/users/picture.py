from lib.imports.default import *

action = "get"

def call(*args, **kwargs):
   return Manager().get_picture_url(kwargs['email'])