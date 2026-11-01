import re

BULLETS = ("-", "*", "+", "•", "●", "▪", "◦", "·")
BULLET_RE = re.compile(r"^([-*+•●▪◦·])\s+")

DATE_PATTERN = re.compile(
    r"\b(?:19|20)\d{2}\b|\b(?:present|current|sekarang|hingga kini|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|januari|februari|maret|april|mei|juni|juli|agustus|september|oktober|november|desember)\b",
    re.I
)

_MONTHS = r"(?:jan(?:uari|uary)?|feb(?:ruari|ruary)?|mar(?:et|ch)?|apr(?:il)?|mei|may|jun[ei]?|jul[iy]?|agu(?:stus)?|aug(?:ust)?|sep(?:t(?:ember)?)?|okt(?:ober)?|oct(?:ober)?|nov(?:ember)?|des(?:ember)?|dec(?:ember)?)"
_YEAR_DATE = rf"(?:(?:{_MONTHS}\.?,?\s+)?(?:19|20)\d{{2}}|\d{{1,2}}/(?:19|20)\d{{2}})"
_OPEN_END = r"(?:present|current|sekarang|saat ini|hingga kini)"
_RANGE_SEP = r"(?:\s*[-–—]\s*|\s+(?:to|until|sampai(?:\s+dengan)?|s\.?d\.?|s/d|hingga)\s+)"
_DATE_RANGE = rf"{_YEAR_DATE}(?:{_RANGE_SEP}(?:{_YEAR_DATE}|{_OPEN_END}))?"
_DATE_LABEL = r"(?:expected(?:\s+graduation)?|graduated|graduation|est\.?|sejak|lulus|periode|tahun|angkatan|class\s+of)\s*:?\s*"

# A whole "part" of a header that is only a date, e.g. "Jan 2022 - Present" or "Graduated: Dec 2023".
DATE_PART_RE = re.compile(rf"^(?:{_DATE_LABEL})?{_DATE_RANGE}$", re.I)
# A date at the very end of a line, separated from the text by any whitespace, pipe or comma.
TAIL_DATE_RE = re.compile(rf"(?:^|(?<=[\s|,]))((?:{_DATE_LABEL})?{_DATE_RANGE})\s*$", re.I)
# A date separated by a wide gap, pipe or comma, followed by anything.
INLINE_DATE_RE = re.compile(
    rf"(?:[ \t]{{2,}}|\s*\|\s*|\s*,\s*)(?:{_DATE_LABEL})?(?:{_YEAR_DATE}|{_OPEN_END}|{_MONTHS})\b[^\n]*$",
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


def split_pipes(text):
    return [part.strip() for part in re.split(r"\s*\|\s*", text) if part.strip()]


def extract_inline_date(line):
    m = INLINE_DATE_RE.search(line)
    if m:
        text = line[:m.start()].strip()
        date = line[m.start():].strip().lstrip('|, \t')
        return text, date
    s = line.strip()
    if s and s[0].isalnum() and (s[0].isdigit() or s[0].isupper()) and len(s.split()) <= 14 and not s.endswith("."):
        m = TAIL_DATE_RE.search(s)
        if m and m.start(1) > 0:
            return s[:m.start(1)].strip(" |,-–—"), m.group(1).strip()
    return s, None


def is_entry_header(line):
    s = line.strip()
    if not s or s.startswith(BULLETS) or s.startswith(("[", "{", "(")):
        return False
    return extract_inline_date(s)[1] is not None


def peel_dates(line):
    """Split a header line into (text without dates, date or None); dates may be pipe parts or a trailing token."""
    kept = []
    dates = []
    for part in split_pipes(line):
        (dates if DATE_PART_RE.match(part) else kept).append(part)
    date = dates[0] if dates else None
    if kept and not date:
        text, tail = extract_inline_date(kept[-1])
        if tail:
            date = tail
            if text:
                kept[-1] = text
            else:
                kept.pop()
    return " | ".join(kept), date


def institution_score(part):
    return 2 * bool(SCHOOL_KEYWORDS.search(part)) - bool(DEGREE_KEYWORDS.search(part))


def assign_education(parts):
    """Pick (school, degree, extras) from one or two header parts regardless of their order."""
    extras = parts[2:]
    if len(parts) == 1:
        only = parts[0]
        if DEGREE_KEYWORDS.search(only) and not SCHOOL_KEYWORDS.search(only):
            return "", only, extras
        return only, "", extras
    first, second = parts[0], parts[1]
    if institution_score(second) > institution_score(first):
        return second, first, extras
    return first, second, extras


def is_continuation_candidate(line):
    s = line.strip()
    return bool(s) and not s.startswith(BULLETS) and not re.match(r"(?i)^(?:gpa|ipk)\b", s)


def apply_header(entry, first, details, section):
    """Fill entry from the header line (and, if needed, the line after it). Returns extra description lines."""
    text, date = peel_dates(first)
    if date and not entry.get("dates"):
        entry["dates"] = date
    parts = split_pipes(text)
    if not parts:
        return []

    if section == "education":
        if len(parts) == 1 and details and is_continuation_candidate(details[0]):
            next_text, next_date = peel_dates(details[0])
            if next_text and len(next_text.split()) <= 15 and not next_text.endswith("."):
                details.pop(0)
                parts += split_pipes(next_text)
                if next_date and not entry.get("dates"):
                    entry["dates"] = next_date
        school, degree, extras = assign_education(parts)
        if school:
            entry.setdefault("school", school)
        if degree:
            entry.setdefault("degree", degree)
        return [" | ".join(extras)] if extras else []

    if section == "projects":
        entry.setdefault("name", parts[0])
        return [" | ".join(parts[1:])] if len(parts) > 1 else []

    title, company, extras = parts[0], None, parts[2:]
    if len(parts) > 1:
        if len(parts[1].split()) > 10 or parts[1].endswith("."):
            extras = parts[1:]
        else:
            company = parts[1]
    else:
        match = re.split(r"\s+(?:at|@|di)\s+", title, maxsplit=1, flags=re.I)
        title = match[0]
        if len(match) > 1:
            company = match[1]
        elif details and is_continuation_candidate(details[0]):
            next_text, next_date = peel_dates(details[0])
            next_parts = split_pipes(next_text)
            if next_parts and len(next_parts[0].split()) <= 12 and not next_parts[0].endswith("."):
                details.pop(0)
                company = next_parts[0]
                extras = next_parts[1:]
                if next_date and not entry.get("dates"):
                    entry["dates"] = next_date
    entry.setdefault("title", title)
    if company:
        entry.setdefault("company", company)
    return [" | ".join(extras)] if extras else []


def merge_wrapped(lines):
    """Join PDF-wrapped continuation lines onto the bullet they belong to and normalise bullet spacing."""
    merged = []
    for line in lines:
        s = BULLET_RE.sub(lambda m: m.group(1) + " ", re.sub(r"\s+", " ", line.strip()))
        if not s:
            continue
        if merged and merged[-1].startswith(BULLETS) and not s.startswith(BULLETS):
            previous = merged[-1]
            if not previous.endswith((".", "!", "?", ":", ";")) and (s[0].islower() or previous.endswith((",", "(", "/", "-", "&"))):
                merged[-1] = f"{previous} {s}"
                continue
        merged.append(s)
    return "\n".join(merged)



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
        elif line.strip():
            details.append(line.strip())

    extras = apply_header(entry, first_line, details, section) if first_line else []

    remaining = list(extras)
    for line in details:
        text = strip_format(line)
        if not text:
            continue
        rest, date = peel_dates(text)
        if date and not rest and not entry.get("dates") and not line.startswith(BULLETS):
            entry["dates"] = date
        else:
            remaining.append(text)
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
