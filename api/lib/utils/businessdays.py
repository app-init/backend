import datetime
import lib.settings.get as get_setting

def get_stale_days():
   kwargs = {
      'application': 'support-exceptions',
      'name': 'Stale-Days',
      'permissions': 'admin',
      'output': 'value',
   }

   stale_values = [int(value) for value in get_setting.call(**kwargs)['values']]

   output = 0
   if stale_values:
      output = max(stale_values)
   else:
      output = 5

   return output

# returns the total number of business days between two dates
def count_business_days(fromdate, todate):
   daygenerator = (fromdate + datetime.timedelta(x + 1) for x in range((todate - fromdate).days))
   # count weekdays in between two dates
   return sum(1 for day in daygenerator if day.weekday() < 5)

# returns the shifted date based on the days passed in
# e.g. subtract_business_days(5) returns the date that is 5 business days before the current date.
def subtract_business_days(days):
   lastBusDay = datetime.datetime.utcnow()

   for i in range(days):
      # subtract 3 days if Monday, 2 if Sunday, 1 otherwise
      shift = datetime.timedelta(max(1, (lastBusDay.weekday() + 6) % 7 - 3))
      lastBusDay = lastBusDay - shift

   return lastBusDay

def get_stale_date():
   return subtract_business_days(get_stale_days())

def is_stale(se, stale_date):
   if se['status'] in ['new', 'in-progress']:
      return se['lastUpdated'] < stale_date
   # elif se['status'] == 'new':
   #    print([se['lastUpdated'], se['created']])
   #    return se['created'] < stale_date

   return False
