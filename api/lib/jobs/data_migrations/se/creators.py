from lib.imports.default import *
import lib.users.picture as get_picture

permissions = "developer"

def call(**kwargs):
   from io import StringIO
   manager = Manager()
   db = manager.db("support-exceptions")
   allSEs = db.se.find({ "creator": { "$exists": True } })
   output = StringIO()
   print("Could not use LDAP to update the following SE's:", file=output)

   for se in allSEs:
      try:
         ldap_user = manager.ldap_lookup(se["creator"]["uid"])
         picture = get_picture.call(email=ldap_user['mail'][0])
         creator = {
            "uid": se["creator"]["uid"],
            "firstname": ldap_user["displayName"][0],
            "lastname": ldap_user["sn"][0],
            "email": ldap_user["mail"][0],
            "picture": picture,
         }

         db.se.update(
            { "_id": se["_id"] },
            { "$set": {
                  "creator": creator
               }
            }
         )
      except Exception:
         # in case something goes wrong in the ldap lookup and update
         print("\t SE #" + str(se["se_id"]), file=output)


   print("Could not use LDAP to update the following comments:", file=output)
   allComments = db.comments.find({ "creator": { "$exists": True } })
   for comment in allComments:
      try:
         ldap_user = manager.ldap_lookup(comment["creator"]["uid"])
         picture = get_picture.call(email=ldap_user['mail'][0])
         creator = {
            "uid": comment["creator"]["uid"],
            "firstname": ldap_user["displayName"][0],
            "lastname": ldap_user["sn"][0],
            "email": ldap_user["mail"][0],
            "picture": picture,
         }

         db.comments.update(
            { "_id": comment["_id"] },
            { "$set": {
                  "creator": creator
               }
            }
         )
      except Exception:
         print("\t Comment::" + str(comment["_id"]), file=output)

   out = output.getvalue()
   output.close()
   return out