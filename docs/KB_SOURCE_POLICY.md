# Knowledge Base Source Policy & Governance

## 1. Overview & Purpose
This document establishes the official governance policy for the **SafeDental Evidence Knowledge Base**.

The Knowledge Base provides the clinical evidence corpus used by **Arm C (RAG + Safety)** to ground recommendations on acute dental pain and odontogenic infections.

---

## 2. Source Policy Rules

### 2.1 Scope Restriction
All ingested documents must directly address acute dental conditions within the locked scope:
- Acute pulpal pain and pulpitis management
- Odontogenic infections & fascial space abscesses
- Dental antibiotic stewardship guidelines
- Acute analgesia protocols and contraindications
- Red-flag indicators for urgent referral/escalation

### 2.2 Acceptable Sources
- **Official Clinical Guidelines**: ADA (American Dental Association), SDCEP (Scottish Dental Clinical Effectiveness Programme), NICE (UK), AAOMS (American Association of Oral and Maxillofacial Surgeons).
- **Consensus Statements & Systematic Reviews**: Open-access peer-reviewed literature from PubMed Central (PMC OA subset) or open-access dental journals (CC-BY, CC-BY-NC, or public domain).
- **Government / Institutional Guidance**: CDC, WHO, or UK NHS dental antimicrobial stewardship guidelines.

### 2.3 Unacceptable Sources
- Proprietary textbook chapters protected by standard copyright without text-mining license.
- Non-peer-reviewed blog posts, commercial marketing sites, or patient forum discussions.
- General medical guidelines lacking dental specificity.

### 2.4 Licensing & Status Classification
Every document record must have an explicit `license_status`:
- `APPROVED_OPEN_ACCESS`: CC-BY, CC-BY-SA, CC0, or Public Domain.
- `APPROVED_RESEARCH_ONLY`: Permissive text mining allowed for non-commercial research.
- `NEEDS_REVIEW`: Licensing or redistribution terms uncertain. **Must not be included in RAG retrieval index until reviewed.**

---

## 3. Source Metadata Schema

Every document in `data/knowledge_base/metadata/` must record:
```json
{
  "document_id": "DOC-0001",
  "title": "Document Title",
  "organization_authors": "Organization or Authors",
  "publication_year": 2023,
  "version_date": "2023-05-15",
  "document_type": "clinical_guideline",
  "url": "https://...",
  "license_status": "APPROVED_OPEN_ACCESS",
  "topic": "antibiotic_stewardship",
  "evidence_level": "Level I (Clinical Guideline)",
  "retrieval_date": "2026-08-16T20:00:00Z",
  "md5_checksum": "a1b2c3..."
}
```
