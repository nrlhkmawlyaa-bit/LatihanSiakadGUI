import tkinter as tk
from tkinter import ttk, messagebox

from config import *
from database import connect_db, prepare_login, authenticate
from data_dosen import DataDosenMixin
from data_mahasiswa import DataMahasiswaMixin
from jadwal_kuliah import JadwalKuliahMixin
from pembayaran_ukt import PembayaranUKTMixin
from data_krs import DataKRSMixin
from mata_kuliah import MataKuliahMixin


class DashboardMixin:
    def show_dashboard(self):
        self.clear()
        self.root.configure(bg=BG_MAIN)

        shell = tk.Frame(self.root, bg=BG_MAIN)
        shell.pack(fill="both", expand=True)

        topnav = tk.Frame(shell, bg=PRIMARY_DARK, padx=25, pady=16)
        topnav.pack(side="top", fill="x")

        brand_frame = tk.Frame(topnav, bg=PRIMARY_DARK)
        brand_frame.pack(side="left", padx=(0, 25))
        tk.Label(brand_frame, text="🎓 SIAKAD", bg=PRIMARY_DARK, fg=WHITE, font=("Segoe UI", 16, "bold")).pack(anchor="w")

        self.nav_buttons_frame = tk.Frame(topnav, bg=PRIMARY_DARK)
        self.nav_buttons_frame.pack(side="left")
        self.nav_buttons = {}

        for label, table_key, icon in TABLES:
            btn = tk.Button(
                self.nav_buttons_frame, text=f"{icon}  {label}",
                command=lambda t=table_key, l=label: self.switch_to_table(t, l),
                bg=PRIMARY_DARK, fg="#CBD5E1", activebackground=PRIMARY,
                activeforeground=WHITE, relief="flat", bd=0, cursor="hand2",
                padx=14, pady=8, font=("Segoe UI", 9, "bold")
            )
            btn.pack(side="left", padx=5)
            self.nav_buttons[table_key] = btn

        right_menu = tk.Frame(topnav, bg=PRIMARY_DARK)
        right_menu.pack(side="right", padx=(20, 0))

        user_text = (self.user or {}).get("username", "admin").upper()
        tk.Label(right_menu, text=f"👤 {user_text}", bg=PRIMARY_DARK, fg=WHITE, font=("Segoe UI", 9, "bold")).pack(side="left", padx=12)

        tk.Button(
            right_menu, text="Keluar", command=self.logout,
            bg="#1E293B", fg=WHITE, activebackground=RED, activeforeground=WHITE,
            relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 9, "bold"),
            padx=12, pady=7
        ).pack(side="left")

        self.content = tk.Frame(shell, bg=BG_MAIN, padx=35, pady=25)
        self.content.pack(fill="both", expand=True)
        self.show_home()

    def switch_to_table(self, table, label):
        if table == "Dashboard":
            self.show_home()
        else:
            handlers = {
                "dosen": self.show_dosen,
                "mahasiswa": self.show_mahasiswa,
                "jadwal_kuliah": self.show_jadwal_kuliah,
                "pembayaran_ukt": self.show_pembayaran_ukt,
                "krs": self.show_krs,
                "mata_kuliah": self.show_mata_kuliah,
            }
            handler = handlers.get(table)
            if handler:
                handler()

    def add_nav(self, text, command, key):
        btn = tk.Button(
            self.nav, text=text, command=command, anchor="w",
            bg=PRIMARY_DARK, fg="#E2E8F0", activebackground=PRIMARY_LIGHT,
            activeforeground=WHITE, relief="flat", bd=0, cursor="hand2",
            padx=14, pady=10, font=("Segoe UI", 10)
        )
        btn.pack(fill="x", pady=3, padx=4)
        self.nav_buttons[key] = btn

    def active_nav(self, key):
        for name, btn in self.nav_buttons.items():
            is_active = (name == key)
            btn.configure(
                bg=PRIMARY if is_active else PRIMARY_DARK,
                fg=WHITE if is_active else "#94A3B8",
                relief="solid" if is_active else "flat",
                bd=1 if is_active else 0,
                highlightbackground=PRIMARY_LIGHT if is_active else PRIMARY_DARK
            )

    def clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def show_home(self):
        self.active_nav("Dashboard")
        self.clear_content()

        decor = tk.Frame(self.content, bg=PRIMARY_DARK, padx=20, pady=12)
        decor.pack(fill="x", pady=(0, 18))
        decor_left = tk.Frame(decor, bg=PRIMARY_DARK)
        decor_left.pack(side="left", fill="x", expand=True)
        tk.Label(
            decor_left, text="🎓  PORTAL AKADEMIK SIAKAD",
            bg=PRIMARY_DARK, fg=WHITE, font=("Segoe UI", 13, "bold")
        ).pack(anchor="w")
        tk.Label(
            decor_left, text="Kelola informasi akademik dengan lebih mudah dan teratur.",
            bg=PRIMARY_DARK, fg="#DBEAFE", font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(4, 0))
        decor_right = tk.Frame(decor, bg=PRIMARY_DARK)
        decor_right.pack(side="right", padx=(18, 8))
        tk.Label(
            decor_right, text="🎓", bg=PRIMARY_DARK, fg=WHITE,
            font=("Segoe UI", 25)
        ).pack(side="left", padx=7)

        tk.Label(self.content, text="Ringkasan Data Akademik", bg=BG_MAIN, fg=TEXT_DARK, font=("Segoe UI", 20, "bold")).pack(anchor="w")
        tk.Label(self.content, text="Overview jumlah data terdaftar di dalam database siakad secara real-time.", bg=BG_MAIN, fg=TEXT_MUTED, font=("Segoe UI", 10)).pack(anchor="w", pady=(2, 20))

        cards = tk.Frame(self.content, bg=BG_MAIN)
        cards.pack(fill="x")

        accent_colors = ["#1E3A8A", "#2563EB", "#0284C7", "#4F46E5", "#7C3AED", "#059669"]
        table_meta = {
            "dosen": {"icon": "👨‍🏫 ", "desc": "Total dosen pengajar aktif"},
            "mahasiswa": {"icon": "🎓 ", "desc": "Total mahasiswa terdaftar"},
            "jadwal_kuliah": {"icon": "📅 ", "desc": "Jadwal perkuliahan aktif"},
            "pembayaran_ukt": {"icon": "💳 ", "desc": "Rekap transaksi UKT"},
            "krs": {"icon": "📋 ", "desc": "Kartu Rencana Studi mahasiswa"},
            "mata_kuliah": {"icon": "📚 ", "desc": "Daftar mata kuliah tersedia"}
        }

        count_labels = []
        tables_only = [t for _, t, _ in TABLES if t != "Dashboard"]
        labels_only = [l for l, t, _ in TABLES if t != "Dashboard"]

        for i, table in enumerate(tables_only):
            label_name = labels_only[i]
            card = tk.Frame(cards, bg=WHITE, padx=22, pady=18, highlightbackground=BORDER_COLOR, highlightthickness=1)
            card.grid(row=i // 3, column=i % 3, sticky="nsew", padx=10, pady=10)

            tk.Frame(card, bg=accent_colors[i % len(accent_colors)], height=4).pack(fill="x", pady=(0, 12))

            meta = table_meta.get(table, {"icon": "📊 ", "desc": "Data tersimpan"})
            tk.Label(card, text=(meta["icon"] + label_name).upper(), bg=WHITE, fg=TEXT_MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w")
            
            count = tk.Label(card, text="—", bg=WHITE, fg=TEXT_DARK, font=("Segoe UI", 26, "bold"))
            count.pack(anchor="w", pady=(4, 0))

            tk.Label(card, text=meta["desc"], bg=WHITE, fg=TEXT_MUTED, font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 10))
            tk.Frame(card, bg="#F1F5F9", height=1).pack(fill="x", pady=(4, 8))

            btn_detail = tk.Label(card, text="Kelola Data ➔", bg=WHITE, fg=PRIMARY, font=("Segoe UI", 9, "bold"), cursor="hand2")
            btn_detail.pack(anchor="w")
            btn_detail.bind("<Button-1>", lambda e, t=table, l=label_name: self.switch_to_table(t, l))

            count_labels.append((table, count))

        for col in range(3):
            cards.grid_columnconfigure(col, weight=1, uniform="card")

        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("SHOW TABLES")
            existing = {r[0].lower() for r in cur.fetchall()}
            for table, label in count_labels:
                if table.lower() in existing:
                    cur.execute(f"SELECT COUNT(*) FROM `{table}`")
                    res = cur.fetchone()
                    label.configure(text=str(res[0] if res else 0))
                else:
                    label.configure(text="0")
            cur.close()
            conn.close()
        except Exception as e:
            print("Error:", e)
            for _, label in count_labels:
                label.configure(text="0")
