from setuptools import setup

import os 
#from capturica_db import __version__
from setuptools import setup
reqs_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')

link = 'git+git://github.com/kz159/WalldDataBase.git'

setup(name='walld_db',
      version='0.1',
      description='represents walld db tables',
      url=link,
      author='kz159',
      author_email='loh@kz159.ru',
      license='GNU',
      packages=['walld_db'],
      install_requires=[s.strip() for s in open(reqs_file).readlines()])
