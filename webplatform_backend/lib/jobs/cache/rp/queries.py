from lib.imports.default import *
from lib.rp.subteams.get import call as get_subteam
from lib.rp.bugzilla.build_query import call as build_query

def call(**kwargs):
   manager = Manager()
   db = manager.db("release-planning")

   subteam_ids = db.subteams.find({}, {"_id": 1})

   subteams = []
   for doc in subteam_ids:
      subteams.append(get_subteam(id=doc['_id']))

   output = []
   count = 0
   for team in subteams:
      for release_data in team['releases']:
         if release_data['id'] in ["Testing", "Development", "Planning"]:
            for release in release_data['releases']:
               count += 1
               print(release, team['name'], count)
               output.append(build_query(update=True, subteam=team['id'], release=release))

   # return subteams
   return output
