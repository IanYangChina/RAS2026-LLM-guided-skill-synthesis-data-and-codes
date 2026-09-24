## Search State

- **Seed**: 9
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6 | -0.1649 | 0.13 | ✅ accepted |

**Proposal policy**: task_score is 0.13 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
| push_1 | 1.00 | 1.00 | 0.1838 |
| descend_1 | 1.00 | 1.00 | 0.2300 |
| descend_2 | 1.00 | 1.00 | 0.0407 |
| grasp_1 | 1.00 | 1.00 | 0.0121 |
| approach_1 | 1.00 | 1.00 | 0.0763 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| rotate_1 | rotate | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.574, 0.155, 0.137) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| pull_1 | pull | 1.00 / time_limit | (0.574, 0.155, 0.137)→(0.590, 0.222, 0.281) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| push_1 | push | 1.00 / time_limit | (0.590, 0.222, 0.281)→(0.595, 0.199, 0.098) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_1 | descend | 1.00 / step_budget | (0.595, 0.199, 0.098)→(0.514, -0.006, 0.043) | (0.515, -0.017, 0.026)→(0.504, -0.042, 0.015) | 0.270→0.300 | 1.00 / 7.000 | 12.542 | 0.737 |
| descend_2 | descend | 1.00 / step_budget | (0.514, -0.006, 0.043)→(0.500, -0.040, 0.029) | (0.504, -0.042, 0.015)→(0.490, -0.055, 0.012) | 0.300→0.318 | 1.00 / 10.667 | 0.487 | 0.764 |
| grasp_1 | grasp | 1.00 / step_budget | (0.500, -0.040, 0.029)→(0.491, -0.040, 0.021) | (0.490, -0.055, 0.012)→(0.486, -0.045, 0.005) | 0.318→0.316 | 1.00 / 27.667 | 0.673 | 0.709 |
| approach_1 | approach | 1.00 / step_budget | (0.491, -0.040, 0.021)→(0.482, -0.045, 0.096) | (0.486, -0.045, 0.005)→(0.482, -0.042, 0.016) | 0.316→0.309 | 1.00 / 8.333 | 94251.175 | 0.996 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.159
- phase_score: 0.238
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.000
- phase_breakdown.descend_1_score: 0.793
- phase_breakdown.release_1_score: 0.000
- phase_breakdown.approach_1_score: 0.165
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
- **Final σ (mean)**: 0.362


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82547,"average_solve_count":212.0,"average_success_count":212.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0933,"grasp_1.grip_force":17.98885,"pull_1.pull_distance":0.05886,"push_1.push_distance":0.18281,"push_1.push_speed":0.09895,"rotate_1.yaw_angle":0.35645},"optimized_scores":{"best_composite_score":-0.17856,"best_fitness_score":0.27144,"best_task_score":0.09501},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1959.0,"contact_point_centroid":[0.50347,-0.05883,-0.00414],"force_p95":0.70166,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.2613,"mean_force":0.24648,"phase_index":6.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50884,-0.0512,0.05534]},{"body_a":"world","body_b":"grasp_target","contact_count":1678.0,"contact_point_centroid":[0.51198,-0.05451,-0.00842],"force_p95":0.93788,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.95894,"mean_force":0.55973,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51491,-0.04892,0.01738]},{"body_a":"world","body_b":"grasp_target","contact_count":3631.0,"contact_point_centroid":[0.53665,-0.0225,-0.00289],"force_p95":0.59465,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.77869,"mean_force":0.18731,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.56372,0.09726,0.06801]},{"body_a":"world","body_b":"grasp_target","contact_count":3444.0,"contact_point_centroid":[0.52234,-0.05776,-0.00543],"force_p95":0.6576,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71361,"mean_force":0.34531,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.52569,-0.03267,0.03058]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6812.0,"contact_point_centroid":[0.51031,-0.03144,0.03878],"force_p95":0.24283,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.63478,"mean_force":0.09867,"phase_index":6.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50892,-0.05026,0.03983]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4688.0,"contact_point_centroid":[0.50666,-0.06974,0.03229],"force_p95":0.18136,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33242,"mean_force":0.11199,"phase_index":6.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50909,-0.05009,0.037]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8839.0,"contact_point_centroid":[0.52329,-0.07608,0.02527],"force_p95":0.15632,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31188,"mean_force":0.08534,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.52521,-0.03484,0.02987]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1750.0,"contact_point_centroid":[0.54189,-0.02665,0.0442],"force_p95":0.20589,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25043,"mean_force":0.12056,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54191,0.01611,0.04871]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2374.0,"contact_point_centroid":[0.51377,-0.0256,0.01556],"force_p95":0.22277,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24644,"mean_force":0.10605,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51385,-0.04885,0.01621]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5310.0,"contact_point_centroid":[0.51119,-0.08068,0.01453],"force_p95":0.20915,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24121,"mean_force":0.13832,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51507,-0.04892,0.01755]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.53702,-0.02132,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.53682,0.07971,0.21414]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.57881,0.20088,0.19629]},{"body_a":"world","body_b":"grasp_target","contact_count":3004.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.59152,0.21022,0.18531]},{"body_a":"left_finger","body_b":"right_finger","contact_count":609.0,"contact_point_centroid":[0.50891,-0.05305,0.0877],"force_p95":0.0138,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01611,"mean_force":0.01083,"phase_index":6.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50821,-0.05303,0.08564]}],"total_contact_groups":14},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.50051,-0.04787,0.01602],"final_tcp_position":[0.50825,-0.0534,0.09165],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":9748.98845,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.57391,0.15482,0.13706],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21146,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58999,0.22216,0.28073],"tcp_start":[0.57391,0.15482,0.13706],"tcp_to_object_dist_end":0.35632,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":751.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3004.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59496,0.19936,0.09896],"tcp_start":[0.58999,0.22216,0.28073],"tcp_to_object_dist_end":0.23953,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":970.0,"n_steps_budget":1000.0,"object_pos_end":[0.5273,-0.05101,0.01112],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3509,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.62789,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5381.0,"raw_peak_contact_force":0.77869,"tcp_end":[0.53429,-0.01262,0.04195],"tcp_start":[0.59496,0.19936,0.09896],"tcp_to_object_dist_end":0.04973,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":940.0,"n_steps_budget":1000.0,"object_pos_end":[0.51787,-0.06708,0.01052],"object_pos_start":[0.5273,-0.05101,0.01112],"object_to_goal_dist_end":0.36638,"object_to_goal_dist_start":0.3509,"object_z_max":0.01112,"peak_contact_force":0.6987,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12283.0,"raw_peak_contact_force":0.71361,"tcp_end":[0.52235,-0.04922,0.0256],"tcp_start":[0.53429,-0.01262,0.04195],"tcp_to_object_dist_end":0.0238,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51273,-0.0539,0.00053],"object_pos_start":[0.51787,-0.06708,0.01052],"object_to_goal_dist_end":0.36283,"object_to_goal_dist_start":0.36638,"object_z_max":0.01052,"peak_contact_force":0.95915,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9362.0,"raw_peak_contact_force":0.95894,"tcp_end":[0.51384,-0.0488,0.0162],"tcp_start":[0.52235,-0.04922,0.0256],"tcp_to_object_dist_end":0.01651,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":863.0,"n_steps_budget":1000.0,"object_pos_end":[0.50051,-0.04787,0.01602],"object_pos_start":[0.51273,-0.0539,0.00053],"object_to_goal_dist_end":0.35307,"object_to_goal_dist_start":0.36283,"object_z_max":0.03336,"peak_contact_force":9748.98845,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14068.0,"raw_peak_contact_force":1.2613,"tcp_end":[0.50825,-0.0534,0.09165],"tcp_start":[0.51384,-0.0488,0.0162],"tcp_to_object_dist_end":0.07623,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82629,"average_solve_count":213.0,"average_success_count":213.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0848,"grasp_1.grip_force":22.48155,"pull_1.pull_distance":0.17936,"push_1.push_distance":0.07004,"push_1.push_speed":0.09977,"rotate_1.yaw_angle":1.0911},"optimized_scores":{"best_composite_score":-0.16239,"best_fitness_score":0.28761,"best_task_score":0.13705},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2791.0,"contact_point_centroid":[0.52155,-0.06946,-0.00368],"force_p95":0.61447,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.09491,"mean_force":0.2197,"phase_index":6.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52122,-0.05739,0.05647]},{"body_a":"world","body_b":"grasp_target","contact_count":1777.0,"contact_point_centroid":[0.52766,-0.06295,-0.0087],"force_p95":0.79308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.81253,"mean_force":0.57015,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52572,-0.05327,0.01895]},{"body_a":"world","body_b":"grasp_target","contact_count":3629.0,"contact_point_centroid":[0.53358,-0.06258,-0.00523],"force_p95":0.62248,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.80168,"mean_force":0.33323,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.53578,-0.03583,0.03187]},{"body_a":"world","body_b":"grasp_target","contact_count":3812.0,"contact_point_centroid":[0.5453,-0.03015,-0.00273],"force_p95":0.56579,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.75155,"mean_force":0.17655,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.56786,0.09474,0.06817]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6089.0,"contact_point_centroid":[0.52012,-0.03883,0.0341],"force_p95":0.13239,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.51561,"mean_force":0.07497,"phase_index":6.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5207,-0.05533,0.03668]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8920.0,"contact_point_centroid":[0.53382,-0.07839,0.02683],"force_p95":0.14794,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35485,"mean_force":0.08503,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.53554,-0.03742,0.03147]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3743.0,"contact_point_centroid":[0.5205,-0.07374,0.02917],"force_p95":0.21614,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34042,"mean_force":0.12712,"phase_index":6.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52077,-0.05506,0.03408]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5306.0,"contact_point_centroid":[0.52153,-0.08363,0.01615],"force_p95":0.24349,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2758,"mean_force":0.14868,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52574,-0.05327,0.01896]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2808.0,"contact_point_centroid":[0.52373,-0.03243,0.01664],"force_p95":0.15223,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22373,"mean_force":0.07051,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52451,-0.05319,0.01758]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1705.0,"contact_point_centroid":[0.54994,-0.03115,0.04555],"force_p95":0.19586,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21016,"mean_force":0.1095,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54946,0.01179,0.04908]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.5456,-0.02923,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.53682,0.07971,0.21414]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.57881,0.20088,0.19629]},{"body_a":"world","body_b":"grasp_target","contact_count":3004.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.59152,0.21022,0.18531]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1138.0,"contact_point_centroid":[0.52248,-0.05993,0.08331],"force_p95":0.01224,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01576,"mean_force":0.01048,"phase_index":6.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52178,-0.05993,0.08098]}],"total_contact_groups":14},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.52199,-0.06021,0.01602],"final_tcp_position":[0.52223,-0.06098,0.09105],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":273004.41465,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.57391,0.15482,0.13706],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21681,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58999,0.22216,0.28073],"tcp_start":[0.57391,0.15482,0.13706],"tcp_to_object_dist_end":0.36062,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":751.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3004.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59496,0.19936,0.09896],"tcp_start":[0.58999,0.22216,0.28073],"tcp_to_object_dist_end":0.24497,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5381,-0.05559,0.01305],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.29062,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":35.77021,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5517.0,"raw_peak_contact_force":0.75155,"tcp_end":[0.54392,-0.01359,0.0433],"tcp_start":[0.59496,0.19936,0.09896],"tcp_to_object_dist_end":0.05209,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":974.0,"n_steps_budget":1000.0,"object_pos_end":[0.52961,-0.07366,0.00965],"object_pos_start":[0.5381,-0.05559,0.01305],"object_to_goal_dist_end":0.30913,"object_to_goal_dist_start":0.29062,"object_z_max":0.01305,"peak_contact_force":0.64108,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12549.0,"raw_peak_contact_force":0.80168,"tcp_end":[0.53307,-0.05362,0.0273],"tcp_start":[0.54392,-0.01359,0.0433],"tcp_to_object_dist_end":0.02693,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52689,-0.06161,-0.00017],"object_pos_start":[0.52961,-0.07366,0.00965],"object_to_goal_dist_end":0.30644,"object_to_goal_dist_start":0.30913,"object_z_max":0.00965,"peak_contact_force":0.81272,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9891.0,"raw_peak_contact_force":0.81253,"tcp_end":[0.5245,-0.05313,0.01757],"tcp_start":[0.53307,-0.05362,0.0273],"tcp_to_object_dist_end":0.0198,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":941.0,"n_steps_budget":1000.0,"object_pos_end":[0.52199,-0.06021,0.01602],"object_pos_start":[0.52689,-0.06161,-0.00017],"object_to_goal_dist_end":0.29811,"object_to_goal_dist_start":0.30644,"object_z_max":0.02769,"peak_contact_force":273004.41465,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13761.0,"raw_peak_contact_force":1.09491,"tcp_end":[0.52223,-0.06098,0.09105],"tcp_start":[0.5245,-0.05313,0.01757],"tcp_to_object_dist_end":0.07503,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7161,"average_solve_count":236.0,"average_success_count":236.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08084,"grasp_1.grip_force":19.50266,"pull_1.pull_distance":0.05409,"push_1.push_distance":0.12027,"push_1.push_speed":0.0652,"rotate_1.yaw_angle":0.55694},"optimized_scores":{"best_composite_score":-0.15376,"best_fitness_score":0.29624,"best_task_score":0.15892},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2864.0,"contact_point_centroid":[0.42436,-0.02291,-0.00232],"force_p95":0.23325,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.77534,"mean_force":0.14222,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.44889,-0.00892,0.0364]},{"body_a":"world","body_b":"grasp_target","contact_count":3219.0,"contact_point_centroid":[0.46235,-0.00082,-0.00236],"force_p95":0.30486,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68188,"mean_force":0.1503,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53064,0.10795,0.0681]},{"body_a":"world","body_b":"grasp_target","contact_count":1334.0,"contact_point_centroid":[0.41229,-0.0229,-0.00209],"force_p95":0.32596,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63049,"mean_force":0.14303,"phase_index":6.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.42212,-0.01901,0.07348]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":962.0,"contact_point_centroid":[0.41886,-0.03514,0.04691],"force_p95":0.39712,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4675,"mean_force":0.24724,"phase_index":6.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.42743,-0.01847,0.04772]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2385.0,"contact_point_centroid":[0.42431,-0.00069,0.04286],"force_p95":0.21525,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43381,"mean_force":0.11808,"phase_index":6.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.428,-0.01839,0.04424]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.42207,-0.02091,-0.00287],"force_p95":0.28624,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35498,"mean_force":0.19176,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.43649,-0.01807,0.02889]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":241.0,"contact_point_centroid":[0.45133,-0.03597,0.0388],"force_p95":0.13604,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33643,"mean_force":0.08387,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.46089,0.00626,0.04113]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2655.0,"contact_point_centroid":[0.42685,-0.04547,0.02999],"force_p95":0.20496,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22961,"mean_force":0.12616,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4355,-0.01805,0.02798]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2775.0,"contact_point_centroid":[0.4329,0.00744,0.02763],"force_p95":0.21925,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22151,"mean_force":0.11487,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.43533,-0.01804,0.02782]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":675.0,"contact_point_centroid":[0.46987,-0.01391,0.04493],"force_p95":0.173,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21032,"mean_force":0.1094,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47731,0.0284,0.04824]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.46286,-7e-05,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.53682,0.07971,0.21414]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.57881,0.20088,0.19629]},{"body_a":"world","body_b":"grasp_target","contact_count":3272.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.59155,0.21001,0.18373]},{"body_a":"left_finger","body_b":"right_finger","contact_count":549.0,"contact_point_centroid":[0.41868,-0.01952,0.09805],"force_p95":0.01387,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01646,"mean_force":0.0109,"phase_index":6.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.41753,-0.01949,0.09602]}],"total_contact_groups":14},"final_pose_error":0.00992,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.42203,-0.01877,0.01602],"final_tcp_position":[0.4161,-0.01967,0.10443],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":1.22665,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.57391,0.15482,0.13706],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22058,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58999,0.22216,0.28073],"tcp_start":[0.57391,0.15482,0.13706],"tcp_to_object_dist_end":0.36115,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":818.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3272.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.595,0.19916,0.09745],"tcp_start":[0.58999,0.22216,0.28073],"tcp_to_object_dist_end":0.24952,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":840.0,"n_steps_budget":1000.0,"object_pos_end":[0.44728,-0.01928,0.0194],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.25832,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":1.22665,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3894.0,"raw_peak_contact_force":0.68188,"tcp_end":[0.46466,0.00941,0.04355],"tcp_start":[0.595,0.19916,0.09745],"tcp_to_object_dist_end":0.04133,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":791.0,"n_steps_budget":1000.0,"object_pos_end":[0.42257,-0.0228,0.01602],"object_pos_start":[0.44728,-0.01928,0.0194],"object_to_goal_dist_end":0.27806,"object_to_goal_dist_start":0.25832,"object_z_max":0.0194,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3105.0,"raw_peak_contact_force":0.77534,"tcp_end":[0.44315,-0.01811,0.03501],"tcp_start":[0.46466,0.00941,0.04355],"tcp_to_object_dist_end":0.02839,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.41918,-0.01986,0.01386],"object_pos_start":[0.42257,-0.0228,0.01602],"object_to_goal_dist_end":0.27936,"object_to_goal_dist_start":0.27806,"object_z_max":0.01602,"peak_contact_force":0.24769,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7230.0,"raw_peak_contact_force":0.35498,"tcp_end":[0.4353,-0.01803,0.02779],"tcp_start":[0.44315,-0.01811,0.03501],"tcp_to_object_dist_end":0.02139,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":593.0,"n_steps_budget":1000.0,"object_pos_end":[0.42203,-0.01877,0.01602],"object_pos_start":[0.41918,-0.01986,0.01386],"object_to_goal_dist_end":0.2759,"object_to_goal_dist_start":0.27936,"object_z_max":0.03752,"peak_contact_force":0.12264,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5230.0,"raw_peak_contact_force":0.63049,"tcp_end":[0.4161,-0.01967,0.10443],"tcp_start":[0.4353,-0.01803,0.02779],"tcp_to_object_dist_end":0.08862,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```