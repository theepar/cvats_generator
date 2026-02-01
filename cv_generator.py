from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font('Times', '', 10)

def clean_text(text):
    if not text: return ""
    replacements = {
        '\u2022': '-',
        '\u2013': '-',
        '\u2014': '--',
        '\u2018': "'",
        '\u2019': "'",
        '\u201c': '"',
        '\u201d': '"',
        '\u2026': '...',
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    return text.encode('latin-1', 'replace').decode('latin-1')

def generate_cv(data, font_choice="Times New Roman"):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    font_map = {
        "Times New Roman": "Times",
        "Arial": "Helvetica",
        "Courier": "Courier"
    }
    main_font = font_map.get(font_choice, "Times")
    
    pdf.set_font(main_font, 'B', 24)
    pdf.cell(0, 10, clean_text(data.get('name', 'Name')).upper(), 0, 1, 'C')
    
    pdf.set_font(main_font, '', 11)
    
    def prep_url(url):
        if not url: return ""
        url = clean_text(url)
        if not url.startswith('http'):
            return f'https://{url}'
        return url

    parts = []
    if data.get('location'): parts.append(clean_text(data['location']))
    if data.get('phone'): parts.append(clean_text(data['phone']))
    if data.get('email'): 
        email = clean_text(data['email'])
        parts.append(f'<a href="mailto:{email}">{email}</a>')
    
    if parts:
        html_contact = " | ".join(parts)
        pdf.write_html(f'<p align="center" style="font-family:{main_font}; font-size:11pt">{html_contact}</p>')
    
    links = []
    if data.get('linkedin'): 
        lbl = clean_text(data['linkedin'])
        url = prep_url(lbl)
        links.append(f'<a href="{url}">{lbl}</a>')
    if data.get('github'): 
        lbl = clean_text(data['github'])
        url = prep_url(lbl)
        links.append(f'<a href="{url}">{lbl}</a>')
    
    if links:
        html_links = " | ".join(links)
        pdf.write_html(f'<p align="center" style="font-family:{main_font}; font-size:11pt">{html_links}</p>')

    pdf.ln(2)

    def add_section_header(title):
        pdf.ln(2)
        pdf.set_font(main_font, 'B', 12)
        pdf.cell(0, 6, title.upper(), 0, 1, 'L')
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(2)

    if data.get('summary'):
        add_section_header("Professional Summary")
        pdf.set_font(main_font, '', 11)
        pdf.multi_cell(0, 5, clean_text(data['summary']))

    if data.get('skills'):
        add_section_header("Technical Skills")
        pdf.set_font(main_font, '', 11)
        skills_text = clean_text(data['skills'])
        pdf.multi_cell(0, 5, skills_text)

    def render_block(entries):
        for item in entries:
            pdf.set_font(main_font, 'B', 11)
            title = clean_text(item.get('title', item.get('name', '')))
            
            pdf.cell(100, 6, title, 0, 0, 'L')
            
            pdf.set_font(main_font, '', 11)
            pdf.cell(0, 6, clean_text(item.get('dates', '')), 0, 1, 'R')
            
            comp = clean_text(item.get('company', ''))
            pdf.set_font(main_font, 'I', 11)
            pdf.cell(0, 6, comp, 0, 1, 'L')
            
            pdf.set_font(main_font, '', 11)
            desc = item.get('description', item.get('desc', ''))
            if desc:
                lines = desc.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line: continue
                    line = clean_text(line)
                    if not line.startswith('-') and not line.startswith('•'):
                        line = '- ' + line
                    
                    current_x = pdf.get_x()
                    pdf.set_x(current_x + 2)
                    pdf.multi_cell(0, 5, line)
                    pdf.set_x(current_x)
            pdf.ln(3)

    if data.get('experience'):
        add_section_header("Work Experience")
        render_block(data['experience'])

    # --- Organizations (New) ---
    if data.get('organizations'):
        add_section_header("Organizational Experience")
        render_block(data['organizations'])

    if data.get('education'):
        add_section_header("Education")
        for edu in data['education']:
            y = pdf.get_y()
            pdf.set_font(main_font, '', 11)
            pdf.cell(0, 6, clean_text(edu.get('dates', '')), 0, 1, 'R')
            
            pdf.set_y(y) 
            pdf.set_font(main_font, 'B', 11)
            pdf.cell(120, 6, clean_text(edu.get('school', '')), 0, 0, 'L')
            pdf.ln(6)

            pdf.set_font(main_font, '', 11)
            pdf.cell(0, 6, clean_text(edu.get('degree', '')), 0, 1, 'L')
            pdf.ln(2)
    
    if data.get('projects'):
        add_section_header("Achievements & Projects")
        for proj in data['projects']:
            pdf.set_font(main_font, 'B', 11)
            pdf.cell(0, 6, clean_text(proj['name']), 0, 1, 'L') 
            
            pdf.set_font(main_font, '', 11)
            desc = proj.get('description', proj.get('desc', ''))
            if desc:
                pdf.multi_cell(0, 5, clean_text(desc))
            pdf.ln(6)

    return bytes(pdf.output(dest='S'))
