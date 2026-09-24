# Motion primitives

Motion primitives generate target trajectories and control actions for the
compiled skill phases. Control modes, trajectory generators, and termination
conditions are kept separate so that structural programs can be validated
without running physics.

The simulation executor consumes the generated trajectory and records the
state needed by evaluation metrics and optional rendering.
