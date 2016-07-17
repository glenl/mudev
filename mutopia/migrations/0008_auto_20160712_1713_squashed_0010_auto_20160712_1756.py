# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-12 20:24
from __future__ import unicode_literals

from django.db import migrations, models


# Functions from the following migrations need manual copying.
# Move them and any dependencies into this file, then update the
# RunPython operations to refer to the local versions:
# mutopia.migrations.0009_data_20160712_1717

def move_collection_pieces(apps, schema_editor):
    # data migration from deprecated CollectionPiece into the new m:m
    # relationship in Collection.
    CollectionPiece = apps.get_model('mutopia', 'CollectionPiece')
    for cp in CollectionPiece.objects.all():
        cp.collection.pieces.add(cp.piece)

class Migration(migrations.Migration):

    replaces = [('mutopia', '0008_auto_20160712_1713'), ('mutopia', '0009_data_20160712_1717'), ('mutopia', '0010_auto_20160712_1756')]

    dependencies = [
        ('mutopia', '0007_piece_collections'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='piece',
            name='collections',
        ),
        migrations.AddField(
            model_name='collection',
            name='pieces',
            field=models.ManyToManyField(to='mutopia.Piece'),
        ),
        migrations.RunPython(move_collection_pieces),
        migrations.RemoveField(
            model_name='collectionpiece',
            name='collection',
        ),
        migrations.RemoveField(
            model_name='collectionpiece',
            name='piece',
        ),
        migrations.DeleteModel(
            name='CollectionPiece',
        ),
    ]