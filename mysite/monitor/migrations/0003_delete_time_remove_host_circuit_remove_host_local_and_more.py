# Generated by Django 4.0.4 on 2022-07-13 17:25

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0002_time'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Time',
        ),
        migrations.RemoveField(
            model_name='host',
            name='circuit',
        ),
        migrations.RemoveField(
            model_name='host',
            name='local',
        ),
        migrations.RemoveField(
            model_name='host',
            name='max_retries',
        ),
        migrations.RemoveField(
            model_name='host',
            name='retries',
        ),
        migrations.AddField(
            model_name='host',
            name='set_time',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name=' time'),
        ),
    ]
