# Generated by Django 4.0.2 on 2022-06-14 16:03

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('room_and_group', '0006_alter_group_options_alter_room_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 14, 23, 3, 39, 109290)),
        ),
    ]