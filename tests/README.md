# Tests

These tests cover public imports, CLI argument validation, catalog resolution,
skill rendering input handling, and bounded output behavior. Run them from the
repository root:

```bash
python -m pytest tests/ -q
```

The tests do not replace the paper protocol. A passing test suite means the
public interfaces are internally consistent; scientific claims require the
curated records, hashes, and declared MuJoCo protocol.
