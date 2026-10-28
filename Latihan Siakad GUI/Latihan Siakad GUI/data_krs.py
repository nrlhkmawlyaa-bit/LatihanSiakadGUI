# Modul khusus menu Data KRS.
from data_table_base import DataTableBase


class DataKRSMixin:
    def show_krs(self):
        DataTableBase.show_table(self, "krs", "Data KRS")
