# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-01 07:06
from __future__ import unicode_literals

from django.db import migrations

def create_existing_user_profiles(apps, schema_editor):
    UserProfile = apps.get_model("public", "UserProfile")
    for u in UserProfile.objects.all():
        try:
            u.userprofile
        except:
            profile, is_new = UserProfile.objects.get_or_create(user=u)


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_existing_user_profiles),
    ]