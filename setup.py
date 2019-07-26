from setuptools import setup, find_packages

setup(name = "webplatform-backend",
   version = "1.0.5",
   description = "Backend Flask instance used for a webplatform",
   author = "Matthew Owens",
   author_email = "mowens@redhat.com",
   url = "https://github.com/lost-osiris/webplatform-backend",
   packages = find_packages(),
   include_package_data = True,
   install_requires = [
      'webplatform-cli',
      "webplatform-auth",
      'Flask',
      'markdown2',
      'gunicorn',
      'querystring-parser',
      'gevent',
   ],
   python_requires='>=3',
   license='MIT',
   long_description = """TODO""",
   classifiers = [
       "Programming Language :: Python :: 3",
       "License :: OSI Approved :: MIT License",
       "Operating System :: OS Independent",
   ],
   # entry_points={
   #     "console_scripts": ["webplatform-=webplatform_cli.cli:main"]
   # },
   scripts = [
      "webplatform_backend/webplatform-backend"
   ]
)
