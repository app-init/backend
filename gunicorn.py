from appinit.lib.config import Settings
import os

settings = Settings()
routes = settings.get_variable('route-configs')

reload = True
# reload_extra_files = [i['api']['path'] for i in routes]
reload_engine = 'inotify'

bind = '0.0.0.0:8000'

workers = 1
worker_class = 'gevent'
# worker_connections = 10000
# timeout = 120

# spew = True

# daemon = False

# umask = 0
# user = None
# group = None
# tmp_upload_dir = None

# preload = True
# capture_output = True

# proc_name = None

controller_path = os.path.dirname(os.path.realpath(__file__))
base_path = os.path.abspath(os.path.join(controller_path))
pythonpath = base_path
check_config = True
