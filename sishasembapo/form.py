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
