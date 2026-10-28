# Modul khusus menu Mata Kuliah.
from data_table_base import DataTableBase


class MataKuliahMixin:
    def show_mata_kuliah(self):
        DataTableBase.show_table(self, "mata_kuliah", "Mata Kuliah")
