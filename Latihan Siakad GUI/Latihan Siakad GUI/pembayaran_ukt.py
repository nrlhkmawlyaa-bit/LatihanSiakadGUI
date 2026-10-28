# Modul khusus menu Pembayaran UKT.
from data_table_base import DataTableBase


class PembayaranUKTMixin:
    def show_pembayaran_ukt(self):
        DataTableBase.show_table(self, "pembayaran_ukt", "Pembayaran UKT")
