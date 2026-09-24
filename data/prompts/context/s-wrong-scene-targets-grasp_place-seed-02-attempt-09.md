## Search State

- **Seed**: 2
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | lift → approach → descend → grasp → lift → approach | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 10 | -0.3833 | 0.16 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 10 | -0.2313 | 0.13 | ❌ rejected |
| 7 | lift → approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 12 | -0.3585 | 0.20 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | -0.3645 | 0.13 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | -0.2398 | 0.16 | ❌ rejected |

**Proposal policy**: task_score is 0.16 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.383) — your mutation base

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

- **Composite score**: -0.383
- **task_score** (E): 0.157
- **fitness_score**: 0.237  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.620

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| raise_tcp | 1.00 | 1.00 | 0.3582 |
| approach_object | 0.00 | 1.00 | 0.5588 |
| descend_to_object | 0.67 | 1.00 | 0.0362 |
| grasp_action | 1.00 | 1.00 | 0.0000 |
| lift_object | 0.33 | 1.00 | 0.0064 |
| transport_to_goal | 0.00 | 1.00 | 0.1076 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| raise_tcp | lift | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.503, -0.000, 0.659) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 167.515 | 0.138 |
| approach_object | approach | 0.00 / step_budget | (0.503, -0.000, 0.659)→(0.471, -0.027, 0.104) | (0.493, -0.015, 0.026)→(0.485, -0.007, 0.022) | 0.281→0.280 | 1.00 / 5.333 | 56050.943 | 1578.236 |
| descend_to_object | descend | 0.67 / step_budget | (0.471, -0.027, 0.104)→(0.475, -0.009, 0.084) | (0.485, -0.007, 0.022)→(0.485, -0.002, 0.019) | 0.280→0.278 | 1.00 / 5.667 | 105.198 | 197.795 |
| grasp_action | grasp | 1.00 / step_budget | (0.475, -0.010, 0.084)→(0.475, -0.010, 0.084) | (0.485, -0.002, 0.019)→(0.484, -0.001, 0.019) | 0.278→0.278 | 1.00 / 9.667 | 495.945 | 136.794 |
| lift_object | lift | 0.33 / step_budget | (0.477, -0.011, 0.099)→(0.479, -0.015, 0.104) | (0.484, -0.001, 0.019)→(0.484, -0.001, 0.019) | 0.278→0.278 | 1.00 / 9.000 | 3279.887 | 129.512 |
| transport_to_goal | approach | 0.00 / step_budget | (0.479, -0.015, 0.104)→(0.511, 0.007, 0.202) | (0.484, -0.001, 0.019)→(0.484, -0.001, 0.019) | 0.278→0.278 | 1.00 / 8.667 | 23.478 | 127.716 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.146
- phase_score: 0.338
- phase_breakdown.grasp_contact_score: 1.000
- phase_breakdown.approach_object_score: 0.191
- phase_breakdown.place_goal_score: 0.000
- grasp_place_fitness: 0.256

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.256
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.164
- **Median Q (composite search score)**: -0.386
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.345


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":17.0,"average_failure_rate":0.09497,"average_mean_iterations":23.94413,"average_solve_count":179.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_arc_height":0.11654,"approach_object.approach_offset_z":0.2436,"approach_object.approach_speed":0.11903,"descend_to_object.descend_speed":0.05122,"lift_object.lift_height":0.10458,"lift_object.lift_speed":0.12235,"raise_tcp.raise_height":0.39978,"raise_tcp.raise_speed":0.16432,"transport_to_goal.transport_arc_height":0.11224,"transport_to_goal.transport_speed":0.2087},"optimized_scores":{"best_composite_score":-0.36385,"best_fitness_score":0.25615,"best_task_score":0.14623},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":27.0,"contact_point_centroid":[0.6958,0.00206,-0.00649],"force_p95":1261.068,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1562.62135,"mean_force":327.45716,"phase_index":1.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.44936,0.00321,0.1047]},{"body_a":"link5","body_b":"hand","contact_count":566.0,"contact_point_centroid":[0.55577,-9e-05,0.18537],"force_p95":168.64427,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":300.70645,"mean_force":104.60473,"phase_index":1.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4636,-0.05739,0.13266]},{"body_a":"world","body_b":"link6","contact_count":68.0,"contact_point_centroid":[0.71346,-0.09851,-0.00039],"force_p95":226.78084,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":227.5868,"mean_force":148.30244,"phase_index":2.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.47147,-0.03572,0.06942]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.71983,-0.09658,-9e-05],"force_p95":62.6898,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":177.47623,"mean_force":49.90345,"phase_index":3.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.47212,-0.03401,0.07056]},{"body_a":"world","body_b":"hand","contact_count":66.0,"contact_point_centroid":[0.52578,-0.12783,-0.0004],"force_p95":118.49279,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":160.25783,"mean_force":74.6016,"phase_index":2.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.47144,-0.03599,0.06917]},{"body_a":"world","body_b":"hand","contact_count":514.0,"contact_point_centroid":[0.52711,-0.12496,-5e-05],"force_p95":21.53162,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":91.55715,"mean_force":21.24422,"phase_index":3.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.47213,-0.03401,0.07053]},{"body_a":"world","body_b":"hand","contact_count":4.0,"contact_point_centroid":[0.52711,-0.12499,-4e-05],"force_p95":64.25662,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.0294,"mean_force":34.46798,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47212,-0.03403,0.07053]},{"body_a":"link5","body_b":"hand","contact_count":13.0,"contact_point_centroid":[0.57576,-0.04298,0.19261],"force_p95":36.07657,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":50.38475,"mean_force":8.36978,"phase_index":2.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.46583,-0.08872,0.13496]},{"body_a":"world","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.71984,-0.0965,-8e-05],"force_p95":35.98954,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":44.98693,"mean_force":8.99739,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47211,-0.034,0.07057]},{"body_a":"grasp_target","body_b":"hand","contact_count":9.0,"contact_point_centroid":[0.4954,-0.03996,0.05526],"force_p95":0.24407,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30378,"mean_force":0.10347,"phase_index":1.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.44735,0.0037,0.09863]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47613,-0.02013,-0.00199],"force_p95":0.12298,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20384,"mean_force":0.12262,"phase_index":1.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47052,-0.05059,0.18153]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.47616,-0.02015,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"raise_tcp","phase_type":"lift","tcp_position_centroid":[0.49978,-4e-05,0.47533]},{"body_a":"world","body_b":"grasp_target","contact_count":1752.0,"contact_point_centroid":[0.47612,-0.02012,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.46971,-0.05788,0.09681]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.47612,-0.02012,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.47212,-0.03401,0.07056]},{"body_a":"world","body_b":"grasp_target","contact_count":708.0,"contact_point_centroid":[0.47612,-0.02012,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47286,-0.02693,0.0922]},{"body_a":"world","body_b":"grasp_target","contact_count":2176.0,"contact_point_centroid":[0.47612,-0.02012,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48528,-0.00849,0.18698]}],"total_contact_groups":19},"final_pose_error":0.182,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.47612,-0.02012,0.02602],"final_tcp_position":[0.51634,0.02224,0.25351],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":9749.27016,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":502.30073,"phase_name":"raise_tcp","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.50288,-7e-05,0.6571],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.63196,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47612,-0.02012,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02604,"peak_contact_force":82.52249,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4602.0,"raw_peak_contact_force":1562.62135,"subtask_id":"approach_object","tcp_end":[0.46586,-0.08934,0.1359],"tcp_start":[0.50288,-7e-05,0.6571],"tcp_to_object_dist_end":0.13027,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":438.0,"n_steps_budget":1000.0,"object_pos_end":[0.47612,-0.02012,0.02602],"object_pos_start":[0.47612,-0.02012,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":128.65746,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1899.0,"raw_peak_contact_force":227.5868,"subtask_id":"grasp_contact","tcp_end":[0.47195,-0.03415,0.07097],"tcp_start":[0.46586,-0.08934,0.1359],"tcp_to_object_dist_end":0.04728,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.47612,-0.02012,0.02602],"object_pos_start":[0.47612,-0.02012,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":1366.84211,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":4040.0,"raw_peak_contact_force":177.47623,"tcp_end":[0.47212,-0.03405,0.07049],"tcp_start":[0.47212,-0.03405,0.07049],"tcp_to_object_dist_end":0.04677,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":177.0,"n_steps_budget":600.0,"object_pos_end":[0.47612,-0.02012,0.02602],"object_pos_start":[0.47612,-0.02012,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":9749.27016,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1503.0,"raw_peak_contact_force":69.0294,"tcp_end":[0.47293,-0.02179,0.11208],"tcp_start":[0.47339,-0.02198,0.1111],"tcp_to_object_dist_end":0.08614,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":544.0,"n_steps_budget":1000.0,"object_pos_end":[0.47612,-0.02012,0.02602],"object_pos_start":[0.47612,-0.02012,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4566.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.51634,0.02224,0.25351],"tcp_start":[0.47293,-0.02179,0.11208],"tcp_to_object_dist_end":0.23487,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":22.0,"average_failure_rate":0.15827,"average_mean_iterations":36.82734,"average_solve_count":139.0,"average_success_count":117.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_arc_height":0.0703,"approach_object.approach_offset_z":0.22174,"approach_object.approach_speed":0.19604,"descend_to_object.descend_speed":0.02409,"lift_object.lift_height":0.15427,"lift_object.lift_speed":0.10273,"raise_tcp.raise_height":0.37858,"raise_tcp.raise_speed":0.36853,"transport_to_goal.transport_arc_height":0.10006,"transport_to_goal.transport_speed":0.18211},"optimized_scores":{"best_composite_score":-0.38616,"best_fitness_score":0.23384,"best_task_score":0.16072},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":27.0,"contact_point_centroid":[0.69544,0.00158,-0.00668],"force_p95":1265.79724,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1565.71235,"mean_force":332.96179,"phase_index":1.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.44926,0.00246,0.10483]},{"body_a":"link5","body_b":"hand","contact_count":754.0,"contact_point_centroid":[0.53282,0.0448,0.17371],"force_p95":218.01024,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":279.4312,"mean_force":126.11896,"phase_index":1.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.46814,-0.01441,0.10407]},{"body_a":"world","body_b":"hand","contact_count":410.0,"contact_point_centroid":[0.52989,-0.06247,-0.00014],"force_p95":135.15886,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":212.23716,"mean_force":90.24234,"phase_index":1.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47245,-0.01506,0.08982]},{"body_a":"link5","body_b":"hand","contact_count":351.0,"contact_point_centroid":[0.52219,0.0804,0.19833],"force_p95":175.5114,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":175.89193,"mean_force":106.74128,"phase_index":5.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.494,-0.00408,0.13179]},{"body_a":"link5","body_b":"hand","contact_count":907.0,"contact_point_centroid":[0.51549,0.07022,0.16928],"force_p95":106.12537,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":148.09647,"mean_force":75.69799,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47816,6e-05,0.09232]},{"body_a":"world","body_b":"hand","contact_count":983.0,"contact_point_centroid":[0.53861,-0.02197,-0.00015],"force_p95":86.79835,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":142.68242,"mean_force":75.77295,"phase_index":2.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.47407,0.02035,0.08758]},{"body_a":"link5","body_b":"hand","contact_count":445.0,"contact_point_centroid":[0.51673,0.08409,0.17178],"force_p95":78.56576,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":140.57766,"mean_force":18.17176,"phase_index":2.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.47351,0.0233,0.08787]},{"body_a":"world","body_b":"hand","contact_count":167.0,"contact_point_centroid":[0.53954,-0.03024,-1e-05],"force_p95":53.22218,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":70.1675,"mean_force":32.45283,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47482,0.01215,0.08769]},{"body_a":"world","body_b":"hand","contact_count":550.0,"contact_point_centroid":[0.53914,-0.02739,-0.00011],"force_p95":58.65012,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":60.36616,"mean_force":47.89227,"phase_index":3.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.47451,0.01555,0.08729]},{"body_a":"world","body_b":"grasp_target","contact_count":3704.0,"contact_point_centroid":[0.45854,-0.02485,-0.00236],"force_p95":0.35111,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.7203,"mean_force":0.14762,"phase_index":1.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47287,-0.0125,0.16493]},{"body_a":"world","body_b":"grasp_target","contact_count":3965.0,"contact_point_centroid":[0.45823,0.01814,-0.00203],"force_p95":0.12307,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56619,"mean_force":0.12468,"phase_index":2.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.47406,0.0204,0.08759]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1721.0,"contact_point_centroid":[0.473,-0.02321,0.05345],"force_p95":0.1413,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33476,"mean_force":0.03848,"phase_index":1.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47262,-0.00333,0.08917]},{"body_a":"world","body_b":"grasp_target","contact_count":2404.0,"contact_point_centroid":[0.45856,-0.02632,-0.00194],"force_p95":0.13067,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"raise_tcp","phase_type":"lift","tcp_position_centroid":[0.50051,-4e-05,0.47242]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.45823,0.01843,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.47451,0.01555,0.08729]},{"body_a":"world","body_b":"grasp_target","contact_count":3640.0,"contact_point_centroid":[0.45823,0.01843,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47814,0.00011,0.0923]},{"body_a":"world","body_b":"grasp_target","contact_count":1516.0,"contact_point_centroid":[0.45823,0.01843,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49473,-0.00282,0.13407]}],"total_contact_groups":19},"final_pose_error":0.23036,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.45823,0.01843,0.01602],"final_tcp_position":[0.50522,0.01625,0.16887],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273005.67396,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":602.0,"n_steps_budget":660.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"raise_tcp","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":2404.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.50408,-7e-05,0.65378],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.62996,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46049,0.00753,0.0225],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.27829,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":118.57514,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6616.0,"raw_peak_contact_force":1565.71235,"subtask_id":"approach_object","tcp_end":[0.47244,0.02727,0.08846],"tcp_start":[0.50408,-7e-05,0.65378],"tcp_to_object_dist_end":0.06988,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45823,0.01843,0.01602],"object_pos_start":[0.46049,0.00753,0.0225],"object_to_goal_dist_end":0.27421,"object_to_goal_dist_start":0.27829,"object_z_max":0.0225,"peak_contact_force":86.78105,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5393.0,"raw_peak_contact_force":142.68242,"subtask_id":"grasp_contact","tcp_end":[0.47503,0.01565,0.08709],"tcp_start":[0.47244,0.02727,0.08846],"tcp_to_object_dist_end":0.07308,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.45823,0.01843,0.01602],"object_pos_start":[0.45823,0.01843,0.01602],"object_to_goal_dist_end":0.27421,"object_to_goal_dist_start":0.27421,"object_z_max":0.01602,"peak_contact_force":46.05479,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3522.0,"raw_peak_contact_force":60.36616,"tcp_end":[0.47438,0.01539,0.08734],"tcp_start":[0.47439,0.01541,0.08734],"tcp_to_object_dist_end":0.07319,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":910.0,"n_steps_budget":600.0,"object_pos_end":[0.45823,0.01843,0.01602],"object_pos_start":[0.45823,0.01843,0.01602],"object_to_goal_dist_end":0.27421,"object_to_goal_dist_start":0.27421,"object_z_max":0.01602,"peak_contact_force":70.50618,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8672.0,"raw_peak_contact_force":148.09647,"tcp_end":[0.48429,-0.01229,0.10392],"tcp_start":[0.47795,-0.00188,0.09092],"tcp_to_object_dist_end":0.09669,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":379.0,"n_steps_budget":1000.0,"object_pos_end":[0.45823,0.01843,0.01602],"object_pos_start":[0.45823,0.01843,0.01602],"object_to_goal_dist_end":0.27421,"object_to_goal_dist_start":0.27421,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3542.0,"raw_peak_contact_force":175.89193,"subtask_id":"place_goal","tcp_end":[0.50522,0.01625,0.16887],"tcp_start":[0.48429,-0.01229,0.10392],"tcp_to_object_dist_end":0.15992,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":63.0,"average_failure_rate":0.45652,"average_mean_iterations":94.88406,"average_solve_count":138.0,"average_success_count":75.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_arc_height":0.1162,"approach_object.approach_offset_z":0.1837,"approach_object.approach_speed":0.12269,"descend_to_object.descend_speed":0.0999,"lift_object.lift_height":0.17801,"lift_object.lift_speed":0.10606,"raise_tcp.raise_height":0.38497,"raise_tcp.raise_speed":0.24791,"transport_to_goal.transport_arc_height":0.13524,"transport_to_goal.transport_speed":0.2345},"optimized_scores":{"best_composite_score":-0.3998,"best_fitness_score":0.2202,"best_task_score":0.16429},"replay_outcomes":[{"contacts":{"omitted_contact_groups":10,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":28.0,"contact_point_centroid":[0.69353,-0.01831,-0.00745],"force_p95":1278.74092,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1606.37425,"mean_force":326.08138,"phase_index":1.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.44894,-0.00878,0.10618]},{"body_a":"link5","body_b":"hand","contact_count":807.0,"contact_point_centroid":[0.53762,-0.00112,0.18075],"force_p95":192.83948,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":263.13097,"mean_force":137.89396,"phase_index":1.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.46893,-0.04834,0.10733]},{"body_a":"world","body_b":"hand","contact_count":434.0,"contact_point_centroid":[0.52943,-0.10235,-0.00025],"force_p95":135.04686,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":231.83243,"mean_force":110.46127,"phase_index":1.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47457,-0.05637,0.09215]},{"body_a":"world","body_b":"hand","contact_count":82.0,"contact_point_centroid":[0.55408,-0.05674,-0.00019],"force_p95":101.27107,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":223.11646,"mean_force":59.50833,"phase_index":2.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.47753,-0.01091,0.08935]},{"body_a":"link5","body_b":"hand","contact_count":461.0,"contact_point_centroid":[0.52828,0.02721,0.19667],"force_p95":147.51965,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":207.1323,"mean_force":81.68342,"phase_index":5.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48583,-0.03346,0.1144]},{"body_a":"world","body_b":"link7","contact_count":87.0,"contact_point_centroid":[0.60158,-0.03943,-0.00026],"force_p95":100.03372,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":181.30975,"mean_force":80.35798,"phase_index":2.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.47855,-0.01022,0.09175]},{"body_a":"world","body_b":"link7","contact_count":550.0,"contact_point_centroid":[0.60351,-0.03982,-0.00016],"force_p95":74.92045,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":172.53999,"mean_force":73.75515,"phase_index":3.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.47878,-0.00988,0.0948]},{"body_a":"world","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.60329,-0.04013,-0.00015],"force_p95":167.53632,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":171.40996,"mean_force":87.66409,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47869,-0.01006,0.09495]},{"body_a":"world","body_b":"hand","contact_count":34.0,"contact_point_centroid":[0.54722,-0.07724,-5e-05],"force_p95":71.51465,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":132.0873,"mean_force":71.56488,"phase_index":5.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.47438,-0.02993,0.08868]},{"body_a":"link5","body_b":"hand","contact_count":5.0,"contact_point_centroid":[0.52244,0.04068,0.17188],"force_p95":57.29282,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":62.27419,"mean_force":25.74307,"phase_index":2.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.47467,-0.01626,0.08779]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.60331,-0.04018,-6e-05],"force_p95":30.53667,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":30.53667,"mean_force":30.53667,"phase_index":5.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.47876,-0.01009,0.09519]},{"body_a":"grasp_target","body_b":"link7","contact_count":100.0,"contact_point_centroid":[0.55587,-0.01827,0.06048],"force_p95":2.32286,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.133,"mean_force":0.97341,"phase_index":1.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.45451,-0.01239,0.12513]},{"body_a":"grasp_target","body_b":"hand","contact_count":85.0,"contact_point_centroid":[0.54316,-0.02194,0.05889],"force_p95":1.13497,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.11373,"mean_force":0.70268,"phase_index":1.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.456,-0.01277,0.11657]},{"body_a":"world","body_b":"grasp_target","contact_count":3518.0,"contact_point_centroid":[0.52524,-0.00938,-0.00216],"force_p95":0.23569,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.77381,"mean_force":0.14003,"phase_index":1.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47605,-0.04359,0.16383]},{"body_a":"grasp_target","body_b":"hand","contact_count":124.0,"contact_point_centroid":[0.53649,-0.03088,0.03578],"force_p95":0.34897,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.89426,"mean_force":0.30146,"phase_index":2.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.47791,-0.01069,0.0906]},{"body_a":"world","body_b":"grasp_target","contact_count":472.0,"contact_point_centroid":[0.51831,-0.0077,-0.0026],"force_p95":0.34135,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63249,"mean_force":0.18915,"phase_index":2.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.47799,-0.01066,0.09075]}],"total_contact_groups":26},"final_pose_error":0.2254,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.51692,-0.0021,0.01602],"final_tcp_position":[0.51232,-0.01816,0.18319],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":916.0,"n_steps_budget":990.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"raise_tcp","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3660.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.50324,-7e-05,0.66626],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.64155,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51977,-0.00918,0.01612],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.27376,"object_to_goal_dist_start":0.25012,"object_z_max":0.04265,"peak_contact_force":167951.73011,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4972.0,"raw_peak_contact_force":1606.37425,"subtask_id":"approach_object","tcp_end":[0.47454,-0.01806,0.08793],"tcp_start":[0.50324,-7e-05,0.66626],"tcp_to_object_dist_end":0.08533,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":124.0,"n_steps_budget":1000.0,"object_pos_end":[0.52015,-0.00504,0.01482],"object_pos_start":[0.51977,-0.00918,0.01612],"object_to_goal_dist_end":0.27191,"object_to_goal_dist_start":0.27376,"object_z_max":0.01612,"peak_contact_force":100.15672,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":770.0,"raw_peak_contact_force":223.11646,"subtask_id":"grasp_contact","tcp_end":[0.47899,-0.00991,0.09442],"tcp_start":[0.47454,-0.01806,0.08793],"tcp_to_object_dist_end":0.08974,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.51765,-0.00244,0.01513],"object_pos_start":[0.52015,-0.00504,0.01482],"object_to_goal_dist_end":0.27134,"object_to_goal_dist_start":0.27191,"object_z_max":0.0152,"peak_contact_force":74.93777,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":4072.0,"raw_peak_contact_force":172.53999,"tcp_end":[0.47868,-0.01004,0.09486],"tcp_start":[0.47869,-0.01002,0.09486],"tcp_to_object_dist_end":0.08907,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":6.0,"n_steps_budget":630.0,"object_pos_end":[0.5173,-0.00184,0.01521],"object_pos_start":[0.51732,-0.00186,0.0152],"object_to_goal_dist_end":0.2711,"object_to_goal_dist_start":0.27111,"object_z_max":0.01523,"peak_contact_force":19.88553,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":61.0,"raw_peak_contact_force":171.40996,"tcp_end":[0.47876,-0.01009,0.09519],"tcp_start":[0.47869,-0.01009,0.09496],"tcp_to_object_dist_end":0.08916,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":482.0,"n_steps_budget":1000.0,"object_pos_end":[0.51692,-0.0021,0.01602],"object_pos_start":[0.51729,-0.0018,0.01525],"object_to_goal_dist_end":0.27092,"object_to_goal_dist_start":0.27106,"object_z_max":0.01604,"peak_contact_force":70.18754,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4499.0,"raw_peak_contact_force":207.1323,"subtask_id":"place_goal","tcp_end":[0.51232,-0.01816,0.18319],"tcp_start":[0.47876,-0.01009,0.09519],"tcp_to_object_dist_end":0.168,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```