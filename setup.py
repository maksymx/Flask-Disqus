# coding: utf8

from setuptools import setup

setup(
    name='Flask-Disqus',
    version='0.0.1',
    license='BSD',
    description='Small extension for Flask to make possible using Disqus comments',
    long_description=open('README.rst').read(),
    author='',
    author_email='',
    url='',
        platforms='any',

        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 3',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
            'Topic :: Software Development :: Libraries :: Python Modules'
        ],

    install_requires=['Flask'],

    packages=['flask_disqus'],
)
