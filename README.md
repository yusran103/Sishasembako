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

1. py manage.py migrate
2. Truncate DB

jika ada data harga pasar
3. py manage.py loaddata datapasar1.json

jika data harga pasar kosong
3. py manage.py loaddata datapasar.json

4. py manage.py runserver
