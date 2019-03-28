from setuptools import setup, find_packages

setup(name = "webplatform-backend",
   version = "1.0.1",
   description = "Backend Flask instance used for a webplatform",
   author = "Matthew Owens",
   author_email = "mowens@redhat.com",
   url = "https://github.com/lost-osiris/webplatform-backend",
   packages = find_packages(),
   include_package_data = True,
   install_requires = [
      'docker',
      'pymongo',
      'Flask',
      'ldap3',
      'markdown2',
      'pytz',
      'gunicorn',
      'querystring-parser',
      'xmlsec',
      'python3_saml'
   ],
   dependency_links = [
      'http://github.com/lost-osiris/python3-saml/tarball/master#egg=python3_saml',
   ],
   python_requires='>=3',
   license='MIT',
   # scripts = ["webplatform_backend/webplatform-cli"],
   long_description = """TODO""",
   classifiers = [
       "Programming Language :: Python :: 3",
       "License :: OSI Approved :: MIT License",
       "Operating System :: OS Independent",
   ],
)
