from __future__ import annotations

import os
import tempfile
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import mujoco

from simulation.assets import OBJECTS_DIR, ROBOTS_DIR

ROBOT_REGISTRY: dict[str, Path] = {
    "panda": ROBOTS_DIR / "franka_emika_panda" / "panda_nohand.xml",
    "panda_full": ROBOTS_DIR / "franka_emika_panda" / "panda.xml",
    "panda_pusher": ROBOTS_DIR / "franka_emika_panda" / "panda_with_pusher.xml",
    "panda_peg": ROBOTS_DIR / "franka_emika_panda" / "panda_with_peg.xml",
}
GRIPPER_REGISTRY: dict[str, Path] = {"franka_hand": ROBOTS_DIR / "franka_emika_panda" / "hand.xml"}
OBJECT_REGISTRY: dict[str, Path] = {name: OBJECTS_DIR / f"{name}.xml" for name in ("push_box", "obstacle_block", "grasp_target", "grasp_target_box", "peg_channel", "peg_socket", "door")}
_COMBINED_ROBOT_GRIPPER: dict[tuple[str, str], str] = {("panda", "franka_hand"): "panda_full"}

# MuJoCo actuator names for the bundled Franka hand.  The public executor
# uses this map when opening or closing the gripper during grasp-and-place
# replays.
GRIPPER_ACTUATOR_NAMES: dict[str, list[str]] = {
    "franka_hand": ["actuator8"],
}


@dataclass(frozen=True)
class SceneConfig:
    robot: str
    gripper: Optional[str]
    object_xml: Optional[str]
    target_markers: tuple = field(default=())
    tcp_markers: tuple = field(default=())


_TEMPLATE = textwrap.dedent("""<mujoco model="scene"><option gravity="0 0 -9.81"/>{includes}<worldbody><light pos="0 0 3" dir="0 0 -1"/><geom name="table" type="box" size="0.8 0.8 0.02" pos="0 0 -0.02"/>{markers}</worldbody></mujoco>""")


def _object_path(value: str) -> Path:
    return OBJECT_REGISTRY[value] if value in OBJECT_REGISTRY else Path(value).resolve()


def build_scene(config: SceneConfig) -> "mujoco.MjModel":
    if config.robot not in ROBOT_REGISTRY or config.gripper not in (None, *GRIPPER_REGISTRY):
        raise ValueError("scene configuration requests an asset not included in this public archive")
    combined = _COMBINED_ROBOT_GRIPPER.get((config.robot, config.gripper))
    if combined:
        return build_scene(SceneConfig(combined, None, config.object_xml, config.target_markers, config.tcp_markers))
    robot = ROBOT_REGISTRY[config.robot]
    includes = f'<include file="{robot.name}"/>'
    markers = "".join(f'<body name="target_marker_{index}" pos="{float(position[0])} {float(position[1])} {float(position[2])}"><geom type="sphere" size="0.02" contype="0" conaffinity="0"/></body>' for index, position in enumerate(config.target_markers))
    if config.gripper:
        includes += f'<include file="{GRIPPER_REGISTRY[config.gripper]}"/>'
    if config.object_xml:
        includes += f'<include file="{_object_path(config.object_xml)}"/>'
    path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", dir=robot.parent, delete=False, prefix="public_scene_") as handle:
            handle.write(_TEMPLATE.format(includes=includes, markers=markers))
            path = handle.name
        return mujoco.MjModel.from_xml_path(path)
    except Exception as exc:
        raise RuntimeError(f"MuJoCo scene construction failed: {exc}") from exc
    finally:
        if path and os.path.exists(path):
            os.unlink(path)


def list_robots() -> list[str]: return sorted(ROBOT_REGISTRY)
def list_grippers() -> list[str]: return sorted(GRIPPER_REGISTRY)
def list_objects() -> list[str]: return sorted(OBJECT_REGISTRY)
