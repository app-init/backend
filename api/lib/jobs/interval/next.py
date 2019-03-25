from lib.imports.default import *

permissions = "developer"

def call(**kwargs):
   from time import gmtime, mktime, time, strptime, struct_time
   from datetime import datetime
   from dateutil.relativedelta import relativedelta

   prev_rt = kwargs["prev_rt"]
   interval = kwargs["interval"]

   if "reschedule" in kwargs:
      reschedule = kwargs["reschedule"]
   else:
      reschedule = False

   # prev_date = datetime.utcfromtimestamp(prev_rt)
   prev_date = prev_rt
   new_date = None

   interval["every"] = int(interval["every"])
   if interval["repeats"] == "hourly":
      new_date = prev_date + relativedelta(hours=interval["every"])

   elif interval["repeats"] == "daily":
      new_date = prev_date + relativedelta(days=interval["every"])

   elif interval["repeats"] == "yearly":
      new_date = prev_date + relativedelta(years=interval["every"])

   elif interval["repeats"] == "monthly":
      new_date = prev_date + relativedelta(months=interval["every"])

      if prev_date.day < interval["original"]["day"]:
         delta_org = interval["original"]["day"] - prev_date.day
         end_of_new_month = new_date + relativedelta(day=31)
         delta_end = end_of_new_month.day - prev_date.day
         if delta_end < delta_org:
            new_date = new_date + relativedelta(days=delta_end)
         else:
            new_date = new_date + relativedelta(days=delta_org)

   elif interval["repeats"] == "weekly":
      days_of_the_week = [
         "Monday",
         "Tuesday",
         "Wednesday",
         "Thursday",
         "Friday",
         "Saturday",
         "Sunday"
      ]

      prev_weekday = prev_date.weekday()
      next_weekday = None
      for i in range(prev_weekday + 1, len(days_of_the_week)):
         if interval["days"][days_of_the_week[i]]:
            next_weekday = i
            break

      if next_weekday is not None: # theres another day of the week thats true, so skip to that
         delta_days = next_weekday - prev_weekday
         new_date = prev_date + relativedelta(days=delta_days)
      else: # skip every - 1 weeks then get the first day of the week that is true
         prev_date = prev_date + relativedelta(weeks=interval["every"], days=-prev_weekday)
         for i in range(prev_weekday + 1):
            if interval["days"][days_of_the_week[i]]:
               next_weekday = i
               break

         if next_weekday is None: # TODO should never happen! need to test
            print("Error in determining next weekly interval")
            raise Exception

         new_date = prev_date + relativedelta(days=next_weekday)

   if not reschedule:
      if interval["ends"]["mode"] == "occurence":
         interval["ends"]["occurences"] += 1
         if interval["ends"]["occurences"] >= interval["ends"]["max_occurence"]:
            print("Occurence interval job is ending")
            raise Exception
      elif interval["ends"]["mode"] == "ondate":
         end_date = Manager.local_timestamp_to_datetime(interval["ends"]["on"])
         if new_date > end_date:
            print("Ondate interval job is ending")
            raise Exception

   print(new_date)

   return new_date
