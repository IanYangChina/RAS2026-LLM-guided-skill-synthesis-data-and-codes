# Skill-program DSL

This package defines the typed YAML grammar used for robot skills. It includes
AST nodes, loading and serialization, grammar validation, and public-context
sanitization for semantic study inputs.

Use `dsl.serialiser.load_skill` to read YAML and `dump_skill` to write a stable
representation. Invalid phase types, parameters, termination conditions, or
subtask references are rejected before compilation. Skill YAML is data, not
executable Python.
