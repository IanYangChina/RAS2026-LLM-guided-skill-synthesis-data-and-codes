## Search State

- **Seed**: 5
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 5 | -0.2500 | 0.00 | ❌ rejected |
| 7 | approach → descend | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 5 | 0.6867 | 0.94 | ❌ rejected |
| 6 | approach → descend | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 5 | 0.7177 | 0.97 | ❌ rejected |
| 5 | approach → descend | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 5 | 0.7165 | 0.97 | ❌ rejected |
| 4 | approach → descend | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 5 | 0.6868 | 0.94 | ❌ rejected |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: obstacle_reach
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.5
- Force limit: 5.0 N
- Obstacle body: obstacle_block (contact = collision penalty)
- Primary evaluation target: **TCP distance to goal position (Gaussian proximity kernel)**

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
| `object` | offset from object initial position | approach/contact targets near object |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose | approach/contact targets near fixture |

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

## Current Skill (Q=-0.250) — your mutation base

```yaml
skill: obstacle_reach
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: pre_goal
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: final_goal
  weight: 0.7
phases:
- id: approach_clear
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.15
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.0
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
    pose_tol:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: pre_goal
- id: descend_to_goal
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    pose_tol:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.025
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: final_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_clear** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - pose_tol: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_to_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - pose_tol: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: -0.250
- **task_score** (E): 0.000
- **fitness_score**: 0.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.250

**⚠ Warning**: CMA-ES stagnated + low fitness_score → structure may be fundamentally incompatible with task

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_clear | 0.00 | 1.00 | 0.1379 |
| descend_to_goal | 0.00 | 1.00 | 0.0710 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force | Obstacle/contact |
|---|---|---|---|---|---|---|---|---|---|
| approach_clear | approach | 0.00 / step_budget | (0.350, -0.000, 0.321)→(0.450, 0.009, 0.413) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.732→0.732 | 1.00 / 1.000 | 299.120 | 1715.047 | link6 ↔ obstacle_block/obstacle_block_geom |
| descend_to_goal | descend | 0.00 / step_budget | (0.450, 0.009, 0.413)→(0.507, 0.011, 0.372) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.732→0.732 | 1.00 / 1.000 | 304.586 | 396.127 | link6 ↔ obstacle_block/obstacle_block_geom |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- obstacle_clearance: 0.979
- path_efficiency: 0.508
- arc_smoothness: 0.975
- collision_factor: 0.000  (exp(−peak_force / force_scale))
- peak_obstacle_force: 1688.351 N
- collision_location: obstacle_block  (or None if no contact)
- final_tcp_distance: 0.312
- min_tcp_distance: 0.312
- tcp_proximity_score: 0.125
- goal_reached_rate: 0.000
- peak_obstacle_counterbody: link6
- peak_obstacle_countergeom: None
- peak_obstacle_obstacle_body: obstacle_block
- peak_obstacle_obstacle_geom: obstacle_block_geom

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.250
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.318


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `f3b9025bd026eb63e7a6b7b9dcbae30ae5fd727c3f404b5eea2986d705494aa6`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `016b297ed5457e75e60006ae43546f9e20e6368637b147588ecc5457d8da87e0`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.88421,"average_solve_count":95.0,"average_success_count":95.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_clear.approach_speed":0.06224,"approach_clear.arc_height":0.11021,"approach_clear.pose_tol":0.03552,"descend_to_goal.descend_speed":0.06125,"descend_to_goal.pose_tol":0.01916},"optimized_scores":{"best_composite_score":-0.25,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link6","contact_count":918.0,"contact_point_centroid":[0.53057,0.00162,0.29979],"force_p95":311.47844,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":1688.35145,"mean_force":254.9511,"phase_index":0.0,"phase_name":"approach_clear","phase_type":"approach","tcp_position_centroid":[0.41206,0.00422,0.38928]},{"body_a":"obstacle_block","body_b":"link6","contact_count":940.0,"contact_point_centroid":[0.53997,0.01086,0.29995],"force_p95":297.46646,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":353.82415,"mean_force":264.92635,"phase_index":1.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.47499,0.0141,0.39599]}],"total_contact_groups":2},"final_pose_error":0.31157,"key_states":{"actual_goal_position":[0.7305,0.03079,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.51005,0.01762,0.36977],"realised_goal_position":[0.7305,0.03079,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":1688.35145,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.74638,"object_to_goal_dist_start":0.74638,"object_z_max":0.0,"peak_contact_force":251.9612,"phase_name":"approach_clear","phase_peak_obstacle_force":1688.35145,"phase_type":"approach","raw_contact_event_count":918.0,"raw_peak_contact_force":1688.35145,"subtask_id":"pre_goal","tcp_end":[0.464,0.01232,0.40467],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.61579,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.74638,"object_to_goal_dist_start":0.74638,"object_z_max":0.0,"peak_contact_force":269.47255,"phase_name":"descend_to_goal","phase_peak_obstacle_force":353.82415,"phase_type":"descend","raw_contact_event_count":940.0,"raw_peak_contact_force":353.82415,"subtask_id":"final_goal","tcp_end":[0.51005,0.01762,0.36977],"tcp_start":[0.464,0.01232,0.40467],"tcp_to_object_dist_end":0.63023,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `91da6d91b20aa8f1968f3c6d7ec8aa818a9ddb55695f45bcb9bfaacd3acccdac`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.87209,"average_solve_count":86.0,"average_success_count":86.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_clear.approach_speed":0.04813,"approach_clear.arc_height":0.12839,"approach_clear.pose_tol":0.02942,"descend_to_goal.descend_speed":0.09801,"descend_to_goal.pose_tol":0.01845},"optimized_scores":{"best_composite_score":-0.25,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link6","contact_count":956.0,"contact_point_centroid":[0.52079,0.00033,0.29979],"force_p95":269.02619,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":1736.46327,"mean_force":241.04459,"phase_index":0.0,"phase_name":"approach_clear","phase_type":"approach","tcp_position_centroid":[0.39009,-0.00081,0.37501]},{"body_a":"obstacle_block","body_b":"link6","contact_count":892.0,"contact_point_centroid":[0.53727,-0.00563,0.29995],"force_p95":347.36492,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":485.45933,"mean_force":276.1408,"phase_index":1.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.44639,-0.00391,0.41424]}],"total_contact_groups":2},"final_pose_error":0.29384,"key_states":{"actual_goal_position":[0.70382,-0.01567,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.50936,-0.00789,0.37015],"realised_goal_position":[0.70382,-0.01567,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":1736.46327,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":335.27553,"phase_name":"approach_clear","phase_peak_obstacle_force":1736.46327,"phase_type":"approach","raw_contact_event_count":956.0,"raw_peak_contact_force":1736.46327,"subtask_id":"pre_goal","tcp_end":[0.42426,-0.00178,0.42893],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.60331,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":377.57043,"phase_name":"descend_to_goal","phase_peak_obstacle_force":485.45933,"phase_type":"descend","raw_contact_event_count":892.0,"raw_peak_contact_force":485.45933,"subtask_id":"final_goal","tcp_end":[0.50936,-0.00789,0.37015],"tcp_start":[0.42426,-0.00178,0.42893],"tcp_to_object_dist_end":0.62969,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `fc3e8abaaf02ca668222d0cd4e885164ebd20230be343b2ee428dfce1066794d`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.88298,"average_solve_count":94.0,"average_success_count":94.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_clear.approach_speed":0.06465,"approach_clear.arc_height":0.1008,"approach_clear.pose_tol":0.03178,"descend_to_goal.descend_speed":0.06052,"descend_to_goal.pose_tol":0.02017},"optimized_scores":{"best_composite_score":-0.25,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link6","contact_count":920.0,"contact_point_centroid":[0.53021,0.00322,0.29979],"force_p95":311.38375,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":1720.32705,"mean_force":256.41303,"phase_index":0.0,"phase_name":"approach_clear","phase_type":"approach","tcp_position_centroid":[0.41015,0.00544,0.38875]},{"body_a":"obstacle_block","body_b":"link6","contact_count":949.0,"contact_point_centroid":[0.53997,0.01556,0.29995],"force_p95":292.56167,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":349.09807,"mean_force":261.96455,"phase_index":1.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.47032,0.01855,0.39948]}],"total_contact_groups":2},"final_pose_error":0.30934,"key_states":{"actual_goal_position":[0.71251,0.03972,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.50173,0.02309,0.37581],"realised_goal_position":[0.71251,0.03972,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":1720.32705,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":310.12278,"phase_name":"approach_clear","phase_peak_obstacle_force":1720.32705,"phase_type":"approach","raw_contact_event_count":920.0,"raw_peak_contact_force":1720.32705,"subtask_id":"pre_goal","tcp_end":[0.46117,0.0165,0.40655],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.615,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":266.7162,"phase_name":"descend_to_goal","phase_peak_obstacle_force":349.09807,"phase_type":"descend","raw_contact_event_count":949.0,"raw_peak_contact_force":349.09807,"subtask_id":"final_goal","tcp_end":[0.50173,0.02309,0.37581],"tcp_start":[0.46117,0.0165,0.40655],"tcp_to_object_dist_end":0.62729,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```