from __future__ import annotations
import numpy as np
from primitives.generators import N_STEPS
from simulation.backend import ContactEvent, EpisodeTrace, SimulatorBackend

class MockSimulatorBackend(SimulatorBackend):

    @property
    def name(self) -> str:
        return 'mock'

    def is_available(self) -> bool:
        return True

    def run_episode(self, artifact, parameter_values: dict[str, float], scene_config: dict | None=None, task_spec=None) -> EpisodeTrace:
        success = self._check_parameters_in_range(artifact, parameter_values)
        trajectory = self._build_trajectory(parameter_values)
        contact_history = [ContactEvent(time=1.0, force=6.2, in_contact=True), ContactEvent(time=1.5, force=8.5, in_contact=True), ContactEvent(time=2.0, force=3.1, in_contact=False)]
        metadata: dict = {'backend': self.name, 'scene_config': scene_config}
        if task_spec is not None:
            import numpy as np
            goal = np.array(task_spec.goal_tcp_position, dtype=float)
            if success:
                final_tcp = goal.copy()
            else:
                final_tcp = goal + np.array([0.2, 0.0, 0.0])
            metadata['final_tcp_position'] = final_tcp.tolist()
        return EpisodeTrace(skill_name=artifact.skill_name, parameter_values=dict(parameter_values), success=success, duration=3.0, final_pose_error=0.005 if success else 0.08, peak_contact_force=8.5 if success else 25.0, trajectory_positions=trajectory, contact_history=contact_history, metadata=metadata)

    @staticmethod
    def _check_parameters_in_range(artifact, parameter_values: dict[str, float]) -> bool:
        ranges: dict[str, tuple[float, float]] = artifact.parameter_ranges
        for (name, value) in parameter_values.items():
            if name in ranges:
                (low, high) = ranges[name]
                if not low <= value <= high:
                    return False
        return True

    @staticmethod
    def _build_trajectory(parameter_values: dict[str, float]) -> np.ndarray:
        base = np.zeros((N_STEPS, 3), dtype=float)
        param_sum = sum(parameter_values.values()) if parameter_values else 0.0
        offset = param_sum * 0.001
        base += offset
        return base
