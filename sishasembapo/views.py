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
import datetime
from django.db.models import Q
from django.utils import translation
from django.db.models.functions import Coalesce

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
                    request.session['pasar'] = profil.pasar.nama_pasar
                    request.session['id'] = user.id
                    for key, value in request.session.items():
                        print('{} => {}'.format(key, value))
                    return redirect('/')
                except PetugasPasar.DoesNotExist:
                    messages.add_message(request, messages.INFO, 'Akun Tersebut Belum Terintegrasi Dengan Petugas Pasar Manapun, Silahkan Hubungi Admin PD. Pasar')  
            else:
               messages.add_message(request, messages.INFO, 'Akun Tersebut Bukan Termasuk Akun Petugas Pasar') 
        else:
            messages.add_message(request, messages.INFO, 'Username atau password Anda salah')
    return render(request, 'login.html')

def index(request):

    ambilpasar = Pasar.objects.all()
    ambilsembakosemua = Sembako.objects.annotate(induk=Coalesce('nama_sembako','id')).order_by('induk','id')
    #ambilsembakosemua = Harga.objects.annotate(induk=Coalesce('nama_sembako__nama_sembako','nama_sembako__id')).order_by('induk','nama_sembako__id')

    for key, value in request.session.items():
        print('{} => {}'.format(key, value))

    date_isi = []
    if request.method == "POST":
        ambiltanggal = request.POST['tanggal']
        tanggal = datetime.datetime.strptime(ambiltanggal,'%Y-%m-%d')
        kemarin = datetime.timedelta(days=1)
        date_isi.append({ "kemarin":tanggal - kemarin, "tanggal":tanggal})
    # print(ambilsembakosemua)
   
    data = [];
    for sem in ambilsembakosemua:
        sekarang = 0
        kemarin = 0
        if sem.nama_sembako:
            # print(sem.id)
            for dd in date_isi:
                ambilsembakos = Harga.objects.filter(tanggal=dd['tanggal'],nama_sembako__id=sem.id,validasi=True).first()
                if ambilsembakos:
                    sekarang = ambilsembakos.nominal
                else:
                    sekarang = 0

                ambilkemarin = Harga.objects.filter(tanggal=dd['kemarin'],nama_sembako__id=sem.id,validasi=True).first()
                if ambilkemarin:
                    kemarin = ambilkemarin.nominal
                else:
                    kemarin = 0
        data.append({"induk":sem.nama_sembako,'jenis':sem.jenis_sembako,"sekarang":sekarang,"kemarin":kemarin})
    # print(data)

    return render(request, 'pengunjung/index.html',{'pasar':ambilpasar,'sembakosemua':data})

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
    ambil_pasar = Pasar.objects.get(nama_pasar=request.session['pasar'])
    # list_harga = Harga.objects.filter(nama_pasar = ambil_pasar.id,tanggal = datetime.date.today())
    list_harga = Harga.objects.filter(nama_pasar = ambil_pasar.id)
    translation.activate('id')
    if request.method == "POST":
        form = Harga_form(request.POST)
        if form.is_valid():
            url = '/harga'
            resp_body = '<script>window.location="%s"</script>' % (url)
            hargasembako = Harga(
                nama_sembako = Sembako.objects.get(pk=request.POST.get('nama_sembako')),
                nominal = request.POST['nominal'],
                nama_pasar = ambil_pasar,
                tanggal = request.POST['tanggal'],
                validasi = True
            )
            hargasembako.save()
            messages.add_message(request, messages.INFO, 'Berhasil Menambah Data') 
            return HttpResponse(resp_body)
    else:
        form = Harga_form()
    return render(request,'admin_pasar/Harga.html', {'form':form,'harga':list_harga})
