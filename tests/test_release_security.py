from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_archive import _catalog, _safe_reference, _validate_reference_paths, main  # noqa: E402


@pytest.mark.parametrize("reference", ["", "/tmp/private", "C:\\Users\\Reviewer\\private", "../private", "data/../private", "data//file", "data\\file"])
def test_reference_resolver_rejects_noncanonical_paths(tmp_path: Path, reference: str) -> None:
    with pytest.raises(ValueError):
        _safe_reference(tmp_path, reference)


def test_reference_resolver_rejects_symlink_escape(tmp_path: Path) -> None:
    root = tmp_path / "release"
    root.mkdir()
    (root / "escape").symlink_to(tmp_path)
    with pytest.raises(ValueError):
        _safe_reference(root, "escape/private.txt")


@pytest.mark.parametrize(
    "table,field",
    [
        ("skill_catalog.csv", "path"),
        ("skill_catalog.csv", "scene_bank_path"),
        ("skill_catalog.csv", "parameters_path"),
        ("companions/generation_zero_catalog.csv", "path"),
        ("provenance/normalized_file_provenance.csv", "public_path"),
        ("provenance/winner_extractions.csv", "public_path"),
        ("provenance/winner_extractions.csv", "source_container_path"),
        ("provenance/reconstructed_scene_banks.csv", "public_path"),
        ("provenance/reconstructed_scene_banks.csv", "source_container_path"),
        ("provenance/derived_records.csv", "public_path"),
        ("provenance/derived_records.csv", "source_container_path"),
        ("paper_crosswalk.csv", "public_sources"),
        ("paper_crosswalk.csv", "reproduced_outputs"),
    ],
)
def test_all_reference_tables_reject_escape(tmp_path: Path, table: str, field: str) -> None:
    root = tmp_path / "release"
    data = root / "data"
    data.mkdir(parents=True)
    path = data / table
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[field])
        writer.writeheader()
        writer.writerow({field: "../private"})
    errors: list[str] = []
    _validate_reference_paths(root, [], errors)
    assert any("unsafe" in error and field in error for error in errors), errors


def test_catalog_and_checksum_manifest_reject_escape(tmp_path: Path) -> None:
    root = tmp_path / "release"
    provenance = root / "data/provenance"
    provenance.mkdir(parents=True)
    (root / "data/catalog.csv").write_text("record_id,path,sha256\na,../private,\n", encoding="utf-8")
    errors: list[str] = []
    rows = _catalog(root, errors)
    assert any("unsafe" in error and "path" in error for error in errors)
    (provenance / "checksums.sha256").write_text("0" * 64 + "  ../private\n", encoding="utf-8")
    _validate_reference_paths(root, rows, errors)
    assert any("checksum manifest" in error for error in errors)


def test_validator_rejects_extensionless_credential(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = tmp_path / "release"
    data = root / "data"
    data.mkdir(parents=True)
    (data / "README.md").write_text("Data.\n", encoding="utf-8")
    (data / "CREDENTIALS").write_text('"api_' + 'key": "literal-value"\n', encoding="utf-8")
    with pytest.raises(SystemExit):
        main(["--root", str(root)])
    assert "forbidden release text: data/CREDENTIALS" in capsys.readouterr().out


@pytest.mark.parametrize("suffix", ["obj", "dat", "secret"])
def test_validator_sniffs_unlisted_text_suffixes(tmp_path: Path, capsys: pytest.CaptureFixture[str], suffix: str) -> None:
    root = tmp_path / "release"
    data = root / "data"
    data.mkdir(parents=True)
    (data / "README.md").write_text("Data.\n", encoding="utf-8")
    (data / f"payload.{suffix}").write_text('"api_' + 'key": "literal-value"\n', encoding="utf-8")
    with pytest.raises(SystemExit):
        main(["--root", str(root)])
    assert f"forbidden release text: data/payload.{suffix}" in capsys.readouterr().out


@pytest.mark.parametrize("name", ["payload.dat", "CREDENTIALS", "payload.png"])
def test_validator_rejects_binary_embedded_credential(tmp_path: Path, capsys: pytest.CaptureFixture[str], name: str) -> None:
    root = tmp_path / "release"
    data = root / "data"
    data.mkdir(parents=True)
    (data / "README.md").write_text("Data.\n", encoding="utf-8")
    (data / name).write_bytes(b"\x00binary\napi_" + b"key: literal-value\n")
    with pytest.raises(SystemExit):
        main(["--root", str(root)])
    assert f"forbidden release bytes: data/{name}" in capsys.readouterr().out


def test_validator_rejects_binary_embedded_private_path(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = tmp_path / "release"
    data = root / "data"
    data.mkdir(parents=True)
    (data / "README.md").write_text("Data.\n", encoding="utf-8")
    (data / "payload.dat").write_bytes(b"\x00binary\n/home" + b"/privateperson/data\n")
    with pytest.raises(SystemExit):
        main(["--root", str(root)])
    assert "forbidden release bytes: data/payload.dat" in capsys.readouterr().out


def test_validator_rejects_nul_prefixed_bare_token(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = tmp_path / "release"
    data = root / "data"
    data.mkdir(parents=True)
    (data / "README.md").write_text("Data.\n", encoding="utf-8")
    candidate = "".join(("aB7cD8eF", "9gH0iJ1k", "L2mN3oP4", "qR5sT6uV", "7wX8yZ9A"))
    (data / "payload.dat").write_bytes(b"\x00binary\n" + candidate.encode() + b"\n")
    with pytest.raises(SystemExit):
        main(["--root", str(root)])
    assert "possible high-entropy secret in bytes: data/payload.dat" in capsys.readouterr().out
