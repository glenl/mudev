#!/bin/sh
# Quick script to run tests with coverage analysis
#
coverage run --source=mutopia                   \
         manage.py test mutopia.tests           \
         -v2                                    \
         --settings=mudev.local_settings

coverage report --show-missing
