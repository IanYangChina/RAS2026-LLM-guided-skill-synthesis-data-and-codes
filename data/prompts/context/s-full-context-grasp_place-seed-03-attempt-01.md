## Search State

- **Seed**: 3
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | contact_detected | time_limit | pose_tolerance | 7 | -0.3656 | 0.19 | ✅ accepted |
| 0 | rotate → retract → descend → pull → rotate | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.0374 | 0.17 | ✅ accepted |

**Proposal policy**: task_score is 0.19 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`
- Frozen object start: [0.45856491671436245, -0.02631894934039003, 0.03]
- Frozen task target: [0.6301274465206397, 0.20821620360643678, 0.11411929633605987]
- Goal object position: (0.6301274465206397, 0.20821620360643678, 0.11411929633605987)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6301274465206397, 0.20821620360643678, 0.11411929633605987)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.45856491671436245, -0.02631894934039003, 0.03)
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
  frozen_object_start: [0.4586, -0.0263, 0.03]
  frozen_task_target: [0.6301, 0.2082, 0.1141]
  frozen_object_starts: {'grasp_target': [0.45856491671436245, -0.02631894934039003, 0.03]}
  frozen_targets: {'place_target': [0.6301274465206397, 0.20821620360643678, 0.11411929633605987]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7

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
| `object` | offset from object initial position (0.45856491671436245, -0.02631894934039003, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6301274465206397, 0.20821620360643678, 0.11411929633605987) | final destination targets |
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

## Current Skill (Q=-0.366) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_pregrasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: grasp_contact
  anchor: object
  metric: contact
  weight: 0.3
- id: lift_clear
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: place_goal
  target_entity: object
  weight: 0.2
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    approach_z:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_pregrasp
- id: descend_to_object
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    descend_offset_z:
      type: scalar
      range:
      - 0.0
      - 0.04
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: check_contact
    when: during_phase
    predicate: contact_detected
    threshold: 0.5
    on_failure: continue
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: grasp_contact
- id: grasp_object
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  guards:
  - id: check_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
  subtask_id: grasp_contact
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
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: lift_clear
- id: approach_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    approach_goal_z:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: place_goal
- id: descend_at_goal
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_goal
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    descend_goal_z:
      type: scalar
      range:
      - 0.0
      - 0.04
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: place_goal
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
  retries:
    max_attempts: 0
    strategy: repeat
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
    - 0.2
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    retract_z:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - approach_z: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_to_object** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - descend_offset_z: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=check_contact, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=0.5
  - retries: max_attempts=0, strategy=repeat
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=check_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=repeat
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=0, strategy=repeat
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - approach_goal_z: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_at_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=grasp_target, offset=[0.0, 0.0, 0.02]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - descend_goal_z: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=0, strategy=repeat
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
  - retries: max_attempts=0, strategy=repeat
- **retract_after_place** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.2], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_z: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: -0.366
- **task_score** (E): 0.195
- **fitness_score**: 0.164  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.530

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.00 | 1.00 | 0.1336 |
| descend_to_object | 1.00 | 1.00 | 0.0421 |
| grasp_object | 1.00 | 1.00 | 0.0000 |
| lift_object | 0.00 | 1.00 | 0.0342 |
| approach_goal | 0.00 | 1.00 | 0.0693 |
| descend_at_goal | 1.00 | 1.00 | 0.0599 |
| release_object | 1.00 | 1.00 | 0.0266 |
| retract_after_place | 0.33 | 1.00 | 0.1358 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.431, 0.001, 0.187) | (0.511, 0.002, 0.030)→(0.475, 0.013, 0.016) | 0.244→0.262 | 1.00 / 5.000 | 217.416 | 1444.662 |
| descend_to_object | descend | 1.00 / step_budget | (0.431, 0.001, 0.187)→(0.454, 0.005, 0.209) | (0.475, 0.013, 0.016)→(0.475, 0.013, 0.016) | 0.262→0.262 | 1.00 / 5.000 | 373.612 | 871.871 |
| grasp_object | grasp | 1.00 / step_budget | (0.454, 0.005, 0.208)→(0.454, 0.005, 0.208) | (0.475, 0.013, 0.016)→(0.475, 0.013, 0.016) | 0.262→0.262 | 1.00 / 9.333 | 91049.305 | 397.692 |
| lift_object | lift | 0.00 / step_budget | (0.454, 0.005, 0.208)→(0.443, 0.023, 0.205) | (0.475, 0.013, 0.016)→(0.475, 0.013, 0.016) | 0.262→0.262 | 1.00 / 9.000 | 332.618 | 673.859 |
| approach_goal | approach | 0.00 / step_budget | (0.443, 0.023, 0.205)→(0.431, 0.083, 0.208) | (0.475, 0.013, 0.016)→(0.475, 0.013, 0.016) | 0.262→0.262 | 1.00 / 9.000 | 146.136 | 773.824 |
| descend_at_goal | descend | 1.00 / step_budget | (0.431, 0.083, 0.208)→(0.467, 0.085, 0.238) | (0.475, 0.013, 0.016)→(0.470, 0.021, 0.015) | 0.262→0.260 | 1.00 / 10.333 | 403.221 | 883.110 |
| release_object | release | 1.00 / step_budget | (0.467, 0.085, 0.238)→(0.467, 0.084, 0.265) | (0.470, 0.021, 0.015)→(0.472, 0.020, 0.020) | 0.260→0.258 | 1.00 / 4.667 | 66.151 | 269.167 |
| retract_after_place | retract | 0.33 / step_budget | (0.467, 0.084, 0.265)→(0.461, 0.070, 0.398) | (0.472, 0.020, 0.020)→(0.474, 0.019, 0.016) | 0.258→0.258 | 1.00 / 5.667 | 45.069 | 136.168 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.304
- phase_score: 0.369
- phase_breakdown.lift_clear_score: 0.150
- phase_breakdown.reach_pregrasp_score: 0.099
- phase_breakdown.grasp_contact_score: 1.000
- phase_breakdown.place_goal_score: 0.020
- grasp_place_fitness: 0.216

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.216
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.304
- **Median Q (composite search score)**: -0.375
- **K-run variance**: 0.0015
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.282


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a4a71a7b2980790489e8194d1356bdee33fb951291c2e0792659ad3d3b3dc711`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `8a78b0f0015ebaf8c4b14c8fbc8142d9b66e4b4efca10f362859101c0ae207df`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.24444,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.18831,"approach_object.approach_z":0.14943,"descend_at_goal.descend_goal_z":0.02151,"descend_to_object.descend_offset_z":0.02683,"lift_object.lift_height":0.10655,"release_object.release_duration":1.12674,"retract_after_place.retract_z":0.20666},"optimized_scores":{"best_composite_score":-0.40818,"best_fitness_score":0.12182,"best_task_score":0.11058},"replay_outcomes":[{"contacts":{"omitted_contact_groups":10,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.62934,-0.00698,-0.00047],"force_p95":202.16679,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1435.48771,"mean_force":204.44406,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38563,-0.0068,0.11815]},{"body_a":"world","body_b":"link6","contact_count":999.0,"contact_point_centroid":[0.61632,-0.0157,-0.00024],"force_p95":396.91999,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":865.95099,"mean_force":247.47675,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.41444,-0.01758,0.18376]},{"body_a":"world","body_b":"link6","contact_count":976.0,"contact_point_centroid":[0.51441,0.02338,-0.00028],"force_p95":605.46292,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":792.40998,"mean_force":436.25115,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.40432,-0.01066,0.26139]},{"body_a":"world","body_b":"link6","contact_count":984.0,"contact_point_centroid":[0.54805,-0.00186,-0.00022],"force_p95":453.56471,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":602.67394,"mean_force":298.54755,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.39405,-0.02307,0.23239]},{"body_a":"world","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.52407,0.00045,-0.0031],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":466.70841,"mean_force":21.21402,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37021,-0.00324,0.05006]},{"body_a":"world","body_b":"link6","contact_count":539.0,"contact_point_centroid":[0.60128,-0.02811,-0.00024],"force_p95":223.36737,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":258.94863,"mean_force":197.84665,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.40474,-0.03407,0.19472]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.63608,-0.02332,-0.00014],"force_p95":94.2934,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":198.48426,"mean_force":76.03038,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45257,-0.02604,0.2115]},{"body_a":"link5","body_b":"hand","contact_count":103.0,"contact_point_centroid":[0.45933,0.09547,0.22036],"force_p95":133.65876,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":147.62997,"mean_force":64.82505,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.4238,-0.00034,0.24995]},{"body_a":"link5","body_b":"hand","contact_count":1157.0,"contact_point_centroid":[0.45298,0.09566,0.31607],"force_p95":97.87151,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":125.85227,"mean_force":55.73213,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.41341,-0.01328,0.33711]},{"body_a":"world","body_b":"link6","contact_count":71.0,"contact_point_centroid":[0.55223,0.05194,-0.00017],"force_p95":100.37263,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":120.57777,"mean_force":77.4839,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.42513,0.00031,0.24839]},{"body_a":"link5","body_b":"hand","contact_count":91.0,"contact_point_centroid":[0.4587,0.09916,0.22131],"force_p95":32.90102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":33.37764,"mean_force":14.59638,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.4251,0.0003,0.24846]},{"body_a":"grasp_target","body_b":"hand","contact_count":38.0,"contact_point_centroid":[0.43919,-0.01298,0.04248],"force_p95":3.4555,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.83752,"mean_force":1.57904,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.381,-0.0032,0.05116]},{"body_a":"world","body_b":"grasp_target","contact_count":3926.0,"contact_point_centroid":[0.42232,-0.02479,-0.00212],"force_p95":0.13751,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.30392,"mean_force":0.13774,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39802,-0.0063,0.12825]},{"body_a":"grasp_target","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.47193,-0.00712,0.00821],"force_p95":0.65805,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.66908,"mean_force":0.48661,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.36882,-0.00321,0.0453]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.41731,-0.02456,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.41448,-0.01758,0.18379]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.41731,-0.02456,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45257,-0.02604,0.2115]}],"total_contact_groups":26},"final_pose_error":0.12169,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.41731,-0.02456,0.01602],"final_tcp_position":[0.40887,-0.03409,0.36725],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273004.12076,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41731,-0.02456,0.01602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.3303,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":200.26305,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4880.0,"raw_peak_contact_force":1435.48771,"subtask_id":"reach_pregrasp","tcp_end":[0.39216,-0.01222,0.14301],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13005,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41731,-0.02456,0.01602],"object_pos_start":[0.41731,-0.02456,0.01602],"object_to_goal_dist_end":0.3303,"object_to_goal_dist_start":0.3303,"object_z_max":0.01602,"peak_contact_force":385.82137,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4999.0,"raw_peak_contact_force":865.95099,"subtask_id":"grasp_contact","tcp_end":[0.45271,-0.02599,0.21232],"tcp_start":[0.39216,-0.01222,0.14301],"tcp_to_object_dist_end":0.19947,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.41731,-0.02456,0.01602],"object_pos_start":[0.41731,-0.02456,0.01602],"object_to_goal_dist_end":0.3303,"object_to_goal_dist_start":0.3303,"object_z_max":0.01602,"peak_contact_force":71.73894,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3503.0,"raw_peak_contact_force":198.48426,"subtask_id":"grasp_contact","tcp_end":[0.45258,-0.02606,0.21142],"tcp_start":[0.45258,-0.02605,0.21142],"tcp_to_object_dist_end":0.19856,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.41731,-0.02456,0.01602],"object_pos_start":[0.41731,-0.02456,0.01602],"object_to_goal_dist_end":0.3303,"object_to_goal_dist_start":0.3303,"object_z_max":0.01602,"peak_contact_force":199.32202,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5011.0,"raw_peak_contact_force":258.94863,"subtask_id":"lift_clear","tcp_end":[0.4154,-0.03494,0.21707],"tcp_start":[0.45258,-0.02606,0.21142],"tcp_to_object_dist_end":0.20133,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41731,-0.02456,0.01602],"object_pos_start":[0.41731,-0.02456,0.01602],"object_to_goal_dist_end":0.3303,"object_to_goal_dist_start":0.3303,"object_z_max":0.01602,"peak_contact_force":433.68953,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9252.0,"raw_peak_contact_force":602.67394,"subtask_id":"place_goal","tcp_end":[0.41777,-0.00563,0.25272],"tcp_start":[0.4154,-0.03494,0.21707],"tcp_to_object_dist_end":0.23746,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41731,-0.02456,0.01602],"object_pos_start":[0.41731,-0.02456,0.01602],"object_to_goal_dist_end":0.3303,"object_to_goal_dist_start":0.3303,"object_z_max":0.01602,"peak_contact_force":455.40009,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9455.0,"raw_peak_contact_force":792.40998,"subtask_id":"place_goal","tcp_end":[0.42522,0.0003,0.24856],"tcp_start":[0.41777,-0.00563,0.25272],"tcp_to_object_dist_end":0.234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.41731,-0.02456,0.01602],"object_pos_start":[0.41731,-0.02456,0.01602],"object_to_goal_dist_end":0.3303,"object_to_goal_dist_start":0.3303,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1195.0,"raw_peak_contact_force":120.57777,"tcp_end":[0.42416,-0.00037,0.27652],"tcp_start":[0.42522,0.0003,0.24856],"tcp_to_object_dist_end":0.26171,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41731,-0.02456,0.01602],"object_pos_start":[0.41731,-0.02456,0.01602],"object_to_goal_dist_end":0.3303,"object_to_goal_dist_start":0.3303,"object_z_max":0.01602,"peak_contact_force":78.75173,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":5157.0,"raw_peak_contact_force":125.85227,"tcp_end":[0.40887,-0.03409,0.36725],"tcp_start":[0.42416,-0.00037,0.27652],"tcp_to_object_dist_end":0.35146,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `aa6ec658384c70fac6b4eb656cc8c53536c3d5c760368ab2b384dccf294e2c48`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.30597,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.10001,"approach_object.approach_z":0.11725,"descend_at_goal.descend_goal_z":0.00914,"descend_to_object.descend_offset_z":0.03939,"lift_object.lift_height":0.14046,"release_object.release_duration":1.40375,"retract_after_place.retract_z":0.271},"optimized_scores":{"best_composite_score":-0.3746,"best_fitness_score":0.1554,"best_task_score":0.1695},"replay_outcomes":[{"contacts":{"omitted_contact_groups":11,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.63831,0.00158,-0.00046],"force_p95":249.41178,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1448.72605,"mean_force":203.35831,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.41869,0.00016,0.15661]},{"body_a":"world","body_b":"link6","contact_count":981.0,"contact_point_centroid":[0.61483,0.06284,-0.00025],"force_p95":458.00974,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":939.75617,"mean_force":298.86715,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.42541,0.11718,0.19412]},{"body_a":"world","body_b":"link6","contact_count":996.0,"contact_point_centroid":[0.61754,0.00513,-0.00024],"force_p95":455.31793,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":907.26984,"mean_force":290.11986,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.43224,0.00274,0.20652]},{"body_a":"world","body_b":"link6","contact_count":505.0,"contact_point_centroid":[0.63412,0.00822,-0.00026],"force_p95":507.32733,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":885.30103,"mean_force":279.85819,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.43976,0.01156,0.19738]},{"body_a":"world","body_b":"link6","contact_count":986.0,"contact_point_centroid":[0.61585,0.0358,-0.00024],"force_p95":377.34769,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":790.73916,"mean_force":279.19234,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.43148,0.06545,0.20587]},{"body_a":"world","body_b":"link6","contact_count":546.0,"contact_point_centroid":[0.65642,0.01434,-0.00013],"force_p95":78.08563,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":732.74867,"mean_force":72.77885,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45916,0.00699,0.19866]},{"body_a":"world","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.53393,0.00415,-0.00346],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":469.01352,"mean_force":22.33398,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38046,-0.00014,0.05005]},{"body_a":"world","body_b":"link6","contact_count":70.0,"contact_point_centroid":[0.65966,0.08984,-8e-05],"force_p95":156.44943,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":462.49302,"mean_force":79.37412,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.44017,0.11019,0.17615]},{"body_a":"link5","body_b":"hand","contact_count":124.0,"contact_point_centroid":[0.50764,0.12649,0.37364],"force_p95":60.86536,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":83.86844,"mean_force":31.57926,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.43571,0.09819,0.33936]},{"body_a":"grasp_target","body_b":"link6","contact_count":300.0,"contact_point_centroid":[0.54214,0.01703,0.03238],"force_p95":0.74739,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.68492,"mean_force":0.35189,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39743,1e-05,0.11409]},{"body_a":"grasp_target","body_b":"link7","contact_count":314.0,"contact_point_centroid":[0.52936,0.00524,0.03375],"force_p95":1.45102,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.2231,"mean_force":0.46225,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.3982,1e-05,0.11139]},{"body_a":"grasp_target","body_b":"hand","contact_count":87.0,"contact_point_centroid":[0.49898,0.01396,0.04512],"force_p95":2.55633,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.22231,"mean_force":1.05098,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38955,-8e-05,0.0758]},{"body_a":"world","body_b":"grasp_target","contact_count":3730.0,"contact_point_centroid":[0.51495,0.01027,-0.00215],"force_p95":0.25471,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.53207,"mean_force":0.14768,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.43027,0.00018,0.16631]},{"body_a":"left_finger","body_b":"link5","contact_count":2979.0,"contact_point_centroid":[0.45358,0.12055,0.30399],"force_p95":0.8169,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2.38845,"mean_force":0.3774,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.43678,0.10377,0.27698]},{"body_a":"left_finger","body_b":"link5","contact_count":206.0,"contact_point_centroid":[0.45471,0.12402,0.21838],"force_p95":1.60203,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2.00967,"mean_force":0.93752,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.43881,0.10751,0.19122]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50997,0.0122,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.43232,0.00275,0.20651]}],"total_contact_groups":27},"final_pose_error":0.12459,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.50997,0.0122,0.01602],"final_tcp_position":[0.43549,0.09684,0.34723],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273004.12078,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50997,0.0122,0.01602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.26624,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":249.15498,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5338.0,"raw_peak_contact_force":1448.72605,"subtask_id":"reach_pregrasp","tcp_end":[0.45331,0.00048,0.20933],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20179,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50997,0.0122,0.01602],"object_pos_start":[0.50997,0.0122,0.01602],"object_to_goal_dist_end":0.26624,"object_to_goal_dist_start":0.26624,"object_z_max":0.01602,"peak_contact_force":355.38751,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4996.0,"raw_peak_contact_force":907.26984,"subtask_id":"grasp_contact","tcp_end":[0.45929,0.00698,0.19966],"tcp_start":[0.45331,0.00048,0.20933],"tcp_to_object_dist_end":0.19058,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50997,0.0122,0.01602],"object_pos_start":[0.50997,0.0122,0.01602],"object_to_goal_dist_end":0.26624,"object_to_goal_dist_start":0.26624,"object_z_max":0.01602,"peak_contact_force":273004.12078,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3499.0,"raw_peak_contact_force":732.74867,"subtask_id":"grasp_contact","tcp_end":[0.45916,0.00698,0.19857],"tcp_start":[0.45916,0.00699,0.19857],"tcp_to_object_dist_end":0.18956,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.50997,0.0122,0.01602],"object_pos_start":[0.50997,0.0122,0.01602],"object_to_goal_dist_end":0.26624,"object_to_goal_dist_start":0.26624,"object_z_max":0.01602,"peak_contact_force":410.48719,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4725.0,"raw_peak_contact_force":885.30103,"subtask_id":"lift_clear","tcp_end":[0.46074,0.02115,0.19606],"tcp_start":[0.45916,0.00698,0.19857],"tcp_to_object_dist_end":0.18686,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50997,0.0122,0.01602],"object_pos_start":[0.50997,0.0122,0.01602],"object_to_goal_dist_end":0.26624,"object_to_goal_dist_start":0.26624,"object_z_max":0.01602,"peak_contact_force":2.3594,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9208.0,"raw_peak_contact_force":790.73916,"subtask_id":"place_goal","tcp_end":[0.44027,0.10871,0.19311],"tcp_start":[0.46074,0.02115,0.19606],"tcp_to_object_dist_end":0.21339,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50997,0.0122,0.01602],"object_pos_start":[0.50997,0.0122,0.01602],"object_to_goal_dist_end":0.26624,"object_to_goal_dist_start":0.26624,"object_z_max":0.01602,"peak_contact_force":382.51128,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9200.0,"raw_peak_contact_force":939.75617,"subtask_id":"place_goal","tcp_end":[0.44019,0.11069,0.17653],"tcp_start":[0.44027,0.10871,0.19311],"tcp_to_object_dist_end":0.20083,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50997,0.0122,0.01602],"object_pos_start":[0.50997,0.0122,0.01602],"object_to_goal_dist_end":0.26624,"object_to_goal_dist_start":0.26624,"object_z_max":0.01602,"peak_contact_force":1.54743,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1288.0,"raw_peak_contact_force":462.49302,"tcp_end":[0.43836,0.10642,0.20042],"tcp_start":[0.44019,0.11069,0.17653],"tcp_to_object_dist_end":0.21911,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50997,0.0122,0.01602],"object_pos_start":[0.50997,0.0122,0.01602],"object_to_goal_dist_end":0.26624,"object_to_goal_dist_start":0.26624,"object_z_max":0.01602,"peak_contact_force":56.33382,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":7103.0,"raw_peak_contact_force":83.86844,"tcp_end":[0.43549,0.09684,0.34723],"tcp_start":[0.43836,0.10642,0.20042],"tcp_to_object_dist_end":0.34988,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e1209649252ffcf03853fe0727696e22a1eda11729c6c1ae21659980557d7e98`; realized-scene SHA-256: `e32d7866764afb23ec7c7faebb4bcca0aa39fbf2f1ab61f3c9c527b297153af9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.03008,"average_solve_count":133.0,"average_success_count":133.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.13556,"approach_object.approach_z":0.13342,"descend_at_goal.descend_goal_z":0.03119,"descend_to_object.descend_offset_z":0.01405,"lift_object.lift_height":0.13578,"release_object.release_duration":1.33246,"retract_after_place.retract_z":0.20915},"optimized_scores":{"best_composite_score":-0.31407,"best_fitness_score":0.21593,"best_task_score":0.30396},"replay_outcomes":[{"contacts":{"omitted_contact_groups":15,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.63717,0.00875,-0.00046],"force_p95":221.75385,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1449.77133,"mean_force":204.94419,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.41455,0.00764,0.15224]},{"body_a":"world","body_b":"link6","contact_count":981.0,"contact_point_centroid":[0.6144,0.08812,-0.00024],"force_p95":412.50256,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":928.05957,"mean_force":304.90718,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.42718,0.14103,0.20032]},{"body_a":"world","body_b":"link6","contact_count":924.0,"contact_point_centroid":[0.6001,0.15099,-0.00026],"force_p95":502.66568,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":917.1648,"mean_force":361.17343,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.43444,0.15741,0.21655]},{"body_a":"world","body_b":"link6","contact_count":492.0,"contact_point_centroid":[0.61269,0.0374,-0.00023],"force_p95":573.0925,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":877.3287,"mean_force":336.89794,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.43308,0.05359,0.21597]},{"body_a":"world","body_b":"link6","contact_count":997.0,"contact_point_centroid":[0.60357,0.01956,-0.00024],"force_p95":457.95344,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":842.39134,"mean_force":290.8082,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.42375,0.02315,0.21209]},{"body_a":"link5","body_b":"hand","contact_count":450.0,"contact_point_centroid":[0.48353,0.13887,0.22798],"force_p95":324.47474,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":654.65158,"mean_force":253.1123,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.46116,0.16894,0.23403]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.63352,0.02564,-0.00014],"force_p95":100.20853,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":261.84212,"mean_force":77.38505,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45048,0.03427,0.21426]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.46965,0.10576,0.23403],"force_p95":221.86523,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":224.42874,"mean_force":180.611,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.53725,0.14574,0.29649]},{"body_a":"link5","body_b":"hand","contact_count":189.0,"contact_point_centroid":[0.47269,0.10633,0.26451],"force_p95":178.25319,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":198.78423,"mean_force":87.12967,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.53751,0.14588,0.33003]},{"body_a":"world","body_b":"link6","contact_count":81.0,"contact_point_centroid":[0.58109,0.14936,-0.00015],"force_p95":80.24638,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":91.96264,"mean_force":59.84951,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.53681,0.14549,0.28982]},{"body_a":"grasp_target","body_b":"link7","contact_count":128.0,"contact_point_centroid":[0.50106,0.01982,0.03647],"force_p95":3.75924,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.87783,"mean_force":0.84428,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39008,0.00328,0.08568]},{"body_a":"grasp_target","body_b":"hand","contact_count":120.0,"contact_point_centroid":[0.49915,0.03948,0.05421],"force_p95":2.30184,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.17993,"mean_force":0.91248,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38948,0.00326,0.0843]},{"body_a":"world","body_b":"grasp_target","contact_count":3638.0,"contact_point_centroid":[0.50365,0.04692,-0.00225],"force_p95":0.35833,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.34723,"mean_force":0.15876,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.42718,0.0074,0.16337]},{"body_a":"grasp_target","body_b":"link6","contact_count":173.0,"contact_point_centroid":[0.50859,0.0738,0.03513],"force_p95":1.49468,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.87541,"mean_force":0.73572,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.52017,0.15259,0.28637]},{"body_a":"world","body_b":"grasp_target","contact_count":3776.0,"contact_point_centroid":[0.49759,0.05248,-0.00242],"force_p95":0.4401,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.17491,"mean_force":0.16653,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.42878,0.15853,0.21209]},{"body_a":"grasp_target","body_b":"link5","contact_count":88.0,"contact_point_centroid":[0.50324,0.06506,0.03556],"force_p95":0.36928,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.09998,"mean_force":0.2631,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.53279,0.1453,0.28931]}],"total_contact_groups":31},"final_pose_error":0.04699,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.49571,0.06798,0.01602],"final_tcp_position":[0.53954,0.14623,0.47919],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273004.12059,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49849,0.05039,0.01602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18849,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":202.83119,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4889.0,"raw_peak_contact_force":1449.77133,"subtask_id":"reach_pregrasp","tcp_end":[0.44758,0.01515,0.209],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20267,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49849,0.05039,0.01602],"object_pos_start":[0.49849,0.05039,0.01602],"object_to_goal_dist_end":0.18849,"object_to_goal_dist_start":0.18849,"object_z_max":0.01602,"peak_contact_force":379.62731,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4997.0,"raw_peak_contact_force":842.39134,"subtask_id":"grasp_contact","tcp_end":[0.45064,0.03428,0.21504],"tcp_start":[0.44758,0.01515,0.209],"tcp_to_object_dist_end":0.20533,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.49849,0.05039,0.01602],"object_pos_start":[0.49849,0.05039,0.01602],"object_to_goal_dist_end":0.18849,"object_to_goal_dist_start":0.18849,"object_z_max":0.01602,"peak_contact_force":72.05647,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3501.0,"raw_peak_contact_force":261.84212,"subtask_id":"grasp_contact","tcp_end":[0.45049,0.03423,0.21417],"tcp_start":[0.45049,0.03424,0.21417],"tcp_to_object_dist_end":0.20452,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49849,0.05039,0.01602],"object_pos_start":[0.49849,0.05039,0.01602],"object_to_goal_dist_end":0.18849,"object_to_goal_dist_start":0.18849,"object_z_max":0.01602,"peak_contact_force":388.04563,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4709.0,"raw_peak_contact_force":877.3287,"subtask_id":"lift_clear","tcp_end":[0.45348,0.08207,0.20165],"tcp_start":[0.45049,0.03423,0.21417],"tcp_to_object_dist_end":0.19362,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49849,0.05039,0.01602],"object_pos_start":[0.49849,0.05039,0.01602],"object_to_goal_dist_end":0.18849,"object_to_goal_dist_start":0.18849,"object_z_max":0.01602,"peak_contact_force":2.35894,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9216.0,"raw_peak_contact_force":928.05957,"subtask_id":"place_goal","tcp_end":[0.43376,0.14634,0.17678],"tcp_start":[0.45348,0.08207,0.20165],"tcp_to_object_dist_end":0.19809,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48391,0.07526,0.0121],"object_pos_start":[0.49849,0.05039,0.01602],"object_to_goal_dist_end":0.18364,"object_to_goal_dist_start":0.18849,"object_z_max":0.01602,"peak_contact_force":371.75144,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9608.0,"raw_peak_contact_force":917.1648,"subtask_id":"place_goal","tcp_end":[0.53651,0.14517,0.28956],"tcp_start":[0.43376,0.14634,0.17678],"tcp_to_object_dist_end":0.29093,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48777,0.07087,0.02653],"object_pos_start":[0.48391,0.07526,0.0121],"object_to_goal_dist_end":0.17663,"object_to_goal_dist_start":0.18364,"object_z_max":0.02708,"peak_contact_force":196.78241,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1330.0,"raw_peak_contact_force":224.42874,"tcp_end":[0.53793,0.14609,0.31701],"tcp_start":[0.53651,0.14517,0.28956],"tcp_to_object_dist_end":0.30422,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49571,0.06798,0.01602],"object_pos_start":[0.48777,0.07087,0.02653],"object_to_goal_dist_end":0.17863,"object_to_goal_dist_start":0.17663,"object_z_max":0.02653,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4133.0,"raw_peak_contact_force":198.78423,"tcp_end":[0.53954,0.14623,0.47919],"tcp_start":[0.53793,0.14609,0.31701],"tcp_to_object_dist_end":0.47177,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```