from lib.imports.default import *
import re

def call(*args, **kwargs):
   manager = Manager()
   db = manager.db("findsbr")

   sbrs = db.sbrs.find()

   for sbr in sbrs:
      if ('/' in sbr['link']):
         new_link = (re.sub('/', '-', sbr['link']))
         db.sbrs.update({"_id": ObjectId(sbr["_id"])}, {
            "$set": { "link": new_link }
         })

   packages = db.packages.find()
   for package in packages:
      if "/" in package['primary']:
         print (package)
         new_primary = (re.sub('/', '-', package['primary']))
         db.packages.update({"_id": ObjectId(package["_id"])}, {
            "$set": { "primary": new_primary }
         })
      # if package['secondary'] != False and "/" in package['secondary']:
      #    new_secondary = (re.sub('/', '-', package['secondary']))
      #    db.sbrs.update({"_id": ObjectId(package["_id"])}, {
      #       "$set": { "secondary": new_secondary }
      #    })