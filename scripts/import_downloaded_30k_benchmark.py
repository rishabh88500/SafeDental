#!/usr/bin/env python3
"""
Imports the 30,000 cases from Downloads folder (benchmark_30000_cases.jsonl),
validates each case against ClinicalCase, populates supporting evidence anchors,
and writes the active benchmark dataset and retrieval benchmark files.
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.schema import ClinicalCase, DeterminabilityLabel, ExpectedAction
from src.utils.logging import get_logger

logger = get_logger("import_30k")

DEFAULT_EVIDENCE = {
    DeterminabilityLabel.DETERMINABLE: ("DOC-0004", "analgesia_protocols"),
    DeterminabilityLabel.UNDERDETERMINED: ("DOC-0001", "antibiotic_stewardship"),
    DeterminabilityLabel.SAFETY_CRITICAL: ("DOC-0005", "urgent_escalation_red_flags"),
    DeterminabilityLabel.CONFLICTING: ("DOC-0005", "urgent_escalation_red_flags"),
    DeterminabilityLabel.OUT_OF_SCOPE: ("DOC-0004", "analgesia_protocols"),
}


def import_downloaded_benchmark(
    download_path: Path = Path("/Users/rishabhsingh/Downloads/benchmark_30000_cases.jsonl"),
    dest_cases_path: Path = PROJECT_ROOT / "data" / "benchmarks" / "benchmark_30000_cases.jsonl",
    dest_queries_path: Path = PROJECT_ROOT / "data" / "benchmarks" / "retrieval_benchmark_30000.json"
):
    if not download_path.exists():
        raise FileNotFoundError(f"Could not find downloaded cases at {download_path}")

    dest_cases_path.parent.mkdir(parents=True, exist_ok=True)
    dest_queries_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Importing and validating cases from {download_path}...")
    
    cases: List[Dict[str, Any]] = []
    queries: List[Dict[str, Any]] = []

    with open(download_path, "r", encoding="utf-8") as f_in, \
         open(dest_cases_path, "w", encoding="utf-8") as f_out:
        
        for idx, line in enumerate(f_in):
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            
            # Map default evidence if empty
            label_val = data.get("determinability_label")
            try:
                det_label = DeterminabilityLabel(label_val)
            except ValueError:
                det_label = DeterminabilityLabel.UNDERDETERMINED

            doc_id, topic = DEFAULT_EVIDENCE.get(det_label, ("DOC-0001", "antibiotic_stewardship"))
            if not data.get("supporting_evidence_ids"):
                data["supporting_evidence_ids"] = [doc_id]

            # Validate against Pydantic model
            case_obj = ClinicalCase.model_validate(data)
            
            # Write validated case
            f_out.write(case_obj.model_dump_json() + "\n")
            cases.append(data)

            # Build corresponding retrieval query
            queries.append({
                "query_id": f"Q-{idx+1:05d}",
                "query": case_obj.question,
                "target_doc_id": doc_id,
                "expected_topic": topic
            })

    with open(dest_queries_path, "w", encoding="utf-8") as f_q:
        json.dump(queries, f_q, indent=2)

    logger.info(f"Successfully imported {len(cases)} cases to {dest_cases_path}")
    logger.info(f"Successfully generated {len(queries)} retrieval queries to {dest_queries_path}")
    return len(cases)


if __name__ == "__main__":
    count = import_downloaded_benchmark()
    print(f"Imported and verified {count:,} downloaded benchmark cases.")
