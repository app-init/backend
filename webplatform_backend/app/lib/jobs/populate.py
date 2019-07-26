from lib.imports.default import *
import lib.jobs.scheduled.add as add_job

permissions = "jobAdmin"

def call(**kwargs):
   manager = Manager()

   for i in range(0, 1000):
      params = {
         "name": "test" + str(i),
         "description": "SDfsdfsdf",
         "api": "jobs.test",
         "admin": True,
         "uid": "mowens",
         "hostname": manager.get_hostname(),
      }
      add_job.call(**params)