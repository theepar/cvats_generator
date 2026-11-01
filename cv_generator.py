import html
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from translations import CV_SECTION_HEADERS

class PDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font('Times', '', 10)

def clean_text(text):
    if not text:
        return ""
    replacements = {
        '\u2022': '-',
        '\u2013': '-',
        '\u2014': '--',
        '\u2018': "'",
        '\u2019': "'",
        '\u201c': '"',
        '\u201d': '"',
        '\u2026': '...',
        '\u00a0': ' ',
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    return text.encode('latin-1', 'replace').decode('latin-1')

DEFAULT_SECTIONS = ["summary", "skills", "experience", "organizations", "education", "projects"]

def generate_cv(data, font_choice="Times New Roman", lang="en", section_order=None):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    font_map = {
        "Times New Roman": "Times",
        "Arial": "Helvetica",
        "Courier": "Courier"
    }
    main_font = font_map.get(font_choice, "Times")
    headers = CV_SECTION_HEADERS.get(lang, CV_SECTION_HEADERS["en"])
    
    # 1. Header (Name)
    pdf.set_font(main_font, 'B', 24)
    name = clean_text(data.get('name', 'Name')).upper()
    pdf.cell(0, 10, name, align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_font(main_font, '', 11)
    
    def prep_url(url):
        if not url: return ""
        url = clean_text(url)
        if not url.startswith(('http://', 'https://')):
            return f'https://{url}'
        return url

    # 2. Contact details
    parts = []
    if data.get('location'): parts.append(html.escape(clean_text(data['location'])))
    if data.get('phone'): parts.append(html.escape(clean_text(data['phone'])))
    if data.get('email'): 
        email = clean_text(data['email'])
        safe_email = html.escape(email)
        parts.append(f'<a href="mailto:{safe_email}">{safe_email}</a>')
    
    if parts:
        html_contact = " | ".join(parts)
        pdf.write_html(f'<p align="center" style="font-family:{main_font}; font-size:11pt">{html_contact}</p>')
    
    # 3. Links (LinkedIn, GitHub/Portfolio)
    links = []
    if data.get('linkedin'): 
        lbl = clean_text(data['linkedin'])
        url = prep_url(lbl)
        links.append(f'<a href="{html.escape(url)}">{html.escape(lbl)}</a>')
    if data.get('github'): 
        lbl = clean_text(data['github'])
        url = prep_url(lbl)
        links.append(f'<a href="{html.escape(url)}">{html.escape(lbl)}</a>')
    
    if links:
        html_links = " | ".join(links)
        pdf.write_html(f'<p align="center" style="font-family:{main_font}; font-size:11pt">{html_links}</p>')

    pdf.ln(2)

    def add_section_header(title):
        pdf.ln(2)
        pdf.set_font(main_font, 'B', 12)
        pdf.cell(0, 6, title.upper(), align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(2)

    def render_block(entries):
        for item in entries:
            pdf.set_font(main_font, 'B', 11)
            title = clean_text(item.get('title', item.get('name', '')))
            pdf.cell(100, 6, title, align='L', new_x=XPos.RIGHT, new_y=YPos.TOP)
            
            pdf.set_font(main_font, '', 11)
            pdf.cell(0, 6, clean_text(item.get('dates', '')), align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            comp = clean_text(item.get('company', ''))
            pdf.set_font(main_font, 'I', 11)
            pdf.cell(0, 6, comp, align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            pdf.set_font(main_font, '', 11)
            desc = item.get('description', item.get('desc', ''))
            if desc:
                for line in desc.splitlines():
                    line = line.strip()
                    if not line: continue
                    line = clean_text(line)
                    if not line.startswith(('-', '•', '*')):
                        line = '- ' + line
                    
                    current_x = pdf.get_x()
                    pdf.set_x(current_x + 2)
                    pdf.multi_cell(0, 5, line)
                    pdf.set_x(current_x)
            pdf.ln(3)

    # Section render map
    def render_summary():
        if data.get('summary'):
            add_section_header(headers["summary"])
            pdf.set_font(main_font, '', 11)
            pdf.multi_cell(0, 5, clean_text(data['summary']))

    def render_skills():
        if data.get('skills'):
            add_section_header(headers["skills"])
            pdf.set_font(main_font, '', 11)
            pdf.multi_cell(0, 5, clean_text(data['skills']))

    def render_experience():
        if data.get('experience'):
            add_section_header(headers["experience"])
            render_block(data['experience'])

    def render_organizations():
        if data.get('organizations'):
            add_section_header(headers["organizations"])
            render_block(data['organizations'])

    def render_education():
        if data.get('education'):
            add_section_header(headers["education"])
            for edu in data['education']:
                school = edu.get('school', '')
                degree = edu.get('degree', '')
                header = school if school else degree
                sub = degree if school else ''
                
                y = pdf.get_y()
                pdf.set_font(main_font, '', 11)
                pdf.cell(0, 6, clean_text(edu.get('dates', '')), align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                pdf.set_y(y) 
                pdf.set_font(main_font, 'B', 11)
                pdf.cell(120, 6, clean_text(header), align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

                if sub:
                    pdf.set_font(main_font, '', 11)
                    pdf.cell(0, 6, clean_text(sub), align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(2)

    def render_projects():
        if data.get('projects'):
            add_section_header(headers["projects"])
            for proj in data['projects']:
                dates = proj.get('dates', '')
                if dates:
                    y = pdf.get_y()
                    pdf.set_font(main_font, '', 11)
                    pdf.cell(0, 6, clean_text(dates), align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.set_y(y)
                    pdf.set_font(main_font, 'B', 11)
                    pdf.cell(130, 6, clean_text(proj.get('name', '')), align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                else:
                    pdf.set_font(main_font, 'B', 11)
                    pdf.cell(0, 6, clean_text(proj.get('name', '')), align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                pdf.set_font(main_font, '', 11)
                desc = proj.get('description', proj.get('desc', ''))
                if desc:
                    pdf.multi_cell(0, 5, clean_text(desc))
                pdf.ln(3)

    dispatch = {
        "summary": render_summary,
        "skills": render_skills,
        "experience": render_experience,
        "organizations": render_organizations,
        "education": render_education,
        "projects": render_projects,
    }

    sections_to_render = section_order or DEFAULT_SECTIONS
    for sec in sections_to_render:
        if sec in dispatch:
            dispatch[sec]()

    return bytes(pdf.output())
