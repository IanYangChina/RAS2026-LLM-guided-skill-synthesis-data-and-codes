## Search State

- **Seed**: 8
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 2 | 0.3457 | 0.14 | ✅ accepted |

**Proposal policy**: task_score is 0.14 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`
- Frozen object start: [0.48269722766055606, 0.048727684333792556, 0.03]
- Frozen task target: [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]
- Goal object position: (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.48269722766055606, 0.048727684333792556, 0.03)
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
  frozen_object_start: [0.4827, 0.0487, 0.03]
  frozen_task_target: [0.5819, 0.2289, 0.2305]
  frozen_object_starts: {'grasp_target': [0.48269722766055606, 0.048727684333792556, 0.03]}
  frozen_targets: {'place_target': [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c

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
| `object` | offset from object initial position (0.48269722766055606, 0.048727684333792556, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5818710838485517, 0.2288548935820029, 0.2304844767544324) | final destination targets |
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

## Current Skill (Q=0.346) — your mutation base

```yaml
skill: grasp_place
skill_type: arm_gripper
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  parameters:
    grip_force:
      type: scalar
      range:
      - 5.0
      - 30.0
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open

```

## Design Metrics

- **Composite score**: 0.346
- **task_score** (E): 0.143
- **fitness_score**: 0.536  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.190

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1103 |
| descend_1 | 1.00 | 1.00 | 0.1488 |
| grasp_1 | 1.00 | 1.00 | 0.0130 |
| lift_1 | 1.00 | 1.00 | 0.1604 |
| release_1 | 1.00 | 1.00 | 0.0249 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.515, 0.000, 0.203) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.515, 0.000, 0.203)→(0.516, -0.001, 0.054) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.516, -0.001, 0.054)→(0.508, -0.001, 0.044) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.290 | 1.00 / 47.667 | 0.146 | 0.188 |
| lift_1 | lift | 1.00 / step_budget | (0.508, -0.001, 0.044)→(0.517, -0.001, 0.205) | (0.522, -0.001, 0.026)→(0.525, -0.001, 0.179) | 0.290→0.228 | 1.00 / 38.000 | 0.081 | 0.475 |
| release_1 | release | 1.00 / step_budget | (0.517, -0.001, 0.205)→(0.512, -0.001, 0.229) | (0.525, -0.001, 0.179)→(0.515, -0.001, 0.023) | 0.228→0.293 | 1.00 / 2.000 | 0.206 | 1.614 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.172
- phase_score: 0.240
- phase_breakdown.approach_1_score: 0.022
- phase_breakdown.descend_1_score: 0.871
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.000
- phase_breakdown.release_1_score: 0.012
- grasp_place_fitness: 0.551

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.551
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.172
- **Median Q (composite search score)**: 0.342
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 11.0
- **Final σ (mean)**: 0.283


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2cbd02033d1f1347f2ac2d0b012406a96501e6b48f5b172bd88b34d6c745630c`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5745d7c2d025a63f908a4bf0f58182445bb06541d436718f39304ac5569d60c0`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09988,"grasp_1.grip_force":8.7316},"optimized_scores":{"best_composite_score":0.34222,"best_fitness_score":0.53222,"best_task_score":0.13932},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":158.0,"contact_point_centroid":[0.46773,0.03567,-0.00826],"force_p95":1.37058,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.79822,"mean_force":0.47672,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.47354,0.0468,0.22154]},{"body_a":"world","body_b":"grasp_target","contact_count":143.0,"contact_point_centroid":[0.4803,0.04574,-0.00125],"force_p95":0.26379,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44965,"mean_force":0.06418,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46809,0.04658,0.04772]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19464.0,"contact_point_centroid":[0.47144,0.06594,0.12524],"force_p95":0.07796,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28568,"mean_force":0.05243,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47161,0.04679,0.12313]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19894.0,"contact_point_centroid":[0.4735,0.02776,0.12322],"force_p95":0.08278,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2771,"mean_force":0.05164,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47155,0.04679,0.12254]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48277,0.04872,-0.00216],"force_p95":0.16579,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21928,"mean_force":0.1343,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47054,0.04684,0.04695]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1209.0,"contact_point_centroid":[0.47889,0.02807,0.203],"force_p95":0.08073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16754,"mean_force":0.04672,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.47688,0.04717,0.2031]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.47166,0.02763,0.04655],"force_p95":0.07915,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16753,"mean_force":0.04506,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46937,0.04673,0.04574]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1148.0,"contact_point_centroid":[0.47655,0.06632,0.2041],"force_p95":0.07658,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1578,"mean_force":0.04562,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.47696,0.04718,0.2032]},{"body_a":"world","body_b":"grasp_target","contact_count":2396.0,"contact_point_centroid":[0.4827,0.04873,-0.00194],"force_p95":0.13076,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48892,0.0221,0.20399]},{"body_a":"world","body_b":"grasp_target","contact_count":732.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47755,0.04614,0.08126]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4985.0,"contact_point_centroid":[0.46888,0.06598,0.04905],"force_p95":0.07691,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08423,"mean_force":0.04453,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46938,0.04673,0.04574]}],"total_contact_groups":11},"final_pose_error":0.02086,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.47829,0.04696,0.0217],"final_tcp_position":[0.4782,0.04728,0.20509],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.79822,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":600.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2396.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.47969,0.045,0.10843],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08255,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":183.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":732.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.4775,0.0475,0.05427],"tcp_start":[0.47969,0.045,0.10843],"tcp_to_object_dist_end":0.02875,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48277,0.04771,0.02543],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.291,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16411,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11663.0,"raw_peak_contact_force":0.21928,"tcp_end":[0.46934,0.04672,0.04571],"tcp_start":[0.4775,0.0475,0.05427],"tcp_to_object_dist_end":0.02434,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48477,0.04825,0.17829],"object_pos_start":[0.48277,0.04771,0.02543],"object_to_goal_dist_end":0.21159,"object_to_goal_dist_start":0.291,"object_z_max":0.1781,"peak_contact_force":0.08445,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39501.0,"raw_peak_contact_force":0.44965,"tcp_end":[0.4782,0.04728,0.20509],"tcp_start":[0.46934,0.04672,0.04571],"tcp_to_object_dist_end":0.02761,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47829,0.04696,0.0217],"object_pos_start":[0.48477,0.04825,0.17829],"object_to_goal_dist_end":0.29565,"object_to_goal_dist_start":0.21159,"object_z_max":0.17842,"peak_contact_force":0.35111,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2515.0,"raw_peak_contact_force":1.79822,"tcp_end":[0.47346,0.04679,0.23048],"tcp_start":[0.4782,0.04728,0.20509],"tcp_to_object_dist_end":0.20884,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2b35d39beba75b46a5edd8e67b975c00ef2c88fb75a3753bdd32db5918adf9e2`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73333,"average_solve_count":105.0,"average_success_count":105.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.28365,"grasp_1.grip_force":12.6677},"optimized_scores":{"best_composite_score":0.33407,"best_fitness_score":0.52407,"best_task_score":0.11878},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":182.0,"contact_point_centroid":[0.51904,-0.02065,-0.00781],"force_p95":1.40062,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.51495,"mean_force":0.40944,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52733,-0.021,0.21956]},{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.53414,-0.02057,-0.00112],"force_p95":0.32516,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48359,"mean_force":0.07441,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52172,-0.0209,0.04566]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21035.0,"contact_point_centroid":[0.5262,-0.00184,0.12031],"force_p95":0.07617,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31299,"mean_force":0.04909,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52506,-0.02097,0.11839]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19904.0,"contact_point_centroid":[0.5258,-0.04015,0.12347],"force_p95":0.07319,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29996,"mean_force":0.05118,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52526,-0.02097,0.12085]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02135,-0.00204],"force_p95":0.13542,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16617,"mean_force":0.12619,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52428,-0.02094,0.0454]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1170.0,"contact_point_centroid":[0.53156,-0.04024,0.20373],"force_p95":0.07303,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16122,"mean_force":0.04524,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.53093,-0.02107,0.20216]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1172.0,"contact_point_centroid":[0.53241,-0.00194,0.20292],"force_p95":0.07688,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15409,"mean_force":0.04552,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.53092,-0.02107,0.20216]},{"body_a":"world","body_b":"grasp_target","contact_count":908.0,"contact_point_centroid":[0.53702,-0.02132,-0.00186],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12317,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51398,-0.00923,0.28869]},{"body_a":"world","body_b":"grasp_target","contact_count":2696.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52892,-0.01943,0.16631]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5813.0,"contact_point_centroid":[0.52351,-0.00168,0.04679],"force_p95":0.06525,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0945,"mean_force":0.03803,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52304,-0.02092,0.04395]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5126.0,"contact_point_centroid":[0.52343,-0.04022,0.0471],"force_p95":0.06871,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08402,"mean_force":0.04295,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52304,-0.02092,0.04395]}],"total_contact_groups":11},"final_pose_error":0.02199,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.52853,-0.02101,0.02423],"final_tcp_position":[0.53221,-0.0211,0.20434],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.51495,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":228.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":908.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.52837,-0.01788,0.2802],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25435,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":674.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2696.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53168,-0.02104,0.05418],"tcp_start":[0.52837,-0.01788,0.2802],"tcp_to_object_dist_end":0.02866,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":49.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53695,-0.02119,0.02582],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31675,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13522,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12739.0,"raw_peak_contact_force":0.16617,"tcp_end":[0.52301,-0.02092,0.04391],"tcp_start":[0.53168,-0.02104,0.05418],"tcp_to_object_dist_end":0.02284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54005,-0.0215,0.18007],"object_pos_start":[0.53695,-0.02119,0.02582],"object_to_goal_dist_end":0.26041,"object_to_goal_dist_start":0.31675,"object_z_max":0.17989,"peak_contact_force":0.07976,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41083.0,"raw_peak_contact_force":0.48359,"tcp_end":[0.53221,-0.0211,0.20434],"tcp_start":[0.52301,-0.02092,0.04391],"tcp_to_object_dist_end":0.0255,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52853,-0.02101,0.02423],"object_pos_start":[0.54005,-0.0215,0.18007],"object_to_goal_dist_end":0.31958,"object_to_goal_dist_start":0.26041,"object_z_max":0.18021,"peak_contact_force":0.13155,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2524.0,"raw_peak_contact_force":1.51495,"tcp_end":[0.52725,-0.02099,0.22832],"tcp_start":[0.53221,-0.0211,0.20434],"tcp_to_object_dist_end":0.2041,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `530652a2467d9ac78fab654e7ed7fc5283ca1649270bc8f158e04c16074f9f95`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90526,"average_solve_count":95.0,"average_success_count":95.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.21638,"grasp_1.grip_force":13.93107},"optimized_scores":{"best_composite_score":0.36083,"best_fitness_score":0.55083,"best_task_score":0.17199},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.53246,-0.02817,-0.00918],"force_p95":1.43844,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.52804,"mean_force":0.51345,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.53585,-0.02867,0.21851]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.54278,-0.02821,-0.00116],"force_p95":0.3273,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49033,"mean_force":0.07712,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53,-0.02856,0.04522]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21043.0,"contact_point_centroid":[0.53477,-0.00952,0.12002],"force_p95":0.07691,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31322,"mean_force":0.04915,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53347,-0.02865,0.11804]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19943.0,"contact_point_centroid":[0.53399,-0.04783,0.12306],"force_p95":0.07383,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30876,"mean_force":0.05112,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53365,-0.02865,0.12027]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54562,-0.02926,-0.00206],"force_p95":0.14062,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17713,"mean_force":0.12752,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53259,-0.02863,0.04501]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1169.0,"contact_point_centroid":[0.53997,-0.04796,0.20359],"force_p95":0.07353,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16244,"mean_force":0.04525,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.53948,-0.02879,0.20184]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1171.0,"contact_point_centroid":[0.54127,-0.00968,0.20266],"force_p95":0.07742,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15546,"mean_force":0.04558,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.53948,-0.02879,0.20184]},{"body_a":"world","body_b":"grasp_target","contact_count":1336.0,"contact_point_centroid":[0.5456,-0.02923,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51744,-0.01266,0.25909]},{"body_a":"world","body_b":"grasp_target","contact_count":1984.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53726,-0.02723,0.13634]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5799.0,"contact_point_centroid":[0.53187,-0.00934,0.04643],"force_p95":0.06708,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11492,"mean_force":0.03816,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53134,-0.0286,0.04352]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5139.0,"contact_point_centroid":[0.53144,-0.04789,0.04683],"force_p95":0.07136,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07759,"mean_force":0.0429,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53134,-0.0286,0.04352]}],"total_contact_groups":11},"final_pose_error":0.0222,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.53881,-0.02896,0.02432],"final_tcp_position":[0.54077,-0.02883,0.20408],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.52804,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":335.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1336.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.53708,-0.02574,0.21994],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19414,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":496.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1984.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54004,-0.02882,0.05403],"tcp_start":[0.53708,-0.02574,0.21994],"tcp_to_object_dist_end":0.02856,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":49.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54554,-0.02898,0.02576],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26091,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14016,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12738.0,"raw_peak_contact_force":0.17713,"tcp_end":[0.53131,-0.0286,0.04348],"tcp_start":[0.54004,-0.02882,0.05403],"tcp_to_object_dist_end":0.02274,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54876,-0.02937,0.18002],"object_pos_start":[0.54554,-0.02898,0.02576],"object_to_goal_dist_end":0.21173,"object_to_goal_dist_start":0.26091,"object_z_max":0.17983,"peak_contact_force":0.08025,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41132.0,"raw_peak_contact_force":0.49033,"tcp_end":[0.54077,-0.02883,0.20408],"tcp_start":[0.53131,-0.0286,0.04348],"tcp_to_object_dist_end":0.02536,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53881,-0.02896,0.02432],"object_pos_start":[0.54876,-0.02937,0.18002],"object_to_goal_dist_end":0.26405,"object_to_goal_dist_start":0.21173,"object_z_max":0.18016,"peak_contact_force":0.13662,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2486.0,"raw_peak_contact_force":1.52804,"tcp_end":[0.53578,-0.02867,0.2278],"tcp_start":[0.54077,-0.02883,0.20408],"tcp_to_object_dist_end":0.2035,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```