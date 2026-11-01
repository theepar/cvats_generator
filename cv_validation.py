import re
from dataclasses import dataclass, field


EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PLACEHOLDERS = {"nama lengkap", "name", "full name", "your name", "nama anda", "isi nama", "contoh nama", "your email", "nama@email.com", "budi@example.com"}


@dataclass
class CVValidation:
    missing: list[str] = field(default_factory=list)
    invalid: list[str] = field(default_factory=list)
    review: list[str] = field(default_factory=list)
    details: dict[str, int] = field(default_factory=dict)

    @property
    def is_valid(self):
        return not (self.missing or self.invalid or self.review)


def validate_cv(data, document_warnings=None):
    result = CVValidation()
    name = str(data.get("name") or "").strip()
    email = str(data.get("email") or "").strip()
    phone = str(data.get("phone") or "").strip()
    summary = str(data.get("summary") or "").strip()
    skills = str(data.get("skills") or "").strip()

    if not name:
        result.missing.append("Nama lengkap belum ditemukan.")
    elif len(name.split()) > 8 or len(name) > 100 or name.lower() in PLACEHOLDERS or re.search(r"https?://|@", name):
        result.invalid.append("Nama terlihat seperti contoh, tautan, atau hasil ekstraksi yang salah.")

    if not email:
        result.missing.append("Alamat email belum ditemukan.")
    elif not EMAIL_PATTERN.fullmatch(email):
        result.invalid.append("Format alamat email tidak valid.")
    elif email.lower() in PLACEHOLDERS:
        result.review.append("Email masih menggunakan data contoh.")

    if not phone:
        result.review.append("Nomor telepon tidak ditemukan.")
    elif not 9 <= len(re.sub(r"\D", "", phone)) <= 16:
        result.invalid.append("Nomor telepon tampak tidak valid.")

    if not summary:
        result.review.append("Ringkasan profil belum ditemukan.")
    if not skills:
        result.review.append("Bagian keahlian belum ditemukan.")

    collections = {"education": "pendidikan", "experience": "pengalaman kerja", "organizations": "organisasi", "projects": "proyek/prestasi"}
    for key, label in collections.items():
        entries = data.get(key) or []
        result.details[key] = len(entries)
        for index, entry in enumerate(entries, 1):
            if key == "education":
                if not entry.get("school"):
                    result.review.append(f"Pendidikan #{index}: institusi belum dikenali.")
                if not entry.get("degree"):
                    result.review.append(f"Pendidikan #{index}: jurusan/gelar belum dikenali.")
            elif key in ("experience", "organizations"):
                if not entry.get("company"):
                    result.review.append(f"{label.capitalize()} #{index}: perusahaan/organisasi belum dikenali.")
            if not entry.get("dates") and key != "projects":
                result.review.append(f"{label.capitalize()} #{index}: periode belum ditemukan.")

    if not result.details["education"] and not result.details["experience"]:
        result.review.append("Tidak ada pendidikan atau pengalaman kerja yang berhasil dikenali.")

    for warning in document_warnings or []:
        result.review.append(warning)

    return result
