from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "reports" / "epibench_overclaim_audit"
DEFAULT_SCAN_ROOTS = ["docs", "examples/epibench", "reports", "configs/epibench"]
SCAN_SUFFIXES = {".md", ".yaml", ".yml", ".json", ".txt"}
EXCLUDED_DIR_PARTS = {
    ".git",
    ".venv",
    ".uv-win",
    "__pycache__",
    "epibench_overclaim_audit",
    "commits",
    "delivery",
}
EXCLUDED_FILE_PREFIXES = ("CLAUDE_", "CODEX_", "CLAUDE", "CODEX")

PHRASES = {
    "clinical_or_regulatory": [
        "clinically approved",
        "clinical approval",
        "clinically certified",
        "clinical certification",
        "clinically safe",
        "ready for deployment",
        "deployment ready",
        "regulatory approved",
        "medical device",
    ],
    "scope_or_generality": [
        "generalizable",
        "generalise",
        "generalize",
        "universal certification",
        "universal standard",
        "community-ready standard",
    ],
    "edge_or_realtime": [
        "real-time",
        "on-device",
        "edge-ready",
    ],
    "sota_or_leaderboard": [
        "sota",
        "state of the art",
        "leaderboard winner",
    ],
}

SAFE_MARKERS = [
    "not ",
    "not_",
    "no ",
    "does not",
    "do not",
    "must not",
    "cannot",
    "can't",
    "forbidden",
    "anti-overclaim",
    "boundary",
    "doesn't mean",
    "ne signifie pas",
    "pas ",
    "sans ",
    "not a",
    "not clinical",
    "not clinically",
    "feasibility",
]

STRUCTURAL_SAFE_MARKERS = [
    "expected forbidden phrases",
    "blocks claim phrases",
    "forbidden phrases",
    "forbidden:",
    "sota_registry",
    "preferred_source",
    "relationship:",
    "rule:",
    "anti_overclaim",
    "anti-overclaim",
    "it is not",
    "optional but expected",
    "sota alignment",
    "sota registry",
    "sota review",
    "non-reinvention",
    "compatibility",
    "compatible",
    "citation",
    "source",
]

REVIEW_MARKERS = [
    "certified",
    "approved",
    "ready",
    "winner",
    "universal",
    "generalizable",
    "real-time",
    "on-device",
    "edge-ready",
    "sota",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit EpiBench artefacts for overclaim-prone wording.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--root", action="append", default=None, help="Scan root, repeatable")
    args = parser.parse_args()

    roots = [Path(root) for root in args.root] if args.root else [REPO_ROOT / root for root in DEFAULT_SCAN_ROOTS]
    result = build_overclaim_audit(roots=roots, out_dir=args.out_dir)
    print(
        "Built overclaim audit with "
        f"{result['finding_count']} finding(s), {result['requires_review_count']} requiring review"
    )
    return 0


def build_overclaim_audit(roots: list[Path], out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    findings = []
    for path in _iter_scan_files(roots):
        findings.extend(_scan_file(path))
    _write_csv(out_dir / "overclaim_findings.csv", findings)
    (out_dir / "README.md").write_text(_render_readme(findings), encoding="utf-8")
    return {
        "finding_count": len(findings),
        "bounded_count": sum(1 for finding in findings if finding["classification"] == "bounded"),
        "requires_review_count": sum(
            1 for finding in findings if finding["classification"] == "requires_review"
        ),
        "out_dir": str(out_dir),
    }


def _iter_scan_files(roots: list[Path]) -> list[Path]:
    files = []
    for root in roots:
        root = root if root.is_absolute() else REPO_ROOT / root
        if root.is_file() and root.suffix.lower() in SCAN_SUFFIXES:
            files.append(root)
            continue
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in SCAN_SUFFIXES:
                continue
            if any(part in EXCLUDED_DIR_PARTS for part in path.parts):
                continue
            if path.parent.name == "docs" and path.name.startswith(EXCLUDED_FILE_PREFIXES):
                continue
            files.append(path)
    return sorted(set(files))


def _scan_file(path: Path) -> list[dict[str, Any]]:
    findings = []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    for index, line in enumerate(lines, start=1):
        normalized = _normalize(line)
        for category, phrases in PHRASES.items():
            for phrase in phrases:
                if _phrase_matches(normalized, phrase):
                    context = _context(lines, index)
                    classification = _classify(line, context, phrase, path)
                    findings.append(
                        {
                            "file": _repo_relative(path),
                            "line": index,
                            "category": category,
                            "phrase": phrase,
                            "classification": classification,
                            "severity": _severity(category, classification),
                            "action": _action(classification),
                            "context": context.strip(),
                        }
                    )
    return findings


def _phrase_matches(normalized_line: str, phrase: str) -> bool:
    normalized_phrase = _normalize(phrase)
    if normalized_phrase == "sota":
        return bool(re.search(r"\bsota\b", normalized_line))
    return normalized_phrase in normalized_line


def _classify(line: str, context: str, phrase: str, path: Path) -> str:
    normalized_line = _normalize(line)
    normalized_context = _normalize(context)
    if phrase == "sota" and "sota_registry" in path.name:
        return "bounded"
    if any(marker in normalized_line for marker in SAFE_MARKERS):
        return "bounded"
    if any(marker in normalized_context for marker in STRUCTURAL_SAFE_MARKERS):
        return "bounded"
    if (
        phrase in {"medical device", "real-time", "on-device", "edge-ready"}
        and "forbidden_phrases" in normalized_context
    ):
        return "bounded"
    if any(marker in normalized_line for marker in REVIEW_MARKERS):
        return "requires_review"
    return "requires_review"


def _action(classification: str) -> str:
    if classification == "bounded":
        return "No action if context remains explicitly anti-overclaim."
    return "Review wording; add evidence boundary or remove unsupported claim."


def _severity(category: str, classification: str) -> str:
    if classification == "bounded":
        return "bounded"
    if category == "clinical_or_regulatory":
        return "critical"
    if category in {"scope_or_generality", "edge_or_realtime"}:
        return "major"
    return "moderate"


def _context(lines: list[str], line_number: int) -> str:
    start = max(0, line_number - 7)
    end = min(len(lines), line_number + 1)
    return " ".join(lines[start:end])


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _render_readme(findings: list[dict[str, Any]]) -> str:
    counts = _counts(finding["classification"] for finding in findings)
    category_counts = _counts(finding["category"] for finding in findings)
    severity_counts = _counts(finding["severity"] for finding in findings)
    review = [finding for finding in findings if finding["classification"] == "requires_review"]
    top_files = _top_counts(finding["file"] for finding in review)
    category_summary = _render_counts(category_counts)
    severity_summary = _render_counts(severity_counts)
    top_file_summary = _render_counts(top_files, sort_items=False)
    top_review = "\n".join(
        f"- `{finding['file']}:{finding['line']}` {finding['phrase']} "
        f"({finding['severity']}) -> {finding['action']}"
        for finding in review[:20]
    ) or "- None"
    return f"""# EpiBench Overclaim Audit

Generated from public-facing Markdown, YAML, JSON, and text artefacts.

## Purpose

This audit identifies wording that can be misread as clinical, regulatory, deployment, real-time,
generalization, or SOTA overclaim. It is a review aid, not a scientific certification result.

## Summary

- Findings: `{len(findings)}`.
- Bounded/anti-overclaim context: `{counts.get('bounded', 0)}`.
- Requires wording review: `{counts.get('requires_review', 0)}`.

## Category Counts

{category_summary}

## Severity Counts

{severity_summary}

## Files With Most Review Findings

{top_file_summary}

## Findings Requiring Review

{top_review}

## Boundary

`bounded` means the phrase appears in an explicit limitation, forbidden-phrase list, or
anti-overclaim statement. It should still be checked before submission, but it is not automatically
unsafe.

Before Q1 submission, every `requires_review` line should be either rewritten, bounded by explicit
evidence conditions, or recorded as an intentional editorial waiver in the manuscript review log.
"""


def _counts(values: Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return counts


def _top_counts(values: Any, limit: int = 10) -> dict[str, int]:
    counts = _counts(values)
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit])


def _render_counts(counts: dict[str, int], *, sort_items: bool = True) -> str:
    if not counts:
        return "- None"
    items = sorted(counts.items()) if sort_items else counts.items()
    return "\n".join(f"- `{key}`: `{value}`" for key, value in items)


def _normalize(text: str) -> str:
    return " ".join(text.casefold().replace("_", " ").split())


def _repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
