import streamlit as st
from cv_generator import generate_cv
from translations import TRANSLATIONS
import base64

def main():
    st.set_page_config(page_title="CV Generator", page_icon="📄", layout="wide")
    
    # Language Selection in Sidebar
    st.sidebar.header("🌐 Language Settings / Pengaturan Bahasa")
    lang_choice = st.sidebar.radio(
        "Pilih Bahasa UI / Select UI Language:",
        ["Bahasa Indonesia", "English"],
        index=0
    )
    lang_code = "id" if lang_choice == "Bahasa Indonesia" else "en"
    t = TRANSLATIONS[lang_code]

    st.title(t["app_title"])
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
        data['name'] = col1.text_input(t["full_name"], "")
        data['email'] = col2.text_input(t["email"], "")
        data['phone'] = col1.text_input(t["phone"], "")
        data['location'] = col2.text_input(t["location"], "")
        data['linkedin'] = st.text_input(t["linkedin"], "")
        data['github'] = st.text_input(t["github"], "")
        
        data['summary'] = st.text_area(t["summary"], "", height=150, placeholder=t["summary_placeholder"])

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
        if c_add.button(t["add_edu"]):
            st.session_state['edu_count'] += 1
            st.rerun()
        if c_del.button(t["del_edu"], disabled=st.session_state['edu_count'] <= 0):
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
        if c_add.button(t["add_work"]):
            st.session_state['work_count'] += 1
            st.rerun()
        if c_del.button(t["del_work"], disabled=st.session_state['work_count'] <= 0):
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
        if c_add.button(t["add_org"]):
            st.session_state['org_count'] += 1
            st.rerun()
        if c_del.button(t["del_org"], disabled=st.session_state['org_count'] <= 0):
            st.session_state['org_count'] -= 1
            st.rerun()

    with tab5:
        st.header(t["skills_header"])
        data['skills'] = st.text_area(t["skills_label"], "", height=100, placeholder=t["skills_placeholder"])
        
        st.header(t["achievements_header"])
        data['projects'] = []
        
        for i in range(st.session_state['proj_count']):
            st.subheader(f"{t['achievement']} {i+1}")
            
            proj_name = st.text_input(f"{t['achieve_name']}", key=f"proj_name_{i}")
            proj_desc = st.text_area(f"{t['achieve_desc']}", key=f"proj_desc_{i}")
            if proj_name: 
                data['projects'].append({'name': proj_name, 'description': proj_desc})
            st.divider()
        
        c_add, c_del = st.columns(2)
        if c_add.button(t["add_achieve"]):
            st.session_state['proj_count'] += 1
            st.rerun()
        if c_del.button(t["del_achieve"], disabled=st.session_state['proj_count'] <= 0):
            st.session_state['proj_count'] -= 1
            st.rerun()

    st.markdown("---")
    
    # Document & Output Settings
    st.subheader(t["doc_settings"])
    st.info(t["font_tip"])
    
    col_set1, col_set2 = st.columns(2)
    font_choice = col_set1.selectbox(t["select_font"], ["Times New Roman", "Arial", "Courier"])
    cv_lang_choice = col_set2.selectbox(
        t["cv_lang_label"],
        ["Bahasa Indonesia", "English"],
        index=0 if lang_code == "id" else 1
    )
    cv_lang_code = "id" if cv_lang_choice == "Bahasa Indonesia" else "en"
    
    submitted = st.button(t["generate_btn"], type="primary", use_container_width=True)

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
                mime="application/pdf"
            )

if __name__ == "__main__":
    main()
