## Search State

- **Seed**: 6
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | rotate → align → lift → push → approach → approach → descend → grasp | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_control | position_control | position_control | position_control | force_threshold_switch | position_control | admittance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | -0.3800 | 0.00 | ✅ accepted |

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

## Current Skill (Q=-0.380) — your mutation base

```yaml
skill: obstacle_reach
skill_type: arm_gripper
phases:
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
- id: approach_2
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp

```

## Design Metrics

- **Composite score**: -0.380
- **task_score** (E): 0.000
- **fitness_score**: 0.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

**⚠ Warning**: CMA-ES stagnated + low fitness_score → structure may be fundamentally incompatible with task

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| rotate_1 | 1.00 | 1.00 | 0.0557 |
| align_1 | 0.00 | 1.00 | 0.0450 |
| lift_1 | 1.00 | 0.00 | 0.0137 |
| push_1 | 0.00 | 1.00 | 0.0632 |
| approach_1 | 1.00 | 0.00 | 0.1930 |
| approach_2 | 1.00 | 0.00 | 0.0068 |
| descend_1 | 1.00 | 0.00 | 0.1915 |
| grasp_1 | 1.00 | 1.00 | 0.0110 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force | Obstacle/contact |
|---|---|---|---|---|---|---|---|---|---|
| rotate_1 | rotate | 1.00 / time_limit | (0.350, -0.000, 0.321)→(0.406, 0.000, 0.315) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.717→0.717 | 1.00 / 1.000 | 277.519 | 402.924 | link7 ↔ obstacle_block/obstacle_block_geom |
| align_1 | align | 0.00 / step_budget | (0.406, 0.000, 0.315)→(0.427, 0.000, 0.354) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.717→0.717 | 1.00 / 1.000 | 248.915 | 274.244 | link6 ↔ obstacle_block/obstacle_block_geom |
| lift_1 | lift | 1.00 / step_budget | (0.427, 0.000, 0.354)→(0.440, -0.000, 0.350) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.717→0.717 | 0.00 / 0.000 | 0.000 | 169.078 | link6 ↔ obstacle_block/obstacle_block_geom |
| push_1 | push | 0.00 / step_budget | (0.440, -0.000, 0.350)→(0.495, -0.000, 0.381) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.717→0.717 | 1.00 / 1.000 | 264.742 | 297.382 | link6 ↔ obstacle_block/obstacle_block_geom |
| approach_1 | approach | 1.00 / step_budget | (0.495, -0.000, 0.381)→(0.686, -0.000, 0.356) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.717→0.717 | 0.00 / 0.000 | 0.000 | 308.100 | link6 ↔ obstacle_block/obstacle_block_geom |
| approach_2 | approach | 1.00 / step_budget | (0.686, -0.000, 0.356)→(0.691, -0.000, 0.351) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.717→0.717 | 0.00 / 0.000 | 0.000 | 0.000 | — |
| descend_1 | descend | 1.00 / step_budget | (0.691, -0.000, 0.351)→(0.697, -0.000, 0.159) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.717→0.717 | 0.00 / 0.000 | 0.000 | 0.000 | — |
| grasp_1 | grasp | 1.00 / step_budget | (0.697, -0.000, 0.159)→(0.693, -0.000, 0.149) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.717→0.717 | 1.00 / 1.000 | 53.518 | 62.847 | link5 ↔ obstacle_block/obstacle_block_geom |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- obstacle_clearance: 0.754
- path_efficiency: 0.603
- arc_smoothness: 0.987
- collision_factor: 0.000  (exp(−peak_force / force_scale))
- peak_obstacle_force: 402.924 N
- collision_location: obstacle_block  (or None if no contact)
- final_tcp_distance: 0.019
- min_tcp_distance: 0.019
- tcp_proximity_score: 0.879
- goal_reached_rate: 1.000
- peak_obstacle_counterbody: link7
- peak_obstacle_countergeom: None
- peak_obstacle_obstacle_body: obstacle_block
- peak_obstacle_obstacle_geom: obstacle_block_geom

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.380
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.351


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `89af5e6373a217810de823e85ed206d27eafc89c151e748b39ede2d750fe7c5e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `6b4e4a3a850359b999c84710456096c65c7b37ffa6a27fd54ebaec8821f1dcd2`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61803,"average_solve_count":233.0,"average_success_count":233.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":0.00465,"approach_2.speed":0.04593,"push_1.push_depth":0.03016,"push_1.push_speed":0.0837},"optimized_scores":{"best_composite_score":-0.38,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link7","contact_count":603.0,"contact_point_centroid":[0.46008,0.00101,0.29994],"force_p95":353.04166,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":402.92406,"mean_force":309.44787,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.40497,2e-05,0.30212]},{"body_a":"obstacle_block","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.53997,-0.00338,0.29996],"force_p95":284.4622,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":312.28019,"mean_force":115.46015,"phase_index":4.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49324,-9e-05,0.38204]},{"body_a":"obstacle_block","body_b":"link6","contact_count":982.0,"contact_point_centroid":[0.53997,-0.00395,0.29992],"force_p95":253.39564,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":295.57646,"mean_force":216.97628,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46565,4e-05,0.37138]},{"body_a":"obstacle_block","body_b":"link6","contact_count":190.0,"contact_point_centroid":[0.52527,-0.00446,0.29994],"force_p95":258.8246,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":274.24353,"mean_force":250.04585,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.42396,2e-05,0.34776]},{"body_a":"obstacle_block","body_b":"link7","contact_count":824.0,"contact_point_centroid":[0.46002,0.00154,0.29993],"force_p95":267.15948,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":272.0597,"mean_force":246.7527,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.41156,3e-05,0.32939]},{"body_a":"obstacle_block","body_b":"link6","contact_count":33.0,"contact_point_centroid":[0.54,-0.00507,0.29999],"force_p95":163.03959,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":169.07836,"mean_force":95.60661,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4326,-4e-05,0.35241]},{"body_a":"obstacle_block","body_b":"link5","contact_count":372.0,"contact_point_centroid":[0.54,0.0321,0.29998],"force_p95":57.91395,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":61.36067,"mean_force":53.16578,"phase_index":7.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.69321,-0.00021,0.14834]}],"total_contact_groups":7},"final_pose_error":0.00968,"key_states":{"actual_goal_position":[0.70382,-0.01567,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.69649,-0.00014,0.15902],"realised_goal_position":[0.70382,-0.01567,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":402.92406,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":277.51859,"phase_name":"rotate_1","phase_peak_obstacle_force":402.92406,"phase_type":"rotate","raw_contact_event_count":603.0,"raw_peak_contact_force":402.92406,"tcp_end":[0.40568,3e-05,0.31495],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.51359,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":248.91504,"phase_name":"align_1","phase_peak_obstacle_force":274.24353,"phase_type":"align","raw_contact_event_count":1014.0,"raw_peak_contact_force":274.24353,"tcp_end":[0.4273,1e-05,0.35439],"tcp_start":[0.40568,3e-05,0.31495],"tcp_to_object_dist_end":0.55513,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":77.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lift_1","phase_peak_obstacle_force":169.07836,"phase_type":"lift","raw_contact_event_count":33.0,"raw_peak_contact_force":169.07836,"tcp_end":[0.44014,-8e-05,0.34962],"tcp_start":[0.4273,1e-05,0.35439],"tcp_to_object_dist_end":0.5621,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":285.30162,"phase_name":"push_1","phase_peak_obstacle_force":295.57646,"phase_type":"push","raw_contact_event_count":982.0,"raw_peak_contact_force":295.57646,"tcp_end":[0.49317,-9e-05,0.38213],"tcp_start":[0.44014,-8e-05,0.34962],"tcp_to_object_dist_end":0.62389,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":312.28019,"phase_type":"approach","raw_contact_event_count":3.0,"raw_peak_contact_force":312.28019,"tcp_end":[0.68605,-0.00012,0.3562],"tcp_start":[0.49317,-9e-05,0.38213],"tcp_to_object_dist_end":0.773,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":28.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.69011,-0.00014,0.35123],"tcp_start":[0.68605,-0.00012,0.3562],"tcp_to_object_dist_end":0.77435,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":465.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.69649,-0.00014,0.15902],"tcp_start":[0.69011,-0.00014,0.35123],"tcp_to_object_dist_end":0.71441,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":52.59482,"phase_name":"grasp_1","phase_peak_obstacle_force":61.36067,"phase_type":"grasp","raw_contact_event_count":372.0,"raw_peak_contact_force":61.36067,"tcp_end":[0.69322,-0.00019,0.14838],"tcp_start":[0.69649,-0.00014,0.15902],"tcp_to_object_dist_end":0.70892,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3dbedbccfafbb480e6b8853d24674113c48a7d6ac70107463f0222214d243e47`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61638,"average_solve_count":232.0,"average_success_count":232.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":0.00104,"approach_2.speed":0.04421,"push_1.push_depth":0.05895,"push_1.push_speed":0.09172},"optimized_scores":{"best_composite_score":-0.38,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link7","contact_count":603.0,"contact_point_centroid":[0.46008,0.00101,0.29994],"force_p95":353.04166,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":402.92406,"mean_force":309.44787,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.40497,2e-05,0.30212]},{"body_a":"obstacle_block","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.53999,-0.00295,0.29999],"force_p95":312.69984,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":312.69984,"mean_force":312.69984,"phase_index":4.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49939,-0.00017,0.37756]},{"body_a":"obstacle_block","body_b":"link6","contact_count":973.0,"contact_point_centroid":[0.53996,-0.00392,0.29991],"force_p95":270.98113,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":303.32536,"mean_force":222.1858,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46813,1e-05,0.37239]},{"body_a":"obstacle_block","body_b":"link6","contact_count":190.0,"contact_point_centroid":[0.52527,-0.00446,0.29994],"force_p95":258.8246,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":274.24353,"mean_force":250.04585,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.42396,2e-05,0.34776]},{"body_a":"obstacle_block","body_b":"link7","contact_count":824.0,"contact_point_centroid":[0.46002,0.00154,0.29993],"force_p95":267.15948,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":272.0597,"mean_force":246.7527,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.41156,3e-05,0.32939]},{"body_a":"obstacle_block","body_b":"link6","contact_count":33.0,"contact_point_centroid":[0.54,-0.00507,0.29999],"force_p95":163.03959,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":169.07836,"mean_force":95.60661,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4326,-4e-05,0.35241]},{"body_a":"obstacle_block","body_b":"link5","contact_count":375.0,"contact_point_centroid":[0.54,0.032,0.29998],"force_p95":62.61393,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":67.0903,"mean_force":57.11865,"phase_index":7.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.69346,-0.00019,0.14891]}],"total_contact_groups":7},"final_pose_error":0.00981,"key_states":{"actual_goal_position":[0.71251,0.03972,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.69661,-0.00014,0.1592],"realised_goal_position":[0.71251,0.03972,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":402.92406,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":277.51859,"phase_name":"rotate_1","phase_peak_obstacle_force":402.92406,"phase_type":"rotate","raw_contact_event_count":603.0,"raw_peak_contact_force":402.92406,"tcp_end":[0.40568,3e-05,0.31495],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.51359,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":248.91504,"phase_name":"align_1","phase_peak_obstacle_force":274.24353,"phase_type":"align","raw_contact_event_count":1014.0,"raw_peak_contact_force":274.24353,"tcp_end":[0.4273,1e-05,0.35439],"tcp_start":[0.40568,3e-05,0.31495],"tcp_to_object_dist_end":0.55513,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":77.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lift_1","phase_peak_obstacle_force":169.07836,"phase_type":"lift","raw_contact_event_count":33.0,"raw_peak_contact_force":169.07836,"tcp_end":[0.44014,-8e-05,0.34962],"tcp_start":[0.4273,1e-05,0.35439],"tcp_to_object_dist_end":0.5621,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":262.20005,"phase_name":"push_1","phase_peak_obstacle_force":303.32536,"phase_type":"push","raw_contact_event_count":973.0,"raw_peak_contact_force":303.32536,"tcp_end":[0.49939,-0.00017,0.37756],"tcp_start":[0.44014,-8e-05,0.34962],"tcp_to_object_dist_end":0.62605,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":312.69984,"phase_type":"approach","raw_contact_event_count":1.0,"raw_peak_contact_force":312.69984,"tcp_end":[0.68965,-0.00012,0.35175],"tcp_start":[0.49939,-0.00017,0.37756],"tcp_to_object_dist_end":0.77417,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.69142,-0.00015,0.3486],"tcp_start":[0.68965,-0.00012,0.35175],"tcp_to_object_dist_end":0.77432,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":458.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.69661,-0.00014,0.1592],"tcp_start":[0.69142,-0.00015,0.3486],"tcp_to_object_dist_end":0.71457,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":56.44563,"phase_name":"grasp_1","phase_peak_obstacle_force":67.0903,"phase_type":"grasp","raw_contact_event_count":375.0,"raw_peak_contact_force":67.0903,"tcp_end":[0.69347,-0.00017,0.14895],"tcp_start":[0.69661,-0.00014,0.1592],"tcp_to_object_dist_end":0.70928,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `71285845baf1b8f9da7d5ce873550759a4c17d69a356cdc4cf82cc31badfb976`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64807,"average_solve_count":233.0,"average_success_count":233.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.00096,"approach_2.speed":0.03997,"push_1.push_depth":0.07168,"push_1.push_speed":0.08251},"optimized_scores":{"best_composite_score":-0.38,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link7","contact_count":603.0,"contact_point_centroid":[0.46008,0.00101,0.29994],"force_p95":353.04166,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":402.92406,"mean_force":309.44787,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.40497,2e-05,0.30212]},{"body_a":"obstacle_block","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.53999,-0.00346,0.29999],"force_p95":273.0512,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":299.32055,"mean_force":111.98253,"phase_index":4.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49238,-9e-05,0.38277]},{"body_a":"obstacle_block","body_b":"link6","contact_count":981.0,"contact_point_centroid":[0.53997,-0.00405,0.29992],"force_p95":252.94331,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":293.24312,"mean_force":216.14582,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46504,0.0,0.37191]},{"body_a":"obstacle_block","body_b":"link6","contact_count":190.0,"contact_point_centroid":[0.52527,-0.00446,0.29994],"force_p95":258.8246,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":274.24353,"mean_force":250.04585,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.42396,2e-05,0.34776]},{"body_a":"obstacle_block","body_b":"link7","contact_count":824.0,"contact_point_centroid":[0.46002,0.00154,0.29993],"force_p95":267.15948,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":272.0597,"mean_force":246.7527,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.41156,3e-05,0.32939]},{"body_a":"obstacle_block","body_b":"link6","contact_count":33.0,"contact_point_centroid":[0.54,-0.00507,0.29999],"force_p95":163.03959,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":169.07836,"mean_force":95.60661,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4326,-4e-05,0.35241]},{"body_a":"obstacle_block","body_b":"link5","contact_count":371.0,"contact_point_centroid":[0.54,0.03212,0.29998],"force_p95":56.75518,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":60.08898,"mean_force":52.07617,"phase_index":7.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.69319,-0.00021,0.14825]}],"total_contact_groups":7},"final_pose_error":0.0097,"key_states":{"actual_goal_position":[0.6827,0.04873,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.69651,-0.00014,0.15905],"realised_goal_position":[0.6827,0.04873,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":402.92406,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":277.51859,"phase_name":"rotate_1","phase_peak_obstacle_force":402.92406,"phase_type":"rotate","raw_contact_event_count":603.0,"raw_peak_contact_force":402.92406,"tcp_end":[0.40568,3e-05,0.31495],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.51359,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":248.91504,"phase_name":"align_1","phase_peak_obstacle_force":274.24353,"phase_type":"align","raw_contact_event_count":1014.0,"raw_peak_contact_force":274.24353,"tcp_end":[0.4273,1e-05,0.35439],"tcp_start":[0.40568,3e-05,0.31495],"tcp_to_object_dist_end":0.55513,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":77.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lift_1","phase_peak_obstacle_force":169.07836,"phase_type":"lift","raw_contact_event_count":33.0,"raw_peak_contact_force":169.07836,"tcp_end":[0.44014,-8e-05,0.34962],"tcp_start":[0.4273,1e-05,0.35439],"tcp_to_object_dist_end":0.5621,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":246.72475,"phase_name":"push_1","phase_peak_obstacle_force":293.24312,"phase_type":"push","raw_contact_event_count":981.0,"raw_peak_contact_force":293.24312,"tcp_end":[0.49232,-9e-05,0.38288],"tcp_start":[0.44014,-8e-05,0.34962],"tcp_to_object_dist_end":0.62368,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":299.32055,"phase_type":"approach","raw_contact_event_count":3.0,"raw_peak_contact_force":299.32055,"tcp_end":[0.68321,-0.00012,0.35924],"tcp_start":[0.49232,-9e-05,0.38288],"tcp_to_object_dist_end":0.7719,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":42.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.69035,-0.00014,0.35172],"tcp_start":[0.68321,-0.00012,0.35924],"tcp_to_object_dist_end":0.77478,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":466.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.69651,-0.00014,0.15905],"tcp_start":[0.69035,-0.00014,0.35172],"tcp_to_object_dist_end":0.71444,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":51.51353,"phase_name":"grasp_1","phase_peak_obstacle_force":60.08898,"phase_type":"grasp","raw_contact_event_count":371.0,"raw_peak_contact_force":60.08898,"tcp_end":[0.69321,-0.00019,0.14829],"tcp_start":[0.69651,-0.00014,0.15905],"tcp_to_object_dist_end":0.70889,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```