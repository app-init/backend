from appinit_backend.lib.imports import *
from appinit_backend.app.lib.jobs.scheduled import get as scheduled_get

permissions = "developer"
action = "add"

def call(**kwargs):
   from time import struct_time, time, mktime, strptime
   import datetime

   manager = Manager()
   db = manager.db("jobs")
   job = {
      "hostname": manager.get_hostname()
   }

   if "api" in kwargs and "uid" in kwargs and "admin" in kwargs and "description" in kwargs and "name" in kwargs:
      job["description"] = kwargs["description"]
      job["name"] = kwargs["name"]
      job["api"] = kwargs["api"]
      job["uid"] = kwargs["uid"]
      job["admin"] = kwargs["admin"]

      job["status"] = "waiting"
      if kwargs["api"] != "jobs.scheduler":
         del kwargs["api"]
         del kwargs["uid"]
         del kwargs["admin"]
         del kwargs["description"]
         del kwargs["name"]

      if "run_time" not in kwargs:
         job["run_time"] = Manager.get_current_time()
      else:
         run_time = kwargs["run_time"]
         del kwargs["run_time"]
         run_time = Manager.timestamp_to_datetime(run_time)
         job["run_time"] = run_time

      if "interval" in kwargs:
         interval = kwargs["interval"]
         del kwargs["interval"]
         if (type(interval) is dict and "ends" in interval and "repeats" in interval and "every" in interval):
            interval["repeats"] = interval["repeats"].lower()
            if interval["repeats"] != "weekly" and "days" in interval:
               del interval["days"]

            if type(interval["ends"]) is dict and "mode" in interval["ends"]:
               if interval["ends"]["mode"] != "ondate" and "on" in interval["ends"]:
                  del interval["ends"]["on"]
               elif interval["ends"]["mode"] == "ondate" and type(interval["ends"]["on"]) is str:
                  string = "%Y-%m-%dT%H:%M:%S.%fZ"
                  interval["ends"]["on"] = datetime.datetime.strptime(interval["ends"]["on"], string).timetuple()

               if interval["ends"]["mode"] != "occurence" and "max_occurence" in interval["ends"]:
                  del interval["ends"]["max_occurence"]

               if interval["ends"]["mode"] == "occurence":
                  interval["ends"]["occurences"] = 0

               job["interval"] = interval

      job["kwargs"] = kwargs
      job["_id"] = ObjectId()
      db.scheduled.insert(job)
      scheduled_get.call(id=job["_id"])
      return job
