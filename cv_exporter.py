import json
from typing import Dict, Any

def cv_to_markdown(data: Dict[str, Any]) -> str:
    """Export CV dictionary to standard Markdown format."""
    lines = []
    
    # Header / Contact
    name = data.get("name", "").strip() or "Nama Lengkap"
    lines.append(f"# {name}")
    
    if data.get("email"):
        lines.append(f"Email: {data['email'].strip()}")
    if data.get("phone"):
        lines.append(f"Phone: {data['phone'].strip()}")
    if data.get("location"):
        lines.append(f"Location: {data['location'].strip()}")
    if data.get("linkedin"):
        lines.append(f"LinkedIn: {data['linkedin'].strip()}")
    if data.get("github"):
        lines.append(f"GitHub: {data['github'].strip()}")
    lines.append("")
    
    # Summary
    if data.get("summary"):
        lines.append("## Ringkasan Profil")
        lines.append(data["summary"].strip())
        lines.append("")
        
    # Education
    if data.get("education"):
        lines.append("## Pendidikan")
        for edu in data["education"]:
            school = edu.get("school", "").strip()
            degree = edu.get("degree", "").strip()
            dates = edu.get("dates", "").strip()
            parts = [p for p in (school, degree, dates) if p]
            lines.append(f"### {' | '.join(parts)}")
        lines.append("")

    # Experience
    if data.get("experience"):
        lines.append("## Pengalaman Kerja")
        for exp in data["experience"]:
            title = exp.get("title", "").strip()
            company = exp.get("company", "").strip()
            dates = exp.get("dates", "").strip()
            parts = [p for p in (title, company, dates) if p]
            lines.append(f"### {' | '.join(parts)}")
            desc = exp.get("description", "").strip()
            if desc:
                for d_line in desc.splitlines():
                    d_line = d_line.strip()
                    if d_line:
                        if not d_line.startswith(("-", "*", "•")):
                            d_line = f"- {d_line}"
                        lines.append(d_line)
            lines.append("")

    # Organizations
    if data.get("organizations"):
        lines.append("## Organisasi")
        for org in data["organizations"]:
            title = org.get("title", "").strip()
            company = org.get("company", "").strip()
            dates = org.get("dates", "").strip()
            parts = [p for p in (title, company, dates) if p]
            lines.append(f"### {' | '.join(parts)}")
            desc = org.get("description", "").strip()
            if desc:
                for d_line in desc.splitlines():
                    d_line = d_line.strip()
                    if d_line:
                        if not d_line.startswith(("-", "*", "•")):
                            d_line = f"- {d_line}"
                        lines.append(d_line)
            lines.append("")

    # Skills
    if data.get("skills"):
        lines.append("## Keahlian")
        for s_line in data["skills"].strip().splitlines():
            s_line = s_line.strip()
            if s_line:
                if not s_line.startswith(("-", "*", "•")) and ":" not in s_line:
                    s_line = f"- {s_line}"
                lines.append(s_line)
        lines.append("")

    # Projects
    if data.get("projects"):
        lines.append("## Prestasi dan Proyek")
        for proj in data["projects"]:
            name = proj.get("name", "").strip()
            dates = proj.get("dates", "").strip()
            header = f"{name} | {dates}" if dates else name
            lines.append(f"### {header}")
            desc = proj.get("description", "").strip()
            if desc:
                for d_line in desc.splitlines():
                    d_line = d_line.strip()
                    if d_line:
                        if not d_line.startswith(("-", "*", "•")):
                            d_line = f"- {d_line}"
                        lines.append(d_line)
            lines.append("")

    return "\n".join(lines).strip() + "\n"

def cv_to_json(data: Dict[str, Any]) -> str:
    """Export CV dictionary to formatted JSON string."""
    return json.dumps(data, indent=2, ensure_ascii=False)

SAMPLE_PROFILES = {
    "tech": {
        "name": "Budi Pratama Santoso",
        "email": "budi.pratama@example.com",
        "phone": "+62 812-3456-7890",
        "location": "Jakarta Selatan, Indonesia",
        "linkedin": "linkedin.com/in/budipratama",
        "github": "github.com/budipratama",
        "summary": "Full Stack Developer dengan 4+ tahun pengalaman dalam membangun aplikasi web skalabel menggunakan React, Node.js, dan Python. Berpengalaman memimpin tim kecil dan meningkatkan performa sistem hingga 30%.",
        "skills": "Bahasa Pemrograman: JavaScript, TypeScript, Python, SQL\nFramework: React, Next.js, FastAPI, Express.js\nTools & Cloud: Git, Docker, PostgreSQL, Redis, Postman",
        "education": [
            {
                "school": "Institut Teknologi Bandung",
                "degree": "S1 Teknik Informatika (IPK 3.82/4.00)",
                "dates": "2020 - 2024"
            }
        ],
        "experience": [
            {
                "title": "Software Engineer",
                "company": "PT Solusi Teknologi Nusantara",
                "dates": "Januari 2024 - Sekarang",
                "description": "- Merancang dan membangun arsitektur microservices yang menangani 100.000+ request harian.\n- Mengoptimalkan query database PostgreSQL, memangkas latency response sebesar 25%.\n- Mengembangkan fitur automasi pipeline CI/CD yang mempercepat deployment sebesar 40%."
            },
            {
                "title": "Full Stack Web Developer Intern",
                "company": "Digital Media Studio",
                "dates": "Juni 2023 - Desember 2023",
                "description": "- Mengembangkan modul dashboard analitik internal menggunakan React dan Tailwind CSS.\n- Berkolaborasi dengan tim produk untuk meluncurkan 5 fitur baru tepat waktu."
            }
        ],
        "organizations": [
            {
                "title": "Ketua Divisi Riset & Teknologi",
                "company": "Himpunan Mahasiswa Informatika",
                "dates": "2022 - 2023",
                "description": "- Memimpin tim beranggotakan 12 orang menyelenggarakan hackathon kampus dengan 200+ peserta.\n- Menginisiasi workshop coding intensif bagi mahasiswa baru."
            }
        ],
        "projects": [
            {
                "name": "ATS CV Optimizer & Builder",
                "description": "- Aplikasi open-source berbasis Streamlit dan NLP untuk parsing dan optimasi CV format ATS.\n- Meraih 500+ bintang GitHub dalam kurun waktu 3 bulan peluncuran."
            }
        ]
    },
    "finance": {
        "name": "Siti Rahmawati, S.Ak., Ak.",
        "email": "siti.rahmawati@example.com",
        "phone": "+62 813-9876-5432",
        "location": "Jakarta Pusat, Indonesia",
        "linkedin": "linkedin.com/in/sitirahmawati-akuntan",
        "github": "",
        "summary": "Senior Accountant & Tax Specialist dengan 5+ tahun pengalaman dalam penyusunan laporan keuangan PSAK/IFRS, rekonsiliasi fiskal, audit kepatuhan internal, dan pelaporan e-Faktur/SPT Masa. Berhasil menghemat beban denda pajak perusahaan sebesar 15% melalui audit berkala.",
        "skills": "Keahlian Akuntansi: PSAK/IFRS, Jurnal Penyesuaian, Buku Besar, Rekonsiliasi Bank, Cash Flow\nPerpajakan: PPh 21, PPh 23, PPh 4(2), PPh Badan 25/29, PPN e-Faktur, Brevet AB Terverifikasi\nSoftware: SAP ERP Financials, Accurate Accounting, Zahir, Microsoft Excel Tingkat Lanjut (VLOOKUP, Pivot, Macros)",
        "education": [
            {
                "school": "Universitas Indonesia",
                "degree": "S1 Akuntansi, Fakultas Ekonomi dan Bisnis (IPK 3.86/4.00, Cum Laude)",
                "dates": "2018 - 2022"
            }
        ],
        "experience": [
            {
                "title": "Senior Financial Accountant",
                "company": "PT Bank Mandiri (Persero) Tbk",
                "dates": "Januari 2023 - Sekarang",
                "description": "- Mengelola penutupan buku akhir bulan (month-end closing) untuk portofolio transaksi bernilai Rp 50 Miliar per bulan.\n- Merekonsiliasi 120+ rekening koran dan pos aktiva lancar dengan tingkat akurasi 99.8%.\n- Memimpin audit internal tahunan bersama Kantor Akuntan Publik (KAP Big 4) tanpa temuan material."
            },
            {
                "title": "Junior Tax Specialist",
                "company": "PT Astra International Tbk",
                "dates": "Maret 2022 - Desember 2022",
                "description": "- Menyusun SPT Masa PPh 21, 23, dan PPN untuk 600+ karyawan dan mitra vendor tepat waktu.\n- Mengidentifikasi potensi restitusi pajak senilai Rp 120 Juta yang berhasil disetujui kantor pajak."
            }
        ],
        "organizations": [
            {
                "title": "Bendahara Umum",
                "company": "Ikatan Akuntan Indonesia (IAI) Muda Wilayah DKI",
                "dates": "2021 - 2023",
                "description": "- Mengaudit laporan pertanggungjawaban keuangan 8 seminar nasional akuntansi publik."
            }
        ],
        "projects": [
            {
                "name": "Otomasi Template Laporan Arus Kas Excel VBA",
                "description": "- Membangun template laporan arus kas otomatis yang memangkas waktu kerja closing bulanan tim dari 4 hari menjadi 1.5 hari."
            }
        ]
    },
    "hr": {
        "name": "Dewi Anggraini, S.Psi.",
        "email": "dewi.anggraini@example.com",
        "phone": "+62 821-5555-7788",
        "location": "Surabaya, Jawa Timur",
        "linkedin": "linkedin.com/in/dewi-anggraini-hr",
        "github": "",
        "summary": "Human Resources Generalist & Talent Acquisition Specialist dengan 4+ tahun pengalaman mengelola end-to-end recruitment, payroll karyawan, administrasi BPJS Ketenagakerjaan/Kesehatan, dan program retensi karyawan. Berhasil menurunkan angka turnover sebesar 18% dalam 12 bulan.",
        "skills": "HR Competencies: Talent Acquisition, End-to-End Recruitment, Behavioral Event Interview (BEI), Onboarding\nKompensasi & Benefit: Payroll Karyawan, PPh 21 Gross Up, BPJS Ketenagakerjaan, BPJS Kesehatan, UU Cipta Kerja\nTools & HRIS: Talenta by Mekari, Darwinbox, LinkedIn Recruiter, Jobstreet Enterprise, Google Workspace",
        "education": [
            {
                "school": "Universitas Airlangga",
                "degree": "S1 Psikologi (IPK 3.78/4.00)",
                "dates": "2019 - 2023"
            }
        ],
        "experience": [
            {
                "title": "HR Generalist & People Operations",
                "company": "PT Surya Semesta Mandiri",
                "dates": "Februari 2023 - Sekarang",
                "description": "- Menutup 45+ posisi strategis (level staf hingga manajerial) dengan rata-rata time-to-hire 21 hari.\n- Menjalankan payroll bulanan untuk 250 karyawan tetap dan kontrak tanpa keterlambatan pembayaran.\n- Menyusun perjanjian kerja PKWT dan PKWTT yang sesuai dengan regulasi Ketenagakerjaan terbaru."
            },
            {
                "title": "Recruitment Specialist Intern",
                "company": "PT Shopee International Indonesia",
                "dates": "Agustus 2022 - Januari 2023",
                "description": "- Melakukan screening 800+ resume kandidat dan menjadwalkan 150 sesi wawancara user.\n- Memperbaiki alur onboarding karyawan baru yang menaikkan skor kepuasan induksi hingga 92%."
            }
        ],
        "organizations": [
            {
                "title": "Kepala Divisi Pengembangan Sumber Daya Anggota",
                "company": "Himpunan Mahasiswa Psikologi",
                "dates": "2021 - 2022",
                "description": "- Mengadakan pelatihan kepemimpinan dan manajemen konflik untuk 80 anggota aktif."
            }
        ],
        "projects": [
            {
                "name": "Inisiatif Program Employee Wellness & Engagement",
                "description": "- Merancang survei keterikatan kerja kuartalan dan program konseling karyawan yang meningkatkan eNPS sebesar 24 poin."
            }
        ]
    },
    "marketing": {
        "name": "Rian Ardiansyah, S.I.Kom.",
        "email": "rian.ardiansyah@example.com",
        "phone": "+62 811-7788-9900",
        "location": "Jakarta Barat, Indonesia",
        "linkedin": "linkedin.com/in/rian-marketing",
        "github": "portfolio.rianmarketing.com",
        "summary": "Digital Marketing & Performance Strategist dengan 4+ tahun pengalaman mengelola paid ads (Meta Ads, Google Ads, TikTok Ads) beranggaran Rp 150 Juta/bulan, SEO, dan konversi funnel e-commerce. Terbukti mencapai ROAS rata-rata 4.2x dan menaikkan organic traffic website sebesar 140%.",
        "skills": "Paid Acquisition: Meta Ads Manager, Google Search/Display Ads, TikTok Ads Manager, Remarketing\nSEO & Analytics: Google Analytics 4 (GA4), Google Search Console, Ahrefs, SEMrush, Technical SEO\nCreative & Content: Copywriting, Conversion Rate Optimization (CRO), A/B Testing, Email Marketing (Mailchimp)",
        "education": [
            {
                "school": "Universitas Padjadjaran",
                "degree": "S1 Ilmu Komunikasi, Konsentrasi Hubungan Masyarakat (IPK 3.75/4.00)",
                "dates": "2019 - 2023"
            }
        ],
        "experience": [
            {
                "title": "Digital Marketing Specialist",
                "company": "PT Retail Inovasi Niaga",
                "dates": "Januari 2023 - Sekarang",
                "description": "- Mengelola kampanye paid ads tahunan yang menghasilkan omzet penjualan sebesar Rp 1.8 Miliar.\n- Mengoptimalkan Customer Acquisition Cost (CAC) turun 22% melalui continuous A/B test ad creative.\n- Memimpin kampanye peluncuran produk baru dengan capaian 50.000 pesanan dalam bulan pertama."
            },
            {
                "title": "Content Strategist & Copywriter",
                "company": "Agensi Digital Sinergi Kreasi",
                "dates": "Juli 2022 - Desember 2022",
                "description": "- Menulis 80+ artikel blog berorientasi SEO yang menempati peringkat 1-3 Google untuk 25 kata kunci industri."
            }
        ],
        "organizations": [
            {
                "title": "Koordinator Publikasi & Hubungan Media",
                "company": "Festival Budaya Kreatif Nusantara",
                "dates": "2022",
                "description": "- Menjalin kemitraan dengan 15 media massa nasional yang meliput acara dengan total 30.000 pengunjung."
            }
        ],
        "projects": [
            {
                "name": "Revitalisasi Organik SEO E-Commerce Fashion",
                "description": "- Meningkatkan trafik organik bulanan dari 12.000 pengunjung menjadi 45.000 pengunjung dalam tempo 6 bulan."
            }
        ]
    },
    "healthcare": {
        "name": "Ners. Anisa Wulandari, S.Kep.",
        "email": "anisa.wulandari@example.com",
        "phone": "+62 852-1122-3344",
        "location": "Semarang, Jawa Tengah",
        "linkedin": "linkedin.com/in/anisa-wulandari-nurse",
        "github": "",
        "summary": "Perawat Klinis Terlisensi (STR Aktif) dengan 4+ tahun pengalaman di instalasi rawat inap dan IGD rumah sakit tipe B. Terampil dalam manajemen triase darurat, pemasangan infus/kateter, pemantauan tanda-tanda vital, dan administrasi obat sesuai standar keselamatan pasien (Patient Safety).",
        "skills": "Keahlian Keperawatan: Basic Life Support (BLS), Triase IGD, Perawatan Luka Modern, Terapi Intravena\nSertifikasi & Lisensi: Surat Tanda Registrasi (STR) Perawat Aktif, Sertifikat BTCLS Kemkes, PPI Dasar\nKompetensi Medis: Dokumentasi Rekam Medis Elektronik (SIMRS), Komunikasi Terapeutik, Patient Safety",
        "education": [
            {
                "school": "Universitas Diponegoro",
                "degree": "Profesi Ners & S1 Keperawatan, Fakultas Kedokteran (IPK 3.80/4.00)",
                "dates": "2018 - 2023"
            }
        ],
        "experience": [
            {
                "title": "Perawat Pelaksana Rawat Inap & IGD",
                "company": "Rumah Sakit Umum Daerah (RSUD) Tugurejo",
                "dates": "Februari 2023 - Sekarang",
                "description": "- Memberikan asuhan keperawatan langsung kepada 15-20 pasien rawat inap per shift kerja.\n- Bertanggung jawab atas pemberian terapi obat injeksi, infus, dan transfusi darah dengan zero medication error.\n- Mengedukasi keluarga pasien tentang perawatan pasca rawat inap dan diet kepatuhan nutrisi."
            },
            {
                "title": "Perawat Praktik Profesi Klinik",
                "company": "Rumah Sakit Umum Pusat Dr. Kariadi",
                "dates": "Januari 2022 - Desember 2022",
                "description": "- Menjalankan rotasi klinis di ruang ICU, Bedah, Anak, dan Maternitas dengan evaluasi predikat A."
            }
        ],
        "organizations": [
            {
                "title": "Pengurus Bidang Kesejahteraan",
                "company": "Persatuan Perawat Nasional Indonesia (PPNI) Komisariat RS",
                "dates": "2023 - Sekarang",
                "description": "- Mengkoordinasikan seminar ilmiah berkala mengenai penanganan sepsis akut bagi perawat muda."
            }
        ],
        "projects": [
            {
                "name": "Inisiasi Standar Operasional Prosedur (SOP) Hand Hygiene Ruang Anak",
                "description": "- Menurunkan angka infeksi nosokomial di bangsal anak sebesar 12% melalui edukasi cuci tangan interaktif."
            }
        ]
    },
    "admin": {
        "name": "Fajar Nugraha, A.Md.",
        "email": "fajar.nugraha@example.com",
        "phone": "+62 878-4433-2211",
        "location": "Bandung, Jawa Barat",
        "linkedin": "linkedin.com/in/fajar-nugraha-admin",
        "github": "",
        "summary": "Staf Administrasi Perkantoran & General Affairs dengan 4+ tahun pengalaman dalam pengelolaan korespondensi dinas, pengadaan inventaris kantor (procurement), pengarsipan digital, dan penjadwalan agenda eksekutif direksi. Teliti, rapi, dan terbiasa bekerja dengan target ketat.",
        "skills": "Administrasi Kantor: Pengarsipan Digital, Notulensi Rapat, Surat-Menyurat Resmi, Inventarisasi Kantor\nPerangkat Lunak: Microsoft Office (Word, Excel, PowerPoint), Google Workspace, Sistem ERP SAP Procurement\nKemampuan Khusus: Manajemen Pengadaan Barang/Jasa (PO & Invoice), Pengelolaan Kas Kecil (Petty Cash)",
        "education": [
            {
                "school": "Politeknik Negeri Bandung",
                "degree": "D3 Administrasi Bisnis (IPK 3.70/4.00)",
                "dates": "2019 - 2022"
            }
        ],
        "experience": [
            {
                "title": "Staff Administrasi & General Affairs",
                "company": "PT Pos Indonesia (Persero)",
                "dates": "Januari 2023 - Sekarang",
                "description": "- Mengelola administrasi petty cash operasional kantor senilai Rp 30 Juta/bulan dengan rekonsiliasi tanpa selisih.\n- Mengatur jadwal penerbangan, hotel, dan ruang rapat untuk 8 jajaran manajer dan direktur divisi.\n- Menertibkan 1.500+ berkas arsip kontrak kerjasama fisik ke sistem database digital terenkripsi."
            },
            {
                "title": "Junior Office Administrative Assistant",
                "company": "Kantor Notaris & PPAT Rekanan",
                "dates": "Agustus 2022 - Desember 2022",
                "description": "- Menyiapkan draf akta tanah, legalisasi dokumen, dan verifikasi berkas perbankan klien."
            }
        ],
        "organizations": [
            {
                "title": "Ketua Seksi Kesekretariatan",
                "company": "Koperasi Pemuda Mandiri Jawa Barat",
                "dates": "2021 - 2023",
                "description": "- Menyusun notulensi Rapat Anggota Tahunan (RAT) dan mengelola pembagian sisa hasil usaha (SHU)."
            }
        ],
        "projects": [
            {
                "name": "Digitalisasi Sistem Pengajuan ATK Internal",
                "description": "- Merancang formulir digital berbasis Google Sheets & Form yang menghemat waktu approval pengadaan barang 50%."
            }
        ]
    }
}

def get_sample_cv_data(industry: str = "tech") -> Dict[str, Any]:
    """Return pre-filled sample CV data for instant testing across multiple industries."""
    return SAMPLE_PROFILES.get(industry, SAMPLE_PROFILES["tech"])


