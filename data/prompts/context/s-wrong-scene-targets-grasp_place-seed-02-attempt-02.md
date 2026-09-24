## Search State

- **Seed**: 2
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | -0.2170 | 0.14 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | -0.2377 | 0.16 | ✅ accepted |
| 0 | align → align → pull → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | contact_detected | 0 | 0.1073 | 0.16 | ✅ accepted |

**Proposal policy**: task_score is 0.14 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.217) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: grasp_contact
  anchor: object
  weight: 0.3
- id: place_goal
  weight: 0.5
phases:
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
    - 0.15
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
      - 0.08
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
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
      - 0.3
      default: 0.15
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
    place_approach_z:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    place_transport_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
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
    place_force_thresh:
      type: scalar
      range:
      - 3.0
      - 15.0
      default: 6.0
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
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
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
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - place_approach_z: status=consumed; consumers=target.offset.z (replace)
    - place_transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
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

- **Composite score**: -0.217
- **task_score** (E): 0.139
- **fitness_score**: 0.313  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.780

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.33 | 1.00 | 0.1782 |
| descend_grasp | 1.00 | 1.00 | 0.0093 |
| grasp_action | 1.00 | 1.00 | 0.0746 |
| lift_object | 1.00 | 1.00 | 0.0775 |
| approach_goal | 0.00 | 0.67 | 0.1454 |
| descend_place | 1.00 | 1.00 | 0.0031 |
| release_object | 1.00 | 1.00 | 0.0248 |
| retract_after_place | 0.00 | 1.00 | 0.0005 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.436, -0.009, 0.160) | (0.493, -0.015, 0.030)→(0.466, -0.015, 0.019) | 0.279→0.300 | 1.00 / 4.667 | 270.777 | 943.630 |
| descend_grasp | descend | 1.00 / force_exceeded | (0.436, -0.009, 0.160)→(0.440, -0.009, 0.152) | (0.466, -0.015, 0.019)→(0.466, -0.015, 0.019) | 0.300→0.300 | 1.00 / 4.667 | 586.169 | 283.658 |
| grasp_action | grasp | 1.00 / step_budget | (0.441, -0.009, 0.152)→(0.418, -0.009, 0.081) | (0.466, -0.015, 0.019)→(0.455, -0.015, 0.016) | 0.300→0.306 | 1.00 / 20.667 | 44.439 | 334.927 |
| lift_object | lift | 1.00 / step_budget | (0.448, -0.014, 0.144)→(0.450, -0.015, 0.221) | (0.455, -0.015, 0.016)→(0.457, -0.015, 0.083) | 0.306→0.285 | 1.00 / 11.333 | 0.131 | 62.179 |
| approach_goal | approach | 0.00 / step_budget | (0.450, -0.015, 0.221)→(0.522, 0.068, 0.315) | (0.457, -0.015, 0.083)→(0.455, -0.001, 0.054) | 0.285→0.279 | 0.67 / 5.667 | 133.385 | 254.918 |
| descend_place | descend | 1.00 / force_exceeded | (0.522, 0.068, 0.315)→(0.523, 0.070, 0.314) | (0.455, -0.001, 0.054)→(0.454, 0.003, 0.021) | 0.279→0.295 | 1.00 / 6.667 | 93788.543 | 137.722 |
| release_object | release | 1.00 / step_budget | (0.523, 0.070, 0.314)→(0.524, 0.069, 0.339) | (0.454, 0.003, 0.021)→(0.450, 0.004, 0.016) | 0.295→0.300 | 1.00 / 4.667 | 38.615 | 130.327 |
| retract_after_place | retract | 0.00 / step_budget | (0.524, 0.069, 0.339)→(0.525, 0.069, 0.339) | (0.450, 0.004, 0.016)→(0.450, 0.004, 0.016) | 0.300→0.300 | 1.00 / 4.667 | 62.337 | 56.881 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.188
- phase_score: 0.132
- phase_breakdown.grasp_contact_score: 0.015
- phase_breakdown.approach_object_score: 0.591
- phase_breakdown.place_goal_score: 0.019
- grasp_place_fitness: 0.581

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.581
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.188
- **Median Q (composite search score)**: -0.350
- **K-run variance**: 0.0358
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.282


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":26.0,"average_failure_rate":0.23009,"average_mean_iterations":50.11504,"average_solve_count":113.0,"average_success_count":87.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.place_approach_z":0.14128,"approach_goal.place_arc_height":0.08435,"approach_goal.place_transport_speed":0.29708,"approach_object.approach_arc_height":0.14955,"approach_object.approach_offset_z":0.20515,"approach_object.approach_speed":0.35737,"descend_grasp.descend_force_thresh":7.80485,"descend_place.place_force_thresh":4.76132,"lift_object.lift_height":0.23464,"lift_object.lift_speed":0.10104,"release_object.release_duration":1.11986,"retract_after_place.retract_speed":0.2462},"optimized_scores":{"best_composite_score":-0.35047,"best_fitness_score":0.17953,"best_task_score":0.12126},"replay_outcomes":[{"contacts":{"omitted_contact_groups":10,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":617.0,"contact_point_centroid":[0.6339,-0.00377,-0.00055],"force_p95":213.61595,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1518.61621,"mean_force":212.49978,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38498,-0.00365,0.10188]},{"body_a":"link5","body_b":"hand","contact_count":58.0,"contact_point_centroid":[0.55396,0.00867,0.32076],"force_p95":674.87128,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":764.24406,"mean_force":517.39891,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51703,0.08346,0.33442]},{"body_a":"link5","body_b":"hand","contact_count":1.0,"contact_point_centroid":[0.55371,0.02265,0.30344],"force_p95":411.10064,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":411.10064,"mean_force":411.10064,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52455,0.09375,0.34129]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.55374,0.02194,0.30449],"force_p95":369.88325,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":389.01634,"mean_force":253.63037,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.52884,0.09047,0.35163]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.63454,-0.00803,-0.00026],"force_p95":296.22058,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":296.22058,"mean_force":296.22058,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.38788,-0.00889,0.11674]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.63519,-0.00811,-0.00013],"force_p95":86.43246,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":256.8447,"mean_force":72.45346,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.38826,-0.00889,0.11643]},{"body_a":"world","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.5235,0.00236,-0.00351],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":252.80841,"mean_force":10.11234,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37353,-0.00082,0.04576]},{"body_a":"link5","body_b":"hand","contact_count":2.0,"contact_point_centroid":[0.55419,0.01994,0.3236],"force_p95":167.06038,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":170.39638,"mean_force":137.03635,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.5294,0.09017,0.37162]},{"body_a":"world","body_b":"link6","contact_count":7.0,"contact_point_centroid":[0.63533,-0.00816,-9e-05],"force_p95":75.63313,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":92.8752,"mean_force":24.5481,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.38838,-0.00894,0.11646]},{"body_a":"grasp_target","body_b":"hand","contact_count":49.0,"contact_point_centroid":[0.45886,-0.00889,0.03523],"force_p95":3.68018,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.07404,"mean_force":1.55946,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38285,-0.00078,0.05102]},{"body_a":"world","body_b":"grasp_target","contact_count":2849.0,"contact_point_centroid":[0.44262,-0.01918,-0.00218],"force_p95":0.16889,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.37808,"mean_force":0.14462,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40207,-0.00314,0.11796]},{"body_a":"grasp_target","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.48121,-0.00307,0.01286],"force_p95":0.85301,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.94036,"mean_force":0.40046,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37353,-0.00082,0.04576]},{"body_a":"left_finger","body_b":"link5","contact_count":70.0,"contact_point_centroid":[0.51817,0.05548,0.34443],"force_p95":0.7455,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.78389,"mean_force":0.54331,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.52937,0.09038,0.36106]},{"body_a":"left_finger","body_b":"link5","contact_count":2.0,"contact_point_centroid":[0.51896,0.05444,0.3535],"force_p95":0.7598,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.76911,"mean_force":0.67602,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.5294,0.09017,0.37162]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.43615,-0.01898,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.38788,-0.00889,0.11674]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.43615,-0.01898,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.38826,-0.00889,0.11643]}],"total_contact_groups":26},"final_pose_error":0.12717,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.43615,-0.01898,0.01602],"final_tcp_position":[0.52935,0.09028,0.37172],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1518.61621,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":728.0,"n_steps_budget":1000.0,"object_pos_end":[0.43615,-0.01898,0.01602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.31647,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":211.67825,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3565.0,"raw_peak_contact_force":1518.61621,"subtask_id":"approach_object","tcp_end":[0.38788,-0.00889,0.11674],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11215,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.43615,-0.01898,0.01602],"object_pos_start":[0.43615,-0.01898,0.01602],"object_to_goal_dist_end":0.31647,"object_to_goal_dist_start":0.31647,"object_z_max":0.01602,"peak_contact_force":865.88506,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":296.22058,"subtask_id":"grasp_contact","tcp_end":[0.38785,-0.00877,0.11678],"tcp_start":[0.38788,-0.00889,0.11674],"tcp_to_object_dist_end":0.1122,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.43615,-0.01898,0.01602],"object_pos_start":[0.43615,-0.01898,0.01602],"object_to_goal_dist_end":0.31647,"object_to_goal_dist_start":0.31647,"object_z_max":0.01602,"peak_contact_force":66.77957,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3494.0,"raw_peak_contact_force":256.8447,"tcp_end":[0.38837,-0.00892,0.11624],"tcp_start":[0.38837,-0.00892,0.11624],"tcp_to_object_dist_end":0.11148,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":407.0,"n_steps_budget":900.0,"object_pos_end":[0.43615,-0.01898,0.01602],"object_pos_start":[0.43615,-0.01898,0.01602],"object_to_goal_dist_end":0.31647,"object_to_goal_dist_start":0.31647,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3332.0,"raw_peak_contact_force":92.8752,"tcp_end":[0.43024,-0.01826,0.2335],"tcp_start":[0.42972,-0.01808,0.23204],"tcp_to_object_dist_end":0.21756,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":383.0,"n_steps_budget":1000.0,"object_pos_end":[0.43615,-0.01898,0.01602],"object_pos_start":[0.43615,-0.01898,0.01602],"object_to_goal_dist_end":0.31647,"object_to_goal_dist_start":0.31647,"object_z_max":0.01602,"peak_contact_force":400.0333,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3234.0,"raw_peak_contact_force":764.24406,"subtask_id":"place_goal","tcp_end":[0.52455,0.09375,0.34129],"tcp_start":[0.43024,-0.01826,0.2335],"tcp_to_object_dist_end":0.35542,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.43615,-0.01898,0.01602],"object_pos_start":[0.43615,-0.01898,0.01602],"object_to_goal_dist_end":0.31647,"object_to_goal_dist_start":0.31647,"object_z_max":0.01602,"peak_contact_force":411.10064,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9.0,"raw_peak_contact_force":411.10064,"tcp_end":[0.52493,0.09358,0.34204],"tcp_start":[0.52455,0.09375,0.34129],"tcp_to_object_dist_end":0.35615,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.43615,-0.01898,0.01602],"object_pos_start":[0.43615,-0.01898,0.01602],"object_to_goal_dist_end":0.31647,"object_to_goal_dist_start":0.31647,"object_z_max":0.01602,"peak_contact_force":115.59885,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1296.0,"raw_peak_contact_force":389.01634,"tcp_end":[0.5294,0.09017,0.37152],"tcp_start":[0.52493,0.09358,0.34204],"tcp_to_object_dist_end":0.38339,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":2.0,"n_steps_budget":600.0,"object_pos_end":[0.43615,-0.01898,0.01602],"object_pos_start":[0.43615,-0.01898,0.01602],"object_to_goal_dist_end":0.31647,"object_to_goal_dist_start":0.31647,"object_z_max":0.01602,"peak_contact_force":186.76437,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":12.0,"raw_peak_contact_force":170.39638,"tcp_end":[0.52935,0.09028,0.37172],"tcp_start":[0.5294,0.09017,0.37152],"tcp_to_object_dist_end":0.3836,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":26.0,"average_failure_rate":0.25,"average_mean_iterations":53.88462,"average_solve_count":104.0,"average_success_count":78.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.place_approach_z":0.16087,"approach_goal.place_arc_height":0.09541,"approach_goal.place_transport_speed":0.40845,"approach_object.approach_arc_height":0.18865,"approach_object.approach_offset_z":0.23528,"approach_object.approach_speed":0.23257,"descend_grasp.descend_force_thresh":7.8616,"descend_place.place_force_thresh":7.88524,"lift_object.lift_height":0.17716,"lift_object.lift_speed":0.16419,"release_object.release_duration":1.65458,"retract_after_place.retract_speed":0.26098},"optimized_scores":{"best_composite_score":-0.35096,"best_fitness_score":0.17904,"best_task_score":0.10892},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":556.0,"contact_point_centroid":[0.61189,-0.01763,-0.00059],"force_p95":209.65558,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1312.13591,"mean_force":216.54516,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.35973,-0.01574,0.09867]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.6114,-0.02077,-0.00027],"force_p95":554.62666,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":554.62666,"mean_force":554.62666,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.35845,-0.01953,0.10244]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.61227,-0.02073,-0.00013],"force_p95":86.34832,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":122.84597,"mean_force":71.57877,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.35911,-0.01959,0.10221]},{"body_a":"world","body_b":"link6","contact_count":7.0,"contact_point_centroid":[0.61248,-0.02078,-0.0001],"force_p95":88.21879,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":92.73132,"mean_force":53.70059,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.35932,-0.01964,0.10228]},{"body_a":"grasp_target","body_b":"hand","contact_count":38.0,"contact_point_centroid":[0.43845,-0.03084,0.04083],"force_p95":3.70478,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.13351,"mean_force":1.67824,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.36247,-0.01269,0.05427]},{"body_a":"grasp_target","body_b":"link7","contact_count":29.0,"contact_point_centroid":[0.46232,-0.01777,0.01124],"force_p95":0.63721,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.61311,"mean_force":0.38753,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.35251,-0.01268,0.0577]},{"body_a":"world","body_b":"grasp_target","contact_count":2610.0,"contact_point_centroid":[0.4253,-0.02795,-0.00222],"force_p95":0.19539,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.02979,"mean_force":0.14744,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38084,-0.01461,0.11588]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.41795,-0.02834,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.35845,-0.01953,0.10244]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.41795,-0.02834,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.35911,-0.01959,0.10221]},{"body_a":"world","body_b":"grasp_target","contact_count":1180.0,"contact_point_centroid":[0.41795,-0.02834,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.38468,-0.02376,0.14121]},{"body_a":"world","body_b":"grasp_target","contact_count":1172.0,"contact_point_centroid":[0.41795,-0.02834,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.44711,0.01252,0.24862]},{"body_a":"world","body_b":"grasp_target","contact_count":20.0,"contact_point_centroid":[0.41795,-0.02834,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.49754,0.07454,0.29297]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.41795,-0.02834,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.49798,0.07714,0.296]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.41795,-0.02834,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.49816,0.07706,0.31638]},{"body_a":"left_finger","body_b":"right_finger","contact_count":742.0,"contact_point_centroid":[0.36136,-0.01962,0.10146],"force_p95":0.01297,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01107,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.35924,-0.01961,0.10201]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1248.0,"contact_point_centroid":[0.44941,0.0127,0.24832],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.01046,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.44735,0.01273,0.24895]}],"total_contact_groups":20},"final_pose_error":0.19315,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.41795,-0.02834,0.01602],"final_tcp_position":[0.49829,0.07715,0.31653],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273773.3142,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":669.0,"n_steps_budget":1000.0,"object_pos_end":[0.41795,-0.02834,0.01602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.33257,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":208.53156,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3252.0,"raw_peak_contact_force":1312.13591,"subtask_id":"approach_object","tcp_end":[0.35845,-0.01953,0.10244],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10529,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.41795,-0.02834,0.01602],"object_pos_start":[0.41795,-0.02834,0.01602],"object_to_goal_dist_end":0.33257,"object_to_goal_dist_start":0.33257,"object_z_max":0.01602,"peak_contact_force":810.35441,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":554.62666,"subtask_id":"grasp_contact","tcp_end":[0.35859,-0.01956,0.10268],"tcp_start":[0.35845,-0.01953,0.10244],"tcp_to_object_dist_end":0.10541,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.41795,-0.02834,0.01602],"object_pos_start":[0.41795,-0.02834,0.01602],"object_to_goal_dist_end":0.33257,"object_to_goal_dist_start":0.33257,"object_z_max":0.01602,"peak_contact_force":66.41066,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3492.0,"raw_peak_contact_force":122.84597,"tcp_end":[0.35925,-0.01962,0.102],"tcp_start":[0.35925,-0.01961,0.102],"tcp_to_object_dist_end":0.10447,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":295.0,"n_steps_budget":600.0,"object_pos_end":[0.41795,-0.02834,0.01602],"object_pos_start":[0.41795,-0.02834,0.01602],"object_to_goal_dist_end":0.33257,"object_to_goal_dist_start":0.33257,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":2411.0,"raw_peak_contact_force":92.73132,"tcp_end":[0.40867,-0.02743,0.17745],"tcp_start":[0.40787,-0.02724,0.17621],"tcp_to_object_dist_end":0.1617,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":293.0,"n_steps_budget":1000.0,"object_pos_end":[0.41795,-0.02834,0.01602],"object_pos_start":[0.41795,-0.02834,0.01602],"object_to_goal_dist_end":0.33257,"object_to_goal_dist_start":0.33257,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2420.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.4972,0.07369,0.29264],"tcp_start":[0.40867,-0.02743,0.17745],"tcp_to_object_dist_end":0.3053,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.41795,-0.02834,0.01602],"object_pos_start":[0.41795,-0.02834,0.01602],"object_to_goal_dist_end":0.33257,"object_to_goal_dist_start":0.33257,"object_z_max":0.01602,"peak_contact_force":273773.3142,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":40.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49803,0.07578,0.29319],"tcp_start":[0.4972,0.07369,0.29264],"tcp_to_object_dist_end":0.30672,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.41795,-0.02834,0.01602],"object_pos_start":[0.41795,-0.02834,0.01602],"object_to_goal_dist_end":0.33257,"object_to_goal_dist_start":0.33257,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1031.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49814,0.07702,0.31622],"tcp_start":[0.49803,0.07578,0.29319],"tcp_to_object_dist_end":0.32811,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.41795,-0.02834,0.01602],"object_pos_start":[0.41795,-0.02834,0.01602],"object_to_goal_dist_end":0.33257,"object_to_goal_dist_start":0.33257,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":12.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49829,0.07715,0.31653],"tcp_start":[0.49814,0.07702,0.31622],"tcp_to_object_dist_end":0.32847,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":28.0,"average_failure_rate":0.27451,"average_mean_iterations":59.32353,"average_solve_count":102.0,"average_success_count":74.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.place_approach_z":0.1162,"approach_goal.place_arc_height":0.18216,"approach_goal.place_transport_speed":0.28706,"approach_object.approach_arc_height":0.15906,"approach_object.approach_offset_z":0.20941,"approach_object.approach_speed":0.23252,"descend_grasp.descend_force_thresh":9.44205,"descend_place.place_force_thresh":7.65068,"lift_object.lift_height":0.25587,"lift_object.lift_speed":0.15236,"release_object.release_duration":1.61356,"retract_after_place.retract_speed":0.27204},"optimized_scores":{"best_composite_score":0.05055,"best_fitness_score":0.58055,"best_task_score":0.18806},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":32.0,"contact_point_centroid":[0.53045,-0.04227,-0.0032],"force_p95":549.01752,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":625.09094,"mean_force":115.72512,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.48578,0.00228,-0.01008]},{"body_a":"world","body_b":"right_finger","contact_count":925.0,"contact_point_centroid":[0.48942,0.04448,-0.00546],"force_p95":14.43448,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":25.71254,"mean_force":3.33691,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.48696,0.00227,-0.00607]},{"body_a":"world","body_b":"left_finger","contact_count":936.0,"contact_point_centroid":[0.49087,-0.03977,-0.00525],"force_p95":14.67864,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":25.51116,"mean_force":3.18885,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.48703,0.00227,-0.00592]},{"body_a":"grasp_target","body_b":"hand","contact_count":153.0,"contact_point_centroid":[0.54129,0.00607,0.02374],"force_p95":3.79179,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.59139,"mean_force":0.8454,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.49563,0.00221,0.00915]},{"body_a":"world","body_b":"grasp_target","contact_count":1.0,"contact_point_centroid":[0.52022,0.03839,-0.00082],"force_p95":1.94404,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.94404,"mean_force":1.94404,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.54691,0.04041,0.30677]},{"body_a":"world","body_b":"grasp_target","contact_count":781.0,"contact_point_centroid":[0.49755,0.06034,-0.0036],"force_p95":0.78451,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.84127,"mean_force":0.19341,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.546,0.04031,0.30784]},{"body_a":"world","body_b":"grasp_target","contact_count":1713.0,"contact_point_centroid":[0.51758,0.00117,-0.00272],"force_p95":0.64214,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.56266,"mean_force":0.18968,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.50972,0.00221,0.03221]},{"body_a":"world","body_b":"grasp_target","contact_count":69.0,"contact_point_centroid":[0.51088,0.00241,-0.00096],"force_p95":0.83467,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.93022,"mean_force":0.18859,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50569,0.00207,0.02462]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":452.0,"contact_point_centroid":[0.51334,0.02465,0.2588],"force_p95":0.21708,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38628,"mean_force":0.11529,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51462,0.00701,0.26627]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12571.0,"contact_point_centroid":[0.50685,-0.01714,0.12102],"force_p95":0.12063,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36148,"mean_force":0.059,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50534,0.00183,0.12164]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12115.0,"contact_point_centroid":[0.50649,0.02091,0.11977],"force_p95":0.11945,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35803,"mean_force":0.06096,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50532,0.00183,0.1203]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":366.0,"contact_point_centroid":[0.51307,-0.01218,0.25669],"force_p95":0.25002,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33391,"mean_force":0.14221,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51368,0.00598,0.26408]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4727.0,"contact_point_centroid":[0.5077,0.02135,0.0243],"force_p95":0.08585,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20973,"mean_force":0.04604,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.50639,0.00211,0.02318]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4715.0,"contact_point_centroid":[0.50834,-0.01712,0.02403],"force_p95":0.08676,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14861,"mean_force":0.04676,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.5064,0.00211,0.02318]},{"body_a":"world","body_b":"grasp_target","contact_count":204.0,"contact_point_centroid":[0.54431,0.00113,-0.00136],"force_p95":0.13839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12472,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.53061,0.00055,0.29692]},{"body_a":"world","body_b":"grasp_target","contact_count":36.0,"contact_point_centroid":[0.54431,0.00113,-0.00207],"force_p95":0.12666,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12666,"mean_force":0.12542,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.56753,0.0013,0.25036]}],"total_contact_groups":18},"final_pose_error":0.15567,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.49722,0.06037,0.01602],"final_tcp_position":[0.54646,0.04044,0.32846],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":7181.21351,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":52.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02587],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25022,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":392.12257,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":204.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.5631,0.00097,0.26159],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23647,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":9.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02587],"object_pos_start":[0.54431,0.00113,0.02587],"object_to_goal_dist_end":0.25022,"object_to_goal_dist_start":0.25022,"object_z_max":0.02587,"peak_contact_force":82.26629,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":36.0,"raw_peak_contact_force":0.12666,"subtask_id":"grasp_contact","tcp_end":[0.57487,0.00218,0.2367],"tcp_start":[0.5631,0.00097,0.26159],"tcp_to_object_dist_end":0.21304,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51194,0.00183,0.01704],"object_pos_start":[0.54431,0.00113,0.02587],"object_to_goal_dist_end":0.27041,"object_to_goal_dist_start":0.25022,"object_z_max":0.02602,"peak_contact_force":0.12747,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13201.0,"raw_peak_contact_force":625.09094,"tcp_end":[0.50672,0.0021,0.0235],"tcp_start":[0.57487,0.00218,0.2367],"tcp_to_object_dist_end":0.00832,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":718.0,"n_steps_budget":1000.0,"object_pos_end":[0.51817,0.00118,0.21716],"object_pos_start":[0.51194,0.00183,0.01704],"object_to_goal_dist_end":0.20508,"object_to_goal_dist_start":0.27041,"object_z_max":0.21695,"peak_contact_force":0.14814,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24755.0,"raw_peak_contact_force":0.93022,"tcp_end":[0.50961,0.00169,0.25306],"tcp_start":[0.50672,0.0021,0.0235],"tcp_to_object_dist_end":0.03691,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":128.0,"n_steps_budget":1000.0,"object_pos_end":[0.51088,0.04435,0.12915],"object_pos_start":[0.51817,0.00118,0.21716],"object_to_goal_dist_end":0.18834,"object_to_goal_dist_start":0.20508,"object_z_max":0.23353,"peak_contact_force":0.0,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":818.0,"raw_peak_contact_force":0.38628,"subtask_id":"place_goal","tcp_end":[0.54518,0.03752,0.31149],"tcp_start":[0.50961,0.00169,0.25306],"tcp_to_object_dist_end":0.18567,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":29.0,"n_steps_budget":1000.0,"object_pos_end":[0.50809,0.05651,0.0298],"object_pos_start":[0.51088,0.04435,0.12915],"object_to_goal_dist_end":0.23623,"object_to_goal_dist_start":0.18834,"object_z_max":0.12915,"peak_contact_force":7181.21351,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":1.94404,"tcp_end":[0.54703,0.04049,0.3066],"tcp_start":[0.54518,0.03752,0.31149],"tcp_to_object_dist_end":0.27998,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49722,0.06037,0.01602],"object_pos_start":[0.50809,0.05651,0.0298],"object_to_goal_dist_end":0.25065,"object_to_goal_dist_start":0.23623,"object_z_max":0.0298,"peak_contact_force":0.1226,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":856.0,"raw_peak_contact_force":1.84127,"tcp_end":[0.54593,0.04021,0.32778],"tcp_start":[0.54703,0.04049,0.3066],"tcp_to_object_dist_end":0.31618,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.49722,0.06037,0.01602],"object_pos_start":[0.49722,0.06037,0.01602],"object_to_goal_dist_end":0.25065,"object_to_goal_dist_start":0.25065,"object_z_max":0.01602,"peak_contact_force":0.12261,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":12.0,"raw_peak_contact_force":0.1226,"tcp_end":[0.54646,0.04044,0.32846],"tcp_start":[0.54593,0.04021,0.32778],"tcp_to_object_dist_end":0.31693,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```