#!/usr/bin/env python3
"""Create and verify a deterministic, standalone public release ZIP.

The command is intentionally local: it validates the immutable archive, writes a
root-file SHA-256 manifest, and emits a sibling ZIP plus its checksum.  Neither
output contains credentials or generated reviewer results.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import unquote

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from release_safety import _is_generated_path, _is_text_file, _scan_raw_bytes, _scan_relative_name, _scan_text

MAX_FILE_BYTES = 100 * 1024 * 1024
MANIFEST_NAME = "MANIFEST.sha256"
ZIP_TIMESTAMP = (2026, 1, 1, 0, 0, 0)
LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
REFERENCE_PATTERN = re.compile(r"^\s*\[[^\]]+\]:\s*(\S+)", re.M)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and package this public repository as a deterministic ZIP.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1], help="public repository root")
    parser.add_argument("--output", type=Path, help="ZIP path (default: sibling <root-name>.zip)")
    parser.add_argument("--verify-only", action="store_true", help="check the existing manifest and ZIP without writing files")
    return parser


def _release_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if _is_generated_path(relative) or relative.name == MANIFEST_NAME:
            continue
        if path.is_file():
            files.append(path)
    return sorted(files, key=lambda item: item.relative_to(root).as_posix())


def _link_target(raw: str) -> str:
    target = raw.strip()
    if target.startswith("<") and ">" in target:
        target = target[1:target.index(">")]
    else:
        target = target.split(maxsplit=1)[0]
    return unquote(target)


def _check_readme_links(root: Path, errors: list[str]) -> None:
    for readme in root.rglob("README.md"):
        relative = readme.relative_to(root)
        if _is_generated_path(relative):
            continue
        text = readme.read_text(encoding="utf-8", errors="replace")
        raw_targets = LINK_PATTERN.findall(text) + REFERENCE_PATTERN.findall(text)
        for raw in raw_targets:
            target = _link_target(raw)
            if not target or target.startswith(("#", "http://", "https://", "mailto:", "data:")):
                continue
            target = target.split("#", 1)[0].split("?", 1)[0]
            if not target:
                continue
            candidate = (root / target.lstrip("/")) if target.startswith("/") else (readme.parent / target)
            try:
                candidate.resolve().relative_to(root.resolve())
            except ValueError:
                errors.append(f"README link leaves release root: {relative} -> {target}")
                continue
            if not candidate.exists():
                errors.append(f"broken README link: {relative} -> {target}")


def _preflight(root: Path) -> list[str]:
    errors: list[str] = []
    if root.name != "robot-skill-program-synthesis":
        errors.append("release root must be named robot-skill-program-synthesis")
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if _is_generated_path(relative):
            continue
        _scan_relative_name(relative, errors)
        if path.is_symlink():
            errors.append(f"symlink is not permitted: {relative}")
        elif path.is_file():
            if path.stat().st_size > MAX_FILE_BYTES:
                errors.append(f"file exceeds 100 MiB: {relative}")
            if path.name.startswith(".env") and path.name != ".env.example":
                errors.append(f"environment file is not permitted: {relative}")
            if _is_text_file(path):
                _scan_text(path, root, errors)
            _scan_raw_bytes(path, root, errors)
    _check_readme_links(root, errors)
    return errors


def _manifest_lines(root: Path) -> list[str]:
    return [f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(root).as_posix()}" for path in _release_files(root)]


def _write_manifest(root: Path) -> Path:
    manifest = root / MANIFEST_NAME
    manifest.write_text("\n".join(_manifest_lines(root)) + "\n", encoding="utf-8")
    return manifest


def _verify_manifest(root: Path) -> list[str]:
    manifest = root / MANIFEST_NAME
    if not manifest.is_file():
        return [f"missing {MANIFEST_NAME}"]
    expected = "\n".join(_manifest_lines(root)) + "\n"
    return [] if manifest.read_text(encoding="utf-8") == expected else [f"{MANIFEST_NAME} does not match release files"]


def _zip_directories(root: Path) -> list[PurePosixPath]:
    directories = {PurePosixPath(root.name)}
    for path in _release_files(root) + [root / MANIFEST_NAME]:
        relative = PurePosixPath(path.relative_to(root).as_posix())
        for parent in relative.parents:
            if parent != PurePosixPath("."):
                directories.add(PurePosixPath(root.name) / parent)
    return sorted(directories, key=lambda item: item.as_posix())


def _zip_info(name: str, *, directory: bool = False) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name + ("/" if directory else ""), date_time=ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = ((0o40755 if directory else 0o100644) << 16) | (0x10 if directory else 0)
    return info


def _write_zip(root: Path, output: Path) -> None:
    if output.resolve().is_relative_to(root.resolve()):
        raise ValueError("ZIP output must be a sibling of the release directory")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=output.parent, prefix=f".{output.name}.", suffix=".tmp", delete=False) as temporary:
        temporary_path = Path(temporary.name)
    try:
        with zipfile.ZipFile(temporary_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9, strict_timestamps=True) as handle:
            for directory in _zip_directories(root):
                handle.writestr(_zip_info(directory.as_posix(), directory=True), b"")
            for path in _release_files(root) + [root / MANIFEST_NAME]:
                name = (PurePosixPath(root.name) / path.relative_to(root).as_posix()).as_posix()
                handle.writestr(_zip_info(name), path.read_bytes())
        os.replace(temporary_path, output)
    finally:
        temporary_path.unlink(missing_ok=True)


def _write_zip_checksum(output: Path) -> Path:
    checksum = output.with_suffix(output.suffix + ".sha256")
    checksum.write_text(f"{hashlib.sha256(output.read_bytes()).hexdigest()}  {output.name}\n", encoding="utf-8")
    return checksum


def _verify_zip_layout(root: Path, output: Path) -> None:
    with zipfile.ZipFile(output) as handle:
        names = handle.namelist()
        prefixes = {name.split("/", 1)[0] for name in names if name}
        if prefixes != {root.name}:
            raise ValueError(f"ZIP must contain only top-level directory {root.name}")
        for info in handle.infolist():
            member = PurePosixPath(info.filename)
            if member.is_absolute() or ".." in member.parts:
                raise ValueError(f"ZIP contains unsafe member: {info.filename}")
            if ((info.external_attr >> 16) & 0o170000) == 0o120000:
                raise ValueError(f"ZIP contains symlink member: {info.filename}")


def _verify_zip_contents(root: Path, output: Path) -> None:
    """Bind every ZIP member to the checked source tree, not just its name."""
    expected_files = _release_files(root) + [root / MANIFEST_NAME]
    expected = {(PurePosixPath(root.name) / path.relative_to(root).as_posix()).as_posix(): path for path in expected_files}
    expected_names = set(expected) | {f"{directory.as_posix()}/" for directory in _zip_directories(root)}
    manifest = (root / MANIFEST_NAME).read_bytes()
    source_hashes = {line.split("  ", 1)[1]: line.split("  ", 1)[0] for line in manifest.decode("utf-8").splitlines()}
    with zipfile.ZipFile(output) as handle:
        infos = handle.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)):
            raise ValueError("ZIP contains duplicate member names")
        if set(names) != expected_names:
            raise ValueError("ZIP member names do not exactly match the release tree")
        for info in infos:
            if info.is_dir():
                continue
            path = expected[info.filename]
            if info.file_size != path.stat().st_size:
                raise ValueError(f"ZIP member size mismatch: {info.filename}")
            digest = hashlib.sha256()
            with handle.open(info) as member:
                for chunk in iter(lambda: member.read(1024 * 1024), b""):
                    digest.update(chunk)
            relative = path.relative_to(root).as_posix()
            expected_hash = hashlib.sha256(manifest).hexdigest() if relative == MANIFEST_NAME else source_hashes[relative]
            if digest.hexdigest() != expected_hash:
                raise ValueError(f"ZIP member hash mismatch: {info.filename}")
        if handle.read(f"{root.name}/{MANIFEST_NAME}") != manifest:
            raise ValueError("embedded ZIP manifest differs from source manifest")


def _run_strict_validator(root: Path, output: Path) -> None:
    _verify_zip_layout(root, output)
    _verify_zip_contents(root, output)
    command = [sys.executable, str(root / "scripts" / "validate_archive.py"), "--root", str(root), "--strict", "--zip", str(output)]
    subprocess.run(command, check=True)


def main(argv: list[str] | None = None) -> None:
    args = _parser().parse_args(argv)
    root = args.root.resolve()
    output = (args.output or root.parent / f"{root.name}.zip").resolve()
    errors = _preflight(root)
    if errors:
        raise SystemExit("\n".join(f"ERROR: {error}" for error in errors))
    if args.verify_only:
        errors = _verify_manifest(root)
        if not output.is_file():
            errors.append(f"ZIP does not exist: {output}")
        else:
            checksum = output.with_suffix(output.suffix + ".sha256")
            if not checksum.is_file():
                errors.append(f"ZIP checksum sidecar is missing: {checksum}")
            elif checksum.read_text(encoding="utf-8") != f"{hashlib.sha256(output.read_bytes()).hexdigest()}  {output.name}\n":
                errors.append(f"ZIP checksum does not match: {checksum}")
        if errors:
            raise SystemExit("\n".join(f"ERROR: {error}" for error in errors))
        _run_strict_validator(root, output)
    else:
        manifest = _write_manifest(root)
        errors = _verify_manifest(root)
        if errors:
            raise SystemExit("\n".join(f"ERROR: {error}" for error in errors))
        _write_zip(root, output)
        checksum = _write_zip_checksum(output)
        _run_strict_validator(root, output)
        print(f"wrote {manifest}\nwrote {output}\nwrote {checksum}")


if __name__ == "__main__":
    main()
