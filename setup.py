#!/usr/bin/env python

try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(name='pyress',
      packages=['iress'],
      version='0.1.0',
      description='Pythonic wrapper around the IRESS COM Interface.',
      author='James Brotchie',
      author_email='brotchie@gmail.com',
      url='http://code.google.com/p/pyress/',
      long_description= \
          'IRESS is a market data system developed by IRESS Market Technology Ltd.\n'
          'Their desktop IRESS solution provides real-time and historical data for\n'
          'wide range of equities and derivatives.\n\n'
          'The IRESS application exposes a COM Automation Object Model that allows\n'
          'direct access to the data streams that drive the user interface. pyress\n'
          'wraps sections of the IRESS COM Automation Object Model in a pythonic interface.',
      platforms=['win32'],
      license='Apache 2.0',
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: Microsoft :: Windows',
        'Topic :: Office/Business :: Financial',
        'Environment :: Win32 (MS Windows)',
      ],
)
