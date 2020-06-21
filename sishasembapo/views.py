from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, logout, login, update_session_auth_hash
from sishasembapo.models import *
from sishasembapo.form import *
from django.db import connection
from django.http import HttpResponse,FileResponse, Http404, HttpResponseRedirect
from django.contrib.auth.hashers import make_password,check_password
from django.contrib.auth.decorators import login_required
import datetime
from django.db import connection
from django.db.models import Q, Avg
from django.utils import translation
from django.db.models.functions import Coalesce
from .serializers import *
from django.core import serializers
from django.core.serializers import serialize 
from rest_framework import generics

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
                    request.session['idpasar'] = profil.pasar.id
                    request.session['id'] = user.id
                    if 'next' in request.POST:
                        return redirect(request.POST.get('next'))
                    elif 'url' in request.session:
                        return redirect(request.session['url'])
                    else:
                        return redirect('/')
                except PetugasPasar.DoesNotExist:
                    messages.add_message(request, messages.INFO, 'Akun Tersebut Belum Terintegrasi Dengan Petugas Pasar Manapun, Silahkan Hubungi Admin PD. Pasar')
                    return redirect(request.META['HTTP_REFERER'])
            else:
                messages.add_message(request, messages.INFO, 'Akun Tersebut Bukan Termasuk Akun Petugas Pasar')
                return redirect(request.META['HTTP_REFERER'])
        else:
            messages.add_message(request, messages.INFO, 'Username atau password Anda salah')
            return redirect(request.META['HTTP_REFERER'])
    return render(request, 'login.html')

def index(request):
    request.session['url'] = request.get_full_path()
    ambilpasar = Pasar.objects.all()
    ambilsembakosemua = Sembako.objects.annotate(induk=Coalesce('nama_sembako','id')).order_by('induk','id')
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
        if 'pasar' not in request.session:
            ambilpasar1 = 1
        else:
            ambilpasar1 = ambilpasar.get(nama_pasar=request.session['pasar']).id
        kemarin = datetime.timedelta(days=1)
        date_isi.append({ "kemarin":ambiltanggal - kemarin, "tanggal":ambiltanggal,'pasar':ambilpasar1})
        pencarian.append({ "pasar":Pasar.objects.get(id=ambilpasar1).nama_pasar,"tanggal":ambiltanggal})
   
    data = []
    for sem in ambilsembakosemua:
        sekarang = 0
        kemarin = 0
        perubahan = 0
        persen = 0
        if sem.nama_sembako:
            for dd in date_isi:
                ambilsembakos = Harga.objects.filter(tanggal=dd['tanggal'],nama_sembako__id=sem.id,validasi=Harga.St.setuju,nama_pasar__id=dd['pasar']).order_by('-id').first()
                if ambilsembakos:
                    sekarang = ambilsembakos.nominal
                else:
                    sekarang = 0

                ambilkemarin = Harga.objects.filter(tanggal=dd['kemarin'],nama_sembako__id=sem.id,validasi=Harga.St.setuju,nama_pasar__id=dd['pasar']).order_by('-id').first()
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
    return render(request, 'pengunjung/index.html',{'pasar':ambilpasar,'sembakosemua':data,"pencarian":pencarian})

def Logout(request):
    logout(request)
    for key in request.session.keys():
        del request.session[key]
    return redirect('/') 

# CHANGEPASSWORD 
@login_required(login_url='/login')
def changepassword(request,pk):
    pesan = []
    user = User.objects.filter(id = request.session['id']).first()
    if request.method == "POST":
        old_password = request.POST['old_password']
        comnewpassword = request.POST['confrim_password']
        newpassword = request.POST['password']
        form = User_form(request.POST, instance=user)
        if check_password(old_password, user.password):
            if newpassword == comnewpassword:
                if form.is_valid():
                    newpw = form.save(commit=False)
                    newpw.username = user.username
                    newpw.password = make_password(newpassword)
                    newpw.save()
                    pesan.append({"id":"1","status":"success","messages":"Sandi berhasil dirubah"})
                    update_session_auth_hash(request, form.instance)
            else:
                pesan.append({"id":"2","status":"danger","messages":"Sandi baru tidak cocok. Masukkan sekali lagi."})
        else:
            pesan.append({"id":"3","status":"danger","messages":"Sandi lama yang anda masuk salah. Masukkan sekali lagi."})
    else:
        form = User_form(instance=user)
    return render(request, 'changepassword.html', {'form': form, 'user' : user,'pesan':pesan})

@login_required(login_url='/login')
def profile(request,pk):
    request.session['url'] = request.get_full_path()
    user = PetugasPasar.objects.filter(akun_id = request.session['id']).first()
    translation.activate('id')
    return render(request, 'changeprofile.html', {'user' : user})

@login_required(login_url='/login')
def view_harga(request):
    ambil_pasar = Pasar.objects.get(nama_pasar=request.session['pasar'])
    list_harga = Harga.objects.filter(nama_pasar = ambil_pasar.id,tanggal=datetime.datetime.now()).order_by('-id')
    kemarin = datetime.date.today() - datetime.timedelta(days=1)
    harga_kemarin = Harga.objects.filter(nama_pasar = ambil_pasar.id,tanggal=kemarin,validasi=Harga.St.setuju)
    return render(request,'admin_pasar/Harga.html', {'harga':list_harga,'kemarin':harga_kemarin})

@login_required(login_url='/login')
def update_harga(request,pk):
    ambil_pasar = Pasar.objects.get(nama_pasar=request.session['pasar'])
    harga = Harga.objects.get(pk=pk)
    sembako = Sembako.objects.get(pk=harga.nama_sembako.id)
    if request.method == "POST":
        cursor = connection.cursor()
        cursor.execute("update tb_harga set nominal='%s' , validasi=3 where id='%s'"%(request.POST['nominal'],pk))
    else:
        form = Harga_form(instance=harga)
    return render(request,'admin_pasar/edit_harga.html',{'form':form,'harga':harga})

def view_grafik(request):
    request.session['url'] = request.get_full_path()
    ambil_pasar = Pasar.objects.all()
    ambil_Sembako = Sembako.objects.filter(nama_sembako__isnull=False).order_by('nama_sembako')
    x = datetime.datetime.now()
    data_isi1 = []
    pencarian1 = []
    if request.method == "POST":
        nama_pasar = request.POST['nama_pasar']
        nama_bahan = request.POST.get('nama_bahan')
        tahun1 = request.POST['tahun']
        tahun = datetime.date(year=int(tahun1),month=1,day=1).year
        if nama_pasar == "semua":
            data_isi1.append({"pasar":"semua","nama_bahan":Sembako.objects.get(id=nama_bahan).id,"tahun":tahun})
            pencarian1.append({"pasar":"Semua Pasar","tahun":tahun,"nama_bahan":Sembako.objects.get(id=nama_bahan).nama_sembako.jenis_sembako,"nama_jenis":Sembako.objects.get(id=nama_bahan).jenis_sembako,"satuan":Sembako.objects.get(id=nama_bahan).satuan})
        else:
            data_isi1.append({"nama_pasar":Pasar.objects.get(id=nama_pasar).id,"nama_bahan":Sembako.objects.get(id=nama_bahan).id,"tahun":tahun})
            pencarian1.append({"Semua Pasar":Pasar.objects.get(id=nama_pasar).nama_pasar,"tahun":tahun,"nama_bahan":Sembako.objects.get(id=nama_bahan).nama_sembako.jenis_sembako,"nama_jenis":Sembako.objects.get(id=nama_bahan).jenis_sembako,"satuan":Sembako.objects.get(id=nama_bahan).satuan})
    else:
        if 'pasar' not in request.session:
            nama_pasar = str(ambil_pasar.first().id)
        else:
            nama_pasar = str(ambil_pasar.get(nama_pasar=request.session['pasar']).id)
        nama_bahan = "28"
        tahun = x.year
        data_isi1.append({"nama_pasar":nama_pasar,"nama_bahan":nama_bahan,"tahun":tahun})
        pencarian1.append({"pasar":Pasar.objects.get(id=nama_pasar).nama_pasar,"tahun":tahun,"nama_bahan":Sembako.objects.get(id=nama_bahan).nama_sembako.jenis_sembako,"nama_jenis":Sembako.objects.get(id=nama_bahan).jenis_sembako,"satuan":Sembako.objects.get(id=nama_bahan).satuan})
    # Grafik Besar
    listpasar = []
    setono=[]
    pahing=[]
    banjaran=[]
    bawang=[]
    ngronggo=[]
    ngalim=[]
    bandar=[]
    mrican =[]
    for i in data_isi1:
        for a in range(1,13):
            b = '%02d' % a
            if nama_pasar == "semua":
                for p in ambil_pasar:
                    if p.pk == 1:
                        isi = Harga.objects.filter(nama_sembako=i['nama_bahan'],nama_pasar=p.pk,tanggal__month=b,tanggal__year=i['tahun'],validasi=Harga.St.setuju).aggregate(Avg('nominal'))
                        if isi['nominal__avg'] != None:
                            setono.append(round(isi['nominal__avg']))
                    elif p.pk == 2:
                        isi = Harga.objects.filter(nama_sembako=i['nama_bahan'],nama_pasar=p.pk,tanggal__month=b,tanggal__year=i['tahun'],validasi=Harga.St.setuju).aggregate(Avg('nominal'))
                        if isi['nominal__avg'] != None:
                            pahing.append(round(isi['nominal__avg']))
                    elif p.pk == 3:
                        isi = Harga.objects.filter(nama_sembako=i['nama_bahan'],nama_pasar=p.pk,tanggal__month=b,tanggal__year=i['tahun'],validasi=Harga.St.setuju).aggregate(Avg('nominal'))
                        if isi['nominal__avg'] != None:
                            banjaran.append(round(isi['nominal__avg']))
                    elif p.pk == 4:
                        isi = Harga.objects.filter(nama_sembako=i['nama_bahan'],nama_pasar=p.pk,tanggal__month=b,tanggal__year=i['tahun'],validasi=Harga.St.setuju).aggregate(Avg('nominal'))
                        if isi['nominal__avg'] != None:
                            bawang.append(round(isi['nominal__avg']))
                    elif p.pk == 5:
                        isi = Harga.objects.filter(nama_sembako=i['nama_bahan'],nama_pasar=p.pk,tanggal__month=b,tanggal__year=i['tahun'],validasi=Harga.St.setuju).aggregate(Avg('nominal'))
                        if isi['nominal__avg'] != None:
                            ngronggo.append(round(isi['nominal__avg']))
                    elif p.pk == 6:
                        isi = Harga.objects.filter(nama_sembako=i['nama_bahan'],nama_pasar=p.pk,tanggal__month=b,tanggal__year=i['tahun'],validasi=Harga.St.setuju).aggregate(Avg('nominal'))
                        if isi['nominal__avg'] != None:
                            ngalim.append(round(isi['nominal__avg']))
                    elif p.pk == 7:
                        isi = Harga.objects.filter(nama_sembako=i['nama_bahan'],nama_pasar=p.pk,tanggal__month=b,tanggal__year=i['tahun'],validasi=Harga.St.setuju).aggregate(Avg('nominal'))
                        if isi['nominal__avg'] != None:
                            bandar.append(round(isi['nominal__avg']))
                    elif p.pk == 8:
                        isi = Harga.objects.filter(nama_sembako=i['nama_bahan'],nama_pasar=p.pk,tanggal__month=b,tanggal__year=i['tahun'],validasi=Harga.St.setuju).aggregate(Avg('nominal'))
                        if isi['nominal__avg'] != None:
                            mrican.append(round(isi['nominal__avg']))
            elif nama_pasar == "1":
                isi = Harga.objects.filter(nama_sembako=i['nama_bahan'],nama_pasar=i['nama_pasar'],tanggal__month=b,tanggal__year=i['tahun'],validasi=Harga.St.setuju).aggregate(Avg('nominal'))
                if isi['nominal__avg'] != None:
                    setono.append(round(isi['nominal__avg']))
            elif nama_pasar == "2":
                isi = Harga.objects.filter(nama_sembako=i['nama_bahan'],nama_pasar=i['nama_pasar'],tanggal__month=b,tanggal__year=i['tahun'],validasi=Harga.St.setuju).aggregate(Avg('nominal'))
                if isi['nominal__avg'] != None:
                    pahing.append(round(isi['nominal__avg']))
            elif nama_pasar == "3":
                isi = Harga.objects.filter(nama_sembako=i['nama_bahan'],nama_pasar=i['nama_pasar'],tanggal__month=b,tanggal__year=i['tahun'],validasi=Harga.St.setuju).aggregate(Avg('nominal'))
                if isi['nominal__avg'] != None:
                    banjaran.append(round(isi['nominal__avg']))
            elif nama_pasar == "4":
                isi = Harga.objects.filter(nama_sembako=i['nama_bahan'],nama_pasar=i['nama_pasar'],tanggal__month=b,tanggal__year=i['tahun'],validasi=Harga.St.setuju).aggregate(Avg('nominal'))
                if isi['nominal__avg'] != None:
                    bawang.append(round(isi['nominal__avg']))
            elif nama_pasar == "5":
                isi = Harga.objects.filter(nama_sembako=i['nama_bahan'],nama_pasar=i['nama_pasar'],tanggal__month=b,tanggal__year=i['tahun'],validasi=Harga.St.setuju).aggregate(Avg('nominal'))
                if isi['nominal__avg'] != None:
                    ngronggo.append(round(isi['nominal__avg']))
            elif nama_pasar == "6":
                isi = Harga.objects.filter(nama_sembako=i['nama_bahan'],nama_pasar=i['nama_pasar'],tanggal__month=b,tanggal__year=i['tahun'],validasi=Harga.St.setuju).aggregate(Avg('nominal'))
                if isi['nominal__avg'] != None:
                    ngalim.append(round(isi['nominal__avg']))
            elif nama_pasar == "7":
                isi = Harga.objects.filter(nama_sembako=i['nama_bahan'],nama_pasar=i['nama_pasar'],tanggal__month=b,tanggal__year=i['tahun'],validasi=Harga.St.setuju).aggregate(Avg('nominal'))
                if isi['nominal__avg'] != None:
                    bandar.append(round(isi['nominal__avg']))
            elif nama_pasar == "8":
                isi = Harga.objects.filter(nama_sembako=i['nama_bahan'],nama_pasar=i['nama_pasar'],tanggal__month=b,tanggal__year=i['tahun'],validasi=Harga.St.setuju).aggregate(Avg('nominal'))
                if isi['nominal__avg'] != None:
                    mrican.append(round(isi['nominal__avg']))
        listpasar.append({"Setono":setono,"Pahing":pahing,"Banjaran":banjaran,"Bawang":bawang,"Ngronggo":ngronggo,"Ngalim":ngalim,"Bandar":bandar,"Mrican":mrican})             
    # Tabel
    tabel = []
    for a in ambil_Sembako:
        rata_rata = Harga.objects.filter(nama_sembako=a,tanggal=x,validasi=Harga.St.setuju).aggregate(Avg('nominal'))
        if rata_rata['nominal__avg']:
            tabel.append({"sembako":a,"harga":round(rata_rata['nominal__avg']),"satuan":a.satuan})
        else:
            tabel.append({"sembako":a,"harga":0})
    past30day = []
    for i in reversed(range(0,31)):
        kemarin = datetime.timedelta(days=i)
        a = x - kemarin
        past30day.append({"tanggal":a.date()})
    induk = [19,23,24,25]
    induk1 = []
    for j in induk:
        ibu = Sembako.objects.filter(pk=j)
        for y in ibu:
            induk1.append({"id":y.pk,"nama_sembako":y.jenis_sembako,"satuan":y.satuan})
    # Grafik 4 tabel 
    beras = []
    bramo = []
    bengawan = []
    menthik = []
    ir = []
    telur = []
    bloiler = []
    kampung = []
    cabe = []
    besar = []
    kriting = []
    rawit = []
    bawang = []
    merah = []
    putih = []
    for z in induk:
        sembako1 = Sembako.objects.filter(nama_sembako_id=z)
        for e in sembako1:
            for a in past30day:
                ambilinduk = Harga.objects.filter(tanggal=a['tanggal'],nama_sembako=e.pk,validasi=Harga.St.setuju).aggregate(Avg('nominal'))
                if e.pk == 28:
                    if ambilinduk['nominal__avg'] != None:
                        bramo.append({"tanggal":a['tanggal'],"nama":e,"harga":round(ambilinduk['nominal__avg'])})
                elif e.pk == 29:
                    if ambilinduk['nominal__avg'] != None:
                        bengawan.append({"tanggal":a['tanggal'],"nama":e,"harga":round(ambilinduk['nominal__avg'])})
                elif e.pk == 30:
                    if ambilinduk['nominal__avg'] != None:
                        menthik.append({"tanggal":a['tanggal'],"nama":e,"harga":round(ambilinduk['nominal__avg'])})
                elif e.pk == 31:
                    if ambilinduk['nominal__avg'] != None:
                        ir.append({"tanggal":a['tanggal'],"nama":e,"harga":round(ambilinduk['nominal__avg'])})
                elif e.pk == 37:
                    if ambilinduk['nominal__avg'] != None:
                        bloiler.append({"tanggal":a['tanggal'],"nama":e,"harga":round(ambilinduk['nominal__avg'])})
                elif e.pk == 38:
                    if ambilinduk['nominal__avg'] != None:
                        kampung.append({"tanggal":a['tanggal'],"nama":e,"harga":round(ambilinduk['nominal__avg'])})
                elif e.pk == 39:
                    if ambilinduk['nominal__avg'] != None:
                        besar.append({"tanggal":a['tanggal'],"nama":e,"harga":round(ambilinduk['nominal__avg'])})
                elif e.pk == 40:
                    if ambilinduk['nominal__avg'] != None:
                        kriting.append({"tanggal":a['tanggal'],"nama":e,"harga":round(ambilinduk['nominal__avg'])})
                elif e.pk == 41:
                    if ambilinduk['nominal__avg'] != None:
                        rawit.append({"tanggal":a['tanggal'],"nama":e,"harga":round(ambilinduk['nominal__avg'])})
                elif e.pk == 42:
                    if ambilinduk['nominal__avg'] != None:
                        merah.append({"tanggal":a['tanggal'],"nama":e,"harga":round(ambilinduk['nominal__avg'])})
                elif e.pk == 43:
                    if ambilinduk['nominal__avg'] != None:
                        putih.append({"tanggal":a['tanggal'],"nama":e,"harga":round(ambilinduk['nominal__avg'])})
    telur.append({"bloiler":bloiler,"kampung":kampung})
    cabe.append({"merah":besar,"rawit":rawit,"kriting":kriting})
    bawang.append({"merah":merah,"putih":putih})
    beras.append({"bramo":bramo,"bengawan":bengawan,"menthik":menthik,"ir":ir})
    return render(request,'admin_pasar/Grafik.html',{'pasar':ambil_pasar,'sembako':ambil_Sembako,'data':listpasar,'pencarian1':pencarian1,'tabel':tabel,"tanggal":past30day,"induk":induk1,"beras":beras,"telur":telur,"cabe":cabe,"bawang":bawang})

def maps(request):
    request.session['url'] = request.get_full_path()
    api_key = "pk.eyJ1IjoieXVzcmFuMTAzIiwiYSI6ImNrMWo0MDNpdjAyMDQzaHA0aHdkcjhtbTUifQ.2S8rcVwnT1x4-41R20FBWg"
    pasar = []
    harga = []
    x = datetime.datetime.now()
    list_pasar = Pasar.objects.all()
    nominal = 0
    for pasar1 in list_pasar:
        rata_rata = Harga.objects.filter(nama_pasar = pasar1,tanggal=x,validasi=Harga.St.setuju)
        koordinat = pasar1.lokasi
        lngraw , latraw = koordinat
        lat = str(latraw).replace(',','.')
        lng = str(lngraw).replace(',','.')
        pasar.append({"id":pasar1.id,"nama_pasar":pasar1.nama_pasar,"lat":lat,"lng":lng,"alamat":pasar1.alamat_pasar,"kel":pasar1.kelurahan,"kec":pasar1.kecamatan,"tlp":pasar1.notlp,"harga":rata_rata})
    return render(request,'admin_pasar/maps.html',{'api':api_key,'pasar':pasar,'time':x.date()})

class HargaList(generics.ListCreateAPIView):
    queryset = Harga.objects.filter(tanggal=datetime.date.today())
    serializer_class = HargaSerializer
