# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-25 14:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0012_order_tax_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='dob',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='title',
            field=models.CharField(blank=True, max_length=24, null=True),
        ),
    ]
