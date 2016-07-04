Getting Started
===============
For developers, this documents the tools required for contributions
and outlines the installation on the platform I use (Ubuntu 15.10).
The project should travel well to other environments.

The project uses `heroku <https://www.heroku.com/home>`_ to demo the
site. More on that later.


Requirements
------------

The following tools are necessary to get started:

 - **python3**
 - **virtualenv** and **virtualenvwrapper**
 - **PostgreSQL**, this was developed using version 9.4

The project uses its virtual environment to *freeze* requirements into
a file that can be used by **pip**, the python installer, to install
the remainder of the tools. You can skip to :ref:`installing` or stay here
and read a little more about what will be installed.

 - **dj-database-url** - used by Heroku.
 - **gunicorn** - wsgi server, used by Heroku.
 - **whitenoise** - simplified static file serving, for Heroku.
 - **Django** - web frameworks.
 - **isodate** - used for date formatting.
 - **psycopg2** - required for PostgreSQL database backend in Django.
 - **pyparsing** -
 - **rdflib** - for reading RDF files.
 - **requests** - simplified internet requests.

.. _installing:

Installing the Basic Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Start by setting up for virtual environments. ::

  $ sudo apt-get virtualenv,virtualenvwrapper

Virtual environments will allow us to match environments among
developers. To create one for this project that will use ``python3`` exclusively, ::

  $ mkvirtualenv -p /usr/bin/python3 mudevo

Once in this environment we can install the other required tools.
Moving among environments is done with the ``workon`` tool, ::

  $ workon mudevo
  (mudevo) $ python --version
  Python 3.4.3+

The requirements have been separated into two files,

 - **requirements.txt** - the kitchen sink, includes ``sphinx`` which
   installs more than you need if you are not doing documentation.

 - **req-noshpinx.txt** - just the essentials

These are simple text files that specify the version of each tool.
Look through these and select one, then have pip go to work, ::

  (mudevo) $ pip install -r requirements.txt

You may have as many environments as you like but take care to use
(``workon``) the correct environment when you develop code in this project.


Configuring PostgreSQL
----------------------

Here is a summary of the steps, if you get lost you can go to these
`ubuntu_pages <https://help.ubuntu.com/community/PostgreSQL/>`_. ::

$ sudo apt-get install postgresql postgresql-contrib

During installation, the system should have created a postgres user
that you will need for defining system-wide postgres configuration. It
has a password and just so the usage can be shown, here is how you
would change the password, ::

  $ sudo -u postgres psql postgres
  postgres=# \password
  postgres=# \q

To break that down,

* `sudo -u postgres` - run a command as user postgres
* `psql postgres` - run the ``postgres`` command-line using the
  postgres database (which is where the configuration tables live.)
* `\\password` is a command to the interpreter to change your password.
  It will prompt for the new password. 
* `\\q` quits the interpreter

Full Text Search
----------------

FTS is available by default in postgres but the
normalization of accented characters is an extension that, while built
in, needs to be enabled in order to work. The extension is called
*unaccent* and it is enabled as follows, ::

  $ sudo -u postgres psql postgres
  postgres=# create extension unaccent;
  postgres=# \q

Note that when you make changes to the **postgres** database, as
above, you are actually modifying the default database configuration
for all users. You want to do this in the event you write tests that
use this extension.

The Database for Django
~~~~~~~~~~~~~~~~~~~~~~~

The default database for a Django project
is SQLite, which is convenient since it requires no extra
configuration. In that mode, Django will do all the work of creating
the database and its tables without much grief from the user. To have
FTS we need to switch the database back-end to `postgres` and that
means extra configuration is required. Here are the steps, ::

  $ sudo -u postgres createdb mutopiadb
  $ sudo -u postgres psql
  CREATE ROLE muuser WITH LOGIN PASSWORD 'mumusic';
  GRANT ALL PRIVILEGES ON DATABASE mutopiadb TO muuser;
  ALTER USER muuser CREATEDB;

The ``createdb`` used in the first line is a utility provided by the
``postgresql`` installation. The next few steps use the ``psql`` utility
to create a user (*muuser*) with a password. These can be changed but
must match those found in the Django settings file. We give our user
all privileges on the database and, lastly, we let our user create
databases so the application tests can create and delete a temporary
database.
