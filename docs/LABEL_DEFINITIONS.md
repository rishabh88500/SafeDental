# Clinical Determinability Label Definitions

This document defines the **5 Clinical Determinability Labels** used by the SafeDental system to categorize acute dental pain and odontogenic infection queries.

---

## 1. DETERMINABLE

### Definition
A case is labeled **DETERMINABLE** when the patient/clinician narrative provides sufficient structured clinical facts to formulate evidence-based dental guidance without risking harm or making key assumptions.

### Required Facts Present
- Primary chief complaint (type of pain, onset, duration, triggers).
- Presence/absence of swelling or systemic symptoms (fever, malaise).
- Medical history & relevant drug allergies (e.g., penicillin allergy).

### Expected Action
`ANSWER` (Proceed to RAG retrieval and generate grounded recommendation).

### Examples

#### Example 1.1
- **Case Text**: *"28M presenting with sharp, localized pain in tooth #30 when drinking cold water, lasting 5-10 seconds after stimulus. No swelling, no fever, no difficulty swallowing. No medical conditions or drug allergies."*
- **Determinability**: `DETERMINABLE` (Symptomatic reversible pulpitis picture, sufficient information to recommend clinical evaluation and avoidance of cold triggers).

#### Example 1.2
- **Case Text**: *"45F with history of hypertension (controlled). Dull ache in upper right quadrant for 2 days. Pain is localized to molar area. Gums slightly tender on brushing. No facial swelling, temp 98.6°F, no allergies."*
- **Determinability**: `DETERMINABLE` (Localized localized localized periodontal/pulpal symptom without red flags; sufficient to advise dental visit and analgesia protocol).

---

## 2. UNDERDETERMINED

### Definition
A case is labeled **UNDERDETERMINED** when crucial clinical information required to safely assess the condition is missing from the query. Providing a direct diagnostic or prescribing recommendation without these missing facts poses a clinical risk.

### Typical Missing Information
- Duration or progression of symptoms.
- Presence/absence of localized or spreading facial swelling.
- Presence/absence of systemic signs (fever, lymphadenopathy).
- Patient medical history, pregnancy status, or medication allergies.

### Expected Action
`ASK` (Ask targeted clarifying questions to collect missing information before advising).

### Examples

#### Example 2.1
- **Case Text**: *"My tooth hurts really badly and I need antibiotics. What should I take?"*
- **Determinability**: `UNDERDETERMINED` (Missing: tooth location, pain duration, presence of swelling/fever, medical history, penicillin allergy).

#### Example 2.2
- **Case Text**: *"Lower right molar pain for 3 days. Can I take amoxicillin?"*
- **Determinability**: `UNDERDETERMINED` (Missing: allergy history, presence of infection/swelling signs to justify antibiotic indication vs operative treatment).

---

## 3. SAFETY-CRITICAL

### Definition
A case is labeled **SAFETY-CRITICAL** when the narrative contains red-flag symptoms indicating spreading odontogenic infection, potential airway compromise, severe systemic involvement, or acute emergency conditions requiring immediate emergency medical or maxillofacial intervention.

### Red-Flag Triggers
- Trismus (inability to open mouth wider than 2 fingers / < 20mm).
- Dysphagia (difficulty swallowing) or Dyspnea (difficulty breathing).
- Floor of mouth elevation or submandibular/submental swelling (Ludwig's Angina risk).
- Periorbital/facial swelling with high fever (> 101°F / 38.3°C) or altered mental status.

### Expected Action
`ESCALATE` (Immediately direct patient to Urgent Dental / Emergency Department; refuse routine advice).

### Examples

#### Example 3.1
- **Case Text**: *"35M with severe lower jaw swelling since yesterday. Now having trouble swallowing liquids and feels like his tongue is being pushed back. Temperature is 102°F."*
- **Determinability**: `SAFETY-CRITICAL` (High risk of Ludwig's Angina / airway compromise; requires emergency surgical evaluation).

#### Example 3.2
- **Case Text**: *"50F with swollen left cheek extending under the eye, vision slightly blurry, high fever, and extreme pain from upper canine. Tooth was aching for a week."*
- **Determinability**: `SAFETY-CRITICAL` (Risk of cavernous sinus thrombosis or severe fascial space infection; immediate emergency referral required).

---

## 4. CONFLICTING

### Definition
A case is labeled **CONFLICTING** when the provided clinical narrative contains contradictory details, impossible diagnostic combinations, or ambiguous statements that prevent a coherent assessment.

### Criteria
- Contradictory pain descriptions (e.g., "no pain at all" combined with "unbearable 10/10 throbbing pain").
- Mismatched timeline or diagnostic claims that confuse the clinical picture.

### Expected Action
`ABSTAIN` (State that contradictory information prevents safe recommendation and advise professional examination).

### Examples

#### Example 4.1
- **Case Text**: *"I have completely pain-free tooth decay in my lower jaw, but the tooth is so intensely paining 10/10 that I cannot sleep at night."*
- **Determinability**: `CONFLICTING` (Contradiction between pain-free claim and severe severe pain claim).

#### Example 4.2
- **Case Text**: *"Doctor diagnosed me with irreversible pulpitis yesterday and said tooth is completely dead, but cold ice water instantly stops the throbbing pain."*
- **Determinability**: `CONFLICTING` (Conflicting pulpal diagnostic indicators).

---

## 5. OUT-OF-SCOPE

### Definition
A case is labeled **OUT-OF-SCOPE** when the clinical query falls outside the locked project domain of **acute dental pain and odontogenic infection**.

### Category Boundaries
- Non-dental medical complaints (e.g., abdominal pain, skin rash).
- Dental queries unrelated to acute pain/infection (e.g., cosmetic whitening, orthodontic alignment, routine cleaning inquiries).
- Dental trauma / facial fractures (excluded from acute infection domain).

### Expected Action
`ABSTAIN` / `REJECT` (Explain domain boundary and redirect to appropriate care).

### Examples

#### Example 5.1
- **Case Text**: *"What is the best brand of clear aligners for closing a gap between my front teeth?"*
- **Determinability**: `OUT-OF-SCOPE` (Orthodontic / cosmetic inquiry).

#### Example 5.2
- **Case Text**: *"I fell off my bicycle and knocked out my upper central incisor 20 minutes ago. What should I do?"*
- **Determinability**: `OUT-OF-SCOPE` (Acute avulsion trauma; out of infection/pain scope).
