## Search State

- **Seed**: 2
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 13 | -0.3119 | 0.13 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 13 | -0.5021 | 0.13 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | -0.4925 | 0.13 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 10 | -0.2139 | 0.16 | ❌ rejected |
| 10 | grasp → lift → approach → descend → release | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | admittance_control | position_control | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 7 | -0.1005 | 0.20 | ❌ rejected |

**Proposal policy**: task_score is 0.13 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`
- Frozen object start: [0.631422574059428, 0.1591915942135097, 0.1900150788948481]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5, 0.0, 0.3)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.4761612134249316, -0.02015088565858767, 0.03)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.4761612134249316, -0.02015088565858767, 0.03]
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
  frozen_object_start: [0.4762, -0.0202, 0.03]
  frozen_task_target: [0.6314, 0.1592, 0.19]
  frozen_object_starts: {'grasp_target': [0.631422574059428, 0.1591915942135097, 0.1900150788948481]}
  frozen_targets: {'place_target': [0.5, 0.0, 0.3]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a

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
| `object` | offset from object initial position (0.631422574059428, 0.1591915942135097, 0.1900150788948481) | approach/contact targets near object start |
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

## Current Skill (Q=-0.312) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: grasp_contact
  anchor: object
  weight: 0.3
- id: place_goal
  metric: goal_progress
  weight: 0.5
phases:
- id: raise_tcp
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
    - 0.3
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    raise_height:
      type: scalar
      range:
      - 0.2
      - 0.4
      default: 0.3
      binds_to:
      - path: target.offset.z
        mode: replace
    raise_speed:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
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
    - 0.2
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    approach_offset_z:
      type: scalar
      range:
      - 0.15
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.25
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_object
- id: descend_grasp
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    descend_force_thresh:
      type: scalar
      range:
      - 3.0
      - 15.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  guards:
  - id: grasp_contact_guard
    when: during_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
  subtask_id: grasp_contact
- id: grasp_action
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
  - id: bilateral_grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: lift_object
  type: lift
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: object_lifted_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
- id: transport_to_goal
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
    - 0.15
    tolerance: 0.025
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    transport_arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.25
      binds_to:
      - path: generator.speed
        mode: replace
    transport_z:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_goal
- id: descend_place
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - -0.02
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    place_force_thresh:
      type: scalar
      range:
      - 3.0
      - 15.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
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
  parameters:
    release_duration:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **raise_tcp** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.3], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - raise_height: status=consumed; consumers=target.offset.z (replace)
    - raise_speed: status=consumed; consumers=generator.speed (replace)
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - approach_offset_z: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - descend_force_thresh: status=consumed; consumers=termination.force_threshold (replace)
  - guards:
    - id=grasp_contact_guard, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **grasp_action** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=bilateral_grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=repeat
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=object_lifted_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.02
  - retries: max_attempts=1, strategy=repeat
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.025
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - transport_arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_z: status=consumed; consumers=target.offset.z (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, -0.02], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - place_force_thresh: status=consumed; consumers=termination.force_threshold (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: -0.312
- **task_score** (E): 0.130
- **fitness_score**: 0.202  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.286
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.800

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.33 | 1.00 | 0.1769 |
| descend_grasp | 1.00 | 1.00 | 0.0012 |
| grasp_action | 1.00 | 1.00 | 0.0000 |
| lift_object | 1.00 | 1.00 | 0.0010 |
| transport_to_goal | 0.33 | 1.00 | 0.2056 |
| descend_place | 1.00 | 1.00 | 0.0013 |
| release_object | 1.00 | 1.00 | 0.0291 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.436, -0.008, 0.161) | (0.493, -0.015, 0.030)→(0.466, -0.016, 0.019) | 0.279→0.300 | 1.00 / 4.667 | 291.274 | 950.321 |
| descend_grasp | descend | 1.00 / force_exceeded | (0.436, -0.008, 0.161)→(0.436, -0.008, 0.160) | (0.466, -0.016, 0.019)→(0.466, -0.016, 0.019) | 0.300→0.300 | 1.00 / 4.667 | 405.109 | 292.573 |
| grasp_action | grasp | 1.00 / step_budget | (0.415, -0.008, 0.095)→(0.415, -0.008, 0.095) | (0.466, -0.016, 0.019)→(0.465, -0.016, 0.019) | 0.300→0.300 | 1.00 / 8.667 | 44.952 | 242.000 |
| lift_object | lift | 1.00 / step_budget | (0.454, -0.014, 0.153)→(0.454, -0.014, 0.154) | (0.465, -0.016, 0.019)→(0.465, -0.016, 0.019) | 0.300→0.300 | 1.00 / 8.667 | 182006.286 | 254.909 |
| transport_to_goal | approach | 0.33 / step_budget | (0.454, -0.014, 0.154)→(0.527, 0.144, 0.261) | (0.465, -0.016, 0.019)→(0.441, 0.000, 0.016) | 0.300→0.307 | 1.00 / 9.333 | 91177.462 | 1212.094 |
| descend_place | descend | 1.00 / force_exceeded | (0.527, 0.144, 0.261)→(0.528, 0.144, 0.261) | (0.441, 0.000, 0.016)→(0.441, 0.000, 0.016) | 0.307→0.307 | 1.00 / 8.667 | 3393.717 | 164.603 |
| release_object | release | 1.00 / step_budget | (0.528, 0.144, 0.261)→(0.535, 0.141, 0.288) | (0.441, 0.000, 0.016)→(0.441, 0.000, 0.016) | 0.307→0.307 | 1.00 / 4.000 | 0.123 | 271.920 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.156
- phase_score: 0.044
- phase_breakdown.grasp_contact_score: 0.011
- phase_breakdown.approach_object_score: 0.202
- phase_breakdown.place_goal_score: 0.000
- grasp_place_fitness: 0.251

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.251
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.156
- **Median Q (composite search score)**: -0.333
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at lower bound**: release_object.release_duration
- **Final σ (mean)**: 0.346


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `dde525b5f1d1bd9dc458c18c8bb170b8849a392c0909c5e3e8e19baca2e18946`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3eaf951d4314ad541ffae42f4c615c856bb77d128e3ae1cab520a1988305ba67`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.63142,0.15919,0.19002]},{"name":"goal","value":[0.47616,-0.02015,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":4.0,"average_failure_rate":0.0381,"average_mean_iterations":12.14286,"average_solve_count":105.0,"average_success_count":101.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_arc":0.10379,"approach_object.approach_speed":0.29556,"approach_object.approach_z":0.20382,"descend_grasp.descend_force_thresh":8.32716,"descend_grasp.descend_speed":0.10974,"descend_place.place_force_thresh":10.60789,"descend_place.place_speed":0.14192,"lift_object.lift_height":0.13548,"lift_object.lift_speed":0.13168,"release_object.release_duration":1.04642,"transport_to_goal.transport_arc":0.14972,"transport_to_goal.transport_speed":0.29584,"transport_to_goal.transport_z":0.09329},"optimized_scores":{"best_composite_score":-0.33977,"best_fitness_score":0.17452,"best_task_score":0.12604},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":792.0,"contact_point_centroid":[0.63216,0.00228,-0.00048],"force_p95":221.01096,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1314.09664,"mean_force":208.71845,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38468,0.00116,0.10922]},{"body_a":"world","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.52454,0.00846,-0.003],"force_p95":352.3546,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1228.74373,"mean_force":70.4456,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37185,0.00378,0.0483]},{"body_a":"world","body_b":"link6","contact_count":582.0,"contact_point_centroid":[0.57401,-0.01091,-0.00026],"force_p95":347.22874,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":691.31509,"mean_force":220.864,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.35546,-0.01697,0.07724]},{"body_a":"world","body_b":"link6","contact_count":8.0,"contact_point_centroid":[0.6303,-0.00452,-0.00011],"force_p95":360.57469,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":365.4433,"mean_force":273.66286,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.38883,-0.00611,0.12738]},{"body_a":"world","body_b":"link6","contact_count":70.0,"contact_point_centroid":[0.63764,0.12591,-0.00011],"force_p95":77.80508,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":347.83445,"mean_force":72.5525,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.44817,0.09122,0.20334]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.63022,-0.00446,-0.00013],"force_p95":79.98129,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":337.39854,"mean_force":72.38855,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.38855,-0.00603,0.12697]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.62955,-0.0047,-0.00024],"force_p95":307.93421,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":307.93421,"mean_force":307.93421,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.38817,-0.00627,0.12729]},{"body_a":"world","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.63708,0.12552,-8e-05],"force_p95":245.38066,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":248.46678,"mean_force":217.60563,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.44846,0.09114,0.20425]},{"body_a":"world","body_b":"link7","contact_count":79.0,"contact_point_centroid":[0.48574,-0.02391,-7e-05],"force_p95":215.14732,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":239.95649,"mean_force":96.61685,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.34466,-0.0287,0.04435]},{"body_a":"grasp_target","body_b":"hand","contact_count":42.0,"contact_point_centroid":[0.4534,-0.01658,0.03985],"force_p95":3.73791,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.16026,"mean_force":1.63832,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38095,0.00384,0.05142]},{"body_a":"grasp_target","body_b":"hand","contact_count":472.0,"contact_point_centroid":[0.4433,-0.02581,0.02759],"force_p95":0.63809,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.97142,"mean_force":0.5397,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.34167,-0.02327,0.05803]},{"body_a":"grasp_target","body_b":"link7","contact_count":466.0,"contact_point_centroid":[0.44921,-0.01236,0.02629],"force_p95":0.7047,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.58538,"mean_force":0.50294,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.34018,-0.02186,0.05997]},{"body_a":"world","body_b":"grasp_target","contact_count":3543.0,"contact_point_centroid":[0.4412,-0.01981,-0.00216],"force_p95":0.13839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.31405,"mean_force":0.13977,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39851,0.00136,0.12137]},{"body_a":"world","body_b":"grasp_target","contact_count":3422.0,"contact_point_centroid":[0.4222,-0.00463,-0.00316],"force_p95":0.39547,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.82687,"mean_force":0.21682,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.37592,0.00701,0.13163]},{"body_a":"grasp_target","body_b":"link7","contact_count":32.0,"contact_point_centroid":[0.48175,-0.00108,0.01127],"force_p95":0.74026,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.7738,"mean_force":0.31937,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37232,0.00379,0.05413]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.4357,-0.01974,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.38817,-0.00627,0.12729]}],"total_contact_groups":25},"final_pose_error":0.19574,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.41462,0.02048,0.01602],"final_tcp_position":[0.44843,0.09118,0.20414],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273051.53464,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":905.0,"n_steps_budget":1000.0,"object_pos_end":[0.4357,-0.01974,0.01602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.31718,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":218.52032,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4432.0,"raw_peak_contact_force":1314.09664,"subtask_id":"approach_object","tcp_end":[0.38817,-0.00627,0.12729],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12174,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.4357,-0.01974,0.01602],"object_pos_start":[0.4357,-0.01974,0.01602],"object_to_goal_dist_end":0.31718,"object_to_goal_dist_start":0.31718,"object_z_max":0.01602,"peak_contact_force":307.93421,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":307.93421,"subtask_id":"grasp_contact","tcp_end":[0.38815,-0.00618,0.12734],"tcp_start":[0.38817,-0.00627,0.12729],"tcp_to_object_dist_end":0.12181,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.4357,-0.01974,0.01602],"object_pos_start":[0.4357,-0.01974,0.01602],"object_to_goal_dist_end":0.31718,"object_to_goal_dist_start":0.31718,"object_z_max":0.01602,"peak_contact_force":67.34897,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3494.0,"raw_peak_contact_force":337.39854,"tcp_end":[0.38865,-0.00605,0.12678],"tcp_start":[0.38865,-0.00605,0.12678],"tcp_to_object_dist_end":0.12111,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":151.0,"n_steps_budget":600.0,"object_pos_end":[0.4357,-0.01974,0.01602],"object_pos_start":[0.4357,-0.01974,0.01602],"object_to_goal_dist_end":0.31718,"object_to_goal_dist_start":0.31718,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1240.0,"raw_peak_contact_force":365.4433,"tcp_end":[0.42299,-0.0172,0.14054],"tcp_start":[0.42176,-0.01667,0.14052],"tcp_to_object_dist_end":0.12519,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":962.0,"n_steps_budget":1000.0,"object_pos_end":[0.41462,0.02048,0.01602],"object_pos_start":[0.4357,-0.01974,0.01602],"object_to_goal_dist_end":0.31068,"object_to_goal_dist_start":0.31718,"object_z_max":0.03056,"peak_contact_force":292.93964,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9059.0,"raw_peak_contact_force":691.31509,"subtask_id":"place_goal","tcp_end":[0.44846,0.09114,0.20429],"tcp_start":[0.42299,-0.0172,0.14054],"tcp_to_object_dist_end":0.20392,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.41462,0.02048,0.01602],"object_pos_start":[0.41462,0.02048,0.01602],"object_to_goal_dist_end":0.31068,"object_to_goal_dist_start":0.31068,"object_z_max":0.01602,"peak_contact_force":186.74449,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":19.0,"raw_peak_contact_force":248.46678,"tcp_end":[0.44843,0.09118,0.20414],"tcp_start":[0.44846,0.09114,0.20429],"tcp_to_object_dist_end":0.20379,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.41462,0.02048,0.01602],"object_pos_start":[0.41462,0.02048,0.01602],"object_to_goal_dist_end":0.31068,"object_to_goal_dist_start":0.31068,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1090.0,"raw_peak_contact_force":347.83445,"tcp_end":[0.44601,0.09072,0.22764],"tcp_start":[0.44843,0.09118,0.20414],"tcp_to_object_dist_end":0.22517,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `92fc0f2bbc35407e7976a239cbab7bb266e8a517486aa3be6bd6666f4c63f38d`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.63013,0.20822,0.11412]},{"name":"goal","value":[0.45856,-0.02632,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.44554,"average_solve_count":101.0,"average_success_count":101.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_arc":0.17987,"approach_object.approach_speed":0.10467,"approach_object.approach_z":0.23771,"descend_grasp.descend_force_thresh":14.23311,"descend_grasp.descend_speed":0.08682,"descend_place.place_force_thresh":7.02531,"descend_place.place_speed":0.16374,"lift_object.lift_height":0.11021,"lift_object.lift_speed":0.13108,"release_object.release_duration":0.50005,"transport_to_goal.transport_arc":0.16871,"transport_to_goal.transport_speed":0.32858,"transport_to_goal.transport_z":0.10457},"optimized_scores":{"best_composite_score":-0.33269,"best_fitness_score":0.18159,"best_task_score":0.10912},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":732.0,"contact_point_centroid":[0.61376,-0.01465,-0.00051],"force_p95":212.87147,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1536.72764,"mean_force":214.56885,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.36112,-0.0131,0.09804]},{"body_a":"world","body_b":"link6","contact_count":861.0,"contact_point_centroid":[0.58847,0.01956,-0.00026],"force_p95":693.98829,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1396.18177,"mean_force":288.63742,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.3731,0.01161,0.11706]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.61232,-0.01914,-0.00027],"force_p95":569.65845,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":569.65845,"mean_force":569.65845,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.35777,-0.01846,0.09843]},{"body_a":"world","body_b":"link6","contact_count":38.0,"contact_point_centroid":[0.62084,0.12551,-0.00022],"force_p95":419.81978,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":467.80407,"mean_force":78.19162,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.52785,0.18026,0.26879]},{"body_a":"world","body_b":"link6","contact_count":8.0,"contact_point_centroid":[0.61009,-0.02141,-0.0001],"force_p95":397.26578,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":399.15955,"mean_force":313.3823,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.35876,-0.0186,0.09864]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.61871,0.12409,-0.00013],"force_p95":245.22055,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":245.22055,"mean_force":245.22055,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.50501,0.18668,0.2592]},{"body_a":"world","body_b":"link7","contact_count":38.0,"contact_point_centroid":[0.50707,-0.02656,-5e-05],"force_p95":129.48512,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":152.92613,"mean_force":79.03613,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.3477,-0.03592,0.04508]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.60645,-0.0237,-0.00013],"force_p95":84.54816,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":124.23024,"mean_force":72.03364,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.35843,-0.01852,0.0982]},{"body_a":"grasp_target","body_b":"hand","contact_count":38.0,"contact_point_centroid":[0.43977,-0.03178,0.04211],"force_p95":3.55392,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.97536,"mean_force":1.59294,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.36535,-0.00895,0.05656]},{"body_a":"grasp_target","body_b":"link7","contact_count":27.0,"contact_point_centroid":[0.46442,-0.01373,0.01103],"force_p95":0.51237,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.77028,"mean_force":0.29185,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.35563,-0.00898,0.05887]},{"body_a":"grasp_target","body_b":"hand","contact_count":425.0,"contact_point_centroid":[0.44228,-0.03332,0.0284],"force_p95":0.63831,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.99487,"mean_force":0.46369,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.34381,-0.02677,0.05948]},{"body_a":"world","body_b":"grasp_target","contact_count":3311.0,"contact_point_centroid":[0.42358,-0.02823,-0.00216],"force_p95":0.13842,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.77887,"mean_force":0.1414,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.3779,-0.01222,0.11185]},{"body_a":"grasp_target","body_b":"link7","contact_count":260.0,"contact_point_centroid":[0.44337,-0.03575,0.03233],"force_p95":0.4376,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.39671,"mean_force":0.27879,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.3379,-0.02149,0.06129]},{"body_a":"world","body_b":"grasp_target","contact_count":3788.0,"contact_point_centroid":[0.41378,-0.02444,-0.00263],"force_p95":0.32873,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.90739,"mean_force":0.17113,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.38117,0.02144,0.12902]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.41764,-0.02858,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.35777,-0.01846,0.09843]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.41764,-0.02858,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.35843,-0.01852,0.0982]}],"total_contact_groups":25},"final_pose_error":0.19237,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.41294,-0.02336,0.01602],"final_tcp_position":[0.50726,0.18626,0.2605],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273011.08918,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":846.0,"n_steps_budget":1000.0,"object_pos_end":[0.41764,-0.02858,0.01602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.33294,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":211.64999,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4126.0,"raw_peak_contact_force":1536.72764,"subtask_id":"approach_object","tcp_end":[0.35777,-0.01846,0.09843],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10237,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.41764,-0.02858,0.01602],"object_pos_start":[0.41764,-0.02858,0.01602],"object_to_goal_dist_end":0.33294,"object_to_goal_dist_start":0.33294,"object_z_max":0.01602,"peak_contact_force":823.8094,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":569.65845,"subtask_id":"grasp_contact","tcp_end":[0.3579,-0.01846,0.09867],"tcp_start":[0.35777,-0.01846,0.09843],"tcp_to_object_dist_end":0.10248,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.41764,-0.02858,0.01602],"object_pos_start":[0.41764,-0.02858,0.01602],"object_to_goal_dist_end":0.33294,"object_to_goal_dist_start":0.33294,"object_z_max":0.01602,"peak_contact_force":67.38433,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3490.0,"raw_peak_contact_force":124.23024,"tcp_end":[0.35857,-0.01857,0.09802],"tcp_start":[0.35857,-0.01856,0.09802],"tcp_to_object_dist_end":0.10155,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":182.0,"n_steps_budget":600.0,"object_pos_end":[0.41764,-0.02858,0.01602],"object_pos_start":[0.41764,-0.02858,0.01602],"object_to_goal_dist_end":0.33294,"object_to_goal_dist_start":0.33294,"object_z_max":0.01602,"peak_contact_force":273011.08918,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1498.0,"raw_peak_contact_force":399.15955,"tcp_end":[0.40417,-0.02694,0.11569],"tcp_start":[0.40297,-0.02666,0.11564],"tcp_to_object_dist_end":0.10059,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41294,-0.02336,0.01602],"object_pos_start":[0.41764,-0.02858,0.01602],"object_to_goal_dist_end":0.3323,"object_to_goal_dist_start":0.33294,"object_z_max":0.01919,"peak_contact_force":211.84478,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9553.0,"raw_peak_contact_force":1396.18177,"subtask_id":"place_goal","tcp_end":[0.50501,0.18668,0.2592],"tcp_start":[0.40417,-0.02694,0.11569],"tcp_to_object_dist_end":0.33426,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.41294,-0.02336,0.01602],"object_pos_start":[0.41294,-0.02336,0.01602],"object_to_goal_dist_end":0.3323,"object_to_goal_dist_start":0.3323,"object_z_max":0.01602,"peak_contact_force":245.22055,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9.0,"raw_peak_contact_force":245.22055,"tcp_end":[0.50726,0.18626,0.2605],"tcp_start":[0.50501,0.18668,0.2592],"tcp_to_object_dist_end":0.33558,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.41294,-0.02336,0.01602],"object_pos_start":[0.41294,-0.02336,0.01602],"object_to_goal_dist_end":0.3323,"object_to_goal_dist_start":0.3323,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1058.0,"raw_peak_contact_force":467.80407,"tcp_end":[0.53114,0.17922,0.29751],"tcp_start":[0.50726,0.18626,0.2605],"tcp_to_object_dist_end":0.3664,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3b2449a94ded39f3d450008c4da002b4ddf87103ab7d1b86900d116c316ff53`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.64762,0.15808,0.1911]},{"name":"goal","value":[0.54431,0.00113,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.0177,"average_solve_count":113.0,"average_success_count":113.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_arc":0.07379,"approach_object.approach_speed":0.39708,"approach_object.approach_z":0.22184,"descend_grasp.descend_force_thresh":5.99938,"descend_grasp.descend_speed":0.16931,"descend_place.place_force_thresh":11.88364,"descend_place.place_speed":0.1764,"lift_object.lift_height":0.19627,"lift_object.lift_speed":0.11798,"release_object.release_duration":0.96705,"transport_to_goal.transport_arc":0.09277,"transport_to_goal.transport_speed":0.32199,"transport_to_goal.transport_z":0.11574},"optimized_scores":{"best_composite_score":-0.26321,"best_fitness_score":0.25108,"best_task_score":0.15604},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":587.0,"contact_point_centroid":[0.64972,0.01852,-0.00054],"force_p95":339.01542,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1548.78454,"mean_force":215.91224,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.43362,0.01904,0.16618]},{"body_a":"world","body_b":"hand","contact_count":23.0,"contact_point_centroid":[0.50035,-0.01945,-0.00131],"force_p95":230.54602,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":264.37091,"mean_force":53.1298,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.45647,0.00044,-0.00822]},{"body_a":"world","body_b":"right_finger","contact_count":750.0,"contact_point_centroid":[0.46054,0.04195,-0.00464],"force_p95":12.87673,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":18.36943,"mean_force":3.09599,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.45751,0.00042,-0.00498]},{"body_a":"world","body_b":"left_finger","contact_count":748.0,"contact_point_centroid":[0.46059,-0.04108,-0.00465],"force_p95":12.90521,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":18.30613,"mean_force":3.02512,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.45751,0.00042,-0.00501]},{"body_a":"grasp_target","body_b":"link7","contact_count":352.0,"contact_point_centroid":[0.52775,-0.00156,0.0557],"force_p95":0.29008,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.44585,"mean_force":0.28887,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.42525,0.00135,0.14564]},{"body_a":"grasp_target","body_b":"hand","contact_count":139.0,"contact_point_centroid":[0.53399,0.00333,0.04262],"force_p95":1.66804,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.98324,"mean_force":0.66213,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.47166,0.00042,0.01828]},{"body_a":"world","body_b":"grasp_target","contact_count":1986.0,"contact_point_centroid":[0.544,0.00116,-0.00284],"force_p95":0.60119,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.07258,"mean_force":0.18521,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.49607,0.00046,0.05905]},{"body_a":"world","body_b":"grasp_target","contact_count":2989.0,"contact_point_centroid":[0.50889,0.00279,-0.003],"force_p95":0.38738,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.01708,"mean_force":0.18774,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.46929,0.0633,0.20393]},{"body_a":"grasp_target","body_b":"hand","contact_count":6.0,"contact_point_centroid":[0.51566,-0.0159,0.04904],"force_p95":0.7111,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.72331,"mean_force":0.62218,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.42487,-0.00182,0.11163]},{"body_a":"world","body_b":"grasp_target","contact_count":208.0,"contact_point_centroid":[0.54431,0.00113,-0.00137],"force_p95":0.13839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12476,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.53123,0.00058,0.29623]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.54431,0.00113,-0.00207],"force_p95":0.12631,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12631,"mean_force":0.12631,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.56287,0.00102,0.2579]},{"body_a":"world","body_b":"grasp_target","contact_count":2264.0,"contact_point_centroid":[0.54229,0.00118,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12266,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51747,0.00067,0.13634]},{"body_a":"world","body_b":"grasp_target","contact_count":8.0,"contact_point_centroid":[0.49544,0.00372,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62699,0.15432,0.31954]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.49544,0.00372,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62713,0.15437,0.31849]},{"body_a":"left_finger","body_b":"right_finger","contact_count":782.0,"contact_point_centroid":[0.50054,0.00042,0.06096],"force_p95":0.01221,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01644,"mean_force":0.01048,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.49859,0.00042,0.05966]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4033.0,"contact_point_centroid":[0.46251,0.05135,0.19275],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01275,"mean_force":0.01046,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.46091,0.05145,0.194]}],"total_contact_groups":19},"final_pose_error":0.12944,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.49544,0.00372,0.01602],"final_tcp_position":[0.6273,0.15429,0.31888],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273027.60121,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":53.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02586],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25023,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":443.65214,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":208.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.56287,0.00102,0.2579],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23278,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02586],"object_pos_start":[0.54431,0.00113,0.02586],"object_to_goal_dist_end":0.25023,"object_to_goal_dist_start":0.25023,"object_z_max":0.02586,"peak_contact_force":83.58197,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12631,"subtask_id":"grasp_contact","tcp_end":[0.56343,0.00103,0.25476],"tcp_start":[0.56287,0.00102,0.2579],"tcp_to_object_dist_end":0.2297,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.54231,0.00118,0.02602],"object_pos_start":[0.54431,0.00113,0.02586],"object_to_goal_dist_end":0.25092,"object_to_goal_dist_start":0.25023,"object_z_max":0.02777,"peak_contact_force":0.12265,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":4428.0,"raw_peak_contact_force":264.37091,"tcp_end":[0.49862,0.00042,0.05971],"tcp_start":[0.49862,0.00042,0.0597],"tcp_to_object_dist_end":0.05518,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":566.0,"n_steps_budget":900.0,"object_pos_end":[0.54229,0.00118,0.02602],"object_pos_start":[0.54228,0.00118,0.02602],"object_to_goal_dist_end":0.25093,"object_to_goal_dist_start":0.25094,"object_z_max":0.02602,"peak_contact_force":273007.64526,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4729.0,"raw_peak_contact_force":0.12266,"tcp_end":[0.53619,0.00095,0.20455],"tcp_start":[0.53638,0.00097,0.20422],"tcp_to_object_dist_end":0.17863,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":947.0,"n_steps_budget":1000.0,"object_pos_end":[0.49544,0.00372,0.01602],"object_pos_start":[0.54229,0.00118,0.02602],"object_to_goal_dist_end":0.27864,"object_to_goal_dist_start":0.25093,"object_z_max":0.02721,"peak_contact_force":273027.60121,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7967.0,"raw_peak_contact_force":1548.78454,"subtask_id":"place_goal","tcp_end":[0.62682,0.15434,0.31973],"tcp_start":[0.53619,0.00095,0.20455],"tcp_to_object_dist_end":0.36358,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.49544,0.00372,0.01602],"object_pos_start":[0.49544,0.00372,0.01602],"object_to_goal_dist_end":0.27864,"object_to_goal_dist_start":0.27864,"object_z_max":0.01602,"peak_contact_force":9749.18598,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":18.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6273,0.15429,0.31888],"tcp_start":[0.62682,0.15434,0.31973],"tcp_to_object_dist_end":0.36302,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49544,0.00372,0.01602],"object_pos_start":[0.49544,0.00372,0.01602],"object_to_goal_dist_end":0.27864,"object_to_goal_dist_start":0.27864,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6274,0.15432,0.33806],"tcp_start":[0.6273,0.15429,0.31888],"tcp_to_object_dist_end":0.37921,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```