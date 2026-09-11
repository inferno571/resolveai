"""
Generates a beautifully styled Word Document (.docx) guide for demonstrating
ResolveAI to a college professor / teacher during project evaluation & viva.
"""

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from pathlib import Path


def set_cell_background(cell, fill_hex):
    """Set background color of a table cell."""
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set cell padding in twips (1/20th of a pt)."""
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for margin_name, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{margin_name}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def add_callout(doc, text, title="KEY TALKING POINT FOR TEACHER", color_hex="0074CC", bg_hex="EBF4FB"):
    """Adds a callout box with a colored left border and light background."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, bg_hex)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)

    # Set left border
    tcPr = cell._element.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'  <w:left w:val="single" w:sz="36" w:space="0" w:color="{color_hex}"/>'
        f'  <w:top w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'  <w:bottom w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    run_title = p.add_run(f"★ {title}\n")
    run_title.font.name = "Arial"
    run_title.font.size = Pt(10)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(0, 89, 153)

    run_text = p.add_run(text)
    run_text.font.name = "Arial"
    run_text.font.size = Pt(10.5)
    run_text.font.color.rgb = RGBColor(40, 45, 50)
    doc.add_paragraph().paragraph_format.space_after = Pt(6)


def create_demo_document():
    doc = docx.Document()

    # Page setup
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Palette
    ORANGE = RGBColor(244, 130, 37)      # #F48225 (Stack Overflow Orange)
    BLUE = RGBColor(10, 149, 255)        # #0A95FF
    DARK_BLUE = RGBColor(0, 89, 153)
    GREEN = RGBColor(46, 125, 50)
    TEXT_DARK = RGBColor(35, 38, 41)
    GRAY = RGBColor(106, 115, 124)

    # ── TITLE & SUBTITLE ─────────────────────────────────────────────
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(2)
    run_t = title_p.add_run("ResolveAI — Teacher Demo & Presentation Guide")
    run_t.font.name = "Arial"
    run_t.font.size = Pt(22)
    run_t.font.bold = True
    run_t.font.color.rgb = ORANGE

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(16)
    run_sub = sub_p.add_run("Simple, Layman-Language Walkthrough, Live Demo Script & Viva Cheat Sheet")
    run_sub.font.name = "Arial"
    run_sub.font.size = Pt(12)
    run_sub.font.italic = True
    run_sub.font.color.rgb = GRAY

    # ── SECTION 1: THE 30-SECOND ELEVATOR PITCH ──────────────────────
    h1 = doc.add_heading(level=1)
    r1 = h1.add_run("1. The 30-Second Elevator Pitch (What to Say First)")
    r1.font.name = "Arial"
    r1.font.color.rgb = DARK_BLUE

    p = doc.add_paragraph()
    p.add_run("When your teacher says: ")
    run_quote = p.add_run("\"So, what is your project about and what problem does it solve?\"\n")
    run_quote.font.bold = True

    add_callout(
        doc,
        "\"Good morning Sir/Ma'am. Our project is ResolveAI — an Explainable Technical Troubleshooting Assistant.\n\n"
        "Whenever developers or students get command-line errors in Python, pip, virtual environments, or Git, "
        "normal tools like ChatGPT often guess, hallucinate wrong flags, or give dangerous commands without proof.\n\n"
        "ResolveAI solves this by combining three brains:\n"
        "1. RAG (The Official Rulebook) — It pulls exact paragraphs from official documentation manuals.\n"
        "2. CBR (The Senior Developer's Memory) — It searches a database of real, previously solved tickets to see how humans fixed it before.\n"
        "3. Gemini 3.8 Flash (The Explainer) — It takes the manual + the past fix, and writes out a safe, 4-step checklist with exact commands and proof citations.\n\n"
        "Plus, whenever a developer clicks 'Yes, Resolved', our system remembers that fix and learns for future students!\"",
        title="EXACT WORDS TO SAY TO YOUR TEACHER",
        color_hex="F48225",
        bg_hex="FFF8F2"
    )

    # ── SECTION 2: SIMPLE ANALOGY ────────────────────────────────────
    h2 = doc.add_heading(level=1)
    r2 = h2.add_run("2. The Car Mechanic Analogy (If Your Teacher Wants it Simpler)")
    r2.font.name = "Arial"
    r2.font.color.rgb = DARK_BLUE

    p = doc.add_paragraph()
    p.add_run("If the teacher asks: ")
    p.add_run("\"Why both RAG and CBR? Isn't RAG enough?\"\n").font.bold = True
    p.add_run("Use this simple real-world comparison:\n")

    tbl = doc.add_table(rows=4, cols=3)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Component", "Real-World Analogy", "What It Does In ResolveAI"]
    for i, h in enumerate(headers):
        cell = tbl.cell(0, i)
        set_cell_background(cell, "0074CC")
        set_cell_margins(cell, 80, 80, 100, 100)
        run = cell.paragraphs[0].add_run(h)
        run.font.name = "Arial"
        run.font.bold = True
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(255, 255, 255)

    rows_data = [
        ("RAG (Manuals)", "The Official Workshop Manual", "Gives the official theoretical rules and flags (e.g. how pip works)."),
        ("CBR (Casebase)", "The Senior Mechanic's Memory", "Remembers: 'Oh, 2 weeks ago a Windows laptop had this exact permission bug, and running in a venv fixed it!'"),
        ("Gemini 3.8 Flash", "The Helpful Mechanic", "Explains the combined answer to the customer in simple, step-by-step instructions with no technical confusion.")
    ]
    for row_idx, data in enumerate(rows_data, 1):
        bg = "F8F9FA" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, text in enumerate(data):
            cell = tbl.cell(row_idx, col_idx)
            set_cell_background(cell, bg)
            set_cell_margins(cell, 80, 80, 100, 100)
            run = cell.paragraphs[0].add_run(text)
            run.font.name = "Arial"
            run.font.size = Pt(9.5)
            run.font.color.rgb = TEXT_DARK

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # ── SECTION 3: STEP-BY-STEP LIVE DEMO GUIDE ──────────────────────
    h3 = doc.add_heading(level=1)
    r3 = h3.add_run("3. The 3-Minute Live Demo (What to Click & Show on Screen)")
    r3.font.name = "Arial"
    r3.font.color.rgb = DARK_BLUE

    steps = [
        ("Step 1: Open the Frontend", 
         "Open your browser to http://localhost:5173.\n"
         "Say: 'Sir/Ma'am, we modeled our interface after Stack Overflow because it's the gold-standard troubleshooting UI every developer recognizes. Notice the clean top bar, left navigation sidebar, and search bar.'"),
        
        ("Step 2: Show the 'Ask a Question' Form",
         "Show the form fields on the home page.\n"
         "Say: 'A developer doesn't just type a vague prompt. They enter their Problem Title, Environment (Tool & OS), and raw Terminal Error Traceback.'"),
         
        ("Step 3: Click 'Load Example Issue'",
         "Click the white 'Load Example Issue' button next to the blue button.\n"
         "This automatically populates a real error: pip install fails with Permission denied on Windows.\n"
         "Say: 'Notice how the tool is set to pip, the OS to Windows, and the error code contains PermissionError [Errno 13].'"),

        ("Step 4: Point out the AI Engine Controls",
         "Point to the 'Troubleshooting Engine & Model' box.\n"
         "Say: 'We have Google Gemini 3.8 Flash active in cloud mode, or we can switch to local offline Ollama. We also have full ablation modes (Hybrid, RAG only, CBR only, LLM baseline) for academic testing.'"),

        ("Step 5: Click 'Post Your Question / Get Resolution'",
         "Click the blue button. In 2-3 seconds, the Resolution page opens.\n"
         "Say: 'Now look at what happened in under 3 seconds:'"),

        ("Step 6: Show the 5 Key Elements on the Result Page",
         "Point to each on screen:\n"
         "1. Green Checkmark (Accepted Solution) — Shows high confidence diagnosis.\n"
         "2. Numbered Steps with Copy Buttons — Clear commands (e.g. python -m venv myenv).\n"
         "3. Documentation Citations — Click to expand. Show the teacher: 'Look, here are the exact official pip user guide paragraphs we retrieved with RAG.'\n"
         "4. Right Sidebar (Similar Solved Cases) — Show: 'Here is CBR in action! It matched 3 previous solved tickets from our database with an 85% match score.'\n"
         "5. Voting & Feedback — Click 'Yes, Resolved'. Explain: 'This triggers our continuous learning loop. The verified fix gets saved back into SQLite so future queries match it instantly!'"),

        ("Step 7: Click 'Questions / Cases' in Left Sidebar",
         "Click 'Questions / Cases' (shows count 50+).\n"
         "Say: 'Here is our full CBR casebase. We have over 50 real-world verified cases covering Python, pip, virtual environments, Git merge conflicts, Docker, and Linux.'"),

        ("Step 8: Click 'Admin & Metrics'",
         "Click 'Admin & Metrics' in the left sidebar.\n"
         "Say: 'Here is our Admin dashboard. It shows our live system health, 179 indexed documentation chunks in ChromaDB, the 4 CBR similarity weight sliders, and our live Gemini test latency.'")
    ]

    for title, desc in steps:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        run_st = p.add_run(f"▶ {title}\n")
        run_st.font.name = "Arial"
        run_st.font.size = Pt(11)
        run_st.font.bold = True
        run_st.font.color.rgb = ORANGE

        run_sd = p.add_run(desc)
        run_sd.font.name = "Arial"
        run_sd.font.size = Pt(10)
        run_sd.font.color.rgb = TEXT_DARK

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # ── SECTION 4: TEACHER QUESTIONS & SIMPLE ANSWERS ────────────────
    h4 = doc.add_heading(level=1)
    r4 = h4.add_run("4. Viva & Teacher Questions (Simple Cheat Sheet)")
    r4.font.name = "Arial"
    r4.font.color.rgb = DARK_BLUE

    faqs = [
        ("Q1: What is the main research paper behind this project?",
         "Answer: \"Sir, our project is based on the research paper 'CBR-RAG: Case-Based Reasoning for Retrieval Augmented Generation in LLMs for Legal Question Answering' (ArXiv: 2404.04302). While the paper applied it to law, we adapted it to computer science technical troubleshooting where tickets naturally form cases.\""),

        ("Q2: What is Case-Based Reasoning (CBR)?",
         "Answer: \"CBR is a classic AI paradigm that solves new problems by finding similar past solved problems. It follows 4 steps: Retrieve old cases, Reuse their solutions, Revise the result with human feedback, and Retain verified new fixes into memory.\""),

        ("Q3: How do you calculate similarity between cases? Is it just vector search?",
         "Answer: \"No Sir, pure vector search ignores specific error codes and operating systems. We use a transparent 4-part weighted formula:\n"
         "• 40% Problem Semantic Similarity (Cosine on BGE embeddings)\n"
         "• 25% Error Log Similarity (Cosine)\n"
         "• 20% Entity & Error-code Overlap (Jaccard token similarity)\n"
         "• 15% Environment & Tool Match (Exact match for Windows/Linux/Mac)\n"
         "Every single component score is visible and inspectable!\""),

        ("Q4: Where are the files stored? Did you use expensive cloud databases?",
         "Answer: \"No Sir, ResolveAI has zero cloud database cost. We use local persistent SQLite with FTS5 full-text search for cases and BM25, and local ChromaDB for dense vector storage.\""),

        ("Q5: What LLM are you using?",
         "Answer: \"We use a dual architecture: in production we connect to Google's latest Gemini 3.8 Flash via API for sub-second responses, but the code also includes a 100% local offline provider using Ollama running Qwen3 4B for offline lab demonstrations.\""),

        ("Q6: What is your novel contribution compared to the research paper?",
         "Answer: \"The research paper only did Retrieve and a loose Reuse step. They had no human revision and no retention loop. ResolveAI completes the full 4R loop by adding human-in-the-loop verified feedback with duplicate detection (cosine < 0.85), so our casebase actively grows over time.\"")
    ]

    for q, a in faqs:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(2)
        rq = p.add_run(f"❓ {q}\n")
        rq.font.name = "Arial"
        rq.font.size = Pt(11)
        rq.font.bold = True
        rq.font.color.rgb = DARK_BLUE

        ra = p.add_run(a)
        ra.font.name = "Arial"
        ra.font.size = Pt(10)
        ra.font.color.rgb = TEXT_DARK

    # ── FOOTER NOTE ──────────────────────────────────────────────────
    doc.add_paragraph().paragraph_format.space_after = Pt(12)
    p_footer = doc.add_paragraph()
    p_footer.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rf = p_footer.add_run("ResolveAI Major Project • GitHub: https://github.com/inferno571/resolveai • Good Luck on Your Demo!")
    rf.font.name = "Arial"
    rf.font.size = Pt(9)
    rf.font.italic = True
    rf.font.color.rgb = GRAY

    # Save to root folder
    out_path = Path(__file__).parent.parent.parent / "ResolveAI_Teacher_Demo_Guide.docx"
    doc.save(str(out_path))
    print(f"Document successfully created at: {out_path}")


if __name__ == "__main__":
    create_demo_document()
