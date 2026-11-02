import re
from pathlib import Path
from fpdf import FPDF, XPos, YPos


def sanitize_text(text: str) -> str:
    """Replaces non-latin1 unicode characters with ASCII equivalents."""
    replacements = {
        "—": "-",
        "–": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "≥": ">=",
        "≤": "<=",
        "±": "+/-",
        "•": "*",
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    # Strip any remaining non-latin1 characters safely
    return text.encode("latin-1", "replace").decode("latin-1")


class DiaryPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(100, 100, 100)
        header_text = sanitize_text("SafeDental - Final Year Research Project Diary")
        self.cell(0, 8, header_text, border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")
        self.set_draw_color(200, 200, 200)
        self.line(10, 18, 200, 18)
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def build_pdf_from_markdown(md_file: Path, output_pdf: Path):
    pdf = DiaryPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    lines = md_file.read_text(encoding="utf-8").split("\n")

    for line in lines:
        stripped = sanitize_text(line.strip())
        if not stripped:
            pdf.ln(3)
            continue

        if stripped.startswith("# "):
            pdf.set_font("Helvetica", "B", 16)
            pdf.set_text_color(24, 43, 73)
            title = stripped[2:]
            pdf.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_draw_color(24, 43, 73)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(4)

        elif stripped.startswith("## "):
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(40, 80, 120)
            pdf.ln(3)
            subtitle = stripped[3:]
            pdf.cell(0, 8, subtitle, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        elif stripped.startswith("### "):
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(0, 50, 100)
            pdf.ln(2)
            subheading = stripped[4:]
            pdf.cell(0, 6, subheading, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        elif stripped.startswith("- "):
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(30, 30, 30)
            bullet_text = stripped[2:].replace("**", "")
            pdf.set_x(15)
            pdf.multi_cell(180, 5, f"* {bullet_text}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        elif stripped.startswith("  - "):
            pdf.set_font("Helvetica", "", 9.5)
            pdf.set_text_color(60, 60, 60)
            subbullet_text = stripped[4:].replace("**", "")
            pdf.set_x(22)
            pdf.multi_cell(173, 5, f"- {subbullet_text}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(40, 40, 40)
            clean_p = stripped.replace("**", "")
            pdf.set_x(10)
            pdf.multi_cell(190, 5, clean_p, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output_pdf))
    print(f"Successfully generated PDF at '{output_pdf}'")


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    md_path = project_root / "docs" / "PROJECT_DIARY.md"
    pdf_path = project_root / "Project diary sh2627.pdf"
    build_pdf_from_markdown(md_path, pdf_path)
