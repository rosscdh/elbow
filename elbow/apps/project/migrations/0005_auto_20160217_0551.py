# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-17 05:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0004_auto_20160217_0548'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='interest_length',
            field=models.CharField(blank=True, max_length=24, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='interest_rate',
            field=models.IntegerField(default=6.0),
        ),
    ]