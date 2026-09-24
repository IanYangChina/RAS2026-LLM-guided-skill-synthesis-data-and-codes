## Search State

- **Seed**: 7
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | -0.1116 | 0.19 | ❌ rejected |
| 6 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.0470 | 0.18 | ❌ rejected |
| 4 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |
| 3 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |

**Proposal policy**: task_score is 0.19 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.112) — your mutation base

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

- **Composite score**: -0.112
- **task_score** (E): 0.185
- **fitness_score**: 0.468  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_grasp | 1.00 | 1.00 | 0.1682 |
| descend_to_object | 1.00 | 1.00 | 0.0800 |
| grasp_object | 1.00 | 1.00 | 0.0117 |
| lift_object | 0.67 | 1.00 | 0.1058 |
| transport_to_goal | 0.00 | 1.00 | 0.0885 |
| lower_to_goal | 0.00 | 1.00 | 0.0399 |
| release_object | 1.00 | 1.00 | 0.0241 |
| retract_from_goal | 0.00 | 1.00 | 0.0943 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_grasp | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.020, 0.138) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_object | descend | 1.00 / step_budget | (0.506, 0.020, 0.138)→(0.506, 0.022, 0.058) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 5.027 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.506, 0.022, 0.058)→(0.498, 0.022, 0.049) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.274 | 1.00 / 38.667 | 0.152 | 0.198 |
| lift_object | lift | 0.67 / step_budget | (0.495, 0.022, 0.105)→(0.492, 0.022, 0.211) | (0.511, 0.022, 0.026)→(0.502, 0.023, 0.083) | 0.274→0.249 | 1.00 / 17.667 | 3249.629 | 0.579 |
| transport_to_goal | approach | 0.00 / step_budget | (0.492, 0.022, 0.211)→(0.506, 0.051, 0.286) | (0.502, 0.024, 0.084)→(0.510, 0.037, 0.070) | 0.247→0.254 | 1.00 / 14.667 | 182003.704 | 0.570 |
| lower_to_goal | descend | 0.00 / step_budget | (0.506, 0.051, 0.286)→(0.520, 0.078, 0.263) | (0.510, 0.037, 0.070)→(0.517, 0.039, 0.016) | 0.254→0.265 | 1.00 / 8.333 | 91001.707 | 0.661 |
| release_object | release | 1.00 / step_budget | (0.520, 0.078, 0.263)→(0.517, 0.077, 0.287) | (0.517, 0.039, 0.016)→(0.517, 0.039, 0.016) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_from_goal | retract | 0.00 / step_budget | (0.517, 0.077, 0.287)→(0.515, 0.077, 0.381) | (0.517, 0.039, 0.016)→(0.517, 0.039, 0.016) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.291
- phase_score: 0.184
- phase_breakdown.reach_goal_approach_score: 0.042
- phase_breakdown.reach_goal_score: 0.063
- phase_breakdown.reach_lift_clearance_score: 0.488
- grasp_place_fitness: 0.612

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.612
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.291
- **Median Q (composite search score)**: -0.049
- **K-run variance**: 0.0224
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.362


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.22018,"average_solve_count":218.0,"average_success_count":218.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_grasp.speed":0.09372,"descend_to_object.speed":0.03929,"lift_object.lift_height":0.11663,"lift_object.lift_speed":0.09452,"lower_to_goal.speed":0.033,"retract_from_goal.speed":0.01747,"transport_to_goal.arc_height":0.0517,"transport_to_goal.speed":0.03386},"optimized_scores":{"best_composite_score":0.032,"best_fitness_score":0.612,"best_task_score":0.29124},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1937.0,"contact_point_centroid":[0.54367,0.06969,-0.00255],"force_p95":0.20266,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.73857,"mean_force":0.14783,"phase_index":5.0,"phase_name":"lower_to_goal","phase_type":"descend","tcp_position_centroid":[0.52967,0.07856,0.19488]},{"body_a":"world","body_b":"grasp_target","contact_count":148.0,"contact_point_centroid":[0.51011,0.03817,-0.00118],"force_p95":0.31416,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45685,"mean_force":0.0705,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49826,0.03848,0.04508]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11517.0,"contact_point_centroid":[0.49809,0.05725,0.09144],"force_p95":0.10167,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30183,"mean_force":0.06223,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49578,0.03829,0.08949]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11217.0,"contact_point_centroid":[0.49822,0.0194,0.09225],"force_p95":0.09659,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27527,"mean_force":0.06292,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49576,0.03829,0.09021]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4329.0,"contact_point_centroid":[0.52567,0.0865,0.19977],"force_p95":0.13284,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22694,"mean_force":0.0894,"phase_index":5.0,"phase_name":"lower_to_goal","phase_type":"descend","tcp_position_centroid":[0.5197,0.06823,0.20229]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51253,0.03961,-0.00209],"force_p95":0.14811,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2066,"mean_force":0.12963,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50103,0.03872,0.04461]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4290.0,"contact_point_centroid":[0.52577,0.0502,0.19933],"force_p95":0.11913,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18139,"mean_force":0.08849,"phase_index":5.0,"phase_name":"lower_to_goal","phase_type":"descend","tcp_position_centroid":[0.51991,0.06844,0.20214]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12981.0,"contact_point_centroid":[0.50907,0.06767,0.18149],"force_p95":0.09521,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14857,"mean_force":0.07214,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50322,0.04897,0.18084]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12560.0,"contact_point_centroid":[0.50918,0.03051,0.18211],"force_p95":0.09707,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14769,"mean_force":0.07469,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50346,0.04922,0.1815]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5063.0,"contact_point_centroid":[0.49973,0.01938,0.0464],"force_p95":0.06836,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14496,"mean_force":0.04293,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49986,0.03862,0.04331]},{"body_a":"world","body_b":"grasp_target","contact_count":2084.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_to_grasp","phase_type":"approach","tcp_position_centroid":[0.50279,0.01779,0.21864]},{"body_a":"world","body_b":"grasp_target","contact_count":3456.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.50647,0.03814,0.08059]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54369,0.06975,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.53021,0.08225,0.1951]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54369,0.06975,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.52591,0.08153,0.25012]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5446.0,"contact_point_centroid":[0.49956,0.0579,0.04583],"force_p95":0.06766,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07033,"mean_force":0.04104,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49986,0.03862,0.04331]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1825.0,"contact_point_centroid":[0.53072,0.07907,0.19683],"force_p95":0.01163,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01628,"mean_force":0.0106,"phase_index":5.0,"phase_name":"lower_to_goal","phase_type":"descend","tcp_position_centroid":[0.53018,0.07906,0.19457]}],"total_contact_groups":17},"final_pose_error":0.13151,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.54369,0.06975,0.01602],"final_tcp_position":[0.52608,0.08154,0.2842],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.73857,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":522.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2084.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.50772,0.0363,0.13787],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11201,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":864.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3456.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50765,0.03926,0.05201],"tcp_start":[0.50772,0.0363,0.13787],"tcp_to_object_dist_end":0.02645,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51245,0.03892,0.02567],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21295,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14476,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12309.0,"raw_peak_contact_force":0.2066,"tcp_end":[0.49983,0.03862,0.04327],"tcp_start":[0.50765,0.03926,0.05201],"tcp_to_object_dist_end":0.02166,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.50852,0.03834,0.12404],"object_pos_start":[0.51245,0.03892,0.02567],"object_to_goal_dist_end":0.1806,"object_to_goal_dist_start":0.21295,"object_z_max":0.12394,"peak_contact_force":0.08716,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22882.0,"raw_peak_contact_force":0.45685,"subtask_id":"reach_lift_clearance","tcp_end":[0.49591,0.03831,0.1482],"tcp_start":[0.49983,0.03862,0.04327],"tcp_to_object_dist_end":0.02725,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52333,0.06332,0.17924],"object_pos_start":[0.50852,0.03834,0.12404],"object_to_goal_dist_end":0.15479,"object_to_goal_dist_start":0.1806,"object_z_max":0.17921,"peak_contact_force":0.11206,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25541.0,"raw_peak_contact_force":0.14857,"subtask_id":"reach_goal_approach","tcp_end":[0.51738,0.06332,0.21071],"tcp_start":[0.49591,0.03831,0.1482],"tcp_to_object_dist_end":0.03203,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54369,0.06975,0.01602],"object_pos_start":[0.52333,0.06332,0.17924],"object_to_goal_dist_end":0.18504,"object_to_goal_dist_start":0.15479,"object_z_max":0.17924,"peak_contact_force":0.12263,"phase_name":"lower_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12381.0,"raw_peak_contact_force":1.73857,"subtask_id":"reach_goal","tcp_end":[0.53401,0.08286,0.19217],"tcp_start":[0.51738,0.06332,0.21071],"tcp_to_object_dist_end":0.17691,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54369,0.06975,0.01602],"object_pos_start":[0.54369,0.06975,0.01602],"object_to_goal_dist_end":0.18504,"object_to_goal_dist_start":0.18504,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52877,0.08199,0.21569],"tcp_start":[0.53401,0.08286,0.19217],"tcp_to_object_dist_end":0.2006,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54369,0.06975,0.01602],"object_pos_start":[0.54369,0.06975,0.01602],"object_to_goal_dist_end":0.18504,"object_to_goal_dist_start":0.18504,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52608,0.08154,0.2842],"tcp_start":[0.52877,0.08199,0.21569],"tcp_to_object_dist_end":0.26902,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09589,"average_solve_count":292.0,"average_success_count":292.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_grasp.speed":0.03803,"descend_to_object.speed":0.03377,"lift_object.lift_height":0.10496,"lift_object.lift_speed":0.0752,"lower_to_goal.speed":0.02337,"retract_from_goal.speed":0.0258,"transport_to_goal.arc_height":0.10204,"transport_to_goal.speed":0.05131},"optimized_scores":{"best_composite_score":-0.04887,"best_fitness_score":0.53113,"best_task_score":0.14532},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3158.0,"contact_point_centroid":[0.48244,0.06185,-0.00226],"force_p95":0.13019,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.43915,"mean_force":0.13815,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.45866,0.0394,0.20917]},{"body_a":"world","body_b":"grasp_target","contact_count":171.0,"contact_point_centroid":[0.48022,0.04469,-0.00135],"force_p95":0.2407,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41461,"mean_force":0.06495,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46879,0.04704,0.05162]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8490.0,"contact_point_centroid":[0.46917,0.02809,0.08666],"force_p95":0.14036,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38355,"mean_force":0.08861,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46657,0.04683,0.08854]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1057.0,"contact_point_centroid":[0.46779,0.06134,0.14835],"force_p95":0.14695,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32601,"mean_force":0.10652,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.46236,0.04376,0.15174]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11741.0,"contact_point_centroid":[0.46864,0.06509,0.0893],"force_p95":0.12019,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28648,"mean_force":0.06658,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46655,0.04683,0.08954]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":819.0,"contact_point_centroid":[0.46758,0.026,0.14727],"force_p95":0.19035,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26567,"mean_force":0.13366,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.46257,0.04398,0.15104]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48276,0.04869,-0.00215],"force_p95":0.16845,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21508,"mean_force":0.13363,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47163,0.04733,0.05082]},{"body_a":"world","body_b":"grasp_target","contact_count":2232.0,"contact_point_centroid":[0.4827,0.04873,-0.00194],"force_p95":0.13176,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_to_grasp","phase_type":"approach","tcp_position_centroid":[0.48923,0.02173,0.21912]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4178.0,"contact_point_centroid":[0.47084,0.02797,0.05036],"force_p95":0.09308,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13315,"mean_force":0.05535,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47053,0.04722,0.04967]},{"body_a":"world","body_b":"grasp_target","contact_count":2108.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.47753,0.04613,0.09557]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.48252,0.062,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"lower_to_goal","phase_type":"descend","tcp_position_centroid":[0.47018,0.061,0.24218]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.48252,0.062,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.47535,0.07356,0.24444]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.48252,0.062,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.47195,0.07302,0.31076]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5397.0,"contact_point_centroid":[0.47009,0.06615,0.05055],"force_p95":0.06828,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07311,"mean_force":0.03987,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47054,0.04722,0.04967]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3079.0,"contact_point_centroid":[0.45914,0.03944,0.21455],"force_p95":0.01111,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01733,"mean_force":0.01064,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.4587,0.03942,0.21235]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4205.0,"contact_point_centroid":[0.47064,0.06102,0.24435],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01282,"mean_force":0.01059,"phase_index":5.0,"phase_name":"lower_to_goal","phase_type":"descend","tcp_position_centroid":[0.47018,0.06101,0.24219]}],"total_contact_groups":17},"final_pose_error":0.10956,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.48252,0.062,0.01602],"final_tcp_position":[0.47226,0.07305,0.35597],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":273004.94223,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":559.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2232.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.48027,0.0445,0.13846],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11254,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":527.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":14.83475,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2108.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47802,0.04796,0.05755],"tcp_start":[0.48027,0.0445,0.13846],"tcp_to_object_dist_end":0.03188,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48269,0.04758,0.02526],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29123,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.17493,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11375.0,"raw_peak_contact_force":0.21508,"tcp_end":[0.47051,0.04722,0.04964],"tcp_start":[0.47802,0.04796,0.05755],"tcp_to_object_dist_end":0.02725,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":769.0,"n_steps_budget":870.0,"object_pos_end":[0.47305,0.04828,0.11107],"object_pos_start":[0.48269,0.04758,0.02526],"object_to_goal_dist_end":0.2423,"object_to_goal_dist_start":0.29123,"object_z_max":0.11099,"peak_contact_force":0.13812,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20402.0,"raw_peak_contact_force":0.41461,"subtask_id":"reach_lift_clearance","tcp_end":[0.46663,0.04685,0.14467],"tcp_start":[0.47051,0.04722,0.04964],"tcp_to_object_dist_end":0.03424,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48252,0.062,0.01602],"object_pos_start":[0.47305,0.04828,0.11107],"object_to_goal_dist_end":0.28932,"object_to_goal_dist_start":0.2423,"object_z_max":0.12196,"peak_contact_force":273004.94223,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8113.0,"raw_peak_contact_force":1.43915,"subtask_id":"reach_goal_approach","tcp_end":[0.46277,0.04541,0.24875],"tcp_start":[0.46663,0.04685,0.14467],"tcp_to_object_dist_end":0.23416,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48252,0.062,0.01602],"object_pos_start":[0.48252,0.062,0.01602],"object_to_goal_dist_end":0.28932,"object_to_goal_dist_start":0.28932,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lower_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8205.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.47851,0.07402,0.24044],"tcp_start":[0.46277,0.04541,0.24875],"tcp_to_object_dist_end":0.22478,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48252,0.062,0.01602],"object_pos_start":[0.48252,0.062,0.01602],"object_to_goal_dist_end":0.28932,"object_to_goal_dist_start":0.28932,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.4742,0.07336,0.26551],"tcp_start":[0.47851,0.07402,0.24044],"tcp_to_object_dist_end":0.24989,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48252,0.062,0.01602],"object_pos_start":[0.48252,0.062,0.01602],"object_to_goal_dist_end":0.28932,"object_to_goal_dist_start":0.28932,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47226,0.07305,0.35597],"tcp_start":[0.4742,0.07336,0.26551],"tcp_to_object_dist_end":0.34029,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.96542,"average_solve_count":347.0,"average_success_count":347.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_grasp.speed":0.03194,"descend_to_object.speed":0.04974,"lift_object.lift_height":0.10806,"lift_object.lift_speed":0.01157,"lower_to_goal.speed":0.01354,"retract_from_goal.speed":0.07568,"transport_to_goal.arc_height":0.09405,"transport_to_goal.speed":0.02139},"optimized_scores":{"best_composite_score":-0.31787,"best_fitness_score":0.26213,"best_task_score":0.11893},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":7529.0,"contact_point_centroid":[0.52549,-0.01395,-0.00202],"force_p95":0.12273,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86453,"mean_force":0.12526,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51425,-0.02057,0.21419]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9840.0,"contact_point_centroid":[0.51904,-0.00202,0.07349],"force_p95":0.12001,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32031,"mean_force":0.08832,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51866,-0.02067,0.07708]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11279.0,"contact_point_centroid":[0.51906,-0.0391,0.07402],"force_p95":0.1036,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18488,"mean_force":0.07709,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51865,-0.02067,0.07786]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53704,-0.02127,-0.00204],"force_p95":0.13727,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17131,"mean_force":0.12623,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52431,-0.02079,0.05556]},{"body_a":"world","body_b":"grasp_target","contact_count":2380.0,"contact_point_centroid":[0.53702,-0.02132,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_to_grasp","phase_type":"approach","tcp_position_centroid":[0.51369,-0.00963,0.21796]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.52945,-0.02044,0.08776]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.52548,-0.01345,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52323,0.00863,0.37181]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.52548,-0.01345,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"lower_to_goal","phase_type":"descend","tcp_position_centroid":[0.54367,0.06346,0.37219]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52548,-0.01345,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54709,0.07652,0.35991]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.52548,-0.01345,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.54599,0.07615,0.44098]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2671.0,"contact_point_centroid":[0.52398,-0.00202,0.05128],"force_p95":0.09781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10249,"mean_force":0.07611,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52312,-0.02077,0.05414]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2949.0,"contact_point_centroid":[0.52365,-0.03946,0.05106],"force_p95":0.0927,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09276,"mean_force":0.06992,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52312,-0.02077,0.05414]},{"body_a":"left_finger","body_b":"right_finger","contact_count":7371.0,"contact_point_centroid":[0.5142,-0.02057,0.2281],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01651,"mean_force":0.0105,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51383,-0.02056,0.22578]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4269.0,"contact_point_centroid":[0.54407,0.06347,0.37441],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01288,"mean_force":0.01044,"phase_index":5.0,"phase_name":"lower_to_goal","phase_type":"descend","tcp_position_centroid":[0.54367,0.06347,0.37218]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4278.0,"contact_point_centroid":[0.52368,0.0086,0.37411],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.01042,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52321,0.0086,0.37178]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.54872,0.07679,0.35771],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.011,"mean_force":0.00997,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54816,0.07679,0.35526]}],"total_contact_groups":16},"final_pose_error":0.07629,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.52548,-0.01345,0.01602],"final_tcp_position":[0.54684,0.07622,0.5039],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273006.05848,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":596.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2380.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.53019,-0.01961,0.1369],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1111,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5311,-0.02093,0.06372],"tcp_start":[0.53019,-0.01961,0.1369],"tcp_to_object_dist_end":0.03817,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53695,-0.02091,0.02583],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31652,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13571,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7420.0,"raw_peak_contact_force":0.17131,"tcp_end":[0.52309,-0.02077,0.05411],"tcp_start":[0.5311,-0.02093,0.06372],"tcp_to_object_dist_end":0.03149,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":2787.0,"n_steps_budget":1000.0,"object_pos_end":[0.52538,-0.01742,0.01424],"object_pos_start":[0.53695,-0.02091,0.02583],"object_to_goal_dist_end":0.32348,"object_to_goal_dist_start":0.31652,"object_z_max":0.06201,"peak_contact_force":9748.66109,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36019.0,"raw_peak_contact_force":0.86453,"subtask_id":"reach_lift_clearance","tcp_end":[0.51336,-0.02056,0.34031],"tcp_start":[0.51539,-0.02059,0.22311],"tcp_to_object_dist_end":0.32631,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52548,-0.01345,0.01602],"object_pos_start":[0.52548,-0.01345,0.01602],"object_to_goal_dist_end":0.31938,"object_to_goal_dist_start":0.31938,"object_z_max":0.01602,"peak_contact_force":273006.05848,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8278.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal_approach","tcp_end":[0.53733,0.04391,0.39931],"tcp_start":[0.51336,-0.02056,0.34031],"tcp_to_object_dist_end":0.38774,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52548,-0.01345,0.01602],"object_pos_start":[0.52548,-0.01345,0.01602],"object_to_goal_dist_end":0.31938,"object_to_goal_dist_start":0.31938,"object_z_max":0.01602,"peak_contact_force":273004.87698,"phase_name":"lower_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8269.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.5488,0.07682,0.35769],"tcp_start":[0.53733,0.04391,0.39931],"tcp_to_object_dist_end":0.35416,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52548,-0.01345,0.01602],"object_pos_start":[0.52548,-0.01345,0.01602],"object_to_goal_dist_end":0.31938,"object_to_goal_dist_start":0.31938,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54663,0.07637,0.38019],"tcp_start":[0.5488,0.07682,0.35769],"tcp_to_object_dist_end":0.37568,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52548,-0.01345,0.01602],"object_pos_start":[0.52548,-0.01345,0.01602],"object_to_goal_dist_end":0.31938,"object_to_goal_dist_start":0.31938,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54684,0.07622,0.5039],"tcp_start":[0.54663,0.07637,0.38019],"tcp_to_object_dist_end":0.49651,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```