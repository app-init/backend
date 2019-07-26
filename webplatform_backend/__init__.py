
import os, sys

controller_path = os.path.dirname(os.path.realpath(__file__))
base_path = os.path.abspath(os.path.join(controller_path))

if base_path not in sys.path:
   sys.path.append(base_path)

if controller_path not in sys.path:
   sys.path.append(controller_path)

# import views.responses as responses