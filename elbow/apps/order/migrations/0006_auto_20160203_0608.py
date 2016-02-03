# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-03 06:08
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0005_auto_20160127_1506'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ('-created_at',), 'verbose_name': 'Order', 'verbose_name_plural': 'Orders'},
        ),
        migrations.RemoveField(
            model_name='order',
            name='token',
        ),
        migrations.AddField(
            model_name='order',
            name='data',
            field=jsonfield.fields.JSONField(default={}),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[(b'pending', 'Pending'), (b'processing', 'Send for Processing'), (b'paid', 'Paid'), (b'paid_manually', 'Manually Paid'), (b'failed', 'Payment Failed'), (b'cancelled', 'Payment Cancelled')], db_index=True, default=b'pending', max_length=64),
        ),
    ]
