# Public scripts

Run these entry points from the extracted repository root after activating the
Conda environment:

| Script | Purpose |
|---|---|
| `reproduce_paper_results.py` | Regenerate summaries from the immutable catalog; no API or simulation. |
| `run_structural_search.py` | Run Bandit, MAP-QD, or LLM structural refinement. |
| `run_parameter_optimization.py` | Tune continuous skill parameters with CMA-ES. |
| `render_skill.py` | Render a catalog record or explicit replay as MP4/GIF. |
| `validate_archive.py` | Check hashes, paths, safety rules, directory READMEs, and package membership. |

Use `--help` for the complete interface. Start expensive commands with
`--dry-run`. Scientific commands default to MuJoCo; use `--backend mock` only
for a fast software smoke test. Generated files should go to a separate
output directory, not into the immutable catalog.

## Local release packaging

Maintainers can validate the complete public tree, write `MANIFEST.sha256`, and
create a deterministic sibling ZIP plus its SHA-256 sidecar with:

```bash
python scripts/package_release.py
python scripts/package_release.py --verify-only
```

The parent repository tracks the ZIP with Git LFS; the extracted archive does
not need Git history. The checksum sidecar verifies the ZIP bytes. Packaging
omits generated caches and rejects broken README links,
symlinks, oversized files, credentials, private paths, and internal development
labels. `--verify-only` checks every ZIP member against the source manifest,
including its size and SHA-256 digest.
