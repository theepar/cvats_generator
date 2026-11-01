# ATS CV Generator

Aplikasi Streamlit untuk membuat CV PDF dengan tata letak sederhana, rapi, dan optimal untuk sistem Applicant Tracking System (ATS). Data bisa diisi manual lewat formulir, dimuat dari profil contoh 1-klik, atau diimpor dari file Markdown (`.md`), teks (`.txt`), PDF (`.pdf`), dan Word (`.docx`).

## Fitur Utama

- **Pembuat CV PDF Standar ATS**: Tata letak satu kolom bersih, tanpa elemen grafis rumit yang membingungkan parser ATS.
- **Audit Skor ATS & Keyword Matcher**:
  - Skor kelayakan ATS (0 - 100).
  - Pencocokan kata kunci dengan deskripsi lowongan kerja target (*Job Description*).
  - Deteksi metrik pencapaian terukur (*quantifiable achievements*) dan *action verbs* aktif.
  - Rekomendasi perbaikan spesifik secara real-time.
- **Pilihan Urutan Tata Letak (Section Reordering)**:
  - *Standar*: Pengalaman kerja di atas (cocok untuk profesional).
  - *Akademik / Fresh Graduate*: Pendidikan di atas pengalaman kerja.
- **Impor Multi-Format**:
  - Mendukung berkas `.md`, `.txt`, `.pdf` (text-based), dan `.docx`.
  - Pilihan mode: **Format Template** (aturan Python tanpa AI) dan **AI Lokal Format Bebas** (scikit-learn offline).
- **Ekspor Fleksibel**:
  - Unduh **PDF** siap kirim ke rekruter.
  - Unduh **Markdown (`.md`)** dan **JSON (`.json`)** untuk backup dan diedit kembali kapan saja.
- **1-Klik Muat Contoh Profil**:
  - Tombol **Muat Contoh Profil Lengkap** di bagian impor untuk mencoba seluruh fitur aplikasi secara instan.
- **Dua Bahasa (Bilingual)**:
  - Antarmuka dan judul bagian PDF tersedia dalam Bahasa Indonesia dan Bahasa Inggris.
- **Pilihan Tipografi ATS**: Times New Roman, Arial, dan Courier.

## Instalasi

Pastikan Python 3.10+ terpasang di komputer Anda.

```bash
# 1. Pasang dependensi
pip install -r requirements.txt

# 2. Jalankan aplikasi Streamlit
streamlit run app.py
```

Aplikasi dapat diakses di browser melalui `http://localhost:8501`.

## Menjalankan Unit Tests

Proyek ini dilengkapi dengan unit test otomatis menggunakan `pytest`:

```bash
pytest tests/
```

## Struktur Proyek

```
ats_generator/
├── app.py                  # Aplikasi utama Streamlit (Formulir, Preview, Audit ATS)
├── ats_scorer.py           # Engine audit ATS, keyword matcher & STAR analyzer
├── cv_generator.py         # Generator PDF ATS berbasis FPDF2 dengan section ordering
├── cv_parser.py            # Parser teks/markdown berbasis aturan regex
├── cv_ai.py                # Classifier lokal scikit-learn untuk format teks bebas
├── cv_document_reader.py   # Reader dokumen (.md, .txt, .pdf, .docx)
├── cv_validation.py        # Validator data formulir & kelengkapan CV
├── cv_exporter.py          # Serializer data CV ke Markdown dan JSON
├── cv_import_ui.py         # Komponen UI impor dokumen & muat contoh profil
├── translations.py         # Kamus translasi i18n (Indonesia & English)
├── contoh_cv.md            # Contoh template teks CV Markdown
├── requirements.txt        # Daftar dependensi Python
└── tests/                  # Test suite otomatis (pytest)
    └── test_cv.py
```
