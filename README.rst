============
Flask Disqus
============

This is small and simple integration of `disqus`_ into `flask`_.

.. _flask: http://flask.pocoo.org
.. _disqus: http://disqus.com

Installation
------------
- Go to directory with app in console and type *python setup.py install*
- Press "Enter"

Usage
-----
.. code-block:: python
    from flask_disqus import Disqus
    disq = Disqus(app)


in html template:

.. code-block:: html
    {% autoescape false %}
    {{ disqus_dev() }}
    {{ disqus_show_comments("comments_name") }}
    {% endautoescape %}
