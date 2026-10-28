# Modul khusus menu Data Dosen.
from data_table_base import DataTableBase


class DataDosenMixin:
    def show_dosen(self):
        DataTableBase.show_table(self, "dosen", "Data Dosen")
