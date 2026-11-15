import re

from fpdf import FPDF
from fpdf.enums import XPos, YPos
from translations import CV_SECTION_HEADERS

BULLET_MARKERS = ("-", "*", "+", "•", "●", "▪", "◦", "·")
LINE_HEIGHT = 4.7
BODY_SIZE = 10
MARGIN_X = 15


class PDF(FPDF):
    def __init__(self):
        super().__init__(format="A4")
        # cp1252 keeps real bullets, en dashes and curly quotes extractable as text
        self.core_fonts_encoding = "cp1252"


def clean_text(text):
    if not text:
        return ""
    text = str(text).replace(" ", " ").replace("\t", " ")
    return text.encode("cp1252", "replace").decode("cp1252")


def md_safe(text):
    """Strip fpdf2 markdown markers so user text is never read as bold/italic/underline."""
    return clean_text(text).replace("**", "").replace("__", "").replace("--", "-")


DEFAULT_SECTIONS = ["summary", "skills", "experience", "organizations", "education", "projects"]


def split_description(desc):
    """Return (bullets, tech_line). A short unmarked first line above marked bullets is a tech-stack line."""
    lines = [line.strip() for line in (desc or "").splitlines() if line.strip()]
    marked = [line.startswith(BULLET_MARKERS) for line in lines]
    tech = ""
    if lines and any(marked) and not marked[0] and len(lines[0]) <= 140 and not lines[0].endswith("."):
        tech = lines.pop(0)
    bullets = [re.sub(r"^[-*+•●▪◦·]\s*", "", line) for line in lines]
    return bullets, tech


def generate_cv(data, font_choice="Times New Roman", lang="en", section_order=None):
    pdf = PDF()
    pdf.set_margins(MARGIN_X, 12, MARGIN_X)
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.add_page()
    pdf.set_text_color(0, 0, 0)

    font_map = {
        "Times New Roman": "Times",
        "Arial": "Helvetica",
        "Courier": "Courier",
    }
    main_font = font_map.get(font_choice, "Times")
    headers = CV_SECTION_HEADERS.get(lang, CV_SECTION_HEADERS["en"])
    page_width = pdf.w - 2 * MARGIN_X

    def font(style="", size=BODY_SIZE):
        pdf.set_font(main_font, style, size)

    # 1. Name
    font("", 24)
    pdf.set_char_spacing(1.2)
    name = clean_text(data.get("name") or "Name").upper()
    pdf.cell(0, 10, name, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_char_spacing(0)

    # 2. Contact lines: location, then phone | email | links (each centered, links underlined)
    def prep_url(url):
        url = clean_text(url)
        return url if url.startswith(("http://", "https://")) else f"https://{url}"

    def centered_segments(segments, size=BODY_SIZE):
        """segments: [(text, link or None)]; wrap greedily onto centered lines joined by ' | '."""
        separator = " | "
        lines, current, width = [], [], 0.0
        for text, link in segments:
            font("U" if link else "", size)
            seg_width = pdf.get_string_width(text)
            font("", size)
            sep_width = pdf.get_string_width(separator) if current else 0
            if current and width + sep_width + seg_width > page_width:
                lines.append((current, width))
                current, width, sep_width = [], 0.0, 0.0
            current.append((text, link, seg_width))
            width += sep_width + seg_width
        if current:
            lines.append((current, width))
        for items, total in lines:
            pdf.set_x(MARGIN_X + (page_width - total) / 2)
            for index, (text, link, seg_width) in enumerate(items):
                if index:
                    font("", size)
                    pdf.cell(pdf.get_string_width(separator), LINE_HEIGHT, separator)
                font("U" if link else "", size)
                pdf.cell(seg_width, LINE_HEIGHT, text, link=link or "")
            font("", size)
            pdf.ln(LINE_HEIGHT)

    if data.get("location"):
        font("", BODY_SIZE)
        pdf.cell(0, LINE_HEIGHT, clean_text(data["location"]), align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    contact = []
    if data.get("phone"):
        contact.append((clean_text(data["phone"]), None))
    if data.get("email"):
        email = clean_text(data["email"])
        contact.append((email, f"mailto:{email}"))
    for key in ("linkedin", "github"):
        if data.get(key):
            label = clean_text(data[key])
            contact.append((label, prep_url(label)))
    centered_segments(contact)
    pdf.ln(1)

    # 3. Building blocks
    def section_header(title):
        if pdf.will_page_break(14):
            pdf.add_page()
        pdf.ln(2.5)
        font("B", 12)
        pdf.cell(0, 6, clean_text(title), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_line_width(0.3)
        pdf.line(MARGIN_X, pdf.get_y() + 0.3, pdf.w - MARGIN_X, pdf.get_y() + 0.3)
        pdf.ln(1.8)

    def row(left, right="", left_style="", right_style="", markdown=False, min_space=0):
        """Left text wraps in the available width; right text (usually a date) sits flush right on the first line."""
        if pdf.will_page_break(max(min_space, LINE_HEIGHT)):
            pdf.add_page()
        font(right_style)
        right = re.sub(r"\s+-\s+", " – ", clean_text(right))
        right_width = pdf.get_string_width(right) + 1 if right else 0
        y = pdf.get_y()
        font(left_style)
        pdf.set_xy(MARGIN_X, y)
        if left:
            pdf.multi_cell(page_width - right_width - 2, LINE_HEIGHT, left, markdown=markdown, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        else:
            pdf.set_y(y + LINE_HEIGHT)
        end_y = pdf.get_y()
        if right:
            font(right_style)
            pdf.set_xy(pdf.w - MARGIN_X - right_width, y)
            pdf.cell(right_width, LINE_HEIGHT, right, align="R")
        pdf.set_xy(MARGIN_X, end_y)

    def bullets(items):
        indent = 5.5
        font("")
        for text in items:
            text = clean_text(text)
            height = len(pdf.multi_cell(page_width - indent, LINE_HEIGHT, text, dry_run=True, output="LINES")) * LINE_HEIGHT
            if pdf.will_page_break(height):
                pdf.add_page()
            y = pdf.get_y()
            pdf.set_xy(MARGIN_X + 1.5, y)
            pdf.cell(3.5, LINE_HEIGHT, "•")
            pdf.set_xy(MARGIN_X + indent, y)
            pdf.multi_cell(page_width - indent, LINE_HEIGHT, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def entry(heading, right, subtitle, desc, tech_beside_heading=False):
        items, tech = split_description(desc)
        left_markdown = f"**{md_safe(heading)}**"
        if tech and tech_beside_heading:
            left_markdown += f" | __{md_safe(tech)}__"
        header_lines = 1 + bool(subtitle) + bool(tech and not tech_beside_heading)
        row(left_markdown, right, markdown=True, min_space=LINE_HEIGHT * (header_lines + 1))
        if subtitle:
            row(f"__{md_safe(subtitle)}__", markdown=True)
        if tech and not tech_beside_heading:
            row(f"__{md_safe(tech)}__", markdown=True)
        bullets(items)
        pdf.ln(1.8)

    # 4. Sections
    def render_summary():
        if data.get("summary"):
            section_header(headers["summary"])
            font("")
            pdf.multi_cell(0, LINE_HEIGHT, clean_text(data["summary"]), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def render_skills():
        if data.get("skills"):
            section_header(headers["skills"])
            for raw in clean_text(data["skills"]).splitlines():
                line = re.sub(r"^[-*+•●▪◦·]\s*", "", raw.strip())
                if not line:
                    continue
                label, sep, rest = line.partition(":")
                if sep and rest.strip() and len(label.split()) <= 6:
                    line = f"**{md_safe(label)}:**{md_safe(rest)}"
                else:
                    line = md_safe(line)
                if pdf.will_page_break(LINE_HEIGHT):
                    pdf.add_page()
                font("")
                pdf.set_x(MARGIN_X + 1.5)
                pdf.multi_cell(page_width - 1.5, LINE_HEIGHT, line, markdown=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(0.8)

    def render_work(key):
        if data.get(key):
            section_header(headers[key])
            for item in data[key]:
                company = item.get("company", "")
                title = item.get("title", "")
                heading, subtitle = (company, title) if company else (title, "")
                entry(heading, item.get("dates", ""), subtitle, item.get("description", item.get("desc", "")))

    def render_education():
        if data.get("education"):
            section_header(headers["education"])
            for edu in data["education"]:
                school = edu.get("school", "")
                degree = edu.get("degree", "")
                heading, subtitle = (school, degree) if school else (degree, "")
                entry(heading, edu.get("dates", ""), subtitle, edu.get("description", ""))

    def render_projects():
        if data.get("projects"):
            section_header(headers["projects"])
            for proj in data["projects"]:
                entry(
                    proj.get("name", ""),
                    proj.get("dates", ""),
                    "",
                    proj.get("description", proj.get("desc", "")),
                    tech_beside_heading=True,
                )

    dispatch = {
        "summary": render_summary,
        "skills": render_skills,
        "experience": lambda: render_work("experience"),
        "organizations": lambda: render_work("organizations"),
        "education": render_education,
        "projects": render_projects,
    }

    for section in section_order or DEFAULT_SECTIONS:
        if section in dispatch:
            dispatch[section]()

    return bytes(pdf.output())
