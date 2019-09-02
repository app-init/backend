import smtplib
import traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from appinit_backend.lib.imports import *
from appinit_backend.lib.notifications import schedule_email as send_email

from appinit_backend.app.lib.settings import get as get_user_settings
from appinit_backend.app.lib.users import get as get_user

settings = Settings()
app_title = settings.get_variable("app-title")
smtp_server = settings.get_variable("smtp")
admins_email = settings.get_variable("admins")
reply_to = settings.get_variable("reply-to")
issue_tracker = settings.get_variable("issue-tracker")

internal = True

def __html_to_plaintext(html):
   from html.parser import HTMLParser

   class PlainTextBuilder(HTMLParser):
      def __init__(self):
         HTMLParser.__init__(self)
         self.text = ""
         self.indent = 0
         self.tag = ""

      def handle_starttag(self, tag, attrs):
         self.tag = tag
         if tag == 'br':
            self.text += "\n"
         elif tag == 'ul':
            self.indent += 2
            self.text += '\n'
         elif tag == 'li':
            self.text += ' ' * self.indent
            self.text += '- '

      def handle_endtag(self, tag):
         if tag == 'ul':
            self.indent -= 2
         if tag in ['p', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.text += '\n'

      def handle_data(self, data):
         self.text += (str(data).strip())

      def get_text(self):
         return self.text

   parser = PlainTextBuilder()
   parser.feed(html)

   return '\n'.join([line for line in parser.get_text().split('\n')])


def __attach_message(message, email, html=False):
   if html:
      email.attach(MIMEText(message, 'html'))
   else:
      plain_text = __html_to_plaintext(message)
      email.attach(MIMEText(plain_text, 'plain'))


def __build_message(**kwargs):
   msg = MIMEMultipart('alternative')
   msg['Subject'] = kwargs['subject']
   msg['From'] = kwargs['from']

   return msg


def __build_content(body, pre_text, post_text, p_tag):
   footer = """
         <p style="color: black; padding-top: 1%%"><hr width="100%%" color="black" size="1"></p>
         <p style="color: black;">If you have any questions or concerns please feel free to email the %s team at %s.</p>
         <p style="color: black;">Report any bugs or issues via our<a href="%s">Issue Tracker</a></p>
         <p style="color: black;"><hr width="100%%" color="black" size="1"></p>
         <p style="color: black;">Thanks,</p>
         <p style="color: black;">%s Team</p>
      """ % (app_title, reply_to, issue_tracker, app_title)

   BODY = """
         <h3 style="padding-left: 1%%; padding-top: 1%%; padding-bottom: 1%%; color: black;"><i>%s</i></h3>
      """ % body

   content_format = '<p style="padding-left: 1%%; padding-top: 1%%; padding-bottom: 1%%; color: black;"><i>%s</i></p>'
   if p_tag is False:
      content_format = '%s'

   if pre_text is not False:
      BODY = content_format % pre_text + BODY

   if post_text is not False:
      BODY += content_format % post_text

   message = """
         <html>
            <head></head>
            <body style="color: black;">
               <p style="color: black;">You have recieved a notification in %s.</p>
               %s
               %s
            </body>
         </html>
      """ % (app_title, BODY, footer)

   return message


def __set_msg_to(msg, to):
   if 'To' in msg:
      msg.replace_header('To', to)
   else:
      msg['To'] = to


def __get_subject(action, application, title):
   if action:
      return "(Action Required) %s | %s" % (application, title)
   return "%s | %s" % (application, title)


def __get_user_email(manager, uid):
   if uid == "gss-support-readiness":
      user_email = uid + "@redhat.com"
   else:
      user = get_user.call(kerberos=uid)
      if "kerberos" in user:
         user_email = user['kerberos']['mail']
      else:
         user_email = manager.ldap_lookup(uid)['mail']

   return user_email


def __is_prod(manager):
   return manager.settings.get_instance() == 'prod'


def __send_email(sender, to_addrs, msg):
   s = smtplib.SMTP(smtp_server)

   if isinstance(to_addrs, list):
      for addr in to_addrs:
         s.sendmail(sender, addr, msg)

   else:
      s.sendmail(sender, to_addrs, msg)

   s.quit()

def __is_plaintext(uid):
   kwargs = {
      "application": "system",
      "name": "Plain-Text-Email",
      "output": "uid",
      "uid": uid,
   }


   setting = get_user_settings.call(**kwargs)

   if "value" not in setting:
      return False
   return setting["value"]

# send a copy of the email notifications to developers
def __send_dev_notifications(**kwargs):
   is_job = kwargs['job']
   html_msg = kwargs['html_msg']
   email = kwargs['email']
   dev_emails = [admins_email]

   __set_msg_to(html_msg, ', '.join(kwargs['to']))

   emails_sent = [
       [email['from'], dev_emails, html_msg.as_string()]
   ]

   if not kwargs['is_prod']:
      html_msg.replace_header("Subject", "DEVEL ~ " + email['subject'])

      emails_sent = [
          [email['from'], dev_emails, html_msg.as_string()],
      ]

      if not is_job:
         for mail in emails_sent:
            __send_email(mail[0], mail[1], mail[2])
      else:
         send_email.call(emails=emails_sent)


def call(application, title, users, body, action=False, post_text=False, pre_text=False, job=True, p_tag=True):
   try:
      manager = Manager()
      is_prod = __is_prod(manager)

      # arguments:
      # application - the name of the sending application. Example: "Support Exceptions"
      # title - the title that should be borne by the email. Example: "New comment on SE #44"
      # users - set of individual uids that will also get the notification. Example: set([ "mowens@redhat.com", "vanhoof@redhat.com" ])
      # body - what will go into an h3 tag as the main line of the email. Example: "mowens has left a new comment on <a href="tools.apps.cee.redhat.com/se/44">SE #44</a>."
      email_body = __build_content(body, pre_text, post_text, p_tag)

      email = {
          'from': reply_to,
          'subject': __get_subject(action, application, title),
          'body': email_body,
          'plaintext': __html_to_plaintext(email_body),
      }

      html_msg = __build_message(**email)
      plaintext_msg = __build_message(**email)

      html_msg.attach(MIMEText(email['body'], 'html'))
      plaintext_msg.attach(MIMEText(__html_to_plaintext(email['body']), 'plain'))

      emails = []
      to = []

      for uid in users:
         if __is_plaintext(uid):
            msg = plaintext_msg
         else:
            msg = html_msg

         user_email = __get_user_email(manager, uid)
         to.append(user_email)

         if is_prod:
            __set_msg_to(msg, user_email)

            if not job:
               __send_email(email['from'], user_email, msg.as_string())
            else:
               emails.append([email['from'], user_email, msg.as_string()])

      if is_prod and job:
         send_email.call(emails=emails)

      __send_dev_notifications(is_prod=is_prod, html_msg=html_msg, plaintext_msg=plaintext_msg, to=to, email=email, job=job)

   except Exception as e:
      FROM = reply_to

      msg = MIMEMultipart('alternative')
      msg['Subject'] = "%s Failed to Send Email" % app_title
      msg['From'] = reply_to
      msg['To'] = admins_email

      BODY = """
         <h3 style="padding-left: 1%%; padding-top: 1%%; padding-bottom: 1%%; color: black;"><i>%s</i></h3>
      """ % body

      if post_text != False:
         BODY += """
            <p style="padding-left: 1%%; padding-top: 1%%; padding-bottom: 1%%; color: black;"><i>%s</i></p>
         """ % post_text

      message = """
         <html>
            <head></head>
            <body>
               <p>Failed to send email to the following people '%s' with contents below.</p>
               %s
               <hr />
               <p>Below is the stack trace.</p>
               <p><pre>%s</pre></p>
            </body
         </html>
      """ % (', '.join(users), BODY, traceback.format_exc())
      part1 = MIMEText(message, 'html')
      msg.attach(part1)

      if not is_prod:
         msg.replace_header("Subject", "DEVEL ~ " + email['subject'])

      __send_email(FROM, admins_email, msg.as_string())
