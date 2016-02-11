# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-10 08:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0007_auto_20160205_0715'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[(b'created', 'Order Created (1/4)'), (b'large_sum_agreement', 'Large sum agreement (2/4)'), (b'more_info', 'More Info (3/4)'), (b'processing', 'Send for Payment  (4/4)'), (b'paid', 'Paid'), (b'paid_manually', 'Manually Paid'), (b'failed', 'Payment Failed'), (b'cancelled', 'Payment Cancelled')], db_index=True, default=b'created', max_length=64),
        ),
    ]