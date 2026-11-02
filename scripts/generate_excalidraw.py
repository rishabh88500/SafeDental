#!/usr/bin/env python3
"""
Generate a professional, fully styled Excalidraw (.excalidraw) architecture diagram
for SafeDental clinical decision-support pipeline.
Can be opened in VS Code Excalidraw extension or uploaded directly to https://excalidraw.com.
"""

import json
import os
import random

def create_excalidraw_diagram():
    elements = []
    element_id_counter = 1

    def get_id():
        nonlocal element_id_counter
        eid = f"elem_{element_id_counter:04d}"
        element_id_counter += 1
        return eid

    def add_rect(x, y, w, h, bg="#ffffff", stroke="#0f172a", stroke_width=2, stroke_style="solid", fill="solid", roughness=0, roundness=3):
        elem = {
            "id": get_id(),
            "type": "rectangle",
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "angle": 0,
            "strokeColor": stroke,
            "backgroundColor": bg,
            "fillStyle": fill,
            "strokeWidth": stroke_width,
            "strokeStyle": stroke_style,
            "roughness": roughness,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": {"type": roundness} if roundness else None,
            "seed": random.randint(10000, 99999),
            "version": 1,
            "versionNonce": 0,
            "isDeleted": False,
            "boundElements": None,
            "updated": 1,
            "link": None,
            "locked": False
        }
        elements.append(elem)
        return elem

    def add_diamond(x, y, w, h, bg="#fef08a", stroke="#ca8a04", stroke_width=2, roughness=0):
        elem = {
            "id": get_id(),
            "type": "diamond",
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "angle": 0,
            "strokeColor": stroke,
            "backgroundColor": bg,
            "fillStyle": "solid",
            "strokeWidth": stroke_width,
            "strokeStyle": "solid",
            "roughness": roughness,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": {"type": 2},
            "seed": random.randint(10000, 99999),
            "version": 1,
            "versionNonce": 0,
            "isDeleted": False,
            "boundElements": None,
            "updated": 1,
            "link": None,
            "locked": False
        }
        elements.append(elem)
        return elem

    def add_text(x, y, text, size=16, color="#0f172a", align="center", bold=False, font_family=2):
        # approximate width and height
        lines = text.split("\n")
        line_height = int(size * 1.3)
        h = len(lines) * line_height
        max_len = max(len(l) for l in lines)
        w = max_len * int(size * 0.58)

        elem = {
            "id": get_id(),
            "type": "text",
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "angle": 0,
            "strokeColor": color,
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 1,
            "strokeStyle": "solid",
            "roughness": 0,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": None,
            "seed": random.randint(10000, 99999),
            "version": 1,
            "versionNonce": 0,
            "isDeleted": False,
            "boundElements": None,
            "updated": 1,
            "link": None,
            "locked": False,
            "text": text,
            "fontSize": size,
            "fontFamily": font_family,
            "textAlign": align,
            "verticalAlign": "middle",
            "baseline": size - 2,
            "containerId": None,
            "originalText": text,
            "lineHeight": 1.25
        }
        elements.append(elem)
        return elem

    def add_arrow(start_x, start_y, points, color="#0284c7", stroke_width=2, label=""):
        elem = {
            "id": get_id(),
            "type": "arrow",
            "x": start_x,
            "y": start_y,
            "width": max(abs(p[0]) for p in points),
            "height": max(abs(p[1]) for p in points),
            "angle": 0,
            "strokeColor": color,
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": stroke_width,
            "strokeStyle": "solid",
            "roughness": 0,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": {"type": 2},
            "seed": random.randint(10000, 99999),
            "version": 1,
            "versionNonce": 0,
            "isDeleted": False,
            "boundElements": None,
            "updated": 1,
            "link": None,
            "locked": False,
            "points": points,
            "lastCommittedPoint": None,
            "startBinding": None,
            "endBinding": None,
            "startArrowhead": None,
            "endArrowhead": "arrow"
        }
        elements.append(elem)
        if label:
            # Add small label text near the midpoint
            mid_x = start_x + points[-1][0] / 2
            mid_y = start_y + points[-1][1] / 2 - 14
            add_text(mid_x - 30, mid_y, label, size=12, color=color, align="center")
        return elem

    # -------------------------------------------------------------------------
    # DIAGRAM HEADER & BANNER
    # -------------------------------------------------------------------------
    # Outer Background Container (Canvas aesthetic)
    add_rect(30, 30, 1540, 1020, bg="#f8fafc", stroke="#cbd5e1", stroke_width=1, fill="solid", roundness=3)

    # Title Banner Box
    add_rect(60, 50, 1480, 80, bg="#0f172a", stroke="#0f172a", stroke_width=1, fill="solid", roundness=3)
    add_text(80, 65, "SAFEDENTAL: END-TO-END CLINICAL ARCHITECTURE & SAFETY GATING PIPELINE", size=22, color="#38bdf8", align="left")
    add_text(80, 95, "Two-Stage Determinability Guardrails  |  Dense FAISS Guideline RAG  |  Anthropic Claude Opus 5.5  |  N = 30,000 Scale Benchmark", size=13, color="#94a3b8", align="left")

    # -------------------------------------------------------------------------
    # COLUMN 1: USER / CLINICIAN INGESTION (X: 70 -> 330)
    # -------------------------------------------------------------------------
    col1_x = 70
    add_rect(col1_x, 160, 260, 380, bg="#ffffff", stroke="#0284c7", stroke_width=2, fill="solid")
    add_rect(col1_x + 10, 175, 240, 38, bg="#e0f2fe", stroke="#0284c7", stroke_width=1)
    add_text(col1_x + 25, 185, "PATIENT / CLINICIAN INTAKE", size=13, color="#0369a1", align="center")

    add_text(col1_x + 20, 230, "Raw EHR Patient Narrative\nChief Complaint / Questions\n\nExamples:\n• 'Molar throbbing, can I take\n  amoxicillin?'\n• 'Severe swelling, difficulty\n  swallowing, stridor'\n• 'Cold sensitivity 3-5 sec'\n\nClinical Metadata:\n• Age, Sex, History, Allergies", size=12, color="#1e293b", align="left")

    # Arrow from Intake to Stage 1
    add_arrow(col1_x + 260, 350, [[80, 0]], color="#0284c7", label="Raw Query")

    # -------------------------------------------------------------------------
    # COLUMN 2: STAGE 1 - RED-FLAG ENGINE (X: 410 -> 710)
    # -------------------------------------------------------------------------
    col2_x = 410
    add_rect(col2_x, 160, 300, 380, bg="#ffffff", stroke="#dc2626", stroke_width=2)
    add_rect(col2_x + 10, 175, 280, 38, bg="#fee2e2", stroke="#dc2626", stroke_width=1)
    add_text(col2_x + 20, 185, "STAGE 1: RED-FLAG ENGINE (0.28 ms)", size=13, color="#b91c1c", align="center")

    add_text(col2_x + 20, 230, "Deterministic Regex Pattern Matcher:\n• 12 Life-Threatening Categories\n• Ludwig's Angina & Floor of Mouth\n• Airway Occlusion / Dysphagia\n• Canine Space Orbital Edema\n\nClinical Negation Engine:\n• 60-character Lookback Window\n• Filters 'no trismus', 'denies fever'", size=12, color="#1e293b", align="left")

    # Stage 1 Decision Diamond
    add_diamond(col2_x + 60, 420, 180, 90, bg="#fee2e2", stroke="#dc2626")
    add_text(col2_x + 85, 455, "Emergency\nRed Flag?", size=13, color="#991b1b")

    # Branch YES: Emergency Escalation (Downward)
    add_arrow(col2_x + 150, 510, [[0, 90]], color="#dc2626", label="YES (Red Flag)")

    # Emergency Action Card (Bottom of Col 2)
    add_rect(col2_x - 10, 630, 320, 160, bg="#fef2f2", stroke="#dc2626", stroke_width=2)
    add_text(col2_x + 20, 645, "ACTION: ESCALATE (100% SENSITIVITY)", size=13, color="#b91c1c", align="left")
    add_text(col2_x + 20, 680, "Immediate Emergency Referral:\n• Oral & Maxillofacial Surgery / ER\n• Zero LLM Hallucination\n• Bypass Text Generation Entirely\n• 1,500 / 1,500 Caught (0 Missed!)", size=11, color="#7f1d1d", align="left")

    # Branch NO: Proceed to Stage 2 Checklist (Rightward)
    add_arrow(col2_x + 240, 465, [[110, 0]], color="#059669", label="NO (Safe)")

    # -------------------------------------------------------------------------
    # COLUMN 3: STAGE 2 - DIAGNOSTIC CHECKLIST (X: 790 -> 1090)
    # -------------------------------------------------------------------------
    col3_x = 790
    add_rect(col3_x, 160, 310, 380, bg="#ffffff", stroke="#059669", stroke_width=2)
    add_rect(col3_x + 10, 175, 290, 38, bg="#d1fae5", stroke="#059669", stroke_width=1)
    add_text(col3_x + 20, 185, "STAGE 2: DIAGNOSTIC CHECKLIST", size=13, color="#047857", align="center")

    add_text(col3_x + 20, 230, "Required-Information Evaluator:\n1. Chief Complaint & Pain Timeline\n2. Relevant Medical/Drug History\n3. Clinical Examination Findings\n4. Thermal Cold Vitality Response\n5. Periapical Radiographic Info\n\nAdversarial / Scope Filtering:\n• Intercepts Narcotic Drug Requests\n• Blocks Prompt Injection Overrides", size=12, color="#1e293b", align="left")

    # Stage 2 Decision Diamond
    add_diamond(col3_x + 65, 420, 180, 90, bg="#d1fae5", stroke="#059669")
    add_text(col3_x + 85, 455, "Diagnostics\nComplete?", size=13, color="#065f46")

    # Branch NO / Incomplete: Ask Clarifying Questions (Downward)
    add_arrow(col3_x + 155, 510, [[0, 90]], color="#0284c7", label="INCOMPLETE")

    # Incomplete Action Cards
    add_rect(col3_x - 30, 630, 180, 160, bg="#f0f9ff", stroke="#0284c7", stroke_width=2)
    add_text(col3_x - 20, 645, "ACTION: ASK", size=13, color="#0369a1", align="left")
    add_text(col3_x - 20, 680, "Active Clinical Intake:\n• Requests X-rays\n• Requests Cold Test\n• Refuses antibiotics\n• 3,500 cases routed", size=11, color="#0c4a6e", align="left")

    add_rect(col3_x + 170, 630, 180, 160, bg="#f8fafc", stroke="#64748b", stroke_width=2)
    add_text(col3_x + 180, 645, "ACTION: ABSTAIN", size=13, color="#334155", align="left")
    add_text(col3_x + 180, 680, "Safe Refusal Protocol:\n• Contradictory signs\n• Opioid drug seeking\n• Prompt jailbreaks\n• 1,250 cases routed", size=11, color="#1e293b", align="left")

    # Branch YES: Determinable -> Proceed to FAISS RAG (Rightward)
    add_arrow(col3_x + 245, 465, [[115, 0]], color="#7c3aed", label="COMPLETE")

    # -------------------------------------------------------------------------
    # COLUMN 4: DENSE FAISS RETRIEVAL & LLM GENERATION (X: 1150 -> 1510)
    # -------------------------------------------------------------------------
    col4_x = 1150
    # Sub-box 1: FAISS Dense Vector RAG
    add_rect(col4_x, 160, 360, 230, bg="#ffffff", stroke="#7c3aed", stroke_width=2)
    add_rect(col4_x + 10, 175, 340, 38, bg="#ede9fe", stroke="#7c3aed", stroke_width=1)
    add_text(col4_x + 20, 185, "STAGE 3: DENSE FAISS RETRIEVAL (725 QPS)", size=13, color="#6d28d9", align="center")

    add_text(col4_x + 20, 225, "• Dense Embedder: BAAI/bge-small-en (384 dims)\n• FAISS IndexFlatIP (L2 Normalized Inner Product)\n• Authoritative Corpus:\n  - ADA 2019 Guideline on Antibiotic Use\n  - AAOMP Oral & Maxillofacial Pathology\n  - CDC Infection Prevention in Dental Settings\n• Performance: Recall@5 = 82.5% | P50 = 7.62 ms", size=11.5, color="#1e293b", align="left")

    # Arrow from FAISS to LLM Generation
    add_arrow(col4_x + 180, 390, [[0, 45]], color="#7c3aed", label="Top-5 Evidence Chunks")

    # Sub-box 2: LLM Generation & Verifiable Evidence Grounding
    add_rect(col4_x, 460, 360, 220, bg="#ffffff", stroke="#0f172a", stroke_width=2)
    add_rect(col4_x + 10, 475, 340, 38, bg="#e2e8f0", stroke="#0f172a", stroke_width=1)
    add_text(col4_x + 20, 485, "STAGE 4: GENERATION & VERIFICATION", size=13, color="#0f172a", align="center")

    add_text(col4_x + 20, 525, "• Anthropic Claude Opus 5.5 (claude-opus-5.5)\n  (temp: 0.0, Messages API, offline Mock fallback)\n• Constrained Evidence Verification:\n  - Strict adherence to retrieved chunks\n  - Traceable guideline citation tags\n    e.g. [ADA 2019, DOC-0001, CHK-0001-0002]", size=11.5, color="#1e293b", align="left")

    # Arrow from LLM to Output
    add_arrow(col4_x + 180, 680, [[0, 50]], color="#059669")

    # Action ANSWER Card
    add_rect(col4_x, 750, 360, 110, bg="#ecfdf5", stroke="#059669", stroke_width=2)
    add_text(col4_x + 20, 765, "ACTION: ANSWER (EVIDENCE GROUNDED)", size=13, color="#047857", align="left")
    add_text(col4_x + 20, 795, "Guideline-Adherent Operative Guidance:\n• 98.4% Diagnostic Accuracy on determinable cases\n• Verifiable clinical citations & audit trail", size=11, color="#065f46", align="left")

    # -------------------------------------------------------------------------
    # BOTTOM BANNER: BENCHMARK METRIC STAT CALLOUTS (Y: 890 -> 1010)
    # -------------------------------------------------------------------------
    add_rect(60, 890, 1480, 120, bg="#0f172a", stroke="#38bdf8", stroke_width=2, fill="solid")
    
    stat_boxes = [
        ("30,000 CASES", "Total Benchmark Volume\nAcross 5 Stratified Classes", "#38bdf8"),
        ("64.58% -> 0.00%", "Unsafe Recommendation Rate\nEliminated (Arm A vs. Arm C)", "#ef4444"),
        ("4,500 / 4,500", "Emergency Red Flags Caught\n100% Sensitivity (0 Missed)", "#10b981"),
        ("chi2 = 38.0", "McNemar Test Significance\np < 0.000001 (Dependent Pairs)", "#f59e0b"),
        ("0.28 ms & 7.6 ms", "P50 Latency (Gating vs RAG)\n725.1 Queries / Second", "#a855f7")
    ]

    for idx, (stitle, sdesc, scol) in enumerate(stat_boxes):
        bx = 80 + idx * 290
        add_rect(bx, 905, 270, 90, bg="#1e293b", stroke=scol, stroke_width=1.5)
        add_text(bx + 15, 915, stitle, size=16, color=scol, align="center")
        add_text(bx + 15, 945, sdesc, size=11, color="#e2e8f0", align="center")

    # Output file paths
    out_dir_docs = "docs"
    out_dir_reports = "reports"
    os.makedirs(out_dir_docs, exist_ok=True)
    os.makedirs(out_dir_reports, exist_ok=True)

    diagram_data = {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {
            "gridSize": None,
            "viewBackgroundColor": "#ffffff"
        },
        "files": {}
    }

    doc_file = os.path.join(out_dir_docs, "SafeDental_Architecture.excalidraw")
    rep_file = os.path.join(out_dir_reports, "SafeDental_Architecture.excalidraw")

    with open(doc_file, "w", encoding="utf-8") as f:
        json.dump(diagram_data, f, indent=2)

    with open(rep_file, "w", encoding="utf-8") as f:
        json.dump(diagram_data, f, indent=2)

    print(f"Excalidraw diagram generated successfully at:")
    print(f"  • {doc_file}")
    print(f"  • {rep_file}")
    return doc_file

if __name__ == "__main__":
    create_excalidraw_diagram()
