# Generated by Django 4.0.2 on 2022-10-17 07:42

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('room_and_group', '0003_alter_group_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 17, 14, 42, 37, 519405)),
        ),
    ]