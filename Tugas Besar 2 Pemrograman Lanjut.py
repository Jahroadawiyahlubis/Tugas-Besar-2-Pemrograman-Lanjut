import sqlite3
import logging

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Kelas untuk menangani pengecualian HTTP
class HTTPException(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"HTTP {self.status_code}: {self.message}"

# Kelas untuk representasi objek Buku
class Buku:
    def __init__(self, judul, penulis, penerbit, tahun_terbit, konten, iktisar):
        self.judul = judul
        self.penulis = penulis
        self.penerbit = penerbit
        self.tahun_terbit = tahun_terbit
        self.konten = konten
        self.iktisar = iktisar

    def read(self, halaman):
        if halaman > len(self.konten):
            halaman = len(self.konten)
        for i in range(halaman):
            print(f"Bab {i+1}: {self.konten[i]}")

    def __str__(self):
        return f"{self.judul} by {self.penulis}"

    def print_info(self):
        print(f"Judul: {self.judul}")
        print(f"Penulis: {self.penulis}")
        print(f"Penerbit: {self.penerbit}")
        print(f"Tahun Terbit: {self.tahun_terbit}")
        print("Konten:")
        self.read(len(self.konten))
        print(f"Iktisar: {self.iktisar}")

# Fungsi untuk membuat tabel buku dalam database SQLite
def setup_database():
    conn = sqlite3.connect('perpustakaan.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS buku (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    judul TEXT,
                    penulis TEXT,
                    penerbit TEXT,
                    tahun_terbit INTEGER,
                    konten TEXT,
                    iktisar TEXT
                )''')
    conn.commit()
    conn.close()

# Fungsi untuk mengambil buku berdasarkan judul dari database SQLite
def get_buku(judul):
    conn = sqlite3.connect('perpustakaan.db')
    c = conn.cursor()
    c.execute("SELECT * FROM buku WHERE judul=?", (judul,))
    buku_data = c.fetchone()
    conn.close()
    if buku_data:
        return Buku(buku_data[1], buku_data[2], buku_data[3], buku_data[4], buku_data[5].split('|'), buku_data[6])
    else:
        return None

# Fungsi untuk menyimpan buku ke dalam database SQLite
def post_buku(buku):
    conn = sqlite3.connect('perpustakaan.db')
    c = conn.cursor()
    c.execute("INSERT INTO buku (judul, penulis, penerbit, tahun_terbit, konten, iktisar) VALUES (?, ?, ?, ?, ?, ?)",
              (buku.judul, buku.penulis, buku.penerbit, buku.tahun_terbit, '|'.join(buku.konten), buku.iktisar))
    conn.commit()
    conn.close()

# Setup database saat aplikasi dijalankan
setup_database()

# Contoh penggunaan
try:
    buku_baru = Buku(
        judul="Mathematics for Machine Learning",
        penulis="Marc Peter Deisenroth",
        penerbit="Cambridge University Press",
        tahun_terbit="2020",
        konten=["Introduction", "Linear Algebra", "Calculus", "Probability", "Machine Learning Basics"],
        iktisar="Buku ini memberikan dasar matematika yang diperlukan untuk memahami machine learning."
    )
    post_buku(buku_baru)
    logger.info("Buku berhasil disimpan.")
except Exception as e:
    logger.error(f"Terjadi kesalahan: {e}")
    raise HTTPException(500, "Terjadi kesalahan saat menyimpan buku.")

# Mengambil buku dari database
try:
    buku_diambil = get_buku("Mathematics for Machine Learning")
    if buku_diambil:
        buku_diambil.print_info()  # Cetak informasi lengkap buku
    else:
        raise HTTPException(404, "Buku tidak ditemukan.")
except HTTPException as e:
    logger.error(e)

