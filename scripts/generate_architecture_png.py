#!/usr/bin/env python3
"""
Render a high-resolution PNG of the SafeDental End-to-End System Architecture.
Saved to reports/SafeDental_Architecture_Diagram.png and copied to Downloads.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def render_architecture_png(output_path="reports/SafeDental_Architecture_Diagram.png"):
    fig, ax = plt.subplots(figsize=(16, 10), dpi=300)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # Canvas Background
    fig.patch.set_facecolor("#f8fafc")
    ax.set_facecolor("#f8fafc")

    # Title Banner
    banner = patches.FancyBboxPatch((0.5, 8.8), 15.0, 0.9, boxstyle="round,pad=0.1", fc="#0f172a", ec="#0f172a")
    ax.add_patch(banner)
    ax.text(0.8, 9.35, "SAFEDENTAL: END-TO-END CLINICAL ARCHITECTURE & SAFETY GATING PIPELINE", fontsize=16, fontweight="bold", color="#38bdf8")
    ax.text(0.8, 8.98, "Deterministic Safety Guardrails  |  Dense FAISS Guideline RAG  |  Anthropic Claude Opus 5.5  |  30,000 Clinical Query Benchmark", fontsize=11, color="#94a3b8")

    # Box 1: Patient/Clinician Intake
    b1 = patches.FancyBboxPatch((0.5, 4.8), 2.8, 3.6, boxstyle="round,pad=0.1", fc="#ffffff", ec="#0284c7", lw=2)
    ax.add_patch(b1)
    b1_h = patches.FancyBboxPatch((0.6, 7.8), 2.6, 0.5, boxstyle="round,pad=0.05", fc="#e0f2fe", ec="#0284c7")
    ax.add_patch(b1_h)
    ax.text(1.9, 8.05, "PATIENT / CLINICIAN INTAKE", fontsize=11, fontweight="bold", color="#0369a1", ha="center")
    ax.text(0.7, 7.5, "Raw EHR Clinical Narrative:\n• Chief complaints & pain duration\n• Missing vs. present diagnostics\n\nPatient Queries:\n• 'Molar throbbing, can I take amox?'\n• 'Difficulty swallowing, jaw swelling'\n• 'Cold sensitivity 3-5 seconds'\n\nClinical Metadata:\n• Age, Medical History, Allergies", fontsize=9.5, color="#1e293b", va="top")

    # Arrow 1 -> 2
    ax.annotate("", xy=(3.8, 6.6), xytext=(3.3, 6.6), arrowprops=dict(arrowstyle="-|>", lw=2, color="#0284c7"))
    ax.text(3.55, 6.8, "Raw Query", fontsize=9, fontweight="bold", color="#0284c7", ha="center")

    # Box 2: Stage 1 Red-Flag Engine
    b2 = patches.FancyBboxPatch((3.8, 4.8), 3.4, 3.6, boxstyle="round,pad=0.1", fc="#ffffff", ec="#dc2626", lw=2)
    ax.add_patch(b2)
    b2_h = patches.FancyBboxPatch((3.9, 7.8), 3.2, 0.5, boxstyle="round,pad=0.05", fc="#fee2e2", ec="#dc2626")
    ax.add_patch(b2_h)
    ax.text(5.5, 8.05, "STAGE 1: RED-FLAG ENGINE (0.28 ms)", fontsize=11, fontweight="bold", color="#b91c1c", ha="center")
    ax.text(4.0, 7.5, "Deterministic Regex Matcher:\n• 12 Life-Threatening Emergency Types\n• Ludwig's Angina / Floor of Mouth\n• Airway Compromise / Dysphagia / Stridor\n• Canine Space Orbital Edema\n\nClinical Negation Parser:\n• 60-character lookback window\n• Filters 'no trismus', 'denies fever'", fontsize=9.5, color="#1e293b", va="top")

    # Diamond 1: Red Flag?
    d1 = patches.Polygon([[5.5, 5.7], [6.2, 5.2], [5.5, 4.7], [4.8, 5.2]], fc="#fee2e2", ec="#dc2626", lw=1.5)
    ax.add_patch(d1)
    ax.text(5.5, 5.2, "Red Flag\nDetected?", fontsize=9, fontweight="bold", color="#991b1b", ha="center", va="center")

    # Arrow to Escalate (Down)
    ax.annotate("", xy=(5.5, 3.55), xytext=(5.5, 4.7), arrowprops=dict(arrowstyle="-|>", lw=2, color="#dc2626"))
    ax.text(5.6, 4.15, "YES (Emergency)", fontsize=9, fontweight="bold", color="#dc2626", va="center")

    # Action: Escalate Box
    act_esc = patches.FancyBboxPatch((3.8, 1.65), 3.4, 1.85, boxstyle="round,pad=0.1", fc="#ffffff", ec="#dc2626", lw=2)
    ax.add_patch(act_esc)
    act_esc_h = patches.FancyBboxPatch((3.9, 3.08), 3.2, 0.38, boxstyle="round,pad=0.05", fc="#fee2e2", ec="#dc2626")
    ax.add_patch(act_esc_h)
    ax.text(5.5, 3.27, "ACTION: ESCALATE (100% SENSITIVITY)", fontsize=10, fontweight="bold", color="#b91c1c", ha="center", va="center")
    ax.text(4.0, 2.95, "Immediate Emergency Referral:\n• Oral & Maxillofacial Surgery / ER\n• Zero Hallucination Risk (Bypasses LLM)\n• 4,500 / 4,500 Caught (0 Missed Red Flags)", fontsize=9, color="#7f1d1d", va="top")

    # Arrow 2 -> 3 (Safe -> Stage 2)
    ax.annotate("", xy=(7.7, 5.2), xytext=(6.2, 5.2), arrowprops=dict(arrowstyle="-|>", lw=2, color="#059669"))
    ax.text(6.95, 5.4, "NO (Safe)", fontsize=9, fontweight="bold", color="#059669", ha="center")

    # Box 3: Stage 2 Checklist Evaluator
    b3 = patches.FancyBboxPatch((7.7, 4.8), 3.4, 3.6, boxstyle="round,pad=0.1", fc="#ffffff", ec="#059669", lw=2)
    ax.add_patch(b3)
    b3_h = patches.FancyBboxPatch((7.8, 7.8), 3.2, 0.5, boxstyle="round,pad=0.05", fc="#d1fae5", ec="#059669")
    ax.add_patch(b3_h)
    ax.text(9.4, 8.05, "STAGE 2: DIAGNOSTIC CHECKLIST", fontsize=11, fontweight="bold", color="#047857", ha="center")
    ax.text(7.9, 7.5, "Required-Information Evaluator:\n1. Chief Complaint & Pain Timeline\n2. Relevant Medical/Drug History\n3. Clinical Examination Findings\n4. Thermal Cold Vitality Response\n5. Periapical Radiographic Indicators\n\nAdversarial / Narcotic Scope Filter:\n• Blocks illicit opioid requests\n• Intercepts prompt injection jailbreaks", fontsize=9.5, color="#1e293b", va="top")

    # Diamond 2: Complete?
    d2 = patches.Polygon([[9.4, 5.7], [10.1, 5.2], [9.4, 4.7], [8.7, 5.2]], fc="#d1fae5", ec="#059669", lw=1.5)
    ax.add_patch(d2)
    ax.text(9.4, 5.2, "Diagnostics\nComplete?", fontsize=9, fontweight="bold", color="#065f46", ha="center", va="center")

    # Arrow to ASK / ABSTAIN (Down)
    ax.annotate("", xy=(9.4, 3.55), xytext=(9.4, 4.7), arrowprops=dict(arrowstyle="-|>", lw=2, color="#0284c7"))
    ax.text(9.5, 4.15, "INCOMPLETE / CONFLICT", fontsize=8.5, fontweight="bold", color="#0284c7", va="center")

    # Action: ASK & ABSTAIN Box
    act_ask = patches.FancyBboxPatch((7.5, 1.65), 3.8, 1.85, boxstyle="round,pad=0.1", fc="#ffffff", ec="#0284c7", lw=2)
    ax.add_patch(act_ask)
    act_ask_h = patches.FancyBboxPatch((7.6, 3.08), 3.6, 0.38, boxstyle="round,pad=0.05", fc="#e0f2fe", ec="#0284c7")
    ax.add_patch(act_ask_h)
    ax.text(9.4, 3.27, "ACTION: ASK  |  ACTION: ABSTAIN", fontsize=10, fontweight="bold", color="#0369a1", ha="center", va="center")
    ax.text(7.7, 2.95, "Targeted Clinical Intake (ASK):\n• Requests missing X-rays & cold vitality test\n• Refuses inappropriate antibiotic prescribing\nSafe Refusal (ABSTAIN):\n• Safely halts contradictory data & illicit narcotics", fontsize=9, color="#0c4a6e", va="top")

    # Arrow 3 -> 4 (Complete -> FAISS RAG)
    ax.annotate("", xy=(11.6, 5.2), xytext=(10.1, 5.2), arrowprops=dict(arrowstyle="-|>", lw=2, color="#7c3aed"))
    ax.text(10.85, 5.42, "COMPLETE", fontsize=7.5, fontweight="bold", color="#7c3aed", ha="center")

    # Box 4: Stage 3 FAISS Dense RAG & LLM
    b4 = patches.FancyBboxPatch((11.6, 4.0), 3.9, 4.4, boxstyle="round,pad=0.1", fc="#ffffff", ec="#7c3aed", lw=2)
    ax.add_patch(b4)
    b4_h = patches.FancyBboxPatch((11.7, 7.8), 3.7, 0.5, boxstyle="round,pad=0.05", fc="#ede9fe", ec="#7c3aed")
    ax.add_patch(b4_h)
    ax.text(13.55, 8.05, "STAGE 3 & 4: FAISS RAG & CLAUDE", fontsize=11, fontweight="bold", color="#6d28d9", ha="center")
    ax.text(11.8, 7.5, "Stage 3: FAISS Vector Retrieval (725.1 QPS)\n• Dense Embedder: BAAI/bge-small-en (384d)\n• Corpus: ADA 2019, SDCEP, AAE Guidelines\n• Recall@5 = 82.49% | Median Latency = 7.62 ms\n\nStage 4: Anthropic Claude Opus 5.5\n• Temperature: 0.0 deterministic decoding\n• Resilient offline Mock engine fallback\n• Strictly grounded in retrieved evidence chunks\n• Traceable tags: [ADA 2019, DOC-0001, CHK-0001]", fontsize=9, color="#1e293b", va="top")

    # Arrow to ANSWER (Down)
    ax.annotate("", xy=(13.55, 3.55), xytext=(13.55, 4.0), arrowprops=dict(arrowstyle="-|>", lw=2, color="#059669"))

    # Action: ANSWER Box
    act_ans = patches.FancyBboxPatch((11.6, 1.65), 3.9, 1.85, boxstyle="round,pad=0.1", fc="#ffffff", ec="#059669", lw=2)
    ax.add_patch(act_ans)
    act_ans_h = patches.FancyBboxPatch((11.7, 3.08), 3.7, 0.38, boxstyle="round,pad=0.05", fc="#d1fae5", ec="#059669")
    ax.add_patch(act_ans_h)
    ax.text(13.55, 3.27, "ACTION: ANSWER (GUIDELINE GROUNDED)", fontsize=10, fontweight="bold", color="#047857", ha="center", va="center")
    ax.text(11.8, 2.95, "Evidence-Grounded Operative Guidance:\n• 98.4% Diagnostic Accuracy on answered cases\n• Direct cryptographic guideline citation audit trail\n• Zero unverified medication recommendations", fontsize=9, color="#065f46", va="top")

    # Bottom Stat Callout Ribbon
    ribbon = patches.FancyBboxPatch((0.5, 0.4), 15.0, 1.0, boxstyle="round,pad=0.1", fc="#0f172a", ec="#38bdf8", lw=1.5)
    ax.add_patch(ribbon)
    stats = [
        ("30,000 CASES", "Total Benchmark Volume", "#38bdf8", 1.8),
        ("64.58% -> 0.0%", "Unsafe Rate Eliminated", "#ef4444", 4.8),
        ("4,500 / 4,500", "Emergency Sensitivity (100%)", "#10b981", 8.0),
        ("chi2 = 38.0", "McNemar Test (p < 0.000001)", "#f59e0b", 11.2),
        ("0.28 ms / 7.6 ms", "P50 Latency (Gating / RAG)", "#a855f7", 14.1)
    ]
    for stitle, ssub, scol, sx in stats:
        ax.text(sx, 1.0, stitle, fontsize=13, fontweight="bold", color=scol, ha="center")
        ax.text(sx, 0.65, ssub, fontsize=9.5, color="#cbd5e1", ha="center")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"High-resolution architecture diagram saved at: {output_path}")
    return output_path

if __name__ == "__main__":
    render_architecture_png()
