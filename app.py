import base64
import streamlit as st

from cv_generator import generate_cv
from translations import TRANSLATIONS
from cv_import_ui import show_import_section
from ats_scorer import analyze_ats
from cv_exporter import cv_to_markdown, cv_to_json


def main():
    st.set_page_config(page_title="ATS CV Generator", layout="wide", page_icon="📄")

    # Responsive CSS: centers and constraints layout for widescreen monitors and optimizes mobile/tablet view
    st.markdown(
        """
        <style>
        /* Responsive container: centers and limits max-width for ultra-wide / desktop */
        .main .block-container {
            max-width: 1000px !important;
            margin-left: auto !important;
            margin-right: auto !important;
            padding-top: 1.75rem !important;
            padding-bottom: 5rem !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
        }

        /* Mobile & Tablet responsiveness */
        @media (max-width: 768px) {
            .main .block-container {
                padding-left: 0.85rem !important;
                padding-right: 0.85rem !important;
                padding-top: 1rem !important;
            }
            .stTabs [data-baseweb="tab"] {
                padding: 6px 10px !important;
                font-size: 0.85rem !important;
            }
        }

        /* Tab Bar styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 6px;
            border-bottom: 1px solid rgba(128, 128, 128, 0.2);
            flex-wrap: wrap;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            font-weight: 500;
        }

        /* Card border containers */
        div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
            margin-bottom: 1rem;
        }

        /* Subtle headers */
        h1, h2, h3 {
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    with st.container(border=True):
        col_title, col_lang = st.columns([3, 1])

        with col_lang:
            lang_choice = st.radio(
                "Language / Bahasa",
                ["Indonesia", "English"],
                horizontal=True,
                key="lang_toggle"
            )
        
        lang_code = "id" if lang_choice == "Indonesia" else "en"
        t = TRANSLATIONS[lang_code]

        with col_title:
            st.markdown(
                f'''
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                    <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#FF4B4B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                        <line x1="16" y1="13" x2="8" y2="13"></line>
                        <line x1="16" y1="17" x2="8" y2="17"></line>
                        <polyline points="10 9 9 9 8 9"></polyline>
                    </svg>
                    <h1 style="margin: 0; padding: 0; font-size: 1.85rem;">{t["app_title"]}</h1>
                </div>
                ''',
                unsafe_allow_html=True
            )
            st.write(t["app_subtitle"])

    # Initialize section counters in session state
    if 'edu_count' not in st.session_state:
        st.session_state['edu_count'] = 1
    if 'work_count' not in st.session_state:
        st.session_state['work_count'] = 1 
    if 'org_count' not in st.session_state:
        st.session_state['org_count'] = 0 
    if 'proj_count' not in st.session_state:
        st.session_state['proj_count'] = 1

    show_import_section(lang_code)

    data = {}

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        t["tab_personal"],
        t["tab_education"],
        t["tab_experience"],
        t["tab_organizations"],
        t["tab_skills_projects"],
        t["tab_ats_check"]
    ])

    with tab1:
        with st.container(border=True):
            st.header(t["personal_header"])
            col1, col2 = st.columns(2)
            data['name'] = col1.text_input(t["full_name"], key="input_name")
            data['email'] = col2.text_input(t["email"], key="input_email")
            data['phone'] = col1.text_input(t["phone"], key="input_phone")
            data['location'] = col2.text_input(t["location"], key="input_location")
            data['linkedin'] = st.text_input(t["linkedin"], key="input_linkedin")
            
            include_github = st.checkbox(t.get("toggle_portfolio", "Sertakan Portfolio / GitHub di CV"), value=True, key="input_toggle_github")
            if include_github:
                data['github'] = st.text_input(t["github"], key="input_github")
            else:
                data['github'] = ""
            
            data['summary'] = st.text_area(t["summary"], height=140, placeholder=t["summary_placeholder"], key="input_summary")

    with tab2:
        with st.container(border=True):
            st.header(t["edu_header"])
            data['education'] = []
            for i in range(st.session_state['edu_count']):
                with st.container(border=True):
                    st.subheader(f"{t['edu_title']} {i+1}")
                    cols = st.columns(2)
                    school = cols[0].text_input(f"{t['school']}", key=f"school_{i}")
                    degree = cols[1].text_input(f"{t['degree']}", key=f"degree_{i}")
                    dates = st.text_input(f"{t['dates']}", key=f"edu_dates_{i}")
                    
                    if school: 
                        data['education'].append({'school': school, 'degree': degree, 'dates': dates})
            
            c_add, c_del = st.columns(2)
            if c_add.button(t["add_edu"], icon=":material/add:", use_container_width=True):
                st.session_state['edu_count'] += 1
                st.rerun()
            if c_del.button(t["del_edu"], icon=":material/remove:", disabled=st.session_state['edu_count'] <= 0, use_container_width=True):
                st.session_state['edu_count'] -= 1
                st.rerun()

    with tab3:
        with st.container(border=True):
            st.header(t["work_header"])
            data['experience'] = []
            for i in range(st.session_state['work_count']):
                with st.container(border=True):
                    st.subheader(f"{t['role']} {i+1}")
                    c1 = st.columns(2)
                    title = c1[0].text_input(f"{t['job_title']}", key=f"job_{i}")
                    company = c1[1].text_input(f"{t['company']}", key=f"company_{i}")
                    dates = st.text_input(f"{t['dates']}", key=f"job_dates_{i}")
                    desc = st.text_area(f"{t['work_desc']}", height=120, key=f"job_desc_{i}")
                    
                    if title: 
                        data['experience'].append({'title': title, 'company': company, 'dates': dates, 'description': desc})
                    
            c_add, c_del = st.columns(2)
            if c_add.button(t["add_work"], icon=":material/add:", use_container_width=True):
                st.session_state['work_count'] += 1
                st.rerun()
            if c_del.button(t["del_work"], icon=":material/remove:", disabled=st.session_state['work_count'] <= 0, use_container_width=True):
                st.session_state['work_count'] -= 1
                st.rerun()

    with tab4:
        with st.container(border=True):
            st.header(t["org_header"])
            data['organizations'] = []
            for i in range(st.session_state['org_count']):
                with st.container(border=True):
                    st.subheader(f"{t['org_item']} {i+1}")
                    c1 = st.columns(2)
                    title = c1[0].text_input(f"{t['org_role']}", key=f"org_role_{i}")
                    company = c1[1].text_input(f"{t['org_name']}", key=f"org_name_{i}")
                    dates = st.text_input(f"{t['dates']}", key=f"org_dates_{i}")
                    desc = st.text_area(f"{t['org_desc']}", height=120, key=f"org_desc_{i}")
                    
                    if title: 
                        data['organizations'].append({'title': title, 'company': company, 'dates': dates, 'description': desc})
                    
            c_add, c_del = st.columns(2)
            if c_add.button(t["add_org"], icon=":material/add:", use_container_width=True):
                st.session_state['org_count'] += 1
                st.rerun()
            if c_del.button(t["del_org"], icon=":material/remove:", disabled=st.session_state['org_count'] <= 0, use_container_width=True):
                st.session_state['org_count'] -= 1
                st.rerun()

    with tab5:
        with st.container(border=True):
            st.header(t["skills_header"])
            data['skills'] = st.text_area(t["skills_label"], height=100, placeholder=t["skills_placeholder"], key="input_skills")
            
            st.header(t["achievements_header"])
            include_projects = st.checkbox(t.get("toggle_projects_section", "Sertakan bagian Prestasi & Proyek pada CV"), value=True, key="input_toggle_projects")
            
            data['projects'] = []
            if include_projects:
                for i in range(st.session_state['proj_count']):
                    with st.container(border=True):
                        st.subheader(f"{t.get('item', t.get('achievement', 'Prestasi / Proyek'))} {i+1}")
                        name = st.text_input(f"{t.get('item_name', t.get('achieve_name', 'Nama'))}", key=f"proj_name_{i}")
                        desc = st.text_area(f"{t.get('item_desc', t.get('achieve_desc', 'Detail'))}", height=90, key=f"proj_desc_{i}")
                        
                        if name:
                            data['projects'].append({'name': name, 'description': desc})
                
                c_add, c_del = st.columns(2)
                if c_add.button(t.get("add_proj", t.get("add_achieve", "Tambah Prestasi")), icon=":material/add:", use_container_width=True):
                    st.session_state['proj_count'] += 1
                    st.rerun()
                if c_del.button(t.get("del_proj", t.get("del_achieve", "Hapus Prestasi")), icon=":material/remove:", disabled=st.session_state['proj_count'] <= 0, use_container_width=True):
                    st.session_state['proj_count'] -= 1
                    st.rerun()

    with tab6:
        with st.container(border=True):
            st.header(t.get("ats_check_header", t.get("ats_header", "Audit Kompatibilitas ATS")))
            st.write(t.get("ats_check_desc", t.get("ats_desc", "")))
            
            job_desc_input = st.text_area(
                t.get("job_desc_label", "Tempel Deskripsi Lowongan Kerja (Opsional)"),
                height=150,
                placeholder=t.get("job_desc_placeholder", ""),
                key="input_job_desc"
            )

            audit_result = analyze_ats(data, job_desc_input)

            c_sc1, c_sc2, c_sc3, c_sc4 = st.columns(4)
            c_sc1.metric(t.get("overall_score_label", t.get("score_label", "Skor ATS")), f"{audit_result.score}/100")
            if job_desc_input.strip():
                c_sc2.metric(t["match_rate_label"], f"{audit_result.keyword_match_rate:.0%}")
            else:
                c_sc2.metric(t["match_rate_label"], "N/A")
            c_sc3.metric(t["metrics_label"], audit_result.quantifiable_metrics_count)
            c_sc4.metric(t["verbs_label"], audit_result.action_verbs_count)

            if job_desc_input.strip():
                c_kw1, c_kw2 = st.columns(2)
                with c_kw1:
                    st.subheader(t["matched_kw_title"])
                    if audit_result.matched_keywords:
                        badges = " ".join([f"`{kw}`" for kw in audit_result.matched_keywords[:25]])
                        st.markdown(badges)
                    else:
                        st.info("Belum ada kata kunci yang cocok.")
                with c_kw2:
                    st.subheader(t["missing_kw_title"])
                    if audit_result.missing_keywords:
                        badges = " ".join([f"`{kw}`" for kw in audit_result.missing_keywords[:25]])
                        st.markdown(badges)
                    else:
                        st.success("Semua kata kunci utama sudah tercakup!")

            if audit_result.feedback_notes:
                st.subheader(t["recommendations_title"])
                for note in audit_result.feedback_notes:
                    st.warning(f"💡 {note}")
            else:
                st.success("CV sudah memenuhi standar kelayakan dasar ATS!")

    # Document settings container
    with st.container(border=True):
        st.subheader(t["doc_settings"])
        st.markdown(
            f'''
            <div style="display: flex; align-items: center; gap: 10px; padding: 12px 16px; background-color: rgba(255,255,255,0.05); border-left: 4px solid #FF4B4B; border-radius: 4px; margin-bottom: 16px;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FF4B4B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="9" y1="18" x2="15" y2="18"></line>
                    <line x1="10" y1="22" x2="14" y2="22"></line>
                    <path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1.55.64 2.8 1.5 3.5.76.76 1.23 1.52 1.41 2.5"></path>
                </svg>
                <span>{t["font_tip"]}</span>
            </div>
            ''',
            unsafe_allow_html=True
        )
        
        col_set1, col_set2, col_set3 = st.columns(3)
        font_choice = col_set1.selectbox(t["select_font"], ["Times New Roman", "Arial", "Courier"], key="font_choice")
        cv_lang_choice = col_set2.selectbox(
            t["cv_lang_label"],
            ["Bahasa Indonesia", "English"],
            index=0 if lang_code == "id" else 1,
            key="cv_lang_choice"
        )
        cv_lang_code = "id" if cv_lang_choice == "Bahasa Indonesia" else "en"

        order_choice = col_set3.selectbox(
            t["section_order_label"],
            [t["order_standard"], t["order_academic"]],
            key="section_order_choice"
        )

        if order_choice == t["order_academic"]:
            section_order = ["summary", "skills", "education", "experience", "organizations", "projects"]
        else:
            section_order = ["summary", "skills", "experience", "organizations", "education", "projects"]
        
        submitted = st.button(t["generate_btn"], type="primary", use_container_width=True, icon=":material/description:")

        if submitted:
            if not data['name']:
                st.error(t["name_required"])
            else:
                pdf_bytes = generate_cv(data, font_choice, lang=cv_lang_code, section_order=section_order)
                st.success(t["success_msg"])
                
                # Preview PDF
                b64 = base64.b64encode(pdf_bytes).decode()
                pdf_display = f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="800" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
                
                # Action download buttons
                c_dl1, c_dl2, c_dl3 = st.columns(3)
                c_dl1.download_button(
                    label=t["download_btn"],
                    data=pdf_bytes,
                    file_name=f"{data['name']}_CV.pdf",
                    mime="application/pdf",
                    icon=":material/download:",
                    use_container_width=True
                )
                c_dl2.download_button(
                    label=t["download_md_btn"],
                    data=cv_to_markdown(data),
                    file_name=f"{data['name']}_CV.md",
                    mime="text/markdown",
                    icon=":material/code:",
                    use_container_width=True
                )
                c_dl3.download_button(
                    label=t["download_json_btn"],
                    data=cv_to_json(data),
                    file_name=f"{data['name']}_CV.json",
                    mime="application/json",
                    icon=":material/data_object:",
                    use_container_width=True
                )


if __name__ == "__main__":
    main()
