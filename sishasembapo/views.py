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
from django.db.models import Q, Avg
from django.utils import translation
from django.db.models.functions import Coalesce
from django.db import connection

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

    for key, value in request.session.items():
        print('{} => {}'.format(key, value))

    pencarian = []
    date_isi = []
    if request.method == "POST":
        ambiltanggal = request.POST['tanggal']
        ambilpasar1 = request.POST.get('nama_pasar')
        tanggal = datetime.datetime.strptime(ambiltanggal,'%Y-%m-%d')
        kemarin = datetime.timedelta(days=1)
        date_isi.append({ "kemarin":tanggal - kemarin, "tanggal":tanggal,'pasar':ambilpasar1})
        pencarian.append({ "pasar":Pasar.objects.get(id=ambilpasar1).nama_pasar,"tanggal":tanggal})
    else:
        ambiltanggal = datetime.datetime.now().date()
        ambiltanggal1 = datetime.datetime.strftime(ambiltanggal,'%Y-%m-%d')
        ambilpasar1 = 1
        kemarin = datetime.timedelta(days=1)
        date_isi.append({ "kemarin":ambiltanggal - kemarin, "tanggal":ambiltanggal,'pasar':ambilpasar1})
        pencarian.append({ "pasar":Pasar.objects.get(id=ambilpasar1).nama_pasar,"tanggal":ambiltanggal})
   
    data = [];
    for sem in ambilsembakosemua:
        sekarang = 0
        kemarin = 0
        perubahan = 0
        persen = 0
        if sem.nama_sembako:
            for dd in date_isi:
                ambilsembakos = Harga.objects.filter(tanggal=dd['tanggal'],nama_sembako__id=sem.id,validasi=True,nama_pasar__id=dd['pasar']).order_by('-id').first()
                if ambilsembakos:
                    sekarang = ambilsembakos.nominal
                else:
                    sekarang = 0

                ambilkemarin = Harga.objects.filter(tanggal=dd['kemarin'],nama_sembako__id=sem.id,validasi=True,nama_pasar__id=dd['pasar']).order_by('-id').first()
                if ambilkemarin:
                    kemarin = ambilkemarin.nominal
                else:
                    kemarin = 0

                perubahan = sekarang - kemarin
                if sekarang and kemarin:
                    persen = round(((sekarang-kemarin)/kemarin)*100,2)
                else:
                    persen = 0
        data.append({"induk":sem.nama_sembako,'jenis':sem.jenis_sembako,"sekarang":sekarang,"kemarin":kemarin,"satuan":sem.satuan,"perubahan":perubahan,"persen":persen})
    print(data)
    return render(request, 'pengunjung/index.html',{'pasar':ambilpasar,'sembakosemua':data,"pencarian":pencarian})

@login_required(login_url='/login')
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
            url = '/login'
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
def profile(request,pk):
    user = PetugasPasar.objects.filter(akun_id = request.session['id']).first()
    translation.activate('id')
    return render(request, 'changeprofile.html', {'user' : user,'messages':messages})

@login_required(login_url='/login')
def view_harga(request):
    penambahan = []
    ambil_pasar = Pasar.objects.get(nama_pasar=request.session['pasar'])
    # list_harga = Harga.objects.filter(nama_pasar = ambil_pasar.id,tanggal = datetime.date.today())
    list_harga = Harga.objects.filter(nama_pasar = ambil_pasar.id,tanggal__year=datetime.datetime.now().year,tanggal__month=datetime.datetime.now().month).order_by('-id')
    translation.activate('id')
    if request.method == "POST":
        form = Harga_form(request.POST)
        sembako = Sembako.objects.get(pk=request.POST.get('nama_sembako'))
        tanggal = request.POST['tanggal']
        if form.is_valid():
            url = '/harga'
            hargasembako = Harga(
                nama_sembako = sembako,
                nominal = request.POST['nominal'],
                nama_pasar = ambil_pasar,
                tanggal = tanggal,
                validasi = False
            )
            hargasembako.save()
            Tanggal = datetime.datetime.strptime(tanggal,'%Y-%m-%d')
            penambahan.append({"tanggal":Tanggal,"sembako":sembako})
    else:
        form = Harga_form()
    return render(request,'admin_pasar/Harga.html', {'form':form,'harga':list_harga,'penambahan':penambahan})

def update_harga(request,pk):
    perubahan = []
    ambil_pasar = Pasar.objects.get(nama_pasar=request.session['pasar'])
    harga = Harga.objects.get(pk=pk)
    sembako = Sembako.objects.get(pk=harga.nama_sembako.id)
    if request.method == "POST":
        Tanggal = request.POST['tanggal']
        form = Harga_form(request.POST, instance=harga)
        if form.is_valid():
            hargas = form.save(commit=False)
            nama_sembako = sembako,
            nominal = request.POST['nominal'],
            nama_pasar = ambil_pasar,
            tanggal = Tanggal,
            hargas.save()
            tanggals = datetime.datetime.strptime(Tanggal,'%Y-%m-%d')
    else:
        form = Harga_form(instance=harga)
    return render(request,'admin_pasar/edit_harga.html',{'form':form,'perubahan':perubahan,'harga':harga})

def view_grafik(request):
    ambil_pasar = Pasar.objects.all()
    ambil_Sembako = Sembako.objects.filter(nama_sembako__isnull=False).order_by('nama_sembako')
    x = datetime.datetime.now()
    # print(ambil_harga1)
    data_isi1 = []
    pencarian1 = []
    if request.method == "POST":
        nama_pasar = request.POST['nama_pasar'] 
        nama_bahan = request.POST.get('nama_bahan')
        tahun = request.POST['tahun']
        data_isi1.append({"nama_pasar":nama_pasar,"nama_bahan":nama_bahan,"tahun":tahun})
        pencarian1.append({ "pasar":Pasar.objects.get(id=nama_pasar).nama_pasar,"tahun":tahun,"nama_bahan":Sembako.objects.get(id=nama_bahan).nama_sembako.jenis_sembako,"nama_jenis":Sembako.objects.get(id=nama_bahan).jenis_sembako})
    else:
        nama_pasar = 1 
        nama_bahan = 28
        tahun = x.year
        data_isi1.append({"nama_pasar":nama_pasar,"nama_bahan":nama_bahan,"tahun":tahun})
        pencarian1.append({ "pasar":Pasar.objects.get(id=nama_pasar).nama_pasar,"tahun":tahun,"nama_bahan":Sembako.objects.get(id=nama_bahan).nama_sembako.jenis_sembako,"nama_jenis":Sembako.objects.get(id=nama_bahan).jenis_sembako})

    jan = 0
    data1 = []
    for i in data_isi1:
        for a in range(1,13):
            b = '%02d' % a
            isi = Harga.objects.filter(nama_sembako=i['nama_bahan'],nama_pasar=i['nama_pasar'],tanggal__month=b,tanggal__year=i['tahun']).annotate(Avg('nominal')).first()
            if isi:
                data1.append(isi.nominal)
            else:
                data1.append(0)
    return render(request,'admin_pasar/Grafik.html',{'pasar':ambil_pasar,'sembako':ambil_Sembako,'data':data1,'pencarian1':pencarian1})

def maps(request):
    api_key = "pk.eyJ1IjoieXVzcmFuMTAzIiwiYSI6ImNrMWo0MDNpdjAyMDQzaHA0aHdkcjhtbTUifQ.2S8rcVwnT1x4-41R20FBWg"
    pasar =[]
    list_pasar = Pasar.objects.all()
    for pasar1 in list_pasar:
        koordinat = pasar1.lokasi
        pecah = koordinat.split(',')
        lat = pecah[0]
        lng = pecah[1]
        pasar.append({"nama_pasar":pasar1.nama_pasar,"lat":lat,"lng":lng})
    return render(request,'admin_pasar/maps.html',{'api':api_key,'pasar':pasar})
