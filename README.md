# mudev

## Synopsis

This repository is for development of a Python-based clone of the
MutopiaProject web-site using Python. It looks similar because the
templating engine uses the same CSS files and Bootstrap as the existing
site. Underneath the covers, however, it is entirely different.

   * Dynamic page creation for easier maintenance.

   * The entire MutopiaProject catalogue is kept within a PostgreSQL
     database for easy maintenance and analysis.

   * Supports full-text-search.

## Orientation

Building a site with [Django](https://www.djangoproject.com/) is a
matter of defining an object relationship model (``ORM``) and
developing the web-site using view code and html templates.

In Django-speak,

  * The ``Project`` is mudev

  * The ``App`` is mutopia

You will find top-level project code under ``mudev`` but the meat of
this project is under ``mutopia``. If you are not familiar with
Django, I recommend starting at ``mutopia/models.py`` while keeping
the [Django documentation](https://docs.djangoproject.com/) handy.

The project documentation is done in Sphinx under the ``docs`` folder.

## Development setup

This project uses typical Python (python 3!) tools. Once you clone the
repository you will need to create the appropriate virtual
environment. A ``requirements.txt`` file is provided for the full
environment, if you are not going to be doing document builds you can
save some setup time by using ``req-nosphinx.txt``.

```bash
$ mkvirtualenv -p python3 -r ./requirements.txt
```
