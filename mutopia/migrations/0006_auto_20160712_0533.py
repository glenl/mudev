# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-12 05:33
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mutopia', '0005_auto_20160509_0018'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='piece',
            name='tags',
        ),
        migrations.DeleteModel(
            name='Tag',
        ),
    ]