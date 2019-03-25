from socketIO_client import SocketIO
import pytz

def call(**event):
   with SocketIO('http://cee-tools-devel-nodejs', 3000, verify=False) as socketIO:
      if event['event'] == "task":
         start = datetime.now(pytz.timezone("America/New_York")).isoformat('T')
         end = datetime.now(pytz.timezone("America/New_York")).isoformat('T')
         time = {
            "start": start,
            "end": end,
         }
         event['time'] = time

      event['_id'] = str(ObjectId())

      output = {}
      for i in event['cc']:
         tmp = {}
         tmp['is_read'] = False

         output[i] = tmp

      event['cc'] = output

      output = {}
      for i in event['to']:
         tmp = {}
         tmp['is_read'] = False

         output[i] = tmp

      event['to'] = output
      print(event)

      socketIO.emit(event['event'], event)

      #socketIO.wait(seconds=1)
