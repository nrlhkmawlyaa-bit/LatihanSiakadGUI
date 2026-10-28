# Modul khusus menu Data Mahasiswa.
from data_table_base import DataTableBase


class DataMahasiswaMixin:
    def show_mahasiswa(self):
        DataTableBase.show_table(self, "mahasiswa", "Data Mahasiswa")
