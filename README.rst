Installation
============

Agencies project

Requirements
------------

General
^^^^^^^

Blog Analysis its built with **Python 3.6.5**.

To Install Requirements run:

::
    
    $ pip install pipenv (globally)
    $ pipenv install
    $ pipenv shell (to activate env)


Database
--------------

Its required to setup a MongoDB database to store screappers data with a document 
called **agencies** and a collection called **agency**.


Basic Commands
--------------

Run Scrappers
^^^^^^^^^^^^^

::

    $ ​pipenv run scrapy crawl spider_name
