# Kerangka bersama untuk seluruh halaman data akademik.
# Tiap menu tabel mempunyai modul sendiri, misalnya data_dosen.py dan data_mahasiswa.py.
from data_table_base import DataTableBase


class DataAkademikMixin:
    def show_table(self, table, label):
        DataTableBase.show_table(self, table, label)
