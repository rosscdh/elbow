# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-06-09 08:03
from __future__ import unicode_literals

import django.core.files.storage
from django.db import migrations, models
import elbow.apps.document.models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0007_orderdocument_projectdocument'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='document',
            field=models.FileField(blank=True, max_length=255, null=True, storage=django.core.files.storage.FileSystemStorage(), upload_to=elbow.apps.document.models._document_upload_path),
        ),
        migrations.AlterField(
            model_name='document',
            name='document_type',
            field=models.CharField(choices=[('project', 'Project Document'), ('order', 'Order Document'), ('generic_loan_agreement', 'Generic Loan Agreement'), ('loan_agreement', 'Loan Agreement'), ('term_sheet', 'Term Sheet')], db_index=True, default='project', max_length=64),
        ),
    ]
