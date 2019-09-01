python setup.py -q install
export APPINIT_DEVEL="true"

gunicorn appinit_backend.app.app:app -c gunicorn.py
# webplatform-backend $@
