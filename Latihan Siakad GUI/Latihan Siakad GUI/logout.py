import tkinter as tk
from tkinter import ttk, messagebox

from config import *
from database import connect_db, prepare_login, authenticate


class LogoutMixin:
    def logout(self):
        if messagebox.askyesno("Konfirmasi", "Yakin ingin keluar dari sistem?"):
            self.user = None
            self.show_login()
