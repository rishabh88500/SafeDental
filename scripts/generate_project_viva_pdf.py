#!/usr/bin/env python3
"""
generate_project_viva_pdf.py
Generates a publication-grade, professionally formatted PDF document:
SafeDental_Complete_Project_and_Viva_Guide.pdf
from docs/COMPLETE_PROJECT_AND_VIVA_GUIDE.md
"""

import os
import re
from pathlib import Path
from fpdf import FPDF, XPos, YPos


def sanitize_text(text: str) -> str:
    """Replaces unicode characters and emojis with clean ASCII equivalents for PDF rendering."""
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
        "→": "->",
        "←": "<-",
        "↔": "<->",
        "✓": "[Y]",
        "✔": "[Y]",
        "✅": "[PASS]",
        "❌": "[X]",
        "🎓": "",
        "⚡": "",
        "🏥": "",
        "🔬": "",
        "🛠️": "",
        "🏛️": "",
        "🔍": "",
        "🤖": "",
        "📚": "",
        "💡": "[NOTE]",
        "⚠️": "[WARN]",
        "°": " deg ",
        "\\chi^2": "Chi^2",
        "\\chi": "Chi",
        "\\times": "x",
        "\\to": "->",
        "\\text": "",
        "\\circ": " deg",
        "\\,": " ",
        "\\": "",
        "$": "",
        "{": "",
        "}": "",
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)

    # Box-drawing characters
    box_chars = {
        "┌": "+", "┐": "+", "└": "+", "┘": "+",
        "├": "+", "┤": "+", "┬": "+", "┴": "+", "┼": "+",
        "─": "-", "│": "|", "▲": "^", "▼": "v", "►": ">", "◄": "<",
        "═": "=", "║": "|", "╔": "+", "╗": "+", "╚": "+", "╝": "+",
        "╠": "+", "╣": "+", "╦": "+", "╩": "+", "╬": "+",
    }
    for orig, repl in box_chars.items():
        text = text.replace(orig, repl)

    # Strip any remaining emojis or non-latin1 characters
    return text.encode("latin-1", "replace").decode("latin-1")


class ProjectGuidePDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_margins(14, 16, 14)

    def header(self):
        if self.page_no() == 1:
            return  # No header on cover / title page
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(100, 116, 139)  # Slate gray
        header_text = sanitize_text("SafeDental: Clinical Decision Support — Major Project Report & Viva Voce Guide")
        self.cell(0, 6, header_text, border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")
        self.set_draw_color(226, 232, 240)
        self.set_line_width(0.3)
        self.line(14, 22, 196, 22)
        self.ln(3)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(148, 163, 184)
        page_str = f"Page {self.page_no()} of {{nb}}"
        self.cell(0, 8, page_str, align="C")


def clean_markdown_inline(text: str) -> str:
    """Strips markdown bold/italics/code tags for clean text rendering."""
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    return text


def build_pdf_from_markdown(md_file: Path, output_pdf: Path):
    pdf = ProjectGuidePDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)

    content = md_file.read_text(encoding="utf-8")
    lines = content.split("\n")

    in_code_block = False
    code_block_lines = []
    table_lines = []
    in_table = False

    def flush_table(tbl_lines):
        if not tbl_lines:
            return
        # Parse table markdown
        rows = []
        for tl in tbl_lines:
            parts = [clean_markdown_inline(sanitize_text(c.strip())) for c in tl.split("|")]
            # Remove empty first/last elements from leading/trailing pipes
            if parts and parts[0] == "":
                parts = parts[1:]
            if parts and parts[-1] == "":
                parts = parts[:-1]
            if parts and not all(set(c).issubset({"-", ":", " "}) for c in parts):
                rows.append(parts)

        if not rows:
            return

        num_cols = max(len(r) for r in rows)
        if num_cols == 0:
            return

        # Distribute column widths across printable width (182 mm)
        total_width = 182
        if num_cols == 2:
            col_widths = [50, 132]
        elif num_cols == 3:
            col_widths = [45, 60, 77]
        elif num_cols == 4:
            col_widths = [36, 48, 48, 50]
        elif num_cols == 5:
            col_widths = [38, 36, 36, 36, 36]
        else:
            col_widths = [total_width / num_cols] * num_cols

        pdf.set_font("Helvetica", size=8)
        try:
            with pdf.table(col_widths=col_widths, text_align="LEFT") as table:
                is_header = True
                for row_data in rows:
                    row = table.row()
                    # Pad row if missing columns
                    while len(row_data) < num_cols:
                        row_data.append("")
                    for c_idx, cell_value in enumerate(row_data[:num_cols]):
                        if is_header:
                            pdf.set_font("Helvetica", "B", 8)
                        else:
                            pdf.set_font("Helvetica", "", 8)
                        row.cell(cell_value)
                    is_header = False
        except Exception as e:
            # Fallback simple text rendering
            pdf.set_font("Helvetica", "", 8)
            for row_data in rows:
                pdf.cell(0, 5, " | ".join(row_data), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(3)

    idx = 0
    while idx < len(lines):
        line = lines[idx]
        stripped = line.strip()

        # Handle code blocks
        if stripped.startswith("```"):
            if in_code_block:
                in_code_block = False
                # Render code block
                pdf.set_fill_color(248, 250, 252)
                pdf.set_draw_color(203, 213, 225)
                pdf.set_font("Courier", size=7.5)
                pdf.set_text_color(30, 41, 59)
                code_text = sanitize_text("\n".join(code_block_lines))
                # Print code block lines
                for cl in code_text.split("\n"):
                    pdf.cell(0, 3.8, cl, border=0, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(3)
                code_block_lines = []
            else:
                if in_table:
                    flush_table(table_lines)
                    table_lines = []
                    in_table = False
                in_code_block = True
                code_block_lines = []
            idx += 1
            continue

        if in_code_block:
            code_block_lines.append(line)
            idx += 1
            continue

        # Handle tables
        if stripped.startswith("|"):
            in_table = True
            table_lines.append(stripped)
            idx += 1
            continue
        elif in_table:
            flush_table(table_lines)
            table_lines = []
            in_table = False

        if not stripped:
            pdf.ln(2.5)
            idx += 1
            continue

        # Document Header
        if stripped.startswith("# "):
            title = sanitize_text(clean_markdown_inline(stripped[2:]))
            pdf.set_font("Helvetica", "B", 18)
            pdf.set_text_color(30, 58, 138)  # Deep royal navy
            pdf.multi_cell(0, 8, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_draw_color(30, 58, 138)
            pdf.set_line_width(0.8)
            pdf.line(14, pdf.get_y() + 1, 196, pdf.get_y() + 1)
            pdf.ln(4)
            idx += 1
            continue

        # Section Heading 2
        if stripped.startswith("## "):
            title = sanitize_text(clean_markdown_inline(stripped[3:]))
            pdf.ln(3)
            pdf.set_fill_color(241, 245, 249)  # Light slate tint
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(15, 23, 42)     # Slate 900
            pdf.cell(0, 7.5, f"  {title}", fill=True, border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(2)
            idx += 1
            continue

        # Section Heading 3
        if stripped.startswith("### "):
            title = sanitize_text(clean_markdown_inline(stripped[4:]))
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 10.5)
            pdf.set_text_color(14, 116, 144)  # Cyan 700 / Teal
            pdf.cell(0, 6, title, border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(1)
            idx += 1
            continue

        # Viva Question Heading (#### Q...)
        if stripped.startswith("#### Q"):
            q_text = sanitize_text(clean_markdown_inline(stripped[5:].strip()))
            pdf.ln(2.5)
            pdf.set_font("Helvetica", "B", 9.5)
            pdf.set_text_color(30, 58, 138)  # Deep Navy
            pdf.cell(0, 5.5, f"Q: {q_text}", border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(1)
            idx += 1
            continue

        # Blockquote (Answer or Elevator Pitch)
        if stripped.startswith("> "):
            quote_text = sanitize_text(clean_markdown_inline(stripped[2:].strip()))
            # Read ahead if blockquote spans multiple lines
            while idx + 1 < len(lines) and lines[idx + 1].strip().startswith(">"):
                idx += 1
                next_part = sanitize_text(clean_markdown_inline(lines[idx].strip()[1:].strip()))
                if next_part:
                    quote_text += " " + next_part

            pdf.set_fill_color(248, 250, 252)
            pdf.set_draw_color(59, 130, 246)  # Blue accent line
            pdf.set_font("Helvetica", "I", 9)
            pdf.set_text_color(31, 41, 55)

            # Draw left vertical accent bar
            cur_x = pdf.get_x()
            cur_y = pdf.get_y()
            pdf.set_line_width(1.0)

            # Print multi_cell indented by 4mm
            pdf.set_x(cur_x + 4)
            pdf.multi_cell(178, 4.8, quote_text, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            end_y = pdf.get_y()
            pdf.line(cur_x + 1, cur_y, cur_x + 1, end_y)
            pdf.ln(2)
            idx += 1
            continue

        # Bullet point (- or *)
        if stripped.startswith("- ") or stripped.startswith("* "):
            bullet_body = sanitize_text(clean_markdown_inline(stripped[2:].strip()))
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(31, 41, 55)
            pdf.set_x(18)
            pdf.cell(4, 4.8, chr(149), border=0)  # Bullet dot
            pdf.multi_cell(164, 4.8, bullet_body, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            idx += 1
            continue

        # Numbered list (e.g. 1. 2.)
        num_match = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if num_match:
            num = num_match.group(1)
            body = sanitize_text(clean_markdown_inline(num_match.group(2)))
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(31, 41, 55)
            pdf.set_x(18)
            pdf.cell(7, 4.8, f"{num}.", border=0)
            pdf.multi_cell(161, 4.8, body, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            idx += 1
            continue

        # Standard Paragraph
        para_text = sanitize_text(clean_markdown_inline(stripped))
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(0, 4.8, para_text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(1)
        idx += 1

    if in_table:
        flush_table(table_lines)

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output_pdf))
    print(f"Successfully generated PDF report at: {output_pdf}")


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    md_path = project_root / "docs" / "COMPLETE_PROJECT_AND_VIVA_GUIDE.md"
    out_pdf_path = project_root / "SafeDental_Complete_Project_and_Viva_Guide.pdf"
    build_pdf_from_markdown(md_path, out_pdf_path)
