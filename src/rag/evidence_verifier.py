import re
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.rag.schemas import RetrievedChunk
from src.utils.logging import get_logger

logger = get_logger("evidence_verifier")


class ClaimSupportState(str, Enum):
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    NO_EVIDENCE = "NO_EVIDENCE"


class ClaimVerification(BaseModel):
    claim_id: str
    claim_text: str
    support_status: ClaimSupportState
    supporting_evidence_ids: List[str] = Field(default_factory=list)
    reason: str
    citation_correctness: bool = True


class EvidenceVerificationResult(BaseModel):
    claims: List[ClaimVerification] = Field(default_factory=list)
    supported_claim_count: int = 0
    unsupported_claim_count: int = 0
    support_rate: float = 0.0
    citation_correctness_rate: float = 1.0

    @property
    def is_supported(self) -> bool:
        """Returns True if at least 50% of claims are supported or no claims are flagged unsupported."""
        if not self.claims:
            return True
        return self.support_rate >= 0.5 or self.unsupported_claim_count == 0

    @property
    def support_ratio(self) -> float:
        """Alias for support_rate."""
        return self.support_rate



class EvidenceVerifier:
    """
    Evidence Verifier component for SafeDental Arm C.
    Verifies claim-level evidence support and citation correctness against retrieved chunks.
    Does NOT modify clinical determinability decisions.
    """

    def verify(
        self,
        generated_answer: str,
        retrieved_chunks: List[RetrievedChunk]
    ) -> EvidenceVerificationResult:
        if not generated_answer or not generated_answer.strip():
            return EvidenceVerificationResult()

        if not retrieved_chunks:
            # All claims made without retrieved evidence are NO_EVIDENCE
            sentences = [s.strip() for s in re.split(r"[.!?]", generated_answer) if len(s.strip()) > 10]
            claims = [
                ClaimVerification(
                    claim_id=f"CLM-{idx:03d}",
                    claim_text=sent,
                    support_status=ClaimSupportState.NO_EVIDENCE,
                    supporting_evidence_ids=[],
                    reason="No evidence chunks were provided.",
                    citation_correctness=False
                )
                for idx, sent in enumerate(sentences, 1)
            ]
            return EvidenceVerificationResult(
                claims=claims,
                supported_claim_count=0,
                unsupported_claim_count=len(claims),
                support_rate=0.0,
                citation_correctness_rate=0.0
            )

        # Extract sentences as claims
        sentences = [s.strip() for s in re.split(r"[.!?]", generated_answer) if len(s.strip()) > 10]
        claims: List[ClaimVerification] = []
        supported_count = 0
        correct_citation_count = 0

        chunk_texts = [chk.text.lower() for chk in retrieved_chunks]
        chunk_ids = [chk.chunk_id for chk in retrieved_chunks]
        doc_ids = [chk.document_id for chk in retrieved_chunks]

        for idx, sent in enumerate(sentences, 1):
            sent_lower = sent.lower()

            # Find matching citations inside sentence e.g. [DOC-0001], [CHK-0001-0001], [EVIDENCE 1]
            cited_ids = []
            for cid in chunk_ids + doc_ids:
                if cid.lower() in sent_lower:
                    cited_ids.append(cid)

            # Check overlap with evidence text
            matched_evidence = []
            for chk in retrieved_chunks:
                # Key phrase or word overlap
                words = [w for w in re.findall(r"\w+", sent_lower) if len(w) > 4]
                match_count = sum(1 for w in words if w in chk.text.lower())
                if match_count >= 2 or (len(words) < 3 and match_count >= 1):
                    matched_evidence.append(chk.chunk_id)

            citation_correct = True
            if cited_ids:
                # Citation is correct if cited ID is actually present in retrieved chunks
                citation_correct = any(cid in (chunk_ids + doc_ids) for cid in cited_ids)

            if matched_evidence:
                status = ClaimSupportState.SUPPORTED
                reason = f"Supported by evidence chunk(s): {', '.join(matched_evidence)}"
                supported_count += 1
            elif cited_ids and not matched_evidence:
                status = ClaimSupportState.PARTIALLY_SUPPORTED
                reason = "Cited evidence tag present but low textual word overlap."
                supported_count += 1
            else:
                status = ClaimSupportState.UNSUPPORTED
                reason = "Claim text lacks matching statements in retrieved evidence."

            if citation_correct:
                correct_citation_count += 1

            claims.append(
                ClaimVerification(
                    claim_id=f"CLM-{idx:03d}",
                    claim_text=sent,
                    support_status=status,
                    supporting_evidence_ids=list(set(matched_evidence + cited_ids)),
                    reason=reason,
                    citation_correctness=citation_correct
                )
            )

        total_claims = len(claims)
        supp_rate = (supported_count / total_claims * 100.0) if total_claims > 0 else 100.0
        cit_rate = (correct_citation_count / total_claims) if total_claims > 0 else 1.0

        return EvidenceVerificationResult(
            claims=claims,
            supported_claim_count=supported_count,
            unsupported_claim_count=total_claims - supported_count,
            support_rate=round(supp_rate, 2),
            citation_correctness_rate=round(cit_rate, 4)
        )
