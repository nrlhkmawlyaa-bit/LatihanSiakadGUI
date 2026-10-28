import tkinter as tk
from tkinter import ttk, messagebox

from config import *
from database import connect_db, prepare_login, authenticate


class DataTableBase:
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
