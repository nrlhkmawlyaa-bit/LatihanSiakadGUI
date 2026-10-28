# Pengaturan utama aplikasi SIAKAD

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "siakad",
    "connection_timeout": 5,
}

BG_MAIN       = "#EDF2F7"
WHITE         = "#FFFFFF"
PRIMARY       = "#2B527B"
PRIMARY_DARK  = "#1F385C"
PRIMARY_LIGHT = "#4A7BB0"
TEXT_DARK     = "#1E293B"
TEXT_MUTED    = "#64748B"
BORDER_COLOR  = "#E2E8F0"
RED           = "#E11D48"

TABLES = [
    ("Dashboard", "Dashboard", "⌂"),
    ("Data Dosen", "dosen", "👨‍🏫"),
    ("Data Mahasiswa", "mahasiswa", "🎓"),
    ("Jadwal Kuliah", "jadwal_kuliah", "📅"),
    ("Pembayaran UKT", "pembayaran_ukt", "💳"),
    ("Data KRS", "krs", "📋"),
    ("Mata Kuliah", "mata_kuliah", "📚"),
]
