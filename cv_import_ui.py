from pathlib import Path
import re

import streamlit as st

from cv_ai import parse_free_text
from cv_document_reader import read_document
from cv_parser import find_section, parse_cv_text
from cv_validation import validate_cv
from cv_exporter import get_sample_cv_data


FORM_FIELDS = {
    "name": "input_name",
    "email": "input_email",
    "phone": "input_phone",
    "location": "input_location",
    "linkedin": "input_linkedin",
    "github": "input_github",
    "summary": "input_summary",
    "skills": "input_skills",
}

ENTRY_FIELDS = {
    "education": ("edu_count", {"school": "school", "degree": "degree", "dates": "edu_dates"}),
    "experience": ("work_count", {"title": "job", "company": "company", "dates": "job_dates", "description": "job_desc"}),
    "organizations": ("org_count", {"title": "org_role", "company": "org_name", "dates": "org_dates", "description": "org_desc"}),
    "projects": ("proj_count", {"name": "proj_name", "dates": "proj_dates", "description": "proj_desc"}),
}

LABELS = {
    "id": {
        "title": "Impor CV dari File atau Teks",
        "help": "Unggah .md, .txt, .pdf, atau .docx, atau tempel teks. PDF scan tanpa teks belum didukung.",
        "mode": "Metode pembacaan",
        "modes": ["Deteksi otomatis (AI lokal)", "Format template (tanpa AI)"],
        "template": "Download Contoh Markdown",
        "sample_industry": "Pilih Industri:",
        "load_sample": "Muat Contoh Profil",
        "sample_loaded": "Data contoh profil berhasil dimuat ke formulir!",
        "upload": "Pilih file CV",
        "paste": "Atau tempel teks CV",
        "analyze": "Periksa Isi CV",
        "empty": "Unggah dokumen atau tempel teks terlebih dahulu.",
        "error": "CV tidak berhasil dibaca",
        "ready": "Pemeriksaan selesai. Data berhasil dimasukkan ke formulir; silakan periksa lagi sebelum membuat PDF.",
        "review_title": "Periksa hasil ekstraksi sebelum melanjutkan",
        "missing": "Informasi yang belum ditemukan",
        "invalid": "Informasi yang tidak sesuai",
        "review": "Informasi yang perlu ditinjau",
        "result": "Lihat data hasil pembacaan",
        "continue": "Lanjutkan dan Isi Form",
        "cancel": "Batalkan Impor",
        "cancelled": "Impor dibatalkan. Data formulir sebelumnya tidak berubah.",
        "method": "Metode yang dipakai",
    },
    "en": {
        "title": "Import CV from File or Text",
        "help": "Upload .md, .txt, .pdf, or .docx, or paste text. Scanned PDFs without selectable text are not yet supported.",
        "mode": "Reading method",
        "modes": ["Automatic detection (local AI)", "Template format (no AI)"],
        "template": "Download Markdown Template",
        "sample_industry": "Select Industry:",
        "load_sample": "Load Sample Profile",
        "sample_loaded": "Sample profile data loaded into the form!",
        "upload": "Choose CV file",
        "paste": "Or paste your CV text",
        "analyze": "Check CV Content",
        "empty": "Upload a document or paste text first.",
        "error": "Unable to read CV",
        "ready": "Validation complete. The data was added to the form; review it before generating the PDF.",
        "review_title": "Review extracted data before continuing",
        "missing": "Missing information",
        "invalid": "Invalid or mismatched information",
        "review": "Information requiring review",
        "result": "Show extracted data",
        "continue": "Continue and Fill Form",
        "cancel": "Cancel Import",
        "cancelled": "Import cancelled. Existing form values were not changed.",
        "method": "Reading method",
    },
}


def fill_cv_form(cv_data):
    for field, widget_key in FORM_FIELDS.items():
        st.session_state[widget_key] = cv_data.get(field, "")

    st.session_state["input_toggle_github"] = bool(cv_data.get("github"))
    st.session_state["input_toggle_projects"] = bool(cv_data.get("projects"))

    for section, (count_key, field_keys) in ENTRY_FIELDS.items():
        items = cv_data.get(section, [])
        previous_count = st.session_state.get(count_key, 0)
        for index in range(max(previous_count, len(items))):
            for prefix in field_keys.values():
                st.session_state.pop(f"{prefix}_{index}", None)
        st.session_state[count_key] = len(items)
        for index, item in enumerate(items):
            for field, prefix in field_keys.items():
                st.session_state[f"{prefix}_{index}"] = item.get(field, "")


def has_structured_headings(text):
    found = 0
    for line in text.splitlines():
        heading = re.match(r"^\s*#{2,6}\s+(.+)$", line)
        if heading and find_section(heading.group(1)):
            found += 1
    return found >= 2


def extract_cv(text, template_only):
    if template_only or has_structured_headings(text):
        return parse_cv_text(text), "Template / aturan Python"
    return parse_free_text(text), "AI lokal + aturan Python"


def show_issues(heading, issues):
    if issues:
        st.markdown(f"**{heading}**")
        for issue in issues:
            st.write(f"- {issue}")


def show_import_section(language="id"):
    labels = LABELS.get(language, LABELS["id"])
    with st.expander(labels["title"], expanded=bool(st.session_state.get("cv_pending_import"))):
        st.caption(labels["help"])
        
        industry_options = {
            "tech": "Teknologi (Software Engineer)" if language == "id" else "Technology (Software Engineer)",
            "finance": "Keuangan & Akuntansi (Accountant)" if language == "id" else "Finance & Accounting (Accountant)",
            "hr": "Human Resources (HR Generalist)" if language == "id" else "Human Resources (HR Generalist)",
            "marketing": "Pemasaran & Penjualan (Marketing)" if language == "id" else "Marketing & Sales (Marketing)",
            "healthcare": "Kesehatan & Medis (Perawat Klinis)" if language == "id" else "Healthcare & Medical (Clinical Nurse)",
            "admin": "Administrasi & Umum (Office Admin)" if language == "id" else "Office Administration (Admin Staff)",
        }
        
        c_tpl1, c_tpl2, c_tpl3 = st.columns([1.5, 2, 1.5])
        template_file = Path(__file__).with_name("contoh_cv.md")
        c_tpl1.download_button(
            labels["template"],
            data=template_file.read_bytes(),
            file_name="contoh_cv.md",
            mime="text/markdown",
            key="cv_template_download",
            use_container_width=True
        )
        selected_industry = c_tpl2.selectbox(
            labels["sample_industry"],
            options=list(industry_options.keys()),
            format_func=lambda k: industry_options[k],
            label_visibility="collapsed",
            key="select_sample_industry"
        )
        if c_tpl3.button(labels["load_sample"], key="btn_load_sample_profile", use_container_width=True, icon=":material/person:"):
            fill_cv_form(get_sample_cv_data(selected_industry))
            st.session_state["cv_import_success"] = True
            st.rerun()

        mode = st.radio(labels["mode"], labels["modes"], horizontal=True, key=f"cv_import_mode_{language}")
        uploaded = st.file_uploader(labels["upload"], type=["md", "txt", "pdf", "docx"], key="cv_import_file")
        pasted = st.text_area(labels["paste"], height=150, key="cv_import_text")

        if st.button(labels["analyze"], key="cv_import_analyze", type="primary"):
            try:
                if uploaded is not None:
                    document = read_document(uploaded.getvalue(), uploaded.name)
                    source_text = document.text
                    warnings = document.warnings
                else:
                    source_text = pasted
                    warnings = []
                if not source_text.strip():
                    st.warning(labels["empty"])
                else:
                    cv_data, method = extract_cv(source_text, mode == labels["modes"][1])
                    check = validate_cv(cv_data, warnings)
                    if check.is_valid:
                        fill_cv_form(cv_data)
                        st.session_state["cv_import_success"] = True
                    else:
                        st.session_state["cv_pending_import"] = {"data": cv_data, "missing": check.missing, "invalid": check.invalid, "review": check.review, "method": method}
                    st.rerun()
            except (UnicodeDecodeError, ValueError, ImportError) as error:
                st.error(f"{labels['error']}: {error}")

        pending = st.session_state.get("cv_pending_import")
        if pending:
            st.warning(labels["review_title"])
            st.caption(f"{labels['method']}: {pending['method']}")
            show_issues(labels["missing"], pending["missing"])
            show_issues(labels["invalid"], pending["invalid"])
            show_issues(labels["review"], pending["review"])
            with st.expander(labels["result"]):
                st.json(pending["data"])
            left, right = st.columns(2)
            if left.button(labels["continue"], key="cv_import_confirm", type="primary", use_container_width=True):
                fill_cv_form(pending["data"])
                del st.session_state["cv_pending_import"]
                st.session_state["cv_import_success"] = True
                st.rerun()
            if right.button(labels["cancel"], key="cv_import_cancel", use_container_width=True):
                del st.session_state["cv_pending_import"]
                st.session_state["cv_import_cancelled"] = True
                st.rerun()

    if st.session_state.pop("cv_import_success", False):
        st.success(labels["ready"])
    if st.session_state.pop("cv_import_cancelled", False):
        st.info(labels["cancelled"])
