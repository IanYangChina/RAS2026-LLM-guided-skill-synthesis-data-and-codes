## Search State

- **Seed**: 3
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5  | 0.0374 | 0.17 | ✅ accepted |
| 0 | rotate → retract → descend → pull → rotate | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3  | 0.2658 | 0.45 | ✅ accepted |

**Proposal policy**: task_score is 0.45 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`
- Frozen object start: [0.45856491671436245, -0.02631894934039003, 0.03]
- Frozen task target: [0.6301274465206397, 0.20821620360643678, 0.11411929633605987]
- Goal object position: (0.6301274465206397, 0.20821620360643678, 0.11411929633605987)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6301274465206397, 0.20821620360643678, 0.11411929633605987)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.45856491671436245, -0.02631894934039003, 0.03)
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
  frozen_object_start: [0.4586, -0.0263, 0.03]
  frozen_task_target: [0.6301, 0.2082, 0.1141]
  frozen_object_starts: {'grasp_target': [0.45856491671436245, -0.02631894934039003, 0.03]}
  frozen_targets: {'place_target': [0.6301274465206397, 0.20821620360643678, 0.11411929633605987]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7

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
| `object` | offset from object initial position (0.45856491671436245, -0.02631894934039003, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6301274465206397, 0.20821620360643678, 0.11411929633605987) | final destination targets |
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

## Current Skill (Q=0.266) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: pre_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: place_at_goal
  target_entity: object
  metric: goal_progress
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
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: pre_grasp
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.01
  parameters:
    grasp_offset_z:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: contact_guard
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: continue
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
  retries:
    max_attempts: 1
    strategy: repeat
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
    tolerance: 0.01
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
- id: approach_goal
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01
  parameters:
    travel_arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: generator.arc_height
        mode: replace
  subtask_id: place_at_goal
- id: lower_to_place
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.01
  parameters:
    place_offset_z:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
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
- id: retract_from_place
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - parameter_bindings:
    - grasp_offset_z: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=contact_guard, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=1.0
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - retries: max_attempts=1, strategy=repeat
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - parameter_bindings:
    - travel_arc_height: status=consumed; consumers=generator.arc_height (replace)
- **lower_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - parameter_bindings:
    - place_offset_z: status=consumed; consumers=target.offset.z (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract_from_place** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.266
- **task_score** (E): 0.445
- **fitness_score**: 0.696  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1899 |
| descend_to_grasp | 1.00 | 1.00 | 0.0711 |
| grasp_object | 1.00 | 1.00 | 0.0128 |
| lift_object | 1.00 | 1.00 | 0.1195 |
| approach_goal | 0.00 | 1.00 | 0.1059 |
| lower_to_place | 0.67 | 0.67 | 0.1493 |
| release_object | 1.00 | 1.00 | 0.0218 |
| retract_from_place | 1.00 | 1.00 | 0.0528 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.115) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, 0.002, 0.115)→(0.506, 0.002, 0.044) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.506, 0.002, 0.044)→(0.497, 0.002, 0.035) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 42.333 | 0.142 | 0.181 |
| lift_object | lift | 1.00 / step_budget | (0.497, 0.002, 0.035)→(0.493, 0.002, 0.154) | (0.511, 0.002, 0.026)→(0.504, 0.001, 0.137) | 0.246→0.220 | 1.00 / 34.667 | 0.095 | 0.594 |
| approach_goal | approach | 0.00 / step_budget | (0.493, 0.002, 0.154)→(0.524, 0.048, 0.240) | (0.504, 0.001, 0.137)→(0.532, 0.049, 0.216) | 0.220→0.183 | 1.00 / 27.333 | 0.114 | 0.191 |
| lower_to_place | descend | 0.67 / step_budget | (0.524, 0.048, 0.240)→(0.601, 0.154, 0.172) | (0.532, 0.049, 0.216)→(0.595, 0.160, 0.111) | 0.183→0.052 | 0.67 / 20.667 | 0.068 | 0.275 |
| release_object | release | 1.00 / step_budget | (0.601, 0.154, 0.172)→(0.595, 0.153, 0.193) | (0.595, 0.160, 0.111)→(0.591, 0.161, 0.018) | 0.052→0.128 | 1.00 / 3.333 | 0.180 | 1.373 |
| retract_from_place | retract | 1.00 / step_budget | (0.595, 0.153, 0.193)→(0.621, 0.179, 0.226) | (0.591, 0.161, 0.018)→(0.595, 0.166, 0.019) | 0.128→0.126 | 1.00 / 4.000 | 0.123 | 0.219 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.558
- phase_score: 0.351
- phase_breakdown.place_at_goal_score: 0.187
- phase_breakdown.pre_grasp_score: 0.733
- grasp_place_fitness: 0.752

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.752
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.558
- **Median Q (composite search score)**: 0.277
- **K-run variance**: 0.0026
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.404


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a4a71a7b2980790489e8194d1356bdee33fb951291c2e0792659ad3d3b3dc711`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `8a78b0f0015ebaf8c4b14c8fbc8142d9b66e4b4efca10f362859101c0ae207df`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83908,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.travel_arc_height":0.07585,"approach_object.approach_height":0.06139,"descend_to_grasp.grasp_offset_z":0.01084,"lift_object.lift_height":0.13444,"lower_to_place.place_offset_z":0.02027},"optimized_scores":{"best_composite_score":0.27678,"best_fitness_score":0.70678,"best_task_score":0.46852},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":775.0,"contact_point_centroid":[0.57764,0.18463,-0.00319],"force_p95":0.59337,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.15825,"mean_force":0.17038,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58351,0.1596,0.15833]},{"body_a":"world","body_b":"grasp_target","contact_count":127.0,"contact_point_centroid":[0.45521,-0.02507,-0.00112],"force_p95":0.31121,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52161,"mean_force":0.07911,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44429,-0.02552,0.03955]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12107.0,"contact_point_centroid":[0.54005,0.08046,0.19626],"force_p95":0.13174,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35254,"mean_force":0.08093,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.53767,0.09925,0.19837]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15648.0,"contact_point_centroid":[0.4437,-0.0065,0.09896],"force_p95":0.07635,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28537,"mean_force":0.05034,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44174,-0.02544,0.09743]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12877.0,"contact_point_centroid":[0.4422,-0.04465,0.10076],"force_p95":0.0811,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28524,"mean_force":0.0591,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44175,-0.02544,0.09823]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14656.0,"contact_point_centroid":[0.53487,0.11783,0.19747],"force_p95":0.09842,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2545,"mean_force":0.06232,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.53797,0.09964,0.19808]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15367.0,"contact_point_centroid":[0.46624,-0.01425,0.20398],"force_p95":0.10682,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19163,"mean_force":0.06429,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.46314,0.00475,0.20317]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02637,-0.00206],"force_p95":0.14182,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1768,"mean_force":0.12733,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44685,-0.0256,0.03876]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18434.0,"contact_point_centroid":[0.46557,0.02377,0.20473],"force_p95":0.0818,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17524,"mean_force":0.05246,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.46341,0.00509,0.20379]},{"body_a":"world","body_b":"grasp_target","contact_count":2412.0,"contact_point_centroid":[0.45856,-0.02632,-0.00194],"force_p95":0.13067,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47795,-0.01195,0.20059]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5159.0,"contact_point_centroid":[0.44694,-0.00648,0.0391],"force_p95":0.06848,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12844,"mean_force":0.04245,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44569,-0.02556,0.03765]},{"body_a":"world","body_b":"grasp_target","contact_count":760.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45446,-0.02504,0.07315]},{"body_a":"world","body_b":"grasp_target","contact_count":2016.0,"contact_point_centroid":[0.57754,0.18488,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_from_place","phase_type":"retract","tcp_position_centroid":[0.60206,0.18187,0.18834]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4415.0,"contact_point_centroid":[0.44515,-0.04482,0.04044],"force_p95":0.07932,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08505,"mean_force":0.04913,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44569,-0.02557,0.03765]}],"total_contact_groups":14},"final_pose_error":0.01388,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.57754,0.18488,0.01602],"final_tcp_position":[0.62329,0.20363,0.20295],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.15825,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":604.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2412.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.45728,-0.02437,0.1011],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07512,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":190.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":760.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45375,-0.02579,0.04543],"tcp_start":[0.45728,-0.02437,0.1011],"tcp_to_object_dist_end":0.02001,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45849,-0.02606,0.02578],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30356,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14151,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11374.0,"raw_peak_contact_force":0.1768,"tcp_end":[0.44566,-0.02556,0.03762],"tcp_start":[0.45375,-0.02579,0.04543],"tcp_to_object_dist_end":0.01746,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.45217,-0.02613,0.14081],"object_pos_start":[0.45849,-0.02606,0.02578],"object_to_goal_dist_end":0.29547,"object_to_goal_dist_start":0.30356,"object_z_max":0.1407,"peak_contact_force":0.0784,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28652.0,"raw_peak_contact_force":0.52161,"tcp_end":[0.442,-0.02543,0.16075],"tcp_start":[0.44566,-0.02556,0.03762],"tcp_to_object_dist_end":0.02239,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50235,0.04436,0.21537],"object_pos_start":[0.45217,-0.02613,0.14081],"object_to_goal_dist_end":0.23114,"object_to_goal_dist_start":0.29547,"object_z_max":0.21532,"peak_contact_force":0.11037,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":33801.0,"raw_peak_contact_force":0.19163,"subtask_id":"place_at_goal","tcp_end":[0.49462,0.04352,0.24107],"tcp_start":[0.442,-0.02543,0.16075],"tcp_to_object_dist_end":0.02686,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57736,0.1775,0.03434],"object_pos_start":[0.50235,0.04436,0.21537],"object_to_goal_dist_end":0.10046,"object_to_goal_dist_start":0.23114,"object_z_max":0.21537,"peak_contact_force":0.0,"phase_name":"lower_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":26763.0,"raw_peak_contact_force":0.35254,"tcp_end":[0.58797,0.16068,0.15685],"tcp_start":[0.49462,0.04352,0.24107],"tcp_to_object_dist_end":0.12411,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57754,0.18488,0.01602],"object_pos_start":[0.57736,0.1775,0.03434],"object_to_goal_dist_end":0.11373,"object_to_goal_dist_start":0.10046,"object_z_max":0.03434,"peak_contact_force":0.12261,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":775.0,"raw_peak_contact_force":1.15825,"tcp_end":[0.582,0.15915,0.17825],"tcp_start":[0.58797,0.16068,0.15685],"tcp_to_object_dist_end":0.16432,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":504.0,"n_steps_budget":600.0,"object_pos_end":[0.57754,0.18488,0.01602],"object_pos_start":[0.57754,0.18488,0.01602],"object_to_goal_dist_end":0.11373,"object_to_goal_dist_start":0.11373,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_from_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2016.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62329,0.20363,0.20295],"tcp_start":[0.582,0.15915,0.17825],"tcp_to_object_dist_end":0.19335,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `aa6ec658384c70fac6b4eb656cc8c53536c3d5c760368ab2b384dccf294e2c48`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.825,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.travel_arc_height":0.16021,"approach_object.approach_height":0.09262,"descend_to_grasp.grasp_offset_z":0.01008,"lift_object.lift_height":0.14746,"lower_to_place.place_offset_z":0.03466},"optimized_scores":{"best_composite_score":0.19831,"best_fitness_score":0.62831,"best_task_score":0.30909},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":94.0,"contact_point_centroid":[0.61023,0.13008,-0.01192],"force_p95":1.69283,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.91685,"mean_force":0.86684,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61623,0.12714,0.23964]},{"body_a":"world","body_b":"grasp_target","contact_count":141.0,"contact_point_centroid":[0.54042,0.00079,-0.00113],"force_p95":0.45895,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63373,"mean_force":0.09897,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52778,0.00079,0.03515]},{"body_a":"world","body_b":"grasp_target","contact_count":1776.0,"contact_point_centroid":[0.63321,0.14328,-0.0022],"force_p95":0.20657,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38935,"mean_force":0.13096,"phase_index":7.0,"phase_name":"retract_from_place","phase_type":"retract","tcp_position_centroid":[0.63017,0.14282,0.26254]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15168.0,"contact_point_centroid":[0.52672,0.01982,0.10212],"force_p95":0.08178,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35137,"mean_force":0.05709,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52512,0.00075,0.10018]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15794.0,"contact_point_centroid":[0.52668,-0.01828,0.09915],"force_p95":0.08247,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33,"mean_force":0.05524,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52515,0.00075,0.09718]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":861.0,"contact_point_centroid":[0.61415,0.14652,0.22155],"force_p95":0.1071,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24569,"mean_force":0.06711,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61945,0.12796,0.22314]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15461.0,"contact_point_centroid":[0.58271,0.09966,0.24393],"force_p95":0.09861,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21581,"mean_force":0.06571,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.58336,0.08066,0.24339]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18247.0,"contact_point_centroid":[0.58663,0.06197,0.24295],"force_p95":0.08194,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21383,"mean_force":0.05551,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.58327,0.08054,0.24345]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":977.0,"contact_point_centroid":[0.62181,0.10955,0.22059],"force_p95":0.0836,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20886,"mean_force":0.0507,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61958,0.12799,0.2234]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15449.0,"contact_point_centroid":[0.5283,-0.0146,0.22219],"force_p95":0.08617,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.197,"mean_force":0.06204,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52511,0.00423,0.22127]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14847.0,"contact_point_centroid":[0.52766,0.02279,0.22043],"force_p95":0.09112,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17446,"mean_force":0.06473,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52484,0.00387,0.21968]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00116,-0.00203],"force_p95":0.13336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15379,"mean_force":0.12532,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53069,0.00085,0.03498]},{"body_a":"world","body_b":"grasp_target","contact_count":2268.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51715,0.00048,0.21403]},{"body_a":"world","body_b":"grasp_target","contact_count":1044.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53627,0.00097,0.08623]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4840.0,"contact_point_centroid":[0.53067,-0.01823,0.03515],"force_p95":0.0686,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10179,"mean_force":0.04466,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52942,0.00083,0.0335]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4149.0,"contact_point_centroid":[0.53075,0.02004,0.03604],"force_p95":0.07523,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09593,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52942,0.00083,0.0335]}],"total_contact_groups":16},"final_pose_error":0.01345,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.63397,0.1448,0.01602],"final_tcp_position":[0.64261,0.15505,0.279],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.91685,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":568.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2268.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.5369,0.00098,0.12932],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10356,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":261.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1044.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53826,0.00101,0.04391],"tcp_start":[0.5369,0.00098,0.12932],"tcp_to_object_dist_end":0.01888,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54418,0.00105,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25032,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13339,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10789.0,"raw_peak_contact_force":0.15379,"tcp_end":[0.52938,0.00083,0.03346],"tcp_start":[0.53826,0.00101,0.04391],"tcp_to_object_dist_end":0.01663,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.53612,0.00063,0.15199],"object_pos_start":[0.54418,0.00105,0.02587],"object_to_goal_dist_end":0.19686,"object_to_goal_dist_start":0.25032,"object_z_max":0.15187,"peak_contact_force":0.0911,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":31103.0,"raw_peak_contact_force":0.63373,"tcp_end":[0.52555,0.00076,0.16824],"tcp_start":[0.52938,0.00083,0.03346],"tcp_to_object_dist_end":0.01938,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54557,0.02101,0.24688],"object_pos_start":[0.53612,0.00063,0.15199],"object_to_goal_dist_end":0.17976,"object_to_goal_dist_start":0.19686,"object_z_max":0.24677,"peak_contact_force":0.11294,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":30296.0,"raw_peak_contact_force":0.197,"subtask_id":"place_at_goal","tcp_end":[0.538,0.0204,0.27001],"tcp_start":[0.52555,0.00076,0.16824],"tcp_to_object_dist_end":0.02435,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61799,0.1284,0.19542],"object_pos_start":[0.54557,0.02101,0.24688],"object_to_goal_dist_end":0.04216,"object_to_goal_dist_start":0.17976,"object_z_max":0.24691,"peak_contact_force":0.10813,"phase_name":"lower_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":33708.0,"raw_peak_contact_force":0.21581,"tcp_end":[0.621,0.12818,0.22683],"tcp_start":[0.538,0.0204,0.27001],"tcp_to_object_dist_end":0.03155,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62108,0.13185,0.01075],"object_pos_start":[0.61799,0.1284,0.19542],"object_to_goal_dist_end":0.18418,"object_to_goal_dist_start":0.04216,"object_z_max":0.19542,"peak_contact_force":0.28007,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1932.0,"raw_peak_contact_force":1.91685,"tcp_end":[0.61619,0.12714,0.24729],"tcp_start":[0.621,0.12818,0.22683],"tcp_to_object_dist_end":0.23664,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.63397,0.1448,0.01602],"object_pos_start":[0.62108,0.13185,0.01075],"object_to_goal_dist_end":0.17612,"object_to_goal_dist_start":0.18418,"object_z_max":0.02232,"peak_contact_force":0.12263,"phase_name":"retract_from_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1776.0,"raw_peak_contact_force":0.38935,"tcp_end":[0.64261,0.15505,0.279],"tcp_start":[0.61619,0.12714,0.24729],"tcp_to_object_dist_end":0.26332,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e1209649252ffcf03853fe0727696e22a1eda11729c6c1ae21659980557d7e98`; realized-scene SHA-256: `e32d7866764afb23ec7c7faebb4bcca0aa39fbf2f1ab61f3c9c527b297153af9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75974,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.travel_arc_height":0.16991,"approach_object.approach_height":0.07869,"descend_to_grasp.grasp_offset_z":0.01,"lift_object.lift_height":0.11294,"lower_to_place.place_offset_z":0.02986},"optimized_scores":{"best_composite_score":0.32223,"best_fitness_score":0.75223,"best_task_score":0.5579},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":312.0,"contact_point_centroid":[0.57381,0.16725,-0.00404],"force_p95":0.87941,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.04518,"mean_force":0.22389,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58839,0.17163,0.14251]},{"body_a":"world","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.52698,0.02896,-0.0012],"force_p95":0.41663,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62623,"mean_force":0.09515,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51415,0.02938,0.03566]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10904.0,"contact_point_centroid":[0.51267,0.04844,0.08618],"force_p95":0.11014,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4167,"mean_force":0.0613,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5115,0.02921,0.08383]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12976.0,"contact_point_centroid":[0.51344,0.01061,0.08353],"force_p95":0.08631,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32362,"mean_force":0.05096,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51152,0.02921,0.08196]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13913.0,"contact_point_centroid":[0.57247,0.11254,0.16502],"force_p95":0.08923,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25781,"mean_force":0.05441,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.56814,0.13078,0.16539]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1060.0,"contact_point_centroid":[0.58687,0.1912,0.13005],"force_p95":0.08773,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25021,"mean_force":0.05032,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59276,0.173,0.12954]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1099.0,"contact_point_centroid":[0.59567,0.15418,0.12761],"force_p95":0.09506,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24682,"mean_force":0.05081,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59272,0.17298,0.12949]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10726.0,"contact_point_centroid":[0.56685,0.15038,0.1663],"force_p95":0.1093,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22876,"mean_force":0.07107,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.56852,0.13138,0.16494]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53057,0.03078,-0.00211],"force_p95":0.15433,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21311,"mean_force":0.13108,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51705,0.02958,0.03528]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12656.0,"contact_point_centroid":[0.52241,0.06861,0.17664],"force_p95":0.11498,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1834,"mean_force":0.07618,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5204,0.04936,0.17558]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5272.0,"contact_point_centroid":[0.51704,0.01056,0.03594],"force_p95":0.06759,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16639,"mean_force":0.04093,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51579,0.02949,0.03386]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17492.0,"contact_point_centroid":[0.52363,0.03051,0.17504],"force_p95":0.08965,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15595,"mean_force":0.05508,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51999,0.04869,0.17458]},{"body_a":"world","body_b":"grasp_target","contact_count":1936.0,"contact_point_centroid":[0.57336,0.16706,-0.00198],"force_p95":0.12998,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14586,"mean_force":0.12264,"phase_index":7.0,"phase_name":"retract_from_place","phase_type":"retract","tcp_position_centroid":[0.59139,0.17403,0.17346]},{"body_a":"world","body_b":"grasp_target","contact_count":2392.0,"contact_point_centroid":[0.5305,0.03079,-0.00194],"force_p95":0.13083,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51085,0.01398,0.20747]},{"body_a":"world","body_b":"grasp_target","contact_count":908.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52306,0.02915,0.07959]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4181.0,"contact_point_centroid":[0.51663,0.04884,0.03667],"force_p95":0.09142,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09617,"mean_force":0.05483,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5158,0.02949,0.03387]}],"total_contact_groups":16},"final_pose_error":0.01322,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57335,0.16706,0.02602],"final_tcp_position":[0.59693,0.17697,0.1958],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.04518,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":599.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2392.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.52415,0.0284,0.11601],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09025,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":227.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":908.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5245,0.03006,0.04383],"tcp_start":[0.52415,0.0284,0.11601],"tcp_to_object_dist_end":0.01881,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53057,0.03018,0.0256],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18402,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15216,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11253.0,"raw_peak_contact_force":0.21311,"tcp_end":[0.51576,0.02949,0.03382],"tcp_start":[0.5245,0.03006,0.04383],"tcp_to_object_dist_end":0.01696,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.52369,0.02985,0.11886],"object_pos_start":[0.53057,0.03018,0.0256],"object_to_goal_dist_end":0.16822,"object_to_goal_dist_start":0.18402,"object_z_max":0.11875,"peak_contact_force":0.11502,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24025.0,"raw_peak_contact_force":0.62623,"tcp_end":[0.51165,0.02923,0.13436],"tcp_start":[0.51576,0.02949,0.03382],"tcp_to_object_dist_end":0.01963,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54695,0.08139,0.18722],"object_pos_start":[0.52369,0.02985,0.11886],"object_to_goal_dist_end":0.1367,"object_to_goal_dist_start":0.16822,"object_z_max":0.18717,"peak_contact_force":0.11785,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":30148.0,"raw_peak_contact_force":0.1834,"subtask_id":"place_at_goal","tcp_end":[0.539,0.07989,0.20987],"tcp_start":[0.51165,0.02923,0.13436],"tcp_to_object_dist_end":0.02405,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":739.0,"n_steps_budget":1000.0,"object_pos_end":[0.59035,0.17357,0.10432],"object_pos_start":[0.54695,0.08139,0.18722],"object_to_goal_dist_end":0.01282,"object_to_goal_dist_start":0.1367,"object_z_max":0.18722,"peak_contact_force":0.09718,"phase_name":"lower_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":24639.0,"raw_peak_contact_force":0.25781,"tcp_end":[0.59466,0.17338,0.13292],"tcp_start":[0.539,0.07989,0.20987],"tcp_to_object_dist_end":0.02893,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57353,0.16714,0.02651],"object_pos_start":[0.59035,0.17357,0.10432],"object_to_goal_dist_end":0.087,"object_to_goal_dist_start":0.01282,"object_z_max":0.10432,"peak_contact_force":0.13875,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2471.0,"raw_peak_contact_force":1.04518,"tcp_end":[0.58828,0.1716,0.15403],"tcp_start":[0.59466,0.17338,0.13292],"tcp_to_object_dist_end":0.12844,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.57335,0.16706,0.02602],"object_pos_start":[0.57353,0.16714,0.02651],"object_to_goal_dist_end":0.08754,"object_to_goal_dist_start":0.087,"object_z_max":0.02651,"peak_contact_force":0.12263,"phase_name":"retract_from_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1936.0,"raw_peak_contact_force":0.14586,"tcp_end":[0.59693,0.17697,0.1958],"tcp_start":[0.58828,0.1716,0.15403],"tcp_to_object_dist_end":0.1717,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```