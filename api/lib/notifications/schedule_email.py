from lib.imports.default import *
import lib.jobs.scheduled.add as schedule_job
import lib.jobs.scheduled.get as get_job
import lib.jobs.scheduled.edit as edit_job
from datetime import datetime
from pytz import timezone
import smtplib, pytz, time


def call(**kwargs):
   job = {
      'api': 'jobs.notifications.email',
      'name': 'Batch Email',
      'description': 'Sending batch emails',
      'uid': 'mowens',
      'admin': True,
      'hostname': Manager().get_hostname(),
      'emails': kwargs['emails'],
   }

   job_check = get_job.call(name=job['name'])

   if job_check != None:
      for i in ["status", "res_id", "displayInterval", "kwargs"]:
         if i in job_check:
            del job_check[i]

      tz = timezone("US/Eastern")
      run_time = tz.localize(datetime.utcnow())

      job_check['run_time'] = time.mktime(run_time.timetuple())
      job_check['emails'] = job['emails']

      return edit_job.call(**job_check)
   else:
      return schedule_job.call(**job)
