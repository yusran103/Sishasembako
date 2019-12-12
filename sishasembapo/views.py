from django.shortcuts import render, get_object_or_404 ,redirect
from django.contrib import messages
from django.contrib.auth import authenticate, logout, login
from sishasembapo.models import *
from sishasembapo.form import *
from django.db import connection
from django.http import HttpResponse,FileResponse, Http404
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.template import context
from django.views.generic.edit import CreateView

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
                    request.session['id'] = user.id
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


# CHANGEPASSWORD 
@login_required(login_url='/login')
def changepassword(request,pk):
    user = User.objects.filter(id = request.session['id']).first()
    if request.method == "POST":
        form = User_form(request.POST, instance=user)
        if form.is_valid():
            url = '/'
            resp_body = '<script>alert("Password user %s Berhasil di rubah, Silahkan Login Kembali");\
            window.location="%s"</script>' % (user.username , url)
            cursor = connection.cursor()
            cursor.execute("update auth_user set password='%s' where id='%s'"%(make_password(request.POST['password']),user.id))
            logout(request)
            return HttpResponse(resp_body)
    else:
        form = User_form(instance=user)
    return render(request, 'changepassword.html', {'form': form, 'user' : user,'messages':messages})

@login_required(login_url='/login')
def changeprofile(request,pk):
    user = PetugasPasar.objects.filter(akun_id = request.session['id']).first()
    if request.method == "POST":
        form = Profile_form(request.POST, instance=user)
        if form.is_valid():
            url = '/'
            resp_body = '<script>alert("Profil user %s Berhasil di rubah");\
            window.location="%s"</script>' % (user.nama , url)
            cursor = connection.cursor()
            cursor.execute(
                """update tb_siswa set 
                    nama='%s',
                    alamat='%s',
                    nama_bapak='%s',
                    nama_ibu='%s',
                    sekolah='%s',
                    alamat_sekolah='%s' where akun_id ='%s' """
                    %(
                        request.POST['nama'],
                        request.POST['alamat'],
                        request.POST['nama_bapak'],
                        request.POST['nama_ibu'],
                        request.POST['sekolah'],
                        request.POST['alamat_sekolah'],
                        user.akun_id
                    )
                )
            request.session['nama'] = user.nama
            return HttpResponse(resp_body)
    else:
        form = Profile_form(instance=user)
    return render(request, 'changeprofile.html', {'form': form, 'user' : user,'messages':messages})

@login_required(login_url='/login')
def view_harga(request):
    ambil_pasar = Pasar.objects.get(nama=request.session['pasar'])
    list_harga = Harga.objects.filter(nama_pasar = ambil_pasar.id)
    if request.method == "POST":
        form = Harga_form(request.POST)
        if form.is_valid():
            url = '/harga'
            resp_body = '<script>window.location="%s"</script>' % (url)
            hargasembako = Harga(
                nama_sembako = Sembako.objects.get(pk=request.POST.get('nama_sembako')),
                nominal = request.POST['nominal'],
                nama_pasar = ambil_pasar,
                validasi = False
            )
            hargasembako.save()
            messages.add_message(request, messages.INFO, 'Berhasil Menambah Data') 
            return HttpResponse(resp_body)
    else:
        form = Harga_form()
    return render(request,'admin_pasar/Harga.html', {'form':form,'harga':list_harga})
