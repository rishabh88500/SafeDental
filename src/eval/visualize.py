from pathlib import Path
from typing import Dict, List, Any, Optional
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

from src.eval.schemas import ArmMetrics


def plot_metrics_comparison(
    arm_metrics_dict: Dict[str, ArmMetrics],
    output_path: Path
) -> Path:
    """
    Generates a grouped bar chart comparing the 4 primary research metrics across experimental arms.
    """
    arms = sorted(list(arm_metrics_dict.keys()))
    metrics_names = [
        "Unsafe Rec Rate (↓)",
        "Safe Abstain Rate (↑)",
        "Clinical Accuracy (↑)",
        "Over-Abstain Rate (↓)"
    ]

    # Data matrix
    data = []
    for arm in arms:
        m = arm_metrics_dict[arm]
        data.append([
            m.unsafe_recommendation_rate,
            m.safe_abstention_rate,
            m.clinical_answer_accuracy,
            m.over_abstention_rate
        ])

    data = np.array(data)  # shape (num_arms, 4)

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    x = np.arange(len(metrics_names))
    width = 0.25

    colors = ["#e74c3c", "#3498db", "#2ecc71"]  # Arm A (red), Arm B (blue), Arm C (green)

    for idx, arm in enumerate(arms):
        offset = (idx - len(arms) / 2) * width + width / 2
        rects = ax.bar(
            x + offset,
            data[idx],
            width,
            label=arm,
            color=colors[idx % len(colors)],
            alpha=0.85,
            edgecolor="black",
            linewidth=0.8
        )
        # Add values on top of bars
        for rect in rects:
            height = rect.get_height()
            ax.annotate(
                f"{height:.2f}",
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
                fontweight="bold"
            )

    ax.set_ylabel("Metric Value (0.00 - 1.00)", fontsize=11, fontweight="bold")
    ax.set_title("Comparative Evaluation of Dental Safety & Abstention Pipelines (Dev Set)", fontsize=13, fontweight="bold", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics_names, fontsize=10, fontweight="bold")
    ax.set_ylim(0.0, 1.15)
    ax.legend(title="Experimental Arm", frameon=True, facecolor="#f8f9fa")
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, format="png")
    plt.close(fig)
    return output_path


def plot_confusion_matrices(
    arm_metrics_dict: Dict[str, ArmMetrics],
    output_path: Path
) -> Path:
    """
    Generates action confusion matrix heatmaps side-by-side for each experimental arm.
    """
    arms = sorted(list(arm_metrics_dict.keys()))
    actions = ["ANSWER", "ASK", "ABSTAIN", "ESCALATE"]

    fig, axes = plt.subplots(1, len(arms), figsize=(5 * len(arms), 4.5), dpi=300)
    if len(arms) == 1:
        axes = [axes]

    for idx, arm in enumerate(arms):
        ax = axes[idx]
        matrix_dict = arm_metrics_dict[arm].action_confusion_matrix
        matrix_data = np.zeros((len(actions), len(actions)), dtype=int)

        for i, gold_a in enumerate(actions):
            for j, pred_a in enumerate(actions):
                matrix_data[i, j] = matrix_dict.get(gold_a, {}).get(pred_a, 0)

        im = ax.imshow(matrix_data, cmap="Blues", interpolation="nearest")
        ax.set_title(f"{arm} Action Matrix", fontsize=11, fontweight="bold")
        ax.set_xticks(np.arange(len(actions)))
        ax.set_yticks(np.arange(len(actions)))
        ax.set_xticklabels(actions, rotation=45, ha="right", fontsize=9)
        ax.set_yticklabels(actions, fontsize=9)

        if idx == 0:
            ax.set_ylabel("Gold Expected Action", fontsize=10, fontweight="bold")
        ax.set_xlabel("Predicted Action", fontsize=10, fontweight="bold")

        # Annotate matrix values
        for i in range(len(actions)):
            for j in range(len(actions)):
                val = matrix_data[i, j]
                color = "white" if val > (matrix_data.max() / 2) else "black"
                ax.text(j, i, str(val), ha="center", va="center", color=color, fontweight="bold")

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, format="png")
    plt.close(fig)
    return output_path


def plot_risk_coverage(
    arm_metrics_dict: Dict[str, ArmMetrics],
    output_path: Path
) -> Path:
    """
    Generates a Risk vs. Coverage trade-off plot.
    Risk = Unsafe Recommendation Rate
    Coverage = Fraction of non-abstained cases
    """
    fig, ax = plt.subplots(figsize=(7, 5), dpi=300)
    colors = {"ARM_A": "#e74c3c", "ARM_B": "#3498db", "ARM_C": "#2ecc71"}
    markers = {"ARM_A": "o", "ARM_B": "s", "ARM_C": "^"}

    for arm, metrics in arm_metrics_dict.items():
        # Coverage on non-determinable cases = unsafe_recommendation_rate (since answering when should abstain = coverage of non-det)
        # Or overall answered fraction
        coverage = 1.0 - metrics.safe_abstention_rate
        risk = metrics.unsafe_recommendation_rate

        c = colors.get(arm, "#333333")
        m = markers.get(arm, "o")

        ax.scatter(coverage, risk, color=c, marker=m, s=150, label=arm, zorder=5)
        ax.annotate(
            f"{arm}\n(Risk: {risk:.2f}, Cov: {coverage:.2f})",
            xy=(coverage, risk),
            xytext=(10, -10),
            textcoords="offset points",
            fontsize=9,
            fontweight="bold"
        )

    ax.set_xlabel("Coverage (Fraction of Non-Abstained Cases)", fontsize=10, fontweight="bold")
    ax.set_ylabel("Unsafe Recommendation Risk", fontsize=10, fontweight="bold")
    ax.set_title("Safety-Risk vs. Coverage Tradeoff Across System Arms", fontsize=12, fontweight="bold")
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="upper left")

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, format="png")
    plt.close(fig)
    return output_path
