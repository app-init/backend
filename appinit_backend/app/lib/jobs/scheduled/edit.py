from appinit_backend.lib.imports import *
from appinit_backend.app.lib.jobs.scheduled import get as scheduled_get
from appinit_backend.app.lib.jobs.interval import next as get_next_run_time

permissions = "developer"
action = "edit"

def call(**kwargs):
   from time import struct_time, time, mktime, strptime

   manager = Manager()

   db = manager.db("jobs")

   if "id" not in kwargs:
      return None

   job_id = ObjectId(kwargs["id"])
   del kwargs["id"]

   job_data = scheduled_get.call(id=job_id)

   if "mode" in kwargs:
      if kwargs["mode"] == "rerun":

         if "interval" not in job_data:
            db.scheduled.update(
               { "_id": job_id },
               { "$set": {
                     "status": "waiting",
                     "run_time": Manager.get_current_time()
                 }
               }
            )
         else:
            if job_data["interval"]["ends"]["mode"] != "occurence":
               db.scheduled.update(
                  { "_id": job_id },
                  { "$set": {
                      "status": "waiting",
                      "run_time": get_next_run_time.call(prev_rt=job_data["run_time"], interval=job_data["interval"], reschedule=True),
                    }
                  }
               )
            else:
               db.scheduled.update(
                  { "_id": job_id },
                  { "$set": {
                      "status": "waiting",
                      "run_time": get_next_run_time.call(prev_rt=job_data["run_time"], interval=job_data["interval"], reschedule=True),
                      "interval": job_data["interval"]
                    }
                  }
               )

      elif kwargs["mode"] == "stop":
         db.stopped.insert({
            "job_id": job_id
         })
   elif "api" in kwargs and "uid" in kwargs and "name" in kwargs and "description" in kwargs:
      if "run_time" in kwargs:
         run_time = kwargs['run_time']
         run_time = Manager.timestamp_to_datetime(run_time)

         db.scheduled.update(
            { "_id": job_id },
            { "$set": {
                  "run_time": run_time,
               }
            }
         )
         del kwargs["run_time"]

      if "interval" in kwargs:
         interval = kwargs["interval"]
         del kwargs["interval"]

         interval["repeats"] = interval["repeats"].lower()

         if interval["repeats"] != "weekly" and "days" in interval:
            del interval["days"]

         if interval["ends"]["mode"] != "ondate" and "on" in interval["ends"]:
            del interval["ends"]["on"]

         if interval["ends"]["mode"] != "occurence" and "max_occurence" in interval["ends"]:
            del interval["ends"]["max_occurence"]

         if interval["ends"]["mode"] == "occurence":
            interval["ends"]["occurences"] = 0

         db.scheduled.update(
            { "_id": job_id },
            { "$set": {
                  "interval": interval,
               }
            }
         )

      new_job = {}
      old_status = job_data["status"]
      new_job["api"] = kwargs["api"]
      new_job["uid"] = kwargs["uid"]
      new_job["admin"] = kwargs["admin"]
      new_job["description"] = kwargs["description"]
      new_job["name"] = kwargs["name"]

      # Setting status to waiting, otherwise if edit called when job
      # is running, the edited job will not get run.
      # This allows multipled batched email jobs to get called by an api.
      new_job["status"] = "waiting"

      if kwargs["api"] != "jobs.scheduler":
         del kwargs["api"]
         del kwargs["uid"]
         del kwargs["admin"]
         del kwargs["description"]
         del kwargs["name"]

      new_job["kwargs"] = kwargs

      db.scheduled.update(
         { "_id": job_id },
         { "$set": new_job }
      )

   return scheduled_get.call(id=job_id)
