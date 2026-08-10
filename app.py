import streamlit as st
from cv_generator import generate_cv
from translations import TRANSLATIONS
import base64

def main():
    st.set_page_config(page_title="CV Generator", layout="wide")

    # Language Toggle at top of main page (No flag emojis/tags)
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
                <h1 style="margin: 0; padding: 0; font-size: 2rem;">{t["app_title"]}</h1>
            </div>
            ''',
            unsafe_allow_html=True
        )
        st.write(t["app_subtitle"])

    # Initialize session state for dynamic fields
    if 'edu_count' not in st.session_state:
        st.session_state['edu_count'] = 1
    if 'work_count' not in st.session_state:
        st.session_state['work_count'] = 1 
    if 'org_count' not in st.session_state:
        st.session_state['org_count'] = 0 
    if 'proj_count' not in st.session_state:
        st.session_state['proj_count'] = 1

    data = {}

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        t["tab_personal"],
        t["tab_education"],
        t["tab_experience"],
        t["tab_organizations"],
        t["tab_skills_projects"]
    ])

    with tab1:
        st.header(t["personal_header"])
        col1, col2 = st.columns(2)
        data['name'] = col1.text_input(t["full_name"], key="input_name")
        data['email'] = col2.text_input(t["email"], key="input_email")
        data['phone'] = col1.text_input(t["phone"], key="input_phone")
        data['location'] = col2.text_input(t["location"], key="input_location")
        data['linkedin'] = st.text_input(t["linkedin"], key="input_linkedin")
        
        include_github = st.checkbox(t.get("toggle_portfolio", "Sertakan Portfolio / GitHub"), value=True, key="input_toggle_github")
        if include_github:
            data['github'] = st.text_input(t["github"], key="input_github")
        else:
            data['github'] = ""
        
        data['summary'] = st.text_area(t["summary"], height=150, placeholder=t["summary_placeholder"], key="input_summary")

    with tab2:
        st.header(t["edu_header"])
        data['education'] = []
        for i in range(st.session_state['edu_count']):
            st.subheader(f"{t['edu_title']} {i+1}")
            cols = st.columns(2)
            school = cols[0].text_input(f"{t['school']}", key=f"school_{i}")
            degree = cols[1].text_input(f"{t['degree']}", key=f"degree_{i}")
            dates = st.text_input(f"{t['dates']}", key=f"edu_dates_{i}")
            
            if school: 
                data['education'].append({'school': school, 'degree': degree, 'dates': dates})
            st.divider()
        
        c_add, c_del = st.columns(2)
        if c_add.button(t["add_edu"], icon=":material/add:"):
            st.session_state['edu_count'] += 1
            st.rerun()
        if c_del.button(t["del_edu"], icon=":material/remove:", disabled=st.session_state['edu_count'] <= 0):
            st.session_state['edu_count'] -= 1
            st.rerun()

    with tab3:
        st.header(t["work_header"])
        data['experience'] = []
        for i in range(st.session_state['work_count']):
            st.subheader(f"{t['role']} {i+1}")
            
            c1 = st.columns(2)
            title = c1[0].text_input(f"{t['job_title']}", key=f"job_{i}")
            company = c1[1].text_input(f"{t['company']}", key=f"company_{i}")
            dates = st.text_input(f"{t['dates']}", key=f"job_dates_{i}")
            desc = st.text_area(f"{t['work_desc']}", height=120, key=f"job_desc_{i}")
            
            if title: 
                data['experience'].append({'title': title, 'company': company, 'dates': dates, 'description': desc})
            st.divider()
            
        c_add, c_del = st.columns(2)
        if c_add.button(t["add_work"], icon=":material/add:"):
            st.session_state['work_count'] += 1
            st.rerun()
        if c_del.button(t["del_work"], icon=":material/remove:", disabled=st.session_state['work_count'] <= 0):
            st.session_state['work_count'] -= 1
            st.rerun()

    with tab4:
        st.header(t["org_header"])
        data['organizations'] = []
        for i in range(st.session_state['org_count']):
            st.subheader(f"{t['org_item']} {i+1}")
            
            c1 = st.columns(2)
            title = c1[0].text_input(f"{t['org_role']}", key=f"org_role_{i}")
            company = c1[1].text_input(f"{t['org_name']}", key=f"org_name_{i}")
            dates = st.text_input(f"{t['dates']}", key=f"org_dates_{i}")
            desc = st.text_area(f"{t['org_desc']}", height=120, key=f"org_desc_{i}")
            
            if title: 
                data['organizations'].append({'title': title, 'company': company, 'dates': dates, 'description': desc})
            st.divider()
            
        c_add, c_del = st.columns(2)
        if c_add.button(t["add_org"], icon=":material/add:"):
            st.session_state['org_count'] += 1
            st.rerun()
        if c_del.button(t["del_org"], icon=":material/remove:", disabled=st.session_state['org_count'] <= 0):
            st.session_state['org_count'] -= 1
            st.rerun()

    with tab5:
        st.header(t["skills_header"])
        data['skills'] = st.text_area(t["skills_label"], height=100, placeholder=t["skills_placeholder"], key="input_skills")
        
        st.header(t["achievements_header"])
        include_projects = st.checkbox(t.get("toggle_projects_section", "Sertakan bagian Prestasi & Proyek pada CV"), value=True, key="input_toggle_projects")
        data['projects'] = []
        
        if include_projects:
            for i in range(st.session_state['proj_count']):
                st.subheader(f"{t['achievement']} {i+1}")
                
                proj_name = st.text_input(f"{t['achieve_name']}", key=f"proj_name_{i}")
                proj_desc = st.text_area(f"{t['achieve_desc']}", key=f"proj_desc_{i}")
                if proj_name: 
                    data['projects'].append({'name': proj_name, 'description': proj_desc})
                st.divider()
            
            c_add, c_del = st.columns(2)
            if c_add.button(t["add_achieve"], icon=":material/add:"):
                st.session_state['proj_count'] += 1
                st.rerun()
            if c_del.button(t["del_achieve"], icon=":material/remove:", disabled=st.session_state['proj_count'] <= 0):
                st.session_state['proj_count'] -= 1
                st.rerun()

    st.markdown("---")
    
    # Document & Output Settings
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
    
    col_set1, col_set2 = st.columns(2)
    font_choice = col_set1.selectbox(t["select_font"], ["Times New Roman", "Arial", "Courier"], key="font_choice")
    cv_lang_choice = col_set2.selectbox(
        t["cv_lang_label"],
        ["Bahasa Indonesia", "English"],
        index=0 if lang_code == "id" else 1,
        key="cv_lang_choice"
    )
    cv_lang_code = "id" if cv_lang_choice == "Bahasa Indonesia" else "en"
    
    submitted = st.button(t["generate_btn"], type="primary", use_container_width=True, icon=":material/description:")

    if submitted:
        if not data['name']:
            st.error(t["name_required"])
        else:
            pdf_bytes = generate_cv(data, font_choice, lang=cv_lang_code)
            st.success(t["success_msg"])
            
            # Display PDF in browser
            b64 = base64.b64encode(pdf_bytes).decode()
            pdf_display = f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="800" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
            
            # Keep download button as option
            st.download_button(
                label=t["download_btn"],
                data=pdf_bytes,
                file_name=f"{data['name']}_CV.pdf",
                mime="application/pdf",
                icon=":material/download:"
            )

if __name__ == "__main__":
    main()
