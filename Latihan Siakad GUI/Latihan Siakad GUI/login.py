import tkinter as tk
from tkinter import ttk, messagebox

from config import *
from database import connect_db, prepare_login, authenticate


class LoginMixin:
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
