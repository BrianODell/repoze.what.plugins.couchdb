from setuptools import setup, find_packages

version = '0.1'

setup(name='repoze.what.plugins.couchdb',
      version=version,
      description="repoze.what plugin for couchdb",
      long_description=open('README.txt').read(),
      classifiers=[
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='wsgi auth repoze what couchdb',
      author="Brian O'Dell",
      author_email='briantodell@gmail.com',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['repoze', 'repoze.what', 'repoze.what.plugins'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'couchdb',
          'repoze.what',
          'simplejson',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
