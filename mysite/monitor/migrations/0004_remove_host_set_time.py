# Generated by Django 4.0.4 on 2022-07-13 17:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0003_delete_time_remove_host_circuit_remove_host_local_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='host',
            name='set_time',
        ),
    ]
