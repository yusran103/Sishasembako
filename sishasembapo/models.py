from django.db import models
from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import intcomma
from django.template.defaultfilters import date
from location_field.models.plain import PlainLocationField
from mapbox_location_field.models import LocationField

# Create your models here.
class Pasar(models.Model):
    nama_pasar = models.CharField(max_length=100)
    alamat_pasar = models.TextField()
    kelurahan = models.CharField(max_length=100,null=True)
    kecamatan = models.CharField(max_length=100,null=True)
    notlp = models.CharField(max_length=13,null=True)
    lokasi = LocationField(map_attrs={"center": [111.999458,-7.817179], "marker_color": "blue", "placeholder": "Silahkan Pilih lokasi"})
    class Meta:
        db_table = "Tb_Pasar"
        verbose_name_plural = "Pasar"
    
    def __str__(self):
        return self.nama_pasar

class Sembako(models.Model):
    S_CHOICES = [
        ('Kg', 'Kg'),
        ('Perbiji', 'Perbiji'),
        ('Liter', 'Liter')
    ]
    nama_sembako = models.ForeignKey('self',null = True,blank=True,on_delete=models.CASCADE)
    jenis_sembako = models.CharField(max_length=50)
    satuan = models.CharField(max_length=20, choices=S_CHOICES, default='Kg')

    class Meta:
        db_table = "Tb_Sembako"
        verbose_name_plural = "Sembako"

    def __str__(self):
        if not self.nama_sembako:
            return "%s"%(self.jenis_sembako)
        else:
            return "%s - %s"%(self.nama_sembako,self.jenis_sembako)

class Harga(models.Model):
    class St(models.TextChoices):
            setuju = '1', 'Disetujui'
            tolak = '2', 'Ditolak'
            belum = '3', 'Belum Diperiksa'
        
    tanggal = models.DateField()
    nama_sembako = models.ForeignKey(Sembako,on_delete=models.CASCADE)
    nama_pasar = models.ForeignKey(Pasar,on_delete=models.CASCADE)
    nominal = models.IntegerField()
    validasi = models.CharField(max_length=2, choices=St.choices, default=St.belum)

    class Meta:
        db_table = "Tb_Harga"
        verbose_name_plural = "Harga"

    @property
    def harga(self):
        natural = intcomma(self.nominal)
        return "Rp. %s" % natural

    def __str__(self):
        return "%s - %s"%(self.nama_sembako.nama_sembako,self.nama_sembako.jenis_sembako)

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
    Tanggal_lahir = models.DateField()
    alamat = models.TextField()
    pasar = models.ForeignKey(Pasar,on_delete=models.CASCADE)
    No_hp = models.CharField(max_length=100)

    def __str__(self):
        return self.nama

    class Meta:
        db_table = "tb_Petugas_Pasar"
        verbose_name_plural = "Petugas Pasar"

    