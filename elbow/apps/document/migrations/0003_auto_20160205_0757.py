# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-05 07:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0002_document_document_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='document_type',
            field=models.CharField(choices=[('project', 'Project Document'), ('order', 'Order Document')], db_index=True, default='project', max_length=64),
        ),
    ]