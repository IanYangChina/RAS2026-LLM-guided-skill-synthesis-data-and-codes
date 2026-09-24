# Featured demonstrations

This directory contains one looping GIF for each task in the main automatic
comparison matrix. The winners are selected without hand-picking scenes:

1. keep records with `study=primary` for the task;
2. maximize canonical task score;
3. maximize composite score; and
4. choose the lexicographically smallest stable `record_id` for exact ties.

Each render uses the selected record's skill YAML, parameter map, frozen scene
bank, and scene index `0`. The complete machine-readable selection and render
metadata are in [`manifest.json`](manifest.json). The image files are in
[`gifs/`](gifs/README.md). To reproduce a demonstration from the archive root,
run the command recorded in its manifest entry, for example:

```bash
MUJOCO_GL=osmesa python scripts/render_skill.py \
  --record-id p-random-language-fixed-door_push-seed-03 \
  --output media/demos/gifs/door-push.gif \
  --fps 15 --width 640 --height 480
```

The six GIFs are capped at 10 MiB each and loop indefinitely in compatible
GitHub Markdown viewers.
