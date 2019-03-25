def call(cursor):
   output = {}
   for key, value in list(cursor.items()):
      if key == "_id":
         output["id"] = value
      elif key == "permissions":
         output[key] = ",".join(value)
      else:
         output[key] = value

   return output

def get_name(title):
    words = [word for word in title.split(' ') if word != '']
    return '-'.join(words)
