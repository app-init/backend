from datetime import datetime, timedelta
from xmlrpc.client import DateTime
from bson.objectid import ObjectId
from werkzeug.datastructures import FileStorage
from webplatform_auth.lib.session import Session

def convert(data):
   if isinstance(data, dict):
      for i in data:
         data[i] = convert(data[i])
      return data
   elif isinstance(data, list):
      for idx, val in enumerate(data):
         data[idx] = convert(val)
      return data
   elif isinstance(data, set):
      return convert(list(data))
   elif isinstance(data, str):
      return data
   elif isinstance(data, bool):
      return data
   elif isinstance(data, float):
      return data
   elif isinstance(data, tuple):
      return data
   elif isinstance(data, int):
      return data
   elif isinstance(data, bytes):
      return data.decode('utf-8')
   elif isinstance(data, ObjectId):
      return str(data)
   elif isinstance(data, datetime):
      return str(data)
   elif isinstance(data, DateTime):
      return str(data)
   elif isinstance(data, set):
      return list(data)
   elif isinstance(data, FileStorage):
      return data.filename
   elif isinstance(data, Session):
      output = {}
      for key in dir(data):
         output[key] = convert(getattr(data, key))
      return output
   else:
      print(type(data))
      raise TypeError(repr(data) + " is not JSON serializable")

def convert_keys(data):
   if isinstance(data, dict):
      for i in data:
         data[str(i)] = convert_keys(data[i])
      return data
   elif isinstance(data, list):
      for idx, val in enumerate(data):
         data[idx] = convert(val)
      return data
   elif isinstance(data, set):
      return convert(list(data))
   else:
      return data
