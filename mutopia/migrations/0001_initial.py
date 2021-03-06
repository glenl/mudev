# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-07 19:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AssetMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('folder', models.CharField(max_length=128)),
                ('name', models.CharField(blank=True, max_length=64)),
                ('has_lys', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'muAssetMap',
                'ordering': ['folder'],
            },
        ),
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('tag', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=128)),
            ],
            options={
                'db_table': 'muCollection',
            },
        ),
        migrations.CreateModel(
            name='CollectionPiece',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('collection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mutopia.Collection')),
            ],
            options={
                'db_table': 'muCollectionPiece',
            },
        ),
        migrations.CreateModel(
            name='Composer',
            fields=[
                ('composer', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=48)),
            ],
            options={
                'db_table': 'muComposer',
                'ordering': ['composer'],
            },
        ),
        migrations.CreateModel(
            name='Contributor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('url', models.URLField(blank=True)),
            ],
            options={
                'db_table': 'muContributor',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Instrument',
            fields=[
                ('instrument', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('in_mutopia', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'muInstrument',
                'ordering': ['instrument'],
            },
        ),
        migrations.CreateModel(
            name='License',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('url', models.URLField()),
                ('badge', models.CharField(blank=True, max_length=32)),
                ('active', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'muLicense',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='LPVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.CharField(max_length=24, unique=True)),
                ('major', models.IntegerField(blank=True, null=True)),
                ('minor', models.IntegerField(blank=True, null=True)),
                ('edit', models.CharField(blank=True, max_length=8)),
            ],
            options={
                'db_table': 'muVersion',
            },
        ),
        migrations.CreateModel(
            name='Piece',
            fields=[
                ('piece_id', models.IntegerField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=128)),
                ('raw_instrument', models.TextField(blank=True)),
                ('opus', models.CharField(blank=True, default='', max_length=12)),
                ('lyricist', models.CharField(blank=True, default='', max_length=64)),
                ('date_composed', models.CharField(blank=True, max_length=24)),
                ('date_published', models.DateField()),
                ('source', models.CharField(blank=True, max_length=64)),
                ('moreinfo', models.TextField(blank=True, default='')),
                ('composer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mutopia.Composer')),
                ('instruments', models.ManyToManyField(to='mutopia.Instrument')),
                ('license', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mutopia.License')),
                ('maintainer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mutopia.Contributor')),
            ],
            options={
                'db_table': 'muPiece',
            },
        ),
        migrations.CreateModel(
            name='RawInstrumentMap',
            fields=[
                ('raw_instrument', models.TextField(primary_key=True, serialize=False)),
                ('instrument', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mutopia.Instrument')),
            ],
            options={
                'db_table': 'muRawInstrumentMap',
            },
        ),
        migrations.CreateModel(
            name='Style',
            fields=[
                ('style', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('slug', models.SlugField(max_length=32)),
                ('in_mutopia', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'muStyle',
                'ordering': ['style'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('name', models.CharField(max_length=32, primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'muTag',
            },
        ),
        migrations.CreateModel(
            name='UpdateMarker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField()),
            ],
            options={
                'db_table': 'muUpdateMarker',
            },
        ),
        migrations.AddField(
            model_name='piece',
            name='style',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mutopia.Style'),
        ),
        migrations.AddField(
            model_name='piece',
            name='tags',
            field=models.ManyToManyField(to='mutopia.Tag'),
        ),
        migrations.AddField(
            model_name='piece',
            name='version',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mutopia.LPVersion'),
        ),
        migrations.AddField(
            model_name='collectionpiece',
            name='piece',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mutopia.Piece'),
        ),
        migrations.AddField(
            model_name='assetmap',
            name='piece',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mutopia.Piece'),
        ),
    ]
