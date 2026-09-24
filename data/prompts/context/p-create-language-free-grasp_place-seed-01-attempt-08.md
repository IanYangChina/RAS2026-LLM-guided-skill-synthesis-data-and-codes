## Search State

- **Seed**: 1
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.1019 | 0.30 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0906 | 0.32 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.3398 | 0.19 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0696 | 0.36 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1850 | 0.23 | ❌ rejected |

**Proposal policy**: task_score is 0.30 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`
- Frozen object start: [0.5011821624700257, 0.045046369632593536, 0.03]
- Frozen task target: [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]
- Goal object position: (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5011821624700257, 0.045046369632593536, 0.03)
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
  frozen_object_start: [0.5012, 0.045, 0.03]
  frozen_task_target: [0.5644, 0.2449, 0.1468]
  frozen_object_starts: {'grasp_target': [0.5011821624700257, 0.045046369632593536, 0.03]}
  frozen_targets: {'place_target': [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb

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
| `object` | offset from object initial position (0.5011821624700257, 0.045046369632593536, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5644159612719634, 0.2448649447137244, 0.1467747178015728) | final destination targets |
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

## Current Skill (Q=-0.102) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: reach_goal
  weight: 0.7
phases:
- id: approach_1
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
    - 0.05
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
    approach_z:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: descend_1
  type: descend
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
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
- id: grasp_1
  type: grasp
  control: position_control
  termination: force_exceeded
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
    grasp_force_threshold:
      type: scalar
      range:
      - 0.1
      - 5.0
      default: 0.5
      binds_to:
      - path: termination.force_threshold
        mode: replace
- id: lift_1
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
    orientation:
      mode: keep_current
  parameters:
    lift_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    lift_z:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
- id: approach_2
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
    orientation:
      mode: keep_current
  parameters:
    approach2_z:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.25
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
- id: release_1
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
      - 1.0
      default: 0.3
      binds_to:
      - path: duration.max_time
        mode: replace
- id: retract_1
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
    - 0.15
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.05]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_z: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15]
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_speed: status=consumed; consumers=generator.speed (replace)
    - lift_z: status=consumed; consumers=target.offset.z (replace)
- **approach_2** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach2_z: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15]
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.102
- **task_score** (E): 0.296
- **fitness_score**: 0.628  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.730

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1662 |
| descend_1 | 1.00 | 1.00 | 0.1051 |
| grasp_1 | 1.00 | 1.00 | 0.0111 |
| lift_1 | 1.00 | 1.00 | 0.1052 |
| approach_2 | 0.67 | 1.00 | 0.2301 |
| descend_2 | 1.00 | 1.00 | 0.0773 |
| release_1 | 1.00 | 1.00 | 0.0209 |
| retract_1 | 1.00 | 1.00 | 0.1122 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.477, -0.000, 0.140) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.477, -0.000, 0.140)→(0.474, -0.001, 0.035) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.474, -0.001, 0.035)→(0.466, -0.001, 0.027) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 44.333 | 0.143 | 0.206 |
| lift_1 | lift | 1.00 / step_budget | (0.466, -0.001, 0.027)→(0.474, -0.001, 0.132) | (0.479, -0.001, 0.026)→(0.492, -0.001, 0.121) | 0.278→0.244 | 1.00 / 22.333 | 524.440 | 0.677 |
| approach_2 | approach | 0.67 / step_budget | (0.474, -0.001, 0.132)→(0.586, 0.168, 0.220) | (0.492, -0.001, 0.121)→(0.533, 0.101, 0.016) | 0.244→0.186 | 1.00 / 8.333 | 0.123 | 1.567 |
| descend_2 | descend | 1.00 / step_budget | (0.586, 0.168, 0.220)→(0.602, 0.198, 0.151) | (0.533, 0.101, 0.016)→(0.533, 0.101, 0.016) | 0.186→0.186 | 1.00 / 8.000 | 9748.840 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.602, 0.198, 0.151)→(0.595, 0.196, 0.171) | (0.533, 0.101, 0.016)→(0.533, 0.101, 0.016) | 0.186→0.186 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_1 | retract | 1.00 / step_budget | (0.595, 0.196, 0.171)→(0.606, 0.203, 0.283) | (0.533, 0.101, 0.016)→(0.533, 0.101, 0.016) | 0.186→0.186 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.368
- phase_score: 0.665
- phase_breakdown.reach_object_score: 0.306
- phase_breakdown.reach_goal_score: 0.819
- grasp_place_fitness: 0.665

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.665
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.368
- **Median Q (composite search score)**: -0.099
- **K-run variance**: 0.0010
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.288


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8110053be9072e64e15984c6424e4a66fe19af4b6c37a60139a43e94cc34ad53`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `46ef03f7b16015a0d14bf26d80c05d326b92c02b0bf759391930f5ab902d1933`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.15447,"average_solve_count":123.0,"average_success_count":123.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.31537,"approach_1.approach_z":0.09826,"approach_2.approach2_z":0.13603,"approach_2.transport_speed":0.2347,"descend_1.descend_speed":0.24128,"descend_2.place_speed":0.15771,"grasp_1.grasp_force_threshold":4.60301,"lift_1.lift_speed":0.10709,"lift_1.lift_z":0.12172,"release_1.release_duration":0.95382,"retract_1.retract_speed":0.27835},"optimized_scores":{"best_composite_score":-0.09856,"best_fitness_score":0.63144,"best_task_score":0.3046},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2447.0,"contact_point_centroid":[0.51111,0.13576,-0.00236],"force_p95":0.13884,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.57454,"mean_force":0.14368,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.52837,0.14679,0.20507]},{"body_a":"world","body_b":"grasp_target","contact_count":157.0,"contact_point_centroid":[0.49845,0.04199,-0.0013],"force_p95":0.43442,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65528,"mean_force":0.0844,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48675,0.04324,0.0276]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2964.0,"contact_point_centroid":[0.5057,0.08487,0.1455],"force_p95":0.18125,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35856,"mean_force":0.10787,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.50133,0.06681,0.14787]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10164.0,"contact_point_centroid":[0.49208,0.06191,0.07338],"force_p95":0.10522,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30818,"mean_force":0.06584,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48941,0.04302,0.07171]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9670.0,"contact_point_centroid":[0.49234,0.02415,0.0758],"force_p95":0.10592,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29863,"mean_force":0.06816,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48961,0.04302,0.0739]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2641.0,"contact_point_centroid":[0.50548,0.04672,0.14477],"force_p95":0.17889,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29104,"mean_force":0.10609,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.50081,0.06493,0.14669]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04467,-0.00215],"force_p95":0.16679,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25127,"mean_force":0.1345,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4892,0.04351,0.02709]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4045.0,"contact_point_centroid":[0.48861,0.0242,0.02868],"force_p95":0.08189,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14845,"mean_force":0.05192,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48803,0.0434,0.02587]},{"body_a":"world","body_b":"grasp_target","contact_count":1832.0,"contact_point_centroid":[0.50118,0.04505,-0.00192],"force_p95":0.13357,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49768,0.02019,0.21787]},{"body_a":"world","body_b":"grasp_target","contact_count":1268.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4954,0.04252,0.08507]},{"body_a":"world","body_b":"grasp_target","contact_count":1368.0,"contact_point_centroid":[0.51112,0.13597,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.5502,0.21397,0.19164]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51112,0.13597,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55397,0.23561,0.15015]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.51112,0.13597,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55521,0.23816,0.22089]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5025.0,"contact_point_centroid":[0.48859,0.06259,0.02768],"force_p95":0.07442,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08702,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48804,0.0434,0.02588]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2399.0,"contact_point_centroid":[0.52996,0.15027,0.20984],"force_p95":0.01149,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01613,"mean_force":0.0106,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.52957,0.15026,0.20758]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1453.0,"contact_point_centroid":[0.55061,0.21409,0.19376],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01259,"mean_force":0.01049,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55023,0.21406,0.19147]}],"total_contact_groups":17},"final_pose_error":0.01729,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.51112,0.13597,0.01602],"final_tcp_position":[0.56132,0.243,0.27987],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":9748.94166,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":459.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1832.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.4972,0.04113,0.13648],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1106,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":317.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1268.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49615,0.04414,0.03446],"tcp_start":[0.4972,0.04113,0.13648],"tcp_to_object_dist_end":0.00987,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50107,0.0434,0.0255],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24353,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.157,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10870.0,"raw_peak_contact_force":0.25127,"tcp_end":[0.48801,0.04339,0.02584],"tcp_start":[0.49615,0.04414,0.03446],"tcp_to_object_dist_end":0.01307,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":645.0,"n_steps_budget":720.0,"object_pos_end":[0.51406,0.04314,0.12363],"object_pos_start":[0.50107,0.0434,0.0255],"object_to_goal_dist_end":0.2092,"object_to_goal_dist_start":0.24353,"object_z_max":0.12352,"peak_contact_force":0.11153,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19991.0,"raw_peak_contact_force":0.65528,"tcp_end":[0.49633,0.04304,0.13473],"tcp_start":[0.48801,0.04339,0.02584],"tcp_to_object_dist_end":0.02092,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51112,0.13597,0.01602],"object_pos_start":[0.51406,0.04314,0.12363],"object_to_goal_dist_end":0.17831,"object_to_goal_dist_start":0.2092,"object_z_max":0.13951,"peak_contact_force":0.12263,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10451.0,"raw_peak_contact_force":1.57454,"subtask_id":"reach_goal","tcp_end":[0.54403,0.19186,0.23765],"tcp_start":[0.49633,0.04304,0.13473],"tcp_to_object_dist_end":0.23092,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":342.0,"n_steps_budget":1000.0,"object_pos_end":[0.51112,0.13597,0.01602],"object_pos_start":[0.51112,0.13597,0.01602],"object_to_goal_dist_end":0.17831,"object_to_goal_dist_start":0.17831,"object_z_max":0.01602,"peak_contact_force":9748.94166,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2821.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.55834,0.23736,0.14905],"tcp_start":[0.54403,0.19186,0.23765],"tcp_to_object_dist_end":0.1738,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51112,0.13597,0.01602],"object_pos_start":[0.51112,0.13597,0.01602],"object_to_goal_dist_end":0.17831,"object_to_goal_dist_start":0.17831,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55238,0.23484,0.17009],"tcp_start":[0.55834,0.23736,0.14905],"tcp_to_object_dist_end":0.18766,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.51112,0.13597,0.01602],"object_pos_start":[0.51112,0.13597,0.01602],"object_to_goal_dist_end":0.17831,"object_to_goal_dist_start":0.17831,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56132,0.243,0.27987],"tcp_start":[0.55238,0.23484,0.17009],"tcp_to_object_dist_end":0.28913,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1efc3ad2e58ea1c47cd56203c4986b53dab7b80d759e458b85d233ccc9cc04bd`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.27966,"average_solve_count":118.0,"average_success_count":118.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.34501,"approach_1.approach_z":0.10408,"approach_2.approach2_z":0.1052,"approach_2.transport_speed":0.33323,"descend_1.descend_speed":0.13076,"descend_2.place_speed":0.13225,"grasp_1.grasp_force_threshold":3.76209,"lift_1.lift_speed":0.26999,"lift_1.lift_z":0.11318,"release_1.release_duration":0.76878,"retract_1.retract_speed":0.23047},"optimized_scores":{"best_composite_score":-0.14221,"best_fitness_score":0.58779,"best_task_score":0.21501},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2465.0,"contact_point_centroid":[0.5257,0.05107,-0.00233],"force_p95":0.1442,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.67364,"mean_force":0.14118,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.56436,0.08723,0.22068]},{"body_a":"world","body_b":"grasp_target","contact_count":140.0,"contact_point_centroid":[0.47394,-0.01953,-0.00122],"force_p95":0.49682,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69219,"mean_force":0.09226,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46264,-0.01962,0.02844]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2563.0,"contact_point_centroid":[0.49107,-0.01885,0.14048],"force_p95":0.18483,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34768,"mean_force":0.11039,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.4857,-0.00037,0.14043]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3159.0,"contact_point_centroid":[0.49242,0.01902,0.1411],"force_p95":0.17664,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34366,"mean_force":0.09757,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.48675,0.00087,0.14149]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8150.0,"contact_point_centroid":[0.46719,-0.00059,0.0709],"force_p95":0.10619,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31478,"mean_force":0.06699,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46498,-0.01957,0.06859]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8847.0,"contact_point_centroid":[0.46712,-0.03846,0.06948],"force_p95":0.10305,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30303,"mean_force":0.06265,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46488,-0.01957,0.06775]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47615,-0.02002,-0.00204],"force_p95":0.13525,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17516,"mean_force":0.12614,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46491,-0.01968,0.02807]},{"body_a":"world","body_b":"grasp_target","contact_count":1680.0,"contact_point_centroid":[0.47616,-0.02015,-0.00192],"force_p95":0.13414,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48668,-0.00891,0.22202]},{"body_a":"world","body_b":"grasp_target","contact_count":1368.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47181,-0.01901,0.08866]},{"body_a":"world","body_b":"grasp_target","contact_count":920.0,"contact_point_centroid":[0.52558,0.0511,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61482,0.144,0.22886]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52558,0.0511,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61987,0.15308,0.19387]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.52558,0.0511,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.62206,0.1549,0.26322]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5067.0,"contact_point_centroid":[0.46356,-0.00041,0.02983],"force_p95":0.0661,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09116,"mean_force":0.04291,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46379,-0.01966,0.02697]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5397.0,"contact_point_centroid":[0.46343,-0.03891,0.02932],"force_p95":0.06461,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08739,"mean_force":0.0412,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46379,-0.01966,0.02698]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2405.0,"contact_point_centroid":[0.56893,0.09197,0.22744],"force_p95":0.01119,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01576,"mean_force":0.01045,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.56866,0.09197,0.22507]},{"body_a":"left_finger","body_b":"right_finger","contact_count":216.0,"contact_point_centroid":[0.62288,0.15388,0.19265],"force_p95":0.01108,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.01024,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62236,0.15386,0.19036]}],"total_contact_groups":17},"final_pose_error":0.01808,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.52558,0.0511,0.01602],"final_tcp_position":[0.6288,0.1581,0.32216],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":9748.92272,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":421.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1680.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47453,-0.01828,0.14355],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11756,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":342.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1368.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47158,-0.01983,0.03471],"tcp_start":[0.47453,-0.01828,0.14355],"tcp_to_object_dist_end":0.00983,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01967,0.02584],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28826,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13348,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12264.0,"raw_peak_contact_force":0.17516,"tcp_end":[0.46376,-0.01966,0.02694],"tcp_start":[0.47158,-0.01983,0.03471],"tcp_to_object_dist_end":0.01232,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":535.0,"n_steps_budget":600.0,"object_pos_end":[0.48924,-0.01946,0.11598],"object_pos_start":[0.47603,-0.01967,0.02584],"object_to_goal_dist_end":0.24003,"object_to_goal_dist_start":0.28826,"object_z_max":0.11585,"peak_contact_force":1573.09317,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17137.0,"raw_peak_contact_force":0.69219,"tcp_end":[0.47128,-0.01956,0.12624],"tcp_start":[0.46376,-0.01966,0.02694],"tcp_to_object_dist_end":0.02068,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52558,0.0511,0.01602],"object_pos_start":[0.48924,-0.01946,0.11598],"object_to_goal_dist_end":0.23056,"object_to_goal_dist_start":0.24003,"object_z_max":0.14029,"peak_contact_force":0.12263,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10592.0,"raw_peak_contact_force":1.67364,"subtask_id":"reach_goal","tcp_end":[0.60784,0.13513,0.2649],"tcp_start":[0.47128,-0.01956,0.12624],"tcp_to_object_dist_end":0.27526,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":230.0,"n_steps_budget":1000.0,"object_pos_end":[0.52558,0.0511,0.01602],"object_pos_start":[0.52558,0.0511,0.01602],"object_to_goal_dist_end":0.23056,"object_to_goal_dist_start":0.23056,"object_z_max":0.01602,"peak_contact_force":9748.92272,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1920.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.62395,0.15412,0.19409],"tcp_start":[0.60784,0.13513,0.2649],"tcp_to_object_dist_end":0.22803,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52558,0.0511,0.01602],"object_pos_start":[0.52558,0.0511,0.01602],"object_to_goal_dist_end":0.23056,"object_to_goal_dist_start":0.23056,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1016.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61842,0.15262,0.21329],"tcp_start":[0.62395,0.15412,0.19409],"tcp_to_object_dist_end":0.24049,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.52558,0.0511,0.01602],"object_pos_start":[0.52558,0.0511,0.01602],"object_to_goal_dist_end":0.23056,"object_to_goal_dist_start":0.23056,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6288,0.1581,0.32216],"tcp_start":[0.61842,0.15262,0.21329],"tcp_to_object_dist_end":0.34033,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `37495cb43897015e78e007c86af160d11c8460c1ce7249e5c03dce38206c0daf`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.27731,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.23238,"approach_1.approach_z":0.09952,"approach_2.approach2_z":0.05648,"approach_2.transport_speed":0.35711,"descend_1.descend_speed":0.14214,"descend_2.place_speed":0.12795,"grasp_1.grasp_force_threshold":3.10688,"lift_1.lift_speed":0.17575,"lift_1.lift_z":0.12168,"release_1.release_duration":0.3899,"retract_1.retract_speed":0.28927},"optimized_scores":{"best_composite_score":-0.06506,"best_fitness_score":0.66494,"best_task_score":0.36802},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1246.0,"contact_point_centroid":[0.56329,0.11842,-0.00266],"force_p95":0.42349,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.45276,"mean_force":0.16326,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.58075,0.14677,0.15363]},{"body_a":"world","body_b":"grasp_target","contact_count":143.0,"contact_point_centroid":[0.45696,-0.02546,-0.00114],"force_p95":0.4911,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68435,"mean_force":0.07218,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44554,-0.02556,0.02946]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6881.0,"contact_point_centroid":[0.50004,0.05139,0.13828],"force_p95":0.1348,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32737,"mean_force":0.08372,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49503,0.03324,0.13869]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5092.0,"contact_point_centroid":[0.49664,0.00962,0.13774],"force_p95":0.16223,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31721,"mean_force":0.1075,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49126,0.02815,0.13808]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8285.0,"contact_point_centroid":[0.44996,-0.0065,0.07458],"force_p95":0.1064,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31609,"mean_force":0.06651,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44779,-0.02548,0.07228]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9004.0,"contact_point_centroid":[0.44991,-0.04438,0.07331],"force_p95":0.10261,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30228,"mean_force":0.06217,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44772,-0.02548,0.07161]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02616,-0.00206],"force_p95":0.14023,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19305,"mean_force":0.12744,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44782,-0.02565,0.02881]},{"body_a":"world","body_b":"grasp_target","contact_count":1736.0,"contact_point_centroid":[0.45856,-0.02632,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47874,-0.0117,0.21965]},{"body_a":"world","body_b":"grasp_target","contact_count":1332.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45513,-0.02485,0.08672]},{"body_a":"world","body_b":"grasp_target","contact_count":1064.0,"contact_point_centroid":[0.56258,0.11713,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61309,0.19109,0.13042]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56258,0.11713,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61744,0.20137,0.11025]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.56258,0.11713,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.61904,0.20294,0.18309]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4815.0,"contact_point_centroid":[0.44676,-0.0064,0.03016],"force_p95":0.06812,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09806,"mean_force":0.04488,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44673,-0.02561,0.02779]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5173.0,"contact_point_centroid":[0.44661,-0.04484,0.02966],"force_p95":0.06694,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08252,"mean_force":0.043,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44674,-0.02561,0.0278]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1143.0,"contact_point_centroid":[0.58463,0.15155,0.1565],"force_p95":0.01218,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01566,"mean_force":0.01064,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.58437,0.15155,0.15425]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1128.0,"contact_point_centroid":[0.61352,0.19106,0.13265],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.01051,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61305,0.19104,0.1305]}],"total_contact_groups":17},"final_pose_error":0.01889,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.56258,0.11713,0.01602],"final_tcp_position":[0.62647,0.20663,0.24566],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":9748.6544,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":435.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1736.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.4584,-0.02395,0.1391],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11311,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":333.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1332.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.4543,-0.02588,0.03499],"tcp_start":[0.4584,-0.02395,0.1391],"tcp_to_object_dist_end":0.00994,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02565,0.02579],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30327,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13744,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11788.0,"raw_peak_contact_force":0.19305,"tcp_end":[0.44671,-0.02561,0.02777],"tcp_start":[0.4543,-0.02588,0.03499],"tcp_to_object_dist_end":0.0119,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":540.0,"n_steps_budget":600.0,"object_pos_end":[0.47218,-0.02544,0.12268],"object_pos_start":[0.45844,-0.02565,0.02579],"object_to_goal_dist_end":0.28217,"object_to_goal_dist_start":0.30327,"object_z_max":0.12255,"peak_contact_force":0.11539,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17432.0,"raw_peak_contact_force":0.68435,"tcp_end":[0.45392,-0.02549,0.13447],"tcp_start":[0.44671,-0.02561,0.02777],"tcp_to_object_dist_end":0.02173,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56258,0.11713,0.01602],"object_pos_start":[0.47218,-0.02544,0.12268],"object_to_goal_dist_end":0.14994,"object_to_goal_dist_start":0.28217,"object_z_max":0.12273,"peak_contact_force":0.12263,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14362.0,"raw_peak_contact_force":1.45276,"subtask_id":"reach_goal","tcp_end":[0.60471,0.17815,0.15761],"tcp_start":[0.45392,-0.02549,0.13447],"tcp_to_object_dist_end":0.15983,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":266.0,"n_steps_budget":1000.0,"object_pos_end":[0.56258,0.11713,0.01602],"object_pos_start":[0.56258,0.11713,0.01602],"object_to_goal_dist_end":0.14994,"object_to_goal_dist_start":0.14994,"object_z_max":0.01602,"peak_contact_force":9748.6544,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2192.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.62247,0.20302,0.11038],"tcp_start":[0.60471,0.17815,0.15761],"tcp_to_object_dist_end":0.14095,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56258,0.11713,0.01602],"object_pos_start":[0.56258,0.11713,0.01602],"object_to_goal_dist_end":0.14994,"object_to_goal_dist_start":0.14994,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1016.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61549,0.20064,0.12953],"tcp_start":[0.62247,0.20302,0.11038],"tcp_to_object_dist_end":0.15053,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.56258,0.11713,0.01602],"object_pos_start":[0.56258,0.11713,0.01602],"object_to_goal_dist_end":0.14994,"object_to_goal_dist_start":0.14994,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62647,0.20663,0.24566],"tcp_start":[0.61549,0.20064,0.12953],"tcp_to_object_dist_end":0.25461,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```