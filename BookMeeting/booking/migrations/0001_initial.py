# Generated by Django 3.2 on 2022-08-25 02:00

from django.db import migrations, models
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('time_from', models.DateTimeField()),
                ('time_to', models.DateTimeField()),
                ('status', models.CharField(choices=[('-1', 'delete'), ('0', 'active '), ('1', 'completed')], default='0', max_length=20)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['time_from'],
            },
        ),
    ]
