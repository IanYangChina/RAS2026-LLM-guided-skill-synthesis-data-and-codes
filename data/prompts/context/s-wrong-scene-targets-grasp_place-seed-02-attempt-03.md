## Search State

- **Seed**: 2
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | -0.3633 | 0.16 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | -0.2170 | 0.14 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | -0.2377 | 0.16 | ✅ accepted |
| 0 | align → align → pull → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | contact_detected | 0 | 0.1073 | 0.16 | ✅ accepted |

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

## Current Skill (Q=-0.363) — your mutation base

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

- **Composite score**: -0.363
- **task_score** (E): 0.162
- **fitness_score**: 0.167  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.780

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.00 | 1.00 | 0.1519 |
| descend_grasp | 1.00 | 1.00 | 0.0002 |
| grasp_action | 1.00 | 1.00 | 0.0000 |
| lift_object | 1.00 | 1.00 | 0.0071 |
| approach_goal | 0.33 | 1.00 | 0.1173 |
| descend_place | 1.00 | 1.00 | 0.0001 |
| release_object | 1.00 | 1.00 | 0.0274 |
| retract_after_place | 0.33 | 1.00 | 0.0670 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.453, 0.002, 0.189) | (0.493, -0.015, 0.030)→(0.461, -0.009, 0.018) | 0.279→0.299 | 1.00 / 5.000 | 276.384 | 1482.151 |
| descend_grasp | descend | 1.00 / force_exceeded | (0.453, 0.002, 0.189)→(0.453, 0.002, 0.189) | (0.461, -0.009, 0.018)→(0.461, -0.009, 0.018) | 0.299→0.299 | 1.00 / 5.000 | 454.988 | 267.083 |
| grasp_action | grasp | 1.00 / step_budget | (0.453, 0.002, 0.189)→(0.453, 0.002, 0.189) | (0.461, -0.009, 0.018)→(0.460, -0.004, 0.019) | 0.299→0.296 | 1.00 / 9.000 | 74.042 | 451.568 |
| lift_object | lift | 1.00 / step_budget | (0.463, 0.006, 0.213)→(0.460, 0.011, 0.213) | (0.460, -0.002, 0.018)→(0.459, 0.001, 0.016) | 0.295→0.296 | 1.00 / 9.333 | 91091.577 | 165.805 |
| approach_goal | approach | 0.33 / step_budget | (0.460, 0.011, 0.213)→(0.491, 0.093, 0.256) | (0.459, 0.001, 0.016)→(0.462, 0.020, 0.018) | 0.296→0.286 | 1.00 / 9.000 | 94312.077 | 1024.558 |
| descend_place | descend | 1.00 / force_exceeded | (0.491, 0.093, 0.256)→(0.491, 0.093, 0.256) | (0.462, 0.020, 0.018)→(0.462, 0.020, 0.018) | 0.286→0.286 | 1.00 / 8.667 | 197.099 | 218.782 |
| release_object | release | 1.00 / step_budget | (0.491, 0.093, 0.256)→(0.491, 0.093, 0.283) | (0.462, 0.020, 0.018)→(0.463, 0.020, 0.020) | 0.286→0.284 | 1.00 / 3.333 | 0.170 | 208.401 |
| retract_after_place | retract | 0.33 / step_budget | (0.491, 0.093, 0.283)→(0.527, 0.124, 0.238) | (0.463, 0.020, 0.020)→(0.466, 0.020, 0.019) | 0.284→0.284 | 1.00 / 5.333 | 218.751 | 734.768 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.255
- phase_score: 0.070
- phase_breakdown.grasp_contact_score: 0.006
- phase_breakdown.approach_object_score: 0.041
- phase_breakdown.place_goal_score: 0.120
- grasp_place_fitness: 0.170

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.170
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.255
- **Median Q (composite search score)**: -0.362
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.319


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":10.0,"average_failure_rate":0.09709,"average_mean_iterations":24.80583,"average_solve_count":103.0,"average_success_count":93.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.place_approach_z":0.10895,"approach_goal.place_arc_height":0.0947,"approach_goal.place_transport_speed":0.13638,"approach_object.approach_arc_height":0.19699,"approach_object.approach_offset_z":0.17939,"approach_object.approach_speed":0.29526,"descend_grasp.descend_force_thresh":7.14708,"descend_place.place_force_thresh":12.46156,"lift_object.lift_height":0.18271,"lift_object.lift_speed":0.11923,"release_object.release_duration":1.27721,"retract_after_place.retract_speed":0.44105},"optimized_scores":{"best_composite_score":-0.36842,"best_fitness_score":0.16158,"best_task_score":0.12116},"replay_outcomes":[{"contacts":{"omitted_contact_groups":8,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":852.0,"contact_point_centroid":[0.63431,0.0014,-0.00046],"force_p95":217.83678,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1444.83612,"mean_force":207.77423,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39143,0.00043,0.11822]},{"body_a":"world","body_b":"link6","contact_count":15.0,"contact_point_centroid":[0.64553,0.09343,-0.00264],"force_p95":1033.57464,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1039.54731,"mean_force":621.56424,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.45093,0.06941,0.19109]},{"body_a":"world","body_b":"link6","contact_count":959.0,"contact_point_centroid":[0.56627,-0.00361,-0.0003],"force_p95":240.21205,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":951.29679,"mean_force":218.56079,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.35792,-0.00881,0.17508]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.63082,-0.00573,-0.00013],"force_p95":79.30342,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":327.55318,"mean_force":73.02822,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.40082,-0.00708,0.14703]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.63025,-0.00598,-0.00023],"force_p95":307.26282,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":307.26282,"mean_force":307.26282,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.40049,-0.00733,0.1472]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.52272,0.02047,-7e-05],"force_p95":232.55536,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":232.55536,"mean_force":232.55536,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.39452,0.02187,0.25119]},{"body_a":"world","body_b":"link6","contact_count":8.0,"contact_point_centroid":[0.63097,-0.00579,-0.00011],"force_p95":134.56787,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":137.30439,"mean_force":97.6889,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.401,-0.00715,0.1471]},{"body_a":"world","body_b":"link6","contact_count":70.0,"contact_point_centroid":[0.52245,0.0205,-0.00011],"force_p95":79.52389,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":105.37333,"mean_force":66.43317,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.3948,0.02192,0.25139]},{"body_a":"grasp_target","body_b":"hand","contact_count":42.0,"contact_point_centroid":[0.45548,-0.01173,0.03835],"force_p95":3.56908,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.94331,"mean_force":1.62817,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.3844,0.00294,0.05002]},{"body_a":"world","body_b":"grasp_target","contact_count":3787.0,"contact_point_centroid":[0.44083,-0.01906,-0.00214],"force_p95":0.13782,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.33257,"mean_force":0.13906,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40375,0.00063,0.12875]},{"body_a":"grasp_target","body_b":"link7","contact_count":27.0,"contact_point_centroid":[0.48227,-0.00141,0.01109],"force_p95":0.56448,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.5957,"mean_force":0.23093,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37441,0.00288,0.04969]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.43585,-0.01889,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.40049,-0.00733,0.1472]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.43585,-0.01889,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.40082,-0.00708,0.14703]},{"body_a":"world","body_b":"grasp_target","contact_count":676.0,"contact_point_centroid":[0.43585,-0.01889,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.41442,-0.01225,0.16582]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.43585,-0.01889,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.35945,-0.00866,0.17601]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.43585,-0.01889,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.39452,0.02187,0.25119]}],"total_contact_groups":24},"final_pose_error":0.22332,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.43585,-0.01889,0.01602],"final_tcp_position":[0.45302,0.06728,0.19207],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1444.83612,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.43585,-0.01889,0.01602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.3166,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":215.63374,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4731.0,"raw_peak_contact_force":1444.83612,"subtask_id":"approach_object","tcp_end":[0.40049,-0.00733,0.1472],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13636,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.43585,-0.01889,0.01602],"object_pos_start":[0.43585,-0.01889,0.01602],"object_to_goal_dist_end":0.3166,"object_to_goal_dist_start":0.3166,"object_z_max":0.01602,"peak_contact_force":307.26282,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":307.26282,"subtask_id":"grasp_contact","tcp_end":[0.40048,-0.00724,0.14727],"tcp_start":[0.40049,-0.00733,0.1472],"tcp_to_object_dist_end":0.13643,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.43585,-0.01889,0.01602],"object_pos_start":[0.43585,-0.01889,0.01602],"object_to_goal_dist_end":0.3166,"object_to_goal_dist_start":0.3166,"object_z_max":0.01602,"peak_contact_force":68.56884,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3512.0,"raw_peak_contact_force":327.55318,"tcp_end":[0.40089,-0.0071,0.14686],"tcp_start":[0.40089,-0.0071,0.14687],"tcp_to_object_dist_end":0.13595,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":169.0,"n_steps_budget":600.0,"object_pos_end":[0.43585,-0.01889,0.01602],"object_pos_start":[0.43585,-0.01889,0.01602],"object_to_goal_dist_end":0.3166,"object_to_goal_dist_start":0.3166,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1391.0,"raw_peak_contact_force":137.30439,"tcp_end":[0.42664,-0.0167,0.18293],"tcp_start":[0.42578,-0.01625,0.18183],"tcp_to_object_dist_end":0.16718,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43585,-0.01889,0.01602],"object_pos_start":[0.43585,-0.01889,0.01602],"object_to_goal_dist_end":0.3166,"object_to_goal_dist_start":0.3166,"object_z_max":0.01602,"peak_contact_force":169.56745,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9200.0,"raw_peak_contact_force":951.29679,"subtask_id":"place_goal","tcp_end":[0.39452,0.02187,0.25119],"tcp_start":[0.42664,-0.0167,0.18293],"tcp_to_object_dist_end":0.24223,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.43585,-0.01889,0.01602],"object_pos_start":[0.43585,-0.01889,0.01602],"object_to_goal_dist_end":0.3166,"object_to_goal_dist_start":0.3166,"object_z_max":0.01602,"peak_contact_force":232.55536,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9.0,"raw_peak_contact_force":232.55536,"tcp_end":[0.39467,0.02188,0.25136],"tcp_start":[0.39452,0.02187,0.25119],"tcp_to_object_dist_end":0.24237,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.43585,-0.01889,0.01602],"object_pos_start":[0.43585,-0.01889,0.01602],"object_to_goal_dist_end":0.3166,"object_to_goal_dist_start":0.3166,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1085.0,"raw_peak_contact_force":105.37333,"tcp_end":[0.3943,0.02182,0.28085],"tcp_start":[0.39467,0.02188,0.25136],"tcp_to_object_dist_end":0.27115,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":152.0,"n_steps_budget":600.0,"object_pos_end":[0.43585,-0.01889,0.01602],"object_pos_start":[0.43585,-0.01889,0.01602],"object_to_goal_dist_end":0.3166,"object_to_goal_dist_start":0.3166,"object_z_max":0.01602,"peak_contact_force":295.17175,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":623.0,"raw_peak_contact_force":1039.54731,"tcp_end":[0.45302,0.06728,0.19207],"tcp_start":[0.3943,0.02182,0.28085],"tcp_to_object_dist_end":0.19675,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":9.0,"average_failure_rate":0.08824,"average_mean_iterations":22.83333,"average_solve_count":102.0,"average_success_count":93.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.place_approach_z":0.10903,"approach_goal.place_arc_height":0.14219,"approach_goal.place_transport_speed":0.23998,"approach_object.approach_arc_height":0.2444,"approach_object.approach_offset_z":0.16667,"approach_object.approach_speed":0.28476,"descend_grasp.descend_force_thresh":8.78641,"descend_place.place_force_thresh":13.54609,"lift_object.lift_height":0.17459,"lift_object.lift_speed":0.16243,"release_object.release_duration":1.21738,"retract_after_place.retract_speed":0.32705},"optimized_scores":{"best_composite_score":-0.36185,"best_fitness_score":0.16815,"best_task_score":0.1111},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":852.0,"contact_point_centroid":[0.63298,-0.00013,-0.00044],"force_p95":228.8778,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1339.5862,"mean_force":211.68883,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38595,-0.00089,0.10844]},{"body_a":"world","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.52253,0.00654,-0.00312],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1296.59371,"mean_force":54.02474,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37269,0.00268,0.04605]},{"body_a":"world","body_b":"link6","contact_count":75.0,"contact_point_centroid":[0.63517,0.12295,-0.0005],"force_p95":870.91075,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1164.30964,"mean_force":634.46028,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.45372,0.11479,0.21441]},{"body_a":"world","body_b":"link6","contact_count":770.0,"contact_point_centroid":[0.55797,0.02007,-0.00026],"force_p95":511.2729,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1000.04416,"mean_force":247.45617,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.36411,0.01372,0.18792]},{"body_a":"link5","body_b":"hand","contact_count":72.0,"contact_point_centroid":[0.52851,0.07191,0.2026],"force_p95":706.91762,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":793.37572,"mean_force":502.1771,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.47,0.13069,0.21107]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.631,-0.01045,-0.00012],"force_p95":79.13655,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":329.83106,"mean_force":72.29345,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.39225,-0.01135,0.13238]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.63038,-0.01062,-0.0002],"force_p95":310.01281,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":310.01281,"mean_force":310.01281,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.39191,-0.01154,0.13272]},{"body_a":"world","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.60126,0.13221,-0.00011],"force_p95":248.20129,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":251.45373,"mean_force":218.92932,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.43419,0.10295,0.22286]},{"body_a":"world","body_b":"link6","contact_count":67.0,"contact_point_centroid":[0.60178,0.13363,-9e-05],"force_p95":77.34614,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":178.56414,"mean_force":69.73603,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.43385,0.10355,0.22215]},{"body_a":"world","body_b":"link6","contact_count":8.0,"contact_point_centroid":[0.63115,-0.01051,-0.00011],"force_p95":77.65196,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":91.51088,"mean_force":22.88309,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.39238,-0.01142,0.13238]},{"body_a":"left_finger","body_b":"link5","contact_count":416.0,"contact_point_centroid":[0.47798,0.08943,0.22402],"force_p95":10.73767,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":13.35,"mean_force":3.16021,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.46568,0.12547,0.21222]},{"body_a":"grasp_target","body_b":"hand","contact_count":42.0,"contact_point_centroid":[0.43784,-0.01402,0.04147],"force_p95":3.58072,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.8332,"mean_force":1.44156,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38193,0.00272,0.0489]},{"body_a":"world","body_b":"grasp_target","contact_count":3765.0,"contact_point_centroid":[0.42313,-0.02443,-0.00215],"force_p95":0.13823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.37665,"mean_force":0.13974,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39879,-0.0006,0.12013]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.41791,-0.02411,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.39191,-0.01154,0.13272]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.41791,-0.02411,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.39225,-0.01135,0.13238]},{"body_a":"world","body_b":"grasp_target","contact_count":692.0,"contact_point_centroid":[0.41791,-0.02411,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.40159,-0.01694,0.15412]}],"total_contact_groups":25},"final_pose_error":0.15802,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.41791,-0.02411,0.01602],"final_tcp_position":[0.4831,0.15055,0.20875],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273043.58923,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.41791,-0.02411,0.01602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.3296,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":225.84705,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4683.0,"raw_peak_contact_force":1339.5862,"subtask_id":"approach_object","tcp_end":[0.39191,-0.01154,0.13272],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12022,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.41791,-0.02411,0.01602],"object_pos_start":[0.41791,-0.02411,0.01602],"object_to_goal_dist_end":0.3296,"object_to_goal_dist_start":0.3296,"object_z_max":0.01602,"peak_contact_force":873.72705,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":310.01281,"subtask_id":"grasp_contact","tcp_end":[0.39189,-0.01146,0.13277],"tcp_start":[0.39191,-0.01154,0.13272],"tcp_to_object_dist_end":0.12029,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.41791,-0.02411,0.01602],"object_pos_start":[0.41791,-0.02411,0.01602],"object_to_goal_dist_end":0.3296,"object_to_goal_dist_start":0.3296,"object_z_max":0.01602,"peak_contact_force":67.60095,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3509.0,"raw_peak_contact_force":329.83106,"tcp_end":[0.39234,-0.01137,0.1322],"tcp_start":[0.39234,-0.01137,0.1322],"tcp_to_object_dist_end":0.11964,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":173.0,"n_steps_budget":600.0,"object_pos_end":[0.41791,-0.02411,0.01602],"object_pos_start":[0.41791,-0.02411,0.01602],"object_to_goal_dist_end":0.3296,"object_to_goal_dist_start":0.3296,"object_z_max":0.01602,"peak_contact_force":273043.58923,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1439.0,"raw_peak_contact_force":91.51088,"tcp_end":[0.41041,-0.02176,0.1741],"tcp_start":[0.40984,-0.0213,0.17267],"tcp_to_object_dist_end":0.15827,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41791,-0.02411,0.01602],"object_pos_start":[0.41791,-0.02411,0.01602],"object_to_goal_dist_end":0.3296,"object_to_goal_dist_start":0.3296,"object_z_max":0.01602,"peak_contact_force":273017.71997,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8975.0,"raw_peak_contact_force":1000.04416,"subtask_id":"place_goal","tcp_end":[0.43417,0.10296,0.22289],"tcp_start":[0.41041,-0.02176,0.1741],"tcp_to_object_dist_end":0.24332,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.41791,-0.02411,0.01602],"object_pos_start":[0.41791,-0.02411,0.01602],"object_to_goal_dist_end":0.3296,"object_to_goal_dist_start":0.3296,"object_z_max":0.01602,"peak_contact_force":186.40491,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":19.0,"raw_peak_contact_force":251.45373,"tcp_end":[0.43419,0.103,0.2228],"tcp_start":[0.43417,0.10296,0.22289],"tcp_to_object_dist_end":0.24327,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.41791,-0.02411,0.01602],"object_pos_start":[0.41791,-0.02411,0.01602],"object_to_goal_dist_end":0.3296,"object_to_goal_dist_start":0.3296,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1081.0,"raw_peak_contact_force":178.56414,"tcp_end":[0.43282,0.10333,0.24983],"tcp_start":[0.43419,0.103,0.2228],"tcp_to_object_dist_end":0.26671,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":185.0,"n_steps_budget":600.0,"object_pos_end":[0.41791,-0.02411,0.01602],"object_pos_start":[0.41791,-0.02411,0.01602],"object_to_goal_dist_end":0.3296,"object_to_goal_dist_start":0.3296,"object_z_max":0.01602,"peak_contact_force":360.6341,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1303.0,"raw_peak_contact_force":1164.30964,"tcp_end":[0.4831,0.15055,0.20875],"tcp_start":[0.43282,0.10333,0.24983],"tcp_to_object_dist_end":0.26815,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.53465,"average_solve_count":101.0,"average_success_count":101.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.place_approach_z":0.07662,"approach_goal.place_arc_height":0.09006,"approach_goal.place_transport_speed":0.17605,"approach_object.approach_arc_height":0.09363,"approach_object.approach_offset_z":0.09922,"approach_object.approach_speed":0.29452,"descend_grasp.descend_force_thresh":8.28641,"descend_place.place_force_thresh":10.17366,"lift_object.lift_height":0.23765,"lift_object.lift_speed":0.18963,"release_object.release_duration":0.50487,"retract_after_place.retract_speed":0.43614},"optimized_scores":{"best_composite_score":-0.35953,"best_fitness_score":0.17047,"best_task_score":0.25524},"replay_outcomes":[{"contacts":{"omitted_contact_groups":20,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":816.0,"contact_point_centroid":[0.63066,0.0556,-0.00041],"force_p95":654.55229,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1662.02946,"mean_force":327.96071,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.46926,0.05953,0.20921]},{"body_a":"world","body_b":"link6","contact_count":54.0,"contact_point_centroid":[0.6295,0.12622,-0.00025],"force_p95":1020.47511,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1122.33239,"mean_force":553.62262,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.63395,0.14566,0.29262]},{"body_a":"world","body_b":"link6","contact_count":545.0,"contact_point_centroid":[0.62469,0.01478,-0.00014],"force_p95":87.64129,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":697.3199,"mean_force":77.17817,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.56637,0.0258,0.28716]},{"body_a":"world","body_b":"link6","contact_count":86.0,"contact_point_centroid":[0.63686,0.13836,-0.00011],"force_p95":173.47026,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":341.26628,"mean_force":69.7288,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.64447,0.15296,0.29369]},{"body_a":"world","body_b":"link6","contact_count":673.0,"contact_point_centroid":[0.61511,0.02793,-0.00025],"force_p95":230.76165,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":268.59845,"mean_force":210.0637,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.55296,0.0542,0.28443]},{"body_a":"link5","body_b":"hand","contact_count":675.0,"contact_point_centroid":[0.53358,-0.04377,0.23724],"force_p95":226.21962,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":262.69897,"mean_force":192.62221,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.55299,0.05412,0.28444]},{"body_a":"link5","body_b":"hand","contact_count":550.0,"contact_point_centroid":[0.54013,-0.06519,0.2256],"force_p95":26.13183,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":242.26727,"mean_force":25.1473,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.56636,0.02581,0.28716]},{"body_a":"link5","body_b":"hand","contact_count":159.0,"contact_point_centroid":[0.53849,-0.05629,0.22977],"force_p95":177.75278,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":232.56346,"mean_force":96.23195,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.56345,0.03705,0.28643]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.62443,0.01413,-0.00032],"force_p95":183.97278,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":183.97278,"mean_force":183.97278,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.56596,0.02593,0.28673]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.62615,0.14946,-0.00024],"force_p95":172.33735,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":172.33735,"mean_force":172.33735,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.6445,0.15314,0.29342]},{"body_a":"grasp_target","body_b":"link6","contact_count":441.0,"contact_point_centroid":[0.54206,0.01305,0.03848],"force_p95":1.20992,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.87088,"mean_force":0.5484,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49022,0.04481,0.21684]},{"body_a":"grasp_target","body_b":"link7","contact_count":217.0,"contact_point_centroid":[0.52373,0.02027,0.04648],"force_p95":2.89654,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.7935,"mean_force":0.83625,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39304,0.03909,0.12187]},{"body_a":"world","body_b":"grasp_target","contact_count":3272.0,"contact_point_centroid":[0.53888,0.00416,-0.00297],"force_p95":0.5795,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.26369,"mean_force":0.20314,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4744,0.05947,0.21114]},{"body_a":"grasp_target","body_b":"hand","contact_count":27.0,"contact_point_centroid":[0.50024,-0.00817,0.03077],"force_p95":1.96395,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.25167,"mean_force":1.0252,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38803,0.02997,0.05043]},{"body_a":"grasp_target","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.54819,0.01036,0.0345],"force_p95":1.43904,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.43904,"mean_force":1.43904,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.56596,0.02593,0.28673]},{"body_a":"grasp_target","body_b":"link6","contact_count":299.0,"contact_point_centroid":[0.5293,0.0707,0.04677],"force_p95":1.00445,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.38055,"mean_force":0.50169,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.59558,0.11262,0.30325]}],"total_contact_groups":36},"final_pose_error":0.02369,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.54299,0.10337,0.02373],"final_tcp_position":[0.64536,0.15347,0.31422],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52809,0.01687,0.02257],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25027,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":387.67172,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4950.0,"raw_peak_contact_force":1662.02946,"subtask_id":"approach_object","tcp_end":[0.56596,0.02593,0.28673],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.26701,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.52803,0.01696,0.02266],"object_pos_start":[0.52809,0.01687,0.02257],"object_to_goal_dist_end":0.25018,"object_to_goal_dist_start":0.25027,"object_z_max":0.02257,"peak_contact_force":183.97278,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":183.97278,"subtask_id":"grasp_contact","tcp_end":[0.56606,0.02566,0.28696],"tcp_start":[0.56596,0.02593,0.28673],"tcp_to_object_dist_end":0.26717,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.52623,0.02996,0.0257],"object_pos_start":[0.52803,0.01696,0.02266],"object_to_goal_dist_end":0.24189,"object_to_goal_dist_start":0.25018,"object_z_max":0.02591,"peak_contact_force":85.95641,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3535.0,"raw_peak_contact_force":697.3199,"tcp_end":[0.5664,0.02586,0.28716],"tcp_start":[0.5664,0.02585,0.28716],"tcp_to_object_dist_end":0.26457,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":675.0,"n_steps_budget":600.0,"object_pos_end":[0.52436,0.04561,0.0155],"object_pos_start":[0.52752,0.03711,0.02214],"object_to_goal_dist_end":0.24225,"object_to_goal_dist_start":0.24002,"object_z_max":0.02214,"peak_contact_force":231.01929,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7480.0,"raw_peak_contact_force":268.59845,"tcp_end":[0.54356,0.07024,0.28145],"tcp_start":[0.55279,0.05495,0.28497],"tcp_to_object_dist_end":0.26778,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":303.0,"n_steps_budget":1000.0,"object_pos_end":[0.53254,0.10403,0.02054],"object_pos_start":[0.52435,0.04572,0.01602],"object_to_goal_dist_end":0.21274,"object_to_goal_dist_start":0.24182,"object_z_max":0.0232,"peak_contact_force":9748.94236,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2523.0,"raw_peak_contact_force":1122.33239,"subtask_id":"place_goal","tcp_end":[0.6445,0.15314,0.29342],"tcp_start":[0.54356,0.07024,0.28145],"tcp_to_object_dist_end":0.29901,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.53252,0.10404,0.02058],"object_pos_start":[0.53254,0.10403,0.02054],"object_to_goal_dist_end":0.21272,"object_to_goal_dist_start":0.21274,"object_z_max":0.02054,"peak_contact_force":172.33735,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8.0,"raw_peak_contact_force":172.33735,"tcp_end":[0.64454,0.15308,0.29349],"tcp_start":[0.6445,0.15314,0.29342],"tcp_to_object_dist_end":0.29906,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53637,0.10152,0.02669],"object_pos_start":[0.53252,0.10404,0.02058],"object_to_goal_dist_end":0.20642,"object_to_goal_dist_start":0.21272,"object_z_max":0.02746,"peak_contact_force":0.26447,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":869.0,"raw_peak_contact_force":341.26628,"tcp_end":[0.64468,0.1529,0.31907],"tcp_start":[0.64454,0.15308,0.29349],"tcp_to_object_dist_end":0.31601,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.54299,0.10337,0.02373],"object_pos_start":[0.53637,0.10152,0.02669],"object_to_goal_dist_end":0.20483,"object_to_goal_dist_start":0.20642,"object_z_max":0.02669,"peak_contact_force":0.44586,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":43.0,"raw_peak_contact_force":0.44586,"tcp_end":[0.64536,0.15347,0.31422],"tcp_start":[0.64468,0.1529,0.31907],"tcp_to_object_dist_end":0.31205,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```