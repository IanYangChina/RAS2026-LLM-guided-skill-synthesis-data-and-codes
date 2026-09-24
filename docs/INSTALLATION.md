# Installation and environment

The supported setup uses Conda and Python 3.10.19. From the extracted archive
root:

```bash
conda env create -f environment.yml
conda activate robot-skill-synthesis
python -m pip install -e .
python -c "import mujoco, numpy; print('MuJoCo', mujoco.__version__)"
python scripts/validate_archive.py --root .
```

The environment file pins the runtime dependencies. Keep the environment
isolated from system Python and do not install packages globally. The reference
host was Ubuntu 20.04.6, Intel Core i9-10900X, 125 GiB RAM, and two NVIDIA RTX
2080 Ti GPUs. Validation used Python 3.10.19 and MuJoCo 3.5.0. Physics is
executed on the CPU; GPUs are primarily useful for off-screen rendering.

## Linux headless rendering

MuJoCo needs a native OpenGL path even for off-screen frames. For EGL, check
that the host exposes the EGL and GLES libraries; for OSMesa, check the
software rasterizer:

```bash
ldconfig -p | grep -E 'libEGL\.so|libGLESv2\.so|libOSMesa\.so'
```

On Ubuntu, the usual system packages are `libegl1`, `libgl1`, `libgles2`, and
`libosmesa6` (install the subset required by the selected backend through the
OS package manager). Select a backend before starting Python:

```bash
export MUJOCO_GL=egl       # hardware/driver-backed off-screen rendering
# export MUJOCO_GL=osmesa  # CPU software rendering fallback
conda run -n robot-skill-synthesis python -c \
  "import mujoco; c=mujoco.GLContext(16,16); c.free(); print('MuJoCo GL context: ok')"
```

A context check passing does not validate a task scene; use
`python scripts/render_skill.py --help` followed by a catalogued replay for
that. EGL availability depends on the host driver and container permissions;
OSMesa is slower but avoids requiring a display server. Interactive viewers
need a working display server and are not part of exact reanalysis.

Use the mock backend to check imports and data flow before committing to a
physics run:

```bash
python scripts/run_parameter_optimization.py --backend mock \
  --source expert_reference --task obstacle_reach --seed 0 \
  --cma-budget 2 --basins 1 --episodes 1 --dry-run
```

A real MuJoCo run requires the archived assets and catalog records. If either
is absent, the command should fail with a missing-input message; do not replace
scientific records with generated substitutes.
