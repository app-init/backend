python setup.py -q install
export APPINIT_DEVEL="true"

gunicorn appinit_backend.app.app:app -c appinit_backend/container/docker/api/gunicorn.py
# webplatform-backend $@
