# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-18 10:24
from __future__ import unicode_literals

from django.db import migrations
import geoposition.fields


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0008_auto_20160218_0901'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='lat_long',
            field=geoposition.fields.GeopositionField(default='51.1655111, 6.2737308', max_length=42),
        ),
    ]
