import re

DATE_PATTERN = re.compile(
    r"\b(?:19|20)\d{2}\b|\b(?:present|current|sekarang|hingga kini|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|januari|februari|maret|april|mei|juni|juli|agustus|september|oktober|november|desember)\b",
    re.I
)
INLINE_DATE_RE = re.compile(
    r"(?:[ \t]{2,}|\s*\|\s*|\s*,\s*)(?:(?:expected|graduated|est\.?|sejak|lulus|periode|tahun)?\s*"
    r"(?:(?:19|20)\d{2}|present|sekarang|current|hingga kini|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|januari|februari|maret|april|mei|juni|juli|agustus|september|oktober|november|desember)"
    r"[^\n]*)$",
    re.I
)
DEGREE_KEYWORDS = re.compile(
    r"\b(?:bachelor|master|doctor|phd|diploma|associate|sarjana|magister|doktor|s1|s2|s3|d3|d4|b\.?s\.?|b\.?a\.?|b\.?eng\.?|m\.?s\.?|m\.?a\.?|m\.?b\.?a\.?|rekayasa|teknik|engineering|computer science|informatika|sistem informasi)\b",
    re.I
)
SCHOOL_KEYWORDS = re.compile(
    r"\b(?:university|universitas|institute|institut|college|school|sekolah|politeknik|polytechnic|academy|akademi|smk|sma)\b",
    re.I
)

def extract_inline_date(line):
    m = INLINE_DATE_RE.search(line)
    if m:
        text = line[:m.start()].strip()
        date = line[m.start():].strip().lstrip('|, \t')
        return text, date
    return line.strip(), None

def is_entry_header(line):
    s = line.strip()
    if not s or s.startswith(("-", "*", "•")) or s.startswith(("[", "{", "(")):
        return False
    return bool(INLINE_DATE_RE.search(s))


SECTION_NAMES = {
    "personal": {
        "personal", "personal info", "personal information", "profile", "contact",
        "data diri", "informasi pribadi", "info pribadi", "kontak", "biodata", "identitas diri"
    },
    "summary": {
        "summary", "professional summary", "profile summary", "about me", "ringkasan",
        "ringkasan profil", "tentang saya", "profil profesional", "profil diri",
        "career objective", "personal statement", "executive summary", "deskripsi diri",
        "latar belakang singkat", "ikhtisar profesional"
    },
    "education": {
        "education", "academic background", "educational history", "academic qualifications",
        "formal education", "degrees", "university & school", "higher education",
        "pendidikan", "riwayat pendidikan", "latar belakang akademik", "pendidikan formal",
        "riwayat sekolah", "studi dan pendidikan", "pendidikan terakhir", "jenjang pendidikan"
    },
    "experience": {
        "experience", "work experience", "employment", "employment history", "professional experience",
        "work history", "career history", "working history", "corporate experience", "practical experience",
        "pengalaman", "pengalaman kerja", "riwayat pekerjaan", "pengalaman profesional",
        "riwayat karier", "pengalaman magang", "pengalaman industri", "pengalaman praktik",
        "pengalaman mengajar", "riwayat praktik klinis", "praktik kerja", "jejak karier"
    },
    "organizations": {
        "organizations", "organization", "organizational experience", "leadership experience",
        "volunteer experience", "community involvement", "volunteer work", "extracurricular activities",
        "community service", "student organization", "organisasi", "pengalaman organisasi",
        "aktivitas organisasi", "kegiatan komunitas", "pengalaman kepanitiaan", "kepanitiaan",
        "organisasi kampus", "pengalaman kepemimpinan", "kegiatan relawan", "aktivitas kemahasiswaan"
    },
    "skills": {
        "skills", "technical skills", "core competencies", "technology stack", "tools and technologies",
        "hard skills", "soft skills", "tools & frameworks", "specialized skills", "domain competencies",
        "keahlian", "keahlian utama", "keterampilan", "kemampuan teknis", "kompetensi",
        "kompetensi keahlian", "keahlian & kemampuan", "alat dan teknologi", "sertifikasi",
        "penguasaan software", "lisensi & sertifikasi", "keterampilan profesional"
    },
    "projects": {
        "projects", "achievements", "achievements and projects", "projects and achievements",
        "selected projects", "portfolio", "key achievements", "honors & awards", "selected works",
        "prestasi", "proyek", "prestasi dan proyek", "proyek dan prestasi", "daftar portofolio",
        "karya dan proyek", "proyek portofolio", "penghargaan", "publikasi", "karya", "kompetisi"
    },
}

PERSONAL_FIELDS = {
    "name": {"name", "full name", "nama", "nama lengkap"},
    "email": {"email", "e-mail"},
    "phone": {"phone", "phone number", "mobile", "telepon", "no telepon", "nomor telepon", "no hp", "nomor hp"},
    "location": {"location", "address", "lokasi", "alamat", "kota", "domisili"},
    "linkedin": {"linkedin", "linkedin url"},
    "github": {"github", "portfolio", "portofolio", "website", "github url", "portfolio url", "behance", "tautan"},
    "summary": {"summary", "professional summary", "ringkasan", "ringkasan profil", "tentang saya"},
}

ENTRY_FIELDS = {
    "title": {"title", "role", "job title", "position", "jabatan", "posisi", "peran", "profesi", "tugas"},
    "company": {"company", "organization", "organization name", "perusahaan", "organisasi", "nama organisasi", "kantor", "instansi", "rumah sakit", "sekolah", "kementerian", "lembaga", "hospital", "clinic", "firm", "agency"},
    "dates": {"dates", "date", "period", "periode", "tanggal", "tahun", "waktu"},
    "description": {"description", "details", "deskripsi", "detail", "pencapaian", "uraian tugas"},
    "school": {"school", "university", "institution", "college", "academy", "sekolah", "universitas", "institusi", "akademi", "politeknik", "kampus"},
    "degree": {"degree", "major", "qualification", "field of study", "gelar", "jurusan", "program studi", "peminatan", "spesialisasi"},
    "name": {"name", "project", "achievement", "award", "nama", "proyek", "prestasi", "penghargaan", "karya"},
}


def clean_label(value):
    value = re.sub(r"[*_`#]", "", value).strip().strip(":")
    value = value.replace("&", "and").replace("/", " ")
    return re.sub(r"\s+", " ", value).casefold()


def find_field(label, fields):
    label = clean_label(label)
    for key, names in fields.items():
        if label in names:
            return key
    return None


def find_section(label):
    return find_field(label, SECTION_NAMES)


def read_label(line):
    match = re.match(r"^\s*(?:[-*]\s+)?(?:\*\*)?([^:]+?)(?:\*\*)?\s*:\s*(.*)$", line)
    if not match:
        return None, None
    return match.group(1).replace("**", "").strip(), match.group(2).strip()


def strip_format(line):
    line = re.sub(r"^\s*(?:#{1,6}\s+|[-*+]\s+|\d+[.)]\s+)", "", line)
    return line.replace("**", "").strip()


def get_sections(text):
    sections = {name: [] for name in SECTION_NAMES}
    active = "personal"
    for original in text.replace("\r\n", "\n").split("\n"):
        line = original.strip()
        heading = re.match(r"^#{1,6}\s+(.+)$", line)
        section = find_section(heading.group(1) if heading else line.rstrip(":"))
        if section:
            active = section
            continue
        if heading and heading.group(0).startswith("# ") and active == "personal":
            sections[active].append(f"Name: {heading.group(1)}")
            continue
        sections[active].append(line)
    return sections


def split_entries(lines):
    entries = []
    current = []
    for line in lines:
        heading = re.match(r"^#{3,6}\s+", line)
        if heading and current:
            entries.append(current)
            current = []
        elif not line and current:
            entries.append(current)
            current = []
            continue
        if line:
            current.append(line)
    if current:
        entries.append(current)
    return entries


def parse_entry(lines, section):
    entry = {}
    details = []
    first_line = None
    for line in lines:
        label, value = read_label(line)
        field = find_field(label, ENTRY_FIELDS) if label else None
        if field:
            entry[field] = value
        elif first_line is None:
            first_line = strip_format(line)
        else:
            cleaned = strip_format(line)
            if cleaned:
                details.append(cleaned)

    if first_line:
        clean_first, inline_date = extract_inline_date(first_line)
        if inline_date and not entry.get("dates"):
            entry["dates"] = inline_date

        if "|" in clean_first:
            parts = [part.strip() for part in clean_first.split("|")]
            keys = {
                "education": ["school", "degree", "dates"],
                "experience": ["title", "company", "dates"],
                "organizations": ["title", "company", "dates"],
                "projects": ["name", "dates"],
            }[section]
            for key, value in zip(keys, parts):
                entry.setdefault(key, value)
        else:
            if section == "projects":
                entry.setdefault("name", clean_first)
            elif section == "education":
                is_deg = bool(DEGREE_KEYWORDS.search(clean_first))
                is_sch = bool(SCHOOL_KEYWORDS.search(clean_first))
                if is_deg and not is_sch:
                    entry.setdefault("degree", clean_first)
                    if details and not details[0].startswith(("-", "*", "•")) and not DATE_PATTERN.search(details[0]):
                        entry.setdefault("school", details.pop(0))
                    else:
                        entry.setdefault("school", "")
                else:
                    entry.setdefault("school", clean_first)
                    if details and not details[0].startswith(("-", "*", "•")) and not DATE_PATTERN.search(details[0]):
                        entry.setdefault("degree", details.pop(0))
            else:
                match = re.split(r"\s+(?:at|@|di)\s+", clean_first, maxsplit=1, flags=re.I)
                entry.setdefault("title", match[0])
                if len(match) > 1:
                    entry.setdefault("company", match[1])
                elif details and not details[0].startswith(("-", "*", "•")):
                    next_line = details[0]
                    if "|" in next_line:
                        comp, rest = next_line.split("|", 1)
                        entry.setdefault("company", comp.strip())
                        details[0] = rest.strip()
                    elif not DATE_PATTERN.search(next_line):
                        entry.setdefault("company", details.pop(0))

    if details:
        remaining = []
        for line in details:
            if DATE_PATTERN.search(line) and len(line) < 55 and not entry.get("dates") and not line.startswith(("-", "*", "•")):
                entry["dates"] = line
            else:
                remaining.append(line)
        if remaining:
            description = "\n".join(remaining)
            if entry.get("description"):
                description = entry["description"] + "\n" + description
            entry["description"] = description

    if section == "education":
        is_valid = bool(entry.get("school") or entry.get("degree"))
    elif section == "projects":
        is_valid = bool(entry.get("name"))
    else:
        is_valid = bool(entry.get("title"))
    return entry if is_valid else None


def parse_cv_text(text):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Teks CV tidak boleh kosong.")

    sections = get_sections(text)
    data = {
        "name": "", "email": "", "phone": "", "location": "",
        "linkedin": "", "github": "", "summary": "", "skills": "",
        "education": [], "experience": [], "organizations": [], "projects": [],
    }

    personal_notes = []
    for line in sections["personal"]:
        label, value = read_label(line)
        field = find_field(label, PERSONAL_FIELDS) if label else None
        if field:
            data[field] = value
        elif line:
            personal_notes.append(strip_format(line))

    if not data["summary"]:
        data["summary"] = "\n".join(strip_format(line) for line in sections["summary"] if line)
    if not data["name"] and personal_notes:
        data["name"] = personal_notes[0]

    data["skills"] = "\n".join(strip_format(line) for line in sections["skills"] if line)
    for section in ("education", "experience", "organizations", "projects"):
        for lines in split_entries(sections[section]):
            entry = parse_entry(lines, section)
            if entry:
                data[section].append(entry)

    if not data["name"]:
        raise ValueError("Nama tidak ditemukan. Tambahkan 'Nama: ...' atau '# Nama Lengkap'.")
    return data
