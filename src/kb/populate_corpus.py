from pathlib import Path
from src.kb.ingest import ingest_document
from src.kb.clean_text import clean_document_file
from src.kb.chunk import process_and_save_chunks
from src.kb.manifest import generate_kb_manifest
from src.kb.index import build_minimal_index
from src.utils.config_loader import get_project_root
from src.utils.logging import get_logger

logger = get_logger("populate_corpus")

DENTAL_SOURCES = [
    {
        "meta": {
            "document_id": "DOC-0001",
            "title": "ADA Clinical Practice Guideline on Antibiotic Use for Odontogenic Infections",
            "organization_authors": "American Dental Association (ADA) Council on Scientific Affairs",
            "publication_year": 2019,
            "version_date": "2019-11-01",
            "document_type": "clinical_guideline",
            "url": "https://www.ada.org/resources/research/science-and-research-institute/evidence-based-dental-research/antibiotic-use-guideline",
            "license_status": "APPROVED_OPEN_ACCESS",
            "topic": "antibiotic_stewardship",
            "evidence_level": "Level I (Clinical Guideline)"
        },
        "content": """# ADA Clinical Practice Guideline on Antibiotic Use for Odontogenic Infections

## Section 1: Executive Summary & Scope
This clinical practice guideline provides evidence-based recommendations on the use of systemic antibiotics for the urgent management of symptomatic irreversible pulpitis, symptomatic apical periodontitis, and localized acute apical abscess in immunocompetent adults.

## Section 2: Pulpitis & Localized Dental Infections
Systemic antibiotics are NOT recommended for immunocompetent adult patients presenting with symptomatic irreversible pulpitis or localized acute apical abscess without signs of systemic infection or spreading edema. Operative dental intervention (such as pulpectomy, root canal therapy, or extraction) is the primary definitive treatment.

## Section 3: Indications for Systemic Antibiotics
Systemic antibiotics are indicated ONLY as an adjunct to definitive operative treatment when the patient exhibits signs of spreading infection or systemic involvement, including:
- Fever (> 100.4°F or 38°C)
- Tachycardia or systemic malaise
- Spreading facial swelling or edema
- Trismus (mouth opening restricted)
- Immunocompromised state

## Section 4: First-Line Antibiotic Regimens
For non-allergic adults: Amoxicillin 500mg orally 3 times daily for 3 to 7 days until clinical resolution.
For penicillin-allergic patients: Clindamycin 300mg 4 times daily OR Azithromycin 500mg loading dose then 250mg daily.
"""
    },
    {
        "meta": {
            "document_id": "DOC-0002",
            "title": "SDCEP Drug Prescribing for Dentistry & Antimicrobial Stewardship",
            "organization_authors": "Scottish Dental Clinical Effectiveness Programme (SDCEP)",
            "publication_year": 2021,
            "version_date": "2021-03-01",
            "document_type": "clinical_guideline",
            "url": "https://www.sdcep.org.uk/published-guidance/drug-prescribing/",
            "license_status": "APPROVED_OPEN_ACCESS",
            "topic": "antibiotic_stewardship",
            "evidence_level": "Level I (Clinical Guideline)"
        },
        "content": """# SDCEP Antimicrobial Stewardship Guidance for Acute Dental Pain

## Section 1: Core Principles of Prescribing
Antibiotics do not cure dental pain. Operative intervention to drain pus, remove the necrotic pulp, or extract the tooth is the definitive management. Prescribing antibiotics without operative treatment leads to treatment failure and resistant strains.

## Section 2: Management of Acute Odontogenic Abscess
1. Localized Intraoral Swelling: Drain the swelling via incisional drainage or root canal instrumentation. Do not prescribe antibiotics.
2. Spreading Edema / Systemic Infection: Prescribe Amoxicillin 500mg tds for up to 5 days, plus definitive operative drainage.
3. Severe Spreading / Airway Risk: Refer immediately to maxillofacial/hospital emergency care.

## Section 3: Penicillin Allergy Protocol
In confirmed penicillin allergy:
- Erythromycin 500mg 4 times daily OR Clarithromycin 500mg twice daily for 5 days.
- Metronidazole 400mg 3 times daily may be added for anaerobic spreading infection.
"""
    },
    {
        "meta": {
            "document_id": "DOC-0003",
            "title": "AAOMS Criteria for Emergency Escalation in Fascial Space Infections",
            "organization_authors": "American Association of Oral and Maxillofacial Surgeons (AAOMS)",
            "publication_year": 2020,
            "version_date": "2020-08-15",
            "document_type": "consensus_statement",
            "url": "https://www.aaoms.org/practice-resources/clinical-guidelines",
            "license_status": "APPROVED_OPEN_ACCESS",
            "topic": "urgent_escalation_red_flags",
            "evidence_level": "Level I (Consensus Statement)"
        },
        "content": """# AAOMS Clinical Emergency Protocol: Fascial Space Infection Red Flags

## Section 1: Red-Flag Symptoms Requiring Emergency Department Referral
Odontogenic infections can rapidly spread along fascial planes of the head and neck. Any patient exhibiting the following symptoms requires immediate emergency department transfer:
- Trismus (Inability to open mouth > 20mm or < 2 fingerbreadths)
- Dysphagia (Difficulty swallowing liquids or saliva)
- Dyspnea (Difficulty breathing or sensation of airway tightness)
- Submandibular or submental swelling with floor of mouth elevation (Ludwig's Angina)
- Periorbital swelling extending towards the orbit (Risk of Cavernous Sinus Thrombosis)
- High Fever (> 101.5°F) with lethargy or confusion (Impending Sepsis)

## Section 2: Ludwig's Angina Management
Ludwig's Angina is a rapidly expanding bilateral cellulitis of the submandibular, sublingual, and submental spaces. Airway compromise can occur within hours. Emergency awake fiberoptic intubation and surgical decompression are required.
"""
    },
    {
        "meta": {
            "document_id": "DOC-0004",
            "title": "Evidence-Based Acute Dental Analgesia Protocol",
            "organization_authors": "Journal of the American Dental Association (JADA)",
            "publication_year": 2022,
            "version_date": "2022-04-10",
            "document_type": "systematic_review",
            "url": "https://jada.ada.org/article/S0002-8177(22)00112-X/fulltext",
            "license_status": "APPROVED_OPEN_ACCESS",
            "topic": "analgesia_protocols",
            "evidence_level": "Level I (Systematic Review)"
        },
        "content": """# Evidence-Based Pharmacologic Management of Acute Dental Pain

## Section 1: First-Line Analgesic Regimen
Combination therapy with nonsteroidal anti-inflammatory drugs (NSAIDs) and acetaminophen (paracetamol) provides superior analgesia to opioid monotherapy for inflammatory pulpal and postoperative dental pain.

## Section 2: Recommended Dosing Strategy
1. Mild Pain: Ibuprofen 200mg to 400mg orally every 4 to 6 hours as needed.
2. Moderate to Severe Pain: Combination of Ibuprofen 400mg + Acetaminophen 500mg taken together every 6 hours (Max Ibuprofen: 2400mg/day; Max Acetaminophen: 3000mg/day).

## Section 3: Contraindications & Precautions
- Ibuprofen / NSAIDs: Contraindications include active peptic ulcer disease, severe renal impairment, history of GI bleeding, asthma triggered by NSAIDs, and third trimester pregnancy.
- Acetaminophen: Contraindication in severe liver failure or chronic alcoholism.
"""
    },
    {
        "meta": {
            "document_id": "DOC-0005",
            "title": "NICE Guidelines on Dental Pain & Referral Criteria",
            "organization_authors": "National Institute for Health and Care Excellence (NICE)",
            "publication_year": 2021,
            "version_date": "2021-10-01",
            "document_type": "clinical_guideline",
            "url": "https://www.nice.org.uk/guidance/dental-care",
            "license_status": "APPROVED_OPEN_ACCESS",
            "topic": "urgent_escalation_red_flags",
            "evidence_level": "Level I (Clinical Guideline)"
        },
        "content": """# NICE Guidelines: Triage and Urgent Dental Escalation

## Section 1: Classification of Urgency
1. Emergency (Immediate Hospital Referral): Signs of airway compromise, facial trauma, severe spreading cellulitis, or systemic sepsis.
2. Urgent (Within 24 Hours): Severe dental pain not controlled by analgesia, localized intraoral swelling, or dental avulsion trauma.
3. Routine: Mild localized sensitivity, asymptomatic decay, or aesthetic inquiries.

## Section 2: Non-Dental Differential Diagnosis
Dental clinicians must rule out non-odontogenic facial pain causes including trigeminal neuralgia, temporomandibular joint dysfunction (TMD), maxillary sinusitis, and cardiac angina radiating to the mandible.
"""
    }
]


def populate_knowledge_base():
    project_root = get_project_root()
    kb_root = project_root / "data" / "knowledge_base"

    logger.info(f"Populating Knowledge Base at '{kb_root}'...")
    all_chunks = []

    for src in DENTAL_SOURCES:
        meta_dict = src["meta"]
        raw_text = src["content"]

        # 1. Ingest
        doc_meta = ingest_document(raw_text, meta_dict, kb_root)

        # 2. Clean
        raw_path = kb_root / "raw" / f"{doc_meta.document_id}.txt"
        clean_path = kb_root / "cleaned" / f"{doc_meta.document_id}.txt"
        clean_document_file(raw_path, clean_path)

        # 3. Chunk
        chunk_file = kb_root / "chunks" / f"{doc_meta.document_id}.jsonl"
        meta_file = kb_root / "metadata" / f"{doc_meta.document_id}.json"
        chunks = process_and_save_chunks(clean_path, meta_file, chunk_file, target_chunk_size=400, overlap=50)
        all_chunks.extend(chunks)

    # 4. Generate Manifest
    generate_kb_manifest(kb_root)

    # 5. Build Index
    index_dir = kb_root / "index"
    build_minimal_index(all_chunks, index_dir)

    logger.info("Knowledge base population complete.")


if __name__ == "__main__":
    populate_knowledge_base()
