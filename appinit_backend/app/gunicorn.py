import os

bind = '0.0.0.0:8000'
backlog = 2048

workers = 1
worker_class = 'gevent'
worker_connections = 10000
timeout = 120

spew = False

daemon = False

umask = 0
user = None
group = None
tmp_upload_dir = None

reload = True
preload = True
capture_output = True

proc_name = None

controller_path = os.path.dirname(os.path.realpath(__file__))
base_path = os.path.abspath(os.path.join(controller_path))
pythonpath = base_path
