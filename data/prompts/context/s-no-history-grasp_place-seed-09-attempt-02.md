## Search State

- **Seed**: 9
- **Iteration**: 3 / 15

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

- Task name: grasp_place
- Frozen realised-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`
- Frozen object start: [0.5370249203970084, -0.021318279091244466, 0.03]
- Frozen task target: [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]
- Goal object position: (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5370249203970084, -0.021318279091244466, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.537, -0.0213, 0.03]
  frozen_task_target: [0.6103, 0.2278, 0.2074]
  frozen_object_starts: {'grasp_target': [0.5370249203970084, -0.021318279091244466, 0.03]}
  frozen_targets: {'place_target': [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8

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
| `object` | offset from object initial position (0.5370249203970084, -0.021318279091244466, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6103148150051562, 0.2277534082920179, 0.2074111944405348) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

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

## Current Skill (Q=-0.165) — your mutation base

```yaml
skill: grasp_place
skill_type: arm_gripper
phases:
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    yaw_angle:
      type: angle
      range:
      - 0.1
      - 1.57
- id: pull_1
  type: pull
  generator: arc_cartesian
  control: impedance_control
  termination: time_limit
  parameters:
    pull_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
- id: grasp_1
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  parameters:
    grip_force:
      type: scalar
      range:
      - 5.0
      - 30.0
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: -0.165
- **task_score** (E): 0.130
- **fitness_score**: 0.285  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.450

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| rotate_1 | 0.00 | 1.00 | 0.2373 |
| pull_1 | 1.00 | 1.00 | 0.1595 |
| push_1 | 1.00 | 1.00 | 0.1840 |
| descend_1 | 1.00 | 1.00 | 0.2300 |
| descend_2 | 1.00 | 1.00 | 0.0408 |
| grasp_1 | 1.00 | 1.00 | 0.0121 |
| approach_1 | 1.00 | 1.00 | 0.0762 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| rotate_1 | rotate | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.574, 0.155, 0.137) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| pull_1 | pull | 1.00 / time_limit | (0.574, 0.155, 0.137)→(0.590, 0.222, 0.281) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| push_1 | push | 1.00 / time_limit | (0.590, 0.222, 0.281)→(0.595, 0.199, 0.098) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_1 | descend | 1.00 / step_budget | (0.595, 0.199, 0.098)→(0.514, -0.006, 0.043) | (0.515, -0.017, 0.026)→(0.504, -0.042, 0.015) | 0.270→0.300 | 1.00 / 7.000 | 12.541 | 0.737 |
| descend_2 | descend | 1.00 / step_budget | (0.514, -0.006, 0.043)→(0.500, -0.040, 0.029) | (0.504, -0.042, 0.015)→(0.490, -0.055, 0.012) | 0.300→0.318 | 1.00 / 10.667 | 0.488 | 0.763 |
| grasp_1 | grasp | 1.00 / step_budget | (0.500, -0.040, 0.029)→(0.491, -0.040, 0.021) | (0.490, -0.055, 0.012)→(0.486, -0.045, 0.005) | 0.318→0.316 | 1.00 / 27.667 | 0.673 | 0.709 |
| approach_1 | approach | 1.00 / step_budget | (0.491, -0.040, 0.021)→(0.482, -0.045, 0.096) | (0.486, -0.045, 0.005)→(0.481, -0.042, 0.016) | 0.316→0.309 | 1.00 / 8.333 | 91001.553 | 0.992 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.159
- phase_score: 0.238
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.165
- phase_breakdown.release_1_score: 0.000
- phase_breakdown.descend_1_score: 0.793
- phase_breakdown.transport_arc_score: 0.000
- grasp_place_fitness: 0.296

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.296
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.159
- **Median Q (composite search score)**: -0.162
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.367


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `425c48e82220fc6e1b680086671cf7dd2586733ee271dec2149f96a25d69d0c6`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `58e88c03db0a62276863b22a53636bc89fead3e4bc7f4d35fd72d2282ace32bf`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82949,"average_solve_count":217.0,"average_success_count":217.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0999,"grasp_1.grip_force":18.76794,"pull_1.pull_distance":0.13573,"push_1.push_distance":0.10678,"push_1.push_speed":0.08742,"rotate_1.yaw_angle":0.22539},"optimized_scores":{"best_composite_score":-0.17878,"best_fitness_score":0.27122,"best_task_score":0.09491},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1960.0,"contact_point_centroid":[0.50333,-0.05899,-0.00415],"force_p95":0.70049,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.25839,"mean_force":0.24676,"phase_index":6.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50871,-0.0513,0.05524]},{"body_a":"world","body_b":"grasp_target","contact_count":1679.0,"contact_point_centroid":[0.51169,-0.05472,-0.00845],"force_p95":0.93838,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.95919,"mean_force":0.56166,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5149,-0.049,0.0174]},{"body_a":"world","body_b":"grasp_target","contact_count":3634.0,"contact_point_centroid":[0.53665,-0.02251,-0.00289],"force_p95":0.59412,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.77732,"mean_force":0.1871,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.56373,0.09725,0.06769]},{"body_a":"world","body_b":"grasp_target","contact_count":3564.0,"contact_point_centroid":[0.52221,-0.0577,-0.00541],"force_p95":0.65873,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71096,"mean_force":0.3441,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.52576,-0.03227,0.03069]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6884.0,"contact_point_centroid":[0.51009,-0.03164,0.03901],"force_p95":0.24053,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.63463,"mean_force":0.09827,"phase_index":6.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50882,-0.05037,0.04004]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4675.0,"contact_point_centroid":[0.50663,-0.06976,0.03225],"force_p95":0.18098,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33053,"mean_force":0.11199,"phase_index":6.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50901,-0.05018,0.03697]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9177.0,"contact_point_centroid":[0.52331,-0.07571,0.02537],"force_p95":0.15424,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31165,"mean_force":0.08468,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.52526,-0.0345,0.02997]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1750.0,"contact_point_centroid":[0.54191,-0.02661,0.04413],"force_p95":0.20539,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2513,"mean_force":0.12023,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54193,0.01615,0.04862]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2357.0,"contact_point_centroid":[0.5136,-0.02581,0.01564],"force_p95":0.22226,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24603,"mean_force":0.10736,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51384,-0.04893,0.01623]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5313.0,"contact_point_centroid":[0.51119,-0.0807,0.01455],"force_p95":0.20887,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24086,"mean_force":0.13859,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51506,-0.049,0.01757]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.53702,-0.02132,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.53682,0.07971,0.21414]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.57881,0.20088,0.19629]},{"body_a":"world","body_b":"grasp_target","contact_count":3068.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.59154,0.21013,0.18464]},{"body_a":"left_finger","body_b":"right_finger","contact_count":617.0,"contact_point_centroid":[0.50847,-0.05315,0.08784],"force_p95":0.01307,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0165,"mean_force":0.0106,"phase_index":6.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50801,-0.05317,0.0856]}],"total_contact_groups":14},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.50043,-0.04805,0.01602],"final_tcp_position":[0.50803,-0.05354,0.09158],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.25839,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.57391,0.15482,0.13706],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21146,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58999,0.22216,0.28073],"tcp_start":[0.57391,0.15482,0.13706],"tcp_to_object_dist_end":0.35632,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":767.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3068.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59497,0.19928,0.09835],"tcp_start":[0.58999,0.22216,0.28073],"tcp_to_object_dist_end":0.23928,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":971.0,"n_steps_budget":1000.0,"object_pos_end":[0.52728,-0.05109,0.01114],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.35096,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.62505,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5384.0,"raw_peak_contact_force":0.77732,"tcp_end":[0.53429,-0.01262,0.04193],"tcp_start":[0.59497,0.19928,0.09835],"tcp_to_object_dist_end":0.04977,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":971.0,"n_steps_budget":1000.0,"object_pos_end":[0.5177,-0.06731,0.01051],"object_pos_start":[0.52728,-0.05109,0.01114],"object_to_goal_dist_end":0.36663,"object_to_goal_dist_start":0.35096,"object_z_max":0.01114,"peak_contact_force":0.70027,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12741.0,"raw_peak_contact_force":0.71096,"tcp_end":[0.52233,-0.0493,0.02562],"tcp_start":[0.53429,-0.01262,0.04193],"tcp_to_object_dist_end":0.02396,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5125,-0.05404,0.00046],"object_pos_start":[0.5177,-0.06731,0.01051],"object_to_goal_dist_end":0.36304,"object_to_goal_dist_start":0.36663,"object_z_max":0.01051,"peak_contact_force":0.9594,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9349.0,"raw_peak_contact_force":0.95919,"tcp_end":[0.51383,-0.04888,0.01622],"tcp_start":[0.52233,-0.0493,0.02562],"tcp_to_object_dist_end":0.01663,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":861.0,"n_steps_budget":1000.0,"object_pos_end":[0.50043,-0.04805,0.01602],"object_pos_start":[0.5125,-0.05404,0.00046],"object_to_goal_dist_end":0.35323,"object_to_goal_dist_start":0.36304,"object_z_max":0.03343,"peak_contact_force":0.12266,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14136.0,"raw_peak_contact_force":1.25839,"tcp_end":[0.50803,-0.05354,0.09158],"tcp_start":[0.51383,-0.04888,0.01622],"tcp_to_object_dist_end":0.07614,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1e57d18e69439f9d4839513252d085a45363faa5c1c2b52093c9c8149b88bb68`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82629,"average_solve_count":213.0,"average_success_count":213.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08554,"grasp_1.grip_force":23.2633,"pull_1.pull_distance":0.11282,"push_1.push_distance":0.05522,"push_1.push_speed":0.09896,"rotate_1.yaw_angle":0.48062},"optimized_scores":{"best_composite_score":-0.16239,"best_fitness_score":0.28761,"best_task_score":0.13705},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2791.0,"contact_point_centroid":[0.52155,-0.06946,-0.00368],"force_p95":0.61447,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.09491,"mean_force":0.2197,"phase_index":6.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52122,-0.05739,0.05647]},{"body_a":"world","body_b":"grasp_target","contact_count":1777.0,"contact_point_centroid":[0.52766,-0.06295,-0.0087],"force_p95":0.79308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.81253,"mean_force":0.57015,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52572,-0.05327,0.01895]},{"body_a":"world","body_b":"grasp_target","contact_count":3629.0,"contact_point_centroid":[0.53358,-0.06258,-0.00523],"force_p95":0.62248,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.80168,"mean_force":0.33323,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.53578,-0.03583,0.03187]},{"body_a":"world","body_b":"grasp_target","contact_count":3812.0,"contact_point_centroid":[0.5453,-0.03015,-0.00273],"force_p95":0.56579,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.75155,"mean_force":0.17655,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.56786,0.09474,0.06817]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6089.0,"contact_point_centroid":[0.52012,-0.03883,0.0341],"force_p95":0.13239,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.51561,"mean_force":0.07497,"phase_index":6.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5207,-0.05533,0.03668]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8920.0,"contact_point_centroid":[0.53382,-0.07839,0.02683],"force_p95":0.14794,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35485,"mean_force":0.08503,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.53554,-0.03742,0.03147]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3743.0,"contact_point_centroid":[0.5205,-0.07374,0.02917],"force_p95":0.21614,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34042,"mean_force":0.12712,"phase_index":6.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52077,-0.05506,0.03408]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5306.0,"contact_point_centroid":[0.52153,-0.08363,0.01615],"force_p95":0.24349,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2758,"mean_force":0.14868,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52574,-0.05327,0.01896]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2808.0,"contact_point_centroid":[0.52373,-0.03243,0.01664],"force_p95":0.15223,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22373,"mean_force":0.07051,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52451,-0.05319,0.01758]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1705.0,"contact_point_centroid":[0.54994,-0.03115,0.04555],"force_p95":0.19586,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21016,"mean_force":0.1095,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54946,0.01179,0.04908]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.5456,-0.02923,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.53682,0.07971,0.21414]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.57881,0.20088,0.19629]},{"body_a":"world","body_b":"grasp_target","contact_count":3004.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.59152,0.21022,0.18531]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1138.0,"contact_point_centroid":[0.52248,-0.05993,0.08331],"force_p95":0.01224,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01576,"mean_force":0.01048,"phase_index":6.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52178,-0.05993,0.08098]}],"total_contact_groups":14},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.52199,-0.06021,0.01602],"final_tcp_position":[0.52223,-0.06098,0.09105],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":273004.41465,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.57391,0.15482,0.13706],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21681,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58999,0.22216,0.28073],"tcp_start":[0.57391,0.15482,0.13706],"tcp_to_object_dist_end":0.36062,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":751.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3004.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59496,0.19936,0.09896],"tcp_start":[0.58999,0.22216,0.28073],"tcp_to_object_dist_end":0.24497,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5381,-0.05559,0.01305],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.29062,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":35.77021,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5517.0,"raw_peak_contact_force":0.75155,"tcp_end":[0.54392,-0.01359,0.0433],"tcp_start":[0.59496,0.19936,0.09896],"tcp_to_object_dist_end":0.05209,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":974.0,"n_steps_budget":1000.0,"object_pos_end":[0.52961,-0.07366,0.00965],"object_pos_start":[0.5381,-0.05559,0.01305],"object_to_goal_dist_end":0.30913,"object_to_goal_dist_start":0.29062,"object_z_max":0.01305,"peak_contact_force":0.64108,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12549.0,"raw_peak_contact_force":0.80168,"tcp_end":[0.53307,-0.05362,0.0273],"tcp_start":[0.54392,-0.01359,0.0433],"tcp_to_object_dist_end":0.02693,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52689,-0.06161,-0.00017],"object_pos_start":[0.52961,-0.07366,0.00965],"object_to_goal_dist_end":0.30644,"object_to_goal_dist_start":0.30913,"object_z_max":0.00965,"peak_contact_force":0.81272,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9891.0,"raw_peak_contact_force":0.81253,"tcp_end":[0.5245,-0.05313,0.01757],"tcp_start":[0.53307,-0.05362,0.0273],"tcp_to_object_dist_end":0.0198,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":941.0,"n_steps_budget":1000.0,"object_pos_end":[0.52199,-0.06021,0.01602],"object_pos_start":[0.52689,-0.06161,-0.00017],"object_to_goal_dist_end":0.29811,"object_to_goal_dist_start":0.30644,"object_z_max":0.02769,"peak_contact_force":273004.41465,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13761.0,"raw_peak_contact_force":1.09491,"tcp_end":[0.52223,-0.06098,0.09105],"tcp_start":[0.5245,-0.05313,0.01757],"tcp_to_object_dist_end":0.07503,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `5836f8a66456087ed82e2e1accc6472c2a7681a19bf8e3d54637158aadaafc47`; realized-scene SHA-256: `776f3cbcac69f75f44cb26f0b1a492bbf1ced59f3c5fca79400c3f557c2ce565`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46286,-7e-05,0.03]},{"name":"goal","value":[0.61015,0.15287,0.12219]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.46286,-7e-05,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61015,0.15287,0.12219]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67083,"average_solve_count":240.0,"average_success_count":240.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07848,"grasp_1.grip_force":18.48215,"pull_1.pull_distance":0.11613,"push_1.push_distance":0.15469,"push_1.push_speed":0.06277,"rotate_1.yaw_angle":1.05166},"optimized_scores":{"best_composite_score":-0.15375,"best_fitness_score":0.29625,"best_task_score":0.15893},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2864.0,"contact_point_centroid":[0.42436,-0.0229,-0.00232],"force_p95":0.23324,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.77544,"mean_force":0.14223,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.44889,-0.00892,0.0364]},{"body_a":"world","body_b":"grasp_target","contact_count":3219.0,"contact_point_centroid":[0.46235,-0.00082,-0.00236],"force_p95":0.30495,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68202,"mean_force":0.15032,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53063,0.10795,0.06813]},{"body_a":"world","body_b":"grasp_target","contact_count":1333.0,"contact_point_centroid":[0.41204,-0.0229,-0.00211],"force_p95":0.331,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6238,"mean_force":0.14422,"phase_index":6.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.42219,-0.01901,0.07341]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":956.0,"contact_point_centroid":[0.41881,-0.03501,0.0471],"force_p95":0.39736,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44927,"mean_force":0.24879,"phase_index":6.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.42735,-0.01847,0.04798]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2361.0,"contact_point_centroid":[0.42435,-0.00068,0.04269],"force_p95":0.21632,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42974,"mean_force":0.11902,"phase_index":6.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.42805,-0.01839,0.04407]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.42207,-0.0209,-0.00287],"force_p95":0.28589,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35463,"mean_force":0.19162,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4365,-0.01806,0.02888]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":241.0,"contact_point_centroid":[0.45133,-0.03597,0.0388],"force_p95":0.13627,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33639,"mean_force":0.08392,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.46089,0.00626,0.04113]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2656.0,"contact_point_centroid":[0.42685,-0.04547,0.02999],"force_p95":0.20497,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23134,"mean_force":0.1261,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.43551,-0.01805,0.02798]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2775.0,"contact_point_centroid":[0.4329,0.00745,0.02765],"force_p95":0.21924,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2215,"mean_force":0.11489,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.43533,-0.01804,0.02782]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":675.0,"contact_point_centroid":[0.46987,-0.01391,0.04494],"force_p95":0.17307,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21036,"mean_force":0.10946,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47731,0.0284,0.04825]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.46286,-7e-05,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.53682,0.07971,0.21414]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.57881,0.20088,0.19629]},{"body_a":"world","body_b":"grasp_target","contact_count":3316.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.59155,0.20999,0.18358]},{"body_a":"left_finger","body_b":"right_finger","contact_count":549.0,"contact_point_centroid":[0.41848,-0.0195,0.0979],"force_p95":0.0138,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01652,"mean_force":0.01105,"phase_index":6.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.41762,-0.01949,0.09589]}],"total_contact_groups":14},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.42171,-0.01841,0.01602],"final_tcp_position":[0.41616,-0.01967,0.10438],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":1.22657,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.57391,0.15482,0.13706],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22058,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58999,0.22216,0.28073],"tcp_start":[0.57391,0.15482,0.13706],"tcp_to_object_dist_end":0.36115,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":829.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3316.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59499,0.19917,0.09751],"tcp_start":[0.58999,0.22216,0.28073],"tcp_to_object_dist_end":0.24953,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":840.0,"n_steps_budget":1000.0,"object_pos_end":[0.44728,-0.01927,0.01939],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.25831,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":1.22657,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3894.0,"raw_peak_contact_force":0.68202,"tcp_end":[0.46465,0.00941,0.04355],"tcp_start":[0.59499,0.19917,0.09751],"tcp_to_object_dist_end":0.04133,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":791.0,"n_steps_budget":1000.0,"object_pos_end":[0.42257,-0.02279,0.01602],"object_pos_start":[0.44728,-0.01927,0.01939],"object_to_goal_dist_end":0.27805,"object_to_goal_dist_start":0.25831,"object_z_max":0.01939,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3105.0,"raw_peak_contact_force":0.77544,"tcp_end":[0.44315,-0.01811,0.03501],"tcp_start":[0.46465,0.00941,0.04355],"tcp_to_object_dist_end":0.02839,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.41918,-0.01986,0.01387],"object_pos_start":[0.42257,-0.02279,0.01602],"object_to_goal_dist_end":0.27935,"object_to_goal_dist_start":0.27805,"object_z_max":0.01602,"peak_contact_force":0.24752,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7231.0,"raw_peak_contact_force":0.35463,"tcp_end":[0.43531,-0.01802,0.02779],"tcp_start":[0.44315,-0.01811,0.03501],"tcp_to_object_dist_end":0.02138,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":596.0,"n_steps_budget":1000.0,"object_pos_end":[0.42171,-0.01841,0.01602],"object_pos_start":[0.41918,-0.01986,0.01387],"object_to_goal_dist_end":0.2759,"object_to_goal_dist_start":0.27935,"object_z_max":0.03741,"peak_contact_force":0.12264,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5199.0,"raw_peak_contact_force":0.6238,"tcp_end":[0.41616,-0.01967,0.10438],"tcp_start":[0.43531,-0.01802,0.02779],"tcp_to_object_dist_end":0.08854,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```