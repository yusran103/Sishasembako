# Generated by Django 3.0.3 on 2020-06-15 07:57

from django.db import migrations, models
import mapbox_location_field.models


class Migration(migrations.Migration):

    dependencies = [
        ('sishasembapo', '0016_auto_20200525_1053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='harga',
            name='validasi',
            field=models.CharField(choices=[('1', 'Disetujui'), ('2', 'Ditolak'), ('3', 'Belum Diperiksa')], default='1', max_length=2),
        ),
        migrations.AlterField(
            model_name='pasar',
            name='lokasi',
            field=mapbox_location_field.models.LocationField(map_attrs={'center': [111.999458, -7.817179], 'marker_color': 'blue', 'placeholder': 'Silahkan Pilih lokasi'}),
        ),
    ]