from flask import g
from datetime import datetime, timedelta
from pytz import timezone
import pytz

import lib.settings.get as get_user_setting
import lib.settings.set as set_user_setting

def check_user_timezone(session, request):
   if "Webplatform-Timezone" in request.headers:
      tz = request.headers['Webplatform-Timezone']
      user_timezone = timezone(tz)

      current = datetime.now(user_timezone)
      tz_offset = current.utcoffset().total_seconds() / 60 / 60

      setting = get_user_setting.call(name="Timezone", uid=session.uid, application="system", output="uid")

      if len(setting) < 1:
         now = datetime.now(pytz.timezone(tz))
         setting = {
            "name": "Timezone",
            "value": "%s (%s %s)" % (tz, now.tzname(), tz_offset),
         }

         set_user_setting.call(**setting)
