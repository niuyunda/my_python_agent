"""Docstring coverage gate for CI.

Fails when function/class docstring coverage in `src/` drops below threshold.
"""

from __future__ import annotations

import ast
from pathlib import Path


MIN_COVERAGE = 0.80
SRC_DIR = Path(__file__).resolve().parents[2] / "src"


def _collect_docstring_stats() -> tuple[int, int, list[str]]:
    """Return (documented_count, total_count, missing_entries)."""
    documented = 0
    total = 0
    missing: list[str] = []

    for py_file in sorted(SRC_DIR.rglob("*.py")):
        module = ast.parse(py_file.read_text(encoding="utf-8"))
        rel = py_file.relative_to(SRC_DIR.parent)

        for node in ast.walk(module):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                total += 1
                if ast.get_docstring(node):
                    documented += 1
                else:
                    kind = type(node).__name__.replace("Def", "").lower()
                    missing.append(f"{rel}:{node.lineno} {kind} {node.name}")

    return documented, total, missing


def test_docstring_coverage_threshold():
    """Ensure docstring coverage in src/ stays above required threshold."""
    documented, total, missing = _collect_docstring_stats()

    assert total > 0, "No class/function definitions found under src/."

    coverage = documented / total
    assert coverage >= MIN_COVERAGE, (
        f"Docstring coverage {coverage:.2%} is below required {MIN_COVERAGE:.2%}.\n"
        f"Missing ({len(missing)}):\n- "
        + "\n- ".join(missing[:80])
        + ("\n..." if len(missing) > 80 else "")
    )
