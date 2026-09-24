## Search State

- **Seed**: 1
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → align → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | impedance_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.2906 | 0.14 | ❌ rejected |
| 11 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |
| 10 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |
| 9 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |
| 8 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`
- Frozen object start: [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5, 0.0, 0.3)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5011821624700257, 0.045046369632593536, 0.03)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5011821624700257, 0.045046369632593536, 0.03]
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
  frozen_object_start: [0.5012, 0.045, 0.03]
  frozen_task_target: [0.5644, 0.2449, 0.1468]
  frozen_object_starts: {'grasp_target': [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]}
  frozen_targets: {'place_target': [0.5, 0.0, 0.3]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb

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
| `object` | offset from object initial position (0.5644159612719634, 0.2448649447137244, 0.1467747178015728) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
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

## Current Skill (Q=-0.291) — your mutation base

```yaml
skill: grasp_place
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
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: align_2
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
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: -0.291
- **task_score** (E): 0.144
- **fitness_score**: 0.214  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_object | 0.00 | 1.00 | 0.1773 |
| align_to_object | 1.00 | 1.00 | 0.0674 |
| descend_to_object | 1.00 | 1.00 | 0.0041 |
| grasp_object | 1.00 | 1.00 | 0.0000 |
| lift_object | 0.00 | 1.00 | 0.1544 |
| approach_goal | 0.33 | 1.00 | 0.2867 |
| descend_and_place | 1.00 | 1.00 | 0.1543 |
| release_object | 1.00 | 1.00 | 0.0188 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.400, 0.004, 0.155) | (0.479, -0.000, 0.030)→(0.450, 0.000, 0.019) | 0.276→0.297 | 1.00 / 5.000 | 196.110 | 1434.412 |
| align_to_object | align | 1.00 / step_budget | (0.400, 0.004, 0.155)→(0.450, -0.002, 0.117) | (0.450, 0.000, 0.019)→(0.450, 0.000, 0.019) | 0.297→0.297 | 1.00 / 4.000 | 0.123 | 325.298 |
| descend_to_object | descend | 1.00 / force_exceeded | (0.450, -0.002, 0.117)→(0.449, -0.002, 0.113) | (0.450, 0.000, 0.019)→(0.450, 0.000, 0.019) | 0.297→0.297 | 1.00 / 4.000 | 81.142 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.443, -0.003, 0.103)→(0.443, -0.003, 0.103) | (0.450, 0.000, 0.019)→(0.450, 0.000, 0.019) | 0.297→0.297 | 1.00 / 8.667 | 91001.455 | 0.123 |
| lift_object | lift | 0.00 / step_budget | (0.440, -0.003, 0.337)→(0.441, -0.003, 0.491) | (0.450, 0.000, 0.019)→(0.450, 0.000, 0.019) | 0.297→0.297 | 1.00 / 8.333 | 0.123 | 0.123 |
| approach_goal | approach | 0.33 / step_budget | (0.441, -0.003, 0.491)→(0.566, 0.156, 0.296) | (0.450, 0.000, 0.019)→(0.450, 0.000, 0.019) | 0.297→0.297 | 1.00 / 8.333 | 94250.514 | 0.123 |
| descend_and_place | descend | 1.00 / step_budget | (0.566, 0.156, 0.296)→(0.602, 0.199, 0.154) | (0.450, 0.000, 0.019)→(0.450, 0.000, 0.019) | 0.297→0.297 | 1.00 / 8.667 | 0.123 | 0.123 |
| release_object | release | 1.00 / step_budget | (0.602, 0.199, 0.154)→(0.597, 0.198, 0.173) | (0.450, 0.000, 0.019)→(0.450, 0.000, 0.019) | 0.297→0.297 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.201
- phase_score: 0.745
- phase_breakdown.reach_goal_score: 0.822
- phase_breakdown.reach_object_score: 0.567
- grasp_place_fitness: 0.244

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.244
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.201
- **Median Q (composite search score)**: -0.303
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at upper bound**: align_to_object.lateral_offset_x
- **Final σ (mean)**: 0.406


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8110053be9072e64e15984c6424e4a66fe19af4b6c37a60139a43e94cc34ad53`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `46ef03f7b16015a0d14bf26d80c05d326b92c02b0bf759391930f5ab902d1933`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.56442,0.24486,0.14677]},{"name":"goal","value":[0.50118,0.04505,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88552,"average_solve_count":297.0,"average_success_count":297.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_object.lateral_offset_x":0.00271,"align_to_object.lateral_offset_y":0.0018,"approach_above_object.approach_speed":0.09867,"approach_goal.approach_goal_speed":0.07746,"descend_and_place.place_speed":0.03228,"descend_to_object.contact_force_threshold":3.50748,"descend_to_object.descend_speed":0.02598,"lift_object.lift_height":0.18561,"lift_object.lift_speed":0.03406},"optimized_scores":{"best_composite_score":-0.26071,"best_fitness_score":0.24429,"best_task_score":0.20106},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.63529,0.01021,-0.00045],"force_p95":214.99134,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1300.15117,"mean_force":206.38767,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.40295,0.00986,0.13692]},{"body_a":"world","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.52891,0.00888,-0.00302],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1204.81,"mean_force":54.76409,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.37677,0.0041,0.04929]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.62664,0.01908,-5e-05],"force_p95":323.17598,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":328.32761,"mean_force":246.01245,"phase_index":1.0,"phase_name":"align_to_object","phase_type":"align","tcp_position_centroid":[0.42433,0.01894,0.18337]},{"body_a":"grasp_target","body_b":"link7","contact_count":548.0,"contact_point_centroid":[0.49642,0.03103,0.04959],"force_p95":0.93662,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.00975,"mean_force":0.2905,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.39595,0.00709,0.11897]},{"body_a":"grasp_target","body_b":"hand","contact_count":326.0,"contact_point_centroid":[0.48754,0.03016,0.05756],"force_p95":2.20936,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.96723,"mean_force":0.43781,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.39112,0.00543,0.10349]},{"body_a":"world","body_b":"grasp_target","contact_count":2896.0,"contact_point_centroid":[0.49215,0.04796,-0.00284],"force_p95":0.29875,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.39109,"mean_force":0.19219,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.41996,0.00987,0.15269]},{"body_a":"world","body_b":"grasp_target","contact_count":1852.0,"contact_point_centroid":[0.49778,0.04769,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12269,"mean_force":0.12263,"phase_index":1.0,"phase_name":"align_to_object","phase_type":"align","tcp_position_centroid":[0.45801,0.03324,0.15057]},{"body_a":"world","body_b":"grasp_target","contact_count":96.0,"contact_point_centroid":[0.49778,0.04769,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.491,0.04685,0.12175]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.49778,0.04769,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48523,0.04617,0.10929]},{"body_a":"world","body_b":"grasp_target","contact_count":11216.0,"contact_point_centroid":[0.49778,0.04769,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48159,0.04564,0.27012]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.49778,0.04769,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51969,0.13353,0.39097]},{"body_a":"world","body_b":"grasp_target","contact_count":1272.0,"contact_point_centroid":[0.49778,0.04769,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"descend_and_place","phase_type":"descend","tcp_position_centroid":[0.5569,0.23143,0.21068]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.49778,0.04769,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5568,0.23935,0.15411]},{"body_a":"left_finger","body_b":"right_finger","contact_count":755.0,"contact_point_centroid":[0.48643,0.04615,0.10789],"force_p95":0.01323,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01091,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4845,0.04608,0.10794]},{"body_a":"left_finger","body_b":"right_finger","contact_count":12086.0,"contact_point_centroid":[0.48372,0.04575,0.27127],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.01035,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48159,0.04564,0.27144]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4316.0,"contact_point_centroid":[0.5214,0.13334,0.39261],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01277,"mean_force":0.01034,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51951,0.13309,0.39159]}],"total_contact_groups":18},"final_pose_error":0.00982,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.49778,0.04769,0.02602],"final_tcp_position":[0.56021,0.24068,0.15459],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":273004.50701,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49778,0.04769,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24063,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":203.89301,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4678.0,"raw_peak_contact_force":1300.15117,"subtask_id":"reach_object","tcp_end":[0.42425,0.0189,0.18327],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17596,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":463.0,"n_steps_budget":660.0,"object_pos_end":[0.49778,0.04769,0.02602],"object_pos_start":[0.49778,0.04769,0.02602],"object_to_goal_dist_end":0.24062,"object_to_goal_dist_start":0.24063,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_to_object","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1856.0,"raw_peak_contact_force":328.32761,"subtask_id":"reach_object","tcp_end":[0.49127,0.04679,0.12345],"tcp_start":[0.42425,0.0189,0.18327],"tcp_to_object_dist_end":0.09765,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":24.0,"n_steps_budget":1000.0,"object_pos_end":[0.49778,0.04769,0.02602],"object_pos_start":[0.49778,0.04769,0.02602],"object_to_goal_dist_end":0.24062,"object_to_goal_dist_start":0.24062,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":96.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49046,0.04679,0.1191],"tcp_start":[0.49127,0.04679,0.12345],"tcp_to_object_dist_end":0.09338,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.49778,0.04769,0.02602],"object_pos_start":[0.49778,0.04769,0.02602],"object_to_goal_dist_end":0.24062,"object_to_goal_dist_start":0.24062,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2955.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.4845,0.04608,0.10793],"tcp_start":[0.4845,0.04608,0.10793],"tcp_to_object_dist_end":0.083,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":2804.0,"n_steps_budget":1000.0,"object_pos_end":[0.49778,0.04769,0.02602],"object_pos_start":[0.49778,0.04769,0.02602],"object_to_goal_dist_end":0.24062,"object_to_goal_dist_start":0.24062,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23302.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.48356,0.04569,0.51746],"tcp_start":[0.48166,0.04564,0.34384],"tcp_to_object_dist_end":0.49165,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49778,0.04769,0.02602],"object_pos_start":[0.49778,0.04769,0.02602],"object_to_goal_dist_end":0.24062,"object_to_goal_dist_start":0.24062,"object_z_max":0.02602,"peak_contact_force":273002.38169,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8316.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.55484,0.22357,0.26617],"tcp_start":[0.48356,0.04569,0.51746],"tcp_to_object_dist_end":0.30309,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":318.0,"n_steps_budget":1000.0,"object_pos_end":[0.49778,0.04769,0.02602],"object_pos_start":[0.49778,0.04769,0.02602],"object_to_goal_dist_end":0.24062,"object_to_goal_dist_start":0.24062,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_and_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2647.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.56021,0.24068,0.15459],"tcp_start":[0.55484,0.22357,0.26617],"tcp_to_object_dist_end":0.24015,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49778,0.04769,0.02602],"object_pos_start":[0.49778,0.04769,0.02602],"object_to_goal_dist_end":0.24062,"object_to_goal_dist_start":0.24062,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55566,0.23885,0.17339],"tcp_start":[0.56021,0.24068,0.15459],"tcp_to_object_dist_end":0.24822,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1efc3ad2e58ea1c47cd56203c4986b53dab7b80d759e458b85d233ccc9cc04bd`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.63142,0.15919,0.19002]},{"name":"goal","value":[0.47616,-0.02015,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69466,"average_solve_count":262.0,"average_success_count":262.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_object.lateral_offset_x":0.00953,"align_to_object.lateral_offset_y":-0.007,"approach_above_object.approach_speed":0.04509,"approach_goal.approach_goal_speed":0.11857,"descend_and_place.place_speed":0.05728,"descend_to_object.contact_force_threshold":3.25184,"descend_to_object.descend_speed":0.02318,"lift_object.lift_height":0.14308,"lift_object.lift_speed":0.02434},"optimized_scores":{"best_composite_score":-0.30331,"best_fitness_score":0.20169,"best_task_score":0.11997},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.63031,-0.00263,-0.00047],"force_p95":196.22394,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1334.72819,"mean_force":200.18804,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.38712,-0.00263,0.11983]},{"body_a":"world","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.52679,0.00277,-0.00295],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":412.63378,"mean_force":19.64923,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.37133,-0.00162,0.05156]},{"body_a":"world","body_b":"link6","contact_count":11.0,"contact_point_centroid":[0.62519,-0.00416,-0.00017],"force_p95":313.42192,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":324.14993,"mean_force":170.13351,"phase_index":1.0,"phase_name":"align_to_object","phase_type":"align","tcp_position_centroid":[0.39285,-0.00436,0.14322]},{"body_a":"grasp_target","body_b":"hand","contact_count":38.0,"contact_point_centroid":[0.45658,-0.02059,0.04046],"force_p95":3.69708,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.05815,"mean_force":1.703,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.38174,-0.00158,0.05313]},{"body_a":"grasp_target","body_b":"link7","contact_count":28.0,"contact_point_centroid":[0.48132,-0.00544,0.01008],"force_p95":0.59049,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.69127,"mean_force":0.37045,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.37201,-0.00162,0.05541]},{"body_a":"world","body_b":"grasp_target","contact_count":3932.0,"contact_point_centroid":[0.44065,-0.02121,-0.00215],"force_p95":0.1376,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.04755,"mean_force":0.13887,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.39945,-0.00244,0.12969]},{"body_a":"world","body_b":"grasp_target","contact_count":1356.0,"contact_point_centroid":[0.43572,-0.02137,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"align_to_object","phase_type":"align","tcp_position_centroid":[0.41394,-0.01529,0.12645]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.43572,-0.02137,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.43572,-0.02582,0.11202]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.43572,-0.02137,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.42973,-0.0257,0.1019]},{"body_a":"world","body_b":"grasp_target","contact_count":11140.0,"contact_point_centroid":[0.43572,-0.02137,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.42543,-0.0257,0.25159]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.43572,-0.02137,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5101,0.04966,0.37622]},{"body_a":"world","body_b":"grasp_target","contact_count":1556.0,"contact_point_centroid":[0.43572,-0.02137,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"descend_and_place","phase_type":"descend","tcp_position_centroid":[0.60576,0.13733,0.25249]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.43572,-0.02137,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.6209,0.1535,0.19316]},{"body_a":"left_finger","body_b":"right_finger","contact_count":739.0,"contact_point_centroid":[0.43112,-0.02576,0.10046],"force_p95":0.01347,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01111,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.42898,-0.0257,0.10079]},{"body_a":"left_finger","body_b":"right_finger","contact_count":11756.0,"contact_point_centroid":[0.42751,-0.02579,0.25153],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01291,"mean_force":0.01055,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.42543,-0.0257,0.25214]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4344.0,"contact_point_centroid":[0.51239,0.0501,0.37662],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.01028,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51043,0.04997,0.37594]}],"total_contact_groups":18},"final_pose_error":0.00985,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.43572,-0.02137,0.01602],"final_tcp_position":[0.624,0.15425,0.1942],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273004.59751,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43572,-0.02137,0.01602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.31808,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":191.69079,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4905.0,"raw_peak_contact_force":1334.72819,"subtask_id":"reach_object","tcp_end":[0.39258,-0.00427,0.14269],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1349,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":339.0,"n_steps_budget":600.0,"object_pos_end":[0.43572,-0.02137,0.01602],"object_pos_start":[0.43572,-0.02137,0.01602],"object_to_goal_dist_end":0.31808,"object_to_goal_dist_start":0.31808,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"align_to_object","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1367.0,"raw_peak_contact_force":324.14993,"subtask_id":"reach_object","tcp_end":[0.436,-0.02573,0.11332],"tcp_start":[0.39258,-0.00427,0.14269],"tcp_to_object_dist_end":0.0974,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":22.0,"n_steps_budget":1000.0,"object_pos_end":[0.43572,-0.02137,0.01602],"object_pos_start":[0.43572,-0.02137,0.01602],"object_to_goal_dist_end":0.31808,"object_to_goal_dist_start":0.31808,"object_z_max":0.01602,"peak_contact_force":81.14225,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":88.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.43511,-0.02578,0.10989],"tcp_start":[0.436,-0.02573,0.11332],"tcp_to_object_dist_end":0.09398,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.43572,-0.02137,0.01602],"object_pos_start":[0.43572,-0.02137,0.01602],"object_to_goal_dist_end":0.31808,"object_to_goal_dist_start":0.31808,"object_z_max":0.01602,"peak_contact_force":273004.12084,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2939.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.42898,-0.0257,0.10079],"tcp_start":[0.42898,-0.0257,0.10079],"tcp_to_object_dist_end":0.08515,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":2785.0,"n_steps_budget":1000.0,"object_pos_end":[0.43572,-0.02137,0.01602],"object_pos_start":[0.43572,-0.02137,0.01602],"object_to_goal_dist_end":0.31808,"object_to_goal_dist_start":0.31808,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22896.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.42624,-0.02579,0.44733],"tcp_start":[0.42547,-0.02571,0.31422],"tcp_to_object_dist_end":0.43144,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43572,-0.02137,0.01602],"object_pos_start":[0.43572,-0.02137,0.01602],"object_to_goal_dist_end":0.31808,"object_to_goal_dist_start":0.31808,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8344.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.58944,0.12184,0.31281],"tcp_start":[0.42624,-0.02579,0.44733],"tcp_to_object_dist_end":0.36362,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":389.0,"n_steps_budget":1000.0,"object_pos_end":[0.43572,-0.02137,0.01602],"object_pos_start":[0.43572,-0.02137,0.01602],"object_to_goal_dist_end":0.31808,"object_to_goal_dist_start":0.31808,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_and_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3241.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.624,0.15425,0.1942],"tcp_start":[0.58944,0.12184,0.31281],"tcp_to_object_dist_end":0.31311,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.43572,-0.02137,0.01602],"object_pos_start":[0.43572,-0.02137,0.01602],"object_to_goal_dist_end":0.31808,"object_to_goal_dist_start":0.31808,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1031.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61988,0.15318,0.21213],"tcp_start":[0.624,0.15425,0.1942],"tcp_to_object_dist_end":0.32069,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `37495cb43897015e78e007c86af160d11c8460c1ce7249e5c03dce38206c0daf`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.63013,0.20822,0.11412]},{"name":"goal","value":[0.45856,-0.02632,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78134,"average_solve_count":343.0,"average_success_count":343.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_object.lateral_offset_x":0.015,"align_to_object.lateral_offset_y":-0.00676,"approach_above_object.approach_speed":0.02265,"approach_goal.approach_goal_speed":0.06136,"descend_and_place.place_speed":0.03662,"descend_to_object.contact_force_threshold":2.22719,"descend_to_object.descend_speed":0.03276,"lift_object.lift_height":0.16691,"lift_object.lift_speed":0.04364},"optimized_scores":{"best_composite_score":-0.30782,"best_fitness_score":0.19718,"best_task_score":0.11003},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":885.0,"contact_point_centroid":[0.62551,-0.00243,-0.00049],"force_p95":194.1956,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1668.35535,"mean_force":201.1938,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.38221,-0.00246,0.12078]},{"body_a":"world","body_b":"link6","contact_count":10.0,"contact_point_centroid":[0.62003,-0.0036,-0.00018],"force_p95":320.14909,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":323.41524,"mean_force":192.97308,"phase_index":1.0,"phase_name":"align_to_object","phase_type":"align","tcp_position_centroid":[0.38477,-0.00378,0.13837]},{"body_a":"grasp_target","body_b":"hand","contact_count":36.0,"contact_point_centroid":[0.44201,-0.01498,0.04338],"force_p95":3.50614,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.90515,"mean_force":1.54839,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.37854,-0.00165,0.05483]},{"body_a":"world","body_b":"grasp_target","contact_count":3925.0,"contact_point_centroid":[0.42173,-0.02505,-0.00211],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.23597,"mean_force":0.13695,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.395,-0.00229,0.1305]},{"body_a":"grasp_target","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.47133,-0.00737,0.00851],"force_p95":0.43645,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.45858,"mean_force":0.26076,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.36695,-0.00173,0.05207]},{"body_a":"world","body_b":"grasp_target","contact_count":1264.0,"contact_point_centroid":[0.41647,-0.02485,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"align_to_object","phase_type":"align","tcp_position_centroid":[0.40312,-0.01632,0.12428]},{"body_a":"world","body_b":"grasp_target","contact_count":96.0,"contact_point_centroid":[0.41647,-0.02485,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.4221,-0.02842,0.11171]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.41647,-0.02485,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.41601,-0.02826,0.10166]},{"body_a":"world","body_b":"grasp_target","contact_count":11212.0,"contact_point_centroid":[0.41647,-0.02485,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.41231,-0.02824,0.27899]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.41647,-0.02485,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.48377,0.04759,0.40787]},{"body_a":"world","body_b":"grasp_target","contact_count":3104.0,"contact_point_centroid":[0.41647,-0.02485,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"descend_and_place","phase_type":"descend","tcp_position_centroid":[0.58722,0.16346,0.20834]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.41647,-0.02485,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61759,0.20124,0.11341]},{"body_a":"left_finger","body_b":"right_finger","contact_count":747.0,"contact_point_centroid":[0.4174,-0.02832,0.10011],"force_p95":0.01301,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.011,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.41527,-0.02825,0.10061]},{"body_a":"left_finger","body_b":"right_finger","contact_count":11925.0,"contact_point_centroid":[0.41435,-0.02835,0.2796],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01286,"mean_force":0.01048,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.41231,-0.02824,0.28022]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4351.0,"contact_point_centroid":[0.486,0.04789,0.40822],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.01027,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.48391,0.04774,0.40766]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3393.0,"contact_point_centroid":[0.58919,0.16395,0.2091],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01275,"mean_force":0.01022,"phase_index":6.0,"phase_name":"descend_and_place","phase_type":"descend","tcp_position_centroid":[0.58743,0.1637,0.20776]}],"total_contact_groups":18},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.41647,-0.02485,0.01602],"final_tcp_position":[0.62203,0.2025,0.11464],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273004.62583,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41647,-0.02485,0.01602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.33105,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":192.74635,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4877.0,"raw_peak_contact_force":1668.35535,"subtask_id":"reach_object","tcp_end":[0.38455,-0.00369,0.13787],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12773,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":316.0,"n_steps_budget":600.0,"object_pos_end":[0.41647,-0.02485,0.01602],"object_pos_start":[0.41647,-0.02485,0.01602],"object_to_goal_dist_end":0.33105,"object_to_goal_dist_start":0.33105,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"align_to_object","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1274.0,"raw_peak_contact_force":323.41524,"subtask_id":"reach_object","tcp_end":[0.42249,-0.02831,0.11329],"tcp_start":[0.38455,-0.00369,0.13787],"tcp_to_object_dist_end":0.09752,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":24.0,"n_steps_budget":1000.0,"object_pos_end":[0.41647,-0.02485,0.01602],"object_pos_start":[0.41647,-0.02485,0.01602],"object_to_goal_dist_end":0.33105,"object_to_goal_dist_start":0.33105,"object_z_max":0.01602,"peak_contact_force":81.14225,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":96.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.42136,-0.02837,0.10926],"tcp_start":[0.42249,-0.02831,0.11329],"tcp_to_object_dist_end":0.09343,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.41647,-0.02485,0.01602],"object_pos_start":[0.41647,-0.02485,0.01602],"object_to_goal_dist_end":0.33105,"object_to_goal_dist_start":0.33105,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2947.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.41527,-0.02825,0.10061],"tcp_start":[0.41527,-0.02825,0.10061],"tcp_to_object_dist_end":0.08467,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":2803.0,"n_steps_budget":1000.0,"object_pos_end":[0.41647,-0.02485,0.01602],"object_pos_start":[0.41647,-0.02485,0.01602],"object_to_goal_dist_end":0.33105,"object_to_goal_dist_start":0.33105,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23137.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.41387,-0.02835,0.50886],"tcp_start":[0.41239,-0.02824,0.35232],"tcp_to_object_dist_end":0.49286,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41647,-0.02485,0.01602],"object_pos_start":[0.41647,-0.02485,0.01602],"object_to_goal_dist_end":0.33105,"object_to_goal_dist_start":0.33105,"object_z_max":0.01602,"peak_contact_force":9749.03833,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8351.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.55259,0.12403,0.31052],"tcp_start":[0.41387,-0.02835,0.50886],"tcp_to_object_dist_end":0.35696,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":776.0,"n_steps_budget":1000.0,"object_pos_end":[0.41647,-0.02485,0.01602],"object_pos_start":[0.41647,-0.02485,0.01602],"object_to_goal_dist_end":0.33105,"object_to_goal_dist_start":0.33105,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_and_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6497.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.62203,0.2025,0.11464],"tcp_start":[0.55259,0.12403,0.31052],"tcp_to_object_dist_end":0.32197,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.41647,-0.02485,0.01602],"object_pos_start":[0.41647,-0.02485,0.01602],"object_to_goal_dist_end":0.33105,"object_to_goal_dist_start":0.33105,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61594,0.2007,0.13221],"tcp_start":[0.62203,0.2025,0.11464],"tcp_to_object_dist_end":0.32274,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```