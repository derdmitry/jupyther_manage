# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-03-11 13:39
from __future__ import unicode_literals

from django.db import migrations, models

import core.models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0002_auto_20160303_1409'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dockerconainer',
            name='port',
            field=models.IntegerField(default=core.models.rand_port, unique=True),
        ),
    ]
