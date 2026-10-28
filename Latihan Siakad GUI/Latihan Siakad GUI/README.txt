SIAKAD — Kode terpisah per bagian dan per menu akademik

FILE UTAMA
- main.py

BAGIAN UMUM
- config.py
- database.py
- app_core.py
- login.py
- dashboard.py
- logout.py

HALAMAN DATA
- data_table_base.py : fungsi umum tabel data (cari/tambah/hapus/muat ulang)
- data_akademik.py   : penghubung untuk halaman data
- data_dosen.py     : menu Data Dosen
- data_mahasiswa.py : menu Data Mahasiswa
- jadwal_kuliah.py  : menu Jadwal Kuliah
- pembayaran_ukt.py: menu Pembayaran UKT
- data_krs.py       : menu Data KRS
- mata_kuliah.py    : menu Mata Kuliah

CARA MENJALANKAN
1. Ekstrak ZIP ke satu folder.
2. Pastikan MySQL/MariaDB aktif dan database `siakad` sudah tersedia.
3. Instal connector jika diperlukan:
   pip install mysql-connector-python
4. Jalankan dari terminal pada folder itu:
   python main.py

AKUN DEFAULT
Username: admin
Password: admin123

Catatan: Fitur tabel (cari, tambah, hapus, muat ulang) tetap menggunakan
logika tabel umum di data_table_base.py. Setiap menu akademik punya modul
sendiri agar mudah dipelajari dan dikembangkan.
