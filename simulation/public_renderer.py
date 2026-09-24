"""Catalog resolution and lightweight trajectory rendering for the public archive."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


class RenderInputError(ValueError):
    """Raised when a catalog row or explicit render input is invalid."""


@dataclass(frozen=True)
class RenderSpec:
    """Fully resolved inputs for one deterministic render."""

    record_id: str
    task: str
    skill_path: Path
    parameters: dict[str, float]
    scene_bank_path: Path
    scene_index: int
    scene: dict[str, Any]
    metadata: Mapping[str, Any]


class _FrameSink:
    """Bounded-memory output sink for one trajectory.

    MP4 frames are handed directly to imageio's ffmpeg writer. GIF output is
    intentionally bounded to a small palette-optimised frame list and is
    reduced online when a long simulation exceeds the cap. Each GIF frame
    carries its simulation timestamp; thinning recomputes durations from the
    retained timestamps, preserving total playback time to GIF millisecond
    rounding (the tests allow 20 ms).
    """

    def __init__(
        self,
        output: Path,
        *,
        fps: int,
        max_gif_bytes: int,
        max_gif_frames: int = 180,
    ) -> None:
        self.output = output
        self.fps = fps
        self.max_gif_bytes = max_gif_bytes
        self.max_gif_frames = max(2, max_gif_frames)
        self.count = 0
        self._writer: Any = None
        self._gif_frames: list[Any] = []
        self._gif_timestamps: list[float] = []
        self._finish_time: float | None = None

    def __enter__(self) -> "_FrameSink":
        self.output.parent.mkdir(parents=True, exist_ok=True)
        if self.output.suffix.lower() == ".mp4":
            try:
                import imageio.v2 as imageio

                self._writer = imageio.get_writer(
                    self.output, fps=self.fps, codec="libx264", macro_block_size=None
                )
            except Exception as exc:
                raise RuntimeError(
                    "writing MP4 requires imageio and an ffmpeg/libx264 backend"
                ) from exc
        elif self.output.suffix.lower() != ".gif":
            raise RenderInputError("output must end in .mp4 or .gif")
        return self

    def add(self, frame: Any, *, timestamp: float | None = None) -> None:
        if self._writer is not None:
            self._writer.append_data(frame)
        else:
            from PIL import Image

            # Palette conversion at capture time avoids retaining a second RGB
            # copy and makes GIF output substantially smaller.
            image = Image.fromarray(frame).convert(
                "P", palette=Image.Palette.ADAPTIVE, colors=128
            )
            if len(self._gif_frames) >= self.max_gif_frames:
                # Keep a representative prefix while bounding memory and
                # making long trajectories visibly playable.
                self._gif_frames = self._gif_frames[::2]
                self._gif_timestamps = self._gif_timestamps[::2]
            if timestamp is None:
                timestamp = (
                    self._gif_timestamps[-1] + (1.0 / self.fps)
                    if self._gif_frames
                    else 0.0
                )
            self._gif_frames.append(image)
            self._gif_timestamps.append(float(timestamp))
        self.count += 1

    def set_finish_time(self, timestamp: float) -> None:
        """Set the simulation end time used for the final GIF frame duration."""

        self._finish_time = float(timestamp)

    def close(self) -> None:
        try:
            if self._writer is not None:
                self._writer.close()
                self._writer = None
                return
            if not self._gif_frames:
                raise RuntimeError("simulation produced no frames")
            frames = self._gif_frames
            timestamps = self._gif_timestamps
            while True:
                # GIF stores frame durations in centiseconds.  Quantize the
                # cumulative trajectory timestamps, rather than rounding each
                # interval independently; this preserves elapsed time as the
                # expected 60/70 ms alternation for a 15-fps stream.
                origin = timestamps[0]
                target_end = origin + (len(timestamps) / self.fps)
                end_time = max(self._finish_time or 0.0, target_end)
                if end_time <= timestamps[-1]:
                    end_time = timestamps[-1] + (1.0 / self.fps)
                boundaries = [0]
                for timestamp in (*timestamps[1:], end_time):
                    quantized = round(100.0 * (timestamp - origin))
                    boundaries.append(max(quantized, boundaries[-1] + 1))
                durations = [
                    10 * (boundaries[index + 1] - boundaries[index])
                    for index in range(len(boundaries) - 1)
                ]
                frames[0].save(
                    self.output,
                    save_all=True,
                    append_images=frames[1:],
                    duration=durations,
                    loop=0,
                    # Keep one timing-bearing GIF frame per sampled
                    # trajectory state.  Pillow's palette optimiser can
                    # collapse repeated frames to zero-duration entries,
                    # which makes the advertised 15 fps playback unreliable.
                    optimize=False,
                    disposal=2,
                )
                if self.output.stat().st_size <= self.max_gif_bytes:
                    return
                if len(frames) <= 2:
                    break
                frames = frames[::2]
                timestamps = timestamps[::2]
            raise RenderInputError(
                f"GIF exceeds the {self.max_gif_bytes / 1024 / 1024:.1f} MiB limit; "
                "use --width/--height to reduce resolution or request MP4"
            )
        finally:
            if self._writer is not None:
                self._writer.close()
                self._writer = None
            if self.output.exists() and self.output.suffix.lower() == ".gif":
                # A failed size check must never leave an invalid deliverable.
                try:
                    if self.output.stat().st_size > self.max_gif_bytes:
                        self.output.unlink()
                except OSError:
                    pass

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        if exc_type is None:
            self.close()
        elif self._writer is not None:
            self._writer.close()
            self._writer = None
        if exc_type is not None and self.output.exists():
            try:
                self.output.unlink()
            except OSError:
                pass


class _Cadence:
    """Select at most one frame per requested simulation-time sample."""

    def __init__(self, fps: int) -> None:
        self.period = 1.0 / float(fps)
        self.next_time = 0.0

    def due(self, simulation_time: float) -> bool:
        if simulation_time + 1e-12 < self.next_time:
            return False
        self.next_time += self.period
        while self.next_time <= simulation_time:
            self.next_time += self.period
        return True


def archive_root() -> Path:
    """Return the extracted archive root (the directory above this module)."""

    return Path(__file__).resolve().parents[1]


def _inside(root: Path, path: Path, label: str) -> Path:
    resolved = path.expanduser().resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise RenderInputError(f"{label} must be inside the archive: {path}") from exc
    if not resolved.is_file():
        raise RenderInputError(f"{label} does not exist: {path}")
    return resolved


def _path(root: Path, value: str | Path, label: str) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = root / candidate
    return _inside(root, candidate, label)


def _json_value(root: Path, value: Any, label: str) -> Any:
    """Read an inline JSON value or an archive-relative JSON file."""

    if isinstance(value, (dict, list)):
        return value
    if value is None or not str(value).strip():
        raise RenderInputError(f"{label} is required")
    text = str(value).strip()
    candidate = root / text
    if candidate.is_file():
        path = _inside(root, candidate, label)
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise RenderInputError(f"{label} must contain valid JSON: {path}: {exc}") from exc
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise RenderInputError(
            f"{label} must be an archive-relative JSON file or inline JSON"
        ) from exc


def _row_value(row: Mapping[str, str], *names: str) -> str | None:
    for name in names:
        value = row.get(name)
        if value is not None and value.strip():
            return value.strip()
    return None


def read_catalog(catalog_path: Path | None = None) -> list[dict[str, str]]:
    """Read the neutral CSV catalog and require its stable identifier column."""

    root = archive_root()
    path = catalog_path or root / "data" / "catalog.csv"
    path = _inside(root, path, "catalog")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or "record_id" not in reader.fieldnames:
            raise RenderInputError("catalog must contain a 'record_id' column")
        rows = [dict(row) for row in reader]
    if not rows:
        raise RenderInputError(f"catalog contains no records: {path}")
    return rows


def resolve_catalog_record(record_id: str, catalog_path: Path | None = None) -> dict[str, str]:
    """Resolve one stable record ID, rejecting duplicate IDs."""

    rows = read_catalog(catalog_path)
    matches = [row for row in rows if row.get("record_id") == record_id]
    if not matches:
        examples = ", ".join(row.get("record_id", "") for row in rows[:5])
        raise RenderInputError(
            f"record_id {record_id!r} not found in catalog (examples: {examples})"
        )
    if len(matches) != 1:
        raise RenderInputError(f"catalog contains duplicate record_id {record_id!r}")
    return matches[0]


def _parameters(root: Path, value: Any) -> dict[str, float]:
    payload = _json_value(root, value, "parameters")
    if isinstance(payload, Mapping):
        for key in ("parameters", "parameter_values", "best_params", "params"):
            if isinstance(payload.get(key), Mapping):
                payload = payload[key]
                break
    if not isinstance(payload, Mapping):
        raise RenderInputError("parameters must decode to a JSON object")
    try:
        result = {str(key): float(number) for key, number in payload.items()}
    except (TypeError, ValueError) as exc:
        raise RenderInputError("parameters must map names to finite numbers") from exc
    if not all(map(lambda number: number == number and abs(number) != float("inf"), result.values())):
        raise RenderInputError("parameters must map names to finite numbers")
    return result


def _scene_entry(bank_path: Path, index: int) -> dict[str, Any]:
    try:
        payload = json.loads(bank_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RenderInputError(f"scene bank must contain valid JSON: {bank_path}") from exc
    entries = (
        payload.get("configurations", payload.get("scenes", payload))
        if isinstance(payload, Mapping)
        else payload
    )
    if not isinstance(entries, list):
        raise RenderInputError("scene bank must contain a 'configurations' or 'scenes' list")
    if index < 0 or index >= len(entries):
        raise RenderInputError(f"scene-index {index} is outside scene bank size {len(entries)}")
    entry = entries[index]
    if not isinstance(entry, Mapping):
        raise RenderInputError(f"scene bank entry {index} is not an object")
    return dict(entry)


def _validated_public_normalized_configuration(
    root: Path,
    spec: RenderSpec,
    bank_payload: Mapping[str, Any],
    model: Any,
) -> Mapping[str, Any]:
    """Validate and return one normalized release scene configuration.

    Normalized scene banks preserve the original experiment configuration
    hashes, but their public schema label prevents the strict typed loader from
    recomputing those historical hashes.  This compatibility path is therefore
    deliberately narrow: it is available only for a catalog record with a
    matching public provenance row, matching winner evidence, and a complete
    backend state whose dimensions fit the constructed MuJoCo model.
    """

    if spec.record_id == "explicit" or not spec.metadata:
        raise RenderInputError("normalized scene banks require a catalog record")
    def _sha256(value: Any) -> bool:
        return isinstance(value, str) and len(value) == 64 and all(
            character in "0123456789abcdef" for character in value
        )

    if bank_payload.get("schema_version") != "paper-release":
        raise RenderInputError("unsupported normalized scene-bank schema")
    if not _sha256(bank_payload.get("configuration_bank_sha256")):
        raise RenderInputError("normalized scene-bank embedded hash is invalid")
    if bank_payload.get("task_name") != spec.task:
        raise RenderInputError("normalized scene-bank task does not match catalog")
    try:
        outer_seed = int(bank_payload["outer_seed"])
        expected_seed = int(spec.metadata["seed"])
        config_count = int(bank_payload["k_runs"])
    except (KeyError, TypeError, ValueError) as exc:
        raise RenderInputError("normalized scene-bank metadata is incomplete") from exc
    if outer_seed != expected_seed:
        raise RenderInputError("normalized scene-bank seed does not match catalog")
    configurations = bank_payload.get("configurations")
    if not isinstance(configurations, list) or config_count != len(configurations) or not configurations:
        raise RenderInputError("normalized scene-bank configuration count is invalid")
    if spec.scene_index < 0 or spec.scene_index >= len(configurations):
        raise RenderInputError("normalized scene-bank index is outside the bank")

    bank_relative = spec.scene_bank_path.relative_to(root).as_posix()
    provenance_path = root / "data/provenance/normalized_file_provenance.csv"
    if not provenance_path.is_file():
        raise RenderInputError("normalized scene-bank provenance is missing")
    with provenance_path.open(newline="", encoding="utf-8") as handle:
        provenance_rows = list(csv.DictReader(handle))
    evidence = next(
        (
            row
            for row in provenance_rows
            if row.get("cell_id") == spec.record_id
            and row.get("role") == "scene_bank"
            and row.get("public_path") == bank_relative
        ),
        None,
    )
    if evidence is None:
        raise RenderInputError("normalized scene-bank provenance does not identify this record")
    public_hash = hashlib.sha256(spec.scene_bank_path.read_bytes()).hexdigest()
    if evidence.get("public_sha256") != public_hash:
        raise RenderInputError("normalized scene-bank public hash mismatch")
    if not _sha256(evidence.get("original_sha256")) or not _sha256(evidence.get("public_sha256")):
        raise RenderInputError("normalized scene-bank source evidence is incomplete")
    normalization_path = root / "data/provenance/normalization.json"
    try:
        normalization = json.loads(normalization_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RenderInputError("normalization declaration is missing or invalid") from exc
    if not isinstance(normalization, Mapping) or not normalization.get("declaration"):
        raise RenderInputError("normalization declaration is incomplete")

    expected_entry_hashes: list[str] = []
    try:
        cell = json.loads((root / spec.metadata["cell_record_path"]).read_text(encoding="utf-8"))
        run_log = json.loads((root / spec.metadata["run_log_path"]).read_text(encoding="utf-8"))
        if spec.metadata.get("study") == "expert":
            expected_entry_hashes = [str(value) for value in run_log["configuration_sha256"]]
        else:
            winner_index = int(cell["winner_entry_index"])
            winner = run_log[winner_index]
            expected_entry_hashes = [
                str(value["configuration_sha256"])
                for value in winner["posthoc_diagnostics"]["randomised_config_results"]
            ]
    except (KeyError, IndexError, TypeError, ValueError, OSError, json.JSONDecodeError) as exc:
        raise RenderInputError("normalized scene-bank winner evidence is incomplete") from exc
    if len(expected_entry_hashes) != len(configurations) or any(
        not _sha256(value) for value in expected_entry_hashes
    ):
        raise RenderInputError("normalized scene-bank winner hashes are incomplete")
    actual_entry_hashes = [str(value.get("configuration_sha256", "")) for value in configurations]
    if any(not _sha256(value) for value in actual_entry_hashes):
        raise RenderInputError("normalized scene-bank embedded configuration hash is invalid")
    if actual_entry_hashes != expected_entry_hashes:
        raise RenderInputError("normalized scene-bank configuration evidence mismatch")

    configuration = configurations[spec.scene_index]
    if not isinstance(configuration, Mapping):
        raise RenderInputError("normalized scene-bank configuration is not an object")
    if configuration.get("schema_version") != "paper-release":
        raise RenderInputError("normalized scene-bank configuration schema is invalid")
    if configuration.get("config_index") != spec.scene_index:
        raise RenderInputError("normalized scene-bank configuration index mismatch")
    if configuration.get("seed") != outer_seed + spec.scene_index:
        raise RenderInputError("normalized scene-bank configuration seed mismatch")
    if not _sha256(configuration.get("realized_scene_sha256")):
        raise RenderInputError("normalized scene-bank embedded scene hash is invalid")
    realized_scene = configuration.get("realized_scene")
    if not isinstance(realized_scene, Mapping) or realized_scene.get("task_name") != spec.task:
        raise RenderInputError("normalized scene-bank realized scene does not match task")
    state = configuration.get("backend_state")
    if not isinstance(state, Mapping) or state.get("scene_frozen") is not True:
        raise RenderInputError("normalized scene-bank backend state is not frozen")
    qpos_delta = state.get("qpos_delta")
    if (
        not isinstance(qpos_delta, list)
        or len(qpos_delta) != int(model.nq)
        or not all(isinstance(value, (int, float)) and math.isfinite(float(value)) for value in qpos_delta)
    ):
        raise RenderInputError("normalized scene-bank qpos dimensions are invalid")
    body_deltas = state.get("body_deltas")
    if not isinstance(body_deltas, Mapping):
        raise RenderInputError("normalized scene-bank body deltas are invalid")
    for body_id, delta in body_deltas.items():
        try:
            valid_body = 0 <= int(body_id) < int(model.nbody)
        except (TypeError, ValueError):
            valid_body = False
        if (
            not valid_body
            or not isinstance(delta, list)
            or len(delta) != 3
            or not all(isinstance(value, (int, float)) and math.isfinite(float(value)) for value in delta)
        ):
            raise RenderInputError("normalized scene-bank body dimensions are invalid")
    return configuration


def _validated_reconstructed_configuration(
    root: Path,
    spec: RenderSpec,
    bank_payload: Mapping[str, Any],
    model: Any,
) -> Mapping[str, Any]:
    """Validate one provenance-backed scene bank reconstructed from run logs.

    These 540 public banks intentionally have no source configuration hashes
    or realized-scene snapshots.  They are accepted only when the dedicated
    provenance row binds every frozen backend value to the source run-log
    ``randomisation_debug`` evidence.
    """

    def _finite_vector(value: Any, size: int) -> bool:
        return isinstance(value, list) and len(value) == size and all(
            isinstance(item, (int, float)) and math.isfinite(float(item)) for item in value
        )

    if spec.record_id == "explicit" or not spec.metadata:
        raise RenderInputError("reconstructed scene banks require a catalog record")
    if bank_payload.get("schema_version") != "paper-release":
        raise RenderInputError("unsupported reconstructed scene-bank schema")
    if bank_payload.get("task_name") != spec.task:
        raise RenderInputError("reconstructed scene-bank task does not match catalog")
    try:
        outer_seed = int(bank_payload["outer_seed"])
        expected_seed = int(spec.metadata["seed"])
        config_count = int(bank_payload["k_runs"])
    except (KeyError, TypeError, ValueError) as exc:
        raise RenderInputError("reconstructed scene-bank metadata is incomplete") from exc
    if outer_seed != expected_seed:
        raise RenderInputError("reconstructed scene-bank seed does not match catalog")
    configurations = bank_payload.get("configurations")
    if not isinstance(configurations, list) or config_count != len(configurations) or not configurations:
        raise RenderInputError("reconstructed scene-bank configuration count is invalid")
    if spec.scene_index < 0 or spec.scene_index >= len(configurations):
        raise RenderInputError("reconstructed scene-bank index is outside the bank")

    bank_relative = spec.scene_bank_path.relative_to(root).as_posix()
    provenance_path = root / "data/provenance/reconstructed_scene_banks.csv"
    if not provenance_path.is_file():
        raise RenderInputError("reconstructed scene-bank provenance is missing")
    with provenance_path.open(newline="", encoding="utf-8") as handle:
        provenance_rows = list(csv.DictReader(handle))
    evidence = next(
        (
            row
            for row in provenance_rows
            if row.get("cell_id") == spec.record_id and row.get("public_path") == bank_relative
        ),
        None,
    )
    if evidence is None:
        raise RenderInputError("reconstructed scene-bank provenance does not identify this record")
    public_hash = hashlib.sha256(spec.scene_bank_path.read_bytes()).hexdigest()
    if evidence.get("public_sha256") != public_hash:
        raise RenderInputError("reconstructed scene-bank public hash mismatch")
    if not evidence.get("source_container_path") or not evidence.get("source_container_original_sha256"):
        raise RenderInputError("reconstructed scene-bank source evidence is incomplete")
    source_path = root / evidence["source_container_path"]
    # The provenance paths are rooted at data/; reject traversal and require
    # the source container named by the catalog row as well.
    try:
        source_path = source_path.resolve()
        source_path.relative_to(root.resolve())
    except ValueError as exc:
        raise RenderInputError("reconstructed source container is outside the archive") from exc
    normalized_provenance_path = root / "data/provenance/normalized_file_provenance.csv"
    if not normalized_provenance_path.is_file():
        raise RenderInputError("normalized source-container provenance is missing")
    with normalized_provenance_path.open(newline="", encoding="utf-8") as handle:
        normalized_rows = list(csv.DictReader(handle))
    normalized_source = next(
        (
            row
            for row in normalized_rows
            if row.get("cell_id") == spec.record_id
            and row.get("role") == "run_log"
            and row.get("public_path") == evidence["source_container_path"]
        ),
        None,
    )
    if normalized_source is None or normalized_source.get("original_sha256") != evidence["source_container_original_sha256"]:
        raise RenderInputError("reconstructed source-container provenance mismatch")
    if not source_path.is_file() or hashlib.sha256(source_path.read_bytes()).hexdigest() != normalized_source.get("public_sha256"):
        raise RenderInputError("reconstructed source container hash mismatch")
    if evidence.get("source_container_path") != spec.metadata.get("run_log_path", ""):
        raise RenderInputError("reconstructed source container does not match catalog")
    if evidence.get("evidence_field") != "posthoc_diagnostics.randomised_config_results[*].randomisation_debug":
        raise RenderInputError("reconstructed provenance evidence declaration is invalid")
    if not evidence.get("derivation", "").strip():
        raise RenderInputError("reconstructed provenance derivation is missing")
    if int(evidence.get("configuration_count", -1)) != len(configurations):
        raise RenderInputError("reconstructed provenance configuration count mismatch")
    declared_hashes = evidence.get("configuration_sha256s", "").split("|")
    if len(declared_hashes) != len(configurations) or any(value not in {"", "None"} for value in declared_hashes):
        raise RenderInputError("reconstructed provenance hash declaration is invalid")

    try:
        cell = json.loads((root / spec.metadata["cell_record_path"]).read_text(encoding="utf-8"))
        run_log = json.loads((root / spec.metadata["run_log_path"]).read_text(encoding="utf-8"))
        entry_index = int(evidence["entry_index"])
        entry = run_log[entry_index]
        if str(entry.get("iteration")) != str(evidence["entry_iteration"]):
            raise ValueError("entry iteration mismatch")
        if str(cell.get("record_id")) != spec.record_id:
            raise ValueError("cell record mismatch")
        source_results = entry["posthoc_diagnostics"]["randomised_config_results"]
    except (KeyError, IndexError, TypeError, ValueError, OSError, json.JSONDecodeError) as exc:
        raise RenderInputError("reconstructed run-log evidence is incomplete") from exc
    if not isinstance(source_results, list) or len(source_results) != len(configurations):
        raise RenderInputError("reconstructed run-log configuration count mismatch")

    for index, (configuration, source) in enumerate(zip(configurations, source_results)):
        if not isinstance(configuration, Mapping) or not isinstance(source, Mapping):
            raise RenderInputError("reconstructed configuration evidence is not an object")
        if configuration.get("schema_version") != "paper-release":
            raise RenderInputError("reconstructed configuration schema is invalid")
        if configuration.get("configuration_sha256") not in {None, ""} or configuration.get("realized_scene") is not None or configuration.get("realized_scene_sha256") not in {None, ""}:
            raise RenderInputError("reconstructed configuration must not invent hashes or snapshots")
        source_index = source.get("configuration_index", source.get("run_index"))
        source_seed = source.get("configuration_seed", source.get("seed"))
        if configuration.get("config_index") != index or configuration.get("config_index") != source_index:
            raise RenderInputError("reconstructed configuration index mismatch")
        if configuration.get("seed") != source_seed:
            raise RenderInputError("reconstructed configuration seed mismatch")
        state = configuration.get("backend_state")
        debug = source.get("randomisation_debug")
        if not isinstance(state, Mapping) or not isinstance(debug, Mapping):
            raise RenderInputError("reconstructed backend evidence is incomplete")
        if state.get("scene_frozen") is not True or debug.get("scene_frozen") is not True:
            raise RenderInputError("reconstructed backend state is not frozen")
        if state.get("body_deltas") != debug.get("frozen_body_deltas") or state.get("qpos_delta") != debug.get("frozen_qpos_delta"):
            raise RenderInputError("reconstructed backend evidence mismatch")
        qpos_delta = state.get("qpos_delta")
        if not _finite_vector(qpos_delta, int(model.nq)):
            raise RenderInputError("reconstructed qpos dimensions are invalid")
        body_deltas = state.get("body_deltas")
        if not isinstance(body_deltas, Mapping):
            raise RenderInputError("reconstructed body deltas are invalid")
        for body_id, delta in body_deltas.items():
            try:
                valid_body = 0 <= int(body_id) < int(model.nbody)
            except (TypeError, ValueError):
                valid_body = False
            if not valid_body or not _finite_vector(delta, 3):
                raise RenderInputError("reconstructed body dimensions are invalid")
    return configurations[spec.scene_index]


def resolve_spec(
    *,
    record_id: str | None = None,
    task: str | None = None,
    skill: str | Path | None = None,
    parameters: str | Path | Mapping[str, Any] | None = None,
    scene_bank: str | Path | None = None,
    scene_index: int = 0,
    catalog_path: Path | None = None,
) -> RenderSpec:
    """Resolve catalog or explicit inputs into one :class:`RenderSpec`."""

    root = archive_root()
    row: dict[str, str] = {}
    if record_id:
        row = resolve_catalog_record(record_id, catalog_path)
        task = task or _row_value(row, "task", "task_name")
        skill = skill or _row_value(row, "skill_path", "skill", "skill_yaml")
        parameters = parameters or _row_value(
            row, "parameters_path", "parameters", "best_parameters"
        )
        scene_bank = scene_bank or _row_value(
            row, "scene_bank_path", "scene_bank", "scenes"
        )
        if scene_index == 0 and _row_value(row, "scene_index") is not None:
            scene_index = int(_row_value(row, "scene_index") or 0)
    if not task:
        raise RenderInputError("task is required (or select a catalog record with --record-id)")
    if skill is None:
        raise RenderInputError("skill is required (or select a catalog record with --record-id)")
    if parameters is None:
        raise RenderInputError(
            "parameters are required (or select a catalog record with --record-id)"
        )
    if scene_bank is None:
        raise RenderInputError(
            "scene-bank is required (or select a catalog record with --record-id)"
        )
    skill_path = _path(root, skill, "skill")
    bank_path = _path(root, scene_bank, "scene bank")
    scene = _scene_entry(bank_path, int(scene_index))
    return RenderSpec(
        record_id=record_id or "explicit",
        task=str(task),
        skill_path=skill_path,
        parameters=_parameters(root, parameters),
        scene_bank_path=bank_path,
        scene_index=int(scene_index),
        scene=scene,
        metadata=row,
    )


def render_spec(
    spec: RenderSpec,
    output: Path,
    *,
    fps: int = 15,
    width: int = 640,
    height: int = 480,
    max_gif_bytes: int = 10 * 1024 * 1024,
) -> Path:
    """Execute one archived skill and write a GIF or MP4 outside ``data``."""

    if fps <= 0 or width <= 0 or height <= 0:
        raise RenderInputError("fps, width, and height must be positive")
    if max_gif_bytes <= 0:
        raise RenderInputError("max_gif_bytes must be positive")
    root = archive_root()
    output = output.expanduser().resolve()
    data_root = (root / "data").resolve()
    if output == data_root or data_root in output.parents:
        raise RenderInputError("render output must not be written inside immutable data/")
    os.environ.setdefault("MUJOCO_GL", "egl")
    try:
        import mujoco
        from compiler.codegen import compile as compile_skill
        from dsl.serialiser import load_skill
        from evaluation.task_spec import TaskSpec
        from simulation.mujoco_backend import MuJoCoBackend
        from simulation.realized_scene import (
            RealizedSceneConfigBank,
            activate_realized_scene_configuration,
        )
        from simulation.scene import SceneConfig
        from scripts.task_configs import TASK_CONFIGS
    except ImportError as exc:
        raise RuntimeError(
            "the archive runtime is incomplete; install the documented environment"
        ) from exc

    skill = load_skill(spec.skill_path.read_text(encoding="utf-8"))
    artifact = compile_skill(skill)
    scene_cfg: Any = spec.scene.get("scene_config", spec.scene)
    if (
        (not isinstance(scene_cfg, Mapping) or "robot" not in scene_cfg)
        and (spec.metadata.get("scene_config_json") or spec.metadata.get("scene_config"))
    ):
        scene_cfg = _json_value(
            root,
            spec.metadata.get("scene_config_json") or spec.metadata.get("scene_config"),
            "scene configuration",
        )
    if not isinstance(scene_cfg, Mapping):
        raise RenderInputError("scene entry must contain a scene_config object")
    object_xml = scene_cfg.get("object_xml")
    if object_xml:
        object_text = str(object_xml)
        if object_text.endswith(".xml") or "/" in object_text or "\\" in object_text:
            object_xml = str(_path(root, object_text, "scene object"))
    scene_config = SceneConfig(
        robot=str(scene_cfg.get("robot", "panda")),
        gripper=scene_cfg.get("gripper"),
        object_xml=object_xml,
        target_markers=tuple(tuple(item) for item in scene_cfg.get("target_markers", ())),
        tcp_markers=tuple(tuple(item) for item in scene_cfg.get("tcp_markers", ())),
    )
    backend = MuJoCoBackend(scene_config=scene_config, render=False)
    # Catalog rows point to frozen scene banks rather than duplicating the
    # immutable task protocol in every record.  Start with the public task
    # specification, then let a scene entry provide any explicit overrides.
    task_payload: Any = dict(
        TASK_CONFIGS.get(spec.task, {}).get("task_spec", {})
    )
    task_payload.update(spec.scene.get("task_spec", {}))
    if not task_payload and (spec.metadata.get("task_spec_json") or spec.metadata.get("task_spec")):
        task_payload = _json_value(
            root,
            spec.metadata.get("task_spec_json") or spec.metadata.get("task_spec"),
            "task specification",
        )
    task_spec = TaskSpec(**task_payload) if task_payload else None
    bank_payload = json.loads(spec.scene_bank_path.read_text(encoding="utf-8"))
    if isinstance(bank_payload, Mapping) and "configurations" in bank_payload:
        try:
            bank = RealizedSceneConfigBank.from_dict(bank_payload)
            activate_realized_scene_configuration(backend, bank.configurations[spec.scene_index])
        except (KeyError, TypeError, ValueError, IndexError) as exc:
            # The curated records retain the original configuration and scene
            # hashes, while their public schema labels are normalized for the
            # release.  The explicit validator below is the only compatibility
            # path for that public normalized schema; malformed or incomplete
            # records fail closed.
            try:
                validation_model = backend._get_model()
                configurations = bank_payload.get("configurations")
                reconstructed = isinstance(configurations, list) and bool(configurations) and all(
                    isinstance(item, Mapping)
                    and item.get("configuration_sha256") in {None, ""}
                    and item.get("realized_scene") is None
                    and item.get("realized_scene_sha256") in {None, ""}
                    for item in configurations
                )
                if reconstructed:
                    configuration = _validated_reconstructed_configuration(
                        root, spec, bank_payload, validation_model
                    )
                else:
                    configuration = _validated_public_normalized_configuration(
                        root, spec, bank_payload, validation_model
                    )
                state = configuration["backend_state"]

                class _RecordedConfiguration:
                    def __init__(self, backend_state: Mapping[str, Any]) -> None:
                        self.backend_state = dict(backend_state)

                activate_realized_scene_configuration(
                    backend, _RecordedConfiguration(state)
                )
            except (KeyError, TypeError, ValueError, IndexError, RenderInputError) as fallback_exc:
                raise RenderInputError(
                    f"invalid frozen scene bank: {spec.scene_bank_path}: {exc}"
                ) from fallback_exc
    model = backend._get_model()
    camera = mujoco.MjvCamera()
    camera.type = mujoco.mjtCamera.mjCAMERA_FREE
    camera.azimuth, camera.elevation, camera.distance = 90.0, -15.0, 2.2
    camera.lookat[:] = [0.3, 0.0, 0.4]
    cadence = _Cadence(fps)
    simulation_end = 0.0
    with mujoco.Renderer(model, height, width) as renderer, _FrameSink(
        output, fps=fps, max_gif_bytes=max_gif_bytes
    ) as sink:

        def capture(_model: Any, data: Any) -> None:
            nonlocal simulation_end
            simulation_end = max(simulation_end, float(data.time))
            if cadence.due(float(data.time)):
                renderer.update_scene(data, camera=camera)
                sink.add(renderer.render().copy(), timestamp=float(data.time))

        backend.run_episode(
            artifact=artifact,
            parameter_values=spec.parameters,
            task_spec=task_spec,
            step_callback=capture,
        )
        if sink.count == 0:
            raise RuntimeError("simulation produced no frames")
        sink.set_finish_time(simulation_end)
    return output
