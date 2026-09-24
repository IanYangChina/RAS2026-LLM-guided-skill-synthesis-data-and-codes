"""Shared release-file selection and privacy checks for packaging and validation."""
from __future__ import annotations

from collections import Counter
import math
import re
from pathlib import Path, PurePosixPath

GENERATED_DIRECTORY_NAMES = {".pytest_cache", "__pycache__", "build", "dist", "outputs", "renders", "reproduced_results", "runs"}
BYTECODE_SUFFIXES = {".pyc", ".pyo"}
TEXT_SUFFIXES = {".cfg", ".cff", ".conf", ".csv", ".ini", ".json", ".jsonl", ".md", ".py", ".rst", ".sh", ".toml", ".txt", ".xml", ".yaml", ".yml"}
TEXT_FILENAMES = {".env.example", ".gitignore", "LICENSE"}
BINARY_SUFFIXES = {".gif", ".jpeg", ".jpg", ".mp4", ".png", ".stl"}
FORBIDDEN_PATTERNS = (
    re.compile("agentic" + "pmsgen", re.I),
    re.compile(r"(?:^|[^A-Za-z0-9])v\d+\.\d+(?:[^A-Za-z0-9]|$)", re.I),
    re.compile(r"\bsub" + "version\b|\bpaper_" + "campaign\b", re.I),
    re.compile(r"(?:^|/)(?:artifacts(?:_v\d+)?|workspace)(?:/|$)", re.I),
    re.compile(r"(?<![A-Za-z0-9])/(?:home|Users)/[A-Za-z0-9_.-]+"),
    re.compile(r"[A-Za-z]:\\Users\\[A-Za-z0-9_.-]+", re.I),
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
)
TOKEN_PATTERN = re.compile(r"(?<![A-Za-z0-9])[A-Za-z0-9_-]{32,}(?![A-Za-z0-9])")
PUBLIC_ID_PATTERN = re.compile(
    r"(?:skill-)?(?:e-expert-reference|p-(?:create|random|scaffold)-(?:bandit|language|mapqd|param-only)-(?:fixed|free)|"
    r"s-(?:full-context|misaligned-history|misattributed-contact|no-contact-information|no-history|no-scene-description|wrong-scene-targets))"
    r"-(?:door_push|push_to_goal|peg_insert|peg_channel|grasp_place|obstacle_reach)-seed-\d{2}"
    r"(?:-attempt-\d{2}|-best|-initial|-archive|-progress_status|-run_status)?"
)
CREDENTIAL_ASSIGNMENT = re.compile(r"(?<![A-Za-z0-9_])['\"]?(?:api[_-]?key|token|secret|password)['\"]?\s*[:=]\s*(?P<value>[^\s#]+)", re.I)


def _is_generated_path(path: Path | PurePosixPath) -> bool:
    return any(part in GENERATED_DIRECTORY_NAMES or part.endswith(".egg-info") for part in path.parts) or path.suffix.lower() in BYTECODE_SUFFIXES


def _is_text_file(path: Path) -> bool:
    if path.suffix.lower() in TEXT_SUFFIXES or path.name in TEXT_FILENAMES:
        return True
    if path.suffix.lower() in BINARY_SUFFIXES:
        return False
    with path.open("rb") as handle:
        sample = handle.read(8192)
    if b"\0" in sample:
        return False
    try:
        decoded = sample.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return all(ord(char) >= 32 or char in "\t\r\n" for char in decoded)


def _entropy(value: str) -> float:
    if not value:
        return 0.0
    return -sum((count / len(value)) * math.log2(count / len(value)) for count in Counter(value).values())


def _contains_literal_credential(text: str) -> bool:
    allowed = {"api_key", "api_token", "token", "secret", "password", "key", "none", "null", "true", "false", "str", "int", "bool", "bytes", "float", "example", "your-key", "replace-me", "_load_deepseek_api_key()"}
    for match in CREDENTIAL_ASSIGNMENT.finditer(text):
        value = match.group("value").rstrip(",;")
        if value.endswith(")") and not value.endswith("()"):
            value = value.rstrip(")")
        value = value.strip("\"\x27")
        if not value or value.lower() in allowed or value.startswith(("<", "${", "$", "{", "os.environ", "os.getenv")):
            continue
        return True
    return False


def _allowed_nonsecret_token(token: str) -> bool:
    return bool(
        re.fullmatch(r"[0-9a-fA-F]{64}", token)
        or PUBLIC_ID_PATTERN.fullmatch(token)
        or token in {"randomized_config_bank_wrapper_sha256", "_randomized_config_bank_wrapper_sha256"}
    )


def _scan_text(path: Path, root: Path, errors: list[str]) -> None:
    checked = path.read_text(encoding="utf-8", errors="replace")
    if path.name == ".env.example":
        if re.search(r"(?m)^[ \t]*[A-Za-z_][A-Za-z0-9_]*[ \t]*=[ \t]*\S", checked):
            errors.append(f"nonblank environment template: {path.relative_to(root)}")
        checked = re.sub(r"(?m)^\s*[A-Za-z_][A-Za-z0-9_]*\s*=\s*$", "", checked)
    if any(pattern.search(checked) for pattern in FORBIDDEN_PATTERNS) or _contains_literal_credential(checked):
        errors.append(f"forbidden release text: {path.relative_to(root)}")
    for token in TOKEN_PATTERN.findall(checked):
        if not _allowed_nonsecret_token(token) and _entropy(token) >= 4.2:
            errors.append(f"possible high-entropy secret: {path.relative_to(root)}")
            break


def _scan_raw_bytes(path: Path, root: Path, errors: list[str]) -> None:
    """Check private signatures and ASCII tokens in NUL-prefixed/binary files."""
    checked = path.read_bytes().decode("latin-1")
    relative = path.relative_to(root)
    if any(pattern.search(checked) for pattern in FORBIDDEN_PATTERNS) or _contains_literal_credential(checked):
        if f"forbidden release text: {relative}" not in errors:
            errors.append(f"forbidden release bytes: {relative}")
    for match in TOKEN_PATTERN.finditer(checked):
        left = checked[match.start() - 1] if match.start() else "\n"
        right = checked[match.end()] if match.end() < len(checked) else "\n"
        if left not in "\x00\r\n\t " or right not in "\x00\r\n\t ":
            continue  # compressed media can contain accidental alphanumeric runs
        candidate = match.group()
        if not _allowed_nonsecret_token(candidate) and _entropy(candidate) >= 4.2:
            if f"possible high-entropy secret: {relative}" not in errors:
                errors.append(f"possible high-entropy secret in bytes: {relative}")
            break


def _scan_relative_name(relative: Path, errors: list[str]) -> None:
    name = relative.as_posix()
    if any(pattern.search(name) for pattern in FORBIDDEN_PATTERNS):
        errors.append(f"forbidden release path: {name}")
    for token in TOKEN_PATTERN.findall(name):
        if not _allowed_nonsecret_token(token) and _entropy(token) >= 4.2:
            errors.append(f"possible high-entropy secret in path: {name}")
            break
