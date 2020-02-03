from django.contrib import admin
from sishasembapo.models import *
from sishasembapo.form import *
from django.utils import translation
# Register your models here.

admin.site.index_title = 'ADMIN PD. PASAR'
translation.activate('id')
class hargaAdmin(admin.ModelAdmin):
    readonly_fields = ('Tanggal','nama_sembako','nama_pasar','harga')
    list_display = ['Tanggal','nama_sembako','harga','nama_pasar','validasi']
    list_filter = ['nama_pasar__nama_pasar']
    form = Harga_form_admin
    
    def Tanggal(self, obj):
        return obj.tanggal.strftime('%A, %d %B %Y')

class pasarAdmin(admin.ModelAdmin):
    list_display = ['nama_pasar','alamat_pasar']

class sembakoAdmin(admin.ModelAdmin):
    list_display = ['daftar_sembako','satuan']
    form = sembako_form_admin
    def daftar_sembako(self, obj):
        if not obj.nama_sembako:
            return obj.jenis_sembako
        else:
            return '%s - %s'%(obj.nama_sembako,obj.jenis_sembako)

class formadminpasar(admin.ModelAdmin):
    list_display = ['nama','pasar']
    list_filter = ['pasar__nama_pasar']
    form = AdminPasarForm

admin.site.register(Pasar,pasarAdmin)
admin.site.register(Sembako,sembakoAdmin)
admin.site.register(Harga,hargaAdmin)
admin.site.register(PetugasPasar,formadminpasar)
