from setuptools import setup, find_packages

setup(name = "app-init-backend",
   version = "1.0.0",
   description = "Backend Flask instance used for a webplatform",
   author = "Matthew Owens",
   author_email = "mowens@redhat.com",
   url = "https://github.com/app-init/backend",
   packages = find_packages(),
   include_package_data = True,
   install_requires = [
      'app-init-cli',
      "app-init-auth",
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
   zip_safe = False
)
