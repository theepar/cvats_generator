# CV Generator

Aplikasi web sederhana untuk membuat CV dalam format PDF yang ATS-friendly.

## Fitur

- Buat CV dalam format PDF
- Support berbagai section: Personal Info, Education, Work Experience, Organizations, Skills, dan Achievements
- Fitur Multi-Bahasa (i18n): Pilihan bahasa UI dan bahasa output PDF (Bahasa Indonesia & English)
- Pilihan font: Times New Roman, Arial, atau Courier
- Tambah/hapus entry secara dinamis
- Preview PDF langsung di browser
- Download PDF hasil generate

## Cara Pakai

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Jalankan aplikasi:
```bash
streamlit run app.py
```

3. Buka browser di `http://localhost:8501`

4. Isi form sesuai data Anda

5. Klik "Buat CV" untuk generate PDF

## File Structure

- `app.py` - Aplikasi utama (template kosong)
- `cv_generator.py` - Logic untuk generate PDF
- `requirements.txt` - Dependencies Python

## Tech Stack

- **Streamlit** - Framework web app
- **fpdf** - Library untuk generate PDF

## Tips

- Gunakan Times New Roman untuk ATS tradisional
- Arial lebih modern dan mudah dibaca
- Isi data sejelas mungkin untuk hasil terbaik
