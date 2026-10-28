# Koneksi database dan fungsi autentikasi
import hashlib
import secrets

try:
    import mysql.connector
except ImportError:
    mysql = None

from config import DB_CONFIG

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
