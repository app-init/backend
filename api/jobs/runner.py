from multiprocessing import Process
from bson.objectid import ObjectId
from queue import Empty
from time import time, sleep
from lib.utils.db import Manager

class JobRunner(Process):

   def __init__(self, scheduler, queue):
      super(JobRunner, self).__init__()
      self.scheduler = scheduler
      self.queue = queue
      self._id = ObjectId()
      self.job_id = None
      self.scheduler.db.runners.insert({
         "_id": self._id,
         "job_id": None,
      })

   def run(self):
      while True:
         try:
            job = self.queue.get(timeout=2)
            if job is None:
               print(self._id, " is stopping...")
               break
            elif job == "refresh":
               self.scheduler.modules._reinit()
               continue

            job_id = ObjectId(job["id"])

            latest = self.scheduler.db.scheduled.find_one({ "_id" : job_id })
            if latest != None and latest["status"] != "stopped":
               self.scheduler.db.runners.update(
                  { "_id": self._id },
                  { "$set": { "job_id": job_id } }
               )
               self.scheduler.db.scheduled.update(
                  { "_id": job_id },
                  { "$set": { "status": "running", "rid": self._id  } }
               )
               job["rid"] = self._id
               self.run_job(job)
            else:
               print(job_id, "was stopped!")
         except Empty:
            pass
         finally:
            sleep(0.1)

   def run_job(self, job_data):
      from lib.jobs.interval.next import call as get_next_run_time
      # record when the job starts
      job_data["start_time"] = Manager.get_current_time()

      # run the job
      try:
         modules_list = self.scheduler.modules.get_all_modules()
         if job_data["api"] not in modules_list.keys():
            raise Exception("""%s is not in the API modules""" % job_data["api"])

         module_data = self.scheduler.modules.get(job_data['api'], data=True)
         module = module_data['obj']

         permissions = self.scheduler.manager.sessions.get_permissions(job_data["uid"])
         access = self.scheduler.modules.check_permissions(module_data, permissions)
         if not access:
            raise Exception("""%s does not have permission to call %s""" % (job_data["uid"], job_data["api"]))

         self.scheduler.manager.set_hostname(job_data["hostname"])

         result_data = self.scheduler.modules.call(module=module_data['obj'], **job_data["kwargs"])

         # send the results to the db and notify the user
         res_id = self.submit_result(job_data, result_data, True)
         self.scheduler.modules.call("jobs.notify", action="finished", job=job_data)

         # try to reschedule the job or update its status to finished
         try:
            if job_data["interval"]["ends"]["mode"] != "occurence":
               self.scheduler.db.scheduled.update(
                  { "_id": ObjectId(job_data["id"]), "status": { "$ne": "stopped" } },
                  { "$set": {
                      "status": "waiting",
                      "run_time": get_next_run_time(prev_rt=job_data["run_time"], interval=job_data["interval"]),
                      "res_id": res_id
                    }
                  }
               )
            else:
               self.scheduler.db.scheduled.update(
                  { "_id": ObjectId(job_data["id"]), "status": { "$ne": "stopped" } },
                  { "$set": {
                      "status": "waiting",
                      "run_time": get_next_run_time(prev_rt=job_data["run_time"], interval=job_data["interval"]),
                      "res_id": res_id,
                      "interval": job_data["interval"]
                    }
                  }
               )
         except Exception: # get_next_run_time failed, so finish job
            # import traceback
            # print(traceback.format_exc())
            # print("Finishing job...")
            self.finish_job(res_id, job_data)
      except Exception: # modules.call failed, so job failed
         import traceback
         print(job_data["id"], "failed...")
         res_id = self.submit_result(job_data, traceback.format_exc(), False)
         self.scheduler.modules.call("jobs.notify", action="failed", job=job_data)
         self.scheduler.db.scheduled.update(
            { "_id": ObjectId(job_data["id"]) },
            { "$set": {
                  "status": "failed",
                  "res_id": res_id,
               }
            }
         )
         # TODO notify user job failed
      finally:
         self.scheduler.db.runners.update(
            { "_id": self._id },
            { "$set": { "job_id": None } }
         )

   def submit_result(self, job_data, result, success):
         #TODO somehow we will limit this to only 16MB? maybe within mongo...
         status = None
         if success:
            status = "success"
         else:
            status = "failed"

         finish = Manager.get_current_time()
         ttl_time = (finish - job_data["start_time"]).total_seconds()

         result_data = {
            "api": job_data["api"],
            "uid": job_data["uid"],
            "run_time": job_data["run_time"],
            "start_time": job_data["start_time"],
            "finish_time": finish,
            "ttl_time": ttl_time,
            "result": result,
            "job_id": ObjectId(job_data["id"]),
            "status": status,
            "_id": ObjectId()
         }

         if "kwargs" in job_data:
            result_data["kwargs"] = job_data["kwargs"]

         self.scheduler.db.results.insert(result_data)
         return result_data["_id"]

   def finish_job(self, res_id, job_data):
      self.scheduler.db.scheduled.update(
         { "_id": ObjectId(job_data["id"]), "status": { "$ne": "stopped"  } },
         { "$set": {
               "status": "finished",
               "res_id": res_id
            }
         }
      )
