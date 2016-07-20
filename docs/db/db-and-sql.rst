
.. include:: ../subs.txt

This is a brief description of how to access the database using SQL
and presumes that you have created a project database based on
:doc:`../getting-started` chapter.

Accessing data with SQL
-----------------------

I will present these as a series of short tutorials that I can add as
I discover them. For those who are familiar enough with databases and
using SQL, the first section might be of interest to understand how to
find the database details within the |django| projecct definitions.

The setup
~~~~~~~~~

The database for a |django| project is defined in its settings file.
This particular project uses a ``local_settings.py`` file to make it
easier to achieve continuous integration using a |heroku| server. For
the purpose of this tutorial I'll assume you have created and
populated a database with the following criteria,

+----------+-----------+
| database | mutopiadb |
+----------+-----------+
| host     | localhost |
+----------+-----------+
| port     | 5432      |
+----------+-----------+
| user     | muuser    |
+----------+-----------+
| password | mumusic   |
+----------+-----------+

The |psql| command to access the database would be ::

  $ psql -h localhost -p 5432 mutopiadb -U muuser

This will prompt you for the password. The solution to using
this command without having prompt for a password will depend on the
tool but it might be similar to what I use on linux ::

  $ cat >~/.pgpass
  localhost:5432:mutopiadb:muuser:mumusic
  ^D

I also define an alias named ``mudb`` in ``~/.bashrc``, ::

  alias mudb='psql -h localhost -p 5432 mutopiadb -U muuser'

If all is going well using the ``mudb`` command will give you this, ::

  $ mudb
  (mudev) glenl@lola:~/work/mu-django/mudev$ mudb
  psql (9.4.8)
  SSL connection (protocol: TLSv1.2, cipher: ECDHE-RSA-AES256-GCM-SHA384, bits: 256, compression: off)
  Type "help" for help.

  mutopiadb=>


.. _navigating-postgres:

Navigating a Postgres database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before getting to the meat of the tutorials, here are a few commands
to help you get around within |psql|. There are a number of meta
commands that are useful for finding things like table and column
names. The |psql| command can also execute SQL directly or read it in
from a file.

To get a listing of the tables in the datbase you would use the
``\dt`` command, ::

  mutopiadb=> \dt
                 List of relations
   Schema |            Name            | Type  | Owner
  --------+----------------------------+-------+--------
   public | auth_group                 | table | muuser
   public | auth_group_permissions     | table | muuser
   public | auth_permission            | table | muuser
   public | auth_user                  | table | muuser
   .
   .

You can display all columns of a table with ``\d`` once you know its
name, ::

  mutopiadb=> \d "muAssetMap"
                                     Table "public.muAssetMap"
    Column  |          Type          |                         Modifiers
  ----------+------------------------+-----------------------------------------------------------
   id       | integer                | not null default nextval('"muAssetMap_id_seq"'::regclass)
   folder   | character varying(128) | not null
   name     | character varying(64)  | not null
   has_lys  | boolean                | not null
   piece_id | integer                |

Once you know the column names you can access the data, ::

  mutopiadb=> select id, folder, name from "muAssetMap" limit 5;
   id |           folder           |       name
  ----+----------------------------+------------------
    1 | AbtF/swallows              | swallows
    2 | AdamA/giselle              | giselle
    3 | AdamA/minuit_chretiens     | minuit_chretiens
    4 | AdamsS/bluemtns            | bluemtns
    5 | AguadoD/O11/aguado-op11n01 | aguado-op

You can get help on these meta commands with ``\?``.

.. _counting-versions:

Counting versions
~~~~~~~~~~~~~~~~~

If we are going to try to maintain our catalog with high quality
pieces, it helps to build the PDF's with the latest version of
|lilypond|. To be effective, the pieces we should target for update
should be the oldest. The goal of this exercise is to create a
chart of all our LilyPond versions with the count of pieces that use
that version. There are several ways to go about this.

We can see from our ERD that a ``Piece`` has a 1:1 relationship with
an ``LPVersion``. In SQL tables, these relationships are realized by
using an row-id that glues the two together. For example, we could
get a list of the relationship integer value, ::

  mutopiadb=> select version_id from "muPiece" limit 5;
   version_id
  ------------
            7
           58
            2
           12
            2

These are the row-id's of the primary keys for the ``muVersion``
table. We can get the version names into the display with a join,

.. literalinclude:: sql-version-01.sql
   :language: sql

Running this gives, ::

  mutopiadb=> \i docs/db/sql-version-01.sql
   version
  ---------
   2.8.1
   2.8.1
   2.8.1
   2.8.1
   2.8.1

We limit the output to 5 so this document is not too long, but the
problem is apparent. We need to group these together so we can have
SQL count them. Using this SQL,

.. literalinclude:: sql-version-02.sql
   :language: sql


This gives us pretty good output, ::

   version | count
  ---------+-------
   2.1.0   |     1
   2.10.0  |     1
   2.10.13 |     1
   2.10.14 |     4
   2.10.16 |    29

Sorting is done by the ``order`` directive and we want this to be
descending so that the largest counts go on top. This is what we want
so I'll give it a little longer output,

.. literalinclude:: sql-version-03.sql
   :language: sql

And, finally, our top 12, ::

   version | count
  ---------+-------
   2.10.33 |   308
   2.16.1  |   294
   2.18.2  |   206
   2.12.2  |   104
   2.11.34 |    98
   2.18.0  |    82
   2.12.3  |    72
   2.8.7   |    66
   2.11.49 |    66
   2.14.2  |    55
   2.6.4.3 |    41
   2.6.3   |    36

The entire list is of use because there are many with a count of one
piece for a version so it may be possible to reduce the overall number
of versions by updating single pieces. This is easier said than done
in many cases.
