import os
import sys
from setuptools import setup

exec(open('haproxytop/version.py').read())

setup(name='haproxy-top',
      version=version,
      packages=['haproxytop'],
      description='Commandline utility for monitoring HAProxy',
      author='Bradley Cicenas',
      author_email='bradley.cicenas@gmail.com',
      url='https://github.com/bcicen/haproxy-top',
      install_requires=['haproxy-stats>=1.3'],
      license='http://opensource.org/licenses/MIT',
      classifiers=(
          'License :: OSI Approved :: MIT License ',
          'Natural Language :: English',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
      ),
      keywords='haproxy stats cli commandline top monitoring devops',
      entry_points={'console_scripts': ['haproxy-top = haproxytop:main']}
)
