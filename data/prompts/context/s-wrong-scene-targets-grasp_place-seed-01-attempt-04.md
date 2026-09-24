## Search State

- **Seed**: 1
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | contact_detected | time_limit | pose_tolerance | 6 | -0.3258 | 0.14 | ❌ rejected |
| 3 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |
| 2 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | force_threshold_switch | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 9 | -0.0718 | 0.16 | ❌ rejected |
| 0 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ✅ accepted |

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

## Current Skill (Q=-0.326) — your mutation base

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

- **Composite score**: -0.326
- **task_score** (E): 0.143
- **fitness_score**: 0.154  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_object | 0.00 | 1.00 | 0.1712 |
| descend_to_grasp | 1.00 | 1.00 | 0.0323 |
| grasp_object | 1.00 | 1.00 | 0.0000 |
| lift_object | 1.00 | 1.00 | 0.0175 |
| transport_to_goal | 1.00 | 1.00 | 0.2866 |
| descend_to_place | 1.00 | 1.00 | 0.1359 |
| release_object | 1.00 | 1.00 | 0.0189 |
| retract_away | 1.00 | 1.00 | 0.1128 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.409, -0.000, 0.157) | (0.479, -0.000, 0.030)→(0.449, 0.000, 0.019) | 0.276→0.297 | 1.00 / 5.000 | 209.438 | 1345.751 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.409, -0.000, 0.157)→(0.415, 0.003, 0.183) | (0.449, 0.000, 0.019)→(0.448, 0.000, 0.019) | 0.297→0.297 | 1.00 / 5.000 | 253.611 | 465.317 |
| grasp_object | grasp | 1.00 / step_budget | (0.415, 0.003, 0.182)→(0.415, 0.003, 0.182) | (0.448, 0.000, 0.019)→(0.448, 0.000, 0.019) | 0.297→0.297 | 1.00 / 9.000 | 70.823 | 302.246 |
| lift_object | lift | 1.00 / step_budget | (0.415, 0.003, 0.182)→(0.430, 0.001, 0.175) | (0.448, 0.000, 0.019)→(0.448, 0.000, 0.019) | 0.297→0.297 | 1.00 / 8.000 | 3249.640 | 346.474 |
| transport_to_goal | approach | 1.00 / step_budget | (0.430, 0.001, 0.175)→(0.600, 0.195, 0.285) | (0.448, 0.000, 0.019)→(0.448, 0.000, 0.019) | 0.297→0.297 | 1.00 / 8.333 | 0.123 | 0.123 |
| descend_to_place | descend | 1.00 / step_budget | (0.600, 0.195, 0.285)→(0.605, 0.202, 0.150) | (0.448, 0.000, 0.019)→(0.448, 0.000, 0.019) | 0.297→0.297 | 1.00 / 8.000 | 3249.797 | 0.123 |
| release_object | release | 1.00 / step_budget | (0.605, 0.202, 0.150)→(0.600, 0.201, 0.168) | (0.448, 0.000, 0.019)→(0.448, 0.000, 0.019) | 0.297→0.297 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_away | retract | 1.00 / step_budget | (0.600, 0.201, 0.168)→(0.607, 0.203, 0.280) | (0.448, 0.000, 0.019)→(0.448, 0.000, 0.019) | 0.297→0.297 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.197
- phase_score: 0.436
- phase_breakdown.place_phase_score: 0.626
- phase_breakdown.approach_object_score: 0.341
- phase_breakdown.grasp_phase_score: 0.038
- grasp_place_fitness: 0.172

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.172
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.197
- **Median Q (composite search score)**: -0.334
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at upper bound**: descend_to_grasp.descend_speed
- **Final σ (mean)**: 0.331


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.62209,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_speed":0.09729,"descend_to_grasp.descend_speed":0.1,"descend_to_place.place_speed":0.05169,"lift_object.lift_height":0.16541,"lift_object.lift_speed":0.11031,"transport_to_goal.transport_speed":0.16578},"optimized_scores":{"best_composite_score":-0.30811,"best_fitness_score":0.17189,"best_task_score":0.19685},"replay_outcomes":[{"contacts":{"omitted_contact_groups":5,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.64052,0.01583,-0.00045],"force_p95":220.82284,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1346.50215,"mean_force":209.39963,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.40597,0.01504,0.13249]},{"body_a":"world","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.53284,0.01284,-0.00342],"force_p95":263.86761,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1343.72508,"mean_force":68.92323,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.38157,0.00772,0.04657]},{"body_a":"world","body_b":"link6","contact_count":995.0,"contact_point_centroid":[0.61508,0.03266,-0.00024],"force_p95":430.0288,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":881.75307,"mean_force":270.58719,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4206,0.03573,0.19559]},{"body_a":"world","body_b":"link6","contact_count":546.0,"contact_point_centroid":[0.64703,0.04112,-0.00013],"force_p95":82.14793,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":737.74568,"mean_force":74.18145,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45453,0.04831,0.20589]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.64717,0.0411,-0.00011],"force_p95":553.22445,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":587.45787,"mean_force":322.52555,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45459,0.04829,0.20584]},{"body_a":"grasp_target","body_b":"link7","contact_count":604.0,"contact_point_centroid":[0.49839,0.03006,0.04666],"force_p95":0.93151,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.68619,"mean_force":0.2934,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.40001,0.0118,0.11712]},{"body_a":"grasp_target","body_b":"hand","contact_count":335.0,"contact_point_centroid":[0.49259,0.02977,0.05573],"force_p95":2.23279,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.19875,"mean_force":0.47512,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.39514,0.00945,0.10005]},{"body_a":"world","body_b":"grasp_target","contact_count":2954.0,"contact_point_centroid":[0.48956,0.04765,-0.00263],"force_p95":0.30299,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.4916,"mean_force":0.18124,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.42232,0.01493,0.14884]},{"body_a":"grasp_target","body_b":"link7","contact_count":278.0,"contact_point_centroid":[0.50648,0.03658,0.05335],"force_p95":0.28376,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30366,"mean_force":0.17224,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.39221,0.03178,0.16198]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.49247,0.04566,-0.00215],"force_p95":0.20543,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24091,"mean_force":0.13295,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4207,0.03574,0.1956]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.49221,0.04577,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45454,0.04831,0.2059]},{"body_a":"world","body_b":"grasp_target","contact_count":276.0,"contact_point_centroid":[0.49221,0.04577,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46243,0.0475,0.19854]},{"body_a":"world","body_b":"grasp_target","contact_count":2564.0,"contact_point_centroid":[0.49221,0.04577,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51552,0.14159,0.23493]},{"body_a":"world","body_b":"grasp_target","contact_count":2028.0,"contact_point_centroid":[0.49221,0.04577,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55931,0.23749,0.21579]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.49221,0.04577,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55795,0.24134,0.14937]},{"body_a":"world","body_b":"grasp_target","contact_count":1732.0,"contact_point_centroid":[0.49221,0.04577,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.55911,0.24209,0.22203]}],"total_contact_groups":21},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.49221,0.04577,0.02602],"final_tcp_position":[0.56292,0.24395,0.27686],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":9749.14493,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49349,0.04519,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24389,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":226.50974,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4803.0,"raw_peak_contact_force":1346.50215,"subtask_id":"approach_object","tcp_end":[0.42616,0.02722,0.18037],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16936,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49221,0.04577,0.02602],"object_pos_start":[0.49349,0.04519,0.02602],"object_to_goal_dist_end":0.2438,"object_to_goal_dist_start":0.24389,"object_z_max":0.02603,"peak_contact_force":373.62575,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5273.0,"raw_peak_contact_force":881.75307,"subtask_id":"approach_object","tcp_end":[0.45467,0.04828,0.20686],"tcp_start":[0.42616,0.02722,0.18037],"tcp_to_object_dist_end":0.18471,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.49221,0.04577,0.02602],"object_pos_start":[0.49221,0.04577,0.02602],"object_to_goal_dist_end":0.2438,"object_to_goal_dist_start":0.2438,"object_z_max":0.02602,"peak_contact_force":70.70453,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3492.0,"raw_peak_contact_force":737.74568,"subtask_id":"grasp_phase","tcp_end":[0.45454,0.04829,0.20579],"tcp_start":[0.45454,0.04829,0.20579],"tcp_to_object_dist_end":0.18369,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":69.0,"n_steps_budget":600.0,"object_pos_end":[0.49221,0.04577,0.02602],"object_pos_start":[0.49221,0.04577,0.02602],"object_to_goal_dist_end":0.2438,"object_to_goal_dist_start":0.2438,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":572.0,"raw_peak_contact_force":587.45787,"subtask_id":"grasp_phase","tcp_end":[0.47241,0.04636,0.19159],"tcp_start":[0.45454,0.04829,0.20579],"tcp_to_object_dist_end":0.16675,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":641.0,"n_steps_budget":1000.0,"object_pos_end":[0.49221,0.04577,0.02602],"object_pos_start":[0.49221,0.04577,0.02602],"object_to_goal_dist_end":0.2438,"object_to_goal_dist_start":0.2438,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5303.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_phase","tcp_end":[0.55838,0.23318,0.2819],"tcp_start":[0.47241,0.04636,0.19159],"tcp_to_object_dist_end":0.324,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":507.0,"n_steps_budget":1000.0,"object_pos_end":[0.49221,0.04577,0.02602],"object_pos_start":[0.49221,0.04577,0.02602],"object_to_goal_dist_end":0.2438,"object_to_goal_dist_start":0.2438,"object_z_max":0.02602,"peak_contact_force":9749.14493,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4242.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_phase","tcp_end":[0.5611,0.24265,0.14971],"tcp_start":[0.55838,0.23318,0.2819],"tcp_to_object_dist_end":0.2425,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49221,0.04577,0.02602],"object_pos_start":[0.49221,0.04577,0.02602],"object_to_goal_dist_end":0.2438,"object_to_goal_dist_start":0.2438,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_phase","tcp_end":[0.5569,0.24088,0.16862],"tcp_start":[0.5611,0.24265,0.14971],"tcp_to_object_dist_end":0.25018,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":433.0,"n_steps_budget":810.0,"object_pos_end":[0.49221,0.04577,0.02602],"object_pos_start":[0.49221,0.04577,0.02602],"object_to_goal_dist_end":0.2438,"object_to_goal_dist_start":0.2438,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1732.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56292,0.24395,0.27686],"tcp_start":[0.5569,0.24088,0.16862],"tcp_to_object_dist_end":0.32742,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.44878,"average_solve_count":205.0,"average_success_count":205.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_speed":0.07295,"descend_to_grasp.descend_speed":0.02084,"descend_to_place.place_speed":0.03583,"lift_object.lift_height":0.14232,"lift_object.lift_speed":0.06259,"transport_to_goal.transport_speed":0.18956},"optimized_scores":{"best_composite_score":-0.3336,"best_fitness_score":0.1464,"best_task_score":0.12093},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.63591,-0.00601,-0.00045],"force_p95":199.90342,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1327.29343,"mean_force":200.53107,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.39183,-0.00568,0.1162]},{"body_a":"world","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.52696,-0.00031,-0.00312],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1274.82318,"mean_force":53.11763,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.37578,-0.0034,0.04762]},{"body_a":"world","body_b":"link6","contact_count":7.0,"contact_point_centroid":[0.61007,-0.0135,-0.00011],"force_p95":274.81151,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":277.8844,"mean_force":203.69859,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.39793,-0.01403,0.1718]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.61928,-0.01132,-0.00026],"force_p95":195.13168,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":225.39501,"mean_force":193.40425,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.38863,-0.0121,0.14475]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.60992,-0.01343,-0.00014],"force_p95":81.78498,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":83.89697,"mean_force":73.81047,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.39775,-0.01399,0.1717]},{"body_a":"grasp_target","body_b":"hand","contact_count":41.0,"contact_point_centroid":[0.454,-0.01467,0.04009],"force_p95":3.70295,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.08249,"mean_force":1.65434,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.38497,-0.0034,0.04991]},{"body_a":"world","body_b":"grasp_target","contact_count":3923.0,"contact_point_centroid":[0.44064,-0.01931,-0.00214],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.38187,"mean_force":0.13861,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.40378,-0.00531,0.12661]},{"body_a":"grasp_target","body_b":"link7","contact_count":27.0,"contact_point_centroid":[0.48382,-0.00558,0.00994],"force_p95":0.63955,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.65501,"mean_force":0.27827,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.37571,-0.00341,0.05062]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.43566,-0.01918,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.38863,-0.0121,0.14475]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.43566,-0.01918,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.39775,-0.01399,0.1717]},{"body_a":"world","body_b":"grasp_target","contact_count":260.0,"contact_point_centroid":[0.43566,-0.01918,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.40593,-0.01523,0.16768]},{"body_a":"world","body_b":"grasp_target","contact_count":3600.0,"contact_point_centroid":[0.43566,-0.01918,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52157,0.07019,0.24256]},{"body_a":"world","body_b":"grasp_target","contact_count":1920.0,"contact_point_centroid":[0.43566,-0.01918,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62473,0.15473,0.25873]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.43566,-0.01918,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62477,0.157,0.19185]},{"body_a":"world","body_b":"grasp_target","contact_count":1832.0,"contact_point_centroid":[0.43566,-0.01918,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.62614,0.15746,0.26475]},{"body_a":"left_finger","body_b":"right_finger","contact_count":753.0,"contact_point_centroid":[0.3998,-0.01401,0.17041],"force_p95":0.01321,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01093,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.39781,-0.01402,0.17159]}],"total_contact_groups":20},"final_pose_error":0.01991,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.43566,-0.01918,0.01602],"final_tcp_position":[0.63005,0.15863,0.32016],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1327.29343,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43566,-0.01918,0.01602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.31688,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":192.9684,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4902.0,"raw_peak_contact_force":1327.29343,"subtask_id":"approach_object","tcp_end":[0.39977,-0.00912,0.14383],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13314,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43566,-0.01918,0.01602],"object_pos_start":[0.43566,-0.01918,0.01602],"object_to_goal_dist_end":0.31688,"object_to_goal_dist_start":0.31688,"object_z_max":0.01602,"peak_contact_force":193.25042,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5000.0,"raw_peak_contact_force":225.39501,"subtask_id":"approach_object","tcp_end":[0.39738,-0.01393,0.17193],"tcp_start":[0.39977,-0.00912,0.14383],"tcp_to_object_dist_end":0.16063,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.43566,-0.01918,0.01602],"object_pos_start":[0.43566,-0.01918,0.01602],"object_to_goal_dist_end":0.31688,"object_to_goal_dist_start":0.31688,"object_z_max":0.01602,"peak_contact_force":70.96561,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3503.0,"raw_peak_contact_force":83.89697,"subtask_id":"grasp_phase","tcp_end":[0.39781,-0.01403,0.17159],"tcp_start":[0.39781,-0.01402,0.17159],"tcp_to_object_dist_end":0.16019,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":65.0,"n_steps_budget":600.0,"object_pos_end":[0.43566,-0.01918,0.01602],"object_pos_start":[0.43566,-0.01918,0.01602],"object_to_goal_dist_end":0.31688,"object_to_goal_dist_start":0.31688,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":538.0,"raw_peak_contact_force":277.8844,"subtask_id":"grasp_phase","tcp_end":[0.41618,-0.01681,0.16107],"tcp_start":[0.39781,-0.01403,0.17159],"tcp_to_object_dist_end":0.14637,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":900.0,"n_steps_budget":1000.0,"object_pos_end":[0.43566,-0.01918,0.01602],"object_pos_start":[0.43566,-0.01918,0.01602],"object_to_goal_dist_end":0.31688,"object_to_goal_dist_start":0.31688,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7496.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_phase","tcp_end":[0.62253,0.15221,0.32372],"tcp_start":[0.41618,-0.01681,0.16107],"tcp_to_object_dist_end":0.39871,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":480.0,"n_steps_budget":1000.0,"object_pos_end":[0.43566,-0.01918,0.01602],"object_pos_start":[0.43566,-0.01918,0.01602],"object_to_goal_dist_end":0.31688,"object_to_goal_dist_start":0.31688,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4014.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_phase","tcp_end":[0.62789,0.15781,0.19302],"tcp_start":[0.62253,0.15221,0.32372],"tcp_to_object_dist_end":0.3156,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.43566,-0.01918,0.01602],"object_pos_start":[0.43566,-0.01918,0.01602],"object_to_goal_dist_end":0.31688,"object_to_goal_dist_start":0.31688,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1030.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_phase","tcp_end":[0.62376,0.1567,0.21078],"tcp_start":[0.62789,0.15781,0.19302],"tcp_to_object_dist_end":0.32287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":458.0,"n_steps_budget":810.0,"object_pos_end":[0.43566,-0.01918,0.01602],"object_pos_start":[0.43566,-0.01918,0.01602],"object_to_goal_dist_end":0.31688,"object_to_goal_dist_start":0.31688,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1832.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63005,0.15863,0.32016],"tcp_start":[0.62376,0.1567,0.21078],"tcp_to_object_dist_end":0.40237,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.46226,"average_solve_count":212.0,"average_success_count":212.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_speed":0.13242,"descend_to_grasp.descend_speed":0.01016,"descend_to_place.place_speed":0.07004,"lift_object.lift_height":0.16673,"lift_object.lift_speed":0.03272,"transport_to_goal.transport_speed":0.09056},"optimized_scores":{"best_composite_score":-0.33573,"best_fitness_score":0.14427,"best_task_score":0.11015},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.52407,-0.00297,-0.00349],"force_p95":205.7213,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1363.45672,"mean_force":64.82433,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.37408,-0.00538,0.04579]},{"body_a":"world","body_b":"link6","contact_count":888.0,"contact_point_centroid":[0.63392,-0.01126,-0.00046],"force_p95":211.50564,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1358.75122,"mean_force":207.90356,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.39025,-0.01055,0.11568]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.61683,-0.0224,-0.00025],"force_p95":196.98297,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":288.80367,"mean_force":195.00726,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.38552,-0.02341,0.14386]},{"body_a":"world","body_b":"link6","contact_count":9.0,"contact_point_centroid":[0.60789,-0.02531,-0.0001],"force_p95":173.46156,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":174.08021,"mean_force":139.05665,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.39335,-0.02618,0.16879]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.60766,-0.02526,-0.00014],"force_p95":82.65941,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":85.09622,"mean_force":73.85342,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.39321,-0.02614,0.16885]},{"body_a":"grasp_target","body_b":"hand","contact_count":41.0,"contact_point_centroid":[0.43811,-0.01575,0.04114],"force_p95":3.67943,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.87861,"mean_force":1.42337,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.38349,-0.00537,0.04765]},{"body_a":"world","body_b":"grasp_target","contact_count":3915.0,"contact_point_centroid":[0.42242,-0.02555,-0.00213],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.37166,"mean_force":0.13842,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.40224,-0.00984,0.12622]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.41737,-0.02544,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.38552,-0.02341,0.14386]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.41737,-0.02544,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.39321,-0.02614,0.16885]},{"body_a":"world","body_b":"grasp_target","contact_count":156.0,"contact_point_centroid":[0.41737,-0.02544,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.39615,-0.02614,0.16965]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.41737,-0.02544,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51272,0.08964,0.21012]},{"body_a":"world","body_b":"grasp_target","contact_count":2436.0,"contact_point_centroid":[0.41737,-0.02544,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62217,0.20272,0.16975]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.41737,-0.02544,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62129,0.20551,0.10566]},{"body_a":"world","body_b":"grasp_target","contact_count":2104.0,"contact_point_centroid":[0.41737,-0.02544,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.62228,0.20577,0.18389]},{"body_a":"left_finger","body_b":"right_finger","contact_count":754.0,"contact_point_centroid":[0.39507,-0.02616,0.16754],"force_p95":0.01285,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01091,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.39328,-0.02617,0.16873]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4298.0,"contact_point_centroid":[0.51516,0.09044,0.2108],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01286,"mean_force":0.01037,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51326,0.09019,0.21032]}],"total_contact_groups":19},"final_pose_error":0.01991,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.41737,-0.02544,0.01602],"final_tcp_position":[0.6275,0.2073,0.2444],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":9748.67416,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41737,-0.02544,0.01602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.33088,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":208.83736,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4869.0,"raw_peak_contact_force":1363.45672,"subtask_id":"approach_object","tcp_end":[0.40062,-0.01839,0.14757],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1328,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41737,-0.02544,0.01602],"object_pos_start":[0.41737,-0.02544,0.01602],"object_to_goal_dist_end":0.33088,"object_to_goal_dist_start":0.33088,"object_z_max":0.01602,"peak_contact_force":193.95571,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5000.0,"raw_peak_contact_force":288.80367,"subtask_id":"approach_object","tcp_end":[0.39284,-0.02606,0.16908],"tcp_start":[0.40062,-0.01839,0.14757],"tcp_to_object_dist_end":0.15501,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.41737,-0.02544,0.01602],"object_pos_start":[0.41737,-0.02544,0.01602],"object_to_goal_dist_end":0.33088,"object_to_goal_dist_start":0.33088,"object_z_max":0.01602,"peak_contact_force":70.79987,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3504.0,"raw_peak_contact_force":85.09622,"subtask_id":"grasp_phase","tcp_end":[0.39328,-0.02618,0.16873],"tcp_start":[0.39328,-0.02617,0.16873],"tcp_to_object_dist_end":0.1546,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":39.0,"n_steps_budget":600.0,"object_pos_end":[0.41737,-0.02544,0.01602],"object_pos_start":[0.41737,-0.02544,0.01602],"object_to_goal_dist_end":0.33088,"object_to_goal_dist_start":0.33088,"object_z_max":0.01602,"peak_contact_force":9748.67416,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":328.0,"raw_peak_contact_force":174.08021,"subtask_id":"grasp_phase","tcp_end":[0.40118,-0.02599,0.17143],"tcp_start":[0.39328,-0.02618,0.16873],"tcp_to_object_dist_end":0.15626,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":999.0,"n_steps_budget":1000.0,"object_pos_end":[0.41737,-0.02544,0.01602],"object_pos_start":[0.41737,-0.02544,0.01602],"object_to_goal_dist_end":0.33088,"object_to_goal_dist_start":0.33088,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8294.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_phase","tcp_end":[0.61938,0.19839,0.25057],"tcp_start":[0.40118,-0.02599,0.17143],"tcp_to_object_dist_end":0.38199,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":609.0,"n_steps_budget":1000.0,"object_pos_end":[0.41737,-0.02544,0.01602],"object_pos_start":[0.41737,-0.02544,0.01602],"object_to_goal_dist_end":0.33088,"object_to_goal_dist_start":0.33088,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5085.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_phase","tcp_end":[0.62571,0.2068,0.10668],"tcp_start":[0.61938,0.19839,0.25057],"tcp_to_object_dist_end":0.3249,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.41737,-0.02544,0.01602],"object_pos_start":[0.41737,-0.02544,0.01602],"object_to_goal_dist_end":0.33088,"object_to_goal_dist_start":0.33088,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1031.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_phase","tcp_end":[0.61958,0.20499,0.1244],"tcp_start":[0.62571,0.2068,0.10668],"tcp_to_object_dist_end":0.32517,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":526.0,"n_steps_budget":900.0,"object_pos_end":[0.41737,-0.02544,0.01602],"object_pos_start":[0.41737,-0.02544,0.01602],"object_to_goal_dist_end":0.33088,"object_to_goal_dist_start":0.33088,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2104.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6275,0.2073,0.2444],"tcp_start":[0.61958,0.20499,0.1244],"tcp_to_object_dist_end":0.38792,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```