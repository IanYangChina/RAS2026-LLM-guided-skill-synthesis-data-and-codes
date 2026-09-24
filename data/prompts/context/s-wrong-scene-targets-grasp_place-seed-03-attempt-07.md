## Search State

- **Seed**: 3
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2083 | 0.32 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2065 | 0.32 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.1555 | 0.21 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.0838 | 0.26 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.0686 | 0.23 | ✅ accepted |

**Proposal policy**: task_score is 0.32 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.208) — your mutation base

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
    anchor: body
    entity: grasp_target
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
    anchor: body
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
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
  control: impedance_control
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
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.005
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_z_offset:
      type: scalar
      range:
      - -0.01
      - 0.02
      default: 0.005
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
  - target: source=yaml, anchor=body, entity=grasp_target, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=body, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
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
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=abort, threshold=20.0
- **lower_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.005], tolerance=0.01
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

- **Composite score**: 0.208
- **task_score** (E): 0.319
- **fitness_score**: 0.638  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1389 |
| descend_grasp | 1.00 | 1.00 | 0.1337 |
| grasp_close | 1.00 | 1.00 | 0.0122 |
| lift_object | 1.00 | 1.00 | 0.0975 |
| approach_place | 0.00 | 1.00 | 0.0991 |
| lower_to_place | 0.67 | 1.00 | 0.1041 |
| release_object | 1.00 | 1.00 | 0.0218 |
| retract_after_place | 1.00 | 1.00 | 0.0855 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, 0.002, 0.168) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.507, 0.002, 0.168)→(0.506, 0.002, 0.034) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 27.129 | 0.123 |
| grasp_close | grasp | 1.00 / step_budget | (0.506, 0.002, 0.034)→(0.498, 0.002, 0.025) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 42.333 | 0.138 | 0.198 |
| lift_object | lift | 1.00 / step_budget | (0.498, 0.002, 0.025)→(0.494, 0.002, 0.123) | (0.511, 0.002, 0.026)→(0.513, 0.002, 0.119) | 0.246→0.218 | 1.00 / 23.000 | 0.109 | 0.715 |
| approach_place | approach | 0.00 / step_budget | (0.494, 0.002, 0.123)→(0.542, 0.073, 0.167) | (0.513, 0.002, 0.119)→(0.539, 0.081, 0.058) | 0.218→0.176 | 1.00 / 11.333 | 0.135 | 1.033 |
| lower_to_place | descend | 0.67 / step_budget | (0.542, 0.073, 0.167)→(0.600, 0.153, 0.137) | (0.539, 0.081, 0.058)→(0.541, 0.092, 0.016) | 0.176→0.175 | 1.00 / 8.333 | 0.123 | 0.579 |
| release_object | release | 1.00 / step_budget | (0.600, 0.153, 0.137)→(0.593, 0.151, 0.157) | (0.541, 0.092, 0.016)→(0.541, 0.092, 0.016) | 0.175→0.175 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_after_place | retract | 1.00 / step_budget | (0.593, 0.151, 0.157)→(0.590, 0.150, 0.243) | (0.541, 0.092, 0.016)→(0.541, 0.092, 0.016) | 0.175→0.175 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.415
- phase_score: 0.340
- phase_breakdown.place_at_goal_score: 0.120
- phase_breakdown.reach_object_score: 0.855
- grasp_place_fitness: 0.685

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.685
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.415
- **Median Q (composite search score)**: 0.207
- **K-run variance**: 0.0014
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.402


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.212,"average_solve_count":250.0,"average_success_count":250.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.14858,"approach_place.approach_place_height":0.11049,"descend_grasp.descend_speed":0.02713,"lift_object.lift_height":0.12473,"lower_to_place.place_z_offset":0.0045},"optimized_scores":{"best_composite_score":0.20681,"best_fitness_score":0.63681,"best_task_score":0.3115},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3261.0,"contact_point_centroid":[0.53217,0.10166,-0.00226],"force_p95":0.12931,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.49179,"mean_force":0.13769,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.56087,0.12838,0.13741]},{"body_a":"world","body_b":"grasp_target","contact_count":70.0,"contact_point_centroid":[0.45549,-0.02534,-0.00137],"force_p95":0.64286,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66332,"mean_force":0.16745,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44564,-0.02558,0.0291]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5440.0,"contact_point_centroid":[0.44464,-0.00638,0.07816],"force_p95":0.1017,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30305,"mean_force":0.06105,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44348,-0.02549,0.07567]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5944.0,"contact_point_centroid":[0.44471,-0.04451,0.07723],"force_p95":0.09602,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29228,"mean_force":0.05695,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44346,-0.02548,0.07551]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":636.0,"contact_point_centroid":[0.52295,0.05819,0.15408],"force_p95":0.20607,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27419,"mean_force":0.13918,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.51927,0.07596,0.15867]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1026.0,"contact_point_centroid":[0.52273,0.09427,0.15311],"force_p95":0.17079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24912,"mean_force":0.10223,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.51996,0.07702,0.158]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12882.0,"contact_point_centroid":[0.48435,0.04301,0.14826],"force_p95":0.11057,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23876,"mean_force":0.07683,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.47969,0.02446,0.14774]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12492.0,"contact_point_centroid":[0.4836,0.00572,0.14814],"force_p95":0.11632,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22385,"mean_force":0.07972,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.47964,0.02439,0.14772]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02616,-0.00206],"force_p95":0.14002,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19268,"mean_force":0.12738,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.4479,-0.02566,0.02879]},{"body_a":"world","body_b":"grasp_target","contact_count":1412.0,"contact_point_centroid":[0.45856,-0.02632,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48004,-0.0111,0.2446]},{"body_a":"world","body_b":"grasp_target","contact_count":2248.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.45592,-0.02444,0.11099]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53213,0.10154,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58189,0.15822,0.12773]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.53213,0.10154,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.57678,0.1567,0.18851]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4816.0,"contact_point_centroid":[0.44682,-0.00641,0.03011],"force_p95":0.06807,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09786,"mean_force":0.04488,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.44681,-0.02562,0.02778]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5172.0,"contact_point_centroid":[0.44667,-0.04486,0.02961],"force_p95":0.06685,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08231,"mean_force":0.043,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.44682,-0.02562,0.02778]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3199.0,"contact_point_centroid":[0.5636,0.13108,0.13866],"force_p95":0.0111,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0165,"mean_force":0.0106,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.5631,0.13107,0.13645]}],"total_contact_groups":17},"final_pose_error":0.01477,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.53213,0.10154,0.01602],"final_tcp_position":[0.57696,0.15672,0.2332],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.49179,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":354.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1412.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.46022,-0.02314,0.1879],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16192,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":562.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2248.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45439,-0.02589,0.03497],"tcp_start":[0.46022,-0.02314,0.1879],"tcp_to_object_dist_end":0.00988,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02566,0.02579],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30328,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13729,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11788.0,"raw_peak_contact_force":0.19268,"tcp_end":[0.44679,-0.02562,0.02775],"tcp_start":[0.45439,-0.02589,0.03497],"tcp_to_object_dist_end":0.01182,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":314.0,"n_steps_budget":780.0,"object_pos_end":[0.46126,-0.02534,0.12792],"object_pos_start":[0.45844,-0.02566,0.02579],"object_to_goal_dist_end":0.28854,"object_to_goal_dist_start":0.30328,"object_z_max":0.12764,"peak_contact_force":0.10892,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11454.0,"raw_peak_contact_force":0.66332,"tcp_end":[0.44329,-0.02546,0.133],"tcp_start":[0.44679,-0.02562,0.02775],"tcp_to_object_dist_end":0.01867,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52492,0.06907,0.14323],"object_pos_start":[0.46126,-0.02534,0.12792],"object_to_goal_dist_end":0.17686,"object_to_goal_dist_start":0.28854,"object_z_max":0.14322,"peak_contact_force":0.1606,"phase_name":"approach_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25374.0,"raw_peak_contact_force":0.23876,"subtask_id":"place_at_goal","tcp_end":[0.51527,0.069,0.16426],"tcp_start":[0.44329,-0.02546,0.133],"tcp_to_object_dist_end":0.02313,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53213,0.10154,0.01602],"object_pos_start":[0.52492,0.06907,0.14323],"object_to_goal_dist_end":0.17495,"object_to_goal_dist_start":0.17686,"object_z_max":0.14323,"peak_contact_force":0.12263,"phase_name":"lower_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8122.0,"raw_peak_contact_force":1.49179,"tcp_end":[0.58656,0.15946,0.12637],"tcp_start":[0.51527,0.069,0.16426],"tcp_to_object_dist_end":0.136,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53213,0.10154,0.01602],"object_pos_start":[0.53213,0.10154,0.01602],"object_to_goal_dist_end":0.17495,"object_to_goal_dist_start":0.17495,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58006,0.15766,0.14761],"tcp_start":[0.58656,0.15946,0.12637],"tcp_to_object_dist_end":0.15088,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.53213,0.10154,0.01602],"object_pos_start":[0.53213,0.10154,0.01602],"object_to_goal_dist_end":0.17495,"object_to_goal_dist_start":0.17495,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57696,0.15672,0.2332],"tcp_start":[0.58006,0.15766,0.14761],"tcp_to_object_dist_end":0.22853,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17227,"average_solve_count":238.0,"average_success_count":238.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.13418,"approach_place.approach_place_height":0.12798,"descend_grasp.descend_speed":0.01054,"lift_object.lift_height":0.11734,"lower_to_place.place_z_offset":-0.00994},"optimized_scores":{"best_composite_score":0.1628,"best_fitness_score":0.5928,"best_task_score":0.23128},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1519.0,"contact_point_centroid":[0.54963,0.06573,-0.00267],"force_p95":0.31351,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.47809,"mean_force":0.16204,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.55426,0.04242,0.16782]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.54083,0.00072,-0.00133],"force_p95":0.69115,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.74571,"mean_force":0.16086,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52861,0.00084,0.02547]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4793.0,"contact_point_centroid":[0.52868,-0.01813,0.06967],"force_p95":0.10939,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3387,"mean_force":0.07162,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52594,0.00079,0.06738]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5107.0,"contact_point_centroid":[0.52875,0.01963,0.06744],"force_p95":0.10845,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32174,"mean_force":0.06808,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52599,0.00079,0.06556]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5484.0,"contact_point_centroid":[0.53869,0.03448,0.13502],"force_p95":0.14838,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26533,"mean_force":0.09603,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.53406,0.01621,0.13596]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5135.0,"contact_point_centroid":[0.53831,-0.00293,0.13437],"force_p95":0.15577,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24437,"mean_force":0.09801,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.53352,0.01546,0.13511]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00099,-0.00203],"force_p95":0.13172,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15984,"mean_force":0.1253,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.53117,0.00089,0.0256]},{"body_a":"world","body_b":"grasp_target","contact_count":1784.0,"contact_point_centroid":[0.54431,0.00113,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51705,0.00047,0.23461]},{"body_a":"world","body_b":"grasp_target","contact_count":1868.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53607,0.00098,0.10174]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.55068,0.06763,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.59076,0.0917,0.17228]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55068,0.06763,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61279,0.12337,0.17261]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.55068,0.06763,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.60829,0.12228,0.23256]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53091,-0.01833,0.02687],"force_p95":0.07604,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1105,"mean_force":0.05171,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.52992,0.00087,0.02417]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53085,0.01995,0.02599],"force_p95":0.06804,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0965,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.52992,0.00087,0.02417]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1514.0,"contact_point_centroid":[0.5551,0.04305,0.17083],"force_p95":0.01175,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01478,"mean_force":0.01068,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.55475,0.04305,0.16859]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4260.0,"contact_point_centroid":[0.59125,0.09179,0.17456],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01282,"mean_force":0.01046,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.59082,0.09178,0.17228]}],"total_contact_groups":17},"final_pose_error":0.01493,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.55068,0.06763,0.01602],"final_tcp_position":[0.60859,0.12231,0.27745],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":447.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1784.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53665,0.00098,0.17032],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1445,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":467.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1868.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53861,0.00103,0.03424],"tcp_start":[0.53665,0.00098,0.17032],"tcp_to_object_dist_end":0.01,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54415,0.00073,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12964,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15984,"tcp_end":[0.52989,0.00087,0.02413],"tcp_start":[0.53861,0.00103,0.03424],"tcp_to_object_dist_end":0.01437,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":326.0,"n_steps_budget":750.0,"object_pos_end":[0.54567,0.00083,0.11825],"object_pos_start":[0.54415,0.00073,0.02588],"object_to_goal_dist_end":0.20107,"object_to_goal_dist_start":0.25053,"object_z_max":0.118,"peak_contact_force":0.11008,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9978.0,"raw_peak_contact_force":0.74571,"tcp_end":[0.52575,0.0008,0.12195],"tcp_start":[0.52989,0.00087,0.02413],"tcp_to_object_dist_end":0.02026,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55068,0.06763,0.01602],"object_pos_start":[0.54567,0.00083,0.11825],"object_to_goal_dist_end":0.21962,"object_to_goal_dist_start":0.20107,"object_z_max":0.12737,"peak_contact_force":0.12263,"phase_name":"approach_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13652.0,"raw_peak_contact_force":1.47809,"subtask_id":"place_at_goal","tcp_end":[0.56118,0.05116,0.17865],"tcp_start":[0.52575,0.0008,0.12195],"tcp_to_object_dist_end":0.16379,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55068,0.06763,0.01602],"object_pos_start":[0.55068,0.06763,0.01602],"object_to_goal_dist_end":0.21962,"object_to_goal_dist_start":0.21962,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lower_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8260.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61699,0.12426,0.17192],"tcp_start":[0.56118,0.05116,0.17865],"tcp_to_object_dist_end":0.17863,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55068,0.06763,0.01602],"object_pos_start":[0.55068,0.06763,0.01602],"object_to_goal_dist_end":0.21962,"object_to_goal_dist_start":0.21962,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61116,0.12296,0.19215],"tcp_start":[0.61699,0.12426,0.17192],"tcp_to_object_dist_end":0.19427,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.55068,0.06763,0.01602],"object_pos_start":[0.55068,0.06763,0.01602],"object_to_goal_dist_end":0.21962,"object_to_goal_dist_start":0.21962,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60859,0.12231,0.27745],"tcp_start":[0.61116,0.12296,0.19215],"tcp_to_object_dist_end":0.27329,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.02469,"average_solve_count":243.0,"average_success_count":243.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.10904,"approach_place.approach_place_height":0.11073,"descend_grasp.descend_speed":0.01043,"lift_object.lift_height":0.10858,"lower_to_place.place_z_offset":0.01066},"optimized_scores":{"best_composite_score":0.25539,"best_fitness_score":0.68539,"best_task_score":0.41533},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1485.0,"contact_point_centroid":[0.54167,0.10549,-0.00254],"force_p95":0.2963,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.38238,"mean_force":0.15212,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.54385,0.08834,0.14925]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.52721,0.02887,-0.00143],"force_p95":0.69466,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73667,"mean_force":0.16149,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5151,0.02948,0.026]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4468.0,"contact_point_centroid":[0.51497,0.01035,0.06701],"force_p95":0.10852,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33259,"mean_force":0.06916,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51257,0.02931,0.06457]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4845.0,"contact_point_centroid":[0.51502,0.0482,0.06487],"force_p95":0.10628,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33024,"mean_force":0.06538,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51261,0.02932,0.063]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6002.0,"contact_point_centroid":[0.52733,0.07092,0.12439],"force_p95":0.14874,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26915,"mean_force":0.09641,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.52263,0.05262,0.12512]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5584.0,"contact_point_centroid":[0.52706,0.03363,0.12411],"force_p95":0.15255,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25813,"mean_force":0.09732,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.52228,0.052,0.12473]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53054,0.03048,-0.00211],"force_p95":0.15594,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24033,"mean_force":0.13162,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.51767,0.02967,0.026]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4062.0,"contact_point_centroid":[0.51734,0.01039,0.02739],"force_p95":0.08003,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14032,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.51644,0.02958,0.02464]},{"body_a":"world","body_b":"grasp_target","contact_count":2028.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5109,0.01377,0.22264]},{"body_a":"world","body_b":"grasp_target","contact_count":1600.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52301,0.029,0.08995]},{"body_a":"world","body_b":"grasp_target","contact_count":3124.0,"contact_point_centroid":[0.54166,0.10571,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.57489,0.14239,0.12863]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54166,0.10571,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59065,0.17358,0.11263]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.54166,0.10571,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.5853,0.17185,0.17298]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4980.0,"contact_point_centroid":[0.51727,0.04873,0.02644],"force_p95":0.07242,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09075,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.51645,0.02959,0.02465]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1302.0,"contact_point_centroid":[0.54553,0.09033,0.15287],"force_p95":0.01183,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01625,"mean_force":0.01068,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.54506,0.09032,0.15062]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3313.0,"contact_point_centroid":[0.57544,0.14246,0.13086],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.01051,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.57492,0.14244,0.1286]}],"total_contact_groups":17},"final_pose_error":0.01509,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.54166,0.10571,0.01602],"final_tcp_position":[0.58548,0.17188,0.21765],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.38238,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":508.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2028.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52422,0.02808,0.14615],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12033,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":400.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1600.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52493,0.03015,0.0342],"tcp_start":[0.52422,0.02808,0.14615],"tcp_to_object_dist_end":0.00992,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53037,0.02953,0.02563],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18461,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14836,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10842.0,"raw_peak_contact_force":0.24033,"tcp_end":[0.51641,0.02958,0.02461],"tcp_start":[0.52493,0.03015,0.0342],"tcp_to_object_dist_end":0.014,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":294.0,"n_steps_budget":690.0,"object_pos_end":[0.5315,0.02944,0.11048],"object_pos_start":[0.53037,0.02953,0.02563],"object_to_goal_dist_end":0.16478,"object_to_goal_dist_start":0.18461,"object_z_max":0.11023,"peak_contact_force":0.10784,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9391.0,"raw_peak_contact_force":0.73667,"tcp_end":[0.5123,0.0293,0.11382],"tcp_start":[0.51641,0.02958,0.02461],"tcp_to_object_dist_end":0.01949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54166,0.10571,0.01602],"object_pos_start":[0.5315,0.02944,0.11048],"object_to_goal_dist_end":0.1318,"object_to_goal_dist_start":0.16478,"object_z_max":0.11516,"peak_contact_force":0.12263,"phase_name":"approach_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14373.0,"raw_peak_contact_force":1.38238,"subtask_id":"place_at_goal","tcp_end":[0.55056,0.09938,0.15686],"tcp_start":[0.5123,0.0293,0.11382],"tcp_to_object_dist_end":0.14127,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":781.0,"n_steps_budget":1000.0,"object_pos_end":[0.54166,0.10571,0.01602],"object_pos_start":[0.54166,0.10571,0.01602],"object_to_goal_dist_end":0.1318,"object_to_goal_dist_start":0.1318,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lower_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6437.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59551,0.17504,0.1116],"tcp_start":[0.55056,0.09938,0.15686],"tcp_to_object_dist_end":0.12977,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54166,0.10571,0.01602],"object_pos_start":[0.54166,0.10571,0.01602],"object_to_goal_dist_end":0.1318,"object_to_goal_dist_start":0.1318,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58873,0.17294,0.13235],"tcp_start":[0.59551,0.17504,0.1116],"tcp_to_object_dist_end":0.14237,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.54166,0.10571,0.01602],"object_pos_start":[0.54166,0.10571,0.01602],"object_to_goal_dist_end":0.1318,"object_to_goal_dist_start":0.1318,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58548,0.17188,0.21765],"tcp_start":[0.58873,0.17294,0.13235],"tcp_to_object_dist_end":0.21669,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```