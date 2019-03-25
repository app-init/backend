from io import StringIO
import pytz
from pytz import timezone

from lib.imports.default import *
import lib.se.se_parse_cursor as parse_cursor
import lib.notifications.email as email_notifications
import lib.settings.get as get_user_settings
import lib.se.list.stale as get_stale
from lib.utils.businessdays import count_business_days, get_stale_days

def call(**kwargs):
   output = StringIO()

   manager = Manager()
   is_prod = manager.settings.get_instance() == "prod"

   db = manager.db("support-exceptions")

   staleSeIds = get_stale.call()

   print("Notifying...", file=output)

   data = {}

   se_dict = {}

   for se_id in staleSeIds:
      cursor = db.se.find_one({ "se_id": se_id })
      se = parse_cursor.call(cursor)
      se_dict[se['id']] = se

      se_date = se["lastUpdated"]

      # find number of business days between shifted start date
      se_bu_days_since = count_business_days(se_date, datetime.datetime.utcnow())

      for uid, setting in __get_users(se):
         try:
            tz = timezone(setting)
            new_se_date = tz.localize(se_date)
         except pytz.exceptions.UnknownTimeZoneError:
            new_se_date = se_date

         if uid not in data:
            data[uid] = {}

         # adding the SE to the list of stale SEs that the user will be notified about
         data[uid][se['id']] = {
            'last_updated': new_se_date,
            'bu_days_since': se_bu_days_since,
         }


   notifications = []

   def build_se_list(se_data):
      se_list = ""

      for se_id, se in __sort_se_by_dates(se_data):
         account_name = se_dict[se_id]['accountName']
         product = se_dict[se_id]['product']
         title = se_dict[se_id]['title']

         se_list += """
            <li style="margin-bottom: 5px; font-style: normal; font-weight: normal;">
               <a href="%s/support-exceptions/id/%s"><b>SE #%s</b></a> - <b>Updated on:</b> %s
               <ul style="padding-left: 5px;">
                  <li style="margin-top: 5px;"><b>Customer Name:</b> %s</li>
                  <li><b>Product:</b> %s</li>
                  <li><b>Title:</b> %s</li>
               </ul>
               <br />
            </li>
         """ % (manager.get_hostname(), se_id, se_id, se['last_updated'].strftime('%b %d, %Y at %I:%M%p %Z'), account_name, product, title)

      return """
         <ul style="padding-left: 15px">
            %s
         </ul>
      """ % (se_list)

   # email each users a summary of stale exceptions
   for uid, se_data in data.items():
      header = __build_header(get_stale_days())
      message = __build_message(header)
      se_list = build_se_list(se_data)
      subject = __build_subject()
      notifications.append({
         'subject': subject,
         'message': message,
         'uid': uid,
         'size': len(se_data.items()),
         'se_list': se_list,
      })

      if is_prod:
         __send_notification(uid, subject, message, se_list)

   # emailing just the notification with the largest stale SE list size for testing
   if not is_prod:
      __send_dev_notification(notifications)

   out = output.getvalue()
   output.close()
   return out

# generates the uids associated with a SE
def __get_users(se):
   users = se['cc']
   users += list(se['approvals'].keys())
   users.append(se['creator']['uid'])

   if len(se['assigned']) > 0:
      users.append(se['assigned']['uid'])

   kwargs = {
      "application": "system",
      "output": "uid",
      "name": "Timezone"
   }
   for uid in users:
      kwargs['uid'] = uid
      setting = get_user_settings.call(**kwargs)

      if "value" in setting:
         setting = setting['value']
      else:
         setting = 'UTC'

      yield uid, setting

def __build_message(header):
   return """
      %s
      <br>
   """ % (header)

def __sort_se_by_dates(se_data):
   # sorting list of stale SEs by the last updated date, from newest to oldest
   return sorted(se_data.items(), key=lambda x: x[1]['last_updated'], reverse=True)

def __build_subject():
   return 'Stale SEs - %s' % (datetime.datetime.utcnow().strftime('%Y-%m-%d'))

def __build_header(days):
   return "The following support exceptions have not been updated in the last %s business days" % (days)

def __send_notification(to, subject, message, se_list):
   email_notifications.call('Support Exceptions', subject, to, message, action=False, post_text=se_list, p_tag=False)

def __send_dev_notification(notifications):
   data = sorted(notifications, key=lambda x: x['size'])[-1]
   email_notifications.call('Support Exceptions', data['subject'], ['dolee'], data['message'], action=False, post_text=data['se_list'], p_tag=False)
