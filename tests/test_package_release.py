from __future__ import annotations

import hashlib
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from package_release import _preflight, _scan_relative_name, _verify_manifest, _verify_zip_contents, _verify_zip_layout, _write_manifest, _write_zip, _write_zip_checksum, main  # noqa: E402


def _small_release(tmp_path: Path) -> Path:
    root = tmp_path / "robot-skill-program-synthesis"
    root.mkdir()
    (root / "README.md").write_text("[script](scripts/_llm_search.py)\n", encoding="utf-8")
    (root / "scripts").mkdir()
    (root / "scripts/_llm_search.py").write_text(
        'token' + ' = os.environ.get("DEEPSEEK_API_KEY")\n'
        'token' + ' = _load_deepseek_api_key()\n'
        'client = Client(api_' + 'key=token)\n',
        encoding="utf-8",
    )
    return root


def test_safe_runtime_key_lookup_is_not_a_literal_secret(tmp_path: Path) -> None:
    assert _preflight(_small_release(tmp_path)) == []


@pytest.mark.parametrize(
    "text",
    [
        'api_' + 'key = "sk-' + 'abcdefghijklmnop' + 'qrstuvwxyz012345"\n',
        'token' + ' = "aB7cD8eF9gH0iJ1kL2mN3oP' + '4qR5sT6uV7wX8yZ9A"\n',
        'path = "' + '/home' + '/privateperson/private/data"\n',
        "synthetic tag: v" + "99.99\n",
    ],
)
def test_release_preflight_rejects_private_content(tmp_path: Path, text: str) -> None:
    root = _small_release(tmp_path)
    (root / "scripts/private.py").write_text(text, encoding="utf-8")
    assert _preflight(root)


def test_release_preflight_rejects_broken_link_and_symlink(tmp_path: Path) -> None:
    root = _small_release(tmp_path)
    (root / "README.md").write_text("[missing](none.md)\n", encoding="utf-8")
    (root / "external").symlink_to(tmp_path / "outside")
    errors = _preflight(root)
    assert any("broken README link" in error for error in errors)
    assert any("symlink is not permitted" in error for error in errors)


@pytest.mark.parametrize(
    "text",
    [
        '"api_' + 'key": "literal-value"',
        'token' + ': literal-value',
        'password' + ' = "literal-value"',
        'value = "ABCDEFGHIJKLMNOP' + 'qrstuvwxyz012345"',
        'path = "C:' + '\\Users\\Reviewer\\private"',
    ],
)
def test_release_preflight_rejects_credentials_and_private_windows_paths(tmp_path: Path, text: str) -> None:
    root = _small_release(tmp_path)
    (root / "scripts/private.py").write_text(text, encoding="utf-8")
    assert _preflight(root)


def test_release_preflight_scans_relative_names() -> None:
    errors: list[str] = []
    _scan_relative_name(Path("data") / ("v" + "99.99") / "file.txt", errors)
    assert errors


def test_release_preflight_scans_jsonl_records(tmp_path: Path) -> None:
    root = _small_release(tmp_path)
    (root / "data").mkdir()
    (root / "data/trace.jsonl").write_text('{"api_' + 'key": "literal-value"}\n', encoding="utf-8")
    assert _preflight(root)


def test_release_preflight_rejects_extensionless_credential(tmp_path: Path) -> None:
    root = _small_release(tmp_path)
    (root / "data").mkdir()
    (root / "data/CREDENTIALS").write_text('api_' + 'key: literal-value\n', encoding="utf-8")
    assert any("forbidden release text" in error for error in _preflight(root))


@pytest.mark.parametrize("suffix", ["obj", "dat", "secret"])
def test_release_preflight_sniffs_unlisted_text_suffixes(tmp_path: Path, suffix: str) -> None:
    root = _small_release(tmp_path)
    (root / "data").mkdir()
    (root / f"data/payload.{suffix}").write_text('api_' + 'key: literal-value\n', encoding="utf-8")
    assert any("forbidden release text" in error for error in _preflight(root))


@pytest.mark.parametrize("name", ["payload.dat", "CREDENTIALS", "payload.png"])
def test_release_preflight_rejects_binary_embedded_credential(tmp_path: Path, name: str) -> None:
    root = _small_release(tmp_path)
    (root / name).write_bytes(b"\x00binary\napi_" + b"key: literal-value\n")
    assert any(f"forbidden release bytes: {name}" in error for error in _preflight(root))


def test_release_preflight_rejects_binary_embedded_private_path(tmp_path: Path) -> None:
    root = _small_release(tmp_path)
    (root / "payload.dat").write_bytes(b"\x00binary\n/home" + b"/privateperson/data\n")
    assert any("forbidden release bytes: payload.dat" in error for error in _preflight(root))


def test_release_preflight_rejects_nul_prefixed_bare_token(tmp_path: Path) -> None:
    root = _small_release(tmp_path)
    candidate = "".join(("aB7cD8eF", "9gH0iJ1k", "L2mN3oP4", "qR5sT6uV", "7wX8yZ9A"))
    (root / "payload.dat").write_bytes(b"\x00binary\n" + candidate.encode() + b"\n")
    assert any("possible high-entropy secret in bytes: payload.dat" in error for error in _preflight(root))


def test_release_preflight_rejects_nonblank_env_template(tmp_path: Path) -> None:
    root = _small_release(tmp_path)
    (root / ".env.example").write_text("DEEPSEEK_API_KEY=not-a-real-key\n", encoding="utf-8")
    assert any("nonblank environment template" in error for error in _preflight(root))


def test_release_manifest_and_zip_are_deterministic(tmp_path: Path) -> None:
    root = _small_release(tmp_path)
    first_manifest = _write_manifest(root).read_bytes()
    assert _verify_manifest(root) == []
    output = tmp_path / "release.zip"
    _write_zip(root, output)
    _verify_zip_layout(root, output)
    _verify_zip_contents(root, output)
    first_hash = hashlib.sha256(output.read_bytes()).hexdigest()
    sidecar = _write_zip_checksum(output)
    assert sidecar.read_text(encoding="utf-8") == f"{first_hash}  release.zip\n"
    assert _write_manifest(root).read_bytes() == first_manifest
    _write_zip(root, output)
    assert hashlib.sha256(output.read_bytes()).hexdigest() == first_hash
    with zipfile.ZipFile(output) as handle:
        names = handle.namelist()
    assert all(name.startswith(f"{root.name}/") for name in names)


@pytest.mark.parametrize("corruption", ["duplicate", "missing", "extra", "changed", "manifest"])
def test_release_zip_rejects_member_corruption(tmp_path: Path, corruption: str) -> None:
    root = _small_release(tmp_path)
    _write_manifest(root)
    output = tmp_path / "release.zip"
    _write_zip(root, output)
    with zipfile.ZipFile(output) as handle:
        members = [(info.filename, handle.read(info)) for info in handle.infolist()]
    file_name = f"{root.name}/README.md"
    manifest_name = f"{root.name}/MANIFEST.sha256"
    if corruption == "duplicate":
        members.append((file_name, b"duplicate"))
    elif corruption == "missing":
        members = [(name, data) for name, data in members if name != file_name]
    elif corruption == "extra":
        members.append((f"{root.name}/extra.txt", b"extra"))
    else:
        victim = manifest_name if corruption == "manifest" else file_name
        members = [(name, b"changed" if name == victim else data) for name, data in members]
    with zipfile.ZipFile(output, "w") as handle:
        for name, data in members:
            handle.writestr(name, data)
    with pytest.raises(ValueError):
        _verify_zip_contents(root, output)


def test_verify_only_reports_missing_checksum_sidecar(tmp_path: Path) -> None:
    root = _small_release(tmp_path)
    _write_manifest(root)
    output = tmp_path / "release.zip"
    _write_zip(root, output)
    with pytest.raises(SystemExit, match="checksum sidecar is missing"):
        main(["--root", str(root), "--output", str(output), "--verify-only"])
