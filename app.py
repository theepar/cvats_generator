import streamlit as st
from cv_generator import generate_cv
import base64

def main():
    st.set_page_config(page_title="CV Generator", page_icon="📄", layout="wide")
    st.title("📄 CV Generator")
    st.write("Isi data Anda di bawah ini untuk membuat CV dalam format PDF.")

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

    # Define defaults - EMPTY for Production
    default_edu = []
    default_work = []
    default_orgs = []
    default_proj = []

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Personal Info", "Education", "Experience", "Organizations", "Skills & Projects"])

    with tab1:
        st.header("Personal Information")
        col1, col2 = st.columns(2)
        data['name'] = col1.text_input("Nama Lengkap", "")
        data['email'] = col2.text_input("Email", "")
        data['phone'] = col1.text_input("No. Telepon", "")
        data['location'] = col2.text_input("Lokasi", "")
        data['linkedin'] = st.text_input("LinkedIn", "")
        data['github'] = st.text_input("Portfolio/GitHub", "")
        
        default_summary = ""
        data['summary'] = st.text_area("Ringkasan Profil", default_summary, height=150)

    with tab2:
        st.header("Education")
        data['education'] = []
        for i in range(st.session_state['edu_count']):
            st.subheader(f"Education {i+1}")
            cols = st.columns(2)
            school = cols[0].text_input(f"School/University", key=f"school_{i}")
            degree = cols[1].text_input(f"Degree", key=f"degree_{i}")
            dates = st.text_input(f"Dates", key=f"edu_dates_{i}")
            
            if school: 
                data['education'].append({'school': school, 'degree': degree, 'dates': dates})
            st.divider()
        
        c_add, c_del = st.columns(2)
        if c_add.button("➕ Add Education"):
            st.session_state['edu_count'] += 1
            st.rerun()
        if c_del.button("➖ Delete Education", disabled=st.session_state['edu_count'] <= 0):
            st.session_state['edu_count'] -= 1
            st.rerun()

    with tab3:
        st.header("Work Experience")
        data['experience'] = []
        for i in range(st.session_state['work_count']):
            st.subheader(f"Role {i+1}")
            
            c1 = st.columns(2)
            title = c1[0].text_input(f"Job Title", key=f"job_{i}")
            company = c1[1].text_input(f"Company", key=f"company_{i}")
            dates = st.text_input(f"Dates", key=f"job_dates_{i}")
            desc = st.text_area(f"Description / Achievements", height=120, key=f"job_desc_{i}")
            
            if title: 
                data['experience'].append({'title': title, 'company': company, 'dates': dates, 'description': desc})
            st.divider()
            
        c_add, c_del = st.columns(2)
        if c_add.button("➕ Add Experience"):
            st.session_state['work_count'] += 1
            st.rerun()
        if c_del.button("➖ Delete Experience", disabled=st.session_state['work_count'] <= 0):
            st.session_state['work_count'] -= 1
            st.rerun()

    with tab4:
        st.header("Organizations")
        data['organizations'] = []
        for i in range(st.session_state['org_count']):
            st.subheader(f"Organization {i+1}")
            
            c1 = st.columns(2)
            title = c1[0].text_input(f"Role/Position", key=f"org_role_{i}")
            company = c1[1].text_input(f"Organization Name", key=f"org_name_{i}")
            dates = st.text_input(f"Dates", key=f"org_dates_{i}")
            desc = st.text_area(f"Description", height=120, key=f"org_desc_{i}")
            
            if title: 
                data['organizations'].append({'title': title, 'company': company, 'dates': dates, 'description': desc})
            st.divider()
            
        c_add, c_del = st.columns(2)
        if c_add.button("➕ Add Organization"):
            st.session_state['org_count'] += 1
            st.rerun()
        if c_del.button("➖ Delete Organization", disabled=st.session_state['org_count'] <= 0):
            st.session_state['org_count'] -= 1
            st.rerun()

    with tab5:
        st.header("Skills")
        default_skills = ""
        data['skills'] = st.text_area("Skills", default_skills, height=100, placeholder="Contoh:\n• Languages: PHP, JavaScript, Python\n• Framework: Laravel, React, Django")
        
        st.header("Achievements")
        data['projects'] = []
        
        for i in range(st.session_state['proj_count']):
            st.subheader(f"Achievement {i+1}")
            
            proj_name = st.text_input(f"Name", key=f"proj_name_{i}")
            proj_desc = st.text_area(f"Details", key=f"proj_desc_{i}")
            if proj_name: 
                data['projects'].append({'name': proj_name, 'description': proj_desc})
            st.divider()
        
        c_add, c_del = st.columns(2)
        if c_add.button("➕ Add Achievement"):
            st.session_state['proj_count'] += 1
            st.rerun()
        if c_del.button("➖ Delete Achievement", disabled=st.session_state['proj_count'] <= 0):
            st.session_state['proj_count'] -= 1
            st.rerun()

    st.markdown("---")
    
    # Font Selection
    st.subheader("Pengaturan Dokumen")
    st.info("💡 Times New Roman lebih cocok untuk sistem ATS lama. Arial lebih modern.")
    font_choice = st.selectbox("Pilih Font", ["Times New Roman", "Arial", "Courier"])
    
    submitted = st.button("Buat CV", type="primary", use_container_width=True)

    if submitted:
        if not data['name']:
            st.error("Mohon isi nama Anda terlebih dahulu.")
        else:
            pdf_bytes = generate_cv(data, font_choice)
            st.success("CV berhasil dibuat!")
            
            # Display PDF in browser
            b64 = base64.b64encode(pdf_bytes).decode()
            pdf_display = f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="800" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
            
            # Keep download button as option
            st.download_button(
                label="Download PDF",
                data=pdf_bytes,
                file_name=f"{data['name']}_CV.pdf",
                mime="application/pdf"
            )

if __name__ == "__main__":
    main()
