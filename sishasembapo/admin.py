from django.contrib import admin
from sishasembapo.models import *
from sishasembapo.form import *
from django.db.models import F
from django.utils.translation import ugettext_lazy as _
import datetime
from django.http import HttpResponse
from sishasembapo.actions import export_as_xls
from mapbox_location_field.admin import MapAdmin
from django.utils.html import mark_safe
# Register your models here.

admin.site.index_title = 'ADMIN PD. PASAR'
admin.site.site_header = 'SISHASEMBAKO Apps'
admin.site.site_title = 'SISHASEMBAKO Apps'

class SembakoListFilter(admin.SimpleListFilter):
    title = ('Nama Sembako')
    parameter_name = 'Sembako'

    def lookups(self, request, model_admin):
        return [(c.id, ("{} - {}").format(c.nama_sembako,c.jenis_sembako)) for c in Sembako.objects.filter(nama_sembako__isnull=False)]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(nama_sembako=self.value())
        else:
            return queryset

class hargaAdmin(admin.ModelAdmin):
    readonly_fields = ('Tanggal','nama_sembako','nama_pasar','harga')
    list_display = ['Tanggal','nama_sembako','harga','nama_pasar','status']
    list_filter = ['nama_pasar__nama_pasar',SembakoListFilter]
    form = Harga_form_admin
    list_per_page = 10
    date_hierarchy = 'tanggal'
    actions = ['validasi_harga','tolak_harga','hapuspilih',export_as_xls]

    def status(self,obj):
        if obj.validasi == "1": # Setuju
            return mark_safe("<img src='/static/icon/ok.png'  width='20' height='20' />")
        elif obj.validasi == "2": # tolak
            return mark_safe("<img src='/static/icon/cancel.png'  width='20' height='20' />")
        elif obj.validasi == "3": # menunggu
            return mark_safe("<img src='/static/icon/important.png'  width='20' height='20' />")
    status.allow_tags = True
            
    def validasi_harga(self, request, queryset):
        for harga in queryset:
            harga.validasi = Harga.St.setuju
            harga.save()
    validasi_harga.short_description = 'Validasi Disetujui'
    def tolak_harga(self, request, queryset):
        for harga in queryset:
            harga.validasi = Harga.St.tolak
            harga.save()
    tolak_harga.short_description = 'Validasi Ditolak'

    def hapuspilih(self, request, queryset):
        for harga in queryset:
            harga.delete()
    hapuspilih.short_description = 'Hapus yang dipilih'

    def Tanggal(self, obj):
        return obj.tanggal.strftime('%d-%m-%Y')

class pasarAdmin(admin.ModelAdmin):
    list_display = ['nama_pasar','alamat_pasar']
    list_per_page = 10

class sembakoAdmin(admin.ModelAdmin):
    list_display = ['daftar_sembako','satuan']
    form = sembako_form_admin
    list_per_page = 10
    def daftar_sembako(self, obj):
        if not obj.nama_sembako:
            return obj.jenis_sembako
        else:
            return '%s - %s'%(obj.nama_sembako,obj.jenis_sembako)

class formadminpasar(admin.ModelAdmin):
    list_display = ['nama','pasar']
    list_filter = ['pasar__nama_pasar']
    form = AdminPasarForm
    list_per_page = 10

    def get_readonly_fields(self, request, obj=None):
        if obj: #This is the case when obj is already created i.e. it's an edit
            return ['akun']
        else:
            return []

# admin.site.register(Pasar,pasarAdmin)
admin.site.register(Pasar, MapAdmin)
admin.site.register(Sembako,sembakoAdmin)
admin.site.register(Harga,hargaAdmin)
admin.site.register(PetugasPasar,formadminpasar)
