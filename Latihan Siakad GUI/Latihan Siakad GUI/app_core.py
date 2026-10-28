import tkinter as tk
from tkinter import ttk, messagebox

from config import *
from database import connect_db, prepare_login, authenticate


class CoreMixin:
    def __init__(self, root):
        self.root = root
        self.root.title("🎓 SIAKAD | Sistem Informasi Akademik")
        self.root.geometry("1200x750")
        self.root.minsize(1000, 650)
        self.root.configure(bg=BG_MAIN)
        self.password_col = None
        self.user = None
        self.setup_style()
        self.startup()

    def setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        
        style.configure(
            "Treeview", background=WHITE, foreground=TEXT_DARK,
            fieldbackground=WHITE, rowheight=38,
            font=("Segoe UI", 10), borderwidth=0
        )
        style.configure(
            "Treeview.Heading", background=PRIMARY_DARK, foreground=WHITE,
            font=("Segoe UI", 10, "bold"), padding=(12, 10), relief="flat"
        )
        style.map("Treeview", background=[("selected", PRIMARY_LIGHT)], foreground=[("selected", WHITE)])

    def button(self, parent, text, command, bg=PRIMARY, fg=WHITE, **kwargs):
        return tk.Button(
            parent, text=text, command=command, bg=bg, fg=fg,
            activebackground=PRIMARY_DARK, activeforeground=WHITE,
            relief="flat", bd=0, cursor="hand2",
            font=("Segoe UI", 10, "bold"), padx=16, pady=10, **kwargs
        )

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def startup(self):
        try:
            self.password_col = prepare_login()
            self.show_login()
        except Exception as exc:
            self.clear()
            self.root.configure(bg=BG_MAIN)
            panel = tk.Frame(self.root, bg=WHITE, padx=40, pady=40, highlightbackground=BORDER_COLOR, highlightthickness=1)
            panel.pack(fill="both", expand=True, padx=50, pady=50)
            tk.Label(panel, text="Koneksi Database Gagal", bg=WHITE, fg=RED, font=("Segoe UI", 20, "bold")).pack(anchor="w")
            tk.Label(panel, text="Pastikan MySQL di XAMPP aktif dan database `siakad` sudah ada.\n\nError: " + str(exc),
                     bg=WHITE, fg=TEXT_MUTED, font=("Segoe UI", 11), justify="left").pack(anchor="w", pady=20)
            self.button(panel, "Coba Lagi", self.startup).pack(anchor="w")
