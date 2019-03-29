cd ../webplatform-cli/
python setup.py install

cd ../webplatform-backend/webplatform_backend
gunicorn app:app --config gunicorn.py
