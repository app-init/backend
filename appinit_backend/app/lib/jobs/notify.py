from appinit_backend.lib.imports import *
from appinit_backend.lib.notifications import email as email_notifications


def call(action, job=None):
   manager = Manager()
   users = set()
   title = None
   body = None
   if action == "stopped":
      title = "Jobs-Scheduler has stopped"
      # groups.add("jobs.scheduler.stopped")
      users.add("mowens")
      body = "All runners have finished their remaining jobs, and the scheduler has stopped. The container is safe for stopping or restarting."
   elif job is not None:
      jid = None
      if "_id" in job:
         jid = job["_id"]
      else:
         jid = job["id"]
      users.add(job["uid"])
      title = """Job %s has %s""" % (jid, action)
      body = """Job <a href="https://%s/jobs/%s/results/">%s</a> running '%s' has %s.""" % (manager.get_hostname(), jid, jid, job["api"], action)
   else:
      return None

   email_notifications.call("Job Runner", title, users, body, job=False)