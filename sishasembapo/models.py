from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Pasar(models.Model):
    nama = models.CharField(max_length=100)
    alamat = models.TextField()
    
    class Meta:
        db_table = "Tb_Pasar"
        verbose_name_plural = "Pasar"
    
    def __str__(self):
        return self.nama

class Sembako(models.Model):
    PILIHAN_CHOICES = [
        ('kg', 'kg'),
        ('Bungkus', 'Bungkus'),
        ('Liter', 'Liter'),
    ]
    nama = models.CharField(max_length=50)
    satuan = models.CharField(max_length=7, choices=PILIHAN_CHOICES, default='kg')

    class Meta:
        db_table = "Tb_Sembako"
        verbose_name_plural = "Sembako"
    
    def __str__(self):
        return "%s"%(self.nama)

class Harga(models.Model):
    nama_sembako = models.ForeignKey(Sembako, db_column='nama_barang', on_delete=models.CASCADE)
    nominal = models.IntegerField()
    nama_pasar = models.ForeignKey(Pasar,db_column='nama_pasar', on_delete=models.CASCADE)
    Tanggal = models.DateField()
    validasi = models.BooleanField(default=False)

    class Meta:
        db_table = "Tb_Harga"
        verbose_name_plural = "Harga"

    @property
    def price_display(self):
        return "Rp. %s" % self.nominal

    def __str__(self):
        return self.nama_sembako.nama

class PetugasPasar(models.Model):
    JK_CHOICES = [
        ('LK', 'Laki - Laki'),
        ('PR', 'Wanita')
    ]
    akun = models.OneToOneField(
        User,
        on_delete=models.CASCADE,primary_key=True,
    )
    nama = models.CharField(max_length=100)
    jenis_kelamin = models.CharField(max_length=20, choices=JK_CHOICES, default='LK')
    tempat_lahir = models.CharField(max_length=100)
    Tanggal_lahir = models.CharField(max_length=100)
    alamat = models.TextField()
    pasar = models.ForeignKey(Pasar,on_delete=models.CASCADE)
    No_hp = models.CharField(max_length=100)

    def __str__(self):
        return self.nama

    class Meta:
        db_table = "tb_Petugas_Pasar"
        verbose_name_plural = "Petugas Pasar"

    