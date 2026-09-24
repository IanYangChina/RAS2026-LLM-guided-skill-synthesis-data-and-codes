# Evaluation

The evaluation layer runs compiled controllers for a requested number of
episodes and converts traces into task and design metrics. `TaskSpec` holds the
per-task objective and limits; `evaluation.runner.run_evaluation` produces
traces; `evaluation.metrics.compute_metrics` computes the score fields.

The canonical task score is the headline task objective. Composite and
structural diagnostics are retained for analysis. Always record task, seed,
episode count, backend, skill hash, parameter hash, and scene-bank hash with a
new result.
