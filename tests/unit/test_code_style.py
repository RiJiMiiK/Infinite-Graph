from __future__ import annotations

from pathlib import Path
import tomllib


def test_python_module_size_policy() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    pyproject = tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))
    policy = pyproject["tool"]["infinite_graph"]["module_size_policy"]
    warning_lines = int(policy["warning_lines"])
    max_lines = int(policy["max_lines"])

    assert warning_lines < max_lines

    oversized_modules = []
    for file_path in sorted(repo_root.rglob("*.py")):
        relative_path = file_path.relative_to(repo_root).as_posix()
        if ".venv/" in relative_path or "__pycache__/" in relative_path:
            continue
        line_count = sum(1 for _ in file_path.open(encoding="utf-8"))
        if line_count > max_lines:
            oversized_modules.append((relative_path, line_count))

    assert oversized_modules == []
