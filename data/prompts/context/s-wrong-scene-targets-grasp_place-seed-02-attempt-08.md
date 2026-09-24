## Search State

- **Seed**: 2
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 10 | -0.2313 | 0.13 | ❌ rejected |
| 7 | lift → approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 12 | -0.3585 | 0.20 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | -0.3645 | 0.13 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | -0.2398 | 0.16 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | -0.3479 | 0.13 | ❌ rejected |

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

## Current Skill (Q=-0.231) — your mutation base

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

- **Composite score**: -0.231
- **task_score** (E): 0.130
- **fitness_score**: 0.133  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.286
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.650

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.00 | 1.00 | 0.1190 |
| descend_grasp | 1.00 | 1.00 | 0.0002 |
| grasp_action | 1.00 | 1.00 | 0.0000 |
| lift_object | 0.67 | 1.00 | 0.0459 |
| transport_to_goal | 0.00 | 1.00 | 0.2800 |
| descend_place | 1.00 | 1.00 | 0.0072 |
| release_object | 1.00 | 1.00 | 0.0305 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.451, 0.031, 0.202) | (0.493, -0.015, 0.030)→(0.451, -0.015, 0.016) | 0.279→0.309 | 1.00 / 5.000 | 326.395 | 1552.149 |
| descend_grasp | descend | 1.00 / force_exceeded | (0.451, 0.031, 0.202)→(0.451, 0.031, 0.202) | (0.451, -0.015, 0.016)→(0.451, -0.015, 0.016) | 0.309→0.309 | 1.00 / 5.000 | 482.439 | 486.670 |
| grasp_action | grasp | 1.00 / step_budget | (0.451, 0.031, 0.201)→(0.451, 0.031, 0.201) | (0.451, -0.015, 0.016)→(0.451, -0.015, 0.016) | 0.309→0.309 | 1.00 / 9.333 | 70.675 | 341.154 |
| lift_object | lift | 0.67 / step_budget | (0.458, -0.002, 0.252)→(0.452, 0.020, 0.289) | (0.451, -0.015, 0.016)→(0.451, -0.015, 0.016) | 0.309→0.309 | 1.00 / 9.000 | 91115.703 | 429.754 |
| transport_to_goal | approach | 0.00 / step_budget | (0.452, 0.020, 0.289)→(0.558, -0.037, 0.221) | (0.451, -0.015, 0.016)→(0.451, -0.013, 0.016) | 0.309→0.308 | 1.00 / 8.333 | 91008.516 | 418.115 |
| descend_place | descend | 1.00 / force_exceeded | (0.558, -0.037, 0.221)→(0.555, -0.039, 0.216) | (0.451, -0.013, 0.016)→(0.451, -0.013, 0.016) | 0.308→0.308 | 1.00 / 8.667 | 185229.033 | 0.123 |
| release_object | release | 1.00 / step_budget | (0.555, -0.039, 0.216)→(0.552, -0.053, 0.235) | (0.451, -0.013, 0.016)→(0.451, -0.013, 0.016) | 0.308→0.308 | 1.00 / 4.000 | 0.123 | 478.262 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.159
- phase_score: 0.317
- phase_breakdown.grasp_contact_score: 1.000
- phase_breakdown.approach_object_score: 0.085
- phase_breakdown.place_goal_score: 0.000
- grasp_place_fitness: 0.154

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.154
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.159
- **Median Q (composite search score)**: -0.238
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.299


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.54878,"average_solve_count":82.0,"average_success_count":82.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_arc_height":0.14688,"approach_object.approach_speed":0.28782,"descend_grasp.descend_force_thresh":5.50571,"descend_place.place_force_thresh":5.81408,"lift_object.lift_height":0.2383,"lift_object.lift_speed":0.17952,"release_object.release_duration":1.41118,"transport_to_goal.transport_arc_height":0.08076,"transport_to_goal.transport_speed":0.23132,"transport_to_goal.transport_z":0.21039},"optimized_scores":{"best_composite_score":-0.23757,"best_fitness_score":0.12672,"best_task_score":0.12244},"replay_outcomes":[{"contacts":{"omitted_contact_groups":5,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":883.0,"contact_point_centroid":[0.63214,0.02929,-0.00045],"force_p95":360.94901,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1477.21997,"mean_force":236.55897,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.41572,0.02689,0.16088]},{"body_a":"world","body_b":"link6","contact_count":546.0,"contact_point_centroid":[0.63829,0.01619,-0.00014],"force_p95":85.31839,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":635.56799,"mean_force":76.43833,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.45314,0.01969,0.2126]},{"body_a":"world","body_b":"link6","contact_count":366.0,"contact_point_centroid":[0.5387,-0.0091,-0.00036],"force_p95":264.58568,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":633.1914,"mean_force":214.21542,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.35744,0.01147,0.21256]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.63737,0.01597,-0.00028],"force_p95":284.58438,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":284.58438,"mean_force":284.58438,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.4532,0.01928,0.21316]},{"body_a":"world","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.6384,0.01613,-0.0001],"force_p95":171.51211,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":176.71561,"mean_force":114.30573,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45311,0.01965,0.21255]},{"body_a":"grasp_target","body_b":"hand","contact_count":38.0,"contact_point_centroid":[0.45648,-0.00894,0.03873],"force_p95":3.64043,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.02891,"mean_force":1.68939,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38552,0.01775,0.05019]},{"body_a":"world","body_b":"grasp_target","contact_count":3940.0,"contact_point_centroid":[0.4402,-0.01854,-0.00213],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.21124,"mean_force":0.13773,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.42533,0.02531,0.16679]},{"body_a":"grasp_target","body_b":"link6","contact_count":90.0,"contact_point_centroid":[0.45438,0.00364,0.04474],"force_p95":0.48677,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.62804,"mean_force":0.21187,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.35931,0.02353,0.24658]},{"body_a":"grasp_target","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.48371,-0.00217,0.01035],"force_p95":0.47056,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.53767,"mean_force":0.20646,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37439,0.01774,0.04954]},{"body_a":"world","body_b":"grasp_target","contact_count":3799.0,"contact_point_centroid":[0.43296,-0.0158,-0.00208],"force_p95":0.18183,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42803,"mean_force":0.13044,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.38063,0.03475,0.2572]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.43534,-0.01829,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.4532,0.01928,0.21316]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.43534,-0.01829,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.45314,0.01969,0.21261]},{"body_a":"world","body_b":"grasp_target","contact_count":568.0,"contact_point_centroid":[0.43534,-0.01829,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44519,0.00393,0.22591]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.43387,-0.01382,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.41829,0.08631,0.28978]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.43387,-0.01382,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.41675,0.08711,0.29302]},{"body_a":"left_finger","body_b":"right_finger","contact_count":753.0,"contact_point_centroid":[0.45473,0.0197,0.21095],"force_p95":0.01306,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01093,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.45315,0.01969,0.21252]}],"total_contact_groups":21},"final_pose_error":0.23902,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.43387,-0.01382,0.01602],"final_tcp_position":[0.41803,0.08656,0.28952],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273025.30304,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43534,-0.01829,0.01602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.31658,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":361.06261,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4903.0,"raw_peak_contact_force":1477.21997,"subtask_id":"approach_object","tcp_end":[0.4532,0.01928,0.21316],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20149,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.43534,-0.01829,0.01602],"object_pos_start":[0.43534,-0.01829,0.01602],"object_to_goal_dist_end":0.31658,"object_to_goal_dist_start":0.31658,"object_z_max":0.01602,"peak_contact_force":284.58438,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":284.58438,"subtask_id":"grasp_contact","tcp_end":[0.45319,0.01939,0.21321],"tcp_start":[0.4532,0.01928,0.21316],"tcp_to_object_dist_end":0.20155,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.43534,-0.01829,0.01602],"object_pos_start":[0.43534,-0.01829,0.01602],"object_to_goal_dist_end":0.31658,"object_to_goal_dist_start":0.31658,"object_z_max":0.01602,"peak_contact_force":71.62717,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3499.0,"raw_peak_contact_force":635.56799,"tcp_end":[0.45315,0.01968,0.21252],"tcp_start":[0.45315,0.01969,0.21252],"tcp_to_object_dist_end":0.20092,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":142.0,"n_steps_budget":600.0,"object_pos_end":[0.43534,-0.01829,0.01602],"object_pos_start":[0.43534,-0.01829,0.01602],"object_to_goal_dist_end":0.31658,"object_to_goal_dist_start":0.31658,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1180.0,"raw_peak_contact_force":176.71561,"tcp_end":[0.43819,-0.01071,0.2387],"tcp_start":[0.43933,-0.00809,0.23768],"tcp_to_object_dist_end":0.22282,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43387,-0.01382,0.01602],"object_pos_start":[0.43534,-0.01829,0.01602],"object_to_goal_dist_end":0.31502,"object_to_goal_dist_start":0.31658,"object_z_max":0.02288,"peak_contact_force":273025.30304,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8535.0,"raw_peak_contact_force":633.1914,"subtask_id":"place_goal","tcp_end":[0.41833,0.08625,0.28985],"tcp_start":[0.43819,-0.01071,0.2387],"tcp_to_object_dist_end":0.29196,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.43387,-0.01382,0.01602],"object_pos_start":[0.43387,-0.01382,0.01602],"object_to_goal_dist_end":0.31502,"object_to_goal_dist_start":0.31502,"object_z_max":0.01602,"peak_contact_force":9748.83148,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":27.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.41803,0.08656,0.28952],"tcp_start":[0.41833,0.08625,0.28985],"tcp_to_object_dist_end":0.29177,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.43387,-0.01382,0.01602],"object_pos_start":[0.43387,-0.01382,0.01602],"object_to_goal_dist_end":0.31502,"object_to_goal_dist_start":0.31502,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.41608,0.08725,0.31296],"tcp_start":[0.41803,0.08656,0.28952],"tcp_to_object_dist_end":0.31417,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.43902,"average_solve_count":82.0,"average_success_count":82.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_arc_height":0.0309,"approach_object.approach_speed":0.26547,"descend_grasp.descend_force_thresh":6.27185,"descend_place.place_force_thresh":7.54967,"lift_object.lift_height":0.19877,"lift_object.lift_speed":0.19229,"release_object.release_duration":1.28125,"transport_to_goal.transport_arc_height":0.12906,"transport_to_goal.transport_speed":0.25016,"transport_to_goal.transport_z":0.17241},"optimized_scores":{"best_composite_score":-0.24623,"best_fitness_score":0.11806,"best_task_score":0.10859},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":879.0,"contact_point_centroid":[0.63262,0.01244,-0.00043],"force_p95":245.62132,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1479.96244,"mean_force":210.17248,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4046,0.01053,0.14217]},{"body_a":"world","body_b":"link6","contact_count":54.0,"contact_point_centroid":[0.60132,0.13209,-0.00103],"force_p95":496.09523,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":532.32385,"mean_force":261.65682,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.42831,0.12572,0.22073]},{"body_a":"world","body_b":"link6","contact_count":50.0,"contact_point_centroid":[0.61406,-0.01751,-4e-05],"force_p95":214.56951,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":363.34159,"mean_force":131.2818,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.43433,-0.00967,0.21728]},{"body_a":"world","body_b":"link6","contact_count":419.0,"contact_point_centroid":[0.57189,-0.01195,-0.00021],"force_p95":248.09366,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":307.46962,"mean_force":216.97427,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.344,-0.00629,0.14799]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.61938,-0.01309,-0.00016],"force_p95":297.65928,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":297.65928,"mean_force":297.65928,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.44097,-0.00484,0.21809]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.61962,-0.01323,-0.00013],"force_p95":77.7623,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":217.63866,"mean_force":74.53047,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.44125,-0.00483,0.21819]},{"body_a":"grasp_target","body_b":"hand","contact_count":39.0,"contact_point_centroid":[0.44587,-0.02312,0.03646],"force_p95":3.54785,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.73256,"mean_force":1.29499,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38556,0.0092,0.04872]},{"body_a":"world","body_b":"grasp_target","contact_count":3951.0,"contact_point_centroid":[0.41968,-0.02596,-0.0021],"force_p95":0.13761,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.33533,"mean_force":0.13588,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.41523,0.01001,0.15003]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.41454,-0.0259,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.44097,-0.00484,0.21809]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.41454,-0.0259,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.44125,-0.00483,0.21819]},{"body_a":"world","body_b":"grasp_target","contact_count":280.0,"contact_point_centroid":[0.41454,-0.0259,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.43416,-0.0098,0.21728]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.41454,-0.0259,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.37488,0.03697,0.21251]},{"body_a":"world","body_b":"grasp_target","contact_count":48.0,"contact_point_centroid":[0.41454,-0.0259,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.43455,0.12479,0.22658]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.41454,-0.0259,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.42808,0.12584,0.22821]},{"body_a":"left_finger","body_b":"right_finger","contact_count":749.0,"contact_point_centroid":[0.44279,-0.00486,0.21652],"force_p95":0.01325,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01098,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.44127,-0.00486,0.21812]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4197.0,"contact_point_centroid":[0.37655,0.03694,0.21083],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01289,"mean_force":0.01061,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.37489,0.03692,0.21239]}],"total_contact_groups":20},"final_pose_error":0.23382,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.41454,-0.0259,0.01602],"final_tcp_position":[0.43055,0.12561,0.22367],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273060.8963,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41454,-0.0259,0.01602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.33303,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":227.07861,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4892.0,"raw_peak_contact_force":1479.96244,"subtask_id":"approach_object","tcp_end":[0.44097,-0.00484,0.21809],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20488,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.41454,-0.0259,0.01602],"object_pos_start":[0.41454,-0.0259,0.01602],"object_to_goal_dist_end":0.33303,"object_to_goal_dist_start":0.33303,"object_z_max":0.01602,"peak_contact_force":750.46009,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":297.65928,"subtask_id":"grasp_contact","tcp_end":[0.44103,-0.00479,0.21822],"tcp_start":[0.44097,-0.00484,0.21809],"tcp_to_object_dist_end":0.20502,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.41454,-0.0259,0.01602],"object_pos_start":[0.41454,-0.0259,0.01602],"object_to_goal_dist_end":0.33303,"object_to_goal_dist_start":0.33303,"object_z_max":0.01602,"peak_contact_force":72.25064,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3499.0,"raw_peak_contact_force":217.63866,"tcp_end":[0.44127,-0.00487,0.21812],"tcp_start":[0.44127,-0.00486,0.21812],"tcp_to_object_dist_end":0.20494,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":70.0,"n_steps_budget":600.0,"object_pos_end":[0.41454,-0.0259,0.01602],"object_pos_start":[0.41454,-0.0259,0.01602],"object_to_goal_dist_end":0.33303,"object_to_goal_dist_start":0.33303,"object_z_max":0.01602,"peak_contact_force":273060.8963,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":626.0,"raw_peak_contact_force":363.34159,"tcp_end":[0.42742,-0.01466,0.21667],"tcp_start":[0.42962,-0.01305,0.21692],"tcp_to_object_dist_end":0.20137,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41454,-0.0259,0.01602],"object_pos_start":[0.41454,-0.0259,0.01602],"object_to_goal_dist_end":0.33303,"object_to_goal_dist_start":0.33303,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8616.0,"raw_peak_contact_force":307.46962,"subtask_id":"place_goal","tcp_end":[0.43631,0.12393,0.22804],"tcp_start":[0.42742,-0.01466,0.21667],"tcp_to_object_dist_end":0.26053,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":12.0,"n_steps_budget":1000.0,"object_pos_end":[0.41454,-0.0259,0.01602],"object_pos_start":[0.41454,-0.0259,0.01602],"object_to_goal_dist_end":0.33303,"object_to_goal_dist_start":0.33303,"object_z_max":0.01602,"peak_contact_force":272939.70619,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":96.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.43055,0.12561,0.22367],"tcp_start":[0.43631,0.12393,0.22804],"tcp_to_object_dist_end":0.25754,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.41454,-0.0259,0.01602],"object_pos_start":[0.41454,-0.0259,0.01602],"object_to_goal_dist_end":0.33303,"object_to_goal_dist_start":0.33303,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1079.0,"raw_peak_contact_force":532.32385,"tcp_end":[0.4276,0.12588,0.24892],"tcp_start":[0.43055,0.12561,0.22367],"tcp_to_object_dist_end":0.2783,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":98.0,"average_failure_rate":0.66216,"average_mean_iterations":136.81081,"average_solve_count":148.0,"average_success_count":50.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_arc_height":0.07655,"approach_object.approach_speed":0.28332,"descend_grasp.descend_force_thresh":7.09147,"descend_place.place_force_thresh":5.04986,"lift_object.lift_height":0.15777,"lift_object.lift_speed":0.18757,"release_object.release_duration":1.57056,"transport_to_goal.transport_arc_height":0.11861,"transport_to_goal.transport_speed":0.30017,"transport_to_goal.transport_z":0.14924},"optimized_scores":{"best_composite_score":-0.21013,"best_fitness_score":0.15415,"best_task_score":0.15888},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":508.0,"contact_point_centroid":[0.63203,0.06538,-0.00054],"force_p95":677.18136,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1699.26593,"mean_force":333.24907,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.42201,0.05419,0.16952]},{"body_a":"world","body_b":"link5","contact_count":20.0,"contact_point_centroid":[0.65412,-0.17073,-0.00332],"force_p95":785.27187,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":902.33935,"mean_force":236.85433,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.80847,-0.35953,0.10767]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.66886,0.08758,-0.00013],"force_p95":877.76727,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":877.76727,"mean_force":877.76727,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.45936,0.07885,0.17475]},{"body_a":"link5","body_b":"hand","contact_count":293.0,"contact_point_centroid":[0.53727,-0.01404,0.2402],"force_p95":545.25122,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":749.20413,"mean_force":334.91215,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49704,0.03167,0.30028]},{"body_a":"world","body_b":"link6","contact_count":91.0,"contact_point_centroid":[0.68669,0.07351,-7e-05],"force_p95":434.9297,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":532.54876,"mean_force":327.51996,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46668,0.06807,0.17162]},{"body_a":"link5","body_b":"hand","contact_count":72.0,"contact_point_centroid":[0.49071,0.212,0.36098],"force_p95":293.81801,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":313.68507,"mean_force":279.34402,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.46374,0.17022,0.43968]},{"body_a":"world","body_b":"link6","contact_count":544.0,"contact_point_centroid":[0.67017,0.08758,-0.00013],"force_p95":73.23038,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":170.25416,"mean_force":69.53124,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.45926,0.07883,0.17304]},{"body_a":"grasp_target","body_b":"link6","contact_count":131.0,"contact_point_centroid":[0.53483,0.023,0.02925],"force_p95":1.29265,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.98527,"mean_force":0.85761,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38724,0.03274,0.10777]},{"body_a":"grasp_target","body_b":"link7","contact_count":205.0,"contact_point_centroid":[0.51782,0.009,0.04441],"force_p95":2.89234,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.89173,"mean_force":0.92109,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39335,0.03503,0.11641]},{"body_a":"grasp_target","body_b":"hand","contact_count":36.0,"contact_point_centroid":[0.49738,-0.01005,0.0299],"force_p95":2.02932,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.4232,"mean_force":0.96306,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38567,0.02793,0.05369]},{"body_a":"world","body_b":"grasp_target","contact_count":2114.0,"contact_point_centroid":[0.518,0.00044,-0.00269],"force_p95":0.52327,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.30701,"mean_force":0.19125,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.44527,0.05137,0.18689]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.5042,0.00023,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.45936,0.07885,0.17475]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.5042,0.00023,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.45926,0.07883,0.17305]},{"body_a":"world","body_b":"grasp_target","contact_count":1640.0,"contact_point_centroid":[0.5042,0.00023,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48864,0.0417,0.26365]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.5042,0.00023,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[-0.01685,0.22593,0.75151]},{"body_a":"world","body_b":"grasp_target","contact_count":8.0,"contact_point_centroid":[0.5042,0.00023,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.81954,-0.3244,0.14341]}],"total_contact_groups":23},"final_pose_error":0.52256,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.5042,0.00023,0.01602],"final_tcp_position":[0.81757,-0.33021,0.13522],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":272998.56185,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":662.0,"n_steps_budget":1000.0,"object_pos_end":[0.5042,0.00023,0.01602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.27594,"object_to_goal_dist_start":0.24751,"object_z_max":0.03373,"peak_contact_force":391.04349,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3013.0,"raw_peak_contact_force":1699.26593,"subtask_id":"approach_object","tcp_end":[0.45936,0.07885,0.17475],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18272,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.5042,0.00023,0.01602],"object_pos_start":[0.5042,0.00023,0.01602],"object_to_goal_dist_end":0.27594,"object_to_goal_dist_start":0.27594,"object_z_max":0.01602,"peak_contact_force":412.27134,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":877.76727,"subtask_id":"grasp_contact","tcp_end":[0.45945,0.07884,0.17452],"tcp_start":[0.45936,0.07885,0.17475],"tcp_to_object_dist_end":0.18249,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.5042,0.00023,0.01602],"object_pos_start":[0.5042,0.00023,0.01602],"object_to_goal_dist_end":0.27594,"object_to_goal_dist_start":0.27594,"object_z_max":0.01602,"peak_contact_force":68.14816,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3498.0,"raw_peak_contact_force":170.25416,"tcp_end":[0.45925,0.07884,0.17294],"tcp_start":[0.45925,0.07884,0.17294],"tcp_to_object_dist_end":0.18117,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":410.0,"n_steps_budget":600.0,"object_pos_end":[0.5042,0.00023,0.01602],"object_pos_start":[0.5042,0.00023,0.01602],"object_to_goal_dist_end":0.27594,"object_to_goal_dist_start":0.27594,"object_z_max":0.01602,"peak_contact_force":286.08968,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3820.0,"raw_peak_contact_force":749.20413,"tcp_end":[0.48904,0.08565,0.41222],"tcp_start":[0.50374,0.01608,0.30114],"tcp_to_object_dist_end":0.40558,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":542.0,"n_steps_budget":1000.0,"object_pos_end":[0.5042,0.00023,0.01602],"object_pos_start":[0.5042,0.00023,0.01602],"object_to_goal_dist_end":0.27594,"object_to_goal_dist_start":0.27594,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4598.0,"raw_peak_contact_force":313.68507,"subtask_id":"place_goal","tcp_end":[0.82016,-0.32253,0.14614],"tcp_start":[0.48904,0.08565,0.41222],"tcp_to_object_dist_end":0.47003,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.5042,0.00023,0.01602],"object_pos_start":[0.5042,0.00023,0.01602],"object_to_goal_dist_end":0.27594,"object_to_goal_dist_start":0.27594,"object_z_max":0.01602,"peak_contact_force":272998.56185,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":16.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.81757,-0.33021,0.13522],"tcp_start":[0.82016,-0.32253,0.14614],"tcp_to_object_dist_end":0.47074,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5042,0.00023,0.01602],"object_pos_start":[0.5042,0.00023,0.01602],"object_to_goal_dist_end":0.27594,"object_to_goal_dist_start":0.27594,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1051.0,"raw_peak_contact_force":902.33935,"tcp_end":[0.81157,-0.37191,0.14176],"tcp_start":[0.81757,-0.33021,0.13522],"tcp_to_object_dist_end":0.49877,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```