Database How-to
===============

.. include:: subs.txt

This section covers basic database details like :ref:`db-populating`,
:ref:`db-updating`, and a short introduction to :ref:`db-queries`.

Required reading:

 - :ref:`pg-configure-label`
 - :ref:`pg-django-label`
 - :ref:`pg-notes-label`

.. _db-introduction:

Introduction
------------

The |mutopia| website is a read-only interface to an archive of
musical pieces and the database design recognizes this separation of
functionality,

 - Submitting a piece to the archive.
 - Adding the submitted piece to the database.

Prior to using |django| the second part of this process included a
rebuild of static web pages that were then pushed to the server. There
were several goals for this work on the presentation side of things,

 - Keep the current archive structure intact.
 - Maintain a database that reflects the contents of the archive.
 - Make the update process as automatic as possible.
 - Use dynamic page creation so that all we have to do is update
   the database to see new submissions.

Implicit in these goals is support for rebuilding the database from
scratch given an existing hierarchy. That's a great goal but |django|
supports dumping databases so why not provide support for populating
via a backup?

.. _db-populating:

Populating the database
-----------------------
|django| uses `JSON <https://en.wikipedia.org/wiki/JSON>`_ for its
database output format. Without going into why this is a good idea,
let's take a look at the methods for backing up and restoring. These
two commands will output the Composer model and then load it back in, ::

  (mudevo) $ python manage.py dumpdata --output=comp.json mutopia.Composer
  (mudevo) $ python manage.py loaddata comp.json

The JSON output is often called a fixture and there is support within
|django| to load data in this format. You can dump the entire database
but I've chosen to dump individual tables so I can load just one table
if I want. Here is that script,

.. literalinclude:: ../make-fixtures.sh

As you might guess the ``load-fixtures.sh`` script looks similar but
uses the ``loaddata`` command for each fixture. All models are saved,
including ``UpdateMarker`` which is used to timestamp our last update.
This is explained in the next section. For this section, it is
sufficient to know that you can load an entire working database using
this command, ::

  (mudevo) $ @load-fixtures.sh

If you load fixtures individually, be aware that it is important to
load them in the correct order. Some models use references to other
models that must exist before making the reference. In an empty
database, it will not work to load ``Piece.json`` unless you have
already loaded several other models (``composer.json``,
``License.json``, etc.).

.. _db-updating:

Updating the database
---------------------
There are several models that are integral to the update process,

 - ``AssetMap`` - A mapping of physical location to the piece.
 - ``UpdateMarker`` - A timestamp recording.

``AssetMap`` is also used in the presentation domain to locate the
physical publication in the archive (its *assets*) as well as playing a role
in updating. Here is the outline of how an update works,

 - Read the timestamp in an ``UpdateMarker``
 - Use the github-api, query a one-line log from the github repository
   of changes since this timestamp
 - Parse each line to find new and changed assets.
 - For each changed asset, update its corresponding row in the
   ``AssetMap`` and zero out its ``Piece`` reference.
 - Update the ``UpdateMarker`` with the current timestamp.
 - For each ``AssetMap`` rows with a null ``Piece`` reference,

   * Use the asset map to create the RDF file name
   * Parse the RDF file to create or update the corresponding ``Piece``
   * Save the new piece

Breaking up this process into two sections has advantages,

 - If you want a *do-over* you can modify the ``muUpdateMarker``
   table, the SQL table in the database that corresponds to the model, and
   delete the last timestamp.
 - The fixtures in github will always give you an advantage since you
   can load fixtures followed by an update.
 - A piece can be forced to update by nulling out the ``AssetMap``
   pointer by hand. It would not be difficult to do this in a
   management command.
 - You can always perform an update. If there are no new or update
   pieces, it will simply do nothing but record the timestamp.

This update process is embodied in an application management command
called ``dbupdate``.

Updating FTS
~~~~~~~~~~~~
Because free text search is implemented as a *materialized view* it
can be recreated or refreshed at any time but does not have its own
fixture. An additional management command, ``postgres_fts`` is
provided to create the view from scratch or refresh it. ::

  (mudevo) $ python manage.py postgres_fts
  (mudevo) $ python manage.py postgres_fts --refresh
