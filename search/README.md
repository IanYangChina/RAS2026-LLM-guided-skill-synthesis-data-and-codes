# Search and optimization

This package provides CMA-ES parameter optimization, structural refinement,
archive interfaces, proposal parsing, semantic-context policies, and catalog
resolution.

- `parameter_optimiser.py` tunes continuous parameters against frozen scene
  configurations.
- `public_catalog.py` resolves a stable record ID and verifies its SHA-256.
- `winner.py` persists replayable winning records.
- `semantic_context_policy.py` applies declared context transformations without
  changing the underlying archived skill.

Use the public scripts rather than importing private helpers for a complete
run. LLM proposal calls are optional and require environment-only credentials.
