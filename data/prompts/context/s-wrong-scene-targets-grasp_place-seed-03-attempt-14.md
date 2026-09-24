## Search State

- **Seed**: 3
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1055 | 0.34 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0250 | 0.29 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | 0.0616 | 0.21 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0005 | 0.24 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1214 | 0.38 | ✅ accepted |

**Proposal policy**: task_score is 0.34 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.105) — your mutation base

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

- **Composite score**: 0.105
- **task_score** (E): 0.345
- **fitness_score**: 0.635  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.530

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1253 |
| descend_grasp | 1.00 | 1.00 | 0.1279 |
| grasp_close | 1.00 | 1.00 | 0.0121 |
| lift_object | 1.00 | 1.00 | 0.1302 |
| approach_place | 0.00 | 1.00 | 0.0797 |
| lower_to_place | 0.67 | 1.00 | 0.1393 |
| release_object | 1.00 | 1.00 | 0.0214 |
| retract_after_place | 1.00 | 1.00 | 0.0852 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, 0.002, 0.183) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.508, 0.002, 0.183)→(0.506, 0.002, 0.055) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_close | grasp | 1.00 / step_budget | (0.506, 0.002, 0.055)→(0.498, 0.002, 0.046) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 45.667 | 0.140 | 0.185 |
| lift_object | lift | 1.00 / step_budget | (0.498, 0.002, 0.046)→(0.495, 0.002, 0.176) | (0.511, 0.002, 0.026)→(0.510, 0.002, 0.151) | 0.246→0.216 | 1.00 / 24.667 | 0.107 | 0.426 |
| approach_place | approach | 0.00 / step_budget | (0.495, 0.002, 0.176)→(0.533, 0.059, 0.215) | (0.510, 0.002, 0.151)→(0.536, 0.053, 0.115) | 0.216→0.189 | 1.00 / 16.000 | 0.123 | 0.691 |
| lower_to_place | descend | 0.67 / step_budget | (0.533, 0.059, 0.215)→(0.605, 0.158, 0.150) | (0.536, 0.053, 0.115)→(0.569, 0.090, 0.016) | 0.189→0.172 | 1.00 / 8.000 | 3249.710 | 1.008 |
| release_object | release | 1.00 / step_budget | (0.605, 0.158, 0.150)→(0.598, 0.157, 0.171) | (0.569, 0.090, 0.016)→(0.569, 0.090, 0.016) | 0.172→0.172 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_after_place | retract | 1.00 / step_budget | (0.598, 0.157, 0.171)→(0.596, 0.156, 0.256) | (0.569, 0.090, 0.016)→(0.569, 0.090, 0.016) | 0.172→0.172 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.536
- phase_score: 0.304
- phase_breakdown.place_at_goal_score: 0.067
- phase_breakdown.reach_object_score: 0.855
- grasp_place_fitness: 0.732

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.732
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.536
- **Median Q (composite search score)**: 0.078
- **K-run variance**: 0.0049
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.341


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40708,"average_solve_count":226.0,"average_success_count":226.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.19291,"approach_place.approach_place_height":0.19618,"approach_place.approach_place_speed":0.03957,"descend_grasp.descend_speed":0.04982,"descend_grasp.descend_z_offset":0.02021,"lift_object.lift_height":0.15539,"lower_to_place.place_z_offset":0.01005},"optimized_scores":{"best_composite_score":0.07806,"best_fitness_score":0.60806,"best_task_score":0.29239},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3156.0,"contact_point_centroid":[0.54111,0.07975,-0.00235],"force_p95":0.12691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.66755,"mean_force":0.13928,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.55784,0.12345,0.16816]},{"body_a":"world","body_b":"grasp_target","contact_count":71.0,"contact_point_centroid":[0.45614,-0.02534,-0.00139],"force_p95":0.38914,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40739,"mean_force":0.10164,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44622,-0.02553,0.04927]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7228.0,"contact_point_centroid":[0.44568,-0.0444,0.10844],"force_p95":0.10361,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25842,"mean_force":0.06226,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44407,-0.02542,0.10759]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6570.0,"contact_point_centroid":[0.44582,-0.00639,0.1087],"force_p95":0.10821,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25771,"mean_force":0.06731,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44407,-0.02542,0.10796]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1120.0,"contact_point_centroid":[0.51349,0.04223,0.20614],"force_p95":0.12602,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23489,"mean_force":0.09515,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.50756,0.0601,0.21048]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":943.0,"contact_point_centroid":[0.51322,0.07765,0.20625],"force_p95":0.15518,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21158,"mean_force":0.11545,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.50708,0.05941,0.21105]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02628,-0.00206],"force_p95":0.14181,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18959,"mean_force":0.12763,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.44842,-0.02561,0.04899]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10865.0,"contact_point_centroid":[0.47701,-0.00518,0.19846],"force_p95":0.11746,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17331,"mean_force":0.08378,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.47166,0.01311,0.1999]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9810.0,"contact_point_centroid":[0.47614,0.03036,0.19796],"force_p95":0.13484,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16469,"mean_force":0.09231,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.47069,0.01186,0.19927]},{"body_a":"world","body_b":"grasp_target","contact_count":960.0,"contact_point_centroid":[0.45856,-0.02632,-0.00186],"force_p95":0.13692,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12314,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48152,-0.01033,0.26596]},{"body_a":"world","body_b":"grasp_target","contact_count":2440.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.45748,-0.0238,0.14223]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54113,0.07985,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58453,0.16058,0.14496]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.54113,0.07985,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.5797,0.15911,0.20562]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4837.0,"contact_point_centroid":[0.44684,-0.00632,0.04821],"force_p95":0.06881,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10365,"mean_force":0.0451,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.44737,-0.02557,0.04796]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5397.0,"contact_point_centroid":[0.44668,-0.04478,0.04859],"force_p95":0.06515,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08208,"mean_force":0.0409,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.44737,-0.02557,0.04796]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3123.0,"contact_point_centroid":[0.56066,0.12649,0.16844],"force_p95":0.01123,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01642,"mean_force":0.01058,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.56031,0.12649,0.16624]}],"total_contact_groups":17},"final_pose_error":0.01481,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.54113,0.07985,0.01602],"final_tcp_position":[0.57991,0.15913,0.25031],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.66755,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":241.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":960.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.46264,-0.02189,0.23083],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20489,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":610.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2440.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45477,-0.02584,0.05523],"tcp_start":[0.46264,-0.02189,0.23083],"tcp_to_object_dist_end":0.02946,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4585,-0.02581,0.02575],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30337,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.1407,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12034.0,"raw_peak_contact_force":0.18959,"tcp_end":[0.44734,-0.02557,0.04793],"tcp_start":[0.45477,-0.02584,0.05523],"tcp_to_object_dist_end":0.02483,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":408.0,"n_steps_budget":990.0,"object_pos_end":[0.45837,-0.02568,0.15744],"object_pos_start":[0.4585,-0.02581,0.02575],"object_to_goal_dist_end":0.2934,"object_to_goal_dist_start":0.30337,"object_z_max":0.15716,"peak_contact_force":0.10573,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13869.0,"raw_peak_contact_force":0.40739,"tcp_end":[0.44415,-0.02541,0.1838],"tcp_start":[0.44734,-0.02557,0.04793],"tcp_to_object_dist_end":0.02994,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50765,0.05079,0.1829],"object_pos_start":[0.45837,-0.02568,0.15744],"object_to_goal_dist_end":0.21099,"object_to_goal_dist_start":0.2934,"object_z_max":0.18287,"peak_contact_force":0.11447,"phase_name":"approach_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20675.0,"raw_peak_contact_force":0.17331,"subtask_id":"place_at_goal","tcp_end":[0.50197,0.05112,0.21964],"tcp_start":[0.44415,-0.02541,0.1838],"tcp_to_object_dist_end":0.03718,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54113,0.07985,0.01602],"object_pos_start":[0.50765,0.05079,0.1829],"object_to_goal_dist_end":0.18445,"object_to_goal_dist_start":0.21099,"object_z_max":0.1829,"peak_contact_force":0.12263,"phase_name":"lower_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8342.0,"raw_peak_contact_force":1.66755,"tcp_end":[0.589,0.1618,0.14374],"tcp_start":[0.50197,0.05112,0.21964],"tcp_to_object_dist_end":0.15912,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54113,0.07985,0.01602],"object_pos_start":[0.54113,0.07985,0.01602],"object_to_goal_dist_end":0.18445,"object_to_goal_dist_start":0.18445,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58279,0.16004,0.1648],"tcp_start":[0.589,0.1618,0.14374],"tcp_to_object_dist_end":0.17408,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.54113,0.07985,0.01602],"object_pos_start":[0.54113,0.07985,0.01602],"object_to_goal_dist_end":0.18445,"object_to_goal_dist_start":0.18445,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57991,0.15913,0.25031],"tcp_start":[0.58279,0.16004,0.1648],"tcp_to_object_dist_end":0.25036,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48325,"average_solve_count":209.0,"average_success_count":209.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.12765,"approach_place.approach_place_height":0.19183,"approach_place.approach_place_speed":0.02738,"descend_grasp.descend_speed":0.0426,"descend_grasp.descend_z_offset":0.02109,"lift_object.lift_height":0.17947,"lower_to_place.place_z_offset":0.01066},"optimized_scores":{"best_composite_score":0.03674,"best_fitness_score":0.56674,"best_task_score":0.20678},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3008.0,"contact_point_centroid":[0.55613,0.02821,-0.00235],"force_p95":0.12564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.74521,"mean_force":0.13794,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.54595,0.0298,0.23132]},{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.54197,0.00073,-0.00136],"force_p95":0.40784,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4297,"mean_force":0.09305,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5289,0.00085,0.04636]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7682.0,"contact_point_centroid":[0.52988,-0.01816,0.11506],"force_p95":0.11203,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28828,"mean_force":0.07307,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52643,0.00081,0.11318]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8764.0,"contact_point_centroid":[0.53022,0.01963,0.11991],"force_p95":0.09853,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28721,"mean_force":0.06555,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52642,0.00081,0.11756]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1441.0,"contact_point_centroid":[0.53541,-0.01267,0.20762],"force_p95":0.17385,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27109,"mean_force":0.10183,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.52879,0.00609,0.20717]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2057.0,"contact_point_centroid":[0.53557,0.02465,0.20783],"force_p95":0.10059,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.161,"mean_force":0.0727,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.52902,0.00654,0.20748]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00109,-0.00203],"force_p95":0.13167,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15322,"mean_force":0.12538,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.53143,0.0009,0.04654]},{"body_a":"world","body_b":"grasp_target","contact_count":1856.0,"contact_point_centroid":[0.54431,0.00113,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51711,0.00048,0.23133]},{"body_a":"world","body_b":"grasp_target","contact_count":1444.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53622,0.00099,0.10912]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.55613,0.02822,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.59728,0.09806,0.21779]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55613,0.02822,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62583,0.13813,0.20027]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.55613,0.02822,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.62191,0.13703,0.25957]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4836.0,"contact_point_centroid":[0.53125,-0.01834,0.04772],"force_p95":0.06718,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10459,"mean_force":0.04501,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.53022,0.00088,0.0451]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5121.0,"contact_point_centroid":[0.53096,0.02008,0.04731],"force_p95":0.06543,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08588,"mean_force":0.04291,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.53022,0.00088,0.0451]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2984.0,"contact_point_centroid":[0.54705,0.03083,0.23471],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01573,"mean_force":0.01052,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.54675,0.03083,0.23248]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4287.0,"contact_point_centroid":[0.59767,0.09792,0.22015],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01295,"mean_force":0.01041,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.59716,0.09791,0.21785]}],"total_contact_groups":17},"final_pose_error":0.01556,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.55613,0.02822,0.01602],"final_tcp_position":[0.62226,0.13706,0.3042],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.74521,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":465.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1856.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53673,0.00098,0.16391],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1381,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":361.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1444.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53863,0.00103,0.05522],"tcp_start":[0.53673,0.00098,0.16391],"tcp_to_object_dist_end":0.02975,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54422,0.00093,0.02586],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25039,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13103,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11757.0,"raw_peak_contact_force":0.15322,"tcp_end":[0.53019,0.00088,0.04507],"tcp_start":[0.53863,0.00103,0.05522],"tcp_to_object_dist_end":0.02378,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":532.0,"n_steps_budget":1000.0,"object_pos_end":[0.54227,0.00106,0.17918],"object_pos_start":[0.54422,0.00093,0.02586],"object_to_goal_dist_end":0.18947,"object_to_goal_dist_start":0.25039,"object_z_max":0.17892,"peak_contact_force":0.10683,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16523.0,"raw_peak_contact_force":0.4297,"tcp_end":[0.52681,0.00082,0.2049],"tcp_start":[0.53019,0.00088,0.04507],"tcp_to_object_dist_end":0.03001,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55613,0.02822,0.01602],"object_pos_start":[0.54227,0.00106,0.17918],"object_to_goal_dist_end":0.23641,"object_to_goal_dist_start":0.18947,"object_z_max":0.1816,"peak_contact_force":0.12263,"phase_name":"approach_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9490.0,"raw_peak_contact_force":1.74521,"subtask_id":"place_at_goal","tcp_end":[0.55699,0.04389,0.24708],"tcp_start":[0.52681,0.00082,0.2049],"tcp_to_object_dist_end":0.23159,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55613,0.02822,0.01602],"object_pos_start":[0.55613,0.02822,0.01602],"object_to_goal_dist_end":0.23641,"object_to_goal_dist_start":0.23641,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lower_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8287.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62965,0.13902,0.20011],"tcp_start":[0.55699,0.04389,0.24708],"tcp_to_object_dist_end":0.2271,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55613,0.02822,0.01602],"object_pos_start":[0.55613,0.02822,0.01602],"object_to_goal_dist_end":0.23641,"object_to_goal_dist_start":0.23641,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62439,0.13771,0.21959],"tcp_start":[0.62965,0.13902,0.20011],"tcp_to_object_dist_end":0.24102,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.55613,0.02822,0.01602],"object_pos_start":[0.55613,0.02822,0.01602],"object_to_goal_dist_end":0.23641,"object_to_goal_dist_start":0.23641,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62226,0.13706,0.3042],"tcp_start":[0.62439,0.13771,0.21959],"tcp_to_object_dist_end":0.31507,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.2807,"average_solve_count":228.0,"average_success_count":228.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.11654,"approach_place.approach_place_height":0.16032,"approach_place.approach_place_speed":0.03278,"descend_grasp.descend_speed":0.02862,"descend_grasp.descend_z_offset":0.02004,"lift_object.lift_height":0.11415,"lower_to_place.place_z_offset":0.00574},"optimized_scores":{"best_composite_score":0.20157,"best_fitness_score":0.73157,"best_task_score":0.53564},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":667.0,"contact_point_centroid":[0.60776,0.16363,-0.00287],"force_p95":0.56291,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.23436,"mean_force":0.17097,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.59083,0.16743,0.11224]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.5281,0.02944,-0.00141],"force_p95":0.41544,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4419,"mean_force":0.09162,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51543,0.02947,0.04613]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5211.0,"contact_point_centroid":[0.56731,0.10262,0.1407],"force_p95":0.13748,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3039,"mean_force":0.10656,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.56191,0.12081,0.1443]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5606.0,"contact_point_centroid":[0.51512,0.04832,0.08748],"force_p95":0.10365,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29928,"mean_force":0.06163,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51306,0.02931,0.08518]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5105.0,"contact_point_centroid":[0.51526,0.01028,0.08712],"force_p95":0.10974,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28555,"mean_force":0.06584,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51306,0.02931,0.08499]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5756.0,"contact_point_centroid":[0.56682,0.13755,0.14178],"force_p95":0.12805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25402,"mean_force":0.09844,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.56116,0.11952,0.14528]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53054,0.0307,-0.00211],"force_p95":0.15229,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.213,"mean_force":0.13071,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.51796,0.02965,0.04608]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12048.0,"contact_point_centroid":[0.53133,0.03879,0.15842],"force_p95":0.11098,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15377,"mean_force":0.07765,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.52606,0.05749,0.1582]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12742.0,"contact_point_centroid":[0.53117,0.07571,0.15854],"force_p95":0.09597,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15159,"mean_force":0.07327,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.52587,0.05711,0.15793]},{"body_a":"world","body_b":"grasp_target","contact_count":1944.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51091,0.01372,0.2263]},{"body_a":"world","body_b":"grasp_target","contact_count":1376.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52313,0.02893,0.10375]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.60903,0.16321,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59012,0.17287,0.10857]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.60903,0.16321,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.5847,0.17113,0.16897]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4793.0,"contact_point_centroid":[0.51778,0.01033,0.0473],"force_p95":0.07106,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11179,"mean_force":0.04534,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.51677,0.02957,0.04471]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5460.0,"contact_point_centroid":[0.51696,0.04881,0.04735],"force_p95":0.06797,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07007,"mean_force":0.04076,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.51677,0.02957,0.04472]},{"body_a":"left_finger","body_b":"right_finger","contact_count":326.0,"contact_point_centroid":[0.59386,0.17144,0.11169],"force_p95":0.01437,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01574,"mean_force":0.01123,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.59332,0.17142,0.10954]}],"total_contact_groups":17},"final_pose_error":0.01508,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.60903,0.16321,0.01602],"final_tcp_position":[0.58488,0.17115,0.21364],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":9748.88392,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":487.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1944.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52418,0.02797,0.1536],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12777,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":344.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1376.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.525,0.03011,0.05434],"tcp_start":[0.52418,0.02797,0.1536],"tcp_to_object_dist_end":0.02886,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53045,0.02997,0.0256],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18423,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14938,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12053.0,"raw_peak_contact_force":0.213,"tcp_end":[0.51674,0.02957,0.04468],"tcp_start":[0.525,0.03011,0.05434],"tcp_to_object_dist_end":0.02349,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":311.0,"n_steps_budget":720.0,"object_pos_end":[0.52844,0.02954,0.11664],"object_pos_start":[0.53045,0.02997,0.0256],"object_to_goal_dist_end":0.16621,"object_to_goal_dist_start":0.18423,"object_z_max":0.11638,"peak_contact_force":0.10926,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10791.0,"raw_peak_contact_force":0.4419,"tcp_end":[0.51284,0.0293,0.13932],"tcp_start":[0.51674,0.02957,0.04468],"tcp_to_object_dist_end":0.02752,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54542,0.08098,0.14582],"object_pos_start":[0.52844,0.02954,0.11664],"object_to_goal_dist_end":0.11874,"object_to_goal_dist_start":0.16621,"object_z_max":0.1458,"peak_contact_force":0.13238,"phase_name":"approach_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24790.0,"raw_peak_contact_force":0.15377,"subtask_id":"place_at_goal","tcp_end":[0.5398,0.08057,0.1776],"tcp_start":[0.51284,0.0293,0.13932],"tcp_to_object_dist_end":0.03228,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":844.0,"n_steps_budget":1000.0,"object_pos_end":[0.60903,0.16321,0.01601],"object_pos_start":[0.54542,0.08098,0.14582],"object_to_goal_dist_end":0.09365,"object_to_goal_dist_start":0.11874,"object_z_max":0.14582,"peak_contact_force":9748.88392,"phase_name":"lower_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11960.0,"raw_peak_contact_force":1.23436,"tcp_end":[0.59504,0.17431,0.10755],"tcp_start":[0.5398,0.08057,0.1776],"tcp_to_object_dist_end":0.09326,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60903,0.16321,0.01602],"object_pos_start":[0.60903,0.16321,0.01601],"object_to_goal_dist_end":0.09364,"object_to_goal_dist_start":0.09365,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58817,0.17223,0.12831],"tcp_start":[0.59504,0.17431,0.10755],"tcp_to_object_dist_end":0.11457,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.60903,0.16321,0.01602],"object_pos_start":[0.60903,0.16321,0.01602],"object_to_goal_dist_end":0.09364,"object_to_goal_dist_start":0.09364,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58488,0.17115,0.21364],"tcp_start":[0.58817,0.17223,0.12831],"tcp_to_object_dist_end":0.19925,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```