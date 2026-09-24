## Search State

- **Seed**: 2
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | -0.4925 | 0.13 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 10 | -0.2139 | 0.16 | ❌ rejected |
| 10 | grasp → lift → approach → descend → release | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | admittance_control | position_control | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 7 | -0.1005 | 0.20 | ❌ rejected |
| 9 | lift → approach → descend → grasp → lift → approach | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 10 | -0.3833 | 0.16 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 10 | -0.2313 | 0.13 | ❌ rejected |

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

## Current Skill (Q=-0.493) — your mutation base

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

- **Composite score**: -0.493
- **task_score** (E): 0.131
- **fitness_score**: 0.157  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.650

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 0.00 | 1.00 | 0.1217 |
| descend_to_grasp | 0.00 | 1.00 | 0.0505 |
| grasp_action | 1.00 | 1.00 | 0.0000 |
| lift_object | 0.67 | 1.00 | 0.0028 |
| transport_to_goal | 0.33 | 1.00 | 0.1154 |
| descend_place | 0.00 | 1.00 | 0.0347 |
| release_object | 1.00 | 1.00 | 0.0228 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.441, 0.017, 0.199) | (0.493, -0.015, 0.030)→(0.453, -0.014, 0.016) | 0.279→0.307 | 1.00 / 5.000 | 391.431 | 1376.666 |
| descend_to_grasp | descend | 0.00 / step_budget | (0.441, 0.017, 0.199)→(0.467, 0.006, 0.159) | (0.453, -0.014, 0.016)→(0.453, -0.014, 0.016) | 0.307→0.307 | 1.00 / 5.667 | 254.949 | 747.208 |
| grasp_action | grasp | 1.00 / step_budget | (0.467, 0.005, 0.158)→(0.467, 0.005, 0.158) | (0.453, -0.014, 0.016)→(0.453, -0.014, 0.016) | 0.307→0.307 | 1.00 / 9.333 | 505.779 | 208.131 |
| lift_object | lift | 0.67 / step_budget | (0.460, 0.001, 0.205)→(0.458, 0.001, 0.206) | (0.453, -0.014, 0.016)→(0.453, -0.014, 0.016) | 0.307→0.307 | 1.00 / 9.000 | 91126.346 | 412.189 |
| transport_to_goal | approach | 0.33 / step_budget | (0.458, 0.001, 0.206)→(0.521, 0.081, 0.209) | (0.453, -0.014, 0.016)→(0.453, -0.013, 0.016) | 0.307→0.306 | 1.00 / 9.667 | 91087.571 | 829.555 |
| descend_place | descend | 0.00 / step_budget | (0.521, 0.081, 0.209)→(0.546, 0.097, 0.201) | (0.453, -0.013, 0.016)→(0.453, -0.013, 0.016) | 0.306→0.306 | 1.00 / 9.333 | 91122.203 | 607.859 |
| release_object | release | 1.00 / step_budget | (0.546, 0.097, 0.201)→(0.549, 0.089, 0.219) | (0.453, -0.013, 0.016)→(0.453, -0.013, 0.016) | 0.306→0.306 | 1.00 / 4.667 | 47.849 | 414.390 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.160
- phase_score: 0.038
- phase_breakdown.grasp_contact_score: 0.059
- phase_breakdown.approach_object_score: 0.104
- phase_breakdown.place_goal_score: 0.000
- grasp_place_fitness: 0.180

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.180
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.160
- **Median Q (composite search score)**: -0.500
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.293


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":24.0,"average_failure_rate":0.18321,"average_mean_iterations":41.05344,"average_solve_count":131.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_arc":0.10704,"approach_above.approach_speed":0.28917,"approach_above.approach_z":0.14115,"descend_place.place_speed":0.13806,"descend_to_grasp.descend_speed":0.14603,"lift_object.lift_height":0.2024,"lift_object.lift_speed":0.11035,"release_object.release_duration":1.60853,"transport_to_goal.transport_arc":0.09493,"transport_to_goal.transport_speed":0.3046},"optimized_scores":{"best_composite_score":-0.50049,"best_fitness_score":0.14951,"best_task_score":0.12085},"replay_outcomes":[{"contacts":{"omitted_contact_groups":13,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":871.0,"contact_point_centroid":[0.63299,0.02256,-0.00043],"force_p95":251.56115,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1326.79029,"mean_force":213.09435,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.40454,0.01978,0.14158]},{"body_a":"world","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.52717,0.01645,-0.00323],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1315.91027,"mean_force":57.21349,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.37621,0.01791,0.04722]},{"body_a":"world","body_b":"link5","contact_count":125.0,"contact_point_centroid":[0.58191,0.26255,-0.00034],"force_p95":614.05794,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1021.49358,"mean_force":458.43932,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.50803,0.07312,0.18853]},{"body_a":"world","body_b":"link6","contact_count":991.0,"contact_point_centroid":[0.64281,-0.0114,-0.00023],"force_p95":488.1478,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":921.61593,"mean_force":352.36927,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4544,-0.00685,0.20482]},{"body_a":"world","body_b":"link6","contact_count":412.0,"contact_point_centroid":[0.56364,0.02122,-0.00029],"force_p95":365.89979,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":791.18131,"mean_force":225.38382,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.39047,-0.03754,0.20714]},{"body_a":"world","body_b":"link6","contact_count":308.0,"contact_point_centroid":[0.66236,0.17306,-3e-05],"force_p95":262.86802,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":648.78954,"mean_force":169.75423,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.48417,0.05057,0.17524]},{"body_a":"world","body_b":"link5","contact_count":74.0,"contact_point_centroid":[0.5912,0.26273,-0.00017],"force_p95":115.31327,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":514.26172,"mean_force":83.14439,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.51246,0.07473,0.18753]},{"body_a":"link5","body_b":"hand","contact_count":50.0,"contact_point_centroid":[0.5264,0.08186,0.14994],"force_p95":252.65121,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":325.71984,"mean_force":117.35466,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46881,-0.01221,0.16883]},{"body_a":"link5","body_b":"hand","contact_count":775.0,"contact_point_centroid":[0.48721,0.15673,0.15239],"force_p95":142.01185,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":297.20174,"mean_force":83.58753,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.48643,0.05339,0.17725]},{"body_a":"world","body_b":"link6","contact_count":8.0,"contact_point_centroid":[0.69121,-0.00155,-8e-05],"force_p95":253.38981,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":272.51043,"mean_force":142.36606,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47006,-0.01543,0.16722]},{"body_a":"link5","body_b":"hand","contact_count":169.0,"contact_point_centroid":[0.48586,0.13909,0.20229],"force_p95":174.33331,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":235.81124,"mean_force":73.68063,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.45668,0.03633,0.19776]},{"body_a":"world","body_b":"link6","contact_count":548.0,"contact_point_centroid":[0.69122,-0.00129,-0.00013],"force_p95":91.81012,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":213.45952,"mean_force":69.43479,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46999,-0.01467,0.16706]},{"body_a":"link5","body_b":"hand","contact_count":579.0,"contact_point_centroid":[0.51479,0.08605,0.14605],"force_p95":99.31936,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":144.5102,"mean_force":23.4599,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.47,-0.01463,0.16712]},{"body_a":"link5","body_b":"hand","contact_count":159.0,"contact_point_centroid":[0.50403,0.17182,0.12653],"force_p95":74.81925,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":74.91872,"mean_force":64.32294,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.51396,0.07252,0.19444]},{"body_a":"link5","body_b":"hand","contact_count":2.0,"contact_point_centroid":[0.51345,0.08614,0.14665],"force_p95":18.30107,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":19.26428,"mean_force":9.63214,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46999,-0.01479,0.16692]},{"body_a":"grasp_target","body_b":"hand","contact_count":40.0,"contact_point_centroid":[0.45387,-0.01824,0.03926],"force_p95":3.62683,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.82174,"mean_force":1.63655,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.3868,0.018,0.04943]}],"total_contact_groups":29},"final_pose_error":0.14754,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.43594,-0.01966,0.01602],"final_tcp_position":[0.5124,0.07487,0.18786],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1366.84211,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43594,-0.01966,0.01602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.31698,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":247.85545,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4888.0,"raw_peak_contact_force":1326.79029,"subtask_id":"approach_object","tcp_end":[0.43753,-0.00252,0.22292],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20762,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43594,-0.01966,0.01602],"object_pos_start":[0.43594,-0.01966,0.01602],"object_to_goal_dist_end":0.31698,"object_to_goal_dist_start":0.31698,"object_z_max":0.01602,"peak_contact_force":287.58665,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5041.0,"raw_peak_contact_force":921.61593,"subtask_id":"grasp_contact","tcp_end":[0.46986,-0.01319,0.1687],"tcp_start":[0.43753,-0.00252,0.22292],"tcp_to_object_dist_end":0.15654,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.43594,-0.01966,0.01602],"object_pos_start":[0.43594,-0.01966,0.01602],"object_to_goal_dist_end":0.31698,"object_to_goal_dist_start":0.31698,"object_z_max":0.01602,"peak_contact_force":1366.84211,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":4119.0,"raw_peak_contact_force":213.45952,"tcp_end":[0.46999,-0.0148,0.16692],"tcp_start":[0.46999,-0.01479,0.16692],"tcp_to_object_dist_end":0.15477,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":167.0,"n_steps_budget":600.0,"object_pos_end":[0.43594,-0.01966,0.01602],"object_pos_start":[0.43594,-0.01966,0.01602],"object_to_goal_dist_end":0.31698,"object_to_goal_dist_start":0.31698,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1400.0,"raw_peak_contact_force":272.51043,"tcp_end":[0.44264,-0.01962,0.20194],"tcp_start":[0.44455,-0.01948,0.20055],"tcp_to_object_dist_end":0.18604,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":12.0,"n_steps":842.0,"n_steps_budget":1000.0,"object_pos_end":[0.43594,-0.01966,0.01602],"object_pos_start":[0.43594,-0.01966,0.01602],"object_to_goal_dist_end":0.31698,"object_to_goal_dist_start":0.31698,"object_z_max":0.01602,"peak_contact_force":209.95684,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7563.0,"raw_peak_contact_force":791.18131,"subtask_id":"place_goal","tcp_end":[0.46399,0.03963,0.18171],"tcp_start":[0.44264,-0.01962,0.20194],"tcp_to_object_dist_end":0.1782,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":500.0,"n_steps_budget":1000.0,"object_pos_end":[0.43594,-0.01966,0.01602],"object_pos_start":[0.43594,-0.01966,0.01602],"object_to_goal_dist_end":0.31698,"object_to_goal_dist_start":0.31698,"object_z_max":0.01602,"peak_contact_force":358.08637,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5395.0,"raw_peak_contact_force":1021.49358,"tcp_end":[0.5124,0.07487,0.18786],"tcp_start":[0.46399,0.03963,0.18171],"tcp_to_object_dist_end":0.21051,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.43594,-0.01966,0.01602],"object_pos_start":[0.43594,-0.01966,0.01602],"object_to_goal_dist_end":0.31698,"object_to_goal_dist_start":0.31698,"object_z_max":0.01602,"peak_contact_force":74.91872,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1253.0,"raw_peak_contact_force":514.26172,"tcp_end":[0.51801,0.06782,0.2101],"tcp_start":[0.5124,0.07487,0.18786],"tcp_to_object_dist_end":0.22816,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":25.0,"average_failure_rate":0.20492,"average_mean_iterations":45.87705,"average_solve_count":122.0,"average_success_count":97.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_arc":0.14426,"approach_above.approach_speed":0.32144,"approach_above.approach_z":0.10536,"descend_place.place_speed":0.18111,"descend_to_grasp.descend_speed":0.18229,"lift_object.lift_height":0.15476,"lift_object.lift_speed":0.12234,"release_object.release_duration":1.33815,"transport_to_goal.transport_arc":0.14748,"transport_to_goal.transport_speed":0.27081},"optimized_scores":{"best_composite_score":-0.50746,"best_fitness_score":0.14254,"best_task_score":0.11244},"replay_outcomes":[{"contacts":{"omitted_contact_groups":8,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":876.0,"contact_point_centroid":[0.63088,0.02605,-0.00042],"force_p95":254.88413,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1315.2288,"mean_force":219.62283,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.4046,0.02335,0.14506]},{"body_a":"world","body_b":"link6","contact_count":641.0,"contact_point_centroid":[0.59937,0.03559,-0.00015],"force_p95":586.94661,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1312.89498,"mean_force":276.12195,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.3834,-0.0196,0.1418]},{"body_a":"world","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.52484,0.01571,-0.00295],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1234.08138,"mean_force":53.65571,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.37408,0.01724,0.04832]},{"body_a":"world","body_b":"link6","contact_count":989.0,"contact_point_centroid":[0.64213,-0.00338,-0.00024],"force_p95":486.43295,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":908.85515,"mean_force":344.79575,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45396,-0.00143,0.20653]},{"body_a":"world","body_b":"link6","contact_count":71.0,"contact_point_centroid":[0.70653,0.13871,-3e-05],"force_p95":282.61092,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":608.00125,"mean_force":113.45036,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.47296,0.04545,0.11531]},{"body_a":"link5","body_b":"hand","contact_count":376.0,"contact_point_centroid":[0.48768,0.17299,0.20374],"force_p95":196.16619,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":491.5517,"mean_force":82.99655,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.4472,0.07497,0.20332]},{"body_a":"world","body_b":"link6","contact_count":91.0,"contact_point_centroid":[0.67579,0.0012,-0.0001],"force_p95":175.16751,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":244.11935,"mean_force":76.16832,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4545,-0.01747,0.16596]},{"body_a":"world","body_b":"link6","contact_count":546.0,"contact_point_centroid":[0.68818,0.00119,-0.00013],"force_p95":75.04236,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":236.63916,"mean_force":67.52815,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46705,-0.01164,0.16723]},{"body_a":"link5","body_b":"hand","contact_count":83.0,"contact_point_centroid":[0.50973,0.15561,0.1328],"force_p95":102.95896,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":115.87354,"mean_force":72.08265,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.47215,0.04301,0.12518]},{"body_a":"link5","body_b":"hand","contact_count":67.0,"contact_point_centroid":[0.52537,0.07786,0.15867],"force_p95":75.8354,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":92.67728,"mean_force":24.84552,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46716,-0.01152,0.1678]},{"body_a":"grasp_target","body_b":"hand","contact_count":39.0,"contact_point_centroid":[0.43958,-0.01505,0.04228],"force_p95":3.3965,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.70359,"mean_force":1.46443,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.385,0.01724,0.04996]},{"body_a":"world","body_b":"grasp_target","contact_count":3924.0,"contact_point_centroid":[0.42243,-0.02427,-0.00212],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.28758,"mean_force":0.13796,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.41548,0.02205,0.15321]},{"body_a":"grasp_target","body_b":"link7","contact_count":108.0,"contact_point_centroid":[0.44464,-0.01047,0.03884],"force_p95":0.37671,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.79129,"mean_force":0.19328,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.34984,-0.0521,0.10062]},{"body_a":"world","body_b":"grasp_target","contact_count":3872.0,"contact_point_centroid":[0.41575,-0.02124,-0.00201],"force_p95":0.14513,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4624,"mean_force":0.12604,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.39579,0.00129,0.17073]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.41744,-0.02395,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45406,-0.0015,0.20628]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.41744,-0.02395,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46705,-0.01163,0.16723]}],"total_contact_groups":24},"final_pose_error":0.22119,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.41635,-0.0201,0.01602],"final_tcp_position":[0.46988,0.05639,0.12019],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":272990.65527,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41744,-0.02395,0.01602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.32979,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":694.97382,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4862.0,"raw_peak_contact_force":1315.2288,"subtask_id":"approach_object","tcp_end":[0.44118,0.00655,0.22243],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20999,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41744,-0.02395,0.01602],"object_pos_start":[0.41744,-0.02395,0.01602],"object_to_goal_dist_end":0.32979,"object_to_goal_dist_start":0.32979,"object_z_max":0.01602,"peak_contact_force":239.74053,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4989.0,"raw_peak_contact_force":908.85515,"subtask_id":"grasp_contact","tcp_end":[0.46704,-0.01043,0.16817],"tcp_start":[0.44118,0.00655,0.22243],"tcp_to_object_dist_end":0.1606,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.41744,-0.02395,0.01602],"object_pos_start":[0.41744,-0.02395,0.01602],"object_to_goal_dist_end":0.32979,"object_to_goal_dist_start":0.32979,"object_z_max":0.01602,"peak_contact_force":65.714,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3589.0,"raw_peak_contact_force":236.63916,"tcp_end":[0.46704,-0.01171,0.16712],"tcp_start":[0.46704,-0.01171,0.16712],"tcp_to_object_dist_end":0.1595,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":131.0,"n_steps_budget":600.0,"object_pos_end":[0.41744,-0.02395,0.01602],"object_pos_start":[0.41744,-0.02395,0.01602],"object_to_goal_dist_end":0.32979,"object_to_goal_dist_start":0.32979,"object_z_max":0.01602,"peak_contact_force":272990.65527,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1183.0,"raw_peak_contact_force":244.11935,"tcp_end":[0.43333,-0.02208,0.16628],"tcp_start":[0.43644,-0.02153,0.1658],"tcp_to_object_dist_end":0.15111,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41635,-0.0201,0.01602],"object_pos_start":[0.41744,-0.02395,0.01602],"object_to_goal_dist_end":0.32781,"object_to_goal_dist_start":0.32979,"object_z_max":0.01834,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9242.0,"raw_peak_contact_force":1312.89498,"subtask_id":"place_goal","tcp_end":[0.46915,0.0586,0.12146],"tcp_start":[0.43333,-0.02208,0.16628],"tcp_to_object_dist_end":0.14178,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.41635,-0.0201,0.01602],"object_pos_start":[0.41635,-0.0201,0.01602],"object_to_goal_dist_end":0.32781,"object_to_goal_dist_start":0.32781,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.46988,0.05639,0.12019],"tcp_start":[0.46915,0.0586,0.12146],"tcp_to_object_dist_end":0.13989,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.41635,-0.0201,0.01602],"object_pos_start":[0.41635,-0.0201,0.01602],"object_to_goal_dist_end":0.32781,"object_to_goal_dist_start":0.32781,"object_z_max":0.01602,"peak_contact_force":68.50553,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1172.0,"raw_peak_contact_force":608.00125,"tcp_end":[0.47368,0.03962,0.12819],"tcp_start":[0.46988,0.05639,0.12019],"tcp_to_object_dist_end":0.13941,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":64.0,"average_failure_rate":0.43243,"average_mean_iterations":90.90541,"average_solve_count":148.0,"average_success_count":84.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_arc":0.14241,"approach_above.approach_speed":0.11739,"approach_above.approach_z":0.13171,"descend_place.place_speed":0.14009,"descend_to_grasp.descend_speed":0.07414,"lift_object.lift_height":0.19874,"lift_object.lift_speed":0.08871,"release_object.release_duration":1.21849,"transport_to_goal.transport_arc":0.12577,"transport_to_goal.transport_speed":0.24294},"optimized_scores":{"best_composite_score":-0.46962,"best_fitness_score":0.18038,"best_task_score":0.16022},"replay_outcomes":[{"contacts":{"omitted_contact_groups":8,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":860.0,"contact_point_centroid":[0.64885,0.03103,-0.00041],"force_p95":436.00888,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1487.97775,"mean_force":244.25223,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.42866,0.02972,0.15342]},{"body_a":"world","body_b":"link6","contact_count":770.0,"contact_point_centroid":[0.6396,0.14541,-0.0003],"force_p95":556.02018,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":801.96226,"mean_force":402.91551,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.6448,0.15419,0.29358]},{"body_a":"link5","body_b":"hand","contact_count":45.0,"contact_point_centroid":[0.53117,-0.0433,0.20303],"force_p95":642.77434,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":719.93813,"mean_force":509.5145,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48947,0.04725,0.21169]},{"body_a":"world","body_b":"link6","contact_count":509.0,"contact_point_centroid":[0.68827,0.04538,-0.00019],"force_p95":289.08618,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":411.1517,"mean_force":249.38387,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45516,0.0457,0.14589]},{"body_a":"world","body_b":"link6","contact_count":19.0,"contact_point_centroid":[0.70811,0.0367,-0.00019],"force_p95":400.98338,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":401.5944,"mean_force":264.98254,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46568,0.04171,0.14114]},{"body_a":"link5","body_b":"hand","contact_count":24.0,"contact_point_centroid":[0.53785,-0.05016,0.2419],"force_p95":379.13067,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":384.58845,"mean_force":312.81218,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49407,0.0385,0.26261]},{"body_a":"world","body_b":"link6","contact_count":541.0,"contact_point_centroid":[0.70447,0.04085,-0.00012],"force_p95":70.36824,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":174.29391,"mean_force":67.03659,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46518,0.04035,0.14035]},{"body_a":"world","body_b":"link6","contact_count":87.0,"contact_point_centroid":[0.66443,0.15362,-0.00013],"force_p95":75.97081,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":120.9063,"mean_force":56.40964,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.65536,0.1593,0.29403]},{"body_a":"grasp_target","body_b":"link7","contact_count":214.0,"contact_point_centroid":[0.52123,0.00874,0.03376],"force_p95":3.32987,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.71128,"mean_force":0.6392,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.3998,0.02036,0.09768]},{"body_a":"grasp_target","body_b":"link6","contact_count":115.0,"contact_point_centroid":[0.54703,0.01699,0.02469],"force_p95":0.85374,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.6917,"mean_force":0.44795,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.39373,0.01948,0.08691]},{"body_a":"grasp_target","body_b":"hand","contact_count":120.0,"contact_point_centroid":[0.50066,-0.00678,0.04675],"force_p95":2.36907,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.39301,"mean_force":0.94723,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.39539,0.01931,0.08169]},{"body_a":"world","body_b":"grasp_target","contact_count":3737.0,"contact_point_centroid":[0.51293,0.00018,-0.0022],"force_p95":0.25462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.64335,"mean_force":0.15305,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.44044,0.02872,0.16396]},{"body_a":"world","body_b":"grasp_target","contact_count":2096.0,"contact_point_centroid":[0.50675,0.00013,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45496,0.0456,0.14596]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.50675,0.00013,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46518,0.04035,0.14036]},{"body_a":"world","body_b":"grasp_target","contact_count":464.0,"contact_point_centroid":[0.50675,0.00013,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47701,0.04493,0.17353]},{"body_a":"world","body_b":"grasp_target","contact_count":1732.0,"contact_point_centroid":[0.50675,0.00013,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53348,0.0879,0.3268]}],"total_contact_groups":24},"final_pose_error":0.08291,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.50675,0.00013,0.01602],"final_tcp_position":[0.65532,0.15978,0.29364],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273052.63327,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50675,0.00013,0.01602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.27468,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":231.46337,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5068.0,"raw_peak_contact_force":1487.97775,"subtask_id":"approach_object","tcp_end":[0.44332,0.04778,0.15081],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15641,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":524.0,"n_steps_budget":1000.0,"object_pos_end":[0.50675,0.00013,0.01602],"object_pos_start":[0.50675,0.00013,0.01602],"object_to_goal_dist_end":0.27468,"object_to_goal_dist_start":0.27468,"object_z_max":0.01602,"peak_contact_force":237.52047,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2605.0,"raw_peak_contact_force":411.1517,"subtask_id":"grasp_contact","tcp_end":[0.4651,0.04023,0.14089],"tcp_start":[0.44332,0.04778,0.15081],"tcp_to_object_dist_end":0.13761,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50675,0.00013,0.01602],"object_pos_start":[0.50675,0.00013,0.01602],"object_to_goal_dist_end":0.27468,"object_to_goal_dist_start":0.27468,"object_z_max":0.01602,"peak_contact_force":84.78081,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3522.0,"raw_peak_contact_force":174.29391,"tcp_end":[0.46518,0.04038,0.14025],"tcp_start":[0.46518,0.04038,0.14025],"tcp_to_object_dist_end":0.13704,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":116.0,"n_steps_budget":690.0,"object_pos_end":[0.50675,0.00013,0.01602],"object_pos_start":[0.50675,0.00013,0.01602],"object_to_goal_dist_end":0.27468,"object_to_goal_dist_start":0.27468,"object_z_max":0.01602,"peak_contact_force":388.25861,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1020.0,"raw_peak_contact_force":719.93813,"tcp_end":[0.49889,0.04399,0.25049],"tcp_start":[0.49833,0.04442,0.24784],"tcp_to_object_dist_end":0.23867,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":433.0,"n_steps_budget":1000.0,"object_pos_end":[0.50675,0.00013,0.01602],"object_pos_start":[0.50675,0.00013,0.01602],"object_to_goal_dist_end":0.27468,"object_to_goal_dist_start":0.27468,"object_z_max":0.01602,"peak_contact_force":273052.63327,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3648.0,"raw_peak_contact_force":384.58845,"subtask_id":"place_goal","tcp_end":[0.63094,0.14443,0.32325],"tcp_start":[0.49889,0.04399,0.25049],"tcp_to_object_dist_end":0.36144,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":847.0,"n_steps_budget":1000.0,"object_pos_end":[0.50675,0.00013,0.01602],"object_pos_start":[0.50675,0.00013,0.01602],"object_to_goal_dist_end":0.27468,"object_to_goal_dist_start":0.27468,"object_z_max":0.01602,"peak_contact_force":273008.39959,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7810.0,"raw_peak_contact_force":801.96226,"tcp_end":[0.65532,0.15978,0.29364],"tcp_start":[0.63094,0.14443,0.32325],"tcp_to_object_dist_end":0.35303,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50675,0.00013,0.01602],"object_pos_start":[0.50675,0.00013,0.01602],"object_to_goal_dist_end":0.27468,"object_to_goal_dist_start":0.27468,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1111.0,"raw_peak_contact_force":120.9063,"tcp_end":[0.65554,0.15959,0.31923],"tcp_start":[0.65532,0.15978,0.29364],"tcp_to_object_dist_end":0.37351,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```