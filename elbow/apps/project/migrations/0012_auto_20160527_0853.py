# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-27 08:53
from __future__ import unicode_literals

import django.core.files.storage
from django.db import migrations, models
import elbow.apps.project.models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0011_auto_20160513_0745'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='loan_agreement_doc',
            field=models.FileField(null=True, storage=django.core.files.storage.FileSystemStorage(), upload_to=elbow.apps.project.models._doc_upload_path),
        ),
        migrations.AddField(
            model_name='project',
            name='term_sheet_doc',
            field=models.FileField(null=True, storage=django.core.files.storage.FileSystemStorage(), upload_to=elbow.apps.project.models._doc_upload_path),
        ),
        migrations.AlterField(
            model_name='project',
            name='status',
            field=models.CharField(choices=[(b'pending', b'Pending'), (b'active', b'Available'), (b'complete', b'Complete'), (b'removed', b'Removed')], db_index=True, default=b'pending', max_length=64),
        ),
    ]
