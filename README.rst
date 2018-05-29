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
    $ pipenv install --dev
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

    $ scrapy crawl spider_name
    $ scrapy crawl hubspot_partners -o reports/test.csv

Run Parser
^^^^^^^^^^

::
    
    $ cd agencies_crawler
    $ pipenv run python -m agencies_parser.merge_results