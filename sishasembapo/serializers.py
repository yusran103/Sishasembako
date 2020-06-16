from rest_framework import serializers
from .models import *


class HargaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Harga
        fields = ('tanggal', 'nominal', 'validasi','nama_sembako','nama_pasar')