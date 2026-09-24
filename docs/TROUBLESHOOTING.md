# Troubleshooting

## Conda cannot solve the environment

Use a recent Conda or Micromamba, remove only the newly created environment,
and retry from the supplied environment file. Do not mix system Python with
the archive's editable install. Capture `conda list` when reporting a failure.

## MuJoCo cannot create a GL context

For headless Linux, set `MUJOCO_GL=osmesa` before starting Python. A mock
backend run can verify the public data flow without a display. Interactive
viewers require a working display server and are not part of the exact
reanalysis path.

## A catalog record is missing

Run `python scripts/validate_archive.py --root . --strict`. Check the relative
path and SHA-256 value in `data/catalog.csv`; do not hand-edit a score or point
to a development checkout. The public archive intentionally fails closed when
scientific inputs are incomplete.

## Rendering fails

Confirm that the skill YAML, parameter JSON, scene-bank JSON, and requested
scene index belong to the same task and record. Use `--dry-run` where available,
then try MP4 before GIF if the size cap is exceeded. A GIF larger than 10 MiB
should be regenerated at a lower size or retained as MP4.

## LLM call fails

Check that `DEEPSEEK_API_KEY` exists only in the current process environment,
that the endpoint/model override is intentional, and that the provider is
reachable. Start with one low-budget call. Never paste the key or a complete
environment dump into an issue or log. Exact reanalysis does not need an LLM.
