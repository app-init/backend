from gevent import monkey
monkey.patch_all()

from appinit.lib.config import Settings
import os

settings = Settings()
routes = settings.get_variable('route-configs')

reload = True
reload_extra_files = [i['api']['path'] for i in routes]

bind = '0.0.0.0:8002'

worker_class = 'gevent'
capture_output = True

controller_path = os.path.dirname(os.path.realpath(__file__))
base_path = os.path.abspath(os.path.join(controller_path))
pythonpath = base_path
