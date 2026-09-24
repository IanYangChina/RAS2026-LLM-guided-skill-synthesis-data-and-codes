## Search State

- **Seed**: 9
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 6 | 0.4207 | 0.79 | ✅ accepted |
| 5 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 7 | 0.2972 | 0.63 | ❌ rejected |
| 4 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 11 | -0.0215 | 0.60 | ❌ rejected |
| 3 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 6 | 0.1459 | 0.48 | ❌ rejected |
| 2 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 7 | 0.3319 | 0.68 | ✅ accepted |

**Proposal policy**: task_score is 0.79 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: push_to_goal
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position | approach/contact targets near object start |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose | targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.421) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  weight: 0.2
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.8
phases:
- id: approach_from_behind
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.025
    offset_along_axis:
      distance: 0.1
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    approach_behind_distance:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    approach_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.04
      default: 0.025
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: approach_pose_check
    when: after_phase
    predicate: pose_within_tolerance
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
  subtask_id: reach_object
- id: push_to_goal_phase
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: none
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    push_time:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 5.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 25.0
    on_failure: abort
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_from_behind** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.025], offset_along_axis={axis=task_goal_direction, distance=0.1, mode=replace_offset_projection, sign=negative}, tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - approach_behind_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - approach_z_offset: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=approach_pose_check, when=after_phase, predicate=pose_within_tolerance, on_failure=retry, threshold=0.02
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **push_to_goal_phase** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_time: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=abort, threshold=25.0

## Design Metrics

- **Composite score**: 0.421
- **task_score** (E): 0.788
- **fitness_score**: 0.721  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.300

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_from_behind | 1.00 | 1.00 | 0.1886 |
| push_to_goal_phase | 1.00 | 1.00 | 0.1478 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_from_behind | approach | 1.00 / step_budget | (0.522, 0.019, 0.216)→(0.532, 0.053, 0.038) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_to_goal_phase | push | 1.00 / time_limit | (0.532, 0.053, 0.038)→(0.497, -0.085, 0.024) | (0.518, -0.020, 0.025)→(0.495, -0.120, 0.026) | 0.139→0.032 | 1.00 / 3.333 | 7.325 | 23.707 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.916
- lateral_force_integral: None
- approach_alignment: 0.656
- goal_progress: 0.915
- terminal_score: 0.915
- phase_score: 0.766
- phase_breakdown.reach_object_score: 0.170
- phase_breakdown.push_to_goal_score: 0.915

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.826
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.915
- **Median Q (composite search score)**: 0.521
- **K-run variance**: 0.0210
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.253


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `327b95871eb659cd41b4cf66bc0b4dfb3b240662e8501854b46ee2b8b86a04c5`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5ffd2bb280d1d50ec9ffd23c1ed75abf73d645c1d10372a9b5bb6e9fac6e0bf8`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.12865,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_from_behind.approach_behind_distance":0.09395,"approach_from_behind.approach_speed":0.04273,"approach_from_behind.approach_tolerance":0.01497,"approach_from_behind.approach_z_offset":0.00263,"push_to_goal_phase.push_speed":0.10566,"push_to_goal_phase.push_time":4.36491},"optimized_scores":{"best_composite_score":0.52562,"best_fitness_score":0.82562,"best_task_score":0.91508},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":586.0,"contact_point_centroid":[0.52893,-0.05574,0.02126],"force_p95":15.92093,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.81282,"mean_force":4.10696,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.52988,-0.04385,0.0208]},{"body_a":"world","body_b":"push_box","contact_count":2419.0,"contact_point_centroid":[0.53371,-0.05699,-3e-05],"force_p95":5.57101,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.50076,"mean_force":1.26083,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.54276,-0.00507,0.02141]},{"body_a":"world","body_b":"push_box","contact_count":4304.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_from_behind","phase_type":"approach","tcp_position_centroid":[0.53381,0.03033,0.16251]}],"total_contact_groups":3},"final_pose_error":0.04833,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50236,-0.13903,0.02484],"final_tcp_position":[0.51069,-0.10309,0.02034],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":21.81282,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1076.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_from_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4304.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.56794,0.05995,0.02741],"tcp_start":[0.56498,0.05676,0.04614],"tcp_to_object_dist_end":0.08873,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50236,-0.13903,0.02484],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.01122,"object_to_goal_dist_start":0.13211,"object_z_max":0.02535,"peak_contact_force":17.65327,"phase_name":"push_to_goal_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3005.0,"raw_peak_contact_force":21.81282,"subtask_id":"push_to_goal","tcp_end":[0.51069,-0.10309,0.02034],"tcp_start":[0.56794,0.05995,0.02741],"tcp_to_object_dist_end":0.03716,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e094d2c5a71c8b89ef1fa30d7ce553b9c4ed64cd3fbca90620c3ede94e719cec`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93478,"average_solve_count":92.0,"average_success_count":92.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_from_behind.approach_behind_distance":0.0992,"approach_from_behind.approach_speed":0.10309,"approach_from_behind.approach_tolerance":0.01487,"approach_from_behind.approach_z_offset":0.01689,"push_to_goal_phase.push_speed":0.10644,"push_to_goal_phase.push_time":7.09739},"optimized_scores":{"best_composite_score":0.52062,"best_fitness_score":0.82062,"best_task_score":0.91243},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":463.0,"contact_point_centroid":[0.53828,-0.06102,0.03082],"force_p95":18.53091,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.94978,"mean_force":6.14621,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.53993,-0.04924,0.03012]},{"body_a":"world","body_b":"push_box","contact_count":2617.0,"contact_point_centroid":[0.54249,-0.06345,-5e-05],"force_p95":6.03034,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.88407,"mean_force":1.37061,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.55645,-0.01258,0.03413]},{"body_a":"world","body_b":"push_box","contact_count":3816.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_from_behind","phase_type":"approach","tcp_position_centroid":[0.5435,0.0258,0.1718]}],"total_contact_groups":3},"final_pose_error":0.04746,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5065,-0.14094,0.025],"final_tcp_position":[0.51525,-0.10506,0.02443],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":24.94978,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":954.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_from_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3816.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.58893,0.05171,0.04647],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09573,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5065,-0.14094,0.025],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.01115,"object_to_goal_dist_start":0.12728,"object_z_max":0.02553,"peak_contact_force":2.72831,"phase_name":"push_to_goal_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3080.0,"raw_peak_contact_force":24.94978,"subtask_id":"push_to_goal","tcp_end":[0.51525,-0.10506,0.02443],"tcp_start":[0.58893,0.05171,0.04647],"tcp_to_object_dist_end":0.03693,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0fd7d18e656259f06515eb57b82afa0c0febd9395a43c1a5f926ddaec3767c64`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.52874,"average_solve_count":87.0,"average_success_count":87.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_from_behind.approach_behind_distance":0.05093,"approach_from_behind.approach_speed":0.11375,"approach_from_behind.approach_tolerance":0.01981,"approach_from_behind.approach_z_offset":0.00467,"push_to_goal_phase.push_speed":0.05987,"push_to_goal_phase.push_time":5.68742},"optimized_scores":{"best_composite_score":0.21575,"best_fitness_score":0.51575,"best_task_score":0.53641},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1797.0,"contact_point_centroid":[0.4677,-0.04554,-4e-05],"force_p95":7.9349,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.35791,"mean_force":3.37558,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.44845,0.00739,0.03262]},{"body_a":"attachment","body_b":"push_box","contact_count":775.0,"contact_point_centroid":[0.46338,-0.01655,0.04703],"force_p95":13.36666,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.73933,"mean_force":6.26466,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.45192,-0.0048,0.0314]},{"body_a":"push_box","body_b":"link7","contact_count":112.0,"contact_point_centroid":[0.49681,-0.04786,0.05481],"force_p95":11.11402,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.19468,"mean_force":5.41726,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.46132,-0.03491,0.02916]},{"body_a":"world","body_b":"push_box","contact_count":3320.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_from_behind","phase_type":"approach","tcp_position_centroid":[0.46943,0.02274,0.16908]}],"total_contact_groups":4},"final_pose_error":0.10974,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.4768,-0.08141,0.02873],"final_tcp_position":[0.46492,-0.04607,0.02837],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":24.35791,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":830.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_from_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3320.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.44007,0.04594,0.039],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0505,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4768,-0.08141,0.02873],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.0725,"object_to_goal_dist_start":0.1564,"object_z_max":0.0287,"peak_contact_force":1.59206,"phase_name":"push_to_goal_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2684.0,"raw_peak_contact_force":24.35791,"subtask_id":"push_to_goal","tcp_end":[0.46492,-0.04607,0.02837],"tcp_start":[0.44007,0.04594,0.039],"tcp_to_object_dist_end":0.03728,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```