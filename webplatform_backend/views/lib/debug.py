from application.views.lib import jsonify 
import simplejson

def log(data):
  print(simplejson.dumps(jsonify.convert(data), indent=2))
