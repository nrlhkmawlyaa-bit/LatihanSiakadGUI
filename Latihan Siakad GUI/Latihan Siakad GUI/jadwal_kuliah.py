# Modul khusus menu Jadwal Kuliah.
from data_table_base import DataTableBase


class JadwalKuliahMixin:
    def show_jadwal_kuliah(self):
        DataTableBase.show_table(self, "jadwal_kuliah", "Jadwal Kuliah")
