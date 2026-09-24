## Search State

- **Seed**: 9
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.2254 | 0.17 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 0 | 0.1349 | 0.19 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.2191 | 0.15 | ❌ rejected |
| 0 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 0 | 0.1349 | 0.19 | ✅ accepted |

**Proposal policy**: task_score is 0.17 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.225) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_grasp_standoff
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: reach_place_standoff
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.7
phases:
- id: approach_object
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.005
    orientation:
      mode: keep_current
  subtask_id: reach_grasp_standoff
- id: descend_object
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
- id: grasp_object
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
- id: lift_object
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.005
    orientation:
      mode: keep_current
- id: approach_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.005
    orientation:
      mode: keep_current
  subtask_id: reach_place_standoff
- id: descend_goal
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
- id: release_object
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
- id: retract_goal
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.005
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.05], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_object** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.05], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **retract_goal** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.05], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.225
- **task_score** (E): 0.167
- **fitness_score**: 0.555  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.33 | 1.00 | 0.1811 |
| descend_object | 1.00 | 1.00 | 0.0858 |
| grasp_object | 1.00 | 1.00 | 0.0119 |
| lift_object | 1.00 | 1.00 | 0.1245 |
| transport_to_goal | 0.00 | 1.00 | 0.0825 |
| descend_goal | 0.00 | 1.00 | 0.0845 |
| release_object | 1.00 | 1.00 | 0.0233 |
| retract_goal | 1.00 | 1.00 | 0.0393 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.503, -0.012, 0.123) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_object | descend | 1.00 / step_budget | (0.503, -0.012, 0.123)→(0.508, -0.016, 0.037) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.508, -0.016, 0.037)→(0.500, -0.016, 0.029) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 38.000 | 0.148 | 0.205 |
| lift_object | lift | 1.00 / step_budget | (0.500, -0.016, 0.029)→(0.496, -0.016, 0.153) | (0.515, -0.016, 0.026)→(0.510, -0.016, 0.132) | 0.270→0.234 | 1.00 / 15.333 | 9963.017 | 0.626 |
| transport_to_goal | approach | 0.00 / step_budget | (0.496, -0.016, 0.153)→(0.518, 0.022, 0.222) | (0.510, -0.016, 0.132)→(0.505, -0.009, 0.016) | 0.234→0.276 | 1.00 / 8.667 | 185253.328 | 1.492 |
| descend_goal | descend | 0.00 / step_budget | (0.518, 0.022, 0.222)→(0.557, 0.088, 0.192) | (0.505, -0.009, 0.016)→(0.505, -0.009, 0.016) | 0.276→0.276 | 1.00 / 8.667 | 182003.862 | 0.123 |
| release_object | release | 1.00 / step_budget | (0.557, 0.088, 0.192)→(0.552, 0.088, 0.215) | (0.505, -0.009, 0.016)→(0.505, -0.009, 0.016) | 0.276→0.276 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_goal | retract | 1.00 / step_budget | (0.552, 0.088, 0.215)→(0.549, 0.087, 0.254) | (0.505, -0.009, 0.016)→(0.505, -0.009, 0.016) | 0.276→0.276 | 1.00 / 4.000 | 27.129 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.232
- phase_score: 0.295
- phase_breakdown.reach_place_standoff_score: 0.033
- phase_breakdown.reach_grasp_standoff_score: 0.907
- grasp_place_fitness: 0.595

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.595
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.232
- **Median Q (composite search score)**: 0.211
- **K-run variance**: 0.0008
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.517


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.74658,"average_solve_count":146.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_object.lift_offset_z":0.15725,"transport_to_goal.place_standoff_z":0.08109,"transport_to_goal.transport_arc_height":0.064},"optimized_scores":{"best_composite_score":0.20078,"best_fitness_score":0.53078,"best_task_score":0.10981},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3635.0,"contact_point_centroid":[0.51657,-0.02601,-0.00226],"force_p95":0.12653,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.56124,"mean_force":0.13614,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52189,-0.00027,0.20459]},{"body_a":"world","body_b":"grasp_target","contact_count":221.0,"contact_point_centroid":[0.5328,-0.02009,-0.00125],"force_p95":0.40993,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71906,"mean_force":0.10764,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5197,-0.02033,0.02518]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":171.0,"contact_point_centroid":[0.52027,-0.03587,0.16294],"force_p95":0.25079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32205,"mean_force":0.09727,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51762,-0.02009,0.16841]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11382.0,"contact_point_centroid":[0.52126,-0.00162,0.08655],"force_p95":0.13896,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32185,"mean_force":0.08322,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51754,-0.02028,0.08586]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12076.0,"contact_point_centroid":[0.52128,-0.03888,0.08414],"force_p95":0.13544,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31377,"mean_force":0.07941,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51756,-0.02028,0.08373]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53705,-0.02104,-0.00208],"force_p95":0.14864,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22636,"mean_force":0.12964,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52308,-0.02039,0.02507]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20.0,"contact_point_centroid":[0.52469,-0.00297,0.16166],"force_p95":0.16485,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18196,"mean_force":0.11859,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51799,-0.02027,0.16844]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.53702,-0.02132,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51157,-0.00859,0.20609]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4073.0,"contact_point_centroid":[0.52311,-0.00117,0.02634],"force_p95":0.07883,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12705,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52183,-0.02037,0.02366]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_object","phase_type":"descend","tcp_position_centroid":[0.52537,-0.01828,0.07541]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51654,-0.02596,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.54319,0.06241,0.2259]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51654,-0.02596,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55426,0.09987,0.22164]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.51654,-0.02596,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.55036,0.09907,0.25915]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4953.0,"contact_point_centroid":[0.52302,-0.03949,0.02544],"force_p95":0.07082,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08776,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52183,-0.02037,0.02367]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3667.0,"contact_point_centroid":[0.52268,0.00093,0.20929],"force_p95":0.0112,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01618,"mean_force":0.01045,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52234,0.00093,0.20693]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4294.0,"contact_point_centroid":[0.54348,0.06232,0.22823],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01039,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.54315,0.06231,0.22591]}],"total_contact_groups":17},"final_pose_error":0.01128,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.51654,-0.02596,0.01602],"final_tcp_position":[0.5503,0.09904,0.28095],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273006.6739,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_grasp_standoff","tcp_end":[0.5229,-0.01552,0.1336],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10866,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53019,-0.02052,0.03313],"tcp_start":[0.5229,-0.01552,0.1336],"tcp_to_object_dist_end":0.00989,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53688,-0.02029,0.02572],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31612,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14272,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10826.0,"raw_peak_contact_force":0.22636,"tcp_end":[0.5218,-0.02037,0.02363],"tcp_start":[0.53019,-0.02052,0.03313],"tcp_to_object_dist_end":0.01522,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":932.0,"n_steps_budget":990.0,"object_pos_end":[0.53069,-0.02079,0.14474],"object_pos_start":[0.53688,-0.02029,0.02572],"object_to_goal_dist_end":0.26841,"object_to_goal_dist_start":0.31612,"object_z_max":0.14511,"peak_contact_force":0.15449,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23679.0,"raw_peak_contact_force":0.71906,"tcp_end":[0.51797,-0.02028,0.16836],"tcp_start":[0.5218,-0.02037,0.02363],"tcp_to_object_dist_end":0.02684,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51654,-0.02596,0.01602],"object_pos_start":[0.53069,-0.02079,0.14474],"object_to_goal_dist_end":0.33135,"object_to_goal_dist_start":0.26841,"object_z_max":0.14474,"peak_contact_force":9748.85775,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7493.0,"raw_peak_contact_force":1.56124,"subtask_id":"reach_place_standoff","tcp_end":[0.53081,0.02273,0.23823],"tcp_start":[0.51797,-0.02028,0.16836],"tcp_to_object_dist_end":0.22793,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51654,-0.02596,0.01602],"object_pos_start":[0.51654,-0.02596,0.01602],"object_to_goal_dist_end":0.33135,"object_to_goal_dist_start":0.33135,"object_z_max":0.01602,"peak_contact_force":273006.6739,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8294.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5578,0.10046,0.21941],"tcp_start":[0.53081,0.02273,0.23823],"tcp_to_object_dist_end":0.24301,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51654,-0.02596,0.01602],"object_pos_start":[0.51654,-0.02596,0.01602],"object_to_goal_dist_end":0.33135,"object_to_goal_dist_start":0.33135,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55295,0.09958,0.24191],"tcp_start":[0.5578,0.10046,0.21941],"tcp_to_object_dist_end":0.26098,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.51654,-0.02596,0.01602],"object_pos_start":[0.51654,-0.02596,0.01602],"object_to_goal_dist_end":0.33135,"object_to_goal_dist_start":0.33135,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5503,0.09904,0.28095],"tcp_start":[0.55295,0.09958,0.24191],"tcp_to_object_dist_end":0.29488,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72993,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_object.lift_offset_z":0.12523,"transport_to_goal.place_standoff_z":0.14293,"transport_to_goal.transport_arc_height":0.05026},"optimized_scores":{"best_composite_score":0.21069,"best_fitness_score":0.54069,"best_task_score":0.15804},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3699.0,"contact_point_centroid":[0.54223,-0.04122,-0.00221],"force_p95":0.12823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.43225,"mean_force":0.1343,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5276,-0.01219,0.19088]},{"body_a":"world","body_b":"grasp_target","contact_count":247.0,"contact_point_centroid":[0.54274,-0.02573,-0.00141],"force_p95":0.17858,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39302,"mean_force":0.08246,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52506,-0.02618,0.0439]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8158.0,"contact_point_centroid":[0.52846,-0.00755,0.09258],"force_p95":0.1362,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36298,"mean_force":0.08943,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52303,-0.02611,0.09141]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8453.0,"contact_point_centroid":[0.52845,-0.04461,0.09235],"force_p95":0.12663,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36012,"mean_force":0.08801,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52304,-0.02611,0.09152]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54571,-0.02894,-0.00223],"force_p95":0.18856,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24993,"mean_force":0.13898,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52854,-0.02627,0.04365]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5.0,"contact_point_centroid":[0.53081,-0.00963,0.14782],"force_p95":0.18791,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18924,"mean_force":0.15435,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52334,-0.02611,0.15496]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.52923,-0.04145,0.14951],"force_p95":0.13644,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18416,"mean_force":0.03926,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52311,-0.02603,0.15502]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3111.0,"contact_point_centroid":[0.53101,-0.00737,0.04575],"force_p95":0.10772,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14579,"mean_force":0.0649,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52732,-0.02624,0.04221]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.5456,-0.02923,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51364,-0.01086,0.21296]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_object","phase_type":"descend","tcp_position_centroid":[0.52961,-0.02312,0.09345]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54231,-0.04122,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.55588,0.04075,0.20888]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54231,-0.04122,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57217,0.07452,0.19924]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.54231,-0.04122,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.56786,0.07385,0.23634]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3410.0,"contact_point_centroid":[0.53162,-0.04524,0.04446],"force_p95":0.10291,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10479,"mean_force":0.06402,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52733,-0.02624,0.04222]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3662.0,"contact_point_centroid":[0.52857,-0.01114,0.19614],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01615,"mean_force":0.01048,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5282,-0.01114,0.19378]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4275.0,"contact_point_centroid":[0.5562,0.04071,0.21117],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0128,"mean_force":0.01043,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.55586,0.04071,0.20889]}],"total_contact_groups":17},"final_pose_error":0.01162,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.54231,-0.04122,0.01602],"final_tcp_position":[0.56778,0.07382,0.25812],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":273005.63037,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_grasp_standoff","tcp_end":[0.52566,-0.01897,0.1509],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12688,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53549,-0.02646,0.05191],"tcp_start":[0.52566,-0.01897,0.1509],"tcp_to_object_dist_end":0.02793,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54564,-0.02703,0.02526],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.25972,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.17535,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8321.0,"raw_peak_contact_force":0.24993,"tcp_end":[0.52729,-0.02624,0.04217],"tcp_start":[0.53549,-0.02646,0.05191],"tcp_to_object_dist_end":0.02496,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":752.0,"n_steps_budget":810.0,"object_pos_end":[0.53163,-0.02689,0.1248],"object_pos_start":[0.54564,-0.02703,0.02526],"object_to_goal_dist_end":0.22306,"object_to_goal_dist_start":0.25972,"object_z_max":0.12513,"peak_contact_force":29888.77016,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16858.0,"raw_peak_contact_force":0.39302,"tcp_end":[0.52331,-0.02611,0.15493],"tcp_start":[0.52729,-0.02624,0.04217],"tcp_to_object_dist_end":0.03127,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54231,-0.04122,0.01602],"object_pos_start":[0.53163,-0.02689,0.1248],"object_to_goal_dist_end":0.27674,"object_to_goal_dist_start":0.22306,"object_z_max":0.1248,"peak_contact_force":273005.63037,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7451.0,"raw_peak_contact_force":1.43225,"subtask_id":"reach_place_standoff","tcp_end":[0.53781,0.00497,0.22659],"tcp_start":[0.52331,-0.02611,0.15493],"tcp_to_object_dist_end":0.21562,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54231,-0.04122,0.01602],"object_pos_start":[0.54231,-0.04122,0.01602],"object_to_goal_dist_end":0.27674,"object_to_goal_dist_start":0.27674,"object_z_max":0.01602,"peak_contact_force":273004.78857,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8275.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57603,0.07499,0.19735],"tcp_start":[0.53781,0.00497,0.22659],"tcp_to_object_dist_end":0.218,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54231,-0.04122,0.01602],"object_pos_start":[0.54231,-0.04122,0.01602],"object_to_goal_dist_end":0.27674,"object_to_goal_dist_start":0.27674,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57071,0.07427,0.21936],"tcp_start":[0.57603,0.07499,0.19735],"tcp_to_object_dist_end":0.23557,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.54231,-0.04122,0.01602],"object_pos_start":[0.54231,-0.04122,0.01602],"object_to_goal_dist_end":0.27674,"object_to_goal_dist_start":0.27674,"object_z_max":0.01602,"peak_contact_force":81.14225,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56778,0.07382,0.25812],"tcp_start":[0.57071,0.07427,0.21936],"tcp_to_object_dist_end":0.26925,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.66667,"average_solve_count":150.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_object.lift_offset_z":0.1268,"transport_to_goal.place_standoff_z":0.0838,"transport_to_goal.transport_arc_height":0.0554},"optimized_scores":{"best_composite_score":0.26466,"best_fitness_score":0.59466,"best_task_score":0.23214},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2692.0,"contact_point_centroid":[0.45499,0.04017,-0.00231],"force_p95":0.1334,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.48145,"mean_force":0.14131,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.4678,0.02272,0.18017]},{"body_a":"world","body_b":"grasp_target","contact_count":182.0,"contact_point_centroid":[0.45971,-2e-05,-0.00116],"force_p95":0.52073,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.7645,"mean_force":0.10788,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44889,-0.00024,0.02186]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11198.0,"contact_point_centroid":[0.44929,0.01868,0.07246],"force_p95":0.10902,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30802,"mean_force":0.06917,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44663,-0.00026,0.07068]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2623.0,"contact_point_centroid":[0.44944,0.02056,0.13761],"force_p95":0.16177,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30626,"mean_force":0.10559,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.4467,0.00258,0.14144]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12193.0,"contact_point_centroid":[0.449,-0.01906,0.07002],"force_p95":0.1091,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28281,"mean_force":0.06414,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44666,-0.00026,0.06888]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2323.0,"contact_point_centroid":[0.44943,-0.01602,0.13668],"force_p95":0.17731,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23698,"mean_force":0.10592,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.44639,0.00217,0.14042]},{"body_a":"world","body_b":"grasp_target","contact_count":3804.0,"contact_point_centroid":[0.46286,-7e-05,-0.00196],"force_p95":0.12508,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47875,-6e-05,0.18932]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46283,-4e-05,-0.00201],"force_p95":0.12748,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13832,"mean_force":0.12422,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45165,-0.00021,0.02137]},{"body_a":"world","body_b":"grasp_target","contact_count":1520.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_object","phase_type":"descend","tcp_position_centroid":[0.45761,-0.00013,0.05377]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.45501,0.04041,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.51082,0.06502,0.17708]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.45501,0.04041,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.53376,0.08928,0.16168]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.45501,0.04041,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.52899,0.08845,0.20004]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4146.0,"contact_point_centroid":[0.45078,0.01907,0.02263],"force_p95":0.07654,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09392,"mean_force":0.0521,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45055,-0.00022,0.02033]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5332.0,"contact_point_centroid":[0.45017,-0.01926,0.02268],"force_p95":0.0629,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08318,"mean_force":0.04075,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45055,-0.00022,0.02033]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2597.0,"contact_point_centroid":[0.46943,0.0239,0.18437],"force_p95":0.01119,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01069,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.46907,0.0239,0.18211]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4213.0,"contact_point_centroid":[0.51118,0.06504,0.17932],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01292,"mean_force":0.01057,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.51084,0.06504,0.17706]}],"total_contact_groups":17},"final_pose_error":0.01092,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.45501,0.04041,0.01602],"final_tcp_position":[0.52884,0.08841,0.22189],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":273005.49457,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":952.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3804.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_grasp_standoff","tcp_end":[0.46015,-0.0001,0.08407],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.05811,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":380.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1520.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45806,-0.00013,0.02742],"tcp_start":[0.46015,-0.0001,0.08407],"tcp_to_object_dist_end":0.005,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46271,1e-05,0.02593],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23317,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12737,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11278.0,"raw_peak_contact_force":0.13832,"tcp_end":[0.45052,-0.00022,0.0203],"tcp_start":[0.45806,-0.00013,0.02742],"tcp_to_object_dist_end":0.01343,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":752.0,"n_steps_budget":810.0,"object_pos_end":[0.4667,-0.00019,0.12614],"object_pos_start":[0.46271,1e-05,0.02593],"object_to_goal_dist_end":0.20982,"object_to_goal_dist_start":0.23317,"object_z_max":0.12605,"peak_contact_force":0.12598,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23573.0,"raw_peak_contact_force":0.7645,"tcp_end":[0.44674,-0.00024,0.1361],"tcp_start":[0.45052,-0.00022,0.0203],"tcp_to_object_dist_end":0.0223,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45501,0.04041,0.01602],"object_pos_start":[0.4667,-0.00019,0.12614],"object_to_goal_dist_end":0.21906,"object_to_goal_dist_start":0.20982,"object_z_max":0.1264,"peak_contact_force":273005.49457,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10235.0,"raw_peak_contact_force":1.48145,"subtask_id":"reach_place_standoff","tcp_end":[0.48555,0.03915,0.20086],"tcp_start":[0.44674,-0.00024,0.1361],"tcp_to_object_dist_end":0.18735,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45501,0.04041,0.01602],"object_pos_start":[0.45501,0.04041,0.01602],"object_to_goal_dist_end":0.21906,"object_to_goal_dist_start":0.21906,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8213.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53793,0.08995,0.15881],"tcp_start":[0.48555,0.03915,0.20086],"tcp_to_object_dist_end":0.1724,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45501,0.04041,0.01602],"object_pos_start":[0.45501,0.04041,0.01602],"object_to_goal_dist_end":0.21906,"object_to_goal_dist_start":0.21906,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53215,0.08898,0.18228],"tcp_start":[0.53793,0.08995,0.15881],"tcp_to_object_dist_end":0.18961,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.45501,0.04041,0.01602],"object_pos_start":[0.45501,0.04041,0.01602],"object_to_goal_dist_end":0.21906,"object_to_goal_dist_start":0.21906,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52884,0.08841,0.22189],"tcp_start":[0.53215,0.08898,0.18228],"tcp_to_object_dist_end":0.22391,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```