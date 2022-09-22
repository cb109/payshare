# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-28 18:16
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0002_add_liquidation_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='collective',
            name='key',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
    ]
