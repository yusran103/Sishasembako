from django.contrib import admin
from sishasembapo.models import *
from sishasembapo.form import *
# Register your models here.

admin.site.index_title = 'ADMIN PD. PASAR'

class hargaAdmin(admin.ModelAdmin):
    list_display = ['nama_sembako','price_display','nama_pasar','validasi']

class pasarAdmin(admin.ModelAdmin):
    list_display = ['nama','alamat']

class sembakoAdmin(admin.ModelAdmin):
    list_display = ['nama','satuan']

class formadminpasar(admin.ModelAdmin):
    list_display = ['nama','pasar']
    list_filter = ['pasar__nama']
    form = AdminPasarForm

admin.site.register(Pasar,pasarAdmin)
admin.site.register(Sembako,sembakoAdmin)
admin.site.register(Harga,hargaAdmin)
admin.site.register(PetugasPasar,formadminpasar)
