# Environment

The archive was validated on Ubuntu 20.04.6 with an Intel i9-10900X CPU,
125 GiB RAM, two NVIDIA RTX 2080 Ti GPUs, Python 3.10.19, and MuJoCo 3.5.0.
Simulation uses the CPU; a GPU is useful primarily for interactive rendering.
Linux on x86_64 is the validated platform. MuJoCo's native dependencies and
headless OpenGL setup can differ on macOS, Windows, containers, and remote
servers.

## Install

From the archive root, create the isolated environment and install the archive
in editable mode:

```bash
conda env create -f environment.yml
conda run -n robot-skill-synthesis python -m pip install --editable .
conda run -n robot-skill-synthesis python environment/validate_install.py
conda run -n robot-skill-synthesis python -m pytest tests/ -x -q
```

`environment.yml` pins the dependencies used for validation. A different
operating system or CPU architecture may require a compatible Conda/Python
build, but should retain the pinned Python package versions.

## LLM configuration

LLM refinement is optional. Exact paper reanalysis, catalog inspection,
parameter optimisation, and rendering do not need network access or an API key.
For a new LLM refinement run, set a key only in your shell:

```bash
read -rs DEEPSEEK_API_KEY; export DEEPSEEK_API_KEY
```

The public runner uses the paper endpoint and model when no override is set.
`OPENAI_COMPATIBLE_BASE_URL` and `OPENAI_COMPATIBLE_MODEL` are optional OpenAI-compatible
methodological overrides. Copy `.env.example` only for tools that load
environment files; it intentionally contains blank values. Do not put a key in
source files, run logs intended for sharing, or version control.

## Validation scope

`validate_install.py` checks pinned import versions, imports the runtime
packages, verifies the executable public scripts can display help, and confirms
that MuJoCo can be imported. It makes no network request. By default it skips
OpenGL context creation so general CI and non-rendering hosts can validate the
runtime portably. To require a minimal 1x1 render, run:

```bash
conda run -n robot-skill-synthesis python environment/validate_install.py --check-render-context
```

This optional check fails with a clear nonzero error if the host lacks a usable
display or OpenGL backend. For headless Linux CI, use
`--headless-render-context` to set `MUJOCO_GL=osmesa` when it is not already
configured and run the same check. Run the test command above for archive-level
tests; full rendering still requires a working display or headless OpenGL/EGL
configuration on the host.
