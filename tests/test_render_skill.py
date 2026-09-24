from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest
ARCHIVE_ROOT = Path(__file__).resolve().parents[1]
if str(ARCHIVE_ROOT) not in sys.path:
    sys.path.insert(0, str(ARCHIVE_ROOT))
from simulation import public_renderer
from simulation.public_renderer import RenderInputError, _Cadence, _FrameSink

def _fixture_archive(tmp_path: Path) -> Path:
    (tmp_path / 'data' / 'skills').mkdir(parents=True)
    (tmp_path / 'data' / 'parameters').mkdir()
    (tmp_path / 'data' / 'scenes').mkdir()
    (tmp_path / 'data' / 'skills' / 'demo.yaml').write_text('skill: demo\n', encoding='utf-8')
    (tmp_path / 'data' / 'parameters' / 'demo.json').write_text('{"phase.duration": 1}', encoding='utf-8')
    (tmp_path / 'data' / 'scenes' / 'demo.json').write_text(json.dumps({'scenes': [{'scene_config': {'robot': 'panda', 'gripper': None, 'object_xml': None}}]}), encoding='utf-8')
    return tmp_path

def test_explicit_resolution_is_deterministic(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _fixture_archive(tmp_path)
    monkeypatch.setattr(public_renderer, 'archive_root', lambda : root)
    spec = public_renderer.resolve_spec(task='demo', skill='data/skills/demo.yaml', parameters='data/parameters/demo.json', scene_bank='data/scenes/demo.json')
    assert spec.task == 'demo'
    assert spec.scene_index == 0
    assert spec.parameters == {'phase.duration': 1.0}

def test_catalog_record_resolution_and_scene_index(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _fixture_archive(tmp_path)
    (root / 'data' / 'catalog.csv').write_text('record_id,task,skill_path,parameters_path,scene_bank_path\ndemo-0,demo,data/skills/demo.yaml,data/parameters/demo.json,data/scenes/demo.json\n', encoding='utf-8')
    monkeypatch.setattr(public_renderer, 'archive_root', lambda : root)
    spec = public_renderer.resolve_spec(record_id='demo-0')
    assert spec.record_id == 'demo-0'
    assert spec.skill_path.name == 'demo.yaml'

def test_explicit_inputs_and_output_validation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _fixture_archive(tmp_path)
    monkeypatch.setattr(public_renderer, 'archive_root', lambda : root)
    with pytest.raises(RenderInputError, match='inside the archive'):
        public_renderer.resolve_spec(task='demo', skill=Path('/tmp/not-archived.yaml'), parameters='data/parameters/demo.json', scene_bank='data/scenes/demo.json')
    spec = public_renderer.resolve_spec(task='demo', skill='data/skills/demo.yaml', parameters='data/parameters/demo.json', scene_bank='data/scenes/demo.json')
    with pytest.raises(RenderInputError, match='must not be written'):
        public_renderer.render_spec(spec, root / 'data' / 'bad.gif')

def test_scene_index_bounds(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _fixture_archive(tmp_path)
    monkeypatch.setattr(public_renderer, 'archive_root', lambda : root)
    with pytest.raises(RenderInputError, match='outside scene bank'):
        public_renderer.resolve_spec(task='demo', skill='data/skills/demo.yaml', parameters='data/parameters/demo.json', scene_bank='data/scenes/demo.json', scene_index=1)


def test_cadence_matches_simulation_time_without_duplicate_samples() -> None:
    cadence = _Cadence(10)
    times = [0.0, 0.02, 0.10, 0.11, 0.20, 0.21]
    assert [cadence.due(time) for time in times] == [True, False, True, False, True, False]


def test_gif_sink_bounds_frames_and_enforces_size(tmp_path: Path) -> None:
    output = tmp_path / "large.gif"
    sink = _FrameSink(output, fps=15, max_gif_bytes=100, max_gif_frames=8)
    sink.__enter__()
    for _ in range(20):
        sink.add(np.random.default_rng(4).integers(0, 256, (32, 32, 3), dtype=np.uint8))
    assert len(sink._gif_frames) <= 8
    assert sink.count == 20
    with pytest.raises(RenderInputError, match="GIF exceeds"):
        sink.close()
    assert not output.exists()


def test_gif_thinning_preserves_simulated_duration(tmp_path: Path) -> None:
    from PIL import Image

    output = tmp_path / "thinned.gif"
    sink = _FrameSink(output, fps=10, max_gif_bytes=10 * 1024 * 1024, max_gif_frames=2)
    sink.__enter__()
    frame = np.zeros((8, 8, 3), dtype=np.uint8)
    for index in range(10):
        sink.add(frame, timestamp=index / 10.0)
    sink.set_finish_time(1.0)
    sink.close()
    image = Image.open(output)
    total_duration = 0
    try:
        for _ in range(image.n_frames):
            total_duration += int(image.info.get("duration", 0))
            image.seek(image.tell() + 1)
    except EOFError:
        pass
    # GIF durations are integer milliseconds; permit one frame's rounding.
    assert abs(total_duration / 1000.0 - 1.0) <= 0.02


def test_frame_sink_rejects_unknown_format(tmp_path: Path) -> None:
    with pytest.raises(RenderInputError, match="must end"):
        _FrameSink(tmp_path / "trajectory.webm", fps=15, max_gif_bytes=1000).__enter__()
