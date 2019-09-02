from gevent import monkey
monkey.patch_all()

from appinit.lib.config import Settings
import os

base_path = os.path.dirname(os.path.realpath(__file__))

settings = Settings()
routes = settings.get_variable('route-configs')
files = [i['api']['path'] for i in routes]
files.append(os.path.abspath(os.path.join(base_path, "appinit_backend/")))

reload = True
reload_extra_files = files

bind = '0.0.0.0:8002'

worker_class = 'gevent'
capture_output = True

pythonpath = base_path
