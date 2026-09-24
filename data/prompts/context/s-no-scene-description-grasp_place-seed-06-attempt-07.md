## Search State

- **Seed**: 6
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 15 | -0.1803 | 0.29 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 15 | -0.2966 | 0.31 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.2877 | 0.23 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | admittance_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 15 | -0.7858 | 0.17 | ❌ rejected |
| 3 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1415 | 0.25 | ✅ accepted |

**Proposal policy**: task_score is 0.29 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

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
| `object` | offset from object initial position | approach/contact targets near object start |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose | targets near fixture |

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

## Current Skill (Q=-0.180) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_pre_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.1
- id: reach_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.01
  weight: 0.1
- id: reach_lift
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.2
  weight: 0.2
- id: reach_place
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.4
- id: reach_retract
  offset:
  - 0.0
  - 0.0
  - 0.3
  weight: 0.2
phases:
- id: approach_pre_grasp
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: tcp
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.25
      default: 0.12
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_pre_grasp
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: tcp
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_z:
      type: scalar
      range:
      - -0.03
      - 0.0
      default: -0.01
      binds_to:
      - path: target.offset.z
        mode: add
    speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_grasp
- id: grasp_object
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    grasp_duration:
      type: scalar
      range:
      - 0.1
      - 0.8
      default: 0.4
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: grasp_success_guard
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.01
    - 0.0
  subtask_id: reach_grasp
- id: lift_object
  type: lift
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: tcp
    offset:
    - 0.0
    - 0.0
    - 0.25
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.35
      default: 0.25
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_lift
- id: transport_to_goal
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: tcp
    offset:
    - 0.0
    - 0.0
    - 0.2
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: object_grasped_guard
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.02
    on_failure: abort
  subtask_id: reach_place
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    entity: tcp
    offset:
    - 0.0
    - 0.0
    - -0.02
    orientation:
      mode: keep_current
  parameters:
    force_threshold:
      type: scalar
      range:
      - 1.0
      - 15.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    place_z_offset:
      type: scalar
      range:
      - -0.05
      - 0.0
      default: -0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
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
    orientation:
      mode: keep_current
  parameters:
    release_duration:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
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
    entity: tcp
    offset:
    - 0.0
    - 0.0
    - 0.3
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retract_z:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.3
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_retract

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_pre_grasp** (`approach`)
  - target: source=yaml, anchor=task_object, entity=tcp, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=tcp, offset=[0.0, 0.0, 0.02], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_z: status=consumed; consumers=target.offset.z (add)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_duration: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=grasp_success_guard, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.02
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.01, 0.0]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, entity=tcp, offset=[0.0, 0.0, 0.25], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=tcp, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=object_grasped_guard, when=during_phase, predicate=bilateral_grasp, on_failure=abort, threshold=0.02
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=tcp, offset=[0.0, 0.0, -0.02]
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
- **retract_after_place** (`retract`)
  - target: source=yaml, anchor=task_goal, entity=tcp, offset=[0.0, 0.0, 0.3], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.180
- **task_score** (E): 0.291
- **fitness_score**: 0.625  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.930

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_pre_grasp | 1.00 | 1.00 | 0.1218 |
| descend_to_grasp | 1.00 | 1.00 | 0.1526 |
| grasp_object | 1.00 | 1.00 | 0.0115 |
| lift_object | 1.00 | 1.00 | 0.2522 |
| transport_to_goal | 1.00 | 1.00 | 0.2282 |
| descend_to_place | 1.00 | 1.00 | 0.0065 |
| release_object | 1.00 | 0.67 | 0.0202 |
| retract_after_place | 1.00 | 1.00 | 0.0771 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_pre_grasp | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.030, 0.186) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.496, 0.030, 0.186)→(0.495, 0.024, 0.034) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.495, 0.024, 0.034)→(0.487, 0.024, 0.026) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 43.000 | 0.137 | 0.200 |
| lift_object | lift | 1.00 / step_budget | (0.487, 0.024, 0.026)→(0.496, 0.024, 0.278) | (0.500, 0.024, 0.026)→(0.508, 0.024, 0.270) | 0.272→0.216 | 1.00 / 42.000 | 76.238 | 0.659 |
| transport_to_goal | approach | 1.00 / step_budget | (0.496, 0.024, 0.278)→(0.589, 0.180, 0.406) | (0.508, 0.024, 0.270)→(0.600, 0.180, 0.390) | 0.216→0.183 | 1.00 / 26.667 | 0.147 | 0.167 |
| descend_to_place | descend | 1.00 / force_exceeded | (0.589, 0.180, 0.406)→(0.589, 0.181, 0.400) | (0.600, 0.180, 0.390)→(0.599, 0.181, 0.383) | 0.183→0.176 | 1.00 / 27.000 | 244.817 | 0.318 |
| release_object | release | 1.00 / step_budget | (0.589, 0.181, 0.400)→(0.588, 0.180, 0.420) | (0.599, 0.181, 0.383)→(0.595, 0.181, 0.017) | 0.176→0.191 | 0.67 / 2.000 | 1.281 | 1.673 |
| retract_after_place | retract | 1.00 / step_budget | (0.588, 0.180, 0.420)→(0.598, 0.193, 0.495) | (0.595, 0.181, 0.017)→(0.596, 0.181, 0.016) | 0.191→0.192 | 1.00 / 4.000 | 27.129 | 2.025 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.422
- phase_score: 0.357
- phase_breakdown.reach_retract_score: 0.410
- phase_breakdown.reach_lift_score: 0.227
- phase_breakdown.reach_pre_grasp_score: 0.324
- phase_breakdown.reach_place_score: 0.320
- phase_breakdown.reach_grasp_score: 0.696
- grasp_place_fitness: 0.690

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.690
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.422
- **Median Q (composite search score)**: -0.205
- **K-run variance**: 0.0022
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.298


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `daf90631fcbaf423e19452d0c9b90b9715013985cc94ef12ca0cd881e96195aa`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `94660347aa4f41f6801e53bd449f8df59691da8bebfa4fef4947a3513fe04781`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.05714,"average_solve_count":385.0,"average_success_count":385.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre_grasp.arc_height":0.1708,"approach_pre_grasp.speed":0.06822,"descend_to_grasp.descend_z":-0.01685,"descend_to_grasp.speed":0.04046,"descend_to_place.force_threshold":4.55065,"descend_to_place.place_z_offset":-0.03705,"descend_to_place.speed":0.02128,"grasp_object.grasp_duration":0.28917,"lift_object.lift_height":0.26372,"lift_object.speed":0.05553,"release_object.release_duration":0.25933,"retract_after_place.retract_z":0.30756,"retract_after_place.speed":0.04112,"transport_to_goal.arc_height":0.05015,"transport_to_goal.speed":0.0398},"optimized_scores":{"best_composite_score":-0.22045,"best_fitness_score":0.58455,"best_task_score":0.21168},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1243.0,"contact_point_centroid":[0.58709,0.16804,-0.00355],"force_p95":0.64974,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.39898,"mean_force":0.17954,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.58383,0.17873,0.49653]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.50102,-0.01514,-0.00139],"force_p95":0.57986,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70631,"mean_force":0.18595,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48966,-0.01513,0.02393]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16117.0,"contact_point_centroid":[0.49421,0.00409,0.1505],"force_p95":0.07856,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30502,"mean_force":0.05505,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4936,-0.01502,0.14821]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16767.0,"contact_point_centroid":[0.49405,-0.0341,0.14697],"force_p95":0.07738,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29183,"mean_force":0.05335,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49343,-0.01503,0.14498]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":91.0,"contact_point_centroid":[0.58265,0.19067,0.43736],"force_p95":0.15091,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18852,"mean_force":0.09825,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58003,0.1716,0.43883]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01546,-0.00204],"force_p95":0.13696,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18198,"mean_force":0.12671,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49191,-0.01516,0.024]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":119.0,"contact_point_centroid":[0.58101,0.15296,0.43748],"force_p95":0.11824,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17687,"mean_force":0.05817,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58003,0.1716,0.43883]},{"body_a":"world","body_b":"grasp_target","contact_count":1568.0,"contact_point_centroid":[0.50382,-0.01567,-0.00191],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12294,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.49901,0.00699,0.24106]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":936.0,"contact_point_centroid":[0.58075,0.1908,0.43222],"force_p95":0.08962,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13123,"mean_force":0.05691,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57966,0.17187,0.43427]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49778,-0.01173,0.10103]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17401.0,"contact_point_centroid":[0.53108,0.03751,0.37184],"force_p95":0.07901,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12212,"mean_force":0.05382,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52977,0.05636,0.37171]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":844.0,"contact_point_centroid":[0.58036,0.15298,0.43316],"force_p95":0.10039,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12184,"mean_force":0.06131,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57966,0.17187,0.43427]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14301.0,"contact_point_centroid":[0.52943,0.07056,0.36845],"force_p95":0.09324,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1179,"mean_force":0.06378,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52762,0.05147,0.36759]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4093.0,"contact_point_centroid":[0.49124,0.00405,0.02552],"force_p95":0.0771,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11743,"mean_force":0.05178,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49072,-0.01515,0.02276]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4910.0,"contact_point_centroid":[0.49129,-0.03424,0.0246],"force_p95":0.069,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0882,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49072,-0.01515,0.02276]}],"total_contact_groups":15},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.58715,0.16813,0.01602],"final_tcp_position":[0.58742,0.18561,0.53597],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":214.30779,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":393.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1568.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.49994,-0.00777,0.18438],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1586,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.49869,-0.01524,0.03113],"tcp_start":[0.49994,-0.00777,0.18438],"tcp_to_object_dist_end":0.00725,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50367,-0.01501,0.02583],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31198,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13342,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10803.0,"raw_peak_contact_force":0.18198,"subtask_id":"reach_grasp","tcp_end":[0.49069,-0.01514,0.02273],"tcp_start":[0.49869,-0.01524,0.03113],"tcp_to_object_dist_end":0.01335,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":863.0,"n_steps_budget":1000.0,"object_pos_end":[0.51308,-0.01499,0.26397],"object_pos_start":[0.50367,-0.01501,0.02583],"object_to_goal_dist_end":0.21607,"object_to_goal_dist_start":0.31198,"object_z_max":0.26371,"peak_contact_force":0.07052,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32968.0,"raw_peak_contact_force":0.70631,"subtask_id":"reach_lift","tcp_end":[0.50037,-0.01498,0.27008],"tcp_start":[0.49069,-0.01514,0.02273],"tcp_to_object_dist_end":0.0141,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":926.0,"n_steps_budget":1000.0,"object_pos_end":[0.59084,0.17126,0.42403],"object_pos_start":[0.51308,-0.01499,0.26397],"object_to_goal_dist_end":0.1767,"object_to_goal_dist_start":0.21607,"object_z_max":0.42404,"peak_contact_force":0.09524,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31702.0,"raw_peak_contact_force":0.12212,"subtask_id":"reach_place","tcp_end":[0.58005,0.17112,0.43932],"tcp_start":[0.50037,-0.01498,0.27008],"tcp_to_object_dist_end":0.01872,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.59068,0.17237,0.42255],"object_pos_start":[0.59084,0.17126,0.42403],"object_to_goal_dist_end":0.17513,"object_to_goal_dist_start":0.1767,"object_z_max":0.42403,"peak_contact_force":214.30779,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":210.0,"raw_peak_contact_force":0.18852,"tcp_end":[0.57994,0.17196,0.43803],"tcp_start":[0.58005,0.17112,0.43932],"tcp_to_object_dist_end":0.01884,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5871,0.17095,0.03449],"object_pos_start":[0.59068,0.17237,0.42255],"object_to_goal_dist_end":0.21427,"object_to_goal_dist_start":0.17513,"object_z_max":0.42255,"peak_contact_force":0.0,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1780.0,"raw_peak_contact_force":0.13123,"tcp_end":[0.57989,0.17144,0.45864],"tcp_start":[0.57994,0.17196,0.43803],"tcp_to_object_dist_end":0.42422,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":314.0,"n_steps_budget":1000.0,"object_pos_end":[0.58715,0.16813,0.01602],"object_pos_start":[0.5871,0.17095,0.03449],"object_to_goal_dist_end":0.2329,"object_to_goal_dist_start":0.21427,"object_z_max":0.03449,"peak_contact_force":81.14198,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1243.0,"raw_peak_contact_force":2.39898,"subtask_id":"reach_retract","tcp_end":[0.58742,0.18561,0.53597],"tcp_start":[0.57989,0.17144,0.45864],"tcp_to_object_dist_end":0.52024,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fe7e0be33c0bb4db9d2bbbb069b6113d0e5a69a675a0d70bc1f582243e99e3cf`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37255,"average_solve_count":306.0,"average_success_count":306.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre_grasp.arc_height":0.11115,"approach_pre_grasp.speed":0.07314,"descend_to_grasp.descend_z":-0.01255,"descend_to_grasp.speed":0.0481,"descend_to_place.force_threshold":7.77269,"descend_to_place.place_z_offset":-0.02431,"descend_to_place.speed":0.02711,"grasp_object.grasp_duration":0.39649,"lift_object.lift_height":0.29808,"lift_object.speed":0.05801,"release_object.release_duration":0.215,"retract_after_place.retract_z":0.36438,"retract_after_place.speed":0.08587,"transport_to_goal.arc_height":0.17128,"transport_to_goal.speed":0.06427},"optimized_scores":{"best_composite_score":-0.11517,"best_fitness_score":0.68983,"best_task_score":0.4216},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":22.0,"contact_point_centroid":[0.61807,0.16151,-0.00585],"force_p95":2.06848,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.07828,"mean_force":1.52096,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61164,0.15783,0.35951]},{"body_a":"world","body_b":"grasp_target","contact_count":1988.0,"contact_point_centroid":[0.61811,0.16538,-0.00275],"force_p95":0.13731,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.35688,"mean_force":0.13861,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.6191,0.16448,0.42314]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.50933,0.03859,-0.0014],"force_p95":0.53688,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64476,"mean_force":0.16471,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49835,0.03889,0.02877]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":294.0,"contact_point_centroid":[0.61785,0.17721,0.34183],"force_p95":0.16307,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.50206,"mean_force":0.09598,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61403,0.15888,0.34485]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":288.0,"contact_point_centroid":[0.61802,0.14094,0.34193],"force_p95":0.15523,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42155,"mean_force":0.0874,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61403,0.15888,0.3448]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18350.0,"contact_point_centroid":[0.50286,0.05777,0.16519],"force_p95":0.07873,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30886,"mean_force":0.05463,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50222,0.03867,0.16309]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18405.0,"contact_point_centroid":[0.50312,0.0196,0.169],"force_p95":0.0781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30514,"mean_force":0.05422,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50239,0.03867,0.16677]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":749.0,"contact_point_centroid":[0.61572,0.17693,0.33208],"force_p95":0.19912,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27546,"mean_force":0.09467,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61283,0.15848,0.33652]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":719.0,"contact_point_centroid":[0.6158,0.14029,0.33249],"force_p95":0.193,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2649,"mean_force":0.0911,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61285,0.15849,0.3366]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7812.0,"contact_point_centroid":[0.55216,0.06534,0.34596],"force_p95":0.11232,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25577,"mean_force":0.07014,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54841,0.08395,0.34586]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7160.0,"contact_point_centroid":[0.55266,0.10354,0.34651],"force_p95":0.11776,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25303,"mean_force":0.07534,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5491,0.08473,0.34616]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51252,0.03949,-0.00206],"force_p95":0.14113,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1936,"mean_force":0.1277,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50058,0.0391,0.02884]},{"body_a":"world","body_b":"grasp_target","contact_count":1944.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.50185,0.03904,0.2523]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4087.0,"contact_point_centroid":[0.49994,0.01981,0.03035],"force_p95":0.07804,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12762,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49939,0.039,0.02754]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50615,0.04243,0.10073]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4925.0,"contact_point_centroid":[0.49993,0.05811,0.02935],"force_p95":0.07035,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08653,"mean_force":0.04483,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49939,0.039,0.02755]}],"total_contact_groups":16},"final_pose_error":0.01981,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.61811,0.16526,0.01602],"final_tcp_position":[0.6278,0.17147,0.48962],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":269.19141,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":487.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1944.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.50778,0.04619,0.18581],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.50739,0.03967,0.03625],"tcp_start":[0.50778,0.04619,0.18581],"tcp_to_object_dist_end":0.01144,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51238,0.03892,0.02579],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21292,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.13664,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10812.0,"raw_peak_contact_force":0.1936,"subtask_id":"reach_grasp","tcp_end":[0.49936,0.039,0.02751],"tcp_start":[0.50739,0.03967,0.03625],"tcp_to_object_dist_end":0.01314,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":974.0,"n_steps_budget":1000.0,"object_pos_end":[0.51986,0.03866,0.29301],"object_pos_start":[0.51238,0.03892,0.02579],"object_to_goal_dist_end":0.22676,"object_to_goal_dist_start":0.21292,"object_z_max":0.29275,"peak_contact_force":228.57247,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36839.0,"raw_peak_contact_force":0.64476,"subtask_id":"reach_lift","tcp_end":[0.5095,0.03871,0.30409],"tcp_start":[0.49936,0.039,0.02751],"tcp_to_object_dist_end":0.01517,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":542.0,"n_steps_budget":1000.0,"object_pos_end":[0.6269,0.15839,0.32991],"object_pos_start":[0.51986,0.03866,0.29301],"object_to_goal_dist_end":0.18543,"object_to_goal_dist_start":0.22676,"object_z_max":0.3515,"peak_contact_force":0.15254,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14972.0,"raw_peak_contact_force":0.25577,"subtask_id":"reach_place","tcp_end":[0.6145,0.15832,0.34864],"tcp_start":[0.5095,0.03871,0.30409],"tcp_to_object_dist_end":0.02247,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":25.0,"n_steps_budget":1000.0,"object_pos_end":[0.62573,0.15923,0.3217],"object_pos_start":[0.6269,0.15839,0.32991],"object_to_goal_dist_end":0.17718,"object_to_goal_dist_start":0.18543,"object_z_max":0.32991,"peak_contact_force":269.19141,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":582.0,"raw_peak_contact_force":0.50206,"tcp_end":[0.61383,0.15888,0.34123],"tcp_start":[0.6145,0.15832,0.34864],"tcp_to_object_dist_end":0.02288,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61798,0.16128,-0.00129],"object_pos_start":[0.62573,0.15923,0.3217],"object_to_goal_dist_end":0.14706,"object_to_goal_dist_start":0.17718,"object_z_max":0.3217,"peak_contact_force":1.42911,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1490.0,"raw_peak_contact_force":2.07828,"tcp_end":[0.61163,0.15783,0.36058],"tcp_start":[0.61383,0.15888,0.34123],"tcp_to_object_dist_end":0.36194,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":497.0,"n_steps_budget":1000.0,"object_pos_end":[0.61811,0.16526,0.01602],"object_pos_start":[0.61798,0.16128,-0.00129],"object_to_goal_dist_end":0.12956,"object_to_goal_dist_start":0.14706,"object_z_max":0.017,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1988.0,"raw_peak_contact_force":1.35688,"subtask_id":"reach_retract","tcp_end":[0.6278,0.17147,0.48962],"tcp_start":[0.61163,0.15783,0.36058],"tcp_to_object_dist_end":0.47375,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `28f75809d7d1d0a11ca1a36dd459ad950e5a80b6bae34006f33ac9620425f5e5`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.88565,"average_solve_count":446.0,"average_success_count":446.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre_grasp.arc_height":0.16009,"approach_pre_grasp.speed":0.03954,"descend_to_grasp.descend_z":-0.02572,"descend_to_grasp.speed":0.01695,"descend_to_place.force_threshold":7.83816,"descend_to_place.place_z_offset":-0.02046,"descend_to_place.speed":0.03071,"grasp_object.grasp_duration":0.61978,"lift_object.lift_height":0.25254,"lift_object.speed":0.04402,"release_object.release_duration":0.42457,"retract_after_place.retract_z":0.24607,"retract_after_place.speed":0.07488,"transport_to_goal.arc_height":0.09401,"transport_to_goal.speed":0.03642},"optimized_scores":{"best_composite_score":-0.2052,"best_fitness_score":0.5998,"best_task_score":0.23935},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.55808,0.21544,-0.00225],"force_p95":2.75083,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.81033,"mean_force":2.17212,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57178,0.21133,0.44051]},{"body_a":"world","body_b":"grasp_target","contact_count":335.0,"contact_point_centroid":[0.58382,0.20795,-0.00744],"force_p95":1.36941,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.31919,"mean_force":0.31175,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.57519,0.21679,0.44895]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.47875,0.04764,-0.00144],"force_p95":0.60115,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62461,"mean_force":0.23467,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46929,0.04773,0.02786]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16766.0,"contact_point_centroid":[0.4724,0.06673,0.14312],"force_p95":0.07153,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28808,"mean_force":0.04941,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47273,0.04753,0.14168]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":663.0,"contact_point_centroid":[0.57499,0.23108,0.42621],"force_p95":0.10142,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26224,"mean_force":0.06379,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57199,0.21218,0.42587]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17058.0,"contact_point_centroid":[0.4723,0.02835,0.14401],"force_p95":0.07066,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25765,"mean_force":0.04818,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47277,0.04753,0.14239]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":507.0,"contact_point_centroid":[0.57431,0.19324,0.42654],"force_p95":0.10204,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24234,"mean_force":0.07492,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57199,0.21218,0.42587]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48271,0.04853,-0.00207],"force_p95":0.14436,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22312,"mean_force":0.12865,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47135,0.04796,0.02788]},{"body_a":"world","body_b":"grasp_target","contact_count":1856.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.49115,0.03619,0.2527]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":830.0,"contact_point_centroid":[0.57423,0.19279,0.4173],"force_p95":0.09816,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13304,"mean_force":0.06194,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57178,0.21188,0.41678]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1041.0,"contact_point_centroid":[0.575,0.23068,0.417],"force_p95":0.08012,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12272,"mean_force":0.05034,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57178,0.21188,0.41682]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47804,0.05009,0.10739]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18814.0,"contact_point_centroid":[0.50181,0.0682,0.37469],"force_p95":0.0797,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12179,"mean_force":0.05333,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50055,0.08713,0.37356]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16603.0,"contact_point_centroid":[0.50213,0.10646,0.3738],"force_p95":0.0878,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11026,"mean_force":0.05956,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50069,0.08735,0.37214]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5046.0,"contact_point_centroid":[0.47005,0.02861,0.02973],"force_p95":0.06768,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1022,"mean_force":0.04289,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47022,0.04785,0.02673]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5438.0,"contact_point_centroid":[0.46987,0.06713,0.02913],"force_p95":0.06687,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08209,"mean_force":0.04123,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47022,0.04785,0.02674]}],"total_contact_groups":16},"final_pose_error":0.01984,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58374,0.20845,0.01699],"final_tcp_position":[0.57876,0.22268,0.45796],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":250.95123,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":465.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1856.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.48143,0.05198,0.18912],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16314,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.47794,0.04863,0.03456],"tcp_start":[0.48143,0.05198,0.18912],"tcp_to_object_dist_end":0.00978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48258,0.04791,0.02574],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29073,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.14072,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12284.0,"raw_peak_contact_force":0.22312,"subtask_id":"reach_grasp","tcp_end":[0.47019,0.04784,0.0267],"tcp_start":[0.47794,0.04863,0.03456],"tcp_to_object_dist_end":0.01242,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":794.0,"n_steps_budget":1000.0,"object_pos_end":[0.48989,0.04765,0.25159],"object_pos_start":[0.48258,0.04791,0.02574],"object_to_goal_dist_end":0.20431,"object_to_goal_dist_start":0.29073,"object_z_max":0.25132,"peak_contact_force":0.06973,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33910.0,"raw_peak_contact_force":0.62461,"subtask_id":"reach_lift","tcp_end":[0.47919,0.04763,0.25872],"tcp_start":[0.47019,0.04784,0.0267],"tcp_to_object_dist_end":0.01286,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":998.0,"n_steps_budget":1000.0,"object_pos_end":[0.58239,0.21142,0.41582],"object_pos_start":[0.48989,0.04765,0.25159],"object_to_goal_dist_end":0.18616,"object_to_goal_dist_start":0.20431,"object_z_max":0.42814,"peak_contact_force":0.19204,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35417.0,"raw_peak_contact_force":0.12179,"subtask_id":"reach_place","tcp_end":[0.57223,0.21146,0.4311],"tcp_start":[0.47919,0.04763,0.25872],"tcp_to_object_dist_end":0.01834,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":39.0,"n_steps_budget":1000.0,"object_pos_end":[0.58198,0.21192,0.40452],"object_pos_start":[0.58239,0.21142,0.41582],"object_to_goal_dist_end":0.17486,"object_to_goal_dist_start":0.18616,"object_z_max":0.41582,"peak_contact_force":250.95123,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1170.0,"raw_peak_contact_force":0.26224,"tcp_end":[0.57205,0.21215,0.42054],"tcp_start":[0.57223,0.21146,0.4311],"tcp_to_object_dist_end":0.01884,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57848,0.21129,0.01816],"object_pos_start":[0.58198,0.21192,0.40452],"object_to_goal_dist_end":0.21308,"object_to_goal_dist_start":0.17486,"object_z_max":0.40452,"peak_contact_force":2.41367,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1875.0,"raw_peak_contact_force":2.81033,"tcp_end":[0.57177,0.21133,0.44106],"tcp_start":[0.57205,0.21215,0.42054],"tcp_to_object_dist_end":0.42295,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":85.0,"n_steps_budget":600.0,"object_pos_end":[0.58374,0.20845,0.01699],"object_pos_start":[0.57848,0.21129,0.01816],"object_to_goal_dist_end":0.21447,"object_to_goal_dist_start":0.21308,"object_z_max":0.01816,"peak_contact_force":0.12292,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":335.0,"raw_peak_contact_force":2.31919,"subtask_id":"reach_retract","tcp_end":[0.57876,0.22268,0.45796],"tcp_start":[0.57177,0.21133,0.44106],"tcp_to_object_dist_end":0.44123,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```