import json
import random
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict
from src.data.schema import ClinicalCase, DatasetSplit, DeterminabilityLabel
from src.utils.logging import get_logger

logger = get_logger("split")


def stratified_split_cases(
    cases: List[ClinicalCase],
    train_ratio: float = 0.30,
    dev_ratio: float = 0.30,
    test_ratio: float = 0.40,
    seed: int = 42
) -> Dict[DatasetSplit, List[ClinicalCase]]:
    """
    Performs stratified random splitting of cases based on determinability_label.

    Ratios must sum to 1.0.
    Default: Train=30%, Dev=30%, Test=40% (Sealed test set).
    """
    assert abs((train_ratio + dev_ratio + test_ratio) - 1.0) < 1e-5, "Ratios must sum to 1.0"

    random.seed(seed)

    # Group by label
    label_groups: Dict[DeterminabilityLabel, List[ClinicalCase]] = defaultdict(list)
    for case in cases:
        label_groups[case.determinability_label].append(case)

    splits: Dict[DatasetSplit, List[ClinicalCase]] = {
        DatasetSplit.TRAIN: [],
        DatasetSplit.DEV: [],
        DatasetSplit.TEST: []
    }

    for label, group_cases in label_groups.items():
        # Shuffle group reproducibly
        shuffled = list(group_cases)
        random.shuffle(shuffled)

        n_total = len(shuffled)
        n_train = int(round(n_total * train_ratio))
        n_dev = int(round(n_total * dev_ratio))

        train_cases = shuffled[:n_train]
        dev_cases = shuffled[n_train:n_train + n_dev]
        test_cases = shuffled[n_train + n_dev:]

        for c in train_cases:
            c.split = DatasetSplit.TRAIN
            splits[DatasetSplit.TRAIN].append(c)

        for c in dev_cases:
            c.split = DatasetSplit.DEV
            splits[DatasetSplit.DEV].append(c)

        for c in test_cases:
            c.split = DatasetSplit.TEST
            splits[DatasetSplit.TEST].append(c)

    logger.info(
        f"Stratified split complete (seed={seed}): "
        f"Train={len(splits[DatasetSplit.TRAIN])}, "
        f"Dev={len(splits[DatasetSplit.DEV])}, "
        f"Test={len(splits[DatasetSplit.TEST])} (Sealed)"
    )
    return splits


def save_split_files(
    splits: Dict[DatasetSplit, List[ClinicalCase]],
    output_dir: Path
) -> Tuple[Path, Path, Path]:
    """Saves cases into train.jsonl, dev.jsonl, and test.jsonl in output_dir."""
    output_dir.mkdir(parents=True, exist_ok=True)

    train_path = output_dir / "train.jsonl"
    dev_path = output_dir / "dev.jsonl"
    test_path = output_dir / "test.jsonl"

    for split_type, path in [(DatasetSplit.TRAIN, train_path), (DatasetSplit.DEV, dev_path), (DatasetSplit.TEST, test_path)]:
        cases = splits[split_type]
        with open(path, "w", encoding="utf-8") as f:
            for case in cases:
                f.write(case.model_dump_json() + "\n")
        logger.info(f"Saved {len(cases)} cases to {path}")

    return train_path, dev_path, test_path
