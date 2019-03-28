# python setup.py sdist bdist_wheel
python setup.py sdist
python3 -m twine upload dist/*
