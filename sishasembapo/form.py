from django import forms
from django.forms import ModelForm,Select
from sishasembapo.models import *

YEARS= [x for x in range(1940,2021)]
class AdminPasarForm(ModelForm):
    akun = forms.ModelChoiceField(
        queryset = User.objects.filter(is_staff=False),
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
                'placeholder':'Isikan username'
                }
            ),
            required=True
        )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class':'form-control',
                'placeholder':'Isikan password'
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
        queryset = Sembako.objects.all(),
        widget = Select(
            attrs = {
                'class':'form-control',
            }
        )
    )
    nominal = forms.CharField(
        widget=forms.TextInput(
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