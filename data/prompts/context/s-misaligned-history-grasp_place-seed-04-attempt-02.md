## Search State

- **Seed**: 4
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13  | 0.0580 | 0.20 | ❌ rejected |
| 1 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6  | 0.0580 | 0.20 | ✅ accepted |
| 0 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6  | -0.4835 | 0.20 | ❌ rejected |

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

## Current Skill (Q=-0.484) — your mutation base

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

- **Composite score**: -0.484
- **task_score** (E): 0.203
- **fitness_score**: 0.221  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.830

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1552 |
| descend_grasp | 1.00 | 1.00 | 0.0038 |
| grasp | 1.00 | 1.00 | 0.0123 |
| lift | 1.00 | 1.00 | 0.1522 |
| transport_to_goal | 1.00 | 1.00 | 0.2102 |
| descend_place | 1.00 | 1.00 | 0.1384 |
| release | 1.00 | 1.00 | 0.0203 |
| retract | 1.00 | 1.00 | 0.1392 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.519, 0.005, 0.148) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / force_exceeded | (0.519, 0.005, 0.148)→(0.518, 0.005, 0.145) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 153.253 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.518, 0.005, 0.145)→(0.511, 0.004, 0.135) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 8.000 | 0.123 | 0.123 |
| lift | lift | 1.00 / step_budget | (0.511, 0.004, 0.135)→(0.509, 0.004, 0.287) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 8.333 | 94250.953 | 0.123 |
| transport_to_goal | approach | 1.00 / step_budget | (0.509, 0.004, 0.287)→(0.603, 0.162, 0.333) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 8.667 | 182004.998 | 0.123 |
| descend_place | descend | 1.00 / step_budget | (0.603, 0.162, 0.333)→(0.608, 0.172, 0.195) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 8.000 | 3249.669 | 0.123 |
| release | release | 1.00 / step_budget | (0.608, 0.172, 0.195)→(0.602, 0.170, 0.214) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.602, 0.170, 0.214)→(0.610, 0.174, 0.353) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.295
- phase_score: 0.192
- phase_breakdown.reach_goal_score: 0.056
- phase_breakdown.reach_above_object_score: 0.512
- grasp_place_fitness: 0.270

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.270
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.295
- **Median Q (composite search score)**: -0.489
- **K-run variance**: 0.0014
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.329


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.31847,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.10048,"approach_above.approach_speed":0.15688,"descend_grasp.descend_force_threshold":2.87567,"descend_grasp.descend_speed":0.06481,"descend_grasp.grasp_offset_z":0.04515,"descend_place.place_offset_z":-0.01066,"descend_place.place_speed":0.07934,"lift.lift_height":0.12702,"lift.lift_speed":0.08798,"release.release_duration":0.16078,"retract.retract_speed":0.22474,"transport_to_goal.approach_goal_height":0.19119,"transport_to_goal.transport_speed":0.17097},"optimized_scores":{"best_composite_score":-0.48935,"best_fitness_score":0.21565,"best_task_score":0.18872},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1156.0,"contact_point_centroid":[0.54431,0.00113,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51633,0.00044,0.22506]},{"body_a":"world","body_b":"grasp_target","contact_count":56.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53416,0.00089,0.14546]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52748,0.00077,0.13455]},{"body_a":"world","body_b":"grasp_target","contact_count":812.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52366,0.0007,0.17954]},{"body_a":"world","body_b":"grasp_target","contact_count":2788.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5824,0.07735,0.29786]},{"body_a":"world","body_b":"grasp_target","contact_count":1140.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.64139,0.15262,0.28505]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63926,0.15487,0.19861]},{"body_a":"world","body_b":"grasp_target","contact_count":1168.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.64068,0.15558,0.2886]},{"body_a":"left_finger","body_b":"right_finger","contact_count":333.0,"contact_point_centroid":[0.52666,0.00075,0.13493],"force_p95":0.01467,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01134,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52642,0.00075,0.13302]},{"body_a":"left_finger","body_b":"right_finger","contact_count":860.0,"contact_point_centroid":[0.52401,0.0007,0.18189],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01288,"mean_force":0.01051,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52366,0.0007,0.17973]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.64125,0.15534,0.19689],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01272,"mean_force":0.01008,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.64157,0.15552,0.19459]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3007.0,"contact_point_centroid":[0.58256,0.07745,0.30041],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.01035,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58253,0.07752,0.29801]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1233.0,"contact_point_centroid":[0.6409,0.15243,0.28668],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01268,"mean_force":0.01033,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.6414,0.15264,0.28456]}],"total_contact_groups":13},"final_pose_error":0.02957,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.54431,0.00113,0.02602],"final_tcp_position":[0.64532,0.15721,0.36164],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273006.81474,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":290.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1156.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.53485,0.00091,0.14785],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1222,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":14.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":81.14226,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":56.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5336,0.00088,0.14335],"tcp_start":[0.53485,0.00091,0.14785],"tcp_to_object_dist_end":0.11782,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2133.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52642,0.00075,0.13302],"tcp_start":[0.5336,0.00088,0.14335],"tcp_to_object_dist_end":0.10849,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":203.0,"n_steps_budget":900.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":9748.77868,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1672.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52366,0.00069,0.23045],"tcp_start":[0.52642,0.00075,0.13302],"tcp_to_object_dist_end":0.20547,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":697.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":273006.81474,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5795.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.63998,0.1497,0.3659],"tcp_start":[0.52366,0.00069,0.23045],"tcp_to_object_dist_end":0.38307,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":285.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2373.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.64355,0.15596,0.19984],"tcp_start":[0.63998,0.1497,0.3659],"tcp_to_object_dist_end":0.25305,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63786,0.15447,0.21818],"tcp_start":[0.64355,0.15596,0.19984],"tcp_to_object_dist_end":0.26304,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":292.0,"n_steps_budget":600.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.64532,0.15721,0.36164],"tcp_start":[0.63786,0.15447,0.21818],"tcp_to_object_dist_end":0.38367,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64315,"average_solve_count":241.0,"average_success_count":241.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.1002,"approach_above.approach_speed":0.07104,"descend_grasp.descend_force_threshold":6.01786,"descend_grasp.descend_speed":0.05717,"descend_grasp.grasp_offset_z":0.01118,"descend_place.place_offset_z":-0.00077,"descend_place.place_speed":0.03632,"lift.lift_height":0.22695,"lift.lift_speed":0.08869,"release.release_duration":0.35607,"retract.retract_speed":0.24839,"transport_to_goal.approach_goal_height":0.14319,"transport_to_goal.transport_speed":0.13579},"optimized_scores":{"best_composite_score":-0.43547,"best_fitness_score":0.26953,"best_task_score":0.29452},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1240.0,"contact_point_centroid":[0.5305,0.03079,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51025,0.01267,0.22521]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52176,0.0265,0.14455]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51503,0.02618,0.13339]},{"body_a":"world","body_b":"grasp_target","contact_count":1600.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51149,0.02594,0.22844]},{"body_a":"world","body_b":"grasp_target","contact_count":1584.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55046,0.09354,0.28858]},{"body_a":"world","body_b":"grasp_target","contact_count":952.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59191,0.16796,0.19027]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59032,0.173,0.12523]},{"body_a":"world","body_b":"grasp_target","contact_count":1080.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.59199,0.17435,0.21042]},{"body_a":"left_finger","body_b":"right_finger","contact_count":341.0,"contact_point_centroid":[0.51437,0.02611,0.13427],"force_p95":0.01478,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01786,"mean_force":0.01112,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51397,0.02612,0.13192]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1009.0,"contact_point_centroid":[0.59212,0.16781,0.19265],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01282,"mean_force":0.01051,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59191,0.16796,0.1902]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1743.0,"contact_point_centroid":[0.5118,0.02593,0.2312],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01275,"mean_force":0.01025,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51149,0.02594,0.22884]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1719.0,"contact_point_centroid":[0.55092,0.09352,0.29097],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01264,"mean_force":0.01029,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55047,0.09356,0.28858]},{"body_a":"left_finger","body_b":"right_finger","contact_count":218.0,"contact_point_centroid":[0.59358,0.17383,0.12315],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01256,"mean_force":0.01018,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59324,0.17393,0.12084]}],"total_contact_groups":13},"final_pose_error":0.02986,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.5305,0.03079,0.02602],"final_tcp_position":[0.59778,0.177,0.27851],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273008.05614,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":311.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1240.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.5228,0.02634,0.14773],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12203,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":21.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":84.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52111,0.02653,0.14185],"tcp_start":[0.5228,0.02634,0.14773],"tcp_to_object_dist_end":0.11629,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2141.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51397,0.02612,0.13192],"tcp_start":[0.52111,0.02653,0.14185],"tcp_to_object_dist_end":0.10729,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":400.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":273003.95685,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3343.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51232,0.02597,0.32928],"tcp_start":[0.51397,0.02612,0.13192],"tcp_to_object_dist_end":0.30384,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":396.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":273008.05614,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3303.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.59002,0.16236,0.25127],"tcp_start":[0.51232,0.02597,0.32928],"tcp_to_object_dist_end":0.26756,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":238.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":9748.76207,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1961.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59565,0.17447,0.12552],"tcp_start":[0.59002,0.16236,0.25127],"tcp_to_object_dist_end":0.18651,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58852,0.17243,0.14512],"tcp_start":[0.59565,0.17447,0.12552],"tcp_to_object_dist_end":0.19394,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":270.0,"n_steps_budget":600.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1080.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59778,0.177,0.27851],"tcp_start":[0.58852,0.17243,0.14512],"tcp_to_object_dist_end":0.29942,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81283,"average_solve_count":187.0,"average_success_count":187.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.10065,"approach_above.approach_speed":0.14571,"descend_grasp.descend_force_threshold":2.95654,"descend_grasp.descend_speed":0.06676,"descend_grasp.grasp_offset_z":0.03948,"descend_place.place_offset_z":-0.00898,"descend_place.place_speed":0.0604,"lift.lift_height":0.1916,"lift.lift_speed":0.09121,"release.release_duration":0.26046,"retract.retract_speed":0.19895,"transport_to_goal.approach_goal_height":0.14559,"transport_to_goal.transport_speed":0.10296},"optimized_scores":{"best_composite_score":-0.52572,"best_fitness_score":0.17928,"best_task_score":0.12474},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1100.0,"contact_point_centroid":[0.50382,-0.01567,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49936,-0.00643,0.22628]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.49995,-0.01337,0.14978]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49357,-0.01341,0.14078]},{"body_a":"world","body_b":"grasp_target","contact_count":1296.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49011,-0.01339,0.21831]},{"body_a":"world","body_b":"grasp_target","contact_count":2600.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53516,0.08224,0.33939]},{"body_a":"world","body_b":"grasp_target","contact_count":908.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.58139,0.17918,0.32142]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58014,0.18315,0.25853]},{"body_a":"world","body_b":"grasp_target","contact_count":1104.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.58159,0.18435,0.34708]},{"body_a":"left_finger","body_b":"right_finger","contact_count":335.0,"contact_point_centroid":[0.49295,-0.0134,0.1418],"force_p95":0.0143,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01129,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49256,-0.0134,0.13944]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1400.0,"contact_point_centroid":[0.49079,-0.01339,0.22071],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01279,"mean_force":0.01033,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4901,-0.01339,0.21853]},{"body_a":"left_finger","body_b":"right_finger","contact_count":977.0,"contact_point_centroid":[0.58127,0.17902,0.32361],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01269,"mean_force":0.01037,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.58139,0.17918,0.32132]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2815.0,"contact_point_centroid":[0.53529,0.08208,0.34175],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01268,"mean_force":0.01031,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53511,0.08213,0.33935]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.58161,0.1836,0.25635],"force_p95":0.01086,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01088,"mean_force":0.00992,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58197,0.18383,0.25401]}],"total_contact_groups":13},"final_pose_error":0.02957,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.50382,-0.01567,0.02602],"final_tcp_position":[0.58541,0.18649,0.4186],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":297.47423,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":276.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1100.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.49995,-0.01337,0.14978],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12384,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":297.47423,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49981,-0.01341,0.14929],"tcp_start":[0.49995,-0.01337,0.14978],"tcp_to_object_dist_end":0.12336,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2135.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49256,-0.0134,0.13944],"tcp_start":[0.49981,-0.01341,0.14929],"tcp_to_object_dist_end":0.114,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":324.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":2696.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49065,-0.0134,0.30134],"tcp_start":[0.49256,-0.0134,0.13944],"tcp_to_object_dist_end":0.27564,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":650.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5415.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.57989,0.17465,0.38039],"tcp_start":[0.49065,-0.0134,0.30134],"tcp_to_object_dist_end":0.40938,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":227.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1885.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58346,0.18422,0.25827],"tcp_start":[0.57989,0.17465,0.38039],"tcp_to_object_dist_end":0.31661,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57909,0.18274,0.27853],"tcp_start":[0.58346,0.18422,0.25827],"tcp_to_object_dist_end":0.32984,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":276.0,"n_steps_budget":600.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1104.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58541,0.18649,0.4186],"tcp_start":[0.57909,0.18274,0.27853],"tcp_to_object_dist_end":0.44905,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```