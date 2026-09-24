## Search State

- **Seed**: 2
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
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

## Current Skill (Q=-0.238) — your mutation base

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

- **Composite score**: -0.238
- **task_score** (E): 0.156
- **fitness_score**: 0.192  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.680

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.00 | 1.00 | 0.2085 |
| descend_grasp | 1.00 | 1.00 | 0.0002 |
| grasp_action | 1.00 | 1.00 | 0.0000 |
| lift_object | 0.67 | 1.00 | 0.0213 |
| approach_goal | 0.33 | 1.00 | 0.2576 |
| descend_place | 1.00 | 1.00 | 0.0011 |
| release_object | 1.00 | 1.00 | 0.0223 |
| retract_after_place | 0.33 | 1.00 | 0.0819 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.399, -0.011, 0.121) | (0.493, -0.015, 0.030)→(0.453, -0.016, 0.016) | 0.279→0.308 | 1.00 / 5.000 | 197.873 | 1440.074 |
| descend_grasp | descend | 1.00 / force_exceeded | (0.399, -0.011, 0.121)→(0.399, -0.011, 0.121) | (0.453, -0.016, 0.016)→(0.453, -0.016, 0.016) | 0.308→0.308 | 1.00 / 5.000 | 571.967 | 401.939 |
| grasp_action | grasp | 1.00 / step_budget | (0.399, -0.011, 0.121)→(0.399, -0.011, 0.121) | (0.453, -0.016, 0.016)→(0.453, -0.016, 0.016) | 0.308→0.308 | 1.00 / 9.333 | 91045.898 | 144.198 |
| lift_object | lift | 0.67 / step_budget | (0.451, -0.017, 0.233)→(0.451, -0.018, 0.254) | (0.453, -0.016, 0.016)→(0.453, -0.016, 0.016) | 0.308→0.308 | 1.00 / 8.667 | 91003.064 | 302.589 |
| approach_goal | approach | 0.33 / step_budget | (0.451, -0.018, 0.254)→(0.565, 0.191, 0.324) | (0.453, -0.016, 0.016)→(0.470, 0.008, 0.016) | 0.308→0.288 | 1.00 / 8.667 | 91001.148 | 1201.833 |
| descend_place | descend | 1.00 / force_exceeded | (0.565, 0.191, 0.324)→(0.565, 0.191, 0.324) | (0.470, 0.008, 0.016)→(0.470, 0.008, 0.016) | 0.288→0.288 | 1.00 / 8.667 | 91174.819 | 80.203 |
| release_object | release | 1.00 / step_budget | (0.565, 0.191, 0.324)→(0.565, 0.190, 0.346) | (0.470, 0.008, 0.016)→(0.470, 0.008, 0.016) | 0.288→0.288 | 1.00 / 4.000 | 0.123 | 237.652 |
| retract_after_place | retract | 0.33 / step_budget | (0.565, 0.190, 0.346)→(0.590, 0.144, 0.325) | (0.470, 0.008, 0.016)→(0.470, 0.008, 0.016) | 0.288→0.288 | 1.00 / 4.667 | 186.697 | 382.816 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.242
- phase_score: 0.070
- phase_breakdown.grasp_contact_score: 0.045
- phase_breakdown.approach_object_score: 0.194
- phase_breakdown.place_goal_score: 0.036
- grasp_place_fitness: 0.211

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.211
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.242
- **Median Q (composite search score)**: -0.243
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.382


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":10.0,"average_failure_rate":0.09709,"average_mean_iterations":24.73786,"average_solve_count":103.0,"average_success_count":93.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.place_approach_z":0.09076,"approach_goal.place_transport_speed":0.19463,"approach_object.approach_offset_z":0.24997,"approach_object.approach_speed":0.45257,"descend_grasp.descend_force_thresh":12.83797,"descend_place.place_force_thresh":4.98009,"lift_object.lift_height":0.20873,"lift_object.lift_speed":0.20589,"release_object.release_duration":0.71949,"retract_after_place.retract_speed":0.26802},"optimized_scores":{"best_composite_score":-0.25175,"best_fitness_score":0.17825,"best_task_score":0.1167},"replay_outcomes":[{"contacts":{"omitted_contact_groups":10,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":555.0,"contact_point_centroid":[0.62088,-0.01228,-0.00058],"force_p95":204.21003,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1518.28928,"mean_force":211.81181,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.36963,-0.0111,0.1016]},{"body_a":"world","body_b":"link5","contact_count":64.0,"contact_point_centroid":[0.5994,0.19999,-0.00064],"force_p95":855.89865,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1148.20306,"mean_force":533.67449,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.48612,0.06558,0.21597]},{"body_a":"world","body_b":"link6","contact_count":916.0,"contact_point_centroid":[0.58793,0.03035,-0.00034],"force_p95":576.07826,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1022.68701,"mean_force":404.37736,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.43039,0.01225,0.23173]},{"body_a":"world","body_b":"link6","contact_count":43.0,"contact_point_centroid":[0.65156,0.09829,-0.00079],"force_p95":819.96243,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1016.48694,"mean_force":610.33455,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.46387,0.05778,0.20286]},{"body_a":"world","body_b":"link6","contact_count":76.0,"contact_point_centroid":[0.65222,0.08632,-0.00013],"force_p95":87.08073,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":712.71009,"mean_force":76.71772,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.45889,0.04933,0.19562]},{"body_a":"link5","body_b":"hand","contact_count":175.0,"contact_point_centroid":[0.49088,0.14998,0.14701],"force_p95":219.01241,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":571.16021,"mean_force":115.81705,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.47522,0.06202,0.20939]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.61996,-0.01474,-0.00027],"force_p95":532.97037,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":532.97037,"mean_force":532.97037,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.36808,-0.01414,0.10505]},{"body_a":"world","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.65206,0.08664,-0.0001],"force_p95":237.7003,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":240.36483,"mean_force":213.71954,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.45903,0.04995,0.19602]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.62082,-0.01463,-0.00013],"force_p95":86.10256,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":117.96652,"mean_force":71.36026,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.36873,-0.01411,0.10482]},{"body_a":"world","body_b":"link6","contact_count":6.0,"contact_point_centroid":[0.62101,-0.01467,-0.0001],"force_p95":81.5275,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":92.99165,"mean_force":25.21109,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.3689,-0.01416,0.10482]},{"body_a":"grasp_target","body_b":"link7","contact_count":93.0,"contact_point_centroid":[0.47374,-0.01471,0.02257],"force_p95":2.01675,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.21614,"mean_force":0.50872,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.36629,-0.00898,0.08149]},{"body_a":"grasp_target","body_b":"hand","contact_count":122.0,"contact_point_centroid":[0.451,-0.03783,0.04949],"force_p95":3.34572,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.09615,"mean_force":0.85247,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.36923,-0.00903,0.08302]},{"body_a":"world","body_b":"grasp_target","contact_count":2372.0,"contact_point_centroid":[0.44495,-0.0242,-0.00251],"force_p95":0.33574,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.07316,"mean_force":0.17153,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39208,-0.01035,0.12059]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.43335,-0.02607,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.36808,-0.01414,0.10505]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.43335,-0.02607,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.36873,-0.01411,0.10482]},{"body_a":"world","body_b":"grasp_target","contact_count":1468.0,"contact_point_centroid":[0.43335,-0.02607,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.39769,-0.01992,0.15814]}],"total_contact_groups":26},"final_pose_error":0.17936,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.43335,-0.02607,0.01602],"final_tcp_position":[0.49373,0.06803,0.22001],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273008.94579,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":669.0,"n_steps_budget":1000.0,"object_pos_end":[0.43335,-0.02607,0.01602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.32223,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":203.16729,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3160.0,"raw_peak_contact_force":1518.28928,"subtask_id":"approach_object","tcp_end":[0.36808,-0.01414,0.10505],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11103,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.43335,-0.02607,0.01602],"object_pos_start":[0.43335,-0.02607,0.01602],"object_to_goal_dist_end":0.32223,"object_to_goal_dist_start":0.32223,"object_z_max":0.01602,"peak_contact_force":764.48086,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":532.97037,"subtask_id":"grasp_contact","tcp_end":[0.36821,-0.01412,0.10528],"tcp_start":[0.36808,-0.01414,0.10505],"tcp_to_object_dist_end":0.11114,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.43335,-0.02607,0.01602],"object_pos_start":[0.43335,-0.02607,0.01602],"object_to_goal_dist_end":0.32223,"object_to_goal_dist_start":0.32223,"object_z_max":0.01602,"peak_contact_force":66.39164,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3505.0,"raw_peak_contact_force":117.96652,"tcp_end":[0.36886,-0.01414,0.10461],"tcp_start":[0.36886,-0.01414,0.10461],"tcp_to_object_dist_end":0.11022,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":367.0,"n_steps_budget":600.0,"object_pos_end":[0.43335,-0.02607,0.01602],"object_pos_start":[0.43335,-0.02607,0.01602],"object_to_goal_dist_end":0.32223,"object_to_goal_dist_start":0.32223,"object_z_max":0.01602,"peak_contact_force":273008.94579,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3007.0,"raw_peak_contact_force":92.99165,"tcp_end":[0.42533,-0.02511,0.20811],"tcp_start":[0.42464,-0.02489,0.20683],"tcp_to_object_dist_end":0.19226,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43335,-0.02607,0.01602],"object_pos_start":[0.43335,-0.02607,0.01602],"object_to_goal_dist_end":0.32223,"object_to_goal_dist_start":0.32223,"object_z_max":0.01602,"peak_contact_force":273003.19844,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9206.0,"raw_peak_contact_force":1022.68701,"subtask_id":"place_goal","tcp_end":[0.45902,0.04999,0.19601],"tcp_start":[0.42533,-0.02511,0.20811],"tcp_to_object_dist_end":0.19708,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.43335,-0.02607,0.01602],"object_pos_start":[0.43335,-0.02607,0.01602],"object_to_goal_dist_end":0.32223,"object_to_goal_dist_start":0.32223,"object_z_max":0.01602,"peak_contact_force":187.07425,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":19.0,"raw_peak_contact_force":240.36483,"tcp_end":[0.45904,0.04972,0.19609],"tcp_start":[0.45902,0.04999,0.19601],"tcp_to_object_dist_end":0.19706,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.43335,-0.02607,0.01602],"object_pos_start":[0.43335,-0.02607,0.01602],"object_to_goal_dist_end":0.32223,"object_to_goal_dist_start":0.32223,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1095.0,"raw_peak_contact_force":712.71009,"tcp_end":[0.45596,0.04793,0.21706],"tcp_start":[0.45904,0.04972,0.19609],"tcp_to_object_dist_end":0.21542,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":155.0,"n_steps_budget":600.0,"object_pos_end":[0.43335,-0.02607,0.01602],"object_pos_start":[0.43335,-0.02607,0.01602],"object_to_goal_dist_end":0.32223,"object_to_goal_dist_start":0.32223,"object_z_max":0.01602,"peak_contact_force":452.3015,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":902.0,"raw_peak_contact_force":1148.20306,"tcp_end":[0.49373,0.06803,0.22001],"tcp_start":[0.45596,0.04793,0.21706],"tcp_to_object_dist_end":0.23262,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.04274,"average_solve_count":117.0,"average_success_count":117.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.place_approach_z":0.09208,"approach_goal.place_transport_speed":0.41525,"approach_object.approach_offset_z":0.2258,"approach_object.approach_speed":0.42815,"descend_grasp.descend_force_thresh":10.30184,"descend_place.place_force_thresh":13.69799,"lift_object.lift_height":0.19638,"lift_object.lift_speed":0.10842,"release_object.release_duration":1.32867,"retract_after_place.retract_speed":0.19653},"optimized_scores":{"best_composite_score":-0.24294,"best_fitness_score":0.18706,"best_task_score":0.11041},"replay_outcomes":[{"contacts":{"omitted_contact_groups":5,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":733.0,"contact_point_centroid":[0.61719,-0.0161,-0.0005],"force_p95":212.55761,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1335.97831,"mean_force":213.33739,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.36801,-0.01209,0.09573]},{"body_a":"world","body_b":"link6","contact_count":484.0,"contact_point_centroid":[0.59367,0.0402,-0.00051],"force_p95":879.23954,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1190.0353,"mean_force":488.14414,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.42869,0.02553,0.22381]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.61073,-0.02419,-0.00027],"force_p95":541.92487,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":541.92487,"mean_force":541.92487,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.36406,-0.01787,0.09637]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.61161,-0.02421,-0.00013],"force_p95":83.23592,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":115.015,"mean_force":71.75642,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.36475,-0.01796,0.09616]},{"body_a":"world","body_b":"link6","contact_count":7.0,"contact_point_centroid":[0.61178,-0.02427,-0.0001],"force_p95":74.43504,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":92.4425,"mean_force":19.88375,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.3649,-0.01802,0.09621]},{"body_a":"grasp_target","body_b":"hand","contact_count":39.0,"contact_point_centroid":[0.43751,-0.01988,0.04212],"force_p95":3.44459,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.8331,"mean_force":1.58361,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37186,-0.00794,0.05309]},{"body_a":"world","body_b":"grasp_target","contact_count":3311.0,"contact_point_centroid":[0.42343,-0.02524,-0.00215],"force_p95":0.13839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.27382,"mean_force":0.14072,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38425,-0.01125,0.11001]},{"body_a":"grasp_target","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.46755,-0.01195,0.0102],"force_p95":0.45533,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.47873,"mean_force":0.17484,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.36111,-0.00795,0.0522]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.4175,-0.02506,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.36406,-0.01787,0.09637]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.4175,-0.02506,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.36475,-0.01796,0.09616]},{"body_a":"world","body_b":"grasp_target","contact_count":1416.0,"contact_point_centroid":[0.4175,-0.02506,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.38766,-0.02141,0.14758]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.4175,-0.02506,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.4599,0.1643,0.26376]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.4175,-0.02506,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59984,0.37828,0.42049]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.4175,-0.02506,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60103,0.37826,0.42658]},{"body_a":"world","body_b":"grasp_target","contact_count":2944.0,"contact_point_centroid":[0.4175,-0.02506,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.61085,0.30684,0.41722]},{"body_a":"left_finger","body_b":"right_finger","contact_count":747.0,"contact_point_centroid":[0.36706,-0.018,0.09543],"force_p95":0.0132,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01101,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.36488,-0.018,0.09597]}],"total_contact_groups":21},"final_pose_error":0.20277,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.4175,-0.02506,0.01602],"final_tcp_position":[0.63272,0.21634,0.41671],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1335.97831,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":846.0,"n_steps_budget":1000.0,"object_pos_end":[0.4175,-0.02506,0.01602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.33054,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":211.15233,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4124.0,"raw_peak_contact_force":1335.97831,"subtask_id":"approach_object","tcp_end":[0.36406,-0.01787,0.09637],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09677,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.4175,-0.02506,0.01602],"object_pos_start":[0.4175,-0.02506,0.01602],"object_to_goal_dist_end":0.33054,"object_to_goal_dist_start":0.33054,"object_z_max":0.01602,"peak_contact_force":820.49859,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":541.92487,"subtask_id":"grasp_contact","tcp_end":[0.36419,-0.01786,0.09661],"tcp_start":[0.36406,-0.01787,0.09637],"tcp_to_object_dist_end":0.09689,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.4175,-0.02506,0.01602],"object_pos_start":[0.4175,-0.02506,0.01602],"object_to_goal_dist_end":0.33054,"object_to_goal_dist_start":0.33054,"object_z_max":0.01602,"peak_contact_force":67.18252,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3497.0,"raw_peak_contact_force":115.015,"tcp_end":[0.36488,-0.018,0.09596],"tcp_start":[0.36488,-0.018,0.09597],"tcp_to_object_dist_end":0.09596,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":354.0,"n_steps_budget":750.0,"object_pos_end":[0.4175,-0.02506,0.01602],"object_pos_start":[0.4175,-0.02506,0.01602],"object_to_goal_dist_end":0.33054,"object_to_goal_dist_start":0.33054,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":2899.0,"raw_peak_contact_force":92.4425,"tcp_end":[0.41002,-0.02447,0.19586],"tcp_start":[0.40939,-0.02433,0.1944],"tcp_to_object_dist_end":0.18,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4175,-0.02506,0.01602],"object_pos_start":[0.4175,-0.02506,0.01602],"object_to_goal_dist_end":0.33054,"object_to_goal_dist_start":0.33054,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8716.0,"raw_peak_contact_force":1190.0353,"subtask_id":"place_goal","tcp_end":[0.59984,0.37828,0.42049],"tcp_start":[0.41002,-0.02447,0.19586],"tcp_to_object_dist_end":0.59961,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.4175,-0.02506,0.01602],"object_pos_start":[0.4175,-0.02506,0.01602],"object_to_goal_dist_end":0.33054,"object_to_goal_dist_start":0.33054,"object_z_max":0.01602,"peak_contact_force":317.74011,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59989,0.37831,0.42056],"tcp_start":[0.59984,0.37828,0.42049],"tcp_to_object_dist_end":0.59969,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4175,-0.02506,0.01602],"object_pos_start":[0.4175,-0.02506,0.01602],"object_to_goal_dist_end":0.33054,"object_to_goal_dist_start":0.33054,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60185,0.3789,0.44614],"tcp_start":[0.59989,0.37831,0.42056],"tcp_to_object_dist_end":0.6182,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":736.0,"n_steps_budget":930.0,"object_pos_end":[0.4175,-0.02506,0.01602],"object_pos_start":[0.4175,-0.02506,0.01602],"object_to_goal_dist_end":0.33054,"object_to_goal_dist_start":0.33054,"object_z_max":0.01602,"peak_contact_force":107.66771,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2944.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63272,0.21634,0.41671],"tcp_start":[0.60185,0.3789,0.44614],"tcp_to_object_dist_end":0.51492,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":13.0,"average_failure_rate":0.125,"average_mean_iterations":31.20192,"average_solve_count":104.0,"average_success_count":91.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.place_approach_z":0.17413,"approach_goal.place_transport_speed":0.40584,"approach_object.approach_offset_z":0.17225,"approach_object.approach_speed":0.22203,"descend_grasp.descend_force_thresh":12.10638,"descend_place.place_force_thresh":12.48106,"lift_object.lift_height":0.1986,"lift_object.lift_speed":0.09708,"release_object.release_duration":1.34974,"retract_after_place.retract_speed":0.44184},"optimized_scores":{"best_composite_score":-0.21852,"best_fitness_score":0.21148,"best_task_score":0.24228},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":832.0,"contact_point_centroid":[0.65501,0.00063,-0.00043],"force_p95":485.33559,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1465.95542,"mean_force":227.04701,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.43177,0.00041,0.14907]},{"body_a":"world","body_b":"link6","contact_count":34.0,"contact_point_centroid":[0.50096,-0.17213,-0.00359],"force_p95":1034.82464,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1392.77573,"mean_force":419.37547,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.31884,-0.10119,0.18994]},{"body_a":"world","body_b":"link5","contact_count":219.0,"contact_point_centroid":[0.65104,0.11898,-0.00054],"force_p95":458.68284,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":722.33318,"mean_force":290.73003,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49299,-0.02108,0.17473]},{"body_a":"link5","body_b":"hand","contact_count":190.0,"contact_point_centroid":[0.519,0.0861,0.11977],"force_p95":289.10982,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":580.11143,"mean_force":139.36352,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48273,-0.01351,0.16842]},{"body_a":"world","body_b":"link6","contact_count":46.0,"contact_point_centroid":[0.69067,0.00664,-0.0001],"force_p95":381.52117,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":486.00299,"mean_force":277.45506,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46539,0.00185,0.16086]},{"body_a":"world","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.54211,0.00364,-0.00347],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":312.68417,"mean_force":13.59496,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39114,-1e-05,0.04674]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.68365,0.00354,-0.00012],"force_p95":71.37178,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":199.61267,"mean_force":68.0995,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46428,-2e-05,0.16241]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.68287,0.00302,-0.00053],"force_p95":130.92233,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":130.92233,"mean_force":130.92233,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.46411,-0.00029,0.16241]},{"body_a":"grasp_target","body_b":"link7","contact_count":213.0,"contact_point_centroid":[0.52538,0.00275,0.03161],"force_p95":3.42762,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.42684,"mean_force":0.64072,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40513,0.00012,0.09642]},{"body_a":"grasp_target","body_b":"hand","contact_count":109.0,"contact_point_centroid":[0.50362,-0.00192,0.04385],"force_p95":2.33753,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.11671,"mean_force":0.96181,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40041,6e-05,0.07767]},{"body_a":"world","body_b":"grasp_target","contact_count":3610.0,"contact_point_centroid":[0.51404,0.00313,-0.00232],"force_p95":0.34537,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.0946,"mean_force":0.15783,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.44341,0.00043,0.16037]},{"body_a":"grasp_target","body_b":"link6","contact_count":152.0,"contact_point_centroid":[0.52188,0.03619,0.05613],"force_p95":1.03685,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.52859,"mean_force":0.27571,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47124,0.07165,0.32595]},{"body_a":"grasp_target","body_b":"link6","contact_count":84.0,"contact_point_centroid":[0.5519,0.01406,0.02242],"force_p95":0.72262,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.90996,"mean_force":0.42162,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39693,5e-05,0.07816]},{"body_a":"world","body_b":"grasp_target","contact_count":1853.0,"contact_point_centroid":[0.5384,0.04256,-0.0026],"force_p95":0.5447,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.8502,"mean_force":0.17153,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50435,0.04014,0.31336]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.50788,0.00341,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.46411,-0.00029,0.16241]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.50788,0.00341,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46428,-2e-05,0.16241]}],"total_contact_groups":25},"final_pose_error":0.04972,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.55925,0.0759,0.01602],"final_tcp_position":[0.6436,0.14837,0.3397],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273041.41227,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.50788,0.00341,0.01602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.27223,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":179.30085,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4871.0,"raw_peak_contact_force":1465.95542,"subtask_id":"approach_object","tcp_end":[0.46411,-0.00029,0.16241],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15284,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50788,0.00341,0.01602],"object_pos_start":[0.50788,0.00341,0.01602],"object_to_goal_dist_end":0.27223,"object_to_goal_dist_start":0.27223,"object_z_max":0.01602,"peak_contact_force":130.92233,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":130.92233,"subtask_id":"grasp_contact","tcp_end":[0.46415,-0.00029,0.16249],"tcp_start":[0.46411,-0.00029,0.16241],"tcp_to_object_dist_end":0.1529,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50788,0.00341,0.01602],"object_pos_start":[0.50788,0.00341,0.01602],"object_to_goal_dist_end":0.27223,"object_to_goal_dist_start":0.27223,"object_z_max":0.01602,"peak_contact_force":273004.12068,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3526.0,"raw_peak_contact_force":199.61267,"tcp_end":[0.46427,-5e-05,0.1623],"tcp_start":[0.46427,-4e-05,0.1623],"tcp_to_object_dist_end":0.15268,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":520.0,"n_steps_budget":600.0,"object_pos_end":[0.50788,0.00341,0.01602],"object_pos_start":[0.50788,0.00341,0.01602],"object_to_goal_dist_end":0.27223,"object_to_goal_dist_start":0.27223,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4844.0,"raw_peak_contact_force":722.33318,"tcp_end":[0.51657,-0.00464,0.35879],"tcp_start":[0.5175,-0.0022,0.29804],"tcp_to_object_dist_end":0.34297,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":587.0,"n_steps_budget":1000.0,"object_pos_end":[0.55925,0.0759,0.01602],"object_pos_start":[0.50788,0.00341,0.01602],"object_to_goal_dist_end":0.21265,"object_to_goal_dist_start":0.27223,"object_z_max":0.02523,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4560.0,"raw_peak_contact_force":1392.77573,"subtask_id":"place_goal","tcp_end":[0.63679,0.14358,0.35674],"tcp_start":[0.51657,-0.00464,0.35879],"tcp_to_object_dist_end":0.35593,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":14.0,"n_steps_budget":1000.0,"object_pos_end":[0.55925,0.0759,0.01602],"object_pos_start":[0.55925,0.0759,0.01602],"object_to_goal_dist_end":0.21265,"object_to_goal_dist_start":0.21265,"object_z_max":0.01602,"peak_contact_force":273019.64199,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":112.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63694,0.14455,0.35397],"tcp_start":[0.63679,0.14358,0.35674],"tcp_to_object_dist_end":0.3535,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55925,0.0759,0.01602],"object_pos_start":[0.55925,0.0759,0.01602],"object_to_goal_dist_end":0.21265,"object_to_goal_dist_start":0.21265,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1032.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63789,0.14389,0.37383],"tcp_start":[0.63694,0.14455,0.35397],"tcp_to_object_dist_end":0.37261,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":40.0,"n_steps_budget":600.0,"object_pos_end":[0.55925,0.0759,0.01602],"object_pos_start":[0.55925,0.0759,0.01602],"object_to_goal_dist_end":0.21265,"object_to_goal_dist_start":0.21265,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":160.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6436,0.14837,0.3397],"tcp_start":[0.63789,0.14389,0.37383],"tcp_to_object_dist_end":0.34225,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```