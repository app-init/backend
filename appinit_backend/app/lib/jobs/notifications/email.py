from appinit_backend.lib.imports import *
import smtplib

def call(**kwargs):
   emails = kwargs['emails']
   s = smtplib.SMTP('smtp.corp.redhat.com')

   for e in emails:
      s.sendmail(*e)

   s.quit()

   return True
