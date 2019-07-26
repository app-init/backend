from setuptools import setup, find_packages

setup(name = "webplatform-backend",
   version = "1.0.2",
   description = "Backend Flask instance used for a webplatform",
   author = "Matthew Owens",
   author_email = "mowens@redhat.com",
   url = "https://github.com/lost-osiris/webplatform-backend",
   packages = find_packages(),
   include_package_data = True,
   install_requires = [
      "webplatform-cli",
      "webplatform-auth",
   ],
   python_requires='>=3',
   license='MIT',
   long_description = """TODO""",
   classifiers = [
       "Programming Language :: Python :: 3",
       "License :: OSI Approved :: MIT License",
       "Operating System :: OS Independent",
   ],
   scripts = [
      "webplatform_backend/webplatform-backend"
   ]
)
