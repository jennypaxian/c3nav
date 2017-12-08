# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-08 15:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('control', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpermissions',
            name='access_all',
            field=models.BooleanField(default=False, verbose_name='can access and grant access to everything'),
        ),
    ]