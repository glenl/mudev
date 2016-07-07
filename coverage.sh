#!/bin/sh
# Quick script to run tests with coverage analysis
#
coverage run --source=mutopia                               \
         --branch                                           \
         --omit='mutopia/migrations/*','mutopia/tests/*'    \
         manage.py test mutopia.tests                       \
         -v2                                                \
         --settings=mudev.local_settings

# Generate html report (htmlcov/index.html)
coverage html
