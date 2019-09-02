from appinit_backend.lib.imports import *
from appinit_backend.app.lib.jobs.scheduled import add as add_job

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