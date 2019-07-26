from datetime import datetime, timedelta
from xmlrpc.client import DateTime
from bson.objectid import ObjectId
from werkzeug.datastructures import FileStorage

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
   else:
      print(type(data))
      raise TypeError(repr(data) + " is not JSON serializable")

def convert_old(data):
   if isinstance(data, dict):
      for i in data:
         data[i] = convert_old(data[i])
      return data
   elif isinstance(data, list):
      for idx, val in enumerate(data):
         data[idx] = convert_old(val)
      return data
   elif isinstance(data, set):
      return convert_old(list(data))
   elif isinstance(data, bytes):
      return data.decode('utf-8')
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
   elif isinstance(data, datetime):
      delta = timedelta(hours=4)
      date = data - delta
      return str(date)
   # elif callable(data):
   #    return data()
   else:
      return str(data)

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
