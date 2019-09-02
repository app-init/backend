from appinit_backend.lib.imports import *
import pytz, datetime

def call(**kwargs):
   output = []
   for tz in pytz.common_timezones:
      now = datetime.datetime.now(pytz.timezone(tz))
      offset = now.utcoffset().total_seconds() / 60 / 60

      output.append("%s (%s %s)" % (tz, now.tzname(), int(offset)))
   return output
