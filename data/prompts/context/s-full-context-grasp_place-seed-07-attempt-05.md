## Search State

- **Seed**: 7
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.0470 | 0.18 | ❌ rejected |
| 4 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |
| 3 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1556 | 0.17 | ❌ rejected |
| 1 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |

**Proposal policy**: task_score is 0.18 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`
- Frozen object start: [0.5125095466604667, 0.039721380096957554, 0.03]
- Frozen task target: [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]
- Goal object position: (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5125095466604667, 0.039721380096957554, 0.03)
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
  frozen_object_start: [0.5125, 0.0397, 0.03]
  frozen_task_target: [0.6276, 0.1725, 0.145]
  frozen_object_starts: {'grasp_target': [0.5125095466604667, 0.039721380096957554, 0.03]}
  frozen_targets: {'place_target': [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6

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
| `object` | offset from object initial position (0.5125095466604667, 0.039721380096957554, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6275685690245193, 0.17252071899905919, 0.14502494273668382) | final destination targets |
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

## Current Skill (Q=0.047) — your mutation base

```yaml
skill: grasp_place
skill_type: arm_gripper
phases:
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
- id: insert_1
  type: insert
  generator: impedance_motion
  control: admittance_control
  termination: pose_tolerance
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
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
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
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2

```

## Design Metrics

- **Composite score**: 0.047
- **task_score** (E): 0.184
- **fitness_score**: 0.377  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1384 |
| descend_to_grasp | 1.00 | 1.00 | 0.1035 |
| grasp | 1.00 | 1.00 | 0.0120 |
| lift | 1.00 | 1.00 | 0.1086 |
| transport_to_goal | 1.00 | 1.00 | 0.2518 |
| descend_to_place | 1.00 | 1.00 | 0.0766 |
| release | 1.00 | 1.00 | 0.0200 |
| retract | 1.00 | 1.00 | 0.0851 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.019, 0.168) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, 0.019, 0.168)→(0.506, 0.022, 0.064) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.506, 0.022, 0.064)→(0.498, 0.021, 0.055) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.274 | 1.00 / 26.667 | 0.152 | 0.205 |
| lift | lift | 1.00 / step_budget | (0.498, 0.021, 0.055)→(0.494, 0.021, 0.164) | (0.511, 0.022, 0.026)→(0.494, 0.031, 0.048) | 0.274→0.266 | 1.00 / 12.000 | 0.120 | 0.824 |
| transport_to_goal | approach | 1.00 / step_budget | (0.494, 0.021, 0.164)→(0.598, 0.199, 0.298) | (0.494, 0.031, 0.048)→(0.507, 0.060, 0.016) | 0.266→0.258 | 1.00 / 8.000 | 0.123 | 0.602 |
| descend_to_place | descend | 1.00 / step_budget | (0.598, 0.199, 0.298)→(0.602, 0.206, 0.222) | (0.507, 0.060, 0.016)→(0.507, 0.060, 0.016) | 0.258→0.258 | 1.00 / 8.667 | 0.123 | 0.123 |
| release | release | 1.00 / step_budget | (0.602, 0.206, 0.222)→(0.597, 0.205, 0.242) | (0.507, 0.060, 0.016)→(0.507, 0.060, 0.016) | 0.258→0.258 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.597, 0.205, 0.242)→(0.596, 0.204, 0.327) | (0.507, 0.060, 0.016)→(0.507, 0.060, 0.016) | 0.258→0.258 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.182
- phase_score: 0.704
- phase_breakdown.reach_object_score: 0.870
- phase_breakdown.reach_goal_score: 0.632
- grasp_place_fitness: 0.544

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.544
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.239
- **Median Q (composite search score)**: -0.009
- **K-run variance**: 0.0144
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.116


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `0b279c554151a1bc107b4895d67067efa2444eadb5a644f2482f57ab9ff93d7f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `079d4532bc3cff86c1b89933c7940f2ee474dc4233e12f8d134c76ceb3cd8d4d`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.49333,"average_solve_count":225.0,"average_success_count":225.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.04993,"lift.lift_height":0.1486,"transport_to_goal.transport_speed":0.06401},"optimized_scores":{"best_composite_score":-0.00923,"best_fitness_score":0.32077,"best_task_score":0.23866},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1167.0,"contact_point_centroid":[0.49951,0.05675,-0.00256],"force_p95":0.38193,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.00467,"mean_force":0.14133,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49608,0.03767,0.15685]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4784.0,"contact_point_centroid":[0.49767,0.0558,0.08813],"force_p95":0.1449,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31561,"mean_force":0.10397,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49565,0.03763,0.09239]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4955.0,"contact_point_centroid":[0.497,0.01948,0.08676],"force_p95":0.14399,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29581,"mean_force":0.09949,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49565,0.03763,0.09078]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.03968,-0.00213],"force_p95":0.16018,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21406,"mean_force":0.13204,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50073,0.03804,0.05657]},{"body_a":"world","body_b":"grasp_target","contact_count":1112.0,"contact_point_centroid":[0.51251,0.03972,-0.00188],"force_p95":0.13647,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50281,0.01586,0.23542]},{"body_a":"world","body_b":"grasp_target","contact_count":1284.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50613,0.03581,0.11534]},{"body_a":"world","body_b":"grasp_target","contact_count":2480.0,"contact_point_centroid":[0.49803,0.05954,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5566,0.10191,0.22058]},{"body_a":"world","body_b":"grasp_target","contact_count":864.0,"contact_point_centroid":[0.49803,0.05954,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61815,0.16586,0.21253]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.49803,0.05954,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61738,0.16825,0.17213]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.49803,0.05954,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61304,0.16682,0.23158]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2893.0,"contact_point_centroid":[0.49977,0.01925,0.05179],"force_p95":0.0928,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11753,"mean_force":0.07038,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4996,0.03795,0.05528]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2826.0,"contact_point_centroid":[0.50029,0.05678,0.05177],"force_p95":0.10014,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10044,"mean_force":0.07354,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4996,0.03795,0.05529]},{"body_a":"left_finger","body_b":"right_finger","contact_count":743.0,"contact_point_centroid":[0.49626,0.03766,0.17937],"force_p95":0.01316,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01612,"mean_force":0.01099,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49586,0.03765,0.17711]},{"body_a":"left_finger","body_b":"right_finger","contact_count":916.0,"contact_point_centroid":[0.61856,0.16586,0.21498],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.0105,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61813,0.16584,0.21273]},{"body_a":"left_finger","body_b":"right_finger","contact_count":217.0,"contact_point_centroid":[0.62058,0.16915,0.17075],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01261,"mean_force":0.01025,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62004,0.16912,0.16859]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2663.0,"contact_point_centroid":[0.55724,0.10211,0.22291],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01258,"mean_force":0.01039,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55678,0.10209,0.22067]}],"total_contact_groups":16},"final_pose_error":0.01557,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.49803,0.05954,0.01602],"final_tcp_position":[0.61334,0.16686,0.27621],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.00467,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":279.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1112.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50731,0.03326,0.16779],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14202,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":321.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1284.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.5075,0.03857,0.06434],"tcp_start":[0.50731,0.03326,0.16779],"tcp_to_object_dist_end":0.03866,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51248,0.03875,0.02555],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.2131,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.1566,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7519.0,"raw_peak_contact_force":0.21406,"tcp_end":[0.49957,0.03794,0.05525],"tcp_start":[0.5075,0.03857,0.06434],"tcp_to_object_dist_end":0.03239,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.49803,0.05954,0.01602],"object_pos_start":[0.51248,0.03875,0.02555],"object_to_goal_dist_end":0.21491,"object_to_goal_dist_start":0.2131,"object_z_max":0.09884,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11649.0,"raw_peak_contact_force":1.00467,"tcp_end":[0.49606,0.03767,0.1917],"tcp_start":[0.49957,0.03794,0.05525],"tcp_to_object_dist_end":0.17705,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":620.0,"n_steps_budget":1000.0,"object_pos_end":[0.49803,0.05954,0.01602],"object_pos_start":[0.49803,0.05954,0.01602],"object_to_goal_dist_end":0.21491,"object_to_goal_dist_start":0.21491,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5143.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.61626,0.16283,0.25171],"tcp_start":[0.49606,0.03767,0.1917],"tcp_to_object_dist_end":0.28319,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":216.0,"n_steps_budget":1000.0,"object_pos_end":[0.49803,0.05954,0.01602],"object_pos_start":[0.49803,0.05954,0.01602],"object_to_goal_dist_end":0.21491,"object_to_goal_dist_start":0.21491,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1780.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62182,0.16958,0.17252],"tcp_start":[0.61626,0.16283,0.25171],"tcp_to_object_dist_end":0.22787,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49803,0.05954,0.01602],"object_pos_start":[0.49803,0.05954,0.01602],"object_to_goal_dist_end":0.21491,"object_to_goal_dist_start":0.21491,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61582,0.16772,0.19156],"tcp_start":[0.62182,0.16958,0.17252],"tcp_to_object_dist_end":0.23746,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.49803,0.05954,0.01602],"object_pos_start":[0.49803,0.05954,0.01602],"object_to_goal_dist_end":0.21491,"object_to_goal_dist_start":0.21491,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61334,0.16686,0.27621],"tcp_start":[0.61582,0.16772,0.19156],"tcp_to_object_dist_end":0.30416,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `a74f7c08b88460953bfa7e35b953cddf9278fdc17d2d4db8a2ea121b328e8b73`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57627,"average_solve_count":236.0,"average_success_count":236.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.06198,"lift.lift_height":0.10744,"transport_to_goal.transport_speed":0.06333},"optimized_scores":{"best_composite_score":-0.06332,"best_fitness_score":0.26668,"best_task_score":0.13282},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":956.0,"contact_point_centroid":[0.46132,0.05383,-0.00241],"force_p95":0.37573,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16077,"mean_force":0.14412,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4673,0.0463,0.12486]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3510.0,"contact_point_centroid":[0.4668,0.02773,0.07651],"force_p95":0.15322,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38475,"mean_force":0.09507,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46717,0.04629,0.08084]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4064.0,"contact_point_centroid":[0.46764,0.06454,0.07887],"force_p95":0.13548,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29902,"mean_force":0.08746,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46713,0.04628,0.08297]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48276,0.04867,-0.00214],"force_p95":0.16526,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21817,"mean_force":0.13297,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47196,0.04675,0.05775]},{"body_a":"world","body_b":"grasp_target","contact_count":1100.0,"contact_point_centroid":[0.4827,0.04873,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49088,0.01954,0.23542]},{"body_a":"world","body_b":"grasp_target","contact_count":3832.0,"contact_point_centroid":[0.45769,0.05485,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52108,0.13556,0.24398]},{"body_a":"world","body_b":"grasp_target","contact_count":1300.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47917,0.04402,0.11564]},{"body_a":"world","body_b":"grasp_target","contact_count":816.0,"contact_point_centroid":[0.45769,0.05485,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57626,0.22279,0.29746]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.45769,0.05485,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57516,0.22463,0.25928]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.45769,0.05485,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.5725,0.22324,0.3196]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2654.0,"contact_point_centroid":[0.46992,0.02796,0.05275],"force_p95":0.09751,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11716,"mean_force":0.0761,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47088,0.04665,0.05661]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2831.0,"contact_point_centroid":[0.47048,0.06542,0.05282],"force_p95":0.10019,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10045,"mean_force":0.07319,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47089,0.04665,0.05662]},{"body_a":"left_finger","body_b":"right_finger","contact_count":547.0,"contact_point_centroid":[0.46751,0.04629,0.1443],"force_p95":0.01374,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01563,"mean_force":0.01106,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46699,0.04628,0.14207]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4058.0,"contact_point_centroid":[0.52177,0.13601,0.24669],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01052,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52136,0.13599,0.24444]},{"body_a":"left_finger","body_b":"right_finger","contact_count":855.0,"contact_point_centroid":[0.57678,0.22283,0.29942],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01106,"mean_force":0.01063,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57627,0.2228,0.29734]},{"body_a":"left_finger","body_b":"right_finger","contact_count":226.0,"contact_point_centroid":[0.57719,0.22554,0.25729],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01094,"mean_force":0.00991,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57688,0.22551,0.25529]}],"total_contact_groups":16},"final_pose_error":0.01453,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.45769,0.05485,0.01602],"final_tcp_position":[0.57293,0.22334,0.36453],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.16077,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":276.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1100.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.4823,0.04091,0.16795],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14215,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":325.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1300.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47847,0.04737,0.06471],"tcp_start":[0.4823,0.04091,0.16795],"tcp_to_object_dist_end":0.03894,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48268,0.04753,0.0255],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.2911,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16197,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7285.0,"raw_peak_contact_force":0.21817,"tcp_end":[0.47085,0.04665,0.05658],"tcp_start":[0.47847,0.04737,0.06471],"tcp_to_object_dist_end":0.03327,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.45769,0.05485,0.01602],"object_pos_start":[0.48268,0.04753,0.0255],"object_to_goal_dist_end":0.30281,"object_to_goal_dist_start":0.2911,"object_z_max":0.06973,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9077.0,"raw_peak_contact_force":1.16077,"tcp_end":[0.46714,0.04629,0.15261],"tcp_start":[0.47085,0.04665,0.05658],"tcp_to_object_dist_end":0.13718,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":958.0,"n_steps_budget":1000.0,"object_pos_end":[0.45769,0.05485,0.01602],"object_pos_start":[0.45769,0.05485,0.01602],"object_to_goal_dist_end":0.30281,"object_to_goal_dist_start":0.30281,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7890.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_goal","tcp_end":[0.57528,0.22021,0.33397],"tcp_start":[0.46714,0.04629,0.15261],"tcp_to_object_dist_end":0.37718,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":204.0,"n_steps_budget":1000.0,"object_pos_end":[0.45769,0.05485,0.01602],"object_pos_start":[0.45769,0.05485,0.01602],"object_to_goal_dist_end":0.30281,"object_to_goal_dist_start":0.30281,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1671.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57816,0.226,0.259],"tcp_start":[0.57528,0.22021,0.33397],"tcp_to_object_dist_end":0.32069,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45769,0.05485,0.01602],"object_pos_start":[0.45769,0.05485,0.01602],"object_to_goal_dist_end":0.30281,"object_to_goal_dist_start":0.30281,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5742,0.22411,0.27898],"tcp_start":[0.57816,0.226,0.259],"tcp_to_object_dist_end":0.33373,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.45769,0.05485,0.01602],"object_pos_start":[0.45769,0.05485,0.01602],"object_to_goal_dist_end":0.30281,"object_to_goal_dist_start":0.30281,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57293,0.22334,0.36453],"tcp_start":[0.5742,0.22411,0.27898],"tcp_to_object_dist_end":0.40389,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b1a72366a9c9a56aa2e80fc4399e157c8281abf492ab3c1ede02058762a86ed7`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67511,"average_solve_count":237.0,"average_success_count":237.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.05438,"lift.lift_height":0.10559,"transport_to_goal.transport_speed":0.0735},"optimized_scores":{"best_composite_score":0.21356,"best_fitness_score":0.54356,"best_task_score":0.18175},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2633.0,"contact_point_centroid":[0.56459,0.06426,-0.00238],"force_p95":0.1271,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.56146,"mean_force":0.14087,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57594,0.14061,0.25712]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6017.0,"contact_point_centroid":[0.52215,-0.00223,0.09334],"force_p95":0.13064,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30687,"mean_force":0.09588,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.519,-0.02056,0.0968]},{"body_a":"world","body_b":"grasp_target","contact_count":148.0,"contact_point_centroid":[0.53456,-0.02032,-0.00115],"force_p95":0.22838,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29624,"mean_force":0.05509,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52152,-0.02062,0.05582]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6108.0,"contact_point_centroid":[0.52208,-0.03887,0.09364],"force_p95":0.13071,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28764,"mean_force":0.09481,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51902,-0.02056,0.09724]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2076.0,"contact_point_centroid":[0.53348,0.02863,0.16049],"force_p95":0.14687,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21402,"mean_force":0.10854,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52765,0.01035,0.16504]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53705,-0.02127,-0.00205],"force_p95":0.13993,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18145,"mean_force":0.12694,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52434,-0.02068,0.05551]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2372.0,"contact_point_centroid":[0.53341,-0.00695,0.16109],"force_p95":0.12398,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17309,"mean_force":0.09461,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52791,0.0111,0.16555]},{"body_a":"world","body_b":"grasp_target","contact_count":1128.0,"contact_point_centroid":[0.53702,-0.02132,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51275,-0.00856,0.23511]},{"body_a":"world","body_b":"grasp_target","contact_count":1264.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52835,-0.01933,0.11481]},{"body_a":"world","body_b":"grasp_target","contact_count":796.0,"contact_point_centroid":[0.5646,0.06437,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60447,0.21881,0.27354]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5646,0.06437,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60292,0.22251,0.23504]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.5646,0.06437,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.59988,0.22105,0.29444]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2667.0,"contact_point_centroid":[0.52401,-0.00191,0.05123],"force_p95":0.09802,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1055,"mean_force":0.07621,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52316,-0.02065,0.05411]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2956.0,"contact_point_centroid":[0.52367,-0.03934,0.05103],"force_p95":0.09301,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09308,"mean_force":0.06981,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52316,-0.02065,0.05411]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2585.0,"contact_point_centroid":[0.5786,0.14677,0.26377],"force_p95":0.0112,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01632,"mean_force":0.01052,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57827,0.14677,0.26152]},{"body_a":"left_finger","body_b":"right_finger","contact_count":845.0,"contact_point_centroid":[0.60486,0.21884,0.27591],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01275,"mean_force":0.0105,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60447,0.21882,0.27349]}],"total_contact_groups":17},"final_pose_error":0.01519,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.5646,0.06437,0.01602],"final_tcp_position":[0.6003,0.22115,0.33932],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.56146,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":283.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1128.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52797,-0.01792,0.16739],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1417,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":316.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1264.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53137,-0.0208,0.064],"tcp_start":[0.52797,-0.01792,0.16739],"tcp_to_object_dist_end":0.0384,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53696,-0.02084,0.0258],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31649,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13804,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7423.0,"raw_peak_contact_force":0.18145,"tcp_end":[0.52313,-0.02065,0.05407],"tcp_start":[0.53137,-0.0208,0.064],"tcp_to_object_dist_end":0.03147,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.52505,-0.02055,0.1111],"object_pos_start":[0.53696,-0.02084,0.0258],"object_to_goal_dist_end":0.27964,"object_to_goal_dist_start":0.31649,"object_z_max":0.11099,"peak_contact_force":0.11327,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12273.0,"raw_peak_contact_force":0.30687,"tcp_end":[0.5191,-0.02056,0.14732],"tcp_start":[0.52313,-0.02065,0.05407],"tcp_to_object_dist_end":0.03671,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5646,0.06437,0.01602],"object_pos_start":[0.52505,-0.02055,0.1111],"object_to_goal_dist_end":0.25576,"object_to_goal_dist_start":0.27964,"object_z_max":0.14744,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9666.0,"raw_peak_contact_force":1.56146,"subtask_id":"reach_goal","tcp_end":[0.60376,0.21459,0.30982],"tcp_start":[0.5191,-0.02056,0.14732],"tcp_to_object_dist_end":0.33229,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":199.0,"n_steps_budget":1000.0,"object_pos_end":[0.5646,0.06437,0.01602],"object_pos_start":[0.5646,0.06437,0.01602],"object_to_goal_dist_end":0.25576,"object_to_goal_dist_start":0.25576,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1641.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6063,0.22389,0.23553],"tcp_start":[0.60376,0.21459,0.30982],"tcp_to_object_dist_end":0.27454,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5646,0.06437,0.01602],"object_pos_start":[0.5646,0.06437,0.01602],"object_to_goal_dist_end":0.25576,"object_to_goal_dist_start":0.25576,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60182,0.22196,0.25441],"tcp_start":[0.6063,0.22389,0.23553],"tcp_to_object_dist_end":0.28819,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.5646,0.06437,0.01602],"object_pos_start":[0.5646,0.06437,0.01602],"object_to_goal_dist_end":0.25576,"object_to_goal_dist_start":0.25576,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6003,0.22115,0.33932],"tcp_start":[0.60182,0.22196,0.25441],"tcp_to_object_dist_end":0.36108,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```