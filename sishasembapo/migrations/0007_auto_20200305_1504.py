# Generated by Django 3.0.3 on 2020-03-05 08:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sishasembapo', '0006_pasar_location'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pasar',
            old_name='location',
            new_name='lokasi',
        ),
    ]
