# Realtime Data Dashboard with Flask

Dashboard ini adalah aplikasi real-time untuk memantau data dari perangkat **333D01**, termasuk **Acceleration**, **Velocity**, dan **Demodulation**.

---

## 📋 Fitur

- **Realtime Monitoring**: Menampilkan data akselerasi, kecepatan, dan demodulasi secara real-time.
- **Flask Backend**: Backend berbasis Python menggunakan Flask.
- **Responsive Dashboard**: Antarmuka yang ramah pengguna dan responsif.

---

## 🚀 Instalasi

Ikuti langkah-langkah berikut untuk menginstal dan menjalankan proyek ini di mesin lokal Anda:

### 1. Clone repositori ini:

```bash
git clone https://github.com/eddyyucca/digiducer.git
cd digiducer
```

### 2. Pastikan Python dan pip telah terinstal

Periksa versi Python dan pip:

```bash
python --version
pip --version
```

Jika belum terinstal, unduh Python dari [python.org](https://www.python.org/).

### 3. Buat Virtual Environment (Opsional)

Untuk menjaga lingkungan pengembangan tetap bersih, buat virtual environment:

```bash
python -m venv venv
source venv/bin/activate # Linux/MacOS
venv\Scripts\activate # Windows
```

### 4. Instal dependensi Python

Instal semua pustaka yang diperlukan dari `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 5. Jalankan server Flask

Jalankan aplikasi dengan perintah berikut:

```bash
python server.py
```

---

## 📊 Akses Dashboard

Setelah server berjalan, buka browser Anda dan akses:

[http://127.0.0.1:5000/](http://127.0.0.1:5000/)

---

## 📂 Struktur Proyek

```plaintext
project-folder/
├── server.py          # Server Flask utama
├── requirements.txt   # Daftar pustaka Python
├── templates/         # Folder untuk file HTML
│   └── index.html     # Dashboard utama
├── static/            # Folder untuk file statis (CSS, JS, dll.)
│   └── css/           # Folder untuk file CSS (opsional)
│       └── style.css  # Gaya tambahan (opsional)
```

---

## 🛠️ Teknologi yang Digunakan

- **Python**: Bahasa pemrograman utama.
- **Flask**: Framework untuk membangun backend web.
- **Sounddevice**: Untuk menangkap data audio dari perangkat.
- **Scipy**: Untuk pengolahan sinyal digital.
- **HTML/CSS**: Untuk desain dan antarmuka pengguna.

---

## 📄 Lisensi

Proyek ini dilisensikan di bawah MIT License. Silakan lihat file [LICENSE](LICENSE) untuk detailnya.
