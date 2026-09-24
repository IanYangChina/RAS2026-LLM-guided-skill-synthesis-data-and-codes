# Simulation

The simulation package assembles task scenes, runs compiled controllers in
MuJoCo, captures contact and pose telemetry, and supports bounded-memory MP4
and GIF rendering. The reference embodiment is a Franka Emika Panda with a
parallel gripper.

`MuJoCoBackend` is the scientific backend. `MockSimulatorBackend` is intended
for import, parser, and output-shape smoke tests only; mock scores must not be
used as paper evidence. Headless rendering on Linux may require
`MUJOCO_GL=osmesa`.

Scene configuration banks are ordered and hashed. Replay should activate the
recorded configuration index instead of selecting a scene by score.
Third-party asset terms are listed in the repository-level
[`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md).
