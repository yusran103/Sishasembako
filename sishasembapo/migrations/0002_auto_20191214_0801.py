# Generated by Django 2.2.6 on 2019-12-14 01:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sishasembapo', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pasar',
            old_name='alamat',
            new_name='alamat_pasar',
        ),
        migrations.RenameField(
            model_name='pasar',
            old_name='nama',
            new_name='nama_pasar',
        ),
        migrations.AlterField(
            model_name='harga',
            name='nama_pasar',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sishasembapo.Pasar'),
        ),
        migrations.AlterField(
            model_name='harga',
            name='nama_sembako',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sishasembapo.Sembako'),
        ),
    ]
