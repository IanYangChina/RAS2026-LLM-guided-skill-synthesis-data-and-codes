# Compiler

The compiler turns a validated skill-program AST into an executable controller
artifact. It is deterministic and has no network or simulator side effects.

The public entry point is `compiler.compile`. Skills are loaded with
`dsl.serialiser.load_skill`; validation should happen before compilation. The
result is consumed by `evaluation.runner` or `simulation` backends.
