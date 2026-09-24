## Search State

- **Seed**: 4
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.1790 | 0.20 | ❌ rejected |
| 4 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0580 | 0.20 | ❌ rejected |
| 3 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0580 | 0.20 | ❌ rejected |
| 2 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0580 | 0.20 | ❌ rejected |
| 1 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0580 | 0.20 | ❌ rejected |

**Proposal policy**: task_score is 0.20 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: grasp_place
- Frozen realised-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`
- Frozen object start: [0.5443056105572368, 0.0011327552814361583, 0.03]
- Frozen task target: [0.6476243705707704, 0.15808360238956023, 0.19110337479925443]
- Goal object position: (0.6476243705707704, 0.15808360238956023, 0.19110337479925443)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6476243705707704, 0.15808360238956023, 0.19110337479925443)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5443056105572368, 0.0011327552814361583, 0.03)
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
  frozen_object_start: [0.5443, 0.0011, 0.03]
  frozen_task_target: [0.6476, 0.1581, 0.1911]
  frozen_object_starts: {'grasp_target': [0.5443056105572368, 0.0011327552814361583, 0.03]}
  frozen_targets: {'place_target': [0.6476243705707704, 0.15808360238956023, 0.19110337479925443]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8

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
| `object` | offset from object initial position (0.5443056105572368, 0.0011327552814361583, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6476243705707704, 0.15808360238956023, 0.19110337479925443) | final destination targets |
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

## Current Skill (Q=-0.179) — your mutation base

```yaml
skill: grasp_place
skill_type: arm_gripper
phases:
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: release_1
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
- id: insert_1
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: force_exceeded
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.15
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: -0.179
- **task_score** (E): 0.203
- **fitness_score**: 0.228  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.143
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.550

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_object | 1.00 | 1.00 | 0.1664 |
| descend_to_grasp | 1.00 | 1.00 | 0.0009 |
| grasp_object | 1.00 | 1.00 | 0.0000 |
| lift_object | 1.00 | 1.00 | 0.0574 |
| approach_goal | 1.00 | 1.00 | 0.2097 |
| descend_to_place | 1.00 | 1.00 | 0.1232 |
| release_and_retract | 1.00 | 1.00 | 0.1266 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.520, 0.005, 0.137) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 67.864 | 0.123 |
| descend_to_grasp | descend | 1.00 / force_exceeded | (0.520, 0.005, 0.137)→(0.520, 0.005, 0.137) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 8.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.513, 0.005, 0.127)→(0.513, 0.005, 0.127) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 8.333 | 94251.025 | 0.123 |
| lift_object | lift | 1.00 / step_budget | (0.513, 0.005, 0.127)→(0.522, 0.005, 0.184) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 8.333 | 94252.421 | 0.123 |
| approach_goal | approach | 1.00 / step_budget | (0.522, 0.005, 0.184)→(0.599, 0.154, 0.306) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 8.000 | 3249.698 | 0.123 |
| descend_to_place | descend | 1.00 / step_budget | (0.599, 0.154, 0.306)→(0.607, 0.170, 0.184) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| release_and_retract | release | 1.00 / step_budget | (0.607, 0.170, 0.184)→(0.608, 0.173, 0.311) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 10.500 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.295
- phase_score: 0.337
- phase_breakdown.grasp_contact_score: 0.214
- phase_breakdown.reach_object_score: 0.821
- phase_breakdown.place_goal_score: 0.066
- grasp_place_fitness: 0.274

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.274
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.295
- **Median Q (composite search score)**: -0.184
- **K-run variance**: 0.0013
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 5.3
- **Final σ (mean)**: 0.277


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `104d9d5641b6f93313b49acc931f841aa27a6ce63eca9eff4a16c33838e2c9c3`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `9de75aa839370ff688dada9a37e29517e2f368ed4f09f6a013379103594581cf`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.98529,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_speed":0.0773,"approach_goal.transport_speed":0.27565,"descend_to_grasp.contact_force_threshold":3.9574,"descend_to_grasp.descend_offset_z":-0.02354,"descend_to_place.place_offset_z":-0.00523,"lift_object.lift_height":0.17048,"lift_object.lift_speed":0.28259,"release_and_retract.retract_speed":0.44158},"optimized_scores":{"best_composite_score":-0.18449,"best_fitness_score":0.22265,"best_task_score":0.18872},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2240.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13156,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.51718,0.00048,0.21758]},{"body_a":"world","body_b":"grasp_target","contact_count":20.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53683,0.00099,0.136]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5303,0.00088,0.12621]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5328,0.00094,0.15346]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58417,0.06943,0.2463]},{"body_a":"world","body_b":"grasp_target","contact_count":956.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63637,0.14511,0.25678]},{"body_a":"world","body_b":"grasp_target","contact_count":2652.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_and_retract","phase_type":"release","tcp_position_centroid":[0.64235,0.15534,0.25628]},{"body_a":"left_finger","body_b":"right_finger","contact_count":763.0,"contact_point_centroid":[0.52956,0.00087,0.12729],"force_p95":0.01272,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01079,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52942,0.00087,0.12498]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2147.0,"contact_point_centroid":[0.53302,0.00094,0.15572],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0129,"mean_force":0.01064,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53281,0.00094,0.15348]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4289.0,"contact_point_centroid":[0.58455,0.06955,0.24871],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.0104,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58425,0.06955,0.24641]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1015.0,"contact_point_centroid":[0.6368,0.14517,0.25872],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0127,"mean_force":0.01049,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6364,0.14516,0.2564]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2204.0,"contact_point_centroid":[0.6424,0.15501,0.24596],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0127,"mean_force":0.01038,"phase_index":6.0,"phase_name":"release_and_retract","phase_type":"release","tcp_position_centroid":[0.6419,0.15498,0.24366]}],"total_contact_groups":12},"final_pose_error":0.01749,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.54431,0.00113,0.02602],"final_tcp_position":[0.6451,0.15705,0.29383],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":561.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":81.14225,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53696,0.00099,0.13648],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1107,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2963.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.53668,0.00098,0.13524],"tcp_start":[0.53696,0.00099,0.13648],"tcp_to_object_dist_end":0.10949,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":4199.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52942,0.00087,0.12498],"tcp_start":[0.52942,0.00087,0.12498],"tcp_to_object_dist_end":0.10008,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8289.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53949,0.00105,0.18509],"tcp_start":[0.52942,0.00087,0.12498],"tcp_to_object_dist_end":0.15915,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1971.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.6321,0.13766,0.31261],"tcp_start":[0.53949,0.00105,0.18509],"tcp_to_object_dist_end":0.32936,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":239.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4856.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.64182,0.15365,0.19848],"tcp_start":[0.6321,0.13766,0.31261],"tcp_to_object_dist_end":0.25003,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":31.2553,"phase_name":"release_and_retract","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2240.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.64365,0.15645,0.3184],"tcp_start":[0.64182,0.15365,0.19848],"tcp_to_object_dist_end":0.34566,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `349f925163f8e9284ad51ad55d38356f2e3c8deb4dc54e8ff12260e5f6d4b0f8`; realized-scene SHA-256: `e32d7866764afb23ec7c7faebb4bcca0aa39fbf2f1ab61f3c9c527b297153af9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.08108,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_speed":0.38335,"approach_goal.transport_speed":0.21165,"descend_to_grasp.contact_force_threshold":6.22885,"descend_to_grasp.descend_offset_z":-0.05916,"descend_to_place.place_offset_z":-0.01329,"lift_object.lift_height":0.15942,"lift_object.lift_speed":0.25802,"release_and_retract.retract_speed":0.29617},"optimized_scores":{"best_composite_score":-0.13318,"best_fitness_score":0.27396,"best_task_score":0.29452},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1888.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.51099,0.0139,0.21782]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51783,0.0279,0.1282]},{"body_a":"world","body_b":"grasp_target","contact_count":1936.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52,0.02907,0.15046]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55792,0.09889,0.20726]},{"body_a":"world","body_b":"grasp_target","contact_count":1156.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59305,0.16925,0.17615]},{"body_a":"world","body_b":"grasp_target","contact_count":2652.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_and_retract","phase_type":"release","tcp_position_centroid":[0.5951,0.17583,0.17122]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52416,0.0282,0.13706]},{"body_a":"left_finger","body_b":"right_finger","contact_count":761.0,"contact_point_centroid":[0.5173,0.02785,0.1292],"force_p95":0.01253,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01566,"mean_force":0.01083,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51697,0.02785,0.12702]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2202.0,"contact_point_centroid":[0.5955,0.17566,0.15965],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01286,"mean_force":0.01039,"phase_index":6.0,"phase_name":"release_and_retract","phase_type":"release","tcp_position_centroid":[0.59486,0.17562,0.15736]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4264.0,"contact_point_centroid":[0.5584,0.09914,0.20962],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.01046,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55804,0.09913,0.20738]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1224.0,"contact_point_centroid":[0.5935,0.16927,0.17854],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01277,"mean_force":0.01052,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59305,0.16925,0.17624]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2049.0,"contact_point_centroid":[0.5202,0.02907,0.15268],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.01052,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51998,0.02906,0.15035]}],"total_contact_groups":12},"final_pose_error":0.01719,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.5305,0.03079,0.02602],"final_tcp_position":[0.59789,0.17725,0.21135],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":9748.84913,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":473.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":81.14225,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12262,"subtask_id":"reach_object","tcp_end":[0.52416,0.0282,0.13706],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11125,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2961.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.52407,0.02823,0.13681],"tcp_start":[0.52416,0.0282,0.13706],"tcp_to_object_dist_end":0.11101,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":9748.56598,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3985.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51697,0.02785,0.12702],"tcp_start":[0.51697,0.02785,0.12702],"tcp_to_object_dist_end":0.10194,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":9748.79083,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8264.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52568,0.03033,0.17505],"tcp_start":[0.51697,0.02785,0.12702],"tcp_to_object_dist_end":0.14911,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":9748.84913,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2380.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.5917,0.16422,0.2426],"tcp_start":[0.52568,0.03033,0.17505],"tcp_to_object_dist_end":0.26164,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":289.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4854.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59592,0.17519,0.10785],"tcp_start":[0.5917,0.16422,0.2426],"tcp_to_object_dist_end":0.1784,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"release_and_retract","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1888.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.5953,0.17629,0.23702],"tcp_start":[0.59592,0.17519,0.10785],"tcp_to_object_dist_end":0.26437,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a1798e4fdcacfe8740623adfe3f78d2bc74e0d14c8233e64f02c40cf2a534ecc`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.22807,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_speed":0.14628,"approach_goal.transport_speed":0.32838,"descend_to_grasp.contact_force_threshold":3.89864,"descend_to_grasp.descend_offset_z":-0.03806,"descend_to_place.place_offset_z":-0.01438,"lift_object.lift_height":0.17553,"lift_object.lift_speed":0.27102,"release_and_retract.retract_speed":0.2683},"optimized_scores":{"best_composite_score":-0.21927,"best_fitness_score":0.18787,"best_task_score":0.12474},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1852.0,"contact_point_centroid":[0.50382,-0.01567,-0.00192],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.49886,-0.00698,0.21952]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49322,-0.01428,0.12982]},{"body_a":"world","body_b":"grasp_target","contact_count":2032.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49432,-0.01488,0.15878]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53456,0.07104,0.27343]},{"body_a":"world","body_b":"grasp_target","contact_count":1024.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57771,0.17025,0.30574]},{"body_a":"world","body_b":"grasp_target","contact_count":2652.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_and_retract","phase_type":"release","tcp_position_centroid":[0.58299,0.18435,0.31103]},{"body_a":"world","body_b":"grasp_target","contact_count":16.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4995,-0.01433,0.13835]},{"body_a":"left_finger","body_b":"right_finger","contact_count":743.0,"contact_point_centroid":[0.49258,-0.01426,0.13099],"force_p95":0.01318,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01566,"mean_force":0.01106,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49238,-0.01426,0.12875]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2202.0,"contact_point_centroid":[0.58318,0.1839,0.29926],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.01039,"phase_index":6.0,"phase_name":"release_and_retract","phase_type":"release","tcp_position_centroid":[0.58256,0.18387,0.29703]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2115.0,"contact_point_centroid":[0.49449,-0.01488,0.16114],"force_p95":0.01106,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01069,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49434,-0.01488,0.15888]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4267.0,"contact_point_centroid":[0.53481,0.07085,0.27551],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01045,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53447,0.07085,0.27324]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1085.0,"contact_point_centroid":[0.5781,0.17034,0.3076],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.01051,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57774,0.17033,0.30532]}],"total_contact_groups":12},"final_pose_error":0.01675,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.50382,-0.01567,0.02602],"final_tcp_position":[0.58516,0.1864,0.35149],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273008.34861,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":464.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":41.30761,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16.0,"raw_peak_contact_force":0.12262,"subtask_id":"reach_object","tcp_end":[0.49965,-0.0143,0.13873],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1128,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2943.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.49932,-0.01436,0.13773],"tcp_start":[0.49965,-0.0143,0.13873],"tcp_to_object_dist_end":0.11181,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":273004.38611,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":4147.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49238,-0.01426,0.12875],"tcp_start":[0.49238,-0.01426,0.12875],"tcp_to_object_dist_end":0.10337,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":508.0,"n_steps_budget":600.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":273008.34861,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8267.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.4994,-0.01551,0.19084],"tcp_start":[0.49238,-0.01426,0.12875],"tcp_to_object_dist_end":0.16488,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2109.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.57386,0.15983,0.36284],"tcp_start":[0.4994,-0.01551,0.19084],"tcp_to_object_dist_end":0.38621,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":256.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4854.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58248,0.18209,0.24667],"tcp_start":[0.57386,0.15983,0.36284],"tcp_to_object_dist_end":0.30657,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"release_and_retract","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1852.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.58438,0.18583,0.37728],"tcp_start":[0.58248,0.18209,0.24667],"tcp_to_object_dist_end":0.41289,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```