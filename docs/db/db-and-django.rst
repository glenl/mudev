
.. include:: ../subs.txt

This is a brief description of how to access the database
programatically and presumes that you have created a project database
based on :doc:`../getting-started` chapter.

Accessing data with python and Django
-------------------------------------

There are a number of ways to experiment with the |django| API. The
first is simply opening up a python shell using the :file:`manage.py`
shell command provided by |django|, ::

  $ cd ~/work/mu-django/mudev
  $ workon mudev
  (mudev) $ python manage.py shell --settings=mudev.local_settings
  Python 3.4.3+ (default, Oct 14 2015, 16:03:50)
  [GCC 5.2.1 20151010] on linux
  Type "help", "copyright", "credits" or "license" for more information.
  (InteractiveConsole)
  >>>
  >>> from mutopia.models import LPVersion
  >>> LPVersion.objects.all()[:2]
  [<LPVersion: 2.8.1>, <LPVersion: 2.16.1>]
  >>>

.. note::

   Throughout these examples, you will need to use the virtual
   environment that you built for this project.

This is great for checking things out but that can get a little clumsy
when writing larger applications. What would be ideal is if you could
write in an editor and run the program from the command line. The
problem to overcome is that you will have to somehow get the |django|
frameworks loaded so it works as expected. There is more than one way
to do that but the simplest I've found is to create a management
command.

A management command lives under your application area in a predefined
location and then is run from :file:`manage.py`. Your code will create a
class derived from ``BaseCommand`` and implement a method called
``handle``. Here is a ``hello world`` stub, ::

  from django.core.management.base import BaseCommand

  class Command(BaseCommand):
       def handle(self, *args, **options):
           self.stdout.write('Hello world!')

This pseudo-command, even though it has nothing to do with your
application at this point, would have to live in your application area
under the folder :file:`management/commands`. For us that full name is, ::

  mudev/mutopia/management/commands/hello.py

To run ``hello.py`` you would run it like you would run other
``manage.py`` applications, ::

  (mudev) $ python manage.py hello --settings=mudev.local_settings
  Hello world!


Version counts
~~~~~~~~~~~~~~

As a first example I chose to duplicate the tutorial of how to do this
in SQL. Not surprisingly, one is probably no more complicated than the
other depending on your familiarity with python or SQL. When I look at
the final SQL it is not that complicated. Instead of explaining this
python example in tiny steps, the final code is presented and we'll
walk through how it works. I've included the complete working program.

.. literalinclude:: versions.py
   :linenos:

There are a number of interesting points to make about this short bit
of code. The query mechanism in |django| is "lazy" so the ``QuerySet``
object is created but not executed in line 9. The
``versions.annotate`` method (line 10) adds a column to the
``QuerySet`` named "count" whose value is the number of pieces
associated with each version object in the set. The database query is
not executed until line 12 where, finally, the ``QuerySet`` is ordered
in reverse based on the new column.

   2.10.33 : 308
    2.16.1 : 294
    2.18.2 : 206
    2.12.2 : 104
   2.11.34 : 98
    2.18.0 : 82

If you were to insert a line after the assignment of ``vc`` before
line 12 to view the SQL (``self.stdout.write(vc.query)``) you would
see that the SQL is very similar to that developed in the other
tutorial.
