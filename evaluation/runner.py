from __future__ import annotations
import numpy as np
from simulation.backend import EpisodeTrace, SimulatorBackend

def run_evaluation(artifact, backend: SimulatorBackend, n_samples: int=50, seed: int=42, scene_config: dict | None=None, task_spec=None, fixed_params: dict[str, float] | None=None) -> list[EpisodeTrace]:
    if n_samples < 1:
        raise ValueError(f'n_samples must be a positive integer, got {n_samples!r}')
    rng = np.random.default_rng(seed)
    param_names: list[str] = list(artifact.parameter_names if hasattr(artifact, 'parameter_names') else artifact.parameter_ranges.keys())
    ranges: dict[str, tuple[float, float]] = artifact.parameter_ranges
    traces: list[EpisodeTrace] = []
    for _ in range(n_samples):
        if fixed_params is not None:
            parameter_values: dict[str, float] = {name: float(fixed_params[name]) for name in param_names}
        else:
            parameter_values = {name: float(rng.uniform(low=ranges[name][0], high=ranges[name][1])) for name in param_names}
        episode_task_spec = task_spec
        trace = backend.run_episode(artifact, parameter_values, scene_config, episode_task_spec)
        traces.append(trace)
    return traces
