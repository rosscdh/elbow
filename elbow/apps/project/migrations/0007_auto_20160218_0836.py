# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-18 08:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0006_auto_20160218_0829'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='location',
            new_name='lat_long',
        ),
        migrations.AddField(
            model_name='project',
            name='building_location',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
