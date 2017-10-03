from setuptools import setup

setup(name='guldumnet',
      version='1.0',
      description='Guldum.net',
      author='hakanu',
      author_email='hakan@guldum.net',
      url='http://www.python.org/sigs/distutils-sig/',
#      install_requires=['Django>=1.3'],
      install_requires=['web.py', 'requests', 'loggly-python-handler', 'futures'],
     )
