import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
import secrets

try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

try:
    import mysql.connector
except ImportError:
    mysql = None

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "siakad",
    "connection_timeout": 5,
}

BG_MAIN     = "#EDF2F7"
WHITE       = "#FFFFFF"
PRIMARY     = "#2B527B"
PRIMARY_DARK= "#1F385C"
PRIMARY_LIGHT="#4A7BB0"
TEXT_DARK   = "#1E293B"
TEXT_MUTED  = "#64748B"
BORDER_COLOR= "#E2E8F0"
RED         = "#E11D48"

TABLES = [
    ("Dashboard", "Dashboard", "⌂"),
    ("Data Dosen", "dosen", "👨‍🏫"),
    ("Data Mahasiswa", "mahasiswa", "🎓"),
    ("Jadwal Kuliah", "jadwal_kuliah", "📅"),
    ("Pembayaran UKT", "pembayaran_ukt", "💳"),
    ("Data KRS", "krs", "📋"),
    ("Mata Kuliah", "mata_kuliah", "📚"),
]

def connect_db():
    if mysql is None:
        raise RuntimeError("Library MySQL belum terpasang.")
    return mysql.connector.connect(**DB_CONFIG)

def hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 150_000).hex()
    return salt + ":" + digest

def verify_password(password, stored):
    if stored is None:
        return False
    stored = str(stored)
    if ":" not in stored:
        return secrets.compare_digest(password, stored)
    salt, expected = stored.split(":", 1)
    actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 150_000).hex()
    return secrets.compare_digest(actual, expected)

def prepare_login():
    conn = connect_db()
    cur = conn.cursor()
    try:
        cur.execute("SHOW TABLES LIKE 'users'")
        if cur.fetchone() is None:
            cur.execute("""
                CREATE TABLE users (
                    id_user INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    nama_lengkap VARCHAR(100) DEFAULT 'Administrator',
                    role VARCHAR(30) DEFAULT 'admin'
                )
            """)
            conn.commit()

        cur.execute("SHOW COLUMNS FROM users")
        columns = {row[0].lower() for row in cur.fetchall()}
        password_col = "password_hash" if "password_hash" in columns else "password"

        cur.execute("SELECT * FROM users WHERE username=%s LIMIT 1", ("admin",))
        if cur.fetchone() is None:
            insert_cols = ["username", password_col]
            values = ["admin", hash_password("admin123")]
            if "nama_lengkap" in columns:
                insert_cols.append("nama_lengkap")
                values.append("Administrator")
            if "role" in columns:
                insert_cols.append("role")
                values.append("admin")
            sql_cols = ", ".join(f"`{c}`" for c in insert_cols)
            marks = ", ".join(["%s"] * len(values))
            cur.execute(f"INSERT INTO users ({sql_cols}) VALUES ({marks})", tuple(values))
            conn.commit()
        return password_col
    finally:
        cur.close()
        conn.close()

def authenticate(username, password, password_col):
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM users WHERE username=%s LIMIT 1", (username.strip(),))
        row = cur.fetchone()
        if row and verify_password(password, row.get(password_col)):
            return row
        return None
    finally:
        cur.close()
        conn.close()

class SiakadApp:
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

    def show_login(self):
        self.clear()
        self.root.configure(bg=BG_MAIN)

        card = tk.Frame(self.root, bg=WHITE, width=800, height=700, highlightbackground=BORDER_COLOR, highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        inner_frame = tk.Frame(card, bg=WHITE)
        inner_frame.pack(fill="both", expand=True, padx=55, pady=40)

        tk.Label(inner_frame, text="🎓", bg=WHITE, fg=PRIMARY, font=("Segoe UI", 36)).pack()
        tk.Label(inner_frame, text="SIAKAD", bg=WHITE, fg=PRIMARY_DARK, font=("Segoe UI", 22, "bold")).pack(pady=(2, 0))
        tk.Label(inner_frame, text="Sistem Informasi Akademik", bg=WHITE, fg=TEXT_MUTED, font=("Segoe UI", 10)).pack(pady=(0, 15))

        tk.Frame(inner_frame, bg=BORDER_COLOR, height=1).pack(fill="x", pady=(0, 20))

        tk.Label(inner_frame, text="Masukkan Akun Anda", bg=WHITE, fg=TEXT_DARK, font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 15))

        form_frame = tk.Frame(inner_frame, bg=WHITE)
        form_frame.pack(fill="x", pady=(0, 10))

        tk.Label(form_frame, text="Username", bg=WHITE, fg=TEXT_MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))
        username_var = tk.StringVar(value="admin")
        ent_user = tk.Entry(form_frame, textvariable=username_var, font=("Segoe UI", 11), bg="#F8FAFC", fg=TEXT_DARK, relief="solid", bd=1)
        ent_user.pack(fill="x", ipady=7, ipadx=10, pady=(0, 10))

        tk.Label(form_frame, text="Password", bg=WHITE, fg=TEXT_MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))
        password_var = tk.StringVar()
        ent_pass = tk.Entry(form_frame, textvariable=password_var, show="●", font=("Segoe UI", 11), bg="#F8FAFC", fg=TEXT_DARK, relief="solid", bd=1)
        ent_pass.pack(fill="x", ipady=7, ipadx=10, pady=(0, 5))

        bottom_row = tk.Frame(inner_frame, bg=WHITE)
        bottom_row.pack(fill="x", pady=(2, 12))

        show_var = tk.BooleanVar(value=False)
        def toggle_pass():
            ent_pass.configure(show="" if show_var.get() else "●")

        tk.Checkbutton(bottom_row, text="Tampilkan Password", variable=show_var, command=toggle_pass, bg=WHITE, fg=TEXT_MUTED, activebackground=WHITE, font=("Segoe UI", 9)).pack(side="left")

        status_var = tk.StringVar()
        tk.Label(inner_frame, textvariable=status_var, bg=WHITE, fg=RED, font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 5))

        def do_login(event=None):
            if not username_var.get().strip() or not password_var.get():
                status_var.set("Username dan Password wajib diisi!")
                return
            try:
                row = authenticate(username_var.get(), password_var.get(), self.password_col)
                if row:
                    self.user = row
                    self.show_dashboard()
                else:
                    status_var.set("Login gagal! Periksa username/password.")
                    ent_pass.focus_set()
            except Exception as exc:
                status_var.set(f"Gagal login: {exc}")

        self.button(inner_frame, text="➔  Login", command=do_login, bg=PRIMARY, fg=WHITE).pack(fill="x", pady=(2, 8))
        
        tk.Label(inner_frame, text="Default Akun: admin / admin123", bg=WHITE, fg=TEXT_MUTED, font=("Segoe UI", 9)).pack(anchor="w")

        ent_user.bind("<Return>", lambda e: ent_pass.focus_set())
        ent_pass.bind("<Return>", do_login)
        ent_user.focus_set()

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
            self.show_table(table, label)

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
                
    def show_table(self, table, label):
        self.active_nav(table)
        self.clear_content()

        tk.Label(self.content, text=label, bg=BG_MAIN, fg=TEXT_DARK, font=("Segoe UI", 18, "bold")).pack(anchor="w")
        tk.Label(self.content, text=f"Daftar data tersimpan pada tabel `{table}`", bg=BG_MAIN, fg=TEXT_MUTED, font=("Segoe UI", 10)).pack(anchor="w", pady=(2, 15))

        tools = tk.Frame(self.content, bg=BG_MAIN)
        tools.pack(fill="x", pady=(0, 12))

        search_var = tk.StringVar()
        entry_search = tk.Entry(
            tools, textvariable=search_var, font=("Segoe UI", 10),
            bg=WHITE, fg=TEXT_DARK, relief="solid", bd=1, highlightthickness=0
        )
        entry_search.pack(side="left", ipady=7, ipadx=12, padx=(0, 10))

        self.button(tools, "🔍 Cari Data", lambda: render(search_var.get()), bg=PRIMARY).pack(side="left", padx=(0, 6))
        self.button(tools, "＋ Tambah Data", lambda: add_data(), bg="#15803D").pack(side="left", padx=(0, 6))
        self.button(tools, "🗑 Hapus Data", lambda: delete_data(), bg=RED).pack(side="left", padx=(0, 6))
        self.button(tools, "↻ Muat Ulang", lambda: load(), bg=PRIMARY_LIGHT).pack(side="left")

        table_frame = tk.Frame(self.content, bg=WHITE, highlightbackground=BORDER_COLOR, highlightthickness=1)
        table_frame.pack(fill="both", expand=True)

        tree = ttk.Treeview(table_frame, show="headings")
        vs = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        hs = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)

        tree.grid(row=0, column=0, sticky="nsew")
        vs.grid(row=0, column=1, sticky="ns")
        hs.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        tree.tag_configure("evenrow", background=WHITE)
        tree.tag_configure("oddrow", background="#F8FAFC")

        info_var = tk.StringVar(value="Memuat data...")
        tk.Label(self.content, textvariable=info_var, bg=BG_MAIN, fg=TEXT_MUTED, font=("Segoe UI", 9, "italic")).pack(anchor="w", pady=(10, 0))

        all_rows = []

        def render(filter_text=""):
            tree.delete(*tree.get_children())
            needle = filter_text.strip().lower()
            filtered = [
                row for row in all_rows
                if not needle or any(needle in ("" if v is None else str(v)).lower() for v in row)
            ]
            for i, row in enumerate(filtered):
                tag = "evenrow" if i % 2 == 0 else "oddrow"
                formatted_values = ["" if v is None else str(v) for v in row]
                tree.insert("", "end", values=formatted_values, tags=(tag,))
            info_var.set(f"Menampilkan {len(filtered)} dari total {len(all_rows)} baris data.")

        def load():
            nonlocal all_rows
            try:
                conn = connect_db()
                cur = conn.cursor()
                cur.execute("SHOW TABLES")
                existing = {r[0] for r in cur.fetchall()}
                if table not in existing:
                    cur.close()
                    conn.close()
                    tree.delete(*tree.get_children())
                    info_var.set(f"Tabel `{table}` belum tersedia di database.")
                    return

                cur.execute(f"SELECT * FROM `{table}` LIMIT 5000")
                columns = [d[0] for d in cur.description]
                all_rows = cur.fetchall()
                cur.close()
                conn.close()

                tree["columns"] = columns
                for col in columns:
                    heading_text = col.replace("_", " ").title()
                    tree.heading(col, text=heading_text, anchor="w")
                    max_len = max([len(str(r[columns.index(col)] or "")) for r in all_rows] + [len(heading_text)])
                    col_width = max(130, min(300, max_len * 11 + 40))
                    tree.column(col, width=col_width, minwidth=100, anchor="w", stretch=True)

                render(search_var.get())
            except Exception as exc:
                info_var.set("Gagal memuat data dari database.")
                messagebox.showerror("Error", str(exc))

        def delete_data():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning(
                    "Pilih Data", "Pilih satu baris data pada tabel yang ingin dihapus.",
                    parent=self.root
                )
                return

            selected_values = tree.item(selected[0], "values")
            displayed_columns = list(tree["columns"])
            row_data = dict(zip(displayed_columns, selected_values))

            try:
                conn = connect_db()
                cur = conn.cursor()
                cur.execute(f"SHOW COLUMNS FROM `{table}`")
                schema = cur.fetchall()
                primary_keys = [col[0] for col in schema if str(col[3]).upper() == "PRI"]

                if not primary_keys:
                    cur.close()
                    conn.close()
                    messagebox.showerror(
                        "Tidak Bisa Menghapus",
                        f"Tabel `{table}` tidak memiliki primary key. "
                        "Tambahkan primary key terlebih dahulu agar penghapusan data aman.",
                        parent=self.root
                    )
                    return

                missing_keys = [key for key in primary_keys if key not in row_data]
                if missing_keys:
                    cur.close()
                    conn.close()
                    messagebox.showerror(
                        "Gagal Menghapus", "Kolom primary key tidak ditemukan pada tampilan tabel.",
                        parent=self.root
                    )
                    return

                key_summary = "\n".join(f"{key}: {row_data[key]}" for key in primary_keys)
                confirmed = messagebox.askyesno(
                    "Konfirmasi Hapus",
                    f"Yakin ingin menghapus data yang dipilih dari tabel `{table}`?\n\n"
                    f"Identitas data:\n{key_summary}\n\n"
                    "Data yang sudah dihapus tidak dapat dikembalikan.",
                    icon="warning",
                    parent=self.root
                )
                if not confirmed:
                    cur.close()
                    conn.close()
                    return

                where_clause = " AND ".join(f"`{key}` = %s" for key in primary_keys)
                key_values = tuple(row_data[key] for key in primary_keys)
                cur.execute(
                    f"DELETE FROM `{table}` WHERE {where_clause}",
                    key_values
                )
                deleted_count = cur.rowcount
                conn.commit()
                cur.close()
                conn.close()

                if deleted_count:
                    load()
                    messagebox.showinfo("Berhasil", "Data berhasil dihapus.", parent=self.root)
                else:
                    messagebox.showwarning(
                        "Data Tidak Ditemukan", "Data tidak ditemukan atau sudah dihapus.",
                        parent=self.root
                    )
            except Exception as exc:
                try:
                    conn.rollback()
                    conn.close()
                except Exception:
                    pass
                messagebox.showerror(
                    "Gagal Menghapus Data",
                    "Data tidak berhasil dihapus. Jika data terhubung dengan tabel lain, "
                    "periksa relasi foreign key terlebih dahulu.\n\n" + str(exc),
                    parent=self.root
                )

        def add_data():
            dialog = tk.Toplevel(self.root)
            dialog.title(f"Tambah Data - {label}")
            dialog.geometry("560x650")
            dialog.minsize(460, 400)
            dialog.configure(bg=BG_MAIN)
            dialog.transient(self.root)
            dialog.grab_set()

            header = tk.Frame(dialog, bg=PRIMARY_DARK, padx=22, pady=16)
            header.pack(fill="x")
            tk.Label(
                header, text=f"Tambah {label}", bg=PRIMARY_DARK,
                fg=WHITE, font=("Segoe UI", 16, "bold")
            ).pack(anchor="w")
            tk.Label(
                header, text="Isi kolom yang diperlukan, lalu klik Simpan.",
                bg=PRIMARY_DARK, fg="#DBEAFE", font=("Segoe UI", 9)
            ).pack(anchor="w", pady=(4, 0))

            outer = tk.Frame(dialog, bg=WHITE, padx=20, pady=16)
            outer.pack(fill="both", expand=True, padx=16, pady=16)

            canvas = tk.Canvas(outer, bg=WHITE, highlightthickness=0)
            scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
            form = tk.Frame(canvas, bg=WHITE)
            form.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=form, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            try:
                conn = connect_db()
                cur = conn.cursor()
                cur.execute(f"SHOW COLUMNS FROM `{table}`")
                schema = cur.fetchall()
                cur.close()
                conn.close()
            except Exception as exc:
                dialog.destroy()
                messagebox.showerror("Gagal", f"Tidak dapat membaca struktur tabel.\n{exc}")
                return

            fields = []
            for col in schema:
                col_name, col_type, nullable, key, default, extra = col[:6]
                if "auto_increment" in str(extra).lower():
                    continue
                required = nullable == "NO" and default is None
                tk.Label(
                    form, text=col_name.replace("_", " ").title()
                    + (" *" if required else ""),
                    bg=WHITE, fg=TEXT_DARK, font=("Segoe UI", 10, "bold")
                ).pack(anchor="w", pady=(8, 3))
                var = tk.StringVar()
                entry = tk.Entry(
                    form, textvariable=var, font=("Segoe UI", 10),
                    bg="#F8FAFC", fg=TEXT_DARK, relief="solid", bd=1
                )
                entry.pack(fill="x", ipady=6, pady=(0, 4))
                fields.append({
                    "name": col_name, "var": var, "required": required,
                    "default": default, "entry": entry
                })

            if not fields:
                tk.Label(
                    form, text="Tidak ada kolom yang bisa diisi.",
                    bg=WHITE, fg=TEXT_MUTED
                ).pack(anchor="w", pady=10)

            footer = tk.Frame(dialog, bg=BG_MAIN, padx=16, pady=12)
            footer.pack(fill="x")

            def save_data():
                columns, values = [], []
                for field in fields:
                    value = field["var"].get().strip()
                    if value == "":
                        if field["required"]:
                            messagebox.showwarning(
                                "Data belum lengkap",
                                f"Kolom {field['name']} wajib diisi.",
                                parent=dialog
                            )
                            field["entry"].focus_set()
                            return
                        # Kolom kosong yang punya default dibiarkan memakai default MySQL.
                        if field["default"] is not None:
                            continue
                        # Kolom opsional tanpa default disimpan sebagai NULL.
                        columns.append(field["name"])
                        values.append(None)
                    else:
                        columns.append(field["name"])
                        values.append(value)

                if not columns:
                    messagebox.showwarning("Data kosong", "Isi setidaknya satu kolom.", parent=dialog)
                    return

                try:
                    conn = connect_db()
                    cur = conn.cursor()
                    col_sql = ", ".join(f"`{name}`" for name in columns)
                    placeholders = ", ".join(["%s"] * len(values))
                    cur.execute(
                        f"INSERT INTO `{table}` ({col_sql}) VALUES ({placeholders})",
                        tuple(values)
                    )
                    conn.commit()
                    cur.close()
                    conn.close()
                    dialog.destroy()
                    load()
                    messagebox.showinfo("Berhasil", "Data berhasil ditambahkan ke database.")
                except Exception as exc:
                    try:
                        conn.rollback()
                        conn.close()
                    except Exception:
                        pass
                    messagebox.showerror(
                        "Gagal menyimpan data",
                        "Data belum berhasil disimpan. Periksa kembali isi kolom "
                        "dan relasi data (misalnya ID dosen/mahasiswa).\n\n" + str(exc),
                        parent=dialog
                    )

            self.button(footer, "Batal", dialog.destroy, bg="#64748B").pack(side="right", padx=(8, 0))
            self.button(footer, "Simpan Data", save_data, bg="#15803D").pack(side="right")

        entry_search.bind("<Return>", lambda e: render(search_var.get()))
        load()

    def logout(self):
        if messagebox.askyesno("Konfirmasi", "Yakin ingin keluar dari sistem?"):
            self.user = None
            self.show_login()

if __name__ == "__main__":
    root = tk.Tk()
    app = SiakadApp(root)
    root.mainloop()