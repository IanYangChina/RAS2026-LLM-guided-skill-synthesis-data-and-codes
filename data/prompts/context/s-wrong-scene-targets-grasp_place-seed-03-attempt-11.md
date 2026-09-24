## Search State

- **Seed**: 3
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0005 | 0.24 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1214 | 0.38 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2110 | 0.32 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2140 | 0.33 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2083 | 0.32 | ✅ accepted |

**Proposal policy**: task_score is 0.24 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.6301274465206397, 0.20821620360643678, 0.11411929633605987]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5, 0.0, 0.3)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.6301274465206397, 0.20821620360643678, 0.11411929633605987)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.45856491671436245, -0.02631894934039003, 0.03)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.45856491671436245, -0.02631894934039003, 0.03]
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
  frozen_object_starts: {'grasp_target': [0.6301274465206397, 0.20821620360643678, 0.11411929633605987]}
  frozen_targets: {'place_target': [0.5, 0.0, 0.3]}
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
| `object` | offset from object initial position (0.6301274465206397, 0.20821620360643678, 0.11411929633605987) | approach/contact targets near object start |
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

## Current Skill (Q=0.000) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.3
- id: place_at_goal
  target_entity: object
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
    - 0.12
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: descend_grasp
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
    - 0.03
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    descend_z_offset:
      type: scalar
      range:
      - 0.02
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: contact_guard
    when: during_phase
    predicate: force_below
    threshold: 20.0
    on_failure: abort
- id: grasp_close
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
  guards:
  - id: bilateral_grasp_guard
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
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
    - 0.2
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: object_lift_guard
    when: after_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.02
- id: approach_place
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
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_place_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_place_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 20.0
    on_failure: abort
  subtask_id: place_at_goal
- id: lower_to_place
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: place_force_limit
    when: during_phase
    predicate: force_below
    threshold: 20.0
    on_failure: abort
- id: release_object
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
- id: retract_after_place
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_z_offset: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=contact_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=20.0
- **grasp_close** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=bilateral_grasp_guard, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=1, strategy=repeat
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=object_lift_guard, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.02]
- **approach_place** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_place_height: status=consumed; consumers=target.offset.z (replace)
    - approach_place_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=abort, threshold=20.0
- **lower_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=place_force_limit, when=during_phase, predicate=force_below, on_failure=abort, threshold=20.0
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract_after_place** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.000
- **task_score** (E): 0.236
- **fitness_score**: 0.580  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1072 |
| descend_grasp | 1.00 | 1.00 | 0.1461 |
| grasp_close | 1.00 | 1.00 | 0.0121 |
| lift_object | 1.00 | 1.00 | 0.1651 |
| approach_place | 0.00 | 1.00 | 0.1103 |
| lower_to_place | 0.00 | 1.00 | 0.0002 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.201) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.506, 0.002, 0.201)→(0.506, 0.002, 0.055) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_close | grasp | 1.00 / step_budget | (0.506, 0.002, 0.055)→(0.498, 0.002, 0.046) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 44.333 | 0.140 | 0.181 |
| lift_object | lift | 1.00 / step_budget | (0.498, 0.002, 0.046)→(0.495, 0.002, 0.211) | (0.511, 0.002, 0.026)→(0.509, 0.001, 0.184) | 0.246→0.224 | 1.00 / 22.667 | 524.446 | 0.422 |
| approach_place | approach | 0.00 / step_budget | (0.495, 0.002, 0.211)→(0.477, 0.055, 0.193) | (0.509, 0.001, 0.184)→(0.516, 0.035, 0.019) | 0.224→0.227 | 1.00 / 10.667 | 147442.615 | 1199.919 |
| lower_to_place | descend | 0.00 / guard_failure | (0.477, 0.055, 0.193)→(0.477, 0.055, 0.193) | (0.516, 0.035, 0.019)→(0.516, 0.035, 0.019) | 0.227→0.227 | 1.00 / 10.333 | 606.202 | 226.323 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.345
- phase_score: 0.140
- phase_breakdown.place_at_goal_score: 0.043
- phase_breakdown.reach_object_score: 0.367
- grasp_place_fitness: 0.636

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.636
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.345
- **Median Q (composite search score)**: -0.004
- **K-run variance**: 0.0019
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: descend_grasp.descend_z_offset
- **Final σ (mean)**: 0.322


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
{"anchors":[{"name":"object","value":[0.63013,0.20822,0.11412]},{"name":"goal","value":[0.45856,-0.02632,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73737,"average_solve_count":198.0,"average_success_count":198.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.13417,"approach_place.approach_place_height":0.1707,"approach_place.approach_place_speed":0.0768,"descend_grasp.descend_speed":0.02562,"descend_grasp.descend_z_offset":0.02186,"lift_object.lift_height":0.19861,"lower_to_place.descend_place_speed":0.03525,"lower_to_place.place_z_offset":0.00796},"optimized_scores":{"best_composite_score":-0.05071,"best_fitness_score":0.52929,"best_task_score":0.13902},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":32.0,"contact_point_centroid":[0.50873,-0.00578,-0.00305],"force_p95":1146.32473,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1381.59341,"mean_force":147.28434,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.37449,-0.01306,0.03486]},{"body_a":"world","body_b":"link6","contact_count":891.0,"contact_point_centroid":[0.6303,0.01669,-0.00033],"force_p95":230.50391,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":727.45918,"mean_force":214.81996,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.39125,-0.0036,0.11294]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.61879,0.03821,-0.00018],"force_p95":220.9931,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":220.9931,"mean_force":220.9931,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.4065,0.0151,0.16992]},{"body_a":"grasp_target","body_b":"hand","contact_count":469.0,"contact_point_centroid":[0.47893,-0.00954,0.04418],"force_p95":0.82543,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.66797,"mean_force":0.35281,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.38516,-0.01009,0.0885]},{"body_a":"world","body_b":"grasp_target","contact_count":3672.0,"contact_point_centroid":[0.44918,-0.00878,-0.00308],"force_p95":0.31699,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.76764,"mean_force":0.18291,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.39177,-0.00382,0.11135]},{"body_a":"grasp_target","body_b":"link7","contact_count":269.0,"contact_point_centroid":[0.4833,-0.01461,0.03985],"force_p95":0.39358,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.34124,"mean_force":0.14114,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.38268,-0.01131,0.07985]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":709.0,"contact_point_centroid":[0.47994,-0.03925,0.20138],"force_p95":0.36454,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.51282,"mean_force":0.18976,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.4733,-0.02214,0.20455]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":464.0,"contact_point_centroid":[0.47351,-0.00491,0.2208],"force_p95":0.31412,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42004,"mean_force":0.16995,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.4684,-0.02374,0.2246]},{"body_a":"world","body_b":"grasp_target","contact_count":71.0,"contact_point_centroid":[0.45618,-0.02536,-0.00138],"force_p95":0.36504,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38366,"mean_force":0.09006,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44596,-0.02553,0.05084]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8660.0,"contact_point_centroid":[0.44636,-0.0442,0.12682],"force_p95":0.10994,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25913,"mean_force":0.06718,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44387,-0.02543,0.12657]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8021.0,"contact_point_centroid":[0.44644,-0.0065,0.12853],"force_p95":0.13456,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25807,"mean_force":0.07386,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44387,-0.02543,0.12862]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02629,-0.00206],"force_p95":0.14163,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18889,"mean_force":0.12754,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.44816,-0.02562,0.05051]},{"body_a":"world","body_b":"grasp_target","contact_count":1572.0,"contact_point_centroid":[0.45856,-0.02632,-0.00191],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12294,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47961,-0.0113,0.23734]},{"body_a":"world","body_b":"grasp_target","contact_count":1716.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.45569,-0.02456,0.11503]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.44915,-0.00878,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.4065,0.0151,0.16992]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4838.0,"contact_point_centroid":[0.44659,-0.00633,0.04953],"force_p95":0.06837,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10274,"mean_force":0.04513,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.44711,-0.02558,0.04949]}],"total_contact_groups":19},"final_pose_error":0.29932,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.44915,-0.00878,0.02602],"final_tcp_position":[0.40654,0.0151,0.1701],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273001.30425,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":394.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1572.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.45961,-0.02344,0.1736],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14761,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":429.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1716.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45449,-0.02585,0.05675],"tcp_start":[0.45961,-0.02344,0.1736],"tcp_to_object_dist_end":0.031,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4585,-0.02583,0.02576],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30338,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14067,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12034.0,"raw_peak_contact_force":0.18889,"tcp_end":[0.44708,-0.02557,0.04946],"tcp_start":[0.45449,-0.02585,0.05675],"tcp_to_object_dist_end":0.02631,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":538.0,"n_steps_budget":1000.0,"object_pos_end":[0.45621,-0.02658,0.19763],"object_pos_start":[0.4585,-0.02583,0.02576],"object_to_goal_dist_end":0.3039,"object_to_goal_dist_start":0.30338,"object_z_max":0.19735,"peak_contact_force":0.13734,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16752.0,"raw_peak_contact_force":0.38366,"tcp_end":[0.44421,-0.02543,0.22852],"tcp_start":[0.44708,-0.02557,0.04946],"tcp_to_object_dist_end":0.03315,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44915,-0.00878,0.02602],"object_pos_start":[0.45621,-0.02658,0.19763],"object_to_goal_dist_end":0.29597,"object_to_goal_dist_start":0.3039,"object_z_max":0.20324,"peak_contact_force":273001.30425,"phase_name":"approach_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9919.0,"raw_peak_contact_force":1381.59341,"subtask_id":"place_at_goal","tcp_end":[0.4065,0.0151,0.16992],"tcp_start":[0.44421,-0.02543,0.22852],"tcp_to_object_dist_end":0.15197,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.44915,-0.00878,0.02602],"object_pos_start":[0.44915,-0.00878,0.02602],"object_to_goal_dist_end":0.29597,"object_to_goal_dist_start":0.29597,"object_z_max":0.02602,"peak_contact_force":220.9931,"phase_name":"lower_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10.0,"raw_peak_contact_force":220.9931,"tcp_end":[0.40654,0.0151,0.1701],"tcp_start":[0.4065,0.0151,0.16992],"tcp_to_object_dist_end":0.15213,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `aa6ec658384c70fac6b4eb656cc8c53536c3d5c760368ab2b384dccf294e2c48`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.64762,0.15808,0.1911]},{"name":"goal","value":[0.54431,0.00113,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88177,"average_solve_count":203.0,"average_success_count":203.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.19671,"approach_place.approach_place_height":0.21967,"approach_place.approach_place_speed":0.07308,"descend_grasp.descend_speed":0.02249,"descend_grasp.descend_z_offset":0.02003,"lift_object.lift_height":0.17936,"lower_to_place.descend_place_speed":0.024,"lower_to_place.place_z_offset":0.00015},"optimized_scores":{"best_composite_score":-0.00409,"best_fitness_score":0.57591,"best_task_score":0.2228},"replay_outcomes":[{"contacts":{"omitted_contact_groups":8,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":80.0,"contact_point_centroid":[0.56954,-0.04539,-0.0025],"force_p95":710.27124,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":971.71694,"mean_force":240.62015,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.51901,0.01063,-0.00393]},{"body_a":"world","body_b":"link6","contact_count":522.0,"contact_point_centroid":[0.64404,0.02711,-0.00016],"force_p95":357.75875,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":393.80528,"mean_force":209.55933,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.50687,0.04822,0.15213]},{"body_a":"world","body_b":"link7","contact_count":409.0,"contact_point_centroid":[0.60786,-0.01363,-0.00021],"force_p95":248.97056,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":342.69555,"mean_force":147.83896,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.47961,0.00515,0.03876]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.55914,0.00137,-0.00021],"force_p95":227.20484,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":227.20484,"mean_force":227.20484,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.57278,0.01586,0.29338]},{"body_a":"world","body_b":"left_finger","contact_count":1367.0,"contact_point_centroid":[0.52253,-0.00319,-0.00558],"force_p95":8.32497,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":40.53647,"mean_force":3.91769,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.51879,0.01051,-0.00373]},{"body_a":"world","body_b":"right_finger","contact_count":1227.0,"contact_point_centroid":[0.5205,0.02524,-0.00593],"force_p95":8.16742,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":39.79005,"mean_force":4.02753,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.51989,0.01075,-0.00501]},{"body_a":"grasp_target","body_b":"hand","contact_count":573.0,"contact_point_centroid":[0.58459,0.00893,0.02806],"force_p95":1.53631,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.30005,"mean_force":0.90319,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.48297,0.00629,0.03735]},{"body_a":"grasp_target","body_b":"link7","contact_count":606.0,"contact_point_centroid":[0.59752,0.02183,0.02059],"force_p95":1.15467,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.55618,"mean_force":0.65267,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.47732,0.00788,0.04873]},{"body_a":"grasp_target","body_b":"link6","contact_count":266.0,"contact_point_centroid":[0.55931,0.03599,0.03473],"force_p95":1.08132,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.40293,"mean_force":0.40901,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.5336,0.08895,0.2231]},{"body_a":"world","body_b":"grasp_target","contact_count":3121.0,"contact_point_centroid":[0.58031,0.02999,-0.00615],"force_p95":0.84483,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.38891,"mean_force":0.41562,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.50383,0.03224,0.10183]},{"body_a":"grasp_target","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.53527,0.02607,0.03644],"force_p95":0.93739,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.93739,"mean_force":0.93739,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.57278,0.01586,0.29338]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":654.0,"contact_point_centroid":[0.57866,-0.01046,0.18221],"force_p95":0.41746,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.86736,"mean_force":0.20461,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.57185,0.00772,0.18447]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":633.0,"contact_point_centroid":[0.5731,0.026,0.18809],"force_p95":0.40184,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.60502,"mean_force":0.18633,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.5681,0.00705,0.19026]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.55396,0.05209,-0.00238],"force_p95":0.49941,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52352,"mean_force":0.23542,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.57278,0.01586,0.29338]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.54169,0.00081,-0.00137],"force_p95":0.41687,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44157,"mean_force":0.09474,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52906,0.00086,0.04544]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7602.0,"contact_point_centroid":[0.53013,-0.01797,0.11619],"force_p95":0.11161,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31499,"mean_force":0.0736,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52657,0.00082,0.11437]}],"total_contact_groups":24},"final_pose_error":0.19067,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.55297,0.05411,0.01517],"final_tcp_position":[0.57275,0.01563,0.29352],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":285.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1136.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53515,0.00093,0.23067],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20486,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":581.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2324.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53883,0.00103,0.05435],"tcp_start":[0.53515,0.00093,0.23067],"tcp_to_object_dist_end":0.02886,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54421,0.00078,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25048,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12992,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10791.0,"raw_peak_contact_force":0.14751,"tcp_end":[0.53034,0.00088,0.04418],"tcp_start":[0.53883,0.00103,0.05435],"tcp_to_object_dist_end":0.02297,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":532.0,"n_steps_budget":1000.0,"object_pos_end":[0.54174,0.00105,0.1786],"object_pos_start":[0.54421,0.00078,0.02588],"object_to_goal_dist_end":0.18981,"object_to_goal_dist_start":0.25048,"object_z_max":0.17834,"peak_contact_force":1573.09317,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15171.0,"raw_peak_contact_force":0.44157,"tcp_end":[0.52695,0.00083,0.20392],"tcp_start":[0.53034,0.00088,0.04418],"tcp_to_object_dist_end":0.02932,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.553,0.05404,0.01511],"object_pos_start":[0.54174,0.00105,0.1786],"object_to_goal_dist_end":0.22528,"object_to_goal_dist_start":0.18981,"object_z_max":0.17975,"peak_contact_force":167951.73011,"phase_name":"approach_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12356.0,"raw_peak_contact_force":971.71694,"subtask_id":"place_at_goal","tcp_end":[0.57278,0.01586,0.29338],"tcp_start":[0.52695,0.00083,0.20392],"tcp_to_object_dist_end":0.28157,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.55297,0.05411,0.01517],"object_pos_start":[0.553,0.05404,0.01511],"object_to_goal_dist_end":0.22522,"object_to_goal_dist_start":0.22528,"object_z_max":0.01511,"peak_contact_force":1366.84211,"phase_name":"lower_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11.0,"raw_peak_contact_force":227.20484,"tcp_end":[0.57275,0.01563,0.29352],"tcp_start":[0.57278,0.01586,0.29338],"tcp_to_object_dist_end":0.2817,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e1209649252ffcf03853fe0727696e22a1eda11729c6c1ae21659980557d7e98`; realized-scene SHA-256: `e32d7866764afb23ec7c7faebb4bcca0aa39fbf2f1ab61f3c9c527b297153af9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.60153,0.17858,0.10809]},{"name":"goal","value":[0.5305,0.03079,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78469,"average_solve_count":209.0,"average_success_count":209.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.16321,"approach_place.approach_place_height":0.24498,"approach_place.approach_place_speed":0.05657,"descend_grasp.descend_speed":0.01803,"descend_grasp.descend_z_offset":0.02,"lift_object.lift_height":0.1758,"lower_to_place.descend_place_speed":0.02765,"lower_to_place.place_z_offset":0.01979},"optimized_scores":{"best_composite_score":0.05623,"best_fitness_score":0.63623,"best_task_score":0.3448},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":352.0,"contact_point_centroid":[0.56476,0.1511,-0.00064],"force_p95":275.31233,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1246.44705,"mean_force":131.89657,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.46552,0.1125,0.06919]},{"body_a":"world","body_b":"link6","contact_count":772.0,"contact_point_centroid":[0.68183,0.03504,-0.00024],"force_p95":266.4798,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":622.73845,"mean_force":211.36584,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.45433,0.11897,0.08712]},{"body_a":"world","body_b":"link7","contact_count":30.0,"contact_point_centroid":[0.59723,0.04431,-0.00016],"force_p95":455.52603,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":461.55645,"mean_force":248.42149,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.46815,0.07559,0.03427]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.6833,0.05172,-5e-05],"force_p95":230.77184,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":230.77184,"mean_force":230.77184,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.45041,0.13393,0.1165]},{"body_a":"world","body_b":"hand","contact_count":1.0,"contact_point_centroid":[0.55042,0.15382,-0.00025],"force_p95":81.68228,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":81.68228,"mean_force":81.68228,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.45041,0.13393,0.1165]},{"body_a":"world","body_b":"right_finger","contact_count":893.0,"contact_point_centroid":[0.51626,0.06863,-0.00477],"force_p95":8.93249,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":50.23515,"mean_force":4.1794,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.5102,0.05656,-0.00381]},{"body_a":"world","body_b":"left_finger","contact_count":842.0,"contact_point_centroid":[0.50937,0.04233,-0.00435],"force_p95":7.61495,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":38.07058,"mean_force":3.92996,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.51028,0.05644,-0.00431]},{"body_a":"grasp_target","body_b":"hand","contact_count":388.0,"contact_point_centroid":[0.56144,0.0595,0.03206],"force_p95":1.54037,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.60917,"mean_force":0.79425,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.46921,0.09088,0.04645]},{"body_a":"world","body_b":"grasp_target","contact_count":3167.0,"contact_point_centroid":[0.55818,0.05706,-0.00539],"force_p95":1.0529,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.46584,"mean_force":0.34635,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.46144,0.11423,0.0804]},{"body_a":"grasp_target","body_b":"link7","contact_count":908.0,"contact_point_centroid":[0.56986,0.06544,0.02611],"force_p95":1.21789,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.90649,"mean_force":0.47175,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.45914,0.11267,0.07811]},{"body_a":"grasp_target","body_b":"link6","contact_count":383.0,"contact_point_centroid":[0.58766,0.04657,0.02389],"force_p95":0.35929,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.50287,"mean_force":0.20097,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.45627,0.12644,0.08876]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":522.0,"contact_point_centroid":[0.55307,0.01272,0.1904],"force_p95":0.40116,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.56833,"mean_force":0.19677,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.54971,0.03214,0.19191]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":722.0,"contact_point_centroid":[0.56182,0.05033,0.18765],"force_p95":0.37866,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.50358,"mean_force":0.18789,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.55312,0.03294,0.18798]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.5281,0.02942,-0.00142],"force_p95":0.4124,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43987,"mean_force":0.09326,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5156,0.0295,0.04618]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8556.0,"contact_point_centroid":[0.51654,0.0482,0.11588],"force_p95":0.10323,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29826,"mean_force":0.06527,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5132,0.02934,0.11351]},{"body_a":"grasp_target","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.55941,0.07595,0.03645],"force_p95":0.28763,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28763,"mean_force":0.28763,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.45041,0.13393,0.1165]}],"total_contact_groups":25},"final_pose_error":0.15781,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.5473,0.06013,0.01569],"final_tcp_position":[0.45052,0.13417,0.11663],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1374.81158,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":355.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1416.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52367,0.02707,0.1995],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17365,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":500.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52519,0.03014,0.05443],"tcp_start":[0.52367,0.02707,0.1995],"tcp_to_object_dist_end":0.02891,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53045,0.02997,0.02563],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18422,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14798,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12030.0,"raw_peak_contact_force":0.20799,"tcp_end":[0.51689,0.02959,0.04475],"tcp_start":[0.52519,0.03014,0.05443],"tcp_to_object_dist_end":0.02344,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":514.0,"n_steps_budget":1000.0,"object_pos_end":[0.529,0.02989,0.17571],"object_pos_start":[0.53045,0.02997,0.02563],"object_to_goal_dist_end":0.17872,"object_to_goal_dist_start":0.18422,"object_z_max":0.17545,"peak_contact_force":0.10775,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16095.0,"raw_peak_contact_force":0.43987,"tcp_end":[0.51352,0.02936,0.20108],"tcp_start":[0.51689,0.02959,0.04475],"tcp_to_object_dist_end":0.02973,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54731,0.06011,0.01568],"object_pos_start":[0.529,0.02989,0.17571],"object_to_goal_dist_end":0.15973,"object_to_goal_dist_start":0.17872,"object_z_max":0.1766,"peak_contact_force":1374.81158,"phase_name":"approach_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12067.0,"raw_peak_contact_force":1246.44705,"subtask_id":"place_at_goal","tcp_end":[0.45041,0.13393,0.1165],"tcp_start":[0.51352,0.02936,0.20108],"tcp_to_object_dist_end":0.15813,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.5473,0.06013,0.01569],"object_pos_start":[0.54731,0.06011,0.01568],"object_to_goal_dist_end":0.15972,"object_to_goal_dist_start":0.15973,"object_z_max":0.01568,"peak_contact_force":230.77184,"phase_name":"lower_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11.0,"raw_peak_contact_force":230.77184,"tcp_end":[0.45052,0.13417,0.11663],"tcp_start":[0.45041,0.13393,0.1165],"tcp_to_object_dist_end":0.15823,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```