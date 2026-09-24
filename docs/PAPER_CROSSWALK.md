# Paper cross-reference

The machine-readable mapping is `data/paper_crosswalk.csv`. Each row contains a
paper label, public source paths, their SHA-256 hashes, and the reproduction
command. All reported numerical material is regenerated with:

```bash
python scripts/reproduce_paper_results.py --strict
```

| Paper material | Public source |
|---|---|
| Expert-reference comparison (`tab:expert_comparison`) | `data/paper_results/expert/` |
| Main automatic comparison (`fig:main_baselines`, `tab:supp_main_summary`, `tab:supp_main_seeds`) | `data/paper_results/main/` |
| Refinement dynamics (`tab:supp_trajectory_summary`) | `data/paper_results/trajectories/` |
| Semantic interventions (`fig:semantic_context`, supplementary semantic tables) | `data/paper_results/semantic/` |
| Structural case studies (`tab:structural_cases`) | `data/paper_results/cases/structural_cases.json` |
| Generation-zero checks | `data/companions/generation_zero_catalog.csv` |
| Executable replay and demonstrations | `data/catalog.csv` replay identity columns |

The reproduction command writes regenerated tables, paired bootstrap results,
gap-recovery values, retention summaries, a copy of every figure-source CSV,
and `verification_report.json`. Strict mode fails if an input is missing or a
full-precision result differs by more than `1e-12`; it reports discrepancies
rather than altering archived measurements.
