## Search State

- **Seed**: 3
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.2590 | 0.33 | ✅ accepted |
| 2 | rotate → retract → descend → pull → rotate | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.0374 | 0.17 | ❌ rejected |
| 1 | rotate → retract → descend → pull → rotate | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.0374 | 0.17 | ❌ rejected |
| 0 | rotate → retract → descend → pull → rotate | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.0374 | 0.17 | ✅ accepted |

**Proposal policy**: task_score is 0.33 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.259) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: reach_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: reach_goal
  weight: 0.7
phases:
- id: approach_grasp
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
    - 0.05
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_grasp
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    descend_depth:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_grasp
- id: grasp
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
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
- id: lift_clear
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
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
- id: transport_approach
  type: approach
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
    orientation:
      mode: keep_current
  subtask_id: reach_goal
- id: place_descend
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    place_depth:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_goal
- id: release
  type: release
  control: position_control
  termination: pose_tolerance
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
- id: retract
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
    - 0.0
    offset_along_axis:
      distance: 0.05
      axis: world_z
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_grasp** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.05]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_depth: status=consumed; consumers=target.offset.z (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **lift_clear** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=1, strategy=repeat
- **transport_approach** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **place_descend** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_depth: status=consumed; consumers=target.offset.z (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.05, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.259
- **task_score** (E): 0.332
- **fitness_score**: 0.639  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_grasp | 1.00 | 1.00 | 0.2170 |
| descend_to_grasp | 1.00 | 1.00 | 0.0453 |
| grasp | 1.00 | 1.00 | 0.0121 |
| lift_clear | 1.00 | 1.00 | 0.1030 |
| transport_approach | 0.00 | 1.00 | 0.1018 |
| place_descend | 0.67 | 1.00 | 0.1029 |
| release | 1.00 | 1.00 | 0.0216 |
| retract | 1.00 | 1.00 | 0.0381 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_grasp | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.088) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 9.705 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, 0.002, 0.088)→(0.505, 0.002, 0.043) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 42.333 | 0.141 | 0.199 |
| grasp | grasp | 1.00 / step_budget | (0.505, 0.002, 0.043)→(0.497, 0.002, 0.034) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 23.667 | 0.105 | 0.590 |
| lift_clear | lift | 1.00 / step_budget | (0.497, 0.002, 0.034)→(0.493, 0.002, 0.137) | (0.511, 0.002, 0.026)→(0.508, 0.002, 0.119) | 0.246→0.220 | 1.00 / 14.000 | 0.119 | 0.998 |
| transport_approach | approach | 0.00 / step_budget | (0.493, 0.002, 0.137)→(0.546, 0.079, 0.172) | (0.508, 0.002, 0.119)→(0.535, 0.072, 0.056) | 0.220→0.182 | 1.00 / 8.333 | 91002.097 | 0.539 |
| place_descend | descend | 0.67 / step_budget | (0.546, 0.079, 0.172)→(0.602, 0.156, 0.139) | (0.535, 0.072, 0.056)→(0.550, 0.091, 0.016) | 0.182→0.171 | 1.00 / 4.000 | 0.123 | 0.123 |
| release | release | 1.00 / step_budget | (0.602, 0.156, 0.139)→(0.596, 0.154, 0.160) | (0.550, 0.091, 0.016)→(0.550, 0.091, 0.016) | 0.171→0.171 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.596, 0.154, 0.160)→(0.592, 0.153, 0.198) | (0.550, 0.091, 0.016)→(0.550, 0.091, 0.016) | 0.171→0.171 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.381
- phase_score: 0.729
- phase_breakdown.reach_grasp_score: 0.434
- phase_breakdown.reach_goal_score: 0.855
- grasp_place_fitness: 0.667

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.667
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.395
- **Median Q (composite search score)**: 0.285
- **K-run variance**: 0.0015
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.239


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73381,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_grasp.approach_speed":0.25609,"descend_to_grasp.descend_depth":0.01564,"lift_clear.lift_height":0.11073,"place_descend.place_depth":0.00929},"optimized_scores":{"best_composite_score":0.28501,"best_fitness_score":0.66501,"best_task_score":0.39527},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2647.0,"contact_point_centroid":[0.56881,0.13063,-0.00229],"force_p95":0.13022,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.37144,"mean_force":0.13878,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.56849,0.1377,0.13844]},{"body_a":"world","body_b":"grasp_target","contact_count":128.0,"contact_point_centroid":[0.45584,-0.02472,-0.00113],"force_p95":0.34622,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44567,"mean_force":0.05948,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.44552,-0.02535,0.04503]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10644.0,"contact_point_centroid":[0.44544,-0.00626,0.09157],"force_p95":0.09255,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28163,"mean_force":0.06122,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.44313,-0.02524,0.08929]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11110.0,"contact_point_centroid":[0.44544,-0.04422,0.08987],"force_p95":0.09285,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2755,"mean_force":0.05955,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.44313,-0.02524,0.08806]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2667.0,"contact_point_centroid":[0.53391,0.06926,0.15482],"force_p95":0.14625,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25092,"mean_force":0.09128,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.52771,0.08743,0.15721]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2598.0,"contact_point_centroid":[0.53441,0.10631,0.15448],"force_p95":0.12422,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21454,"mean_force":0.09211,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.52829,0.08813,0.15697]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02622,-0.00207],"force_p95":0.14439,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19956,"mean_force":0.12846,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44795,-0.02544,0.04422]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12895.0,"contact_point_centroid":[0.48699,0.00777,0.15446],"force_p95":0.0964,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18986,"mean_force":0.07273,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.4811,0.02644,0.15391]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12457.0,"contact_point_centroid":[0.48745,0.04582,0.15455],"force_p95":0.09787,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13879,"mean_force":0.07533,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.48164,0.02711,0.1541]},{"body_a":"world","body_b":"grasp_target","contact_count":2156.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13209,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_grasp","phase_type":"approach","tcp_position_centroid":[0.47801,-0.01202,0.19471]},{"body_a":"world","body_b":"grasp_target","contact_count":564.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45492,-0.025,0.07017]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56894,0.13064,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58356,0.16017,0.13147]},{"body_a":"world","body_b":"grasp_target","contact_count":1820.0,"contact_point_centroid":[0.56894,0.13064,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.57836,0.15862,0.16988]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4826.0,"contact_point_centroid":[0.44687,-0.00618,0.04549],"force_p95":0.06899,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10694,"mean_force":0.04493,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44688,-0.0254,0.0432]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5179.0,"contact_point_centroid":[0.44673,-0.04463,0.04498],"force_p95":0.06779,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.06961,"mean_force":0.04286,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44689,-0.0254,0.0432]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2484.0,"contact_point_centroid":[0.57131,0.14066,0.13974],"force_p95":0.01134,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01579,"mean_force":0.01065,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57094,0.14066,0.13741]}],"total_contact_groups":17},"final_pose_error":0.01234,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.56894,0.13064,0.01602],"final_tcp_position":[0.57813,0.15854,0.18958],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.37144,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":540.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":564.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.45719,-0.02443,0.08962],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06365,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":141.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14145,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11805.0,"raw_peak_contact_force":0.19956,"subtask_id":"reach_grasp","tcp_end":[0.45428,-0.02566,0.05042],"tcp_start":[0.45719,-0.02443,0.08962],"tcp_to_object_dist_end":0.02479,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45849,-0.02564,0.02573],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30325,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.08684,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":21882.0,"raw_peak_contact_force":0.44567,"tcp_end":[0.44686,-0.0254,0.04317],"tcp_start":[0.45428,-0.02566,0.05042],"tcp_to_object_dist_end":0.02097,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.45641,-0.02529,0.11915],"object_pos_start":[0.45849,-0.02564,0.02573],"object_to_goal_dist_end":0.29108,"object_to_goal_dist_start":0.30325,"object_z_max":0.11904,"peak_contact_force":0.11285,"phase_name":"lift_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25352.0,"raw_peak_contact_force":0.18986,"tcp_end":[0.44313,-0.02523,0.14301],"tcp_start":[0.44686,-0.0254,0.04317],"tcp_to_object_dist_end":0.02731,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52371,0.07263,0.13505],"object_pos_start":[0.45641,-0.02529,0.11915],"object_to_goal_dist_end":0.17363,"object_to_goal_dist_start":0.29108,"object_z_max":0.13505,"peak_contact_force":0.12263,"phase_name":"transport_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10396.0,"raw_peak_contact_force":1.37144,"subtask_id":"reach_goal","tcp_end":[0.51803,0.07261,0.16696],"tcp_start":[0.44313,-0.02523,0.14301],"tcp_to_object_dist_end":0.03241,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56894,0.13064,0.01602],"object_pos_start":[0.52371,0.07263,0.13505],"object_to_goal_dist_end":0.13923,"object_to_goal_dist_start":0.17363,"object_z_max":0.13505,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.58818,0.16139,0.13018],"tcp_start":[0.51803,0.07261,0.16696],"tcp_to_object_dist_end":0.11979,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56894,0.13064,0.01602],"object_pos_start":[0.56894,0.13064,0.01602],"object_to_goal_dist_end":0.13923,"object_to_goal_dist_start":0.13923,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1820.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58175,0.1596,0.15133],"tcp_start":[0.58818,0.16139,0.13018],"tcp_to_object_dist_end":0.13896,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.56894,0.13064,0.01602],"object_pos_start":[0.56894,0.13064,0.01602],"object_to_goal_dist_end":0.13923,"object_to_goal_dist_start":0.13923,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2156.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.57813,0.15854,0.18958],"tcp_start":[0.58175,0.1596,0.15133],"tcp_to_object_dist_end":0.17603,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71094,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_grasp.approach_speed":0.40365,"descend_to_grasp.descend_depth":0.00525,"lift_clear.lift_height":0.12201,"place_descend.place_depth":-0.0033},"optimized_scores":{"best_composite_score":0.20509,"best_fitness_score":0.58509,"best_task_score":0.21847},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2694.0,"contact_point_centroid":[0.54374,0.05278,-0.00244],"force_p95":0.22587,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.46394,"mean_force":0.14791,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.55222,0.04043,0.1703]},{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.54117,0.00045,-0.00111],"force_p95":0.46599,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68002,"mean_force":0.09237,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.52756,0.00082,0.03033]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9122.0,"contact_point_centroid":[0.52877,-0.01797,0.07855],"force_p95":0.11151,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33468,"mean_force":0.07654,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.52489,0.00078,0.07666]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9415.0,"contact_point_centroid":[0.5289,0.01949,0.07766],"force_p95":0.10898,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31682,"mean_force":0.07461,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.52493,0.00078,0.07583]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1529.0,"contact_point_centroid":[0.53289,-0.00931,0.13834],"force_p95":0.18828,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24294,"mean_force":0.11775,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.52852,0.00887,0.14183]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1893.0,"contact_point_centroid":[0.53311,0.02775,0.13858],"force_p95":0.16516,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23572,"mean_force":0.10471,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.52911,0.00993,0.1425]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.001,-0.00203],"force_p95":0.13217,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15889,"mean_force":0.12536,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53046,0.00088,0.03011]},{"body_a":"world","body_b":"grasp_target","contact_count":2332.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_grasp","phase_type":"approach","tcp_position_centroid":[0.5174,0.00049,0.19249]},{"body_a":"world","body_b":"grasp_target","contact_count":652.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53635,0.00098,0.06253]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54439,0.05441,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.59581,0.09824,0.17975]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54439,0.05441,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61842,0.13026,0.17938]},{"body_a":"world","body_b":"grasp_target","contact_count":1820.0,"contact_point_centroid":[0.54439,0.05441,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.6139,0.12912,0.2167]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4114.0,"contact_point_centroid":[0.53045,-0.01835,0.03135],"force_p95":0.07614,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11528,"mean_force":0.05175,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52921,0.00086,0.02868]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4879.0,"contact_point_centroid":[0.53036,0.01993,0.03047],"force_p95":0.06819,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09145,"mean_force":0.04477,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52922,0.00086,0.02868]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2816.0,"contact_point_centroid":[0.55297,0.04087,0.1729],"force_p95":0.01121,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01845,"mean_force":0.01063,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.55256,0.04087,0.17072]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4235.0,"contact_point_centroid":[0.59624,0.09826,0.18202],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01295,"mean_force":0.01052,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.59582,0.09825,0.17975]}],"total_contact_groups":17},"final_pose_error":0.0129,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.54439,0.05441,0.01602],"final_tcp_position":[0.61375,0.12907,0.23633],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273006.0443,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":584.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":652.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.53706,0.00099,0.08675],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06116,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":163.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13013,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15889,"subtask_id":"reach_grasp","tcp_end":[0.53782,0.00101,0.03869],"tcp_start":[0.53706,0.00099,0.08675],"tcp_to_object_dist_end":0.01424,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54417,0.00073,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.11868,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":18679.0,"raw_peak_contact_force":0.68002,"tcp_end":[0.52918,0.00085,0.02864],"tcp_start":[0.53782,0.00101,0.03869],"tcp_to_object_dist_end":0.01524,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.54102,0.00086,0.12321],"object_pos_start":[0.54417,0.00073,0.02588],"object_to_goal_dist_end":0.20172,"object_to_goal_dist_start":0.25053,"object_z_max":0.1231,"peak_contact_force":0.12263,"phase_name":"lift_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8932.0,"raw_peak_contact_force":1.46394,"tcp_end":[0.52506,0.00079,0.13811],"tcp_start":[0.52918,0.00085,0.02864],"tcp_to_object_dist_end":0.02184,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54439,0.05441,0.01602],"object_pos_start":[0.54102,0.00086,0.12321],"object_to_goal_dist_end":0.22816,"object_to_goal_dist_start":0.20172,"object_z_max":0.12367,"peak_contact_force":273006.0443,"phase_name":"transport_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8235.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.56588,0.05768,0.18682],"tcp_start":[0.52506,0.00079,0.13811],"tcp_to_object_dist_end":0.17218,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54439,0.05441,0.01602],"object_pos_start":[0.54439,0.05441,0.01602],"object_to_goal_dist_end":0.22816,"object_to_goal_dist_start":0.22816,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.62252,0.13117,0.17889],"tcp_start":[0.56588,0.05768,0.18682],"tcp_to_object_dist_end":0.19628,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54439,0.05441,0.01602],"object_pos_start":[0.54439,0.05441,0.01602],"object_to_goal_dist_end":0.22816,"object_to_goal_dist_start":0.22816,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1820.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61684,0.12984,0.19882],"tcp_start":[0.62252,0.13117,0.17889],"tcp_to_object_dist_end":0.21061,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.54439,0.05441,0.01602],"object_pos_start":[0.54439,0.05441,0.01602],"object_to_goal_dist_end":0.22816,"object_to_goal_dist_start":0.22816,"object_z_max":0.01602,"peak_contact_force":0.12262,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2332.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.61375,0.12907,0.23633],"tcp_start":[0.61684,0.12984,0.19882],"tcp_to_object_dist_end":0.24273,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.70866,"average_solve_count":127.0,"average_success_count":127.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_grasp.approach_speed":0.24495,"descend_to_grasp.descend_depth":0.00497,"lift_clear.lift_height":0.11168,"place_descend.place_depth":0.00628},"optimized_scores":{"best_composite_score":0.28697,"best_fitness_score":0.66697,"best_task_score":0.3814},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2520.0,"contact_point_centroid":[0.5359,0.08838,-0.0023],"force_p95":0.13262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.33897,"mean_force":0.13886,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.54164,0.0851,0.15223]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.52737,0.02852,-0.00121],"force_p95":0.45902,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64284,"mean_force":0.09138,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.51425,0.0293,0.03104]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8825.0,"contact_point_centroid":[0.51504,0.01034,0.07478],"force_p95":0.10977,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32724,"mean_force":0.07256,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.51166,0.02913,0.07286]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9161.0,"contact_point_centroid":[0.51515,0.04791,0.07374],"force_p95":0.10622,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32567,"mean_force":0.07101,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.5117,0.02913,0.07194]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2884.0,"contact_point_centroid":[0.52241,0.06333,0.12976],"force_p95":0.15945,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24758,"mean_force":0.10226,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.51815,0.04528,0.13253]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2504.0,"contact_point_centroid":[0.52233,0.02548,0.12984],"force_p95":0.18194,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24335,"mean_force":0.10905,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.51735,0.04364,0.13194]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03051,-0.00213],"force_p95":0.15992,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23885,"mean_force":0.13247,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51713,0.0295,0.0306]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4064.0,"contact_point_centroid":[0.51699,0.01022,0.03197],"force_p95":0.08063,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14555,"mean_force":0.05191,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51592,0.02942,0.02924]},{"body_a":"world","body_b":"grasp_target","contact_count":2300.0,"contact_point_centroid":[0.5305,0.03079,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_grasp","phase_type":"approach","tcp_position_centroid":[0.51098,0.01417,0.19292]},{"body_a":"world","body_b":"grasp_target","contact_count":664.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52318,0.02924,0.0629]},{"body_a":"world","body_b":"grasp_target","contact_count":2512.0,"contact_point_centroid":[0.53588,0.08848,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57567,0.14379,0.1302]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53588,0.08848,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59007,0.17287,0.10917]},{"body_a":"world","body_b":"grasp_target","contact_count":1820.0,"contact_point_centroid":[0.53588,0.08848,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.58453,0.17111,0.14726]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4996.0,"contact_point_centroid":[0.5169,0.04857,0.03102],"force_p95":0.07323,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08654,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51592,0.02942,0.02924]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2380.0,"contact_point_centroid":[0.54367,0.0876,0.15575],"force_p95":0.01135,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0184,"mean_force":0.0106,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.54315,0.08759,0.15351]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2682.0,"contact_point_centroid":[0.57626,0.14393,0.13241],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01277,"mean_force":0.01044,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57574,0.14391,0.13011]}],"total_contact_groups":17},"final_pose_error":0.01264,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.53588,0.08848,0.01602],"final_tcp_position":[0.58427,0.17102,0.16694],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":28.86901,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":576.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":28.86901,"phase_name":"approach_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":664.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.52411,0.02864,0.08733],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06168,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":166.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15206,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10860.0,"raw_peak_contact_force":0.23885,"subtask_id":"reach_grasp","tcp_end":[0.52433,0.02997,0.03879],"tcp_start":[0.52411,0.02864,0.08733],"tcp_to_object_dist_end":0.0142,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5304,0.02946,0.02558],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18468,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.1107,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":18132.0,"raw_peak_contact_force":0.64284,"tcp_end":[0.51589,0.02941,0.0292],"tcp_start":[0.52433,0.02997,0.03879],"tcp_to_object_dist_end":0.01496,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.52767,0.02929,0.11455],"object_pos_start":[0.5304,0.02946,0.02558],"object_to_goal_dist_end":0.16669,"object_to_goal_dist_start":0.18468,"object_z_max":0.11445,"peak_contact_force":0.12263,"phase_name":"lift_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10288.0,"raw_peak_contact_force":1.33897,"tcp_end":[0.51174,0.02915,0.12866],"tcp_start":[0.51589,0.02941,0.0292],"tcp_to_object_dist_end":0.02128,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53588,0.08848,0.01602],"object_pos_start":[0.52767,0.02929,0.11455],"object_to_goal_dist_end":0.14459,"object_to_goal_dist_start":0.16669,"object_z_max":0.11459,"peak_contact_force":0.12263,"phase_name":"transport_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5194.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.55449,0.10621,0.16314],"tcp_start":[0.51174,0.02915,0.12866],"tcp_to_object_dist_end":0.14935,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":628.0,"n_steps_budget":1000.0,"object_pos_end":[0.53588,0.08848,0.01602],"object_pos_start":[0.53588,0.08848,0.01602],"object_to_goal_dist_end":0.14459,"object_to_goal_dist_start":0.14459,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.59499,0.17431,0.10816],"tcp_start":[0.55449,0.10621,0.16314],"tcp_to_object_dist_end":0.13911,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53588,0.08848,0.01602],"object_pos_start":[0.53588,0.08848,0.01602],"object_to_goal_dist_end":0.14459,"object_to_goal_dist_start":0.14459,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1820.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58813,0.17223,0.12891],"tcp_start":[0.59499,0.17431,0.10816],"tcp_to_object_dist_end":0.14996,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.53588,0.08848,0.01602],"object_pos_start":[0.53588,0.08848,0.01602],"object_to_goal_dist_end":0.14459,"object_to_goal_dist_start":0.14459,"object_z_max":0.01602,"peak_contact_force":0.12262,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2300.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.58427,0.17102,0.16694],"tcp_start":[0.58813,0.17223,0.12891],"tcp_to_object_dist_end":0.17869,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```