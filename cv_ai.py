import re
from pathlib import Path

import joblib
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion, make_pipeline
from sklearn.svm import LinearSVC

from cv_parser import SECTION_NAMES, ENTRY_FIELDS, PERSONAL_FIELDS, find_field, parse_entry, read_label, strip_format

MODEL_FILE = Path(__file__).with_name("cv_model.joblib")

HEADINGS = {
    "summary": [
        # English (20)
        "Summary", "Professional Summary", "About Me", "Career Objective", "Personal Statement",
        "Profile", "Executive Summary", "Personal Profile", "Overview", "Biography",
        "Career Summary", "Professional Bio", "Summary of Qualifications", "Career Profile", "Brief Profile",
        "Self Introduction", "Objective", "Candidate Profile", "Work Summary", "About",
        # Indonesian (20)
        "Ringkasan", "Profil Singkat", "Tentang Saya", "Ringkasan Diri", "Deskripsi Singkat",
        "Profil Profesional", "Ringkasan Eksekutif", "Ringkasan Karier", "Latar Belakang Singkat", "Profil Diri",
        "Tentang Profil", "Profil Pribadi", "Tujuan Karier", "Deskripsi Diri", "Ringkasan Kualifikasi",
        "Tentang Kandidat", "Pernyataan Diri", "Latar Belakang Diri", "Visi Karier", "Biodata Diri"
    ],
    "education": [
        # English (20)
        "Education", "Academic Background", "Educational History", "Academic Qualifications", "Education and Training",
        "Formal Education", "Degrees", "University & School", "Academic Record", "Higher Education",
        "Schooling", "Educational Background", "Degrees & Diplomas", "University Education", "Academic Profile",
        "College Education", "Academic Credentials", "Formal Studies", "Studies and Degrees", "Educational Credentials",
        # Indonesian (20)
        "Pendidikan", "Riwayat Pendidikan", "Latar Belakang Akademik", "Pendidikan Formal", "Riwayat Sekolah",
        "Studi dan Pendidikan", "Pendidikan Terakhir", "Riwayat Perkuliahan", "Jenjang Pendidikan", "Akademik",
        "Pendidikan dan Pelatihan", "Latar Belakang Pendidikan", "Kualifikasi Akademik", "Riwayat Studi", "Latar Belakang Studi",
        "Riwayat Kuliah", "Pendidikan Lanjutan", "Institusi Pendidikan", "Sekolah dan Kuliah", "Studi Formal"
    ],
    "experience": [
        # English (20)
        "Experience", "Employment History", "Professional Experience", "Work History", "Career History",
        "Work Experience", "Jobs", "Internship Experience", "Working History", "Employment",
        "Professional Background", "Work Background", "Practical Experience", "Relevant Experience", "Corporate Experience",
        "Career Journey", "Employment Record", "Work and Career", "Job Experience", "Industry Experience",
        # Indonesian (20)
        "Pengalaman Kerja", "Riwayat Pekerjaan", "Pengalaman Profesional", "Pengalaman Magang", "Riwayat Karier",
        "Riwayat Karier Kerja", "Pengalaman Bekerja", "Pengalaman Kerja & Magang", "Karier Profesional", "Pengalaman Industri",
        "Jejak Karier", "Riwayat Pengalaman", "Riwayat Kerja", "Pengalaman Terkait", "Pengalaman Praktik",
        "Karier dan Pekerjaan", "Pengalaman Bekerja Nyata", "Riwayat Profesi", "Aktivitas Pekerjaan", "Jejak Pengalaman Kerja"
    ],
    "organizations": [
        # English (20)
        "Organizations", "Leadership Experience", "Volunteer Experience", "Community Involvement", "Organizational Activities",
        "Volunteer Work", "Extracurricular Activities", "Student Organization", "Leadership & Activities", "Community Work",
        "Extracurriculars", "Community Service", "Student Union Experience", "Leadership History", "Volunteering & Community",
        "Student Activities", "Campus Involvement", "Organizational Roles", "Club & Society Activities", "Social Initiatives",
        # Indonesian (20)
        "Organisasi", "Pengalaman Organisasi", "Aktivitas Organisasi", "Kegiatan Komunitas", "Pengalaman Kepanitiaan",
        "Organisasi Kampus", "Pengalaman Kepemimpinan", "Kegiatan Relawan", "Kepanitiaan & Organisasi", "Aktivitas Kemahasiswaan",
        "Kepanitiaan", "Komunitas", "Aktivitas Non Akademik", "Pengalaman Sukarelawan", "Kegiatan Mahasiswa",
        "Aktivitas Organisasi Kampus", "Pengalaman Keorganisasian", "Kegiatan Sukarela", "Aktivitas Ekstrakurikuler", "Kepanitiaan Kampus"
    ],
    "skills": [
        # English (20)
        "Skills", "Technical Skills", "Core Competencies", "Technology Stack", "Tools and Technologies",
        "Hard Skills", "Soft Skills", "Tools & Frameworks", "Programming Languages", "Tech Stack",
        "Tools & Software", "Technical Proficiencies", "Expertise", "Technical Stack", "Core Skills",
        "Key Competencies", "Technologies", "Software Proficiencies", "Specialized Skills", "Domain Competencies",
        # Indonesian (20)
        "Keahlian", "Kemampuan Teknis", "Keterampilan", "Kompetensi", "Keahlian Utama",
        "Keahlian Komputer", "Keterampilan Teknis", "Kompetensi Keahlian", "Keahlian & Kemampuan", "Keahlian Bidang",
        "Keterampilan Utama", "Penguasaan Tools", "Kemampuan Komputasi", "Keahlian Pemrograman", "Alat dan Teknologi",
        "Keterampilan Komputer", "Penguasaan Perangkat Lunak", "Keahlian Teknis & Bahasa", "Penguasaan Bahasa Pemrograman", "Kemampuan Spesifik"
    ],
    "projects": [
        # English (20)
        "Projects", "Selected Projects", "Portfolio", "Key Achievements", "Awards and Projects",
        "Personal Projects", "Academic Projects", "Honors & Awards", "Key Projects", "Selected Works",
        "Notable Projects", "Personal Portfolio", "Independent Projects", "Featured Work", "Project Highlights",
        "Capstone Projects", "Product Portfolio", "Technical Projects", "Software Projects", "Achievements & Awards",
        # Indonesian (20)
        "Proyek", "Proyek Pilihan", "Portofolio", "Pencapaian", "Prestasi dan Proyek",
        "Proyek Portofolio", "Prestasi", "Penghargaan", "Daftar Portofolio", "Karya dan Proyek",
        "Proyek Independen", "Prestasi Akademik & Lomba", "Daftar Karya", "Portofolio Proyek", "Karya Portofolio",
        "Prestasi dan Penghargaan", "Daftar Pencapaian", "Hasil Karya dan Portofolio", "Proyek Tugas Akhir", "Kompetisi dan Lomba"
    ],
}

EXAMPLES = {
    "summary": [
        "Professional summary: Results-driven software engineer with 4+ years building high-throughput distributed systems.",
        "Passionate full-stack developer committed to crafting elegant web experiences and maintaining clean software architecture.",
        "Experienced technical lead adept at guiding agile squads, conducting code reviews, and delivering enterprise roadmaps.",
        "Dynamic problem solver with strong background in backend API development, performance tuning, and database modeling.",
        "Results-oriented project manager with proven history of delivering multi-million dollar SaaS products on schedule.",
        "Detail-oriented data analyst passionate about transforming raw telemetry into actionable executive business intelligence.",
        "Creative UI/UX designer with 5 years crafting human-centered user experiences across iOS and Android ecosystems.",
        "DevOps engineer dedicated to automating CI/CD release pipelines and architecting resilient Kubernetes clusters.",
        "Ambitious computer science graduate seeking a junior software engineering role to leverage problem-solving skills.",
        "Motivated professional with expertise in technical consulting, cloud security compliance, and vendor management.",
        "Self-starter with demonstrated passion for scalable web platforms, open-source contribution, and team collaboration.",
        "Certified Scrum Master with extensive experience facilitating sprint ceremonies and eliminating technical roadblocks.",
        "Innovative product designer focused on design systems, accessibility standards, and responsive web aesthetics.",
        "Energetic software developer eager to contribute hands-on coding and algorithmic design to high-impact projects.",
        "Customer-centric engineering manager with track record of scaling engineering organizations from 5 to 30 engineers.",
        "Summary: Seasoned cybersecurity analyst specializing in threat intelligence, vulnerability assessment, and risk audits.",
        "Career objective: To leverage solid foundations in distributed computing and microservices at a forward-thinking company.",
        "Forward-thinking technologist with broad expertise across modern cloud infrastructure and automated software delivery.",
        "Accomplished mobile developer with 6+ years publishing top-charting consumer applications on the Apple App Store.",
        "Adaptive full stack engineer who thrives in fast-paced startup environments and enjoys solving ambiguous challenges.",
        "Profile: Dedicated machine learning researcher passionate about generative models and natural language processing.",
        "Reliable software engineer known for rigorous code testing, meticulous technical documentation, and cross-team empathy.",
        "Resourceful developer with comprehensive experience across the complete software development lifecycle (SDLC).",
        "Analytical professional with deep passion for data engineering, ETL orchestration, and predictive business models.",
        "Senior solutions architect with 8+ years designing fault-tolerant cloud infrastructures for financial institutions.",
        "About me: Passionate software developer who values code simplicity, automated testing, and continuous learning.",
        "Enthusiastic QA engineer dedicated to building robust test automation frameworks and ensuring zero-defect production releases.",
        "High-performing engineering professional passionate about cloud economics, serverless paradigms, and DevOps culture.",
        "Proactive IT consultant with proven success aligning business strategies with modern technological implementations.",
        "Versatile programmer who combines creative design thinking with rigorous algorithmic and architectural foundations.",
        "Ringkasan profesional: Software engineer berdedikasi dengan pengalaman 4+ tahun merancang sistem backend skalabel.",
        "Full stack developer yang berfokus pada performa aplikasi web modern dan kepuasan pengalaman pengguna akhir.",
        "Lulusan Sarjana Teknik Informatika yang antusias memulai karier profesional di bidang rekayasa perangkat lunak.",
        "Pribadi yang adaptif, komunikatif, serta terbiasa bekerja dalam lingkungan kerja cepat berbasis metodologi Agile Scrum.",
        "Profesional teknologi informasi dengan spesialisasi pada arsitektur cloud, kontainerisasi, dan otomatisasi deployment.",
        "Data analyst dengan ketelitian tinggi dalam memproses data bisnis kompleks menjadi visualisasi dashboard strategis.",
        "UI/UX designer berpengalaman dalam riset pengguna, wireframing interaktif, serta pembuatan design system konsisten.",
        "DevOps practitioner yang berkomitmen menjaga keandalan infrastruktur server dan otomatisasi pipeline CI/CD.",
        "Project manager berorientasi target dengan rekam jejak sukses mengelola siklus pengembangan produk software tepat waktu.",
        "Saya seorang programmer yang menyukai pemecahan masalah algoritma, optimasi query, dan penulisan kode bersih.",
        "Memiliki aspirasi karier untuk berkontribusi maksimal sebagai backend engineer pada perusahaan teknologi berkembang.",
        "Tenaga profesional yang memiliki komitmen kuat terhadap kualitas perangkat lunak, keamanan kode, dan dokumentasi rapi.",
        "Profil singkat: Spesialis rekayasa data dengan pengalaman membangun pipeline ETL dan pemodelan data pergudangan.",
        "Tekun, berintegritas, serta mampu bekerja secara mandiri maupun dalam tim kolaboratif lintas divisi fungsional.",
        "Berpengalaman memimpin inisiatif modernisasi sistem aplikasi legacy menuju arsitektur microservices terdistribusi.",
        "Praktisi IT support dan administrator sistem dengan sertifikasi resmi di bidang manajemen jaringan komputer.",
        "Memiliki ketertarikan mendalam pada kecerdasan buatan, machine learning, serta implementasi otomasi cerdas.",
        "Frontend engineer yang berdedikasi menciptakan antarmuka web responsif, aksesibel, dan cepat dimuat di berbagai peramban.",
        "Lulusan baru dengan predikat pujian yang siap menerapkan keahlian pemrograman web dan analisis sistem secara profesional.",
        "Pengembang aplikasi mobile dengan portofolio aplikasi Flutter yang telah terbit resmi di Google Play Store.",
        "Profesional QA dengan pengalaman menyusun skenario uji otomatis untuk menjamin keandalan sistem perbankan.",
        "Summary: Technical lead yang berpengalaman membimbing engineer junior dan menegakkan standar rekayasa software.",
        "Pribadi yang proaktif dengan keahlian berpikir analitis kuat dalam menyelesaikan kendala operasional sistem IT.",
        "Berorientasi pada efisiensi operasional sistem, stabilitas infrastruktur cloud, dan kepuasan pelanggan korporat.",
        "Spesialis keamanan informasi dengan rekam jejak dalam audit kepatuhan ISO 27001 dan pengujian penetrasi sistem.",
        "Pengembang software yang memiliki disiplin tinggi dalam penerapan Test-Driven Development (TDD) dan Clean Code.",
        "Memiliki rekam jejak sukses dalam mengkoordinasikan rilis perangkat lunak skala enterprise dengan risiko downtime minimal.",
        "Tentang saya: Pengembang perangkat lunak yang bersemangat mempelajari framework baru dan metodologi rekayasa modern.",
        "Individu yang memiliki motivasi tinggi dalam menghadirkan solusi teknologi yang tepat guna dan bernilai bisnis nyata.",
        "Berpengalaman selama 3 tahun dalam mengelola integrasi REST API dan gateway pembayaran pihak ketiga secara aman.",
        "Professional summary: Results-driven software engineer with 4+ years building high-throughput distributed systems.",
        "Passionate full-stack developer committed to crafting elegant web experiences and maintaining clean software architecture.",
        "DevOps engineer dedicated to automating CI/CD release pipelines and architecting resilient Kubernetes clusters.",
        "Detail-oriented data analyst passionate about transforming raw telemetry into actionable executive business intelligence.",
        "Senior accountant with 6+ years experience managing financial reporting, statutory audits, and tax compliance under IFRS.",
        "Certified financial analyst skilled in financial modeling, valuation, portfolio risk assessment, and cash flow budgeting.",
        "Human resources generalist with proven track record in talent acquisition, employee relations, payroll, and benefits.",
        "Talent acquisition specialist experienced in full-lifecycle recruitment, candidate sourcing, and behavioral interviewing.",
        "Dynamic digital marketing strategist with 5 years experience driving paid acquisition, SEO growth, and conversion funnels.",
        "Results-oriented account executive with strong track record in B2B enterprise software sales and client relationship management.",
        "Licensed registered nurse (RN) dedicated to delivering compassionate patient care, triage management, and clinical documentation.",
        "Detail-oriented clinical research coordinator experienced in patient protocol compliance, GCP standards, and trial data.",
        "Accomplished executive assistant with 7+ years managing executive calendars, cross-department travel, and office procurement.",
        "Supply chain coordinator experienced in inventory forecasting, warehouse logistics, and vendor contract negotiations.",
        "Passionate high school educator with 5+ years teaching STEM curriculum, facilitating student development, and grading.",
        "Academic lecturer dedicated to interactive instructional design, higher education research, and student mentorship.",
        "Corporate legal counsel with expertise in commercial contract drafting, regulatory compliance audits, and corporate governance.",
        "Compliance officer skilled in anti-money laundering (AML) protocols, risk management frameworks, and internal controls.",
        "Ringkasan profesional: Software engineer berdedikasi dengan pengalaman 4+ tahun merancang sistem backend skalabel.",
        "Full stack developer yang berfokus pada performa aplikasi web modern dan kepuasan pengalaman pengguna akhir.",
        "DevOps practitioner yang berkomitmen menjaga keandalan infrastruktur server dan otomatisasi pipeline CI/CD.",
        "Data analyst dengan ketelitian tinggi dalam memproses data bisnis kompleks menjadi visualisasi dashboard strategis.",
        "Akuntan senior dengan pengalaman 5+ tahun dalam penyusunan laporan keuangan PSAK, rekonsiliasi fiskal, dan audit internal.",
        "Analis keuangan profesional yang mahir dalam perencanaan anggaran perusahaan, audit arus kas, dan pelaporan pajak e-Faktur.",
        "HR Generalist berpengalaman menangani end-to-end recruitment, payroll karyawan, serta administrasi BPJS Ketenagakerjaan.",
        "Praktisi human resources dengan keahlian dalam evaluasi kinerja pegawai, mediasi hubungan industrial, dan retensi talenta.",
        "Digital marketing specialist dengan rekam jejak sukses mengelola paid ads, optimasi SEO, dan funnel penjualan e-commerce.",
        "Account executive berorientasi target dengan rekam jejak melampaui kuota penjualan solusi B2B korporat dan negosiasi kontrak.",
        "Perawat klinis terlisensi STR aktif dengan pengalaman 4 tahun di ruang rawat inap, instalasi gawat darurat, dan patient safety.",
        "Tenaga kefarmasian dan apoteker berdedikasi dengan keahlian dalam dispensing obat, evaluasi resep dokter, dan manajemen stok apotek.",
        "Staf administrasi perkantoran yang teliti dan terorganisir dalam korespondensi dinas, pengarsipan digital, dan kas kecil.",
        "Koordinator logistik dan operasional gudang berpengalaman dalam manajemen rantai pasok, pengadaan barang, dan inventaris.",
        "Tenaga pendidik profesional dengan pengalaman 4 tahun menyusun modul ajar Kurikulum Merdeka dan bimbingan belajar siswa.",
        "Dosen dan pengajar perguruan tinggi yang berkomitmen pada tri dharma perguruan tinggi, publikasi ilmiah, dan riset terapan.",
        "Staf legal korporat berpengalaman dalam penyusunan draf kontrak bisnis komersial, perizinan berusaha OSS, dan kepatuhan hukum.",
        "Spesialis hukum dan kepatuhan regulasi dengan rekam jejak dalam audit kepatuhan perusahaan dan penanganan sengketa perdata.",
    ],
    "education": [
        "Bachelor of Science in Computer Science, State University, GPA 3.85 / 4.00, Graduated Magna Cum Laude",
        "Master of Science in Information Systems, National Institute of Technology, Graduated with Honors 2023",
        "Associate Degree in Computer Engineering, State Polytechnic, 2020 - 2023, GPA 3.72",
        "Bachelor of Business Administration, Major in Marketing and Management, School of Business, Class of 2022",
        "High School Diploma in Natural Sciences, National High School, Graduated in top 5% of class ranking",
        "Bachelor of Engineering in Electrical Engineering, Faculty of Engineering, Final Thesis: Embedded IoT Systems",
        "Candidate for Bachelor of Computer Science, expected graduation in December 2025, Current GPA 3.80",
        "Completed university coursework in Data Structures, Algorithms, Distributed Databases, and Compiler Design",
        "Diploma in Graphic Design and Multimedia Communication, Creative Arts College, Graduated 2021",
        "Bachelor of Information Technology, Department of Computing, Academic standing: First Class Honors",
        "Master of Business Administration (MBA), Graduate School of Management, Concentration in Tech Strategy",
        "Undergraduate degree in Software Engineering, School of Informatics, GPA 3.91 / 4.00",
        "International Exchange Student Program in Software Systems at National University of Singapore (NUS) 2023",
        "Bachelor of Science in Mathematics and Statistics, Faculty of Science, GPA 3.65",
        "Vocational High School Diploma in Computer Network Engineering (TKJ) with national certification",
        "Bachelor of Cyber Security and Digital Forensics, Institute of Technology, Graduated 2024",
        "Completed undergraduate thesis titled: Deep Neural Networks for Automated Medical Image Diagnosis",
        "Bachelor of Arts in English Literature and Linguistics, Faculty of Humanities, GPA 3.70",
        "Master of Data Science, School of Computing, Completed research on Natural Language Processing",
        "Dual Degree Program: Bachelor of Computer Science and Bachelor of Commerce, 2018 - 2023",
        "Undergraduate coursework: Operating Systems, Computer Networks, Linear Algebra, and Cloud Architecture",
        "Bachelor of Mechanical Engineering, Department of Mechanical Sciences, Graduated with distinction",
        "Postgraduate Diploma in Applied Artificial Intelligence, Institute of Advanced Technology 2022",
        "Vocational Diploma in Software Application Engineering, Technical College, Final project score 95/100",
        "Bachelor of Science in Physics, Faculty of Mathematics and Natural Sciences, GPA 3.55",
        "Bachelor of Finance and Banking, Faculty of Economics and Business, Class of 2021",
        "High School Diploma with honors in Mathematics and Physical Sciences, Graduated June 2020",
        "Bachelor of Design in Interactive Media and UI/UX Design, School of Art and Design, GPA 3.82",
        "Undergraduate student in Informatics Engineering, semester 7, specialization in Artificial Intelligence",
        "Bachelor of Telecommunications Engineering, Faculty of Electronics, Academic GPA 3.68",
        "S1 Teknik Informatika, Institut Teknologi Bandung (ITB), IPK 3.82 / 4.00, Lulus dengan Predikat Cum Laude",
        "Sarjana Sistem Informasi, Universitas Indonesia (UI), Fakultas Ilmu Komputer, Angkatan 2019 - 2023",
        "D3 Manajemen Informatika, Politeknik Negeri Bandung, Lulus tahun 2022 dengan IPK 3.75",
        "SMK Negeri 1 Jurusan Rekayasa Perangkat Lunak (RPL), Lulus tahun 2021 dengan nilai rata-rata 88.5",
        "S1 Ilmu Komputer, Universitas Gadjah Mada (UGM), Skripsi: Klasifikasi Citra Medis Berbasis CNN",
        "Sarjana Desain Komunikasi Visual (DKV), Fakultas Seni Rupa dan Desain, Lulus tahun 2022, IPK 3.68",
        "D4 Teknik Informatika / Sarjana Terapan Komputer, Politeknik Elektronika Negeri Surabaya (PENS)",
        "S1 Teknik Elektro, Universitas Diponegoro, Konsentrasi Sistem Tenaga dan Kendali Otomasi, IPK 3.60",
        "Mahasiswa S1 Teknik Informatika di Universitas Brawijaya semester akhir, IPK sementara 3.78",
        "SMA Negeri 8 Jakarta, Peminatan Matematika dan Ilmu Pengetahuan Alam (MIPA), Lulus 2020",
        "Magister Ilmu Komputer (S2), Fakultas Ilmu Komputer Universitas Indonesia, IPK 3.90",
        "S1 Manajemen Bisnis, Sekolah Bisnis dan Manajemen ITB, Lulus dengan Predikat Sangat Memuaskan",
        "D3 Teknik Komputer dan Jaringan (TKJ), Politeknik Negeri Jakarta, Lulus tahun 2021",
        "Sarjana Akuntansi (S.Ak.), Fakultas Ekonomi dan Bisnis Universitas Padjadjaran, IPK 3.74",
        "S1 Sistem Komputer, Institut Teknologi Sepuluh Nopember (ITS), Konsentrasi Internet of Things",
        "SMK Negeri 2 Jurusan Teknik Komputer dan Jaringan, Lulusan berprestasi peringkat 1 kejuruan",
        "Sarjana Hukum (S.H.), Fakultas Hukum Universitas Airlangga, Angkatan 2018 - 2022",
        "Pendidikan formal S1 Statistika Terapan dan Sains Data, Fakultas MIPA, IPK 3.85 / 4.00",
        "S1 Pendidikan Teknologi Informasi, Fakultas Ilmu Pendidikan dan Keguruan, Lulus 2023",
        "Pendidikan Profesi Insinyur (PPI), Persatuan Insinyur Indonesia, Lulus dengan Sertifikasi Pratama",
        "D3 Akuntansi dan Keuangan Perbankan, Politeknik Negeri Semarang, Lulus 2020 dengan IPK 3.69",
        "Sarjana Sains (S.Si.) Matematika, Fakultas Sains dan Matematika Universitas Sebelas Maret",
        "S1 Rekayasa Perangkat Lunak, Telkom University Bandung, Lulus 2023 dengan predikat Cum Laude",
        "Kuliah S1 Sistem Informasi di Universitas Bina Nusantara (BINUS), Konsentrasi E-Business, IPK 3.80",
        "SMA Negeri 1 Yogyakarta, Jurusan IPA, Lulus dengan nilai ujian sekolah berpredikat memuaskan",
        "D4 Manajemen Perhotelan dan Pariwisata, Sekolah Tinggi Pariwisata, Lulus tahun 2021",
        "Program Studi S1 Farmasi Klinis, Fakultas Farmasi, Menyelesaikan tugas akhir formulasi obat",
        "Sarjana Psikologi (S.Psi.), Fakultas Psikologi Universitas Negeri Jakarta, IPK 3.67",
        "Riwayat pendidikan sekolah: Menyelesaikan studi sarjana teknik telekomunikasi periode 2019-2023",
        "Lulusan sarjana teknik industri dengan fokus riset manajemen rantai pasok dan operasional pabrik",
        "Bachelor of Science in Computer Science, State University, GPA 3.85 / 4.00, Graduated Magna Cum Laude",
        "Master of Science in Information Systems, National Institute of Technology, Graduated with Honors 2023",
        "Bachelor of Engineering in Electrical Engineering, Faculty of Engineering, Final Thesis: Embedded IoT Systems",
        "Bachelor of Science in Accounting, School of Business and Economics, GPA 3.82, Dean's List",
        "Master of Business Administration (MBA), Concentration in Finance and Corporate Strategy, Graduated 2022",
        "Bachelor of Science in Finance and Banking, Department of Economics, Academic Honors",
        "Bachelor of Arts in Psychology, School of Social Sciences, GPA 3.75, Focus on Organizational Psychology",
        "Bachelor of Science in Human Resource Management, Faculty of Business Administration, Graduated 2021",
        "Bachelor of Arts in Communication and Public Relations, School of Media, GPA 3.70",
        "Bachelor of Business Administration, Major in Marketing and Consumer Behavior, Class of 2023",
        "Bachelor of Science in Nursing (BSN), School of Nursing and Health Sciences, Licensed RN, GPA 3.80",
        "Doctor of Medicine (M.D.), Faculty of Medicine, Completed clinical rotations with distinction",
        "Bachelor of Pharmacy (B.Pharm), Department of Pharmaceutical Sciences, Graduated 2022",
        "Associate Degree in Business Administration and Office Management, State College, GPA 3.65",
        "Bachelor of Science in Supply Chain Management and Logistics, School of Industrial Management",
        "Bachelor of Education (B.Ed.) in Secondary Education, Department of Pedagogy, Graduated with Honors",
        "Master of Arts in Educational Leadership and Curriculum Development, School of Education",
        "Bachelor of Laws (LL.B.), Faculty of Law, Concentration in Commercial and Corporate Law, GPA 3.72",
        "Master of Laws (LL.M.) in Corporate Governance and International Trade Law, Graduated 2023",
        "S1 Teknik Informatika, Institut Teknologi Bandung (ITB), IPK 3.82 / 4.00, Lulus dengan Predikat Cum Laude",
        "Sarjana Sistem Informasi, Universitas Indonesia (UI), Fakultas Ilmu Komputer, Angkatan 2019 - 2023",
        "D3 Teknik Komputer dan Jaringan, Politeknik Negeri Bandung, Lulus dengan IPK 3.70",
        "Sarjana Akuntansi (S.Ak.), Fakultas Ekonomi dan Bisnis Universitas Gadjah Mada (UGM), IPK 3.85, Cum Laude",
        "S1 Manajemen Keuangan dan Perbankan, Universitas Diponegoro, Lulus dengan Predikat Sangat Memuaskan",
        "Pendidikan Profesi Akuntan (PPAk), Universitas Padjadjaran, Lulus Ujian Sertifikasi Akuntan Publik",
        "Sarjana Psikologi (S.Psi.), Fakultas Psikologi Universitas Airlangga, Konsentrasi Psikologi Industri dan Organisasi",
        "S1 Administrasi Publik, Fakultas Ilmu Administrasi Universitas Brawijaya, Lulus tahun 2022, IPK 3.68",
        "S1 Ilmu Komunikasi, Universitas Sebelas Maret, Konsentrasi Manajemen Hubungan Masyarakat dan Periklanan",
        "Sarjana Desain Komunikasi Visual (DKV), Institut Seni Indonesia, Lulus tahun 2022, IPK 3.72",
        "Profesi Ners dan S1 Ilmu Keperawatan, Fakultas Ilmu Kesehatan Universitas Indonesia, IPK 3.80",
        "Sarjana Farmasi (S.Farm.), Fakultas Farmasi Universitas Hasanuddin, Skripsi formulasi sediaan farmasi",
        "Pendidikan Dokter (S.Ked), Fakultas Kedokteran Universitas Sumatera Utara, Lulus Ujian Kompetensi Dokter",
        "D3 Administrasi Bisnis / Kesekretariatan, Politeknik Negeri Jakarta, Lulus tahun 2021 dengan IPK 3.75",
        "S1 Teknik Logistik dan Manajemen Rantai Pasok, Universitas Pertamina, IPK 3.65",
        "Sarjana Pendidikan (S.Pd.) Pendidikan Guru Sekolah Dasar (PGSD), Universitas Pendidikan Indonesia (UPI)",
        "S1 Pendidikan Bahasa dan Sastra Inggris, Fakultas Bahasa dan Seni Universitas Negeri Yogyakarta",
        "Sarjana Hukum (S.H.), Fakultas Hukum Universitas Padjadjaran, Konsentrasi Hukum Bisnis dan Perdata, IPK 3.78",
        "Magister Kenotariatan (M.Kn.), Program Pascasarjana Fakultas Hukum Universitas Diponegoro",
    ],
    "experience": [
        "Senior Frontend Developer at PT Telkom Indonesia Tbk (Jan 2022 - Present): Led Next.js migration for 2M active users.",
        "Backend Engineer at Tokopedia (Full-time, 2021 - 2023): Architected checkout microservices processing 15k RPM on Go.",
        "Full Stack Developer at Shopee Indonesia: Engineered vendor analytics dashboard, cutting load latency by 45%.",
        "Software Engineer at Microsoft Corporation: Developed scalable Azure cloud services and enterprise API endpoints.",
        "Data Scientist at GoTo Financial: Built and deployed production fraud detection ML pipeline achieving 99.1% accuracy.",
        "DevOps Engineer at PT Djarum (2020 - 2022): Provisioned Kubernetes clusters with Terraform and automated CI/CD pipelines.",
        "Lead Mobile Developer at PT Karya Digital Nusantara: Supervised 5 engineers building Flutter cross-platform applications.",
        "UI/UX Designer at Traveloka: Spearheaded design of multi-city flight booking interface, boosting conversions by 22%.",
        "QA Automation Engineer at Blibli.com: Wrote 600+ automated regression suites using Playwright and Jest in GitHub Actions.",
        "Cloud Solutions Architect at Amazon Web Services (AWS): Consulted enterprise clients on serverless cloud architecture.",
        "Site Reliability Engineer (SRE) at Stripe: Maintained 99.999% uptime across global high-volume payment processing nodes.",
        "Technical Lead at PT Bank Central Asia Tbk (BCA): Managed squad of 10 developers modernizing core banking service APIs.",
        "Junior Web Developer at PT Inovasi Solusi Media: Built and maintained custom client portals with Laravel and React.",
        "Machine Learning Engineer at NVIDIA: Optimized GPU tensor acceleration pipelines for real-time computer vision inference.",
        "Associate Product Manager at Grab Indonesia: Conducted user interviews and drafted technical product requirement specs.",
        "Database Administrator at PT Telekomunikasi Selular: Administered multi-node Oracle RAC and PostgreSQL clusters.",
        "Security Operations Center (SOC) Analyst at PT Cyber Defense: Analyzed SIEM security alerts and handled cyber incidents.",
        "Engineering Manager at Uber: Managed engineering roadmaps, conducted quarterly performance reviews, and scaled team to 20.",
        "IT Support Specialist at PT Astra International Tbk: Provided technical hardware/software troubleshooting for 300 staff.",
        "Senior Backend Engineer at PT Finansial Pintar: Built core double-entry accounting engine handling daily bank disbursements.",
        "Frontend Engineer at ByteDance: Developed interactive creator tools and video upload modules using React and WebAssembly.",
        "Scrum Master at PT XL Axiata Tbk: Facilitated bi-weekly sprint planning, daily standups, and retrospective reviews.",
        "ERP Consultant at Ernst & Young (EY): Implemented SAP S/4HANA financial accounting modules for multinational retail client.",
        "Software Engineer Intern at Google: Developed internal developer metrics tooling using Go, gRPC, and Google Cloud Platform.",
        "Application Support Engineer at PT Bank Negara Indonesia (BNI): Handled production incident triage under strict 15-minute SLA.",
        "Full Stack Developer at Startup Inc (Contract): Built MVP marketplace web platform with Next.js, Prisma, and Stripe.",
        "System Administrator at PT Global Mediatama: Managed on-premise Linux CentOS server clusters and VMware virtual machines.",
        "Senior Mobile Engineer at Bukalapak: Refactored payment SDK in Kotlin and Swift, reducing crash rate from 1.2% to 0.05%.",
        "Technical Writer & Developer Advocate at Twilio: Authored technical documentation, SDK guides, and sample applications.",
        "Cybersecurity Consultant at PwC Indonesia: Performed vulnerability assessments and ISO 27001 readiness reviews.Senior Backend Developer di PT Inovasi Solusi Digital (Januari 2022 - Sekarang): Merancang REST API skala enterprise.",
        "Bekerja sebagai Frontend Engineer di PT Telkom Akses: Membangun dashboard pemantauan jaringan fiber optik nasional.",
        "Full Stack Engineer di Startup Fintech Unicorn: Mengembangkan fitur autentikasi dua faktor (2FA) dan dompet digital.",
        "Staff IT dan Administrator Jaringan di PT Astra International Tbk: Mengelola 250 unit workstation dan server kantor cabang.",
        "Senior Data Analyst di PT Bank Mandiri (Persero) Tbk: Menyusun model analitik prediksi churn nasabah kartu kredit korporat.",
        "Bekerja sebagai Lead Mobile Developer di PT Karya Aplikasi Nusantara: Memimpin tim pengembang aplikasi Flutter.",
        "Magang sebagai Web Developer selama 6 bulan di PT Teknologi Maju Bersama: Membangun modul presensi pegawai berbasis PHP.",
        "Software Engineer di PT Bukalapak.com: Memelihara sistem indeks katalog produk menggunakan Elasticsearch dan Kafka.",
        "Technical Lead di PT Bank Central Asia Tbk (BCA): Mengkoordinasikan arsitektur microservices settlement transaksi harian.",
        "DevOps Engineer di PT Sinarmas Land: Menerapkan container orchestration Docker Kubernetes dan pipeline Gitlab CI/CD.",
        "Bekerja sebagai QA Automation Engineer di PT Fintek Karya Nusantara (LinkAja): Mengotomasi pengujian API dengan Postman.",
        "Database Administrator di PT Telekomunikasi Selular (Telkomsel): Bertanggung jawab atas replikasi database PostgreSQL.",
        "Staff Pengembang Perangkat Lunak di Dinas Komunikasi dan Informatika (Diskominfo): Membangun aplikasi layanan publik warga.",
        "Bekerja sebagai Konsultan IT di PricewaterhouseCoopers (PwC) Indonesia: Melakukan audit kepatuhan tata kelola teknologi.",
        "UI/UX Designer di PT Media Nusantara Citra (MNC): Merancang antarmuka mobile portal berita live streaming berkecepatan tinggi.",
        "Senior System Administrator di PT Indosat Ooredoo Hutchison: Mengelola klaster server Linux RedHat dan firewall jaringan.",
        "Full Stack Developer di Agensi Digital Kreasi: Menyelesaikan 15+ proyek website e-commerce klien korporat tepat waktu.",
        "Bekerja sebagai Scrum Master di PT XL Axiata Tbk: Memfasilitasi upacara sprint agile dan menghapus hambatan kerja tim.",
        "Machine Learning Engineer di PT Surya Teknologi: Membangun pipeline deteksi anomali transaksi perbankan secara realtime.",
        "Spesialis ERP SAP di PT Unilever Indonesia Tbk: Melakukan kustomisasi modul logistik dan supply chain inventaris pabrik.",
        "Senior Account Executive Software di PT Solusi Komputindo: Mencapai 130% target penjualan solusi software akuntansi cloud.",
        "Security Analyst di PT Cyber Defense Nusantara: Memantau log SIEM dan menanggulangi insiden keamanan siber perusahaan.",
        "Junior Software Engineer di PT Global Loyalty Indonesia: Mengembangkan API point reward pelanggan menggunakan Node.js.",
        "Bekerja sebagai Application Support di PT Bank Danamon Indonesia Tbk: Menangani tiket eskalasi gangguan core banking tier 2.",
        "Cloud Solutions Architect di PT Multipolar Technology Tbk: Merancang migrasi server on-premise nasabah perbankan ke AWS.",
        "Bekerja sebagai Web Programmer di Rumah Sakit Umum Pusat: Membangun modul pendaftaran poliklinik online dan antrean pasien.",
        "Senior Frontend Developer di PT Tiket.com: Mengoptimasi kecepatan first contentful paint (FCP) halaman checkout pemesanan.",
        "Kepala Departemen IT di PT Mitra Sarana Industri: Memimpin divisi teknologi informasi beranggotakan 12 orang staf IT.",
        "Staff QA Manual di PT Asuransi Jiwa Generali: Membuat dokumen test scenario dan memverifikasi bug pada aplikasi klaim online.",
        "Bekerja sebagai Software Engineer di PT Astra Digital: Mengembangkan backend microservices pemesanan mobil bekas terverifikasi.",
        "Senior Frontend Developer at PT Telkom Indonesia Tbk (Jan 2022 - Present): Led Next.js migration for 2M active users.",
        "Backend Engineer at Tokopedia: Architected checkout microservices processing 15k RPM on Go and PostgreSQL.",
        "DevOps Engineer at Cloud Solutions Inc: Provisioned Kubernetes clusters with Terraform and automated CI/CD.",
        "Senior Financial Accountant at Standard Chartered Bank: Reconciled 150+ ledger accounts and prepared monthly balance sheets.",
        "Tax Specialist at KPMG: Prepared annual corporate tax returns and handled cross-border transfer pricing documentation.",
        "Internal Audit Associate at Ernst & Young (EY): Evaluated operational financial risk controls across 12 multinational clients.",
        "Human Resources Generalist at Unilever: Managed employee onboarding, annual performance reviews, and dispute resolution.",
        "Talent Acquisition Specialist at Shopee: Recruited and closed 40+ strategic roles with average time-to-hire of 20 days.",
        "Digital Marketing Lead at Traveloka: Managed $100k monthly advertising budget across Meta and Google, delivering 4.5x ROAS.",
        "Senior Account Executive at Salesforce: Pitched enterprise CRM software solutions and achieved 125% of annual sales quota.",
        "Registered Clinical Nurse at Metropolitan General Hospital: Delivered patient nursing care in emergency ward under triage protocol.",
        "Clinical Pharmacist at CVS Health: Dispensed medications, reviewed drug interactions, and counseled 80+ patients daily.",
        "Executive Office Administrator at PT Astra International Tbk: Managed executive travel, confidential correspondence, and supply purchasing.",
        "Supply Chain Specialist at DHL Global Logistics: Coordinated multimodal freight customs clearance and shipping routes.",
        "High School Mathematics Teacher at National Academy: Instructed 150 students and increased departmental pass rate by 18%.",
        "University Lecturer at Faculty of Business: Delivered undergraduate corporate finance courses and supervised 15 final theses.",
        "Corporate Legal Counsel at PT Sinarmas Group: Drafted commercial vendor contracts, non-disclosure agreements, and joint ventures.",
        "Regulatory Compliance Specialist at Citibank: Audited banking compliance protocols against central bank regulatory standards.",
        "Senior Backend Developer di PT Inovasi Solusi Digital (Januari 2022 - Sekarang): Merancang REST API skala enterprise.",
        "Full Stack Engineer di Startup Fintech Unicorn: Mengembangkan fitur autentikasi dua faktor (2FA) dan gateway pembayaran.",
        "Staff IT dan Administrator Jaringan di PT Karya Digital Nusantara: Mengelola 200 workstation dan firewall jaringan.",
        "Senior Financial Accountant di PT Bank Mandiri (Persero) Tbk: Merekonsiliasi transaksi kas dan pos aktiva bernilai Rp 40 Miliar.",
        "Staf Pajak dan Akuntansi di PT Indofood Sukses Makmur Tbk: Menyusun laporan SPT Masa PPh 21, 23, dan e-Faktur PPN tepat waktu.",
        "Auditor Junior di Kantor Akuntan Publik (KAP Tanubrata Sutanto): Melakukan audit kepatuhan keuangan pada 8 klien korporat.",
        "HR Generalist di PT Surya Semesta Mandiri: Mengelola administrasi payroll 250 karyawan dan pendaftaran BPJS Ketenagakerjaan.",
        "Talent Acquisition Officer di PT Bukalapak.com: Melakukan sourcing dan interview berbasis kompetensi untuk 50+ posisi staf.",
        "Digital Marketing Specialist di PT Retail Inovasi Niaga: Mengelola kampanye Meta Ads dan Google Ads dengan capaian omzet Rp 1.5 Miliar.",
        "Sales Supervisor di PT Mayora Indah Tbk: Memimpin tim 12 staf sales retail dan melampaui target omzet kuartalan 115%.",
        "Perawat Pelaksana di Rumah Sakit Umum Daerah (RSUD) Tugurejo: Memberikan asuhan keperawatan dan pemantauan tanda vital 20 pasien.",
        "Apoteker Pengelola Apotek di Kimia Farma Apotek: Bertanggung jawab atas pengelolaan stok obat, peracikan resep, dan konseling obat.",
        "Staf Administrasi & General Affairs di PT Pos Indonesia: Mengelola petty cash operasional kantor dan pengadaan inventaris ATK.",
        "Koordinator Operasional Gudang di PT JNE Express: Mengawasi alur keluar masuk 5.000 paket harian dan akurasi surat jalan.",
        "Guru Kelas di SD Negeri Unggulan: Menyusun modul pembelajaran tematik Kurikulum Merdeka dan memfasilitasi 28 siswa sekolah dasar.",
        "Dosen Tetap di Fakultas Ekonomi Universitas Padjadjaran: Mengajar mata kuliah Akuntansi Keuangan Menengah dan membimbing skripsi.",
        "Staf Legal Officer di PT Telekomunikasi Selular (Telkomsel): Meninjau draf perjanjian kerja sama sewa lahan pemancar seluler.",
        "Asisten Notaris di Kantor Notaris & PPAT Rekanan: Menyusun akta perjanjian kredit, jual beli tanah, dan legalisasi berkas legal.",
    ],
    "organizations": [
        "President of the Computer Science Student Association (HMIF): Led 45 executive committee members and managed 12 programs.",
        "Head of Technology and Research Division at Campus Developer Student Club: Organized 15 coding workshops for 400+ students.",
        "Event Director for National Collegiate Hackathon 2023: Managed 300 participants, 20 judges, and $15,000 corporate sponsor budget.",
        "Secretary General at University Student Executive Board (BEM): Drafted official organization correspondence and legal decrees.",
        "Core Team Lead at Google Developer Student Clubs (GDSC): Led campus tech talks, Android study jams, and cloud certifications.",
        "Volunteer Instructor at Indonesia Mengajar: Taught basic digital literacy and introductory coding to underprivileged youth.",
        "Treasurer for English Debate Society: Managed $8,000 annual operational budget and published monthly financial audit reports.",
        "Head of Logistics & Equipment for Annual Engineering Campus Festival: Coordinated setup for 2,500 daily attendees.",
        "Community Manager at Open Source Jakarta: Moderated 2,000+ developer members and planned quarterly engineering meetups.",
        "Vice President of IEEE University Student Branch: Coordinated industrial technical visits to tech multinational headquarters.",
        "Head of Public Relations for Campus TEDx Conference: Handled media sponsorships and coordinated speaker hospitality.",
        "Active Member of University Autonomous Robotics Club: Competed in national aerial drone search-and-rescue competition.",
        "Volunteer Coordinator for International Youth Model United Nations (MUN): Guided 120 foreign delegates and protocol sessions.",
        "Chief Coordinator of Campus Freshmen Welcoming Orientation: Supervised 80 student mentors welcoming 1,200 incoming freshmen.",
        "Head of Creative Media and Publications at Student Union: Directed graphic design, videography, and social media campaigns.",
        "Peer Academic Tutor at University Learning Center: Conducted weekly calculus and discrete mathematics review sessions.",
        "Director of External Relations for AIESEC Campus Chapter: Established international youth exchange partnerships with 8 NGOs.",
        "Head of Community Service Division at Student Council: Initiated coastal mangrove planting and village solar panel drive.",
        "Member of University Competitive Programming Team: Represented campus in ACM-ICPC Asia Regional Contest.",
        "Committee Lead for Campus Career Expo 2023: Liaised with 40 hiring corporate employers and managed 5,000 jobseeker visitors.",
        "Head of Sports and Arts Division at Faculty Student Association: Organized inter-departmental sports tournament for 800 athletes.",
        "Volunteer Medical and First Aid Coordinator for Red Cross Student Corps during emergency disaster relief response.",
        "President of Campus Music Club: Produced annual musical concert attended by 1,500 students and alumni.",
        "Lead Organizer for University Web Development Bootcamp: Mentored 50 beginner students in building their first HTML/CSS web apps.",
        "Staff of Advocacy and Student Welfare Department at BEM: Assisted 30+ students in resolving university tuition payment appeals.",
        "Head of Sponsorship Division for National Business Plan Competition: Successfully raised $10,000 from banking sponsors.",
        "Volunteer English Teacher at Community Youth Center: Conducted free conversational English classes for rural high schoolers.",
        "Member of Campus Cyber Security Club (CTF Team): Placed top 10 in national university Capture The Flag tournament.",
        "Secretary of University Environmental Conservation Club: Organized campus zero-single-use-plastic advocacy campaign.",
        "Head of Documentation & Broadcasting at University Graduation Committee: Directed live multicam video streaming of graduation.Ketua Himpunan Mahasiswa Informatika (HMIF) periode 2022 - 2023: Memimpin 50 pengurus aktif dan 10 program kerja tahunan.",
        "Ketua Divisi Riset dan Teknologi di BEM Fakultas: Menginisiasi kelas bimbingan pemrograman intensif dan pelatihan Git.",
        "Ketua Pelaksana Seminar Nasional Teknologi Informasi 2023: Mengelola 500 peserta umum dan pembicara praktisi industri.",
        "Sekretaris Jenderal Badan Eksekutif Mahasiswa (BEM) Universitas: Bertanggung jawab atas tata kelola persuratan dan arsip resmi.",
        "Bendahara Umum Panitia Festival Seni dan Budaya Kampus: Mengelola perputaran anggaran dana kegiatan sebesar 45 juta rupiah.",
        "Koordinator Divisi Hubungan Masyarakat (Humas) Paguyuban Mahasiswa: Menjalin komunikasi dengan pihak sponsor dan media partner.",
        "Koordinator Perlengkapan dan Lapangan pada Kegiatan Bakti Sosial Mahasiswa: Menyalurkan logistik bantuan ke wilayah bencana.",
        "Relawan Pengajar di Komunitas Belajar Anak Bangsa: Mengajarkan pengenalan komputer dan logika matematika bagi anak panti asuhan.",
        "Anggota Divisi Advokasi dan Kesejahteraan Mahasiswa BEM: Memfasilitasi banding keringanan uang kuliah tunggal (UKT) 40 mahasiswa.",
        "Ketua Panitia Masa Bimbingan Mahasiswa Baru (MABIM) Fakultas Teknik angkatan 2023: Mengkoordinasikan 70 orang panitia mahasiswa.",
        "Kepala Divisi Publikasi, Dokumentasi, dan Desain (Pubdok) Pameran Karya Teknologi: Merancang poster identitas visual pameran.",
        "Koordinator Tim Medis Korps Sukarela (KSR) Palang Merah Indonesia unit kampus: Bertugas dalam pertolongan pertama kegiatan outdoor.",
        "Pengurus Unit Kegiatan Mahasiswa (UKM) Paduan Suara: Menjabat sebagai manajer konser tahunan dan kompetisi paduan suara.",
        "Anggota Divisi Dana Usaha (Danus) Kepanitiaan Wisuda Universitas: Menggalang dana mandiri sebesar 18 juta rupiah melalui sponsorship.",
        "Staff Ahli Departemen Luar Negeri Himpunan Mahasiswa: Membangun relasi studi banding dengan organisasi mahasiswa luar daerah.",
        "Ketua Komunitas Linux dan Open Source Mahasiswa: Menyelenggarakan workshop instalasi Linux Ubuntu dan pengenalan command line.",
        "Sekretaris Panitia Pemilihan Umum Raya (PEMIRA) Kampus: Mengorganisir jalannya pemungutan suara elektronik ketua BEM.",
        "Relawan Tim Tanggap Bencana Mahasiswa: Mendistribusikan sembako dan mendirikan tenda darurat penampungan korban gempa bumi.",
        "Pengurus Divisi Komunikasi dan Informasi BEM: Mengelola konten publikasi akun Instagram resmi organisasi dengan 10.000 pengikut.",
        "Koordinator Acara Lomba Hackathon Pelajar SMA/SMK se-Jabodetabek: Menyusun rundown kompetisi, teknis penjurian, dan sertifikasi.",
        "Anggota Aktif Tim Robotika Kampus Divisi Mekanik: Merancang rangka robot pemadam api untuk Kontes Robot Indonesia (KRI).",
        "Ketua Klub Debat Bahasa Inggris Mahasiswa: Mengkoordinasikan latihan debat mingguan berstandar British Parliamentary.",
        "Pengurus Paguyuban Beasiswa Bank Indonesia (GenBI): Mengkoordinasikan program edukasi literasi keuangan dan QRIS ke masyarakat.",
        "Kepala Biro Rumah Tangga dan Kesekretariatan Senat Mahasiswa: Mengelola inventaris peralatan kantor dan ruang sidang ormawa.",
        "Koordinator Keamanan dan Ketertiban Kampus pada Sidang Terbuka Senat: Memastikan kelancaran protokol acara wisuda 1.000 wisudawan.",
        "Relawan Pengajar Gerakan Mengajar Desa: Mengabdi selama 1 bulan mengajar literasi baca tulis di sekolah pelosok terpencil.",
        "Staff Divisi Kemitraan Komunitas di Google Developer Student Clubs: Menghubungkan pembicara workshop dengan komunitas teknologi.",
        "Ketua Seksi Konsumsi dan Akomodasi Musyawarah Nasional Mahasiswa: Mengatur konsumsi 200 delegasi mahasiswa se-Indonesia.",
        "Pengurus Himpunan Profesi Akuntansi Mahasiswa Divisi Penelitian: Mengadakan riset tren adopsi teknologi akuntansi di era digital.",
        "Koordinator Pendaftaran dan Registrasi Peserta pada Konferensi Akademik Internasional yang diselenggarakan universitas.",
        "President of the Computer Science Student Association: Led 45 executive committee members and managed 12 technical programs.",
        "Core Team Lead at Google Developer Student Clubs: Organized campus tech talks, Android workshops, and cloud certification jams.",
        "Treasurer for National Student Finance Association: Managed $15,000 annual operational budget and published audit reports.",
        "President of Campus Investment Club: Managed simulated equity portfolio of $50k and hosted financial literacy seminars.",
        "Head of Human Capital Division at AIESEC University Chapter: Coordinated recruitment and talent development of 60 members.",
        "Volunteer Coordinator for Youth Leadership Forum: Guided 120 regional student delegates during weekend leadership retreat.",
        "Head of Public Relations for Campus TEDx Conference: Handled corporate sponsorships and managed local press coverage.",
        "Director of Media & Communications for International Model UN: Supervised content creation team of 10 graphic designers.",
        "Volunteer Healthcare Assistant at Red Cross Student Corps: Coordinated community blood drives collecting 400 pints of blood.",
        "President of Student Medical Association: Organized rural health screening camps providing free consultations to 500 villagers.",
        "President of University Moot Court Society: Coordinated regional moot court competition and mock trial hearings.",
        "Chief Adjudicator for National University Debate Championship: Managed tournament judging pool of 60 collegiate adjudicators.",
        "Peer Academic Tutor at University Learning Center: Tutored 40 underclassmen in financial accounting and microeconomics.",
        "Volunteer Instructor at Community Education Program: Taught basic literacy and numeracy to underprivileged rural children.",
        "Ketua Himpunan Mahasiswa Informatika (HMIF) periode 2022 - 2023: Memimpin 50 pengurus aktif dan 10 program kerja tahunan.",
        "Ketua Divisi Riset dan Teknologi di BEM Fakultas: Menginisiasi kelas pelatihan teknologi informasi dan bimbingan belajar mahasiswa.",
        "Bendahara Umum Panitia Festival Seni dan Budaya Kampus: Mengelola perputaran anggaran dana kegiatan sebesar 45 juta rupiah.",
        "Pengurus Paguyuban Beasiswa Bank Indonesia (GenBI): Mengkoordinasikan program edukasi literasi keuangan dan sosialisasi QRIS.",
        "Sekretaris Jenderal Badan Eksekutif Mahasiswa (BEM) Universitas: Bertanggung jawab atas tata kelola persuratan dinas dan arsip resmi.",
        "Kepala Biro Pengembangan Sumber Daya Organisasi: Mengadakan pelatihan kepemimpinan dan manajemen organisasi untuk pengurus.",
        "Koordinator Divisi Hubungan Masyarakat (Humas) Paguyuban Mahasiswa: Menjalin komunikasi dengan 12 pihak sponsor dan media partner.",
        "Kepala Divisi Publikasi dan Dokumentasi Pameran Karya Kreatif: Mengkoordinasikan peliputan media massa dan promosi media sosial.",
        "Koordinator Tim Medis Korps Sukarela (KSR) Palang Merah Indonesia unit kampus: Bertugas dalam pertolongan pertama kegiatan lapangan.",
        "Relawan Tim Tanggap Bencana Mahasiswa: Menyalurkan logistik obat-obatan dan mendirikan posko kesehatan pengungsi banjir.",
        "Ketua Lembaga Pengkajian Hukum Mahasiswa: Mengkoordinasikan kajian berkala mengenai undang-undang ketenagakerjaan dan advokasi.",
        "Sekretaris Panitia Musyawarah Besar Anggota: Menyusun draft tata tertib sidang dan mengarsipkan risalah ketetapan sidang.",
        "Relawan Pengajar di Komunitas Belajar Anak Bangsa: Mengajarkan pengenalan membaca, berhitung, dan budi pekerti anak panti asuhan.",
        "Ketua Seksi Edukasi dan Pengabdian Masyarakat: Menyelenggarakan program pengajaran calistung gratis bagi anak-anak desa pesisir.",
    ],
    "skills": [
        "Programming Languages: Python, Go (Golang), JavaScript, TypeScript, Java, C++, Rust, PHP, C#, SQL",
        "Frontend Frameworks: React, Next.js, Vue.js, Angular, Svelte, Tailwind CSS, Bootstrap 5, Redux Toolkit",
        "Backend & APIs: Node.js, Express, FastAPI, Django, Spring Boot, Laravel, NestJS, gRPC, RESTful APIs, GraphQL",
        "Databases & Storage: PostgreSQL, MySQL, MariaDB, MongoDB, Redis, Elasticsearch, DynamoDB, Supabase, SQLite",
        "Cloud Platforms: Amazon Web Services (AWS EC2, S3, RDS, Lambda), Google Cloud Platform (GCP), Microsoft Azure",
        "DevOps & Containers: Docker, Kubernetes, Helm, Terraform, Ansible, Docker Compose, Linux Administration",
        "CI/CD Tools: GitHub Actions, GitLab CI/CD, Bitbucket Pipelines, Jenkins, Git CLI, Gitflow workflow",
        "Testing & QA: Jest, Pytest, Cypress, Playwright, Selenium WebDriver, Postman API Testing, k6 Load Testing",
        "Mobile Development: Flutter, Dart, React Native, Android Studio, Kotlin, iOS Swift, SwiftUI, Xcode",
        "Data Science & AI: Pandas, NumPy, Scikit-Learn, PyTorch, TensorFlow, OpenCV, Hugging Face Transformers, Power BI",
        "UI/UX Design Tools: Figma, Adobe XD, Sketch, Whimsical, Miro, Photoshop, Illustrator, InVision Wireframing",
        "Project Tools: Jira, Confluence, Trello, Asana, Notion Workspace, Slack, Linear, ClickUp",
        "Messaging Queues: Apache Kafka, RabbitMQ, Celery task queue, Redis Pub/Sub, AWS SQS",
        "Web Servers & Networking: Nginx reverse proxy, Apache HTTP Server, Cloudflare CDN, DNS, TCP/IP, SSL/TLS",
        "Security Proficiencies: OAuth 2.0, OpenID Connect, JWT tokens, Role-Based Access Control (RBAC), OWASP Top 10",
        "Data Engineering: Apache Spark, Apache Airflow DAGs, Snowflake, Google BigQuery, dbt data modeling",
        "Hardware & Embedded: Arduino IDE, ESP32, Raspberry Pi, MQTT protocol, Microcontrollers, I2C / SPI sensors",
        "Engineering Practices: Test-Driven Development (TDD), Object-Oriented Design (OOP), Domain-Driven Design (DDD)",
        "Monitoring Tools: Prometheus, Grafana dashboards, ELK Stack (Logstash, Kibana), Datadog, Sentry tracking",
        "Architectural Patterns: Microservices Architecture, Event-Driven Architecture, Serverless, Modular Monolith",
        "Performance Optimization: Lighthouse audits, Core Web Vitals optimization, Asset bundling with Vite and Webpack",
        "Search Technologies: Elasticsearch indexing, Algolia, MeiliSearch, BM25 text ranking, Vector embeddings",
        "Operating Systems: Ubuntu Linux, Debian, CentOS, macOS, Windows Server, Bash shell scripting",
        "Database Tuning: Query execution plans, index optimization, query caching, connection pooling PgBouncer",
        "Container Skills: Kubernetes deployments, services, ingress routing, ConfigMaps, secrets, and pod scaling",
        "API Standards: OpenAPI Specification, Swagger UI documentation, Postman collections, REST API versioning",
        "Mobile State Management: Flutter BLoC pattern, Riverpod, Provider, React Native Redux Toolkit, Context API",
        "Agile Skills: Scrum framework, Kanban boards, sprint capacity estimation, user story mapping, backlog grooming",
        "Language Skills: English (Fluent professional proficiency, TOEFL 600), Indonesian (Native speaker)",
        "Soft Skills: Cross-functional collaboration, technical mentorship, analytical problem-solving, stakeholder communication",
        "Bahasa Pemrograman: Python, PHP, JavaScript, TypeScript, Dart, Java, C#, SQL, HTML5, CSS3",
        "Framework Web: Laravel, CodeIgniter 4, React.js, Next.js, Express.js, Vue.js, Tailwind CSS, Bootstrap",
        "Sistem Basis Data: MySQL, PostgreSQL, MariaDB, Microsoft SQL Server, Redis cache, Firebase Firestore",
        "Alat DevOps & Infrastruktur: Git Version Control, Docker Container, Postman API Testing, Linux Ubuntu, Nginx",
        "Keahlian Arsitektur Web: Perancangan Arsitektur REST API, Object-Oriented Programming (OOP), Model-View-Controller (MVC)",
        "Keahlian Desain UI/UX: Desain Figma, Wireframing Prototipe Interaktif, Panduan Desain Sistem (Design System)",
        "Keahlian Analisis Data: Pengolahan Data Excel Lanjutan (VLOOKUP, Pivot Table), SQL Querying, Tableau, Power BI",
        "Jaringan Komputer: Konfigurasi Router Mikrotik, Cisco CCNA Routing & Switching, TCP/IP, Troubleshooting Jaringan",
        "Metodologi Software: Agile Scrum Framework, Papan Kanban, Sprint Planning, Manajemen Backlog Jira",
        "Keahlian Pengujian Software: Unit Testing otomatis dengan Pytest dan Jest, Integration Testing, Playwright E2E",
        "Integrasi Gateway: Pengalaman implementasi API pembayaran Midtrans, Xendit, Stripe, Doku, dan PayPal",
        "Keahlian Keamanan IT: Konsep Autentikasi OAuth2, JSON Web Token (JWT), Enkripsi SSL/TLS, Audit OWASP Top 10",
        "Administrasi Server: Pengelolaan Server Linux Ubuntu dan CentOS, Virtual Host Nginx, Crontab Automation, SSH",
        "Pengembangan Mobile: Pembuatan aplikasi Android dan iOS menggunakan Flutter, Dart, Android Studio, SQLite",
        "Software Desain & Grafis: Penguasaan Adobe Photoshop, Adobe Illustrator, Premiere Pro video editing, Canva Pro",
        "Keahlian Administrasi Kantor: Microsoft Office (Word, Excel, PowerPoint), Google Workspace, Pengelolaan Dokumen",
        "Keahlian Bahasa: Bahasa Indonesia (Penutur Asli), Bahasa Inggris (Kecakapan Profesional, Skor TOEFL 580)",
        "Hosting & Cloud: Layanan cPanel hosting, VPS DigitalOcean, AWS EC2, Google Cloud Storage, Cloudflare CDN",
        "Teknologi NLP: Ekstraksi fitur TF-IDF, tokenisasi teks bahasa Indonesia, klasifikasi sentimen IndoBERT",
        "Message Broker: Pengalaman menggunakan antrean Redis Pub/Sub, RabbitMQ, dan background job worker",
        "Keahlian IoT: Pemrograman mikrokontroler Arduino, sensor ESP8266/ESP32, protokol komunikasi data MQTT",
        "Optimasi Database: Normalisasi tabel basis data, pembuatan index query, transaksi ACID, stored procedure",
        "Keterampilan Interpersonal (Soft Skills): Komunikasi Efektif, Kepemimpinan Tim, Manajemen Waktu, Berpikir Kritis",
        "Audit Web & Performa: Pemantauan performa aplikasi web menggunakan Google Lighthouse dan Chrome DevTools",
        "Pertukaran Data: Mahir memanipulasi struktur data JSON, XML, Protocol Buffers, dan format CSV berukuran besar",
        "Keahlian Web Scraping: Ekstraksi data website otomatis menggunakan Python BeautifulSoup4 dan Selenium",
        "Fullstack Stack: Penguasaan ekosistem Node.js, Express, Prisma ORM, MongoDB (MERN Stack)",
        "Keahlian Kontainer: Pembuatan Dockerfile multi-stage build, docker-compose untuk database dan aplikasi",
        "Dokumentasi API: Penyusunan dokumentasi endpoint menggunakan Swagger UI dan koleksi Postman publik",
        "Pemecahan Masalah Teknis: Menganalisis log error sistem produksi, debugging kode kompleks, dan perbaikan bug darurat",
        "Programming Languages: Python, Go (Golang), JavaScript, TypeScript, Java, C++, SQL, HTML5, CSS3",
        "Frontend & Backend: React, Next.js, Node.js, Express, FastAPI, Django, Spring Boot, REST APIs",
        "Cloud & DevOps: Amazon Web Services (AWS), Docker, Kubernetes, Terraform, CI/CD GitHub Actions, Linux",
        "Accounting Standards: IFRS, US GAAP, General Ledger, Financial Statement Preparation, Bank Reconciliation",
        "Taxation & Compliance: Corporate Tax, VAT / Sales Tax, Payroll Tax Filing, Transfer Pricing, Tax Auditing",
        "Financial Software: SAP S/4HANA Finance, Oracle Financials, QuickBooks, Xero, Microsoft Excel (Advanced Modeling)",
        "Human Resources: Talent Acquisition, Full-Cycle Recruitment, Behavioral Interviewing, Employee Onboarding",
        "Compensation & Benefits: Payroll Processing, Performance Appraisal Systems, Labor Law Compliance, HR Policies",
        "HRIS & Tools: Workday, BambooHR, LinkedIn Recruiter, Jobvite, Greenhouse, Google Workspace",
        "Digital Marketing: Search Engine Optimization (SEO), Paid Search (Google Ads), Paid Social (Meta Ads Manager)",
        "Marketing Analytics: Google Analytics 4 (GA4), SEMrush, Ahrefs, HubSpot CRM, Conversion Rate Optimization (CRO)",
        "Sales Competencies: B2B Solution Selling, Account Management, Contract Negotiation, Pipeline Management",
        "Clinical Nursing Skills: Patient Triage, Vital Signs Monitoring, Medication Administration, Intravenous (IV) Therapy",
        "Medical Certifications: Basic Life Support (BLS), Advanced Cardiovascular Life Support (ACLS), HIPAA Compliance",
        "Medical Software: Epic Systems EHR, Cerner EMR, Electronic Health Records Documentation, Clinical Pharmacology",
        "Office Administration: Executive Calendar Scheduling, Travel Coordination, Petty Cash Management, Document Archiving",
        "Procurement & Supply Chain: Vendor Management, Purchase Order (PO) Processing, Inventory Control, ERP SAP Logistics",
        "Instructional Skills: Curriculum Design, Classroom Management, Student Assessment, Differentiated Instruction",
        "Educational Tools: Google Classroom, Canvas LMS, Blackboard, Kahoot, Interactive Smartboard Presentations",
        "Legal Proficiencies: Contract Drafting & Review, Due Diligence, Corporate Governance, Intellectual Property Filing",
        "Bahasa Pemrograman: Python, PHP, JavaScript, TypeScript, Dart, Java, C#, SQL, HTML5, CSS3",
        "Framework & Database: Laravel, CodeIgniter, React.js, Next.js, PostgreSQL, MySQL, Redis cache",
        "Alat & Infrastruktur: Git Version Control, Docker Container, Postman API Testing, Linux Ubuntu Server, Nginx",
        "Keahlian Akuntansi: PSAK/IFRS, Jurnal Penyesuaian, Rekonsiliasi Bank, Buku Besar, Penyusunan Laporan Laba Rugi & Arus Kas",
        "Perpajakan Indonesia: PPh Pasal 21, PPh 23, PPh 4(2), PPh Badan 25/29, PPN e-Faktur, Pengisian e-SPT, Sertifikasi Brevet AB",
        "Perangkat Lunak Akuntansi: SAP ERP Financials, Accurate Accounting, Zahir Accounting, Microsoft Excel Lanjutan (VLOOKUP, Pivot)",
        "Manajemen SDM: Talent Acquisition, Behavioral Event Interview (BEI), Onboarding Karyawan, Evaluasi Kinerja (KPI)",
        "Kompensasi & Regulasi: Payroll Karyawan, Perhitungan PPh 21, Administrasi BPJS Ketenagakerjaan & Kesehatan, UU Ketenagakerjaan",
        "Aplikasi HRIS: Talenta by Mekari, Darwinbox, Gadjian, Jobstreet Employer, LinkedIn Recruiter",
        "Pemasaran Digital: Meta Ads Manager, Google Search/Display Ads, TikTok Ads Manager, Optimasi SEO On-Page/Off-Page",
        "Keahlian Penjualan: Negosiasi Bisnis B2B, Manajemen Relasi Klien (CRM), Public Speaking, Penutupan Penjualan (Closing)",
        "Keahlian Keperawatan: Basic Trauma Cardiac Life Support (BTCLS), Perawatan Luka Modern, Terapi Cairan Infus, Patient Safety",
        "Sertifikasi Medis: Surat Tanda Registrasi (STR) Perawat Aktif, Sertifikat Pencegahan dan Pengendalian Infeksi (PPI)",
        "Sistem Informasi Kesehatan: Sistem Informasi Manajemen Rumah Sakit (SIMRS), Rekam Medis Elektronik (RME)",
        "Administrasi Perkantoran: Tata Kelola Surat Dinas, Pengarsipan Digital, Pengelolaan Kas Kecil (Petty Cash), Notulensi Rapat",
        "Operasional & Pengadaan: Pengadaan Barang/Jasa (Procurement), Penerbitan Purchase Order (PO), Manajemen Inventaris ATK",
        "Kompetensi Pendidik: Penyusunan Modul Ajar Kurikulum Merdeka, Manajemen Kelas Inklusif, Pembuatan Butir Soal Asesmen",
        "Keahlian Hukum: Penyusunan Perjanjian Kontrak (Legal Drafting), Legal Due Diligence, Perizinan Usaha OSS, Kepatuhan Regulasi",
    ],
    "projects": [
        "Project: E-Commerce Microservices Platform - Engineered scalable backend handling 50k daily active users with Go and PostgreSQL.",
        "Project: Real-Time Collaborative Workspace - Developed web-based document editing app utilizing WebSockets, React, and Redis Pub/Sub.",
        "Open-Source Project: CLI Scaffolding Tool - Authored automated code generation CLI with over 1,500 GitHub stars and 50k downloads.",
        "Mobile Project: Smart Warehouse Inventory App - Built cross-platform Flutter application integrated with barcode scanner.",
        "Hackathon Project: FinTech Credit Scoring - Won First Place creating AI-powered micro-lending credit scoring prototype on AWS.",
        "Portfolio Project: Developer Website & Blog - Designed minimalist responsive web portfolio with Next.js 14, MDX, and Tailwind CSS.",
        "Healthcare Project: Hospital Patient EHR Portal - Created HIPAA-compliant patient management system using React and Node.js.",
        "Trading Bot Project: Crypto Quantitative Algorithmic Bot - Engineered trading bot executing high-frequency Binance API strategies.",
        "AI Vision Project: Facial Recognition Attendance System - Built OpenCV computer vision webcam attendance tracker logging to MySQL.",
        "Web App Project: Community Discussion Forum - Designed Reddit-inspired social discussion platform with nested comments and voting.",
        "Robotics Project: Autonomous Indoor Delivery Robot - Built ROS2 navigation stack with lidar sensor obstacle avoidance on Raspberry Pi.",
        "Vision Project: Smart Parking ANPR System - Deployed YOLOv8 deep learning model for automated vehicle gate license plate recognition.",
        "SaaS Project: Multi-Tenant CRM Platform - Built customer pipeline management platform with role-based permissions and Stripe billing.",
        "Cloud Project: Serverless Image Optimization - Created AWS Lambda pipeline converting uploaded high-res photos into WebP assets.",
        "Blockchain Project: Decentralized Supply Chain DApp - Built Ethereum Solidity smart contracts tracking pharmaceutical shipping history.",
        "Aviation Project: Flight Booking Engine - Architected booking reservation system handling seat selection and flight schedules.",
        "Web Tool Project: Automated Resume ATS Scorer - Developed web analyzer evaluating CV keyword matching against job descriptions.",
        "IoT Project: Agriculture Weather Monitoring Station - Deployed ESP32 sensor array collecting soil moisture and rainfall metrics.",
        "Machine Learning Project: Customer Churn Prediction - Trained XGBoost classification model reaching 89% ROC-AUC on telecom data.",
        "Graphics Project: Interactive 3D Product Showcase - Built web-based 3D car visualizer utilizing Three.js, WebGL, and GSAP animations.",
        "Communication Project: Real-Time Video Chat App - Implemented WebRTC peer-to-peer video streaming and chat with Socket.io.",
        "DevOps Project: Automated CI/CD Webhook Service - Built lightweight webhook service triggering Docker builds and Slack alerts.",
        "NLP Project: Financial News Sentiment Pipeline - Collected 100k financial news articles using Scrapy and generated sentiment risk.",
        "EdTech Project: Gamified Language Learning Mobile App - Developed interactive quiz game with audio speech recognition on React Native.",
        "Campus Project: School Academic Information Portal - Engineered student grades, attendance, and tuition payment tracking portal.",
        "Logging Project: High-Throughput Log Aggregation Platform - Implemented centralized logging using Elasticsearch, Fluentd, and Kibana.",
        "Fintech Project: Digital Banking KYC Onboarding Flow - Designed and coded 5-step biometric KYC registration prototype in Flutter.",
        "Security Project: Network Packet Sniffer & Traffic Analyzer - Built Python network utility analyzing packet headers and protocol anomalies.",
        "Hospitality Project: Restaurant Table Reservation System - Developed online table booking platform with live interactive floor seating.",
        "Research Paper Project: Edge Computing Optimization - Published peer-reviewed research on edge computing protocols for smart grids.Proyek: Sistem Informasi Manajemen Rumah Sakit (SIMRS) - Membangun aplikasi web rekam medis digital pasien dan pendaftaran poliklinik.",
        "Proyek: Marketplace Jasa Freelance Mahasiswa - Mengembangkan platform marketplace dengan integrasi payment gateway Midtrans.",
        "Proyek Mobile: Aplikasi Pencatatan Keuangan Pribadi - Merancang aplikasi Android berbasis Flutter dengan visualisasi grafik pengeluaran.",
        "Proyek Juara 1 Gemastik: Deteksi Dini Stunting Balita - Mengembangkan aplikasi mobile deteksi stunting balita berbasis kecerdasan buatan.",
        "Proyek Portofolio: Website Interaktif Desainer Grafis - Dibangun menggunakan Three.js, animasi GSAP interaktif, dan framework Next.js.",
        "Proyek IoT: Monitoring Suhu dan Kelembaban Gudang - Menggunakan mikrokontroler ESP32 dan dashboard analitik data ThingSpeak.",
        "Proyek Tugas Akhir: Klasifikasi Penyakit Daun Padi - Mengembangkan model Convolutional Neural Network (CNN) untuk identifikasi daun padi.",
        "Proyek Bot: Notifikasi Server Telegram Realtime - Membangun automasi pengawasan server down dan beban CPU memori berbasis Python.",
        "Proyek Ekstensi: Chrome Extension Produktivitas Kerja - Meraih 3.000 pengguna aktif dengan rating 4.8 bintang di Chrome Web Store.",
        "Proyek Juara Hackathon: Pelaporan Jalan Rusak Smart City - Merancang prototipe sistem pelaporan jalan rusak berbasis sensor GPS geolocation.",
        "Proyek Desktop: Aplikasi Kasir POS Toko Ritel - Membangun software kasir desktop menggunakan Electron, React, dan printer struk thermal.",
        "Proyek Web: Platform Crowdfunding dan Donasi Online - Mengembangkan website penggalangan dana terintegrasi verifikasi identitas e-KTP.",
        "Proyek Akademik: Sistem Informasi Akademik Sekolah (SIAKAD) - Membangun modul presensi online, input nilai raport, dan jadwal pelajaran.",
        "Proyek NLP: Engine Analisis Sentimen Opini Twitter - Melakukan penarikan cuitan dan klasifikasi sentimen menggunakan model IndoBERT.",
        "Proyek Tiket: Aplikasi Pemesanan Tiket Bioskop Realtime - Mengembangkan backend microservices reservasi kursi bioskop dengan locking redis.",
        "Proyek SPK: Sistem Penunjang Keputusan Rekomendasi Beasiswa - Menerapkan metode Simple Additive Weighting (SAW) dan TOPSIS berbasis web.",
        "Proyek Lomba: Aplikasi Mobile Bank Sampah Digital - Membangun prototipe aplikasi bank sampah digital dan edukasi daur ulang sampah.",
        "Proyek AI: Sistem Rekomendasi Film Personal - Membangun modul machine learning rekomendasi film dengan algoritma Collaborative Filtering.",
        "Proyek Edukasi: Aplikasi Ujian Online Interaktif Kampus - Mendukung pengacakan butir soal otomatis, timer pengerjaan, dan anti copy-paste.",
        "Proyek Portal: Website Berita Kampus Terintegrasi - Dibangun menggunakan arsitektur Jamstack Astro, Tailwind CSS, dan Headless CMS.",
        "Proyek Web: Aplikasi ATS Resume Analyzer Berbasis Streamlit - Dibuat untuk mengevaluasi skor kecocokan format CV pelamar lowongan kerja.",
        "Proyek SIG: Sistem Informasi Geografis Pemetaan Banjir - Membangun peta digital interaktif sebaran titik rawan banjir dengan Leaflet.js.",
        "Proyek Psikometri: Platform Tes Minat Bakat Karir - Membangun kuesioner psikometri online dengan hasil laporan rekomendasi format PDF.",
        "Proyek Antrean: Aplikasi Display Antrean Pasien Klinik - Mengembangkan display antrean nomor loket otomatis terhubung suara audio sintesis.",
        "Proyek Hackathon: Dompet Digital Finansial Inklusif - Mengembangkan prototipe dompet digital tanpa rekening bank berbasis QRIS statis.",
        "Proyek Open Source: Pustaka Python Web Scraper - Mengembangkan pustaka scraping data katalog e-commerce dengan 400 bintang di GitHub.",
        "Proyek Presensi: Aplikasi Absensi Pegawai Berbasis Geofencing - Mengembangkan aplikasi mobile Android dengan validasi radius lokasi GPS.",
        "Proyek Logistik: Sistem Pelacakan Pengiriman Kurir Logistik - Membangun dashboard pelacakan paket kurir berbasis koordinat GPS secara realtime.",
        "Proyek UMKM: Website Direktori Katalog Produk Daerah - Membangun website direktori promosi produk makanan dan kerajinan lokal daerah.",
        "Proyek Publikasi Ilmiah: Riset Protokol IoT Hemat Energi - Mempublikasikan paper penelitian jaringan sensor nirkabel pada konferensi nasional.",
        "Project: E-Commerce Microservices Platform - Engineered scalable backend handling 50k daily active users with Go and PostgreSQL.",
        "Open-Source Project: CLI Scaffolding Tool - Authored automated code generation CLI with over 1,500 GitHub stars and 50k downloads.",
        "Project: Corporate Cash Flow Automation - Built financial modeling template in Excel VBA that cut month-end closing time by 50%.",
        "Project: Statutory Tax Audit Preparation - Successfully reconciled corporate tax differences, recovering $45,000 in refunds.",
        "Project: Employee Onboarding Revamp Initiative - Redesigned 90-day induction program, boosting new-hire satisfaction to 94%.",
        "Project: HRIS Migration & Data Cleansing - Migrated 1,200 employee records to cloud HRIS platform without record discrepancies.",
        "Marketing Campaign: National Brand Relaunch - Spearheaded digital multichannel campaign achieving 250k impressions and 180% sales lift.",
        "Sales Project: Strategic Enterprise B2B Partnership - Closed 3-year supply contract with multinational client valued at $1.5M.",
        "Healthcare Quality Project: Patient Fall Prevention Protocol - Implemented clinical safety checklist, reducing ward falls by 35%.",
        "Clinical Project: Electronic Medication Record Integration - Trained 50 ward nurses on barcode scanning medication administration.",
        "Operations Project: Digital Office Procurement System - Streamlined stationery ordering workflow, lowering office expenses by 15%.",
        "Logistics Project: Warehouse Barcode Inventory Audit - Reduced stock discrepancy rate from 4.2% to 0.3% across 10,000 SKUs.",
        "Educational Project: Interactive STEM Learning Modules - Authored science laboratory guides adopted by 6 regional high schools.",
        "Curriculum Project: Digital Learning Portal Implementation - Piloted flipped-classroom model that improved exam averages by 12%.",
        "Legal Project: Standard Corporate Procurement Agreement - Drafted 20 bilingual master service agreement templates for vendor onboarding.",
        "Compliance Project: Anti-Bribery Compliance Audit - Led organization-wide risk assessment ensuring 100% adherence to ISO 37001.",
        "Proyek: Sistem Informasi Manajemen Rumah Sakit (SIMRS) - Membangun aplikasi web rekam medis digital pasien dan pendaftaran poliklinik.",
        "Proyek Mobile: Aplikasi Pencatatan Keuangan Pribadi - Merancang aplikasi Android berbasis Flutter dengan visualisasi grafik pengeluaran.",
        "Proyek: Otomasi Laporan Rekonsiliasi Bank Excel - Mengembangkan template makro VBA yang memangkas waktu kerja rekonsiliasi tim 60%.",
        "Proyek: Audit Kepatuhan Perpajakan Internal - Berhasil mengidentifikasi potensi restitusi lebih bayar pajak senilai Rp 85 Juta.",
        "Proyek HR: Program Retensi dan Engagement Karyawan - Merancang survei kepuasan kerja kuartalan yang menurunkan employee turnover 18%.",
        "Proyek: Standarisasi Standar Kompetensi Jabatan (SKJ) - Menyusun kamus kompetensi kerja untuk 45 posisi di lingkungan perusahaan.",
        "Proyek Kampanye: Peluncuran Produk Skincare Nasional - Memimpin kampanye influencer dan digital ads yang menghasilkan omzet Rp 1.5 Miliar.",
        "Proyek: Revitalisasi Organik SEO Website Retail - Meningkatkan jumlah pengunjung organik bulanan dari 10.000 menjadi 45.000 pengunjung.",
        "Proyek Mutu RS: Penerapan Prosedur Hand Hygiene Ruang Rawat - Berhasil menurunkan angka infeksi nosokomial di bangsal anak sebesar 15%.",
        "Proyek Medis: Digitalisasi Formulir Triase IGD - Mempercepat waktu pencatatan triase pasien gawat darurat dari 8 menit menjadi 3 menit.",
        "Proyek: Digitalisasi 2.000 Dokumen Arsip Fisik Perusahaan - Mengalihkan arsip kertas ke sistem database digital terenkripsi.",
        "Proyek Efisiensi: Pengadaan Terpusat Inventaris Kantor - Menghemat biaya belanja operasional ATK kantor tahunan sebesar 20%.",
        "Proyek Edukasi: Pembuatan Modul Pembelajaran Interaktif Siswa - Mengembangkan media belajar visual yang menaikkan nilai rata-rata ujian siswa.",
        "Proyek Pelatihan: Workshop Pemanfaatan AI untuk Guru - Melatih 100 guru sekolah menengah dalam pembuatan bahan ajar digital.",
        "Proyek Legal: Standarisasi Perjanjian Kerjasama Vendor - Menyusun 20 template kontrak standar dwibahasa untuk pengadaan barang dan jasa.",
        "Proyek Kepatuhan: Audit Kepatuhan Perizinan Berusaha OSS - Menuntaskan perpanjangan izin edar dan sertifikasi halal tepat waktu.",
    ],
}

DATE_PATTERN = re.compile(
    r"\b(?:19|20)\d{2}\b|\b(?:present|current|sekarang|hingga kini|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|januari|februari|maret|april|mei|juni|juli|agustus|september|oktober|november|desember)\b",
    re.I
)
EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
PHONE_PATTERN = re.compile(r"(?<!\w)(?:\+?62|0)[\d\s().-]{8,17}\d(?!\w)")
LINK_PATTERN = re.compile(r"(?:https?://)?(?:www\.)?(?:linkedin\.com/in/|github\.com/)[^\s|,]+", re.I)


def train_local_model():
    heading_texts = []
    heading_labels = []
    body_texts = []
    body_labels = []
    for section, examples in HEADINGS.items():
        heading_texts.extend(examples)
        heading_labels.extend([section] * len(examples))
    for section, examples in EXAMPLES.items():
        body_texts.extend(examples)
        body_labels.extend([section] * len(examples))

    headings = make_pipeline(
        TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), sublinear_tf=True),
        CalibratedClassifierCV(LinearSVC(C=2.0, dual="auto", random_state=42))
    )
    content_features = FeatureUnion([
        ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)),
        ("word", TfidfVectorizer(analyzer="word", ngram_range=(1, 2), sublinear_tf=True)),
    ])
    content = make_pipeline(
        content_features,
        CalibratedClassifierCV(LinearSVC(C=1.5, dual="auto", random_state=42))
    )

    headings.fit(heading_texts, heading_labels)
    content.fit(body_texts, body_labels)

    MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"headings": headings, "content": content, "version": 5}, MODEL_FILE)
    return MODEL_FILE


def load_local_model():
    if not MODEL_FILE.exists():
        train_local_model()
    data = joblib.load(MODEL_FILE)
    # Re-train if version outdated
    if not isinstance(data, dict) or data.get("version", 0) < 5:
        train_local_model()
        data = joblib.load(MODEL_FILE)
    return data


def classify(text, model):
    probabilities = model.predict_proba([text])[0]
    best = probabilities.argmax()
    return str(model.classes_[best]), float(probabilities[best])


def detect_heading(line, models):
    value = strip_format(line).strip().rstrip(":")
    if not value or len(value) > 55 or EMAIL_PATTERN.search(value) or DATE_PATTERN.search(value):
        return None
    normalized = value.casefold()
    for section, aliases in SECTION_NAMES.items():
        if normalized in aliases and section != "personal":
            return section
    if line.lstrip().startswith(('-', '*', '+')) or len(value.split()) > 6:
        return None
    section, score = classify(value, models["headings"])
    return section if score >= 0.55 else None


def empty_cv():
    return {
        "name": "", "email": "", "phone": "", "location": "",
        "linkedin": "", "github": "", "summary": "", "skills": "",
        "education": [], "experience": [], "organizations": [], "projects": []
    }


def extract_contact(line, data):
    label, value = read_label(line)
    field = find_field(label, PERSONAL_FIELDS) if label else None
    if field and value:
        data[field] = value
        return True
    email = EMAIL_PATTERN.search(line)
    phone = PHONE_PATTERN.search(line)
    links = LINK_PATTERN.findall(line)
    found = bool(email or phone or links)
    if email:
        data["email"] = email.group(0)
    if phone:
        data["phone"] = phone.group(0).strip()
    for link in links:
        key = "linkedin" if "linkedin.com" in link.lower() else "github"
        data[key] = link
    return found


def split_blocks(lines):
    blocks = []
    block = []
    for line in lines + [""]:
        if not line.strip():
            if block:
                blocks.append(block)
                block = []
            continue
        if line.lstrip().startswith("### ") and block:
            blocks.append(block)
            block = []
        block.append(line)
    return blocks


def parse_free_entry(block, section):
    if not block:
        return None
    if "|" in block[0]:
        return parse_entry(block, section)
    entry = {}
    details = []
    for line in block:
        label, value = read_label(line)
        field = find_field(label, ENTRY_FIELDS) if label else None
        if field:
            entry[field] = value
        else:
            details.append(strip_format(line))
    if not details:
        return entry if entry else None
    first = details.pop(0)
    if section == "projects":
        entry.setdefault("name", first)
    elif section == "education":
        entry.setdefault("school", first)
        if details and not DATE_PATTERN.search(details[0]):
            entry.setdefault("degree", details.pop(0))
    else:
        match = re.split(r"\s+(?:at|@|di)\s+", first, maxsplit=1, flags=re.I)
        entry.setdefault("title", match[0])
        if len(match) > 1:
            entry.setdefault("company", match[1])
        elif details and not details[0].startswith("-") and len(details[0]) < 65 and not DATE_PATTERN.search(details[0]):
            entry.setdefault("company", details.pop(0))
    remaining = []
    for line in details:
        if DATE_PATTERN.search(line) and len(line) < 55 and not entry.get("dates"):
            entry["dates"] = line
        else:
            remaining.append(line)
    if remaining:
        entry["description"] = "\n".join(remaining)
    required = "school" if section == "education" else "name" if section == "projects" else "title"
    return entry if entry.get(required) else None


def parse_free_text(text):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Teks CV tidak boleh kosong.")
    models = load_local_model()
    data = empty_cv()
    sections = {name: [] for name in EXAMPLES}
    current = None
    for raw_line in text.replace("\r\n", "\n").split("\n"):
        line = raw_line.strip()
        if not line:
            if current:
                sections[current].append("")
            continue
        if extract_contact(line, data):
            continue
        if not data["name"] and current is None and not line.startswith(("-", "*")) and not DATE_PATTERN.search(line) and len(strip_format(line).split()) in range(2, 6):
            possible = strip_format(line)
            heading = detect_heading(line, models)
            if heading is None:
                data["name"] = possible
                continue
        heading = detect_heading(line, models)
        if heading and not line.startswith("### "):
            current = heading
            continue
        if current is None:
            predicted, confidence = classify(strip_format(line), models["content"])
            current = predicted if confidence >= 0.30 else "summary"
        sections[current].append(line)
    data["summary"] = "\n".join(strip_format(line) for line in sections["summary"] if line)
    data["skills"] = "\n".join(strip_format(line) for line in sections["skills"] if line)
    for section in ("education", "experience", "organizations", "projects"):
        for block in split_blocks(sections[section]):
            entry = parse_free_entry(block, section)
            if entry:
                data[section].append(entry)
    if not data["name"]:
        raise ValueError("Nama tidak ditemukan. Tulis nama lengkap di baris pertama atau gunakan 'Nama: ...'.")
    return data
