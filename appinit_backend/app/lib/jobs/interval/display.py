from appinit_backend.lib.imports import *

permissions = "developer"

def call(**kwargs):

   display = None
   if kwargs["repeats"] == "yearly" and kwargs["every"] == 1:
      display = "Repeats annually on {0:02d}-{1:02d}".format(kwargs["original"]["month"], kwargs["original"]["day"])
   else:
      units = {
         "daily": "day(s)",
         "yearly": "years",
         "weekly": "week(s)",
         "monthly": "month(s)",
         "hourly": "hour(s)"
      }

      displayTemplate = "Repeats {repeats} every {every} {unit}"
      display = displayTemplate.format(**kwargs, unit=units[kwargs["repeats"]])

      if kwargs["repeats"] == "weekly":
         display += " on "
         for day in kwargs["days"]:
            if kwargs["days"][day]:
               display += day[:2] + ", "

         display = display[:-2]

   if kwargs["ends"]["mode"] != "never":
      display += " ending "
      if kwargs["ends"]["mode"] == "occurence":
         display += "after {0} occurrences".format(kwargs["ends"]["max_occurence"])
      else:
         from datetime import datetime
         from time import struct_time, time, mktime, strptime

         if type(kwargs['ends']['on']) is str:
            string = "%Y-%m-%dT%H:%M:%S.%fZ"
            kwargs["ends"]["on"] = datetime.strptime(kwargs["ends"]["on"], string).timetuple()
            kwargs["ends"]["on"] = mktime(kwargs["ends"]["on"])

         date = datetime.utcfromtimestamp(kwargs["ends"]["on"])
         display += "on {0:04d}-{1:02d}-{2:02d}".format(date.year, date.month, date.day)

   return display

def _ordinal_indicator(num):
   ones = num % 10
   tens = num % 100

   if ones == 1 and tens != 11:
      return str(num) + "st";

   if ones == 2 and tens != 12:
      return str(num) + "nd"

   if ones == 3 and tens != 13:
      return str(num) + "rd"

   return str(num) + "th"