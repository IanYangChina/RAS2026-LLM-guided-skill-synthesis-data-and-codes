## Search State

- **Seed**: 2
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | -0.3479 | 0.13 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | -0.3633 | 0.16 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | -0.2170 | 0.14 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | -0.2377 | 0.16 | ✅ accepted |
| 0 | align → align → pull → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | contact_detected | 0 | 0.1073 | 0.16 | ✅ accepted |

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

## Current Skill (Q=-0.348) — your mutation base

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
- id: approach_object
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.1
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
    approach_arc_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.12
      binds_to:
      - path: generator.arc_height
        mode: replace
    approach_offset_z:
      type: scalar
      range:
      - 0.05
      - 0.18
      default: 0.1
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
    - 0.08
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
    place_approach_z:
      type: scalar
      range:
      - 0.04
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
    place_arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
    place_transport_speed:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.25
      binds_to:
      - path: generator.speed
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
- id: retract_after_place
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
    tolerance: 0.05
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.25
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - approach_arc_height: status=consumed; consumers=generator.arc_height (replace)
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
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.08], tolerance=0.025
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - place_approach_z: status=consumed; consumers=target.offset.z (replace)
    - place_arc_height: status=consumed; consumers=generator.arc_height (replace)
    - place_transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, -0.02], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - place_force_thresh: status=consumed; consumers=termination.force_threshold (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
- **retract_after_place** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.348
- **task_score** (E): 0.133
- **fitness_score**: 0.182  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.780

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.00 | 1.00 | 0.1959 |
| descend_grasp | 1.00 | 1.00 | 0.0012 |
| grasp_action | 1.00 | 1.00 | 0.0000 |
| lift_object | 1.00 | 1.00 | 0.0014 |
| approach_goal | 0.33 | 1.00 | 0.2515 |
| descend_place | 1.00 | 1.00 | 0.0263 |
| release_object | 1.00 | 1.00 | 0.0316 |
| retract_after_place | 0.33 | 1.00 | 0.1024 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.420, -0.003, 0.127) | (0.493, -0.015, 0.030)→(0.453, -0.014, 0.016) | 0.279→0.307 | 1.00 / 4.667 | 147.256 | 1418.582 |
| descend_grasp | descend | 1.00 / force_exceeded | (0.420, -0.003, 0.127)→(0.419, -0.002, 0.127) | (0.453, -0.014, 0.016)→(0.453, -0.014, 0.016) | 0.307→0.307 | 1.00 / 4.667 | 616.508 | 205.857 |
| grasp_action | grasp | 1.00 / step_budget | (0.420, -0.001, 0.127)→(0.420, -0.001, 0.127) | (0.453, -0.014, 0.016)→(0.453, -0.014, 0.016) | 0.307→0.307 | 1.00 / 9.333 | 91052.389 | 271.253 |
| lift_object | lift | 1.00 / step_budget | (0.445, -0.012, 0.206)→(0.446, -0.012, 0.207) | (0.453, -0.014, 0.016)→(0.453, -0.014, 0.016) | 0.307→0.307 | 1.00 / 8.667 | 91015.907 | 108.516 |
| approach_goal | approach | 0.33 / step_budget | (0.446, -0.012, 0.207)→(0.517, 0.200, 0.218) | (0.453, -0.014, 0.016)→(0.446, -0.002, 0.016) | 0.307→0.305 | 1.00 / 8.667 | 222.329 | 1070.036 |
| descend_place | descend | 1.00 / force_exceeded | (0.517, 0.200, 0.218)→(0.514, 0.219, 0.234) | (0.446, -0.002, 0.016)→(0.446, -0.002, 0.016) | 0.305→0.305 | 1.00 / 9.333 | 181649.299 | 158.027 |
| release_object | release | 1.00 / step_budget | (0.514, 0.219, 0.234)→(0.512, 0.222, 0.258) | (0.446, -0.002, 0.016)→(0.446, -0.002, 0.016) | 0.305→0.305 | 1.00 / 4.000 | 0.123 | 266.477 |
| retract_after_place | retract | 0.33 / step_budget | (0.512, 0.222, 0.258)→(0.567, 0.199, 0.266) | (0.446, -0.002, 0.016)→(0.446, -0.002, 0.016) | 0.305→0.305 | 1.00 / 4.000 | 0.123 | 450.022 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.168
- phase_score: 0.088
- phase_breakdown.grasp_contact_score: 0.118
- phase_breakdown.approach_object_score: 0.189
- phase_breakdown.place_goal_score: 0.028
- grasp_place_fitness: 0.217

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.217
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.168
- **Median Q (composite search score)**: -0.362
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.397


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":16.0,"average_failure_rate":0.13793,"average_mean_iterations":33.23276,"average_solve_count":116.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.place_approach_z":0.09087,"approach_goal.place_arc_height":0.08794,"approach_goal.place_transport_speed":0.29151,"approach_object.approach_arc_height":0.21651,"approach_object.approach_offset_z":0.17998,"approach_object.approach_speed":0.30642,"descend_grasp.descend_force_thresh":6.30236,"descend_place.place_force_thresh":9.00742,"lift_object.lift_height":0.17761,"lift_object.lift_speed":0.13742,"release_object.release_duration":1.462,"retract_after_place.retract_speed":0.27218},"optimized_scores":{"best_composite_score":-0.36804,"best_fitness_score":0.16196,"best_task_score":0.12125},"replay_outcomes":[{"contacts":{"omitted_contact_groups":5,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":852.0,"contact_point_centroid":[0.63426,0.0004,-0.00046],"force_p95":216.55041,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1439.74302,"mean_force":207.53448,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39121,-0.00043,0.11791]},{"body_a":"world","body_b":"link6","contact_count":793.0,"contact_point_centroid":[0.57923,0.02715,-0.00036],"force_p95":792.41494,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1319.88511,"mean_force":371.92002,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.39614,0.01787,0.2027]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.63083,-0.00632,-0.00013],"force_p95":79.39573,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":328.22318,"mean_force":73.02039,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.40048,-0.00761,0.14648]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.63024,-0.00659,-0.00023],"force_p95":306.12273,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":306.12273,"mean_force":306.12273,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.40015,-0.00787,0.14666]},{"body_a":"world","body_b":"link6","contact_count":8.0,"contact_point_centroid":[0.63099,-0.00638,-0.00011],"force_p95":155.69259,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":160.91155,"mean_force":116.31383,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.40067,-0.00767,0.14656]},{"body_a":"grasp_target","body_b":"hand","contact_count":42.0,"contact_point_centroid":[0.45538,-0.01148,0.03835],"force_p95":3.57763,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.93781,"mean_force":1.63048,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38433,0.0022,0.05005]},{"body_a":"world","body_b":"grasp_target","contact_count":3789.0,"contact_point_centroid":[0.44081,-0.01889,-0.00214],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.33384,"mean_force":0.13909,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40354,-0.00019,0.12845]},{"body_a":"grasp_target","body_b":"link7","contact_count":27.0,"contact_point_centroid":[0.48233,-0.002,0.01107],"force_p95":0.56395,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.59773,"mean_force":0.2507,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37434,0.00214,0.04972]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.43585,-0.01869,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.40015,-0.00787,0.14666]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.43585,-0.01869,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.40048,-0.00761,0.14648]},{"body_a":"world","body_b":"grasp_target","contact_count":628.0,"contact_point_centroid":[0.43585,-0.01869,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.41399,-0.01238,0.16299]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.43585,-0.01869,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.40442,0.04018,0.19612]},{"body_a":"world","body_b":"grasp_target","contact_count":72.0,"contact_point_centroid":[0.43585,-0.01869,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.44324,0.50784,0.18703]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.43585,-0.01869,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.41484,0.54626,0.19823]},{"body_a":"world","body_b":"grasp_target","contact_count":716.0,"contact_point_centroid":[0.43585,-0.01869,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.4606,0.47052,0.24616]},{"body_a":"left_finger","body_b":"right_finger","contact_count":761.0,"contact_point_centroid":[0.40257,-0.00762,0.14528],"force_p95":0.01262,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01566,"mean_force":0.01083,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.40055,-0.00763,0.14633]}],"total_contact_groups":21},"final_pose_error":0.26173,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.43585,-0.01869,0.01602],"final_tcp_position":[0.50761,0.38629,0.25008],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273047.475,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.43585,-0.01869,0.01602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.31649,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":214.36089,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4733.0,"raw_peak_contact_force":1439.74302,"subtask_id":"approach_object","tcp_end":[0.40015,-0.00787,0.14666],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13586,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.43585,-0.01869,0.01602],"object_pos_start":[0.43585,-0.01869,0.01602],"object_to_goal_dist_end":0.31649,"object_to_goal_dist_start":0.31649,"object_z_max":0.01602,"peak_contact_force":306.12273,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":306.12273,"subtask_id":"grasp_contact","tcp_end":[0.40013,-0.00778,0.14673],"tcp_start":[0.40015,-0.00787,0.14666],"tcp_to_object_dist_end":0.13594,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.43585,-0.01869,0.01602],"object_pos_start":[0.43585,-0.01869,0.01602],"object_to_goal_dist_end":0.31649,"object_to_goal_dist_start":0.31649,"object_z_max":0.01602,"peak_contact_force":85.46288,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3511.0,"raw_peak_contact_force":328.22318,"tcp_end":[0.40056,-0.00763,0.14632],"tcp_start":[0.40056,-0.00763,0.14633],"tcp_to_object_dist_end":0.13545,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":157.0,"n_steps_budget":600.0,"object_pos_end":[0.43585,-0.01869,0.01602],"object_pos_start":[0.43585,-0.01869,0.01602],"object_to_goal_dist_end":0.31649,"object_to_goal_dist_start":0.31649,"object_z_max":0.01602,"peak_contact_force":273047.475,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1293.0,"raw_peak_contact_force":160.91155,"tcp_end":[0.42607,-0.0165,0.17805],"tcp_start":[0.42509,-0.01603,0.177],"tcp_to_object_dist_end":0.16234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43585,-0.01869,0.01602],"object_pos_start":[0.43585,-0.01869,0.01602],"object_to_goal_dist_end":0.31649,"object_to_goal_dist_start":0.31649,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8996.0,"raw_peak_contact_force":1319.88511,"subtask_id":"place_goal","tcp_end":[0.44709,0.47622,0.16083],"tcp_start":[0.42607,-0.0165,0.17805],"tcp_to_object_dist_end":0.51578,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":18.0,"n_steps_budget":1000.0,"object_pos_end":[0.43585,-0.01869,0.01602],"object_pos_start":[0.43585,-0.01869,0.01602],"object_to_goal_dist_end":0.31649,"object_to_goal_dist_start":0.31649,"object_z_max":0.01602,"peak_contact_force":272822.93692,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":144.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.43624,0.53374,0.20957],"tcp_start":[0.44709,0.47622,0.16083],"tcp_to_object_dist_end":0.58535,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.43585,-0.01869,0.01602],"object_pos_start":[0.43585,-0.01869,0.01602],"object_to_goal_dist_end":0.31649,"object_to_goal_dist_start":0.31649,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.41305,0.54626,0.21511],"tcp_start":[0.43624,0.53374,0.20957],"tcp_to_object_dist_end":0.59944,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":179.0,"n_steps_budget":1000.0,"object_pos_end":[0.43585,-0.01869,0.01602],"object_pos_start":[0.43585,-0.01869,0.01602],"object_to_goal_dist_end":0.31649,"object_to_goal_dist_start":0.31649,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":716.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50761,0.38629,0.25008],"tcp_start":[0.41305,0.54626,0.21511],"tcp_to_object_dist_end":0.47323,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":11.0,"average_failure_rate":0.1028,"average_mean_iterations":25.50467,"average_solve_count":107.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.place_approach_z":0.07024,"approach_goal.place_arc_height":0.07735,"approach_goal.place_transport_speed":0.24949,"approach_object.approach_arc_height":0.21651,"approach_object.approach_offset_z":0.1678,"approach_object.approach_speed":0.3305,"descend_grasp.descend_force_thresh":9.37217,"descend_place.place_force_thresh":11.85611,"lift_object.lift_height":0.20843,"lift_object.lift_speed":0.15148,"release_object.release_duration":0.77329,"retract_after_place.retract_speed":0.22934},"optimized_scores":{"best_composite_score":-0.36237,"best_fitness_score":0.16763,"best_task_score":0.11055},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":852.0,"contact_point_centroid":[0.56331,0.0453,-0.00034],"force_p95":748.19616,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1456.71135,"mean_force":432.21538,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.41529,0.02412,0.23588]},{"body_a":"world","body_b":"link5","contact_count":10.0,"contact_point_centroid":[0.56005,0.23238,-0.00081],"force_p95":1341.21554,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1349.82139,"mean_force":1156.36034,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.54531,0.05264,0.22477]},{"body_a":"world","body_b":"link6","contact_count":852.0,"contact_point_centroid":[0.63264,0.00111,-0.00045],"force_p95":230.06528,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1339.22796,"mean_force":212.18641,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.3856,0.00016,0.10862]},{"body_a":"world","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.52247,0.00768,-0.00305],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1293.43424,"mean_force":51.73737,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.3725,0.00359,0.04666]},{"body_a":"world","body_b":"link6","contact_count":42.0,"contact_point_centroid":[0.60174,0.12631,-0.00021],"force_p95":548.45789,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":576.15124,"mean_force":100.4909,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.48718,-0.02366,0.20945]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.63039,-0.00987,-0.00012],"force_p95":78.77501,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":324.05935,"mean_force":72.17361,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.39167,-0.01078,0.13243]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.62976,-0.01005,-0.00019],"force_p95":311.32601,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":311.32601,"mean_force":311.32601,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.39132,-0.011,0.13279]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.59895,0.13031,-0.00024],"force_p95":286.38212,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":286.38212,"mean_force":286.38212,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.46929,-0.0192,0.20078]},{"body_a":"world","body_b":"link6","contact_count":6.0,"contact_point_centroid":[0.63053,-0.00991,-0.0001],"force_p95":79.27076,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":91.49945,"mean_force":34.68837,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.39176,-0.01082,0.13239]},{"body_a":"grasp_target","body_b":"hand","contact_count":42.0,"contact_point_centroid":[0.43741,-0.01972,0.0416],"force_p95":3.57881,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.83319,"mean_force":1.44449,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38174,0.00364,0.04891]},{"body_a":"world","body_b":"grasp_target","contact_count":3764.0,"contact_point_centroid":[0.42305,-0.02526,-0.00215],"force_p95":0.13822,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.37759,"mean_force":0.13958,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39848,0.00041,0.12029]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.41781,-0.02508,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.39132,-0.011,0.13279]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.41781,-0.02508,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.39167,-0.01078,0.13243]},{"body_a":"world","body_b":"grasp_target","contact_count":1036.0,"contact_point_centroid":[0.41781,-0.02508,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.40194,-0.01748,0.17122]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.41781,-0.02508,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.4166,0.02562,0.2324]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.41781,-0.02508,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.46929,-0.0192,0.20078]}],"total_contact_groups":23},"final_pose_error":0.16254,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.41781,-0.02508,0.01602],"final_tcp_position":[0.55625,0.06478,0.23376],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":271937.38251,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.41781,-0.02508,0.01602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.33035,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":227.28385,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4683.0,"raw_peak_contact_force":1339.22796,"subtask_id":"approach_object","tcp_end":[0.39132,-0.011,0.13279],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12056,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.41781,-0.02508,0.01602],"object_pos_start":[0.41781,-0.02508,0.01602],"object_to_goal_dist_end":0.33035,"object_to_goal_dist_start":0.33035,"object_z_max":0.01602,"peak_contact_force":873.57453,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":311.32601,"subtask_id":"grasp_contact","tcp_end":[0.3913,-0.01093,0.13285],"tcp_start":[0.39132,-0.011,0.13279],"tcp_to_object_dist_end":0.12063,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.41781,-0.02508,0.01602],"object_pos_start":[0.41781,-0.02508,0.01602],"object_to_goal_dist_end":0.33035,"object_to_goal_dist_start":0.33035,"object_z_max":0.01602,"peak_contact_force":67.58251,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3500.0,"raw_peak_contact_force":324.05935,"tcp_end":[0.39176,-0.0108,0.13225],"tcp_start":[0.39175,-0.0108,0.13225],"tcp_to_object_dist_end":0.11997,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":259.0,"n_steps_budget":600.0,"object_pos_end":[0.41781,-0.02508,0.01602],"object_pos_start":[0.41781,-0.02508,0.01602],"object_to_goal_dist_end":0.33035,"object_to_goal_dist_start":0.33035,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":2132.0,"raw_peak_contact_force":91.49945,"tcp_end":[0.41222,-0.02337,0.20723],"tcp_start":[0.41188,-0.023,0.20564],"tcp_to_object_dist_end":0.1913,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41781,-0.02508,0.01602],"object_pos_start":[0.41781,-0.02508,0.01602],"object_to_goal_dist_end":0.33035,"object_to_goal_dist_start":0.33035,"object_z_max":0.01602,"peak_contact_force":233.35047,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9105.0,"raw_peak_contact_force":1456.71135,"subtask_id":"place_goal","tcp_end":[0.46929,-0.0192,0.20078],"tcp_start":[0.41222,-0.02337,0.20723],"tcp_to_object_dist_end":0.19189,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.41781,-0.02508,0.01602],"object_pos_start":[0.41781,-0.02508,0.01602],"object_to_goal_dist_end":0.33035,"object_to_goal_dist_start":0.33035,"object_z_max":0.01602,"peak_contact_force":271937.38251,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9.0,"raw_peak_contact_force":286.38212,"tcp_end":[0.47133,-0.02017,0.20157],"tcp_start":[0.46929,-0.0192,0.20078],"tcp_to_object_dist_end":0.19318,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.41781,-0.02508,0.01602],"object_pos_start":[0.41781,-0.02508,0.01602],"object_to_goal_dist_end":0.33035,"object_to_goal_dist_start":0.33035,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1080.0,"raw_peak_contact_force":576.15124,"tcp_end":[0.48797,-0.02436,0.2386],"tcp_start":[0.47133,-0.02017,0.20157],"tcp_to_object_dist_end":0.23338,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":106.0,"n_steps_budget":750.0,"object_pos_end":[0.41781,-0.02508,0.01602],"object_pos_start":[0.41781,-0.02508,0.01602],"object_to_goal_dist_end":0.33035,"object_to_goal_dist_start":0.33035,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":434.0,"raw_peak_contact_force":1349.82139,"tcp_end":[0.55625,0.06478,0.23376],"tcp_start":[0.48797,-0.02436,0.2386],"tcp_to_object_dist_end":0.27322,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.24272,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.place_approach_z":0.08511,"approach_goal.place_arc_height":0.13461,"approach_goal.place_transport_speed":0.29234,"approach_object.approach_arc_height":0.09572,"approach_object.approach_offset_z":0.17922,"approach_object.approach_speed":0.15491,"descend_grasp.descend_force_thresh":9.91714,"descend_place.place_force_thresh":9.95408,"lift_object.lift_height":0.23832,"lift_object.lift_speed":0.16891,"release_object.release_duration":1.49635,"retract_after_place.retract_speed":0.24828},"optimized_scores":{"best_composite_score":-0.31319,"best_fitness_score":0.21681,"best_task_score":0.1679},"replay_outcomes":[{"contacts":{"omitted_contact_groups":6,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":42.0,"contact_point_centroid":[0.62283,0.00293,-0.00296],"force_p95":575.23902,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1476.77457,"mean_force":103.32429,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47333,-0.00223,0.04086]},{"body_a":"world","body_b":"link6","contact_count":165.0,"contact_point_centroid":[0.70557,-9e-05,-0.00114],"force_p95":363.50837,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":814.46326,"mean_force":219.22306,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4722,-0.00401,0.05631]},{"body_a":"world","body_b":"link6","contact_count":11.0,"contact_point_centroid":[0.5894,0.0138,-0.00036],"force_p95":401.22237,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":433.51275,"mean_force":331.31042,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51609,0.04901,0.27722]},{"body_a":"world","body_b":"link6","contact_count":86.0,"contact_point_centroid":[0.6227,0.12536,-0.00025],"force_p95":125.27866,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":223.15689,"mean_force":77.52224,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.63546,0.14429,0.29313]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.62193,0.12458,-0.00058],"force_p95":187.57614,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":187.57614,"mean_force":187.57614,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.63538,0.14411,0.29239]},{"body_a":"world","body_b":"link6","contact_count":548.0,"contact_point_centroid":[0.71649,-0.02521,-0.00014],"force_p95":103.38763,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":161.47552,"mean_force":70.02571,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46642,0.01499,0.10188]},{"body_a":"world","body_b":"link6","contact_count":6.0,"contact_point_centroid":[0.71652,-0.02511,-0.0001],"force_p95":61.825,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":73.13623,"mean_force":21.34166,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46642,0.015,0.10194]},{"body_a":"grasp_target","body_b":"hand","contact_count":207.0,"contact_point_centroid":[0.5344,0.00476,0.03226],"force_p95":3.16253,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.85494,"mean_force":0.57368,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47411,-0.00352,0.05685]},{"body_a":"world","body_b":"grasp_target","contact_count":1359.0,"contact_point_centroid":[0.52155,0.00088,-0.0027],"force_p95":0.53639,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.99576,"mean_force":0.19654,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49915,-0.00133,0.115]},{"body_a":"grasp_target","body_b":"link6","contact_count":133.0,"contact_point_centroid":[0.5151,0.01315,0.03562],"force_p95":0.79479,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.24853,"mean_force":0.4491,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51808,0.0361,0.30558]},{"body_a":"world","body_b":"grasp_target","contact_count":1471.0,"contact_point_centroid":[0.48714,0.02683,-0.00248],"force_p95":0.56123,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.90099,"mean_force":0.1698,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55573,0.06963,0.30593]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.50441,0.00092,-0.00199],"force_p95":0.12279,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12402,"mean_force":0.12259,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46642,0.01498,0.10188]},{"body_a":"world","body_b":"grasp_target","contact_count":16.0,"contact_point_centroid":[0.50442,0.00091,-0.002],"force_p95":0.12364,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12364,"mean_force":0.1203,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.46707,0.0118,0.10101]},{"body_a":"world","body_b":"grasp_target","contact_count":1864.0,"contact_point_centroid":[0.50441,0.00092,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48365,0.00795,0.17346]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.48394,0.03894,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.63538,0.14411,0.29239]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.48394,0.03894,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.6355,0.14419,0.29936]}],"total_contact_groups":22},"final_pose_error":0.028,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.48394,0.03894,0.01602],"final_tcp_position":[0.638,0.14581,0.31436],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273004.1212,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":356.0,"n_steps_budget":1000.0,"object_pos_end":[0.50433,0.00108,0.01598],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.27541,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12362,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1773.0,"raw_peak_contact_force":1476.77457,"subtask_id":"approach_object","tcp_end":[0.46725,0.01107,0.10022],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09258,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.50434,0.00103,0.01601],"object_pos_start":[0.50433,0.00108,0.01598],"object_to_goal_dist_end":0.27542,"object_to_goal_dist_start":0.27541,"object_z_max":0.016,"peak_contact_force":669.82815,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":16.0,"raw_peak_contact_force":0.12364,"subtask_id":"grasp_contact","tcp_end":[0.46683,0.01363,0.10222],"tcp_start":[0.46725,0.01107,0.10022],"tcp_to_object_dist_end":0.09486,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50441,0.00092,0.01602],"object_pos_start":[0.50434,0.00103,0.01601],"object_to_goal_dist_end":0.27544,"object_to_goal_dist_start":0.27542,"object_z_max":0.01605,"peak_contact_force":273004.1212,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3532.0,"raw_peak_contact_force":161.47552,"tcp_end":[0.46642,0.015,0.10175],"tcp_start":[0.46642,0.01499,0.10175],"tcp_to_object_dist_end":0.09482,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":466.0,"n_steps_budget":600.0,"object_pos_end":[0.50441,0.00092,0.01602],"object_pos_start":[0.50441,0.00092,0.01602],"object_to_goal_dist_end":0.27544,"object_to_goal_dist_start":0.27544,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3932.0,"raw_peak_contact_force":73.13623,"tcp_end":[0.49977,0.00331,0.23637],"tcp_start":[0.49945,0.00336,0.23536],"tcp_to_object_dist_end":0.22041,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":425.0,"n_steps_budget":1000.0,"object_pos_end":[0.48394,0.03894,0.01602],"object_pos_start":[0.50441,0.00092,0.01602],"object_to_goal_dist_end":0.26766,"object_to_goal_dist_start":0.27544,"object_z_max":0.01834,"peak_contact_force":433.51275,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3471.0,"raw_peak_contact_force":433.51275,"subtask_id":"place_goal","tcp_end":[0.63538,0.14411,0.29239],"tcp_start":[0.49977,0.00331,0.23637],"tcp_to_object_dist_end":0.33223,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.48394,0.03894,0.01602],"object_pos_start":[0.48394,0.03894,0.01602],"object_to_goal_dist_end":0.26766,"object_to_goal_dist_start":0.26766,"object_z_max":0.01602,"peak_contact_force":187.57614,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9.0,"raw_peak_contact_force":187.57614,"tcp_end":[0.63547,0.14426,0.29218],"tcp_start":[0.63538,0.14411,0.29239],"tcp_to_object_dist_end":0.33214,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48394,0.03894,0.01602],"object_pos_start":[0.48394,0.03894,0.01602],"object_to_goal_dist_end":0.26766,"object_to_goal_dist_start":0.26766,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1105.0,"raw_peak_contact_force":223.15689,"tcp_end":[0.63567,0.1441,0.31923],"tcp_start":[0.63547,0.14426,0.29218],"tcp_to_object_dist_end":0.35499,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.48394,0.03894,0.01602],"object_pos_start":[0.48394,0.03894,0.01602],"object_to_goal_dist_end":0.26766,"object_to_goal_dist_start":0.26766,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":80.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.638,0.14581,0.31436],"tcp_start":[0.63567,0.1441,0.31923],"tcp_to_object_dist_end":0.35236,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```