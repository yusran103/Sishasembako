from django import forms
from django.forms import ModelForm,Select
from sishasembapo.models import *
from django.db.models import Q
from location_field.forms.plain import PlainLocationField
import datetime

z = datetime.datetime.now().year
YEARS= [x for x in range(1940,z+1)]
class Profile_form(ModelForm):
    nama = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class':'form-control',
                'placeholder':'Isikan nama'
                }
            ),
            required=True
        )
    jenis_kelamin = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class':'form-control',
                'placeholder':'Isikan nama'
                }
            ),
            required=True
        )
    tempat_lahir = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class':'form-control',
                'placeholder':'Isikan nama bapak'
                }
            ),
            required=True
        )
    Tanggal_lahir = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class':'form-control',
                'placeholder':'Isikan username'
                }
            ),
            required=True
        )
    alamat = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class':'form-control',
                'placeholder':'Isikan nama sekolah'
                }
            ),
            required=True
        )
    No_hp = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class':'form-control',
                'placeholder':'Isikan nama angkatan'
                }
            ),
            required=True
        )
    class Meta:
        model = PetugasPasar
        exclude=('akun','pasar')

class AdminPasarForm(ModelForm):
    akun = forms.ModelChoiceField(
        queryset = User.objects.filter(~Q(id__in=PetugasPasar.objects.all()),Q(is_staff=False)),
        widget = Select(
            attrs = {
                'class':'form-control',
            }
        )
    )
    Tanggal_lahir = forms.DateField(label='Tanggal lahir', widget=forms.SelectDateWidget(years=YEARS))
    
    class Meta:
        model = PetugasPasar
        fields = "__all__"
        
class User_form(ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class':'form-control',
                'placeholder':'Isikan nama pengguna'
                }
            ),
            required=True
        )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class':'form-control',
                'placeholder':'Isikan Sandi Baru'
                }
            ),
            required=True
        )
    class Meta:
        model = User
        fields = [
            'username',
            'password'
        ]

class Harga_form(ModelForm):
    nama_sembako = forms.ModelChoiceField(
        queryset = Sembako.objects.filter(nama_sembako__isnull=False).order_by('nama_sembako'),
        widget = Select(
            attrs = {
                'style':'width:100%'
            }
        )
    )
    nominal = forms.CharField(
        widget=forms.NumberInput(
            attrs={
                'class':'form-control',
                'placeholder':'Isikan harga'
                }
            ),
            required=True
        )
    class Meta:
        model = Harga
        fields = [
            'nama_sembako',
            'nominal'
        ]

class Harga_form_admin(ModelForm):
    class Meta:
        model = Harga
        fields = [
            'validasi'
        ]

class sembako_form_admin(ModelForm):
    nama_sembako = forms.ModelChoiceField(
        queryset = Sembako.objects.filter(nama_sembako__isnull=True),
        widget = Select(
            attrs = {
                'class':'form-control',
            }
        ),
        required=False
    )
    class Meta:
        model = Sembako
        fields = "__all__"