## Search State

- **Seed**: 8
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.0720 | 0.18 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.3724 | 0.15 | ❌ rejected |
| 1 | pull → insert → descend → contact → release | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | contact_detected | force_exceeded | time_limit | 5 | 0.0851 | 0.15 | ❌ rejected |
| 0 | pull → insert → descend → contact → release | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | contact_detected | force_exceeded | time_limit | 5 | 0.0851 | 0.15 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`
- Frozen object start: [0.48269722766055606, 0.048727684333792556, 0.03]
- Frozen task target: [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]
- Goal object position: (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.48269722766055606, 0.048727684333792556, 0.03)
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
  frozen_object_start: [0.4827, 0.0487, 0.03]
  frozen_task_target: [0.5819, 0.2289, 0.2305]
  frozen_object_starts: {'grasp_target': [0.48269722766055606, 0.048727684333792556, 0.03]}
  frozen_targets: {'place_target': [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c

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
| `object` | offset from object initial position (0.48269722766055606, 0.048727684333792556, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5818710838485517, 0.2288548935820029, 0.2304844767544324) | final destination targets |
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

## Current Skill (Q=0.072) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: grasp_success
  anchor: object
  metric: contact
  weight: 0.2
- id: lift_clearance
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.2
  weight: 0.2
- id: place_accuracy
  target_entity: object
  weight: 0.4
phases:
- id: approach_object
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  end_effector_action: open
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.15
    offset_along_axis:
      distance: 0.0
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
      tolerance: 0.05
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: reach_object
- id: descend_grasp
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
    - 0.03
    tolerance: 0.01
    orientation:
      mode: keep_current
      tolerance: 0.05
  parameters:
    descent_height:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 1
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: reach_object
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
  guards:
  - id: check_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: grasp_success
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
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
      tolerance: 0.05
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  guards:
  - id: check_lift
    when: after_phase
    predicate: object_lifted
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.02
  subtask_id: lift_clearance
- id: transport_goal
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
      tolerance: 0.05
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: place_accuracy
- id: descend_place
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
    - 0.03
    tolerance: 0.01
    orientation:
      mode: keep_current
      tolerance: 0.05
  parameters:
    place_height:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 1
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: place_accuracy
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
  retries:
    max_attempts: 1
    strategy: repeat
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
      tolerance: 0.05
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 1
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], offset_along_axis={axis=world_z, distance=0.0, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current, tolerance=0.05
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=keep_current, tolerance=0.05
  - parameter_bindings:
    - descent_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=1, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=check_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current, tolerance=0.05
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=check_lift, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=repeat, offset=[0.0, 0.0, 0.02]
- **transport_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current, tolerance=0.05
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=keep_current, tolerance=0.05
  - parameter_bindings:
    - place_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=1, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - retries: max_attempts=1, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **retract_after_place** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current, tolerance=0.05
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=1, strategy=repeat, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.072
- **task_score** (E): 0.184
- **fitness_score**: 0.552  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1270 |
| descend_grasp | 1.00 | 1.00 | 0.1237 |
| grasp_object | 1.00 | 1.00 | 0.0125 |
| lift_object | 1.00 | 0.67 | 0.1204 |
| transport_goal | 0.67 | 1.00 | 0.2444 |
| descend_place | 1.00 | 1.00 | 0.0848 |
| release_object | 1.00 | 1.00 | 0.0200 |
| retract_after_place | 1.00 | 1.00 | 0.1323 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.513, -0.001, 0.181) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.513, -0.001, 0.181)→(0.516, -0.001, 0.057) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.516, -0.001, 0.057)→(0.508, -0.001, 0.048) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 39.333 | 0.148 | 0.191 |
| lift_object | lift | 1.00 / step_budget | (0.508, -0.001, 0.048)→(0.504, -0.001, 0.168) | (0.522, -0.001, 0.026)→(0.515, 0.003, 0.116) | 0.289→0.244 | 0.67 / 15.000 | 0.074 | 0.397 |
| transport_goal | approach | 0.67 / step_budget | (0.504, -0.001, 0.168)→(0.590, 0.172, 0.317) | (0.515, 0.003, 0.116)→(0.536, 0.048, 0.016) | 0.244→0.258 | 1.00 / 8.667 | 94252.613 | 1.590 |
| descend_place | descend | 1.00 / step_budget | (0.590, 0.172, 0.317)→(0.603, 0.201, 0.239) | (0.536, 0.048, 0.016)→(0.536, 0.048, 0.016) | 0.258→0.258 | 1.00 / 8.000 | 0.123 | 0.123 |
| release_object | release | 1.00 / step_budget | (0.603, 0.201, 0.239)→(0.598, 0.199, 0.259) | (0.536, 0.048, 0.016)→(0.536, 0.048, 0.016) | 0.258→0.258 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_after_place | retract | 1.00 / step_budget | (0.598, 0.199, 0.259)→(0.598, 0.199, 0.391) | (0.536, 0.048, 0.016)→(0.536, 0.048, 0.016) | 0.258→0.258 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.247
- phase_score: 0.560
- phase_breakdown.grasp_success_score: 1.000
- phase_breakdown.reach_object_score: 0.219
- phase_breakdown.lift_clearance_score: 0.186
- phase_breakdown.place_accuracy_score: 0.698
- grasp_place_fitness: 0.588

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.588
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.247
- **Median Q (composite search score)**: 0.057
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.406


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2cbd02033d1f1347f2ac2d0b012406a96501e6b48f5b172bd88b34d6c745630c`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5745d7c2d025a63f908a4bf0f58182445bb06541d436718f39304ac5569d60c0`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.2987,"descend_grasp.descent_height":0.02117,"descend_place.place_height":0.04839,"lift_object.lift_height":0.18114,"retract_after_place.retract_height":0.15993,"transport_goal.transport_speed":0.4966},"optimized_scores":{"best_composite_score":0.05183,"best_fitness_score":0.53183,"best_task_score":0.14173},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3853.0,"contact_point_centroid":[0.48374,0.05487,-0.00225],"force_p95":0.12529,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.57435,"mean_force":0.1345,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.51674,0.12879,0.28056]},{"body_a":"world","body_b":"grasp_target","contact_count":137.0,"contact_point_centroid":[0.48016,0.04612,-0.00122],"force_p95":0.27092,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4097,"mean_force":0.06011,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46878,0.04681,0.04965]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14370.0,"contact_point_centroid":[0.46963,0.06521,0.11353],"force_p95":0.10711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29335,"mean_force":0.06641,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46644,0.0466,0.11325]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12629.0,"contact_point_centroid":[0.46909,0.02774,0.10993],"force_p95":0.13634,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27259,"mean_force":0.07548,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46642,0.04659,0.11037]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48275,0.04862,-0.00214],"force_p95":0.16301,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.221,"mean_force":0.13307,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47136,0.04708,0.04887]},{"body_a":"world","body_b":"grasp_target","contact_count":2024.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48665,0.02732,0.22652]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4337.0,"contact_point_centroid":[0.47033,0.02771,0.04888],"force_p95":0.07724,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13541,"mean_force":0.04971,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47026,0.04697,0.04773]},{"body_a":"world","body_b":"grasp_target","contact_count":1640.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47665,0.04508,0.11915]},{"body_a":"world","body_b":"grasp_target","contact_count":816.0,"contact_point_centroid":[0.48374,0.05488,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5707,0.21347,0.31831]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.48374,0.05488,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57408,0.22204,0.28539]},{"body_a":"world","body_b":"grasp_target","contact_count":3612.0,"contact_point_centroid":[0.48374,0.05488,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.57229,0.22089,0.37546]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5503.0,"contact_point_centroid":[0.46982,0.06614,0.04939],"force_p95":0.06985,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07213,"mean_force":0.04036,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47026,0.04697,0.04773]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3881.0,"contact_point_centroid":[0.5197,0.13294,0.28653],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0163,"mean_force":0.01054,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.51934,0.13292,0.28431]},{"body_a":"left_finger","body_b":"right_finger","contact_count":875.0,"contact_point_centroid":[0.5712,0.21351,0.32059],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01258,"mean_force":0.0104,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5707,0.21348,0.31831]},{"body_a":"left_finger","body_b":"right_finger","contact_count":230.0,"contact_point_centroid":[0.57613,0.22292,0.28386],"force_p95":0.01088,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01249,"mean_force":0.00972,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57558,0.22288,0.28145]}],"total_contact_groups":15},"final_pose_error":0.01465,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.48374,0.05488,0.01602],"final_tcp_position":[0.5733,0.22118,0.45038],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.57435,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":357.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2024.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47773,0.04278,0.18305],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15722,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":410.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1640.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47796,0.04771,0.05581],"tcp_start":[0.47773,0.04278,0.18305],"tcp_to_object_dist_end":0.03018,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48268,0.04753,0.02549],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.2911,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15983,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11640.0,"raw_peak_contact_force":0.221,"subtask_id":"grasp_success","tcp_end":[0.47023,0.04697,0.0477],"tcp_start":[0.47796,0.04771,0.05581],"tcp_to_object_dist_end":0.02547,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48071,0.05773,0.11375],"object_pos_start":[0.48268,0.04753,0.02549],"object_to_goal_dist_end":0.23053,"object_to_goal_dist_start":0.2911,"object_z_max":0.16525,"peak_contact_force":0.0,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27136.0,"raw_peak_contact_force":0.4097,"subtask_id":"lift_clearance","tcp_end":[0.4668,0.04663,0.20866],"tcp_start":[0.47023,0.04697,0.0477],"tcp_to_object_dist_end":0.09656,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48374,0.05488,0.01602],"object_pos_start":[0.48071,0.05773,0.11375],"object_to_goal_dist_end":0.29308,"object_to_goal_dist_start":0.23053,"object_z_max":0.11375,"peak_contact_force":0.12263,"phase_name":"transport_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7734.0,"raw_peak_contact_force":1.57435,"subtask_id":"place_accuracy","tcp_end":[0.56606,0.20518,0.35106],"tcp_start":[0.4668,0.04663,0.20866],"tcp_to_object_dist_end":0.37632,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":204.0,"n_steps_budget":1000.0,"object_pos_end":[0.48374,0.05488,0.01602],"object_pos_start":[0.48374,0.05488,0.01602],"object_to_goal_dist_end":0.29308,"object_to_goal_dist_start":0.29308,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1691.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_accuracy","tcp_end":[0.57667,0.22318,0.28499],"tcp_start":[0.56606,0.20518,0.35106],"tcp_to_object_dist_end":0.33062,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48374,0.05488,0.01602],"object_pos_start":[0.48374,0.05488,0.01602],"object_to_goal_dist_end":0.29308,"object_to_goal_dist_start":0.29308,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1030.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5733,0.22156,0.30509],"tcp_start":[0.57667,0.22318,0.28499],"tcp_to_object_dist_end":0.3455,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":903.0,"n_steps_budget":990.0,"object_pos_end":[0.48374,0.05488,0.01602],"object_pos_start":[0.48374,0.05488,0.01602],"object_to_goal_dist_end":0.29308,"object_to_goal_dist_start":0.29308,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3612.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5733,0.22118,0.45038],"tcp_start":[0.5733,0.22156,0.30509],"tcp_to_object_dist_end":0.47365,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2b35d39beba75b46a5edd8e67b975c00ef2c88fb75a3753bdd32db5918adf9e2`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.12214,"average_solve_count":131.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.32538,"descend_grasp.descent_height":0.02762,"descend_place.place_height":0.03228,"lift_object.lift_height":0.10871,"retract_after_place.retract_height":0.10703,"transport_goal.transport_speed":0.33557},"optimized_scores":{"best_composite_score":0.0565,"best_fitness_score":0.5365,"best_task_score":0.16302},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3159.0,"contact_point_centroid":[0.55377,0.04274,-0.00226],"force_p95":0.12779,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.42194,"mean_force":0.13656,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.55923,0.09605,0.23985]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5823.0,"contact_point_centroid":[0.5221,-0.00244,0.08904],"force_p95":0.13685,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33059,"mean_force":0.09848,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51891,-0.02073,0.09185]},{"body_a":"world","body_b":"grasp_target","contact_count":151.0,"contact_point_centroid":[0.53483,-0.02055,-0.00122],"force_p95":0.25178,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.32592,"mean_force":0.06062,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52132,-0.02078,0.05371]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5984.0,"contact_point_centroid":[0.52193,-0.03896,0.09079],"force_p95":0.1339,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30083,"mean_force":0.0964,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51888,-0.02073,0.09392]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1020.0,"contact_point_centroid":[0.52605,-0.02861,0.14911],"force_p95":0.17519,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23952,"mean_force":0.11321,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.52041,-0.01066,0.15311]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1108.0,"contact_point_centroid":[0.5269,0.00964,0.15068],"force_p95":0.13647,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20975,"mean_force":0.10289,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.52104,-0.00824,0.15469]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53701,-0.02128,-0.00208],"force_p95":0.14283,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16946,"mean_force":0.12895,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52417,-0.02084,0.05328]},{"body_a":"world","body_b":"grasp_target","contact_count":2124.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51739,-0.01207,0.22551]},{"body_a":"world","body_b":"grasp_target","contact_count":1472.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52735,-0.01992,0.12077]},{"body_a":"world","body_b":"grasp_target","contact_count":1156.0,"contact_point_centroid":[0.55384,0.04279,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59591,0.19609,0.26964]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55384,0.04279,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60141,0.21844,0.23919]},{"body_a":"world","body_b":"grasp_target","contact_count":2412.0,"contact_point_centroid":[0.55384,0.04279,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.59848,0.21702,0.30208]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3624.0,"contact_point_centroid":[0.52521,-0.00192,0.0509],"force_p95":0.09659,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11086,"mean_force":0.05928,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52298,-0.02081,0.05187]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4015.0,"contact_point_centroid":[0.52406,-0.03963,0.05084],"force_p95":0.09028,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09269,"mean_force":0.05358,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52299,-0.02081,0.05188]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3107.0,"contact_point_centroid":[0.56195,0.10223,0.2472],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01051,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.56157,0.10223,0.245]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1228.0,"contact_point_centroid":[0.59643,0.19608,0.27192],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01269,"mean_force":0.01048,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59591,0.19607,0.26968]}],"total_contact_groups":17},"final_pose_error":0.01525,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.55384,0.04279,0.01602],"final_tcp_position":[0.59897,0.21713,0.35042],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273009.07529,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":382.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2124.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52601,-0.019,0.18034],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15473,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":368.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1472.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53125,-0.02097,0.06179],"tcp_start":[0.52601,-0.019,0.18034],"tcp_to_object_dist_end":0.03623,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53692,-0.02095,0.02555],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14395,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9439.0,"raw_peak_contact_force":0.16946,"subtask_id":"grasp_success","tcp_end":[0.52296,-0.02081,0.05184],"tcp_start":[0.53125,-0.02097,0.06179],"tcp_to_object_dist_end":0.02977,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.52482,-0.02049,0.11293],"object_pos_start":[0.53692,-0.02095,0.02555],"object_to_goal_dist_end":0.27903,"object_to_goal_dist_start":0.31672,"object_z_max":0.11282,"peak_contact_force":0.13476,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11958.0,"raw_peak_contact_force":0.33059,"subtask_id":"lift_clearance","tcp_end":[0.51894,-0.02072,0.14801],"tcp_start":[0.52296,-0.02081,0.05184],"tcp_to_object_dist_end":0.03557,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55384,0.04279,0.01602],"object_pos_start":[0.52482,-0.02049,0.11293],"object_to_goal_dist_end":0.27209,"object_to_goal_dist_start":0.27903,"object_z_max":0.12456,"peak_contact_force":273009.07529,"phase_name":"transport_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8394.0,"raw_peak_contact_force":1.42194,"subtask_id":"place_accuracy","tcp_end":[0.58858,0.17361,0.30428],"tcp_start":[0.51894,-0.02072,0.14801],"tcp_to_object_dist_end":0.31846,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":289.0,"n_steps_budget":1000.0,"object_pos_end":[0.55384,0.04279,0.01602],"object_pos_start":[0.55384,0.04279,0.01602],"object_to_goal_dist_end":0.27209,"object_to_goal_dist_start":0.27209,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2384.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_accuracy","tcp_end":[0.60467,0.21957,0.23928],"tcp_start":[0.58858,0.17361,0.30428],"tcp_to_object_dist_end":0.28927,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55384,0.04279,0.01602],"object_pos_start":[0.55384,0.04279,0.01602],"object_to_goal_dist_end":0.27209,"object_to_goal_dist_start":0.27209,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60033,0.21789,0.25855],"tcp_start":[0.60467,0.21957,0.23928],"tcp_to_object_dist_end":0.30273,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.55384,0.04279,0.01602],"object_pos_start":[0.55384,0.04279,0.01602],"object_to_goal_dist_end":0.27209,"object_to_goal_dist_start":0.27209,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2412.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59897,0.21713,0.35042],"tcp_start":[0.60033,0.21789,0.25855],"tcp_to_object_dist_end":0.37981,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `530652a2467d9ac78fab654e7ed7fc5283ca1649270bc8f158e04c16074f9f95`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02632,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.44195,"descend_grasp.descent_height":0.02022,"descend_place.place_height":0.01008,"lift_object.lift_height":0.11649,"retract_after_place.retract_height":0.18889,"transport_goal.transport_speed":0.47795},"optimized_scores":{"best_composite_score":0.10762,"best_fitness_score":0.58762,"best_task_score":0.24694},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2449.0,"contact_point_centroid":[0.57174,0.04498,-0.00241],"force_p95":0.14142,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.77385,"mean_force":0.14258,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.58751,0.0867,0.2473]},{"body_a":"world","body_b":"grasp_target","contact_count":149.0,"contact_point_centroid":[0.54307,-0.02815,-0.00116],"force_p95":0.29452,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45081,"mean_force":0.07133,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52954,-0.02845,0.04575]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3772.0,"contact_point_centroid":[0.54246,0.01233,0.16392],"force_p95":0.11089,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30201,"mean_force":0.07636,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.53623,-0.00622,0.16336]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10399.0,"contact_point_centroid":[0.5304,-0.00946,0.09306],"force_p95":0.1008,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30022,"mean_force":0.06513,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52698,-0.02836,0.09059]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10727.0,"contact_point_centroid":[0.53051,-0.04724,0.09251],"force_p95":0.09653,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28903,"mean_force":0.06381,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52697,-0.02836,0.09066]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3444.0,"contact_point_centroid":[0.54133,-0.0273,0.16177],"force_p95":0.14106,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25775,"mean_force":0.0803,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.535,-0.00858,0.16133]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54562,-0.02914,-0.00207],"force_p95":0.14115,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18373,"mean_force":0.12811,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53244,-0.02854,0.04549]},{"body_a":"world","body_b":"grasp_target","contact_count":2224.0,"contact_point_centroid":[0.5456,-0.02923,-0.00194],"force_p95":0.13197,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.52224,-0.01653,0.22547]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4635.0,"contact_point_centroid":[0.53193,-0.00931,0.04702],"force_p95":0.07317,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13391,"mean_force":0.04625,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53122,-0.02851,0.04404]},{"body_a":"world","body_b":"grasp_target","contact_count":1540.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.5355,-0.02741,0.11643]},{"body_a":"world","body_b":"grasp_target","contact_count":1144.0,"contact_point_centroid":[0.57175,0.04497,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62085,0.14854,0.24371]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57175,0.04497,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62295,0.15908,0.19281]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.57175,0.04497,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.61936,0.15788,0.28939]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4912.0,"contact_point_centroid":[0.53219,-0.04771,0.04579],"force_p95":0.07055,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0789,"mean_force":0.04496,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53122,-0.02851,0.04404]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2397.0,"contact_point_centroid":[0.59011,0.0909,0.25342],"force_p95":0.01162,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01865,"mean_force":0.01057,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.58987,0.0909,0.25114]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.62603,0.1599,0.19143],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01256,"mean_force":0.01004,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62544,0.15989,0.1894]}],"total_contact_groups":17},"final_pose_error":0.02911,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.57175,0.04497,0.01602],"final_tcp_position":[0.62039,0.15809,0.37196],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":9748.6416,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":407.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2224.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53395,-0.02622,0.17922],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15367,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":385.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1540.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.5397,-0.02876,0.05427],"tcp_start":[0.53395,-0.02622,0.17922],"tcp_to_object_dist_end":0.02886,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54552,-0.02856,0.02574],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26061,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13911,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11347.0,"raw_peak_contact_force":0.18373,"subtask_id":"grasp_success","tcp_end":[0.53119,-0.02851,0.044],"tcp_start":[0.5397,-0.02876,0.05427],"tcp_to_object_dist_end":0.02322,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.53986,-0.02831,0.12282],"object_pos_start":[0.54552,-0.02856,0.02574],"object_to_goal_dist_end":0.22117,"object_to_goal_dist_start":0.26061,"object_z_max":0.12271,"peak_contact_force":0.08591,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21275.0,"raw_peak_contact_force":0.45081,"subtask_id":"lift_clearance","tcp_end":[0.52713,-0.02836,0.14789],"tcp_start":[0.53119,-0.02851,0.044],"tcp_to_object_dist_end":0.02811,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57175,0.04497,0.01602],"object_pos_start":[0.53986,-0.02831,0.12282],"object_to_goal_dist_end":0.20979,"object_to_goal_dist_start":0.22117,"object_z_max":0.15385,"peak_contact_force":9748.6416,"phase_name":"transport_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12062.0,"raw_peak_contact_force":1.77385,"subtask_id":"place_accuracy","tcp_end":[0.61643,0.13839,0.29435],"tcp_start":[0.52713,-0.02836,0.14789],"tcp_to_object_dist_end":0.29697,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":286.0,"n_steps_budget":1000.0,"object_pos_end":[0.57175,0.04497,0.01602],"object_pos_start":[0.57175,0.04497,0.01602],"object_to_goal_dist_end":0.20979,"object_to_goal_dist_start":0.20979,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2357.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_accuracy","tcp_end":[0.62707,0.16015,0.19329],"tcp_start":[0.61643,0.13839,0.29435],"tcp_to_object_dist_end":0.21852,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57175,0.04497,0.01602],"object_pos_start":[0.57175,0.04497,0.01602],"object_to_goal_dist_end":0.20979,"object_to_goal_dist_start":0.20979,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6215,0.1586,0.21216],"tcp_start":[0.62707,0.16015,0.19329],"tcp_to_object_dist_end":0.23207,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57175,0.04497,0.01602],"object_pos_start":[0.57175,0.04497,0.01602],"object_to_goal_dist_end":0.20979,"object_to_goal_dist_start":0.20979,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62039,0.15809,0.37196],"tcp_start":[0.6215,0.1586,0.21216],"tcp_to_object_dist_end":0.37664,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```