# Tugas Akhir

Sistem Informasi Sembilan Harga Bahan Pokok di Kota Kediri

# Important

- Python 3.x

# Needed

```bash
pip install requirements.txt
```

# Step - Step

Langkah - langkah yang dibutuhkan seperti berikut:

1. Jalankan Migrasi
```bash
py manage.py migrate
```
2. Truncate DB
3. Load data
* jika ingin ada data harga pasar
```bash
py manage.py loaddata datapasar1.json
```
* jika ingin data harga pasar kosong
```bash
py manage.py loaddata datapasar.json
```
4. jalankan server
```bash
py manage.py runserver
```
