from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        # No automatic header to allow custom placement on first page
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font('Times', '', 10)
        # self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C') # Optional page number

def clean_text(text):
    if not text: return ""
    # Replacements for Latin-1 compatibility
    replacements = {
        '\u2022': '-',  # Bullet
        '\u2013': '-',  # En dash
        '\u2014': '--', # Em dash
        '\u2018': "'",  # Left single quote
        '\u2019': "'",  # Right single quote
        '\u201c': '"',  # Left double quote
        '\u201d': '"',  # Right double quote
        '\u2026': '...', # Ellipsis
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    # Final safety: encode to latin-1, replacing unknown chars with '?'
    return text.encode('latin-1', 'replace').decode('latin-1')

def generate_cv(data, font_choice="Times New Roman"):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Map friendly names to FPDF core fonts
    font_map = {
        "Times New Roman": "Times",
        "Arial": "Helvetica",
        "Courier": "Courier"
    }
    main_font = font_map.get(font_choice, "Times")
    
    # --- Header ---
    pdf.set_font(main_font, 'B', 24)
    pdf.cell(0, 10, clean_text(data.get('name', 'Name')).upper(), 0, 1, 'C')
    
    pdf.set_font(main_font, '', 11)
    
    # Helper to clean/prep URL
    def prep_url(url):
        if not url: return ""
        url = clean_text(url)
        if not url.startswith('http'):
            return f'https://{url}'
        return url

    # Construct contact line: Location | Phone | Email (Clickable)
    parts = []
    if data.get('location'): parts.append(clean_text(data['location']))
    if data.get('phone'): parts.append(clean_text(data['phone']))
    if data.get('email'): 
        email = clean_text(data['email'])
        parts.append(f'<a href="mailto:{email}">{email}</a>')
    
    if parts:
        html_contact = " | ".join(parts)
        pdf.write_html(f'<p align="center" style="font-family:{main_font}; font-size:11pt">{html_contact}</p>')
    
    # Links Line: LinkedIn | Portfolio
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

    # --- Helper Helper ---
    def add_section_header(title):
        pdf.ln(2)
        pdf.set_font(main_font, 'B', 12)
        pdf.cell(0, 6, title.upper(), 0, 1, 'L')
        # Line is always black
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(2)

    # --- Summary ---
    if data.get('summary'):
        add_section_header("Professional Summary")
        pdf.set_font(main_font, '', 11)
        pdf.multi_cell(0, 5, clean_text(data['summary']))

    # --- Skills ---
    if data.get('skills'):
        add_section_header("Technical Skills")
        pdf.set_font(main_font, '', 11)
        skills_text = clean_text(data['skills'])
        pdf.multi_cell(0, 5, skills_text)

    # --- Experience ---
    # Helper to render job/org/project block
    def render_block(entries):
        for item in entries:
            # Row 1: Title (Left) -- Date (Right)
            pdf.set_font(main_font, 'B', 11)
            title = clean_text(item.get('title', item.get('name', ''))) # Handle 'title' or 'name'
            
            # If there's a website link for the item, make the title clickable? 
            # Or make a "Visit" link? User said "tambahkan section untuk visit webnya lalu bisa diklik"
            # Maybe append (Link) to the title or company?
            # Let's check if 'website' exists
            website = item.get('website')
            
            # We print Title on Left. If website exists, we might bold print the title, then add a small link icon/text?
            # Or just make title clickable if possible using Cell? Cell doesn't support links easily like write_html.
            # We can use write_html for the title line? Alignment is tricky.
            # Let's stick to: Title (Left) ... Dates (Right)
            # Then Company (Left) ... 
            # Maybe put website next to Company? "Company - [Link]"
            
            pdf.cell(100, 6, title, 0, 0, 'L')
            
            pdf.set_font(main_font, '', 11)
            pdf.cell(0, 6, clean_text(item.get('dates', '')), 0, 1, 'R')
            
            # Row 2: Company (Left, Italic)
            comp = clean_text(item.get('company', ''))
            pdf.set_font(main_font, 'I', 11)
            pdf.cell(0, 6, comp, 0, 1, 'L')
            
            # Description (Bulleted)
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

    # --- Education ---
    if data.get('education'):
        add_section_header("Education")
        for edu in data['education']:
            # Row 1: School (Bold) -- Dates (Right)
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
    
    # --- Achievements/Projects ---
    if data.get('projects'):
        add_section_header("Achievements & Projects")
        # Reuse render_block? Projects might not have 'company'.
        # Let's handle generic projects separately or map them.
        for proj in data['projects']:
            pdf.set_font(main_font, 'B', 11)
            pdf.cell(0, 6, clean_text(proj['name']), 0, 1, 'L') 
            
            pdf.set_font(main_font, '', 11)
            desc = proj.get('description', proj.get('desc', ''))
            if desc:
                # If desc is multiline/bulleted, handle it? app.py puts it in 'description'
                # Let's treat it as multiline text.
                pdf.multi_cell(0, 5, clean_text(desc))
            pdf.ln(6)

    return bytes(pdf.output(dest='S'))
