import re
from dataclasses import dataclass, field
from typing import List, Dict, Set, Any

COMMON_STOPWORDS = {
    # English
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
    "can", "did", "do", "does", "doing", "don't", "down", "during", "each", "few", "for", "from",
    "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself", "him", "himself",
    "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just", "me", "more", "most",
    "my", "myself", "no", "nor", "not", "now", "of", "off", "on", "once", "only", "or", "other",
    "our", "ours", "ourselves", "out", "over", "own", "same", "she", "should", "so", "some", "such",
    "than", "that", "the", "their", "theirs", "them", "themselves", "then", "there", "these", "they",
    "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "we", "were",
    "what", "when", "where", "which", "while", "who", "whom", "why", "with", "would", "you", "your",
    "yours", "yourself", "yourselves", "requirements", "responsibilities", "qualification", "qualifications",
    "role", "job", "candidate", "work", "experience", "years", "skills", "ability", "proficient",
    # Indonesian
    "dan", "yang", "di", "ke", "dari", "ini", "itu", "untuk", "pada", "adalah", "sebagai", "dengan",
    "bisa", "dapat", "akan", "telah", "sudah", "atau", "juga", "kami", "kita", "anda", "kamu",
    "mereka", "ia", "dia", "dalam", "bagi", "secara", "lebih", "sangat", "harus", "memiliki",
    "kualifikasi", "persyaratan", "tanggung", "jawab", "deskripsi", "pekerjaan", "pengalaman", "tahun",
    "kemampuan", "posisi", "bidang", "minimal", "jurusan", "lulusan"
}

ACTION_VERBS = {
    # English - Cross Industry (Tech, Business, Finance, Healthcare, HR, Sales, Teaching, Legal)
    "built", "developed", "designed", "engineered", "implemented", "launched", "spearheaded",
    "optimized", "increased", "decreased", "reduced", "scaled", "automated", "delivered",
    "managed", "led", "mentored", "orchestrated", "architected", "refactored", "integrated",
    "created", "achieved", "analyzed", "published", "maintained", "collaborated", "streamlined",
    "negotiated", "executed", "reconciled", "audited", "budgeted", "forecasted", "recruited",
    "onboarded", "trained", "coached", "advised", "formulated", "researched", "facilitated",
    "supervised", "administered", "directed", "resolved", "assisted", "evaluated", "marketed",
    "promoted", "monitored", "treated", "scheduled", "coordinated", "generated", "secured",
    "drafted", "reviewed", "taught", "instructed", "dispensed", "inspected", "diagnosed",
    # Indonesian - Lintas Industri (Teknologi, Keuangan, Kesehatan, HR, Penjualan, Pendidikan, Hukum, Admin)
    "mengembangkan", "membangun", "merancang", "mengimplementasikan", "mengoptimalkan",
    "meningkatkan", "mengurangi", "mengotomatisasi", "memimpin", "mengelola", "mengintegrasikan",
    "membuat", "mencapai", "menganalisis", "memelihara", "berkolaborasi", "mengoordinasikan",
    "merekonsiliasi", "mengaudit", "menganggarkan", "memproyeksikan", "merekrut", "melatih",
    "membina", "memberikan", "menyusun", "meneliti", "memfasilitasi", "mengawasi", "mengevaluasi",
    "memasarkan", "mempromosikan", "memantau", "merawat", "menjadwalkan", "menangani", "menghasilkan",
    "melayani", "menerbitkan", "menyelenggarakan", "mengadvokasi", "menegosiasikan", "membukukan",
    "mengarahkan", "meninjau", "mendiagnosis", "mengajar", "mendidik", "mengkaji", "memeriksa"
}

@dataclass
class ATSAuditResult:
    score: int
    keyword_match_rate: float
    matched_keywords: List[str] = field(default_factory=list)
    missing_keywords: List[str] = field(default_factory=list)
    quantifiable_metrics_count: int = 0
    action_verbs_count: int = 0
    feedback_notes: List[str] = field(default_factory=list)

def extract_tokens(text: str) -> List[str]:
    """Tokenize text into cleaned words (supports programming languages & alphanumeric keywords)."""
    # Preserve words like c++, c#, .net, node.js
    raw_tokens = re.findall(r"\b[A-Za-z0-9+#.-]+\b", text.lower())
    cleaned = []
    for token in raw_tokens:
        clean = token.strip(".-")
        if len(clean) >= 2 and clean not in COMMON_STOPWORDS and not clean.isnumeric():
            cleaned.append(clean)
    return cleaned

def extract_job_keywords(job_description: str, max_keywords: int = 35) -> List[str]:
    """Extract salient keywords from a job description by frequency."""
    tokens = extract_tokens(job_description)
    freq: Dict[str, int] = {}
    for t in tokens:
        freq[t] = freq.get(t, 0) + 1
    
    # Sort by frequency descending
    sorted_keywords = sorted(freq.keys(), key=lambda k: freq[k], reverse=True)
    return sorted_keywords[:max_keywords]

def cv_to_full_text(data: Dict[str, Any]) -> str:
    """Flatten all text content from CV data into a single string for analysis."""
    parts = []
    for key in ("name", "summary", "skills", "location"):
        if data.get(key):
            parts.append(str(data[key]))
    
    for section in ("experience", "organizations"):
        for item in data.get(section, []):
            parts.append(f"{item.get('title', '')} {item.get('company', '')} {item.get('description', '')}")
            
    for item in data.get("education", []):
        parts.append(f"{item.get('school', '')} {item.get('degree', '')}")

    for item in data.get("projects", []):
        parts.append(f"{item.get('name', '')} {item.get('description', '')}")

    return " ".join(parts)

def analyze_ats(cv_data: Dict[str, Any], job_description: str = "") -> ATSAuditResult:
    """Analyze CV content for ATS compatibility and optional Job Description keyword matching."""
    full_cv_text = cv_to_full_text(cv_data).lower()
    cv_tokens = set(extract_tokens(full_cv_text))

    matched_keywords = []
    missing_keywords = []
    keyword_match_rate = 0.0

    if job_description.strip():
        job_keywords = extract_job_keywords(job_description)
        for kw in job_keywords:
            if kw in cv_tokens or kw in full_cv_text:
                matched_keywords.append(kw)
            else:
                missing_keywords.append(kw)
        if job_keywords:
            keyword_match_rate = round((len(matched_keywords) / len(job_keywords)) * 100, 1)

    # Check for quantifiable numbers / metrics in bullet points
    # Examples: 20%, $5k, 100+, 1,000, 50 user, 3x
    metric_regex = re.compile(r"\b\d+([.,]\d+)?\s*(%|x|k|jt|juta|users?|pengguna|clients?|klien|proyek|projects?|hari|days?|bulan|months?|tahun|years?|\+)?\b", re.I)
    
    quantifiable_count = 0
    action_verb_count = 0
    descriptions = []

    for section in ("experience", "organizations", "projects"):
        for item in cv_data.get(section, []):
            desc = item.get("description", "")
            if desc:
                descriptions.append(desc)
                # Count matches
                if metric_regex.search(desc):
                    quantifiable_count += 1
                for verb in ACTION_VERBS:
                    if re.search(rf"\b{verb}\b", desc, re.I):
                        action_verb_count += 1

    feedback = []

    # Calculate overall ATS score (base score from completeness + quality + optional keywords)
    score = 40  # base starting score

    # 1. Contact & Essentials
    if cv_data.get("name") and cv_data.get("email") and cv_data.get("phone"):
        score += 15
    else:
        feedback.append("Kontak belum lengkap (Nama, Email, dan Telepon wajib ada).")

    # 2. Summary & Skills
    if cv_data.get("summary"):
        score += 10
    else:
        feedback.append("Tambahkan Ringkasan Profil (Professional Summary) untuk menarik ATS.")

    if cv_data.get("skills"):
        score += 10
    else:
        feedback.append("Bagian Keahlian (Skills) masih kosong.")

    # 3. Experience & Quantifiable Achievements
    if cv_data.get("experience"):
        score += 15
        if quantifiable_count > 0:
            score += 10
        else:
            feedback.append("Gunakan angka/persentase pada deskripsi pengalaman (misal: 'Meningkatkan konversi 15%').")
    else:
        feedback.append("Tambahkan riwayat pengalaman kerja / magang.")

    # 4. Action Verbs
    if action_verb_count >= 2:
        score += 10
    elif action_verb_count == 1:
        score += 5
    else:
        feedback.append("Gunakan action verbs aktif (contoh: Mengembangkan, Mengoptimalkan, Built, Engineered).")

    # 5. If Job Description is provided, factor into score
    if job_description.strip():
        # Match rate determines 20% weight adjustment
        match_bonus = int((keyword_match_rate / 100) * 20)
        score = min(100, int(score * 0.8) + match_bonus)
        if keyword_match_rate < 50:
            feedback.append(f"Kesesuaian kata kunci dengan loker masih {keyword_match_rate}%. Pertimbangkan menambahkan kata kunci yang hilang.")
    else:
        score = min(100, score)

    return ATSAuditResult(
        score=score,
        keyword_match_rate=keyword_match_rate,
        matched_keywords=matched_keywords,
        missing_keywords=missing_keywords,
        quantifiable_metrics_count=quantifiable_count,
        action_verbs_count=action_verb_count,
        feedback_notes=feedback
    )

