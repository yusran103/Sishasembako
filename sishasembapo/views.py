from django.shortcuts import render, get_object_or_404 ,redirect
from django.contrib import messages, auth
from django.contrib.auth import authenticate, logout, login
from sishasembapo.models import *

# Create your views here.
def Login(request):
    if request.POST:
        user = authenticate(username=request.POST['login_username'], password=request.POST['login_password'])
        if user is not None:
            if not user.is_staff:
                try:
                    profil = PetugasPasar.objects.get(akun_id=user.id)
                    login(request, user)
                    request.session['nama'] = profil.nama
                    request.session['pasar'] = profil.pasar.nama
                    for key, value in request.session.items():
                        print('{} => {}'.format(key, value))
                    return redirect('/')
                except PetugasPasar.DoesNotExist:
                    messages.add_message(request, messages.INFO, 'Akun Tersebut Belum Terintegrasi dengan Petugas Pasar, Silahkan Hubungi Admin PD. Pasar')  
            else:
               messages.add_message(request, messages.INFO, 'Akun Tersebut Bukan Termasuk Akun Petugas Pasar') 
        else:
            messages.add_message(request, messages.INFO, 'Username atau password Anda salah')
    return render(request, 'login.html')

def index(request):
    for key, value in request.session.items():
        print('{} => {}'.format(key, value))
    return render(request, 'pengunjung/index.html')

def Logout(request):
    logout(request)
    for key in request.session.keys():
        del request.session[key]
    return redirect('/')