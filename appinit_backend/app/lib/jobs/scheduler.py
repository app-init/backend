from appinit_backend.lib.imports import *
from appinit_backend.app.lib.jobs.scheduled import add as add_job

permissions = "developer"

def call(**kwargs):
   from io import StringIO
   manager = Manager()
   output = StringIO()

   if "jobs" in kwargs and type(kwargs["jobs"]) is list and \
    "name" in kwargs and "uid" in kwargs and "description" in kwargs and \
    "admin" in kwargs:

      name = kwargs["name"]
      jobs = kwargs["jobs"]
      uid = kwargs["uid"]
      admin = kwargs["admin"]
      description = kwargs["description"]
      del kwargs["name"]
      del kwargs["jobs"]
      del kwargs["uid"]
      del kwargs["admin"]
      del kwargs["description"]
      del kwargs["api"]

      print("Adding", len(jobs), "jobs...", file=output)
      for i in range(len(jobs)):
         job = jobs[i]
         params = {
            "admin": admin,
            "api": job,
            "uid": uid,
            "description": description,
            "name": """%s-%s-%s""" % (name, i, job),
            "hostname": manager.get_hostname(),
         }
         print("\t", params["name"], file=output)
         add_job.call(**params, **kwargs)

      out = output.getvalue()
      output.close()
      return out