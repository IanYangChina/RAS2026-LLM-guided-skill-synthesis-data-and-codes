## Search State

- **Seed**: 2
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | -0.3645 | 0.13 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | -0.2398 | 0.16 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | -0.3479 | 0.13 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | -0.3633 | 0.16 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | -0.2170 | 0.14 | ❌ rejected |

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

## Current Skill (Q=-0.364) — your mutation base

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

- **Composite score**: -0.364
- **task_score** (E): 0.131
- **fitness_score**: 0.166  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.780

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.00 | 1.00 | 0.1765 |
| descend_grasp | 1.00 | 1.00 | 0.0002 |
| grasp_action | 1.00 | 1.00 | 0.0000 |
| lift_object | 0.67 | 1.00 | 0.0777 |
| approach_goal | 0.00 | 1.00 | 0.1997 |
| descend_place | 1.00 | 1.00 | 0.0004 |
| release_object | 1.00 | 1.00 | 0.0210 |
| retract_after_place | 0.00 | 1.00 | 0.1272 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.418, 0.009, 0.149) | (0.493, -0.015, 0.030)→(0.454, -0.013, 0.016) | 0.279→0.306 | 1.00 / 5.000 | 271.777 | 1424.141 |
| descend_grasp | descend | 1.00 / force_exceeded | (0.418, 0.009, 0.149)→(0.418, 0.009, 0.149) | (0.454, -0.013, 0.016)→(0.454, -0.013, 0.016) | 0.306→0.306 | 1.00 / 5.000 | 635.116 | 447.436 |
| grasp_action | grasp | 1.00 / step_budget | (0.418, 0.009, 0.148)→(0.418, 0.009, 0.148) | (0.454, -0.013, 0.016)→(0.454, -0.013, 0.016) | 0.306→0.306 | 1.00 / 9.000 | 67.777 | 276.642 |
| lift_object | lift | 0.67 / step_budget | (0.446, -0.010, 0.230)→(0.429, 0.055, 0.267) | (0.454, -0.013, 0.016)→(0.454, -0.013, 0.016) | 0.306→0.306 | 1.00 / 8.333 | 65.292 | 312.422 |
| approach_goal | approach | 0.00 / step_budget | (0.429, 0.055, 0.267)→(0.563, 0.087, 0.251) | (0.454, -0.013, 0.016)→(0.454, -0.013, 0.016) | 0.306→0.306 | 1.00 / 8.667 | 3656.537 | 1667.743 |
| descend_place | descend | 1.00 / force_exceeded | (0.563, 0.087, 0.251)→(0.563, 0.087, 0.251) | (0.454, -0.013, 0.016)→(0.454, -0.013, 0.016) | 0.306→0.306 | 1.00 / 9.000 | 94351.931 | 498.654 |
| release_object | release | 1.00 / step_budget | (0.563, 0.087, 0.251)→(0.562, 0.087, 0.271) | (0.454, -0.013, 0.016)→(0.454, -0.013, 0.016) | 0.306→0.306 | 1.00 / 4.000 | 0.123 | 290.160 |
| retract_after_place | retract | 0.00 / step_budget | (0.562, 0.087, 0.271)→(0.584, 0.195, 0.249) | (0.454, -0.013, 0.016)→(0.454, -0.013, 0.016) | 0.306→0.306 | 1.00 / 5.333 | 373.184 | 644.849 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.111
- phase_score: 0.076
- phase_breakdown.grasp_contact_score: 0.086
- phase_breakdown.approach_object_score: 0.249
- phase_breakdown.place_goal_score: 0.000
- grasp_place_fitness: 0.169

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.169
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.162
- **Median Q (composite search score)**: -0.364
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.310


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":12.0,"average_failure_rate":0.11765,"average_mean_iterations":28.47059,"average_solve_count":102.0,"average_success_count":90.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.place_approach_z":0.06427,"approach_goal.place_arc_height":0.13305,"approach_goal.place_transport_speed":0.23593,"approach_object.approach_arc_height":0.16728,"approach_object.approach_offset_z":0.17991,"approach_object.approach_speed":0.1898,"descend_grasp.descend_force_thresh":13.49066,"descend_place.place_force_thresh":12.72675,"lift_object.lift_height":0.17841,"lift_object.lift_speed":0.1573,"release_object.release_duration":1.38811,"retract_after_place.retract_speed":0.2166},"optimized_scores":{"best_composite_score":-0.36849,"best_fitness_score":0.16151,"best_task_score":0.12122},"replay_outcomes":[{"contacts":{"omitted_contact_groups":12,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":618.0,"contact_point_centroid":[0.57732,0.00298,-0.00035],"force_p95":507.86488,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1615.35119,"mean_force":260.94769,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.35988,-0.00187,0.16155]},{"body_a":"world","body_b":"link6","contact_count":852.0,"contact_point_centroid":[0.63427,0.00306,-0.00046],"force_p95":219.15494,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1444.42125,"mean_force":208.26498,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39136,0.00185,0.11819]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.66055,0.11299,-0.00016],"force_p95":1261.2601,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1261.2601,"mean_force":1261.2601,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.45649,0.0865,0.17926]},{"body_a":"link5","body_b":"hand","contact_count":18.0,"contact_point_centroid":[0.52874,0.0416,0.17899],"force_p95":872.69894,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":925.37768,"mean_force":721.63543,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.47628,0.11578,0.18601]},{"body_a":"world","body_b":"link6","contact_count":67.0,"contact_point_centroid":[0.66403,0.10595,-0.00034],"force_p95":675.38093,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":827.62262,"mean_force":511.55058,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.46075,0.08752,0.18919]},{"body_a":"world","body_b":"link6","contact_count":123.0,"contact_point_centroid":[0.66108,0.11403,-7e-05],"force_p95":182.40628,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":519.13678,"mean_force":70.72257,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.45611,0.08721,0.17831]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.63054,-0.00483,-0.00013],"force_p95":79.20745,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":328.34686,"mean_force":73.0336,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.40058,-0.00625,0.14708]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.62999,-0.00505,-0.00022],"force_p95":309.17343,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":309.17343,"mean_force":309.17343,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.40026,-0.00649,0.14727]},{"body_a":"world","body_b":"link6","contact_count":8.0,"contact_point_centroid":[0.6307,-0.00489,-0.00011],"force_p95":152.94992,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":158.27975,"mean_force":113.94951,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.40076,-0.00632,0.14716]},{"body_a":"left_finger","body_b":"link5","contact_count":100.0,"contact_point_centroid":[0.48216,0.06161,0.19619],"force_p95":12.37654,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":13.75273,"mean_force":6.49483,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.47267,0.10467,0.18604]},{"body_a":"grasp_target","body_b":"hand","contact_count":42.0,"contact_point_centroid":[0.4557,-0.01042,0.03811],"force_p95":3.56143,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.95182,"mean_force":1.62618,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38435,0.00416,0.05002]},{"body_a":"world","body_b":"grasp_target","contact_count":3790.0,"contact_point_centroid":[0.44081,-0.01875,-0.00214],"force_p95":0.13778,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.32848,"mean_force":0.13913,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40366,0.00199,0.12868]},{"body_a":"grasp_target","body_b":"link7","contact_count":27.0,"contact_point_centroid":[0.48241,-0.00211,0.01127],"force_p95":0.53904,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.57553,"mean_force":0.23194,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37436,0.0041,0.0497]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.4354,-0.0182,-0.00202],"force_p95":0.15678,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21787,"mean_force":0.12479,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.37719,0.01523,0.19028]},{"body_a":"grasp_target","body_b":"link7","contact_count":176.0,"contact_point_centroid":[0.4654,-0.01526,0.03505],"force_p95":0.18898,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2103,"mean_force":0.0919,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.33265,-0.0185,0.13163]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.43586,-0.01853,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.40026,-0.00649,0.14727]}],"total_contact_groups":28},"final_pose_error":0.18564,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.43517,-0.01799,0.01602],"final_tcp_position":[0.47986,0.12325,0.18902],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":272727.97089,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.43586,-0.01853,0.01602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.31639,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":217.72853,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4734.0,"raw_peak_contact_force":1444.42125,"subtask_id":"approach_object","tcp_end":[0.40026,-0.00649,0.14727],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13652,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.43586,-0.01853,0.01602],"object_pos_start":[0.43586,-0.01853,0.01602],"object_to_goal_dist_end":0.31639,"object_to_goal_dist_start":0.31639,"object_z_max":0.01602,"peak_contact_force":309.17343,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":309.17343,"subtask_id":"grasp_contact","tcp_end":[0.40024,-0.00639,0.14734],"tcp_start":[0.40026,-0.00649,0.14727],"tcp_to_object_dist_end":0.1366,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.43586,-0.01853,0.01602],"object_pos_start":[0.43586,-0.01853,0.01602],"object_to_goal_dist_end":0.31639,"object_to_goal_dist_start":0.31639,"object_z_max":0.01602,"peak_contact_force":68.57962,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3512.0,"raw_peak_contact_force":328.34686,"tcp_end":[0.40065,-0.00627,0.14692],"tcp_start":[0.40065,-0.00627,0.14693],"tcp_to_object_dist_end":0.13611,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":159.0,"n_steps_budget":600.0,"object_pos_end":[0.43586,-0.01853,0.01602],"object_pos_start":[0.43586,-0.01853,0.01602],"object_to_goal_dist_end":0.31639,"object_to_goal_dist_start":0.31639,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1308.0,"raw_peak_contact_force":158.27975,"tcp_end":[0.42621,-0.01616,0.17897],"tcp_start":[0.42525,-0.01562,0.1779],"tcp_to_object_dist_end":0.16325,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43517,-0.01799,0.01602],"object_pos_start":[0.43586,-0.01853,0.01602],"object_to_goal_dist_end":0.31652,"object_to_goal_dist_start":0.31639,"object_z_max":0.01603,"peak_contact_force":670.2825,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9029.0,"raw_peak_contact_force":1615.35119,"subtask_id":"place_goal","tcp_end":[0.45649,0.0865,0.17926],"tcp_start":[0.42621,-0.01616,0.17897],"tcp_to_object_dist_end":0.19499,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.43517,-0.01799,0.01602],"object_pos_start":[0.43517,-0.01799,0.01602],"object_to_goal_dist_end":0.31652,"object_to_goal_dist_start":0.31652,"object_z_max":0.01602,"peak_contact_force":272727.97089,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9.0,"raw_peak_contact_force":1261.2601,"tcp_end":[0.4566,0.08661,0.17836],"tcp_start":[0.45649,0.0865,0.17926],"tcp_to_object_dist_end":0.19431,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.43517,-0.01799,0.01602],"object_pos_start":[0.43517,-0.01799,0.01602],"object_to_goal_dist_end":0.31652,"object_to_goal_dist_start":0.31652,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1143.0,"raw_peak_contact_force":519.13678,"tcp_end":[0.45259,0.08626,0.19485],"tcp_start":[0.4566,0.08661,0.17836],"tcp_to_object_dist_end":0.20773,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":125.0,"n_steps_budget":630.0,"object_pos_end":[0.43517,-0.01799,0.01602],"object_pos_start":[0.43517,-0.01799,0.01602],"object_to_goal_dist_end":0.31652,"object_to_goal_dist_start":0.31652,"object_z_max":0.01602,"peak_contact_force":621.65074,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":685.0,"raw_peak_contact_force":925.37768,"tcp_end":[0.47986,0.12325,0.18902],"tcp_start":[0.45259,0.08626,0.19485],"tcp_to_object_dist_end":0.22776,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":11.0,"average_failure_rate":0.10092,"average_mean_iterations":25.46789,"average_solve_count":109.0,"average_success_count":98.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.place_approach_z":0.09196,"approach_goal.place_arc_height":0.134,"approach_goal.place_transport_speed":0.21993,"approach_object.approach_arc_height":0.22996,"approach_object.approach_offset_z":0.16901,"approach_object.approach_speed":0.24694,"descend_grasp.descend_force_thresh":14.87129,"descend_place.place_force_thresh":6.67333,"lift_object.lift_height":0.17708,"lift_object.lift_speed":0.24817,"release_object.release_duration":1.69036,"retract_after_place.retract_speed":0.18985},"optimized_scores":{"best_composite_score":-0.36088,"best_fitness_score":0.16912,"best_task_score":0.11107},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":852.0,"contact_point_centroid":[0.63256,0.00014,-0.00045],"force_p95":229.89222,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1338.77806,"mean_force":211.69341,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38524,-0.00066,0.10788]},{"body_a":"world","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.52416,0.00715,-0.00304],"force_p95":250.39139,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1283.85881,"mean_force":63.87392,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.3724,0.00287,0.04666]},{"body_a":"world","body_b":"link6","contact_count":920.0,"contact_point_centroid":[0.54595,0.02095,-0.00034],"force_p95":676.0097,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1066.3727,"mean_force":343.84045,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.37639,0.01098,0.21441]},{"body_a":"world","body_b":"link5","contact_count":138.0,"contact_point_centroid":[0.5694,0.239,-0.00035],"force_p95":941.32414,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1009.04777,"mean_force":555.02709,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.47893,0.11699,0.24041]},{"body_a":"world","body_b":"link6","contact_count":73.0,"contact_point_centroid":[0.61494,0.13911,-0.00061],"force_p95":773.37021,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":974.138,"mean_force":516.02624,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.44978,0.09102,0.22404]},{"body_a":"link5","body_b":"hand","contact_count":307.0,"contact_point_centroid":[0.46733,0.18619,0.15827],"force_p95":242.82832,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":560.30845,"mean_force":117.7378,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.46501,0.10491,0.23293]},{"body_a":"world","body_b":"link6","contact_count":67.0,"contact_point_centroid":[0.59001,0.09843,-0.00013],"force_p95":198.78451,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":351.21951,"mean_force":85.26466,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.43098,0.07098,0.23351]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.63068,-0.01018,-0.00012],"force_p95":79.17989,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":330.37036,"mean_force":72.27265,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.39102,-0.01113,0.13073]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.63005,-0.01034,-0.0002],"force_p95":310.41902,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":310.41902,"mean_force":310.41902,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.39067,-0.01132,0.13107]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.58919,0.09847,-0.00027],"force_p95":234.5781,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":234.5781,"mean_force":234.5781,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.43111,0.07136,0.23391]},{"body_a":"world","body_b":"link6","contact_count":8.0,"contact_point_centroid":[0.63082,-0.01024,-0.0001],"force_p95":76.71745,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":91.66038,"mean_force":22.29701,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.39115,-0.0112,0.13075]},{"body_a":"grasp_target","body_b":"hand","contact_count":42.0,"contact_point_centroid":[0.43777,-0.01461,0.04146],"force_p95":3.5682,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.82898,"mean_force":1.44251,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38163,0.00292,0.04892]},{"body_a":"world","body_b":"grasp_target","contact_count":3765.0,"contact_point_centroid":[0.42313,-0.02447,-0.00215],"force_p95":0.13823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.37517,"mean_force":0.13974,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39814,-0.00038,0.11962]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.41791,-0.02417,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.39067,-0.01132,0.13107]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.41791,-0.02417,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.39102,-0.01113,0.13073]},{"body_a":"world","body_b":"grasp_target","contact_count":728.0,"contact_point_centroid":[0.41791,-0.02417,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.40097,-0.01689,0.15453]}],"total_contact_groups":25},"final_pose_error":0.14998,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.41791,-0.02417,0.01602],"final_tcp_position":[0.50706,0.13061,0.25055],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1338.77806,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.41791,-0.02417,0.01602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.32964,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":226.44734,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4684.0,"raw_peak_contact_force":1338.77806,"subtask_id":"approach_object","tcp_end":[0.39067,-0.01132,0.13107],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11893,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.41791,-0.02417,0.01602],"object_pos_start":[0.41791,-0.02417,0.01602],"object_to_goal_dist_end":0.32964,"object_to_goal_dist_start":0.32964,"object_z_max":0.01602,"peak_contact_force":873.45957,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":310.41902,"subtask_id":"grasp_contact","tcp_end":[0.39065,-0.01124,0.13113],"tcp_start":[0.39067,-0.01132,0.13107],"tcp_to_object_dist_end":0.119,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.41791,-0.02417,0.01602],"object_pos_start":[0.41791,-0.02417,0.01602],"object_to_goal_dist_end":0.32964,"object_to_goal_dist_start":0.32964,"object_z_max":0.01602,"peak_contact_force":67.51197,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3506.0,"raw_peak_contact_force":330.37036,"tcp_end":[0.39111,-0.01115,0.13055],"tcp_start":[0.39111,-0.01115,0.13055],"tcp_to_object_dist_end":0.11834,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":182.0,"n_steps_budget":600.0,"object_pos_end":[0.41791,-0.02417,0.01602],"object_pos_start":[0.41791,-0.02417,0.01602],"object_to_goal_dist_end":0.32964,"object_to_goal_dist_start":0.32964,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1497.0,"raw_peak_contact_force":91.66038,"tcp_end":[0.41047,-0.02189,0.1765],"tcp_start":[0.40989,-0.02145,0.17503],"tcp_to_object_dist_end":0.16067,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41791,-0.02417,0.01602],"object_pos_start":[0.41791,-0.02417,0.01602],"object_to_goal_dist_end":0.32964,"object_to_goal_dist_start":0.32964,"object_z_max":0.01602,"peak_contact_force":550.18987,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9126.0,"raw_peak_contact_force":1066.3727,"subtask_id":"place_goal","tcp_end":[0.43111,0.07136,0.23391],"tcp_start":[0.41047,-0.02189,0.1765],"tcp_to_object_dist_end":0.23828,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.41791,-0.02417,0.01602],"object_pos_start":[0.41791,-0.02417,0.01602],"object_to_goal_dist_end":0.32964,"object_to_goal_dist_start":0.32964,"object_z_max":0.01602,"peak_contact_force":234.5781,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9.0,"raw_peak_contact_force":234.5781,"tcp_end":[0.43118,0.0713,0.23392],"tcp_start":[0.43111,0.07136,0.23391],"tcp_to_object_dist_end":0.23826,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.41791,-0.02417,0.01602],"object_pos_start":[0.41791,-0.02417,0.01602],"object_to_goal_dist_end":0.32964,"object_to_goal_dist_start":0.32964,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1086.0,"raw_peak_contact_force":351.21951,"tcp_end":[0.43026,0.07077,0.26194],"tcp_start":[0.43118,0.0713,0.23392],"tcp_to_object_dist_end":0.2639,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":282.0,"n_steps_budget":840.0,"object_pos_end":[0.41791,-0.02417,0.01602],"object_pos_start":[0.41791,-0.02417,0.01602],"object_to_goal_dist_end":0.32964,"object_to_goal_dist_start":0.32964,"object_z_max":0.01602,"peak_contact_force":497.77825,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1646.0,"raw_peak_contact_force":1009.04777,"tcp_end":[0.50706,0.13061,0.25055],"tcp_start":[0.43026,0.07077,0.26194],"tcp_to_object_dist_end":0.2948,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":33.0,"average_failure_rate":0.27966,"average_mean_iterations":64.98305,"average_solve_count":118.0,"average_success_count":85.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.place_approach_z":0.07898,"approach_goal.place_arc_height":0.14922,"approach_goal.place_transport_speed":0.26667,"approach_object.approach_arc_height":0.13961,"approach_object.approach_offset_z":0.12068,"approach_object.approach_speed":0.28368,"descend_grasp.descend_force_thresh":8.19708,"descend_place.place_force_thresh":7.48602,"lift_object.lift_height":0.17917,"lift_object.lift_speed":0.09875,"release_object.release_duration":1.57675,"retract_after_place.retract_speed":0.29636},"optimized_scores":{"best_composite_score":-0.36406,"best_fitness_score":0.16594,"best_task_score":0.16217},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":32.0,"contact_point_centroid":[0.66372,0.24042,-0.00968],"force_p95":1813.15154,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2321.50447,"mean_force":384.30097,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.86409,0.17241,0.16705]},{"body_a":"world","body_b":"link6","contact_count":599.0,"contact_point_centroid":[0.65527,0.03654,-0.00047],"force_p95":465.73618,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1489.22292,"mean_force":238.9699,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.42735,0.03299,0.1421]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.67849,0.04225,-0.00013],"force_p95":722.71431,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":722.71431,"mean_force":722.71431,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.46377,0.04441,0.16851]},{"body_a":"link5","body_b":"hand","contact_count":381.0,"contact_point_centroid":[0.53317,0.0302,0.27808],"force_p95":480.53087,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":687.32647,"mean_force":304.41823,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48931,0.05721,0.34611]},{"body_a":"world","body_b":"link6","contact_count":63.0,"contact_point_centroid":[0.69097,0.03328,-8e-05],"force_p95":406.11026,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":433.61851,"mean_force":294.23831,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46795,0.03711,0.16699]},{"body_a":"link5","body_b":"hand","contact_count":9.0,"contact_point_centroid":[0.49873,0.22448,0.36398],"force_p95":192.11018,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":207.69833,"mean_force":134.26817,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.44895,0.20367,0.4487]},{"body_a":"world","body_b":"link6","contact_count":542.0,"contact_point_centroid":[0.67993,0.04214,-0.00012],"force_p95":71.6859,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":171.20922,"mean_force":69.08371,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46358,0.04439,0.16643]},{"body_a":"grasp_target","body_b":"link7","contact_count":146.0,"contact_point_centroid":[0.519,0.00851,0.03402],"force_p95":3.32813,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.86931,"mean_force":0.84194,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39937,0.02397,0.08919]},{"body_a":"grasp_target","body_b":"hand","contact_count":104.0,"contact_point_centroid":[0.50074,-0.00484,0.04602],"force_p95":2.66971,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.3922,"mean_force":1.02612,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39644,0.02331,0.07976]},{"body_a":"world","body_b":"grasp_target","contact_count":2627.0,"contact_point_centroid":[0.51531,0.00258,-0.00225],"force_p95":0.33631,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.18901,"mean_force":0.16333,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.44337,0.03105,0.15752]},{"body_a":"grasp_target","body_b":"link6","contact_count":92.0,"contact_point_centroid":[0.54772,0.02336,0.0245],"force_p95":0.74596,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.01203,"mean_force":0.45093,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.394,0.02347,0.08456]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.50753,0.0026,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.46377,0.04441,0.16851]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.50753,0.0026,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46358,0.04438,0.16645]},{"body_a":"world","body_b":"grasp_target","contact_count":1932.0,"contact_point_centroid":[0.50753,0.0026,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48516,0.05278,0.30843]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50753,0.0026,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50638,0.06064,0.66898]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.50753,0.0026,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.80185,0.10203,0.33946]}],"total_contact_groups":25},"final_pose_error":0.21147,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.50753,0.0026,0.01602],"final_tcp_position":[0.76606,0.33242,0.30841],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":10093.24417,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":723.0,"n_steps_budget":1000.0,"object_pos_end":[0.50753,0.0026,0.01602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.27287,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":371.1545,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3590.0,"raw_peak_contact_force":1489.22292,"subtask_id":"approach_object","tcp_end":[0.46377,0.04441,0.16851],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16407,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50753,0.0026,0.01602],"object_pos_start":[0.50753,0.0026,0.01602],"object_to_goal_dist_end":0.27287,"object_to_goal_dist_start":0.27287,"object_z_max":0.01602,"peak_contact_force":722.71431,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":722.71431,"subtask_id":"grasp_contact","tcp_end":[0.46381,0.04435,0.16823],"tcp_start":[0.46377,0.04441,0.16851],"tcp_to_object_dist_end":0.16378,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50753,0.0026,0.01602],"object_pos_start":[0.50753,0.0026,0.01602],"object_to_goal_dist_end":0.27287,"object_to_goal_dist_start":0.27287,"object_z_max":0.01602,"peak_contact_force":67.23856,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3525.0,"raw_peak_contact_force":171.20922,"tcp_end":[0.46357,0.0444,0.16632],"tcp_start":[0.46357,0.04439,0.16632],"tcp_to_object_dist_end":0.16207,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":483.0,"n_steps_budget":600.0,"object_pos_end":[0.50753,0.0026,0.01602],"object_pos_start":[0.50753,0.0026,0.01602],"object_to_goal_dist_end":0.27287,"object_to_goal_dist_start":0.27287,"object_z_max":0.01602,"peak_contact_force":195.63126,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4477.0,"raw_peak_contact_force":687.32647,"tcp_end":[0.44982,0.20167,0.4441],"tcp_start":[0.50288,0.00604,0.33571],"tcp_to_object_dist_end":0.47562,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50753,0.0026,0.01602],"object_pos_start":[0.50753,0.0026,0.01602],"object_to_goal_dist_end":0.27287,"object_to_goal_dist_start":0.27287,"object_z_max":0.01602,"peak_contact_force":9749.13835,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8485.0,"raw_peak_contact_force":2321.50447,"subtask_id":"place_goal","tcp_end":[0.80185,0.10203,0.33946],"tcp_start":[0.44982,0.20167,0.4441],"tcp_to_object_dist_end":0.44847,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50753,0.0026,0.01602],"object_pos_start":[0.50753,0.0026,0.01602],"object_to_goal_dist_end":0.27287,"object_to_goal_dist_start":0.27287,"object_z_max":0.01602,"peak_contact_force":10093.24417,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.80182,0.10206,0.3394],"tcp_start":[0.80185,0.10203,0.33946],"tcp_to_object_dist_end":0.44841,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50753,0.0026,0.01602],"object_pos_start":[0.50753,0.0026,0.01602],"object_to_goal_dist_end":0.27287,"object_to_goal_dist_start":0.27287,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1029.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.80431,0.10353,0.35711],"tcp_start":[0.80182,0.10206,0.3394],"tcp_to_object_dist_end":0.46326,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":426.0,"n_steps_budget":600.0,"object_pos_end":[0.50753,0.0026,0.01602],"object_pos_start":[0.50753,0.0026,0.01602],"object_to_goal_dist_end":0.27287,"object_to_goal_dist_start":0.27287,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1704.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.76606,0.33242,0.30841],"tcp_start":[0.80431,0.10353,0.35711],"tcp_to_object_dist_end":0.51099,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```