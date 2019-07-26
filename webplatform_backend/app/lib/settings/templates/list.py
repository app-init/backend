from lib.imports.default import *
import lib.settings.templates.parse_cursor as parse_cursor

def call(**kwargs):
   manager = Manager()
   db = manager.db('settings')

   cursor = db.templates.find()

   output = [template for template in cursor]
   return [parse_cursor.call(template) for template in output]
