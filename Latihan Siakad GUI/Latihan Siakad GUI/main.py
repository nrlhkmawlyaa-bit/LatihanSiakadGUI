# File utama untuk menjalankan aplikasi SIAKAD
import tkinter as tk

try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

from app_core import CoreMixin
from login import LoginMixin
from dashboard import DashboardMixin
from data_akademik import DataAkademikMixin
from data_dosen import DataDosenMixin
from data_mahasiswa import DataMahasiswaMixin
from jadwal_kuliah import JadwalKuliahMixin
from pembayaran_ukt import PembayaranUKTMixin
from data_krs import DataKRSMixin
from mata_kuliah import MataKuliahMixin
from logout import LogoutMixin


class SiakadApp(
    CoreMixin,
    LoginMixin,
    DashboardMixin,
    DataAkademikMixin,
    DataDosenMixin,
    DataMahasiswaMixin,
    JadwalKuliahMixin,
    PembayaranUKTMixin,
    DataKRSMixin,
    MataKuliahMixin,
    LogoutMixin,
):
    """Menggabungkan seluruh modul aplikasi SIAKAD."""
    pass


if __name__ == "__main__":
    root = tk.Tk()
    app = SiakadApp(root)
    root.mainloop()
