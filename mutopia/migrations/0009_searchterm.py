# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-17 21:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mutopia', '0008_auto_20160712_1713_squashed_0010_auto_20160712_1756'),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchTerm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.TextField()),
            ],
            options={
                'managed': False,
                'db_table': 'mu_search_view',
            },
        ),
    ]
