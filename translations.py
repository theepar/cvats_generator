"""
Translations module for ATS CV Generator (i18n)
Supports English (en) and Bahasa Indonesia (id)
"""

TRANSLATIONS = {
    "en": {
        # App Header
        "app_title": "ATS-Friendly CV Generator",
        "app_subtitle": "Fill in your details below to create a clean, parsed PDF optimized for ATS.",
        "lang_select": "Language / Bahasa",
        
        # Tabs
        "tab_personal": "Personal Info",
        "tab_education": "Education",
        "tab_experience": "Experience",
        "tab_organizations": "Organizations",
        "tab_skills_projects": "Skills & Projects",
        
        # Personal Info
        "personal_header": "Personal Information",
        "full_name": "Full Name",
        "email": "Email",
        "phone": "Phone Number",
        "location": "Location (City, Country)",
        "linkedin": "LinkedIn URL",
        "github": "Portfolio/GitHub URL",
        "toggle_portfolio": "Include Portfolio / GitHub link in CV",
        "summary": "Professional Summary",
        "summary_placeholder": "e.g., Dedicated software engineer with 3+ years of experience...",
        
        # Education
        "edu_header": "Education",
        "edu_title": "Education",
        "school": "School/University",
        "degree": "Degree",
        "dates": "Dates",
        "add_edu": "Add Education",
        "del_edu": "Delete Education",
        
        # Work Experience
        "work_header": "Work Experience",
        "role": "Role",
        "job_title": "Job Title",
        "company": "Company",
        "work_desc": "Description / Achievements",
        "add_work": "Add Experience",
        "del_work": "Delete Experience",
        
        # Organizations
        "org_header": "Organizations",
        "org_item": "Organization",
        "org_role": "Role/Position",
        "org_name": "Organization Name",
        "org_desc": "Description",
        "add_org": "Add Organization",
        "del_org": "Delete Organization",
        
        # Skills & Achievements
        "skills_header": "Skills",
        "skills_label": "Skills",
        "skills_placeholder": "e.g.:\n• Languages: PHP, JavaScript, Python\n• Frameworks: Laravel, React, Django",
        "achievements_header": "Achievements & Projects",
        "toggle_projects_section": "Include Achievements & Projects section in CV",
        "achievement": "Achievement",
        "achieve_name": "Name",
        "achieve_desc": "Details",
        "add_achieve": "Add Achievement",
        "del_achieve": "Delete Achievement",
        
        # Settings & Actions
        "doc_settings": "Document Settings",
        "font_tip": "Tip: 'Times New Roman' is best for older ATS systems. 'Arial' is clean and modern.",
        "select_font": "Select Font Style",
        "cv_lang_label": "PDF Output Language",
        "generate_btn": "Generate CV",
        "name_required": "Please fill in at least your name.",
        "success_msg": "CV Generated Successfully!",
        "download_btn": "Download PDF",
    },
    "id": {
        # App Header
        "app_title": "Pembuat CV ATS-Friendly",
        "app_subtitle": "Isi data Anda di bawah ini untuk membuat CV PDF yang rapi dan optimal untuk sistem ATS.",
        "lang_select": "Bahasa / Language",
        
        # Tabs
        "tab_personal": "Info Pribadi",
        "tab_education": "Pendidikan",
        "tab_experience": "Pengalaman Kerja",
        "tab_organizations": "Organisasi",
        "tab_skills_projects": "Keahlian & Prestasi",
        
        # Personal Info
        "personal_header": "Informasi Pribadi",
        "full_name": "Nama Lengkap",
        "email": "Email",
        "phone": "No. Telepon",
        "location": "Lokasi (Kota, Negara)",
        "linkedin": "LinkedIn",
        "github": "Portfolio/GitHub",
        "toggle_portfolio": "Sertakan tautan Portfolio / GitHub di CV",
        "summary": "Ringkasan Profil",
        "summary_placeholder": "Contoh: Software engineer berdedikasi dengan pengalaman 3+ tahun...",
        
        # Education
        "edu_header": "Pendidikan",
        "edu_title": "Pendidikan",
        "school": "Sekolah/Universitas",
        "degree": "Gelar/Jurusan",
        "dates": "Tanggal/Periode",
        "add_edu": "Tambah Pendidikan",
        "del_edu": "Hapus Pendidikan",
        
        # Work Experience
        "work_header": "Pengalaman Kerja",
        "role": "Peran",
        "job_title": "Posisi/Jabatan",
        "company": "Perusahaan",
        "work_desc": "Deskripsi / Pencapaian",
        "add_work": "Tambah Pengalaman",
        "del_work": "Hapus Pengalaman",
        
        # Organizations
        "org_header": "Pengalaman Organisasi",
        "org_item": "Organisasi",
        "org_role": "Peran/Jabatan",
        "org_name": "Nama Organisasi",
        "org_desc": "Deskripsi Kegiatan",
        "add_org": "Tambah Organisasi",
        "del_org": "Hapus Organisasi",
        
        # Skills & Achievements
        "skills_header": "Keahlian",
        "skills_label": "Keahlian",
        "skills_placeholder": "Contoh:\n• Bahasa: PHP, JavaScript, Python\n• Framework: Laravel, React, Django",
        "achievements_header": "Prestasi & Proyek",
        "toggle_projects_section": "Sertakan bagian Prestasi & Proyek pada CV",
        "achievement": "Prestasi",
        "achieve_name": "Nama",
        "achieve_desc": "Detail",
        "add_achieve": "Tambah Prestasi",
        "del_achieve": "Hapus Prestasi",
        
        # Settings & Actions
        "doc_settings": "Pengaturan Dokumen",
        "font_tip": "Petunjuk: 'Times New Roman' cocok untuk sistem ATS klasik. 'Arial' lebih modern.",
        "select_font": "Pilih Font",
        "cv_lang_label": "Bahasa Output PDF",
        "generate_btn": "Buat CV",
        "name_required": "Mohon isi nama Anda terlebih dahulu.",
        "success_msg": "CV berhasil dibuat!",
        "download_btn": "Download PDF",
    }
}

CV_SECTION_HEADERS = {
    "en": {
        "summary": "Professional Summary",
        "skills": "Technical Skills",
        "experience": "Work Experience",
        "organizations": "Organizational Experience",
        "education": "Education",
        "projects": "Achievements & Projects"
    },
    "id": {
        "summary": "Ringkasan Profil",
        "skills": "Keahlian Utama",
        "experience": "Pengalaman Kerja",
        "organizations": "Pengalaman Organisasi",
        "education": "Pendidikan",
        "projects": "Prestasi & Proyek"
    }
}
