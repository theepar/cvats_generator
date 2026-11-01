from pathlib import Path
import pytest
from cv_parser import parse_cv_text
from cv_validation import validate_cv
from cv_generator import generate_cv
from ats_scorer import analyze_ats
from cv_exporter import cv_to_markdown, cv_to_json, get_sample_cv_data
from cv_ai import parse_free_text

def test_parse_contoh_cv():
    sample_file = Path(__file__).resolve().parent.parent / "contoh_cv.md"
    assert sample_file.exists()
    text = sample_file.read_text(encoding="utf-8")
    data = parse_cv_text(text)
    
    assert data["name"] == "Nama Lengkap"
    assert data["email"] == "nama@email.com"
    assert data["phone"] == "+62 812-3456-7890"
    assert len(data["education"]) == 1
    assert data["education"][0]["school"] == "Nama Universitas"
    assert len(data["experience"]) == 2
    assert len(data["organizations"]) == 1
    assert len(data["projects"]) == 2

def test_parse_empty_cv():
    with pytest.raises(ValueError):
        parse_cv_text("")

def test_validate_cv():
    data = {
        "name": "Budi Santoso",
        "email": "budi@santoso.com",
        "phone": "+628123456789",
        "summary": "Full stack developer.",
        "skills": "Python, React",
        "education": [{"school": "ITB", "degree": "Informatika", "dates": "2020 - 2024"}],
        "experience": [{"title": "Software Engineer", "company": "Tech Corp", "dates": "2024 - Sekarang"}],
        "organizations": [],
        "projects": []
    }
    validation = validate_cv(data)
    assert len(validation.missing) == 0
    assert len(validation.invalid) == 0

def test_generate_cv_pdf():
    data = get_sample_cv_data()
    # Test default order
    pdf_bytes = generate_cv(data, font_choice="Times New Roman", lang="id")
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF")

    # Test academic order
    academic_order = ["summary", "skills", "education", "experience", "organizations", "projects"]
    pdf_academic = generate_cv(data, font_choice="Arial", lang="en", section_order=academic_order)
    assert isinstance(pdf_academic, bytes)
    assert len(pdf_academic) > 500

def test_ats_scorer():
    data = get_sample_cv_data()
    job_desc = "We need a Full Stack Developer experienced with React, Python, Docker, and PostgreSQL."
    result = analyze_ats(data, job_desc)
    assert result.score > 70
    assert result.keyword_match_rate > 50.0
    assert "react" in result.matched_keywords
    assert "python" in result.matched_keywords
    assert result.quantifiable_metrics_count >= 1
    assert result.action_verbs_count >= 1

def test_cv_exporter():
    data = get_sample_cv_data()
    md = cv_to_markdown(data)
    assert "# Budi Pratama Santoso" in md
    assert "## Pendidikan" in md
    assert "## Pengalaman Kerja" in md
    
    parsed_back = parse_cv_text(md)
    assert parsed_back["name"] == data["name"]
    assert parsed_back["email"] == data["email"]
    
    json_str = cv_to_json(data)
    assert "Budi Pratama Santoso" in json_str

def test_parse_free_text_ai():
    raw_text = """
    Ahmad Rizky
    ahmad@example.com | +62 811-2233-4455
    Bandung, Indonesia

    Ringkasan Profil
    Software developer berpengalaman 4 tahun membangun aplikasi web dan cloud.

    Riwayat Pekerjaan
    Senior Frontend Engineer di PT Inovasi Digital
    Januari 2023 - Sekarang
    - Mengembangkan sistem dashboard dengan React dan Next.js
    - Meningkatkan performa aplikasi sebesar 30%

    Pendidikan
    Universitas Padjadjaran
    S1 Informatika | 2018 - 2022

    Keahlian
    TypeScript, Python, Docker, PostgreSQL, Tailwind CSS

    Prestasi dan Proyek
    Platform E-Commerce B2B
    - Mengintegrasikan sistem pembayaran Midtrans
    """
    parsed = parse_free_text(raw_text)
    assert parsed["name"] == "Ahmad Rizky"
    assert parsed["email"] == "ahmad@example.com"
    assert parsed["phone"] == "+62 811-2233-4455"
    assert len(parsed["experience"]) >= 1
    assert len(parsed["education"]) >= 1
    assert "Docker" in parsed["skills"]
