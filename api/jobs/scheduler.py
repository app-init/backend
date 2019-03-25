from multiprocessing import Process
from multiprocessing import Manager as P_Manager
from bson.objectid import ObjectId
from queue import Queue, Full
from time import sleep, time
from jobs.runner import JobRunner
from lib.utils.modules import Modules
from lib.utils.db import Manager as CeeToolsManager

class Scheduler(Process):
   __instance = None
   __initialized = True

   def __new__(cls, *args, **kwargs):
      if cls.__instance is None:
         print("Creating a new", cls.__name__)
         cls.__instance = super(Scheduler, cls).__new__(cls)
         cls.__initialized = False
      return cls.__instance

   def __init__(self, settings):
      if self.__class__.__initialized: return
      self.__class__.__initialized = True
      print("Initializing the", self.__class__.__name__)
      super(Scheduler, self).__init__()
      self.settings = settings

   def run(self):
      import traceback

      #MongoClient needed to be initialized before process was forked
      self.manager = CeeToolsManager()
      self.modules = Modules(self.settings)
      self.db = self.manager.db("jobs")

      self.shared_memory = P_Manager()
      self.runners = {}
      self.runner_q = Queue()
      self.num_available_cores = self.settings.get_num_cores("jobs")
      print(self.num_available_cores)
      self.q_limit = 50 #TODO calculate this somehow based on memory

      # for some reason if scheduler crashes it doesnt print stack trace
      # this try/except with traceback will hopefully force it to
      try:
         self.db.alerts.remove({})
         self.db.alerts.insert({ "keep_running": True, "refresh": False })
         self.db.runners.remove({}) # clear out any ids of old runners
         # init and start runners
         for i in range(self.num_available_cores):
            queue = self.shared_memory.Queue(maxsize=self.q_limit)
            runner = JobRunner(self, queue)
            self.runners[runner._id] = {
               "queue": queue,
               "runner": runner,
            }
            self.runner_q.put(runner._id)
            runner.start()

         self.print_queues()
         start = time()

         while True:
            alert = self.db.alerts.find_one({ "keep_running": { "$exists": True } })
            if not alert["keep_running"]:
               self.stop_runners()
               break
            elif alert["refresh"]:
               print("Refreshing!")
               self.modules._reinit()
               self.db.alerts.update({ "refresh": True }, { "$set": { "refresh": False } })
               self.refresh_runners()

            self.get_stopped_jobs()
            # get the latest jobs that are ready
            current_utc_time = CeeToolsManager.get_current_time()
            current_edt_time = CeeToolsManager.utc_to_local(current_utc_time, 'US/Eastern')
            cursor = self.db.scheduled.find({
               "status": "waiting",
               "run_time": { "$lte": current_edt_time }
            })

            # if there are jobs to process
            if cursor.count() > 0:

               # for all the jobs
               for sj in cursor:
                  scheduled_job = self.manager.parse_cursor_object(sj)

                  # try to add the job to one of the queues
                  success = False
                  for i in range(self.runner_q.qsize()):

                     # get next runner
                     rid = self.runner_q.get()
                     try:
                        # try to add it to the queue
                        self.runners[rid]["queue"].put(scheduled_job, block=False)
                        self.db.scheduled.update(
                           { "_id": ObjectId(scheduled_job["id"]), "status": { "$ne": "running" } },
                           { "$set": { "status": "queued", "rid": ObjectId(rid) } }
                        )
                        success = True
                        break
                     except Full:
                        pass
                     finally:
                        self.runner_q.put(rid)

                  # all the queues are full
                  if not success:
                     # print("fuck")
                     break

            sleep(1.0)

         for rid, runner_entry in self.runners.items():
            runner_entry["runner"].join()

         self.modules.call("jobs.notify", action="stopped")
         print("Ttl time: " + str(time() - start))
      except Exception:
         print(traceback.format_exc())

   def stop_runners(self):
      while not self.runner_q.empty():
         self.get_stopped_jobs()
         rid = self.runner_q.get()
         try:
            self.runners[rid]["queue"].put(None, block=False)
         except Full:
            self.runner_q.put(rid)
         sleep(0.5)

   def refresh_runners(self):
      q = Queue()
      for (rid, runner_entry) in self.runners.items():
         q.put(rid)
      while not q.empty():
         rid = q.get()
         try:
            self.runners[rid]["queue"].put("refresh", block=False)
         except Full:
            q.put(rid)
         sleep(0.05)

   def get_stopped_jobs(self):
      cursor = self.db.stopped.find()

      if cursor.count() > 0:
         ids = []
         for stopped in cursor:
            ids.append(ObjectId(stopped["_id"]))
            job = self.db.scheduled.find_one({ "_id": ObjectId(stopped["job_id"]) })
            if job is not None:
               if "remove" in stopped and stopped["remove"] is True:
                  self.db.scheduled.remove(
                     { "_id": job["_id"] }
                  )
                  print("Removing job", job["_id"])
               else:
                  self.db.scheduled.update(
                     { "_id": job["_id"] }, #TODO dont set to stopped if already finished?
                     { "$set": {
                          "status": "stopped",
                          "res_id": None
                       }
                     }
                  )

               # if the job was running, kill the runner and make a new one
               if job["status"] == "running":
                  print("Stopping job", job["_id"])
                  rid = ObjectId(job["rid"])
                  try:
                     runner_entry = self.runners[rid]
                     runner_job = self.db.runners.find_one({ "_id": rid })
                     # TODO can else even happen?
                     if runner_job is not None and runner_job["job_id"] == job["_id"]:
                        print("Job was still running, stopping runner", rid)
                        # stop runner
                        runner_entry["runner"].terminate()

                        # create new runner with old one's queue
                        new_runner = JobRunner(self, runner_entry["queue"])
                        self.runners[new_runner._id] = {
                           "queue": runner_entry["queue"],
                           "runner": new_runner,
                        }

                        # delete old runner
                        del runner_entry["runner"]
                        del self.runners[rid]
                        self.db.runners.remove({ "_id": rid })
                        del rid

                        print("New runner", new_runner._id, "started")
                        new_runner.start()
                  except KeyError:
                     print("Runner", rid, "no longer exists, moving on")

               elif job["status"] == "finished":
                  # job just finished before we could stop it...
                  # remove its result
                  print("couldn't stop job", job["_id"], "in time... removing result", job["res_id"])
                  self.db.results.remove(
                     { "_id": ObjectId(job["res_id"]) }
                  )
            else:
               print("Job", stopped["job_id"], "no longer exists... moving on")

         # remake runner queue
         del self.runner_q
         self.runner_q = Queue()
         for rid in self.runners.keys():
            self.runner_q.put(rid)

         self.db.stopped.remove({ "_id": { "$in": ids } })
         self.print_queues()

   # function for teting and book-keeping
   def print_queues(self):
      print("Printing queues...")
      for rid in self.runners.keys():
         print(str(rid) + ":", self.runners[rid]["queue"].qsize())
