## Search State

- **Seed**: 1
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0906 | 0.32 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.3398 | 0.19 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0696 | 0.36 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1850 | 0.23 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.2445 | 0.21 | ❌ rejected |

**Proposal policy**: task_score is 0.32 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.091) — your mutation base

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

- **Composite score**: -0.091
- **task_score** (E): 0.319
- **fitness_score**: 0.639  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.730

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1866 |
| descend_1 | 1.00 | 1.00 | 0.0842 |
| grasp_1 | 1.00 | 1.00 | 0.0111 |
| lift_1 | 0.67 | 0.67 | 0.1221 |
| approach_2 | 0.00 | 1.00 | 0.1703 |
| descend_2 | 1.00 | 1.00 | 0.0867 |
| release_1 | 1.00 | 1.00 | 0.0211 |
| retract_1 | 1.00 | 1.00 | 0.1187 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.476, -0.000, 0.119) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.476, -0.000, 0.119)→(0.474, -0.001, 0.035) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.474, -0.001, 0.035)→(0.466, -0.001, 0.027) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 44.333 | 0.143 | 0.212 |
| lift_1 | lift | 0.67 / step_budget | (0.466, -0.001, 0.027)→(0.472, -0.001, 0.149) | (0.479, -0.001, 0.026)→(0.486, -0.001, 0.132) | 0.278→0.243 | 0.67 / 22.000 | 0.061 | 0.662 |
| approach_2 | approach | 0.00 / step_budget | (0.472, -0.001, 0.149)→(0.559, 0.137, 0.188) | (0.486, -0.001, 0.132)→(0.536, 0.100, 0.060) | 0.243→0.162 | 1.00 / 11.333 | 0.147 | 1.128 |
| descend_2 | descend | 1.00 / step_budget | (0.559, 0.137, 0.188)→(0.601, 0.198, 0.144) | (0.536, 0.100, 0.060)→(0.541, 0.110, 0.016) | 0.162→0.188 | 1.00 / 8.000 | 0.125 | 0.576 |
| release_1 | release | 1.00 / step_budget | (0.601, 0.198, 0.144)→(0.595, 0.196, 0.164) | (0.541, 0.110, 0.016)→(0.541, 0.110, 0.016) | 0.188→0.188 | 1.00 / 4.000 | 0.123 | 0.125 |
| retract_1 | retract | 1.00 / step_budget | (0.595, 0.196, 0.164)→(0.606, 0.203, 0.282) | (0.541, 0.110, 0.016)→(0.541, 0.110, 0.016) | 0.188→0.188 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.415
- phase_score: 0.713
- phase_breakdown.reach_object_score: 0.465
- phase_breakdown.reach_goal_score: 0.819
- grasp_place_fitness: 0.687

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.687
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.415
- **Median Q (composite search score)**: -0.048
- **K-run variance**: 0.0040
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.322


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90141,"average_solve_count":142.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.16975,"approach_1.approach_z":0.0798,"approach_2.approach2_z":0.0516,"approach_2.transport_speed":0.19916,"descend_1.descend_speed":0.18965,"descend_2.place_speed":0.1439,"grasp_1.grasp_force_threshold":7.90989,"lift_1.lift_speed":0.05895,"lift_1.lift_z":0.24085,"release_1.release_duration":0.54441,"retract_1.retract_speed":0.3645},"optimized_scores":{"best_composite_score":-0.04322,"best_fitness_score":0.68678,"best_task_score":0.41542},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":372.0,"contact_point_centroid":[0.56596,0.23209,-0.00421],"force_p95":1.06378,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.4514,"mean_force":0.26077,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55665,0.23439,0.14354]},{"body_a":"world","body_b":"grasp_target","contact_count":194.0,"contact_point_centroid":[0.49703,0.04203,-0.00124],"force_p95":0.45714,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66891,"mean_force":0.09942,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48634,0.04319,0.02755]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19692.0,"contact_point_centroid":[0.4871,0.06208,0.07594],"force_p95":0.07709,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31463,"mean_force":0.0521,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48664,0.04298,0.07418]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19228.0,"contact_point_centroid":[0.48725,0.02386,0.07854],"force_p95":0.07875,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29818,"mean_force":0.05244,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48675,0.04298,0.07645]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50125,0.04467,-0.00216],"force_p95":0.16863,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25764,"mean_force":0.13483,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48915,0.04347,0.02696]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1252.0,"contact_point_centroid":[0.54994,0.18936,0.15576],"force_p95":0.19561,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25756,"mean_force":0.14218,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.54589,0.20752,0.15985]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2119.0,"contact_point_centroid":[0.54932,0.22505,0.15609],"force_p95":0.14948,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20783,"mean_force":0.09327,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.54594,0.20758,0.15987]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13561.0,"contact_point_centroid":[0.51514,0.09577,0.14442],"force_p95":0.11244,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19811,"mean_force":0.07117,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51272,0.11471,0.14434]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3978.0,"contact_point_centroid":[0.4887,0.02417,0.02852],"force_p95":0.08297,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15092,"mean_force":0.05275,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48798,0.04337,0.02574]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15617.0,"contact_point_centroid":[0.5161,0.13521,0.14488],"force_p95":0.0867,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14926,"mean_force":0.06219,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51334,0.11648,0.14493]},{"body_a":"world","body_b":"grasp_target","contact_count":2084.0,"contact_point_centroid":[0.50118,0.04505,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49757,0.02037,0.2087]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56359,0.22856,-0.00199],"force_p95":0.12433,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12939,"mean_force":0.1228,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55434,0.23731,0.14238]},{"body_a":"world","body_b":"grasp_target","contact_count":1068.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49537,0.04269,0.07578]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.56359,0.22856,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55538,0.23908,0.2169]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5027.0,"contact_point_centroid":[0.48855,0.06255,0.02755],"force_p95":0.07465,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08794,"mean_force":0.04477,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48799,0.04337,0.02574]},{"body_a":"left_finger","body_b":"right_finger","contact_count":184.0,"contact_point_centroid":[0.55875,0.2372,0.14443],"force_p95":0.01489,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01564,"mean_force":0.0118,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55784,0.23716,0.14206]}],"total_contact_groups":17},"final_pose_error":0.01758,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.56359,0.22856,0.01602],"final_tcp_position":[0.56139,0.24315,0.27954],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.4514,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":522.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2084.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49708,0.0415,0.11795],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09209,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":267.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1068.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.4961,0.04411,0.03433],"tcp_start":[0.49708,0.0415,0.11795],"tcp_to_object_dist_end":0.00979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50107,0.04337,0.02549],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24356,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15809,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10805.0,"raw_peak_contact_force":0.25764,"tcp_end":[0.48796,0.04336,0.02571],"tcp_start":[0.4961,0.04411,0.03433],"tcp_to_object_dist_end":0.01311,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49953,0.04301,0.1132],"object_pos_start":[0.50107,0.04337,0.02549],"object_to_goal_dist_end":0.21467,"object_to_goal_dist_start":0.24356,"object_z_max":0.1131,"peak_contact_force":0.07003,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39114.0,"raw_peak_contact_force":0.66891,"tcp_end":[0.48937,0.043,0.12278],"tcp_start":[0.48796,0.04336,0.02571],"tcp_to_object_dist_end":0.01397,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54794,0.19381,0.15057],"object_pos_start":[0.49953,0.04301,0.1132],"object_to_goal_dist_end":0.05378,"object_to_goal_dist_start":0.21467,"object_z_max":0.15055,"peak_contact_force":0.15733,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29178.0,"raw_peak_contact_force":0.19811,"subtask_id":"reach_goal","tcp_end":[0.54227,0.19381,0.17271],"tcp_start":[0.48937,0.043,0.12278],"tcp_to_object_dist_end":0.02285,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":397.0,"n_steps_budget":1000.0,"object_pos_end":[0.56345,0.22813,0.01609],"object_pos_start":[0.54794,0.19381,0.15057],"object_to_goal_dist_end":0.13175,"object_to_goal_dist_start":0.05378,"object_z_max":0.15057,"peak_contact_force":0.12992,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3927.0,"raw_peak_contact_force":1.4514,"subtask_id":"reach_goal","tcp_end":[0.55862,0.2391,0.14101],"tcp_start":[0.54227,0.19381,0.17271],"tcp_to_object_dist_end":0.12549,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56359,0.22856,0.01602],"object_pos_start":[0.56345,0.22813,0.01609],"object_to_goal_dist_end":0.13177,"object_to_goal_dist_start":0.13175,"object_z_max":0.01609,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12939,"tcp_end":[0.5527,0.23652,0.16228],"tcp_start":[0.55862,0.2391,0.14101],"tcp_to_object_dist_end":0.14688,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.56359,0.22856,0.01602],"object_pos_start":[0.56359,0.22856,0.01602],"object_to_goal_dist_end":0.13177,"object_to_goal_dist_start":0.13177,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56139,0.24315,0.27954],"tcp_start":[0.5527,0.23652,0.16228],"tcp_to_object_dist_end":0.26394,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.41732,"average_solve_count":127.0,"average_success_count":127.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.3134,"approach_1.approach_z":0.08249,"approach_2.approach2_z":0.09572,"approach_2.transport_speed":0.166,"descend_1.descend_speed":0.13547,"descend_2.place_speed":0.11319,"grasp_1.grasp_force_threshold":4.42284,"lift_1.lift_speed":0.16567,"lift_1.lift_z":0.19304,"release_1.release_duration":0.45744,"retract_1.retract_speed":0.33761},"optimized_scores":{"best_composite_score":-0.18032,"best_fitness_score":0.54968,"best_task_score":0.13895},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3709.0,"contact_point_centroid":[0.47964,-0.02603,-0.00227],"force_p95":0.12428,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.78903,"mean_force":0.13571,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.52252,0.0402,0.22531]},{"body_a":"world","body_b":"grasp_target","contact_count":111.0,"contact_point_centroid":[0.47385,-0.01928,-0.00111],"force_p95":0.51427,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70622,"mean_force":0.06555,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46264,-0.01961,0.02885]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9256.0,"contact_point_centroid":[0.46794,-0.00069,0.09886],"force_p95":0.12987,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33956,"mean_force":0.07509,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46494,-0.01955,0.09718]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9871.0,"contact_point_centroid":[0.46779,-0.03836,0.09643],"force_p95":0.12654,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31118,"mean_force":0.0713,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46481,-0.01955,0.0952]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02003,-0.00204],"force_p95":0.13641,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18556,"mean_force":0.12644,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46486,-0.01967,0.02812]},{"body_a":"world","body_b":"grasp_target","contact_count":1868.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48633,-0.00907,0.21083]},{"body_a":"world","body_b":"grasp_target","contact_count":1124.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4716,-0.01911,0.07806]},{"body_a":"world","body_b":"grasp_target","contact_count":2736.0,"contact_point_centroid":[0.47954,-0.02602,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59656,0.12425,0.20837]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.47954,-0.02602,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62113,0.15448,0.18333]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.47954,-0.02602,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.62269,0.15565,0.25771]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5069.0,"contact_point_centroid":[0.46353,-0.0004,0.02992],"force_p95":0.0663,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09321,"mean_force":0.04289,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46374,-0.01964,0.02702]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5397.0,"contact_point_centroid":[0.4634,-0.03889,0.0294],"force_p95":0.0648,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08788,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46375,-0.01964,0.02702]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3724.0,"contact_point_centroid":[0.52546,0.0431,0.22888],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01633,"mean_force":0.0105,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.52509,0.0431,0.22655]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2921.0,"contact_point_centroid":[0.59705,0.12425,0.21064],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01269,"mean_force":0.01044,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59656,0.12424,0.20837]},{"body_a":"left_finger","body_b":"right_finger","contact_count":218.0,"contact_point_centroid":[0.62406,0.15531,0.18228],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01102,"mean_force":0.0102,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62378,0.1553,0.17996]}],"total_contact_groups":15},"final_pose_error":0.01855,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.47954,-0.02602,0.01602],"final_tcp_position":[0.62893,0.1582,0.32166],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.78903,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":468.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1868.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47406,-0.01849,0.1219],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09592,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":281.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1124.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47154,-0.01981,0.03476],"tcp_start":[0.47406,-0.01849,0.1219],"tcp_to_object_dist_end":0.00989,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01966,0.02583],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28826,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13447,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12266.0,"raw_peak_contact_force":0.18556,"tcp_end":[0.46371,-0.01964,0.02699],"tcp_start":[0.47154,-0.01981,0.03476],"tcp_to_object_dist_end":0.01237,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":692.0,"n_steps_budget":750.0,"object_pos_end":[0.48816,-0.02031,0.17106],"object_pos_start":[0.47603,-0.01966,0.02583],"object_to_goal_dist_end":0.23045,"object_to_goal_dist_start":0.28826,"object_z_max":0.17785,"peak_contact_force":0.0,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19238.0,"raw_peak_contact_force":0.70622,"tcp_end":[0.4722,-0.01956,0.20368],"tcp_start":[0.46371,-0.01964,0.02699],"tcp_to_object_dist_end":0.03632,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47954,-0.02602,0.01602],"object_pos_start":[0.48816,-0.02031,0.17106],"object_to_goal_dist_end":0.29605,"object_to_goal_dist_start":0.23045,"object_z_max":0.17106,"peak_contact_force":0.12263,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7433.0,"raw_peak_contact_force":1.78903,"subtask_id":"reach_goal","tcp_end":[0.5634,0.08577,0.24528],"tcp_start":[0.4722,-0.01956,0.20368],"tcp_to_object_dist_end":0.26849,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":684.0,"n_steps_budget":1000.0,"object_pos_end":[0.47954,-0.02602,0.01602],"object_pos_start":[0.47954,-0.02602,0.01602],"object_to_goal_dist_end":0.29605,"object_to_goal_dist_start":0.29605,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5657.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.62516,0.15557,0.18312],"tcp_start":[0.5634,0.08577,0.24528],"tcp_to_object_dist_end":0.28653,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47954,-0.02602,0.01602],"object_pos_start":[0.47954,-0.02602,0.01602],"object_to_goal_dist_end":0.29605,"object_to_goal_dist_start":0.29605,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61959,0.154,0.20268],"tcp_start":[0.62516,0.15557,0.18312],"tcp_to_object_dist_end":0.29473,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.47954,-0.02602,0.01602],"object_pos_start":[0.47954,-0.02602,0.01602],"object_to_goal_dist_end":0.29605,"object_to_goal_dist_start":0.29605,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62893,0.1582,0.32166],"tcp_start":[0.61959,0.154,0.20268],"tcp_to_object_dist_end":0.38687,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.22581,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.29116,"approach_1.approach_z":0.07696,"approach_2.approach2_z":0.05353,"approach_2.transport_speed":0.23867,"descend_1.descend_speed":0.2453,"descend_2.place_speed":0.08904,"grasp_1.grasp_force_threshold":2.59855,"lift_1.lift_speed":0.10385,"lift_1.lift_z":0.10524,"release_1.release_duration":0.54558,"retract_1.retract_speed":0.30049},"optimized_scores":{"best_composite_score":-0.04832,"best_fitness_score":0.68168,"best_task_score":0.40153},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":138.0,"contact_point_centroid":[0.57974,0.13368,-0.00738],"force_p95":1.17664,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.39691,"mean_force":0.49657,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.56711,0.12898,0.14456]},{"body_a":"world","body_b":"grasp_target","contact_count":124.0,"contact_point_centroid":[0.45637,-0.02489,-0.00112],"force_p95":0.45061,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61048,"mean_force":0.06387,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44569,-0.02554,0.02951]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9613.0,"contact_point_centroid":[0.5015,0.01783,0.12726],"force_p95":0.15755,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32065,"mean_force":0.0887,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49721,0.03661,0.12758]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9546.0,"contact_point_centroid":[0.44992,-0.0065,0.07224],"force_p95":0.09973,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27932,"mean_force":0.06159,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44817,-0.02545,0.07034]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9954.0,"contact_point_centroid":[0.44971,-0.04441,0.07025],"force_p95":0.10109,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27428,"mean_force":0.05982,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44799,-0.02545,0.06875]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12239.0,"contact_point_centroid":[0.50814,0.06404,0.12914],"force_p95":0.10086,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1989,"mean_force":0.06929,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.50415,0.04581,0.12926]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02615,-0.00206],"force_p95":0.14082,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19383,"mean_force":0.12756,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44779,-0.02563,0.02873]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.57928,0.12743,-0.00199],"force_p95":0.1233,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15248,"mean_force":0.12196,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59698,0.17065,0.12134]},{"body_a":"world","body_b":"grasp_target","contact_count":1928.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47833,-0.01189,0.20812]},{"body_a":"world","body_b":"grasp_target","contact_count":1076.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4549,-0.02498,0.07548]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57928,0.12744,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61456,0.19742,0.10851]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.57928,0.12744,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.61747,0.20082,0.18222]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4813.0,"contact_point_centroid":[0.44674,-0.00638,0.0301],"force_p95":0.0682,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09821,"mean_force":0.04489,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44671,-0.02559,0.02771]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5174.0,"contact_point_centroid":[0.44659,-0.04482,0.02959],"force_p95":0.06705,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08247,"mean_force":0.04302,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44671,-0.02559,0.02772]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4150.0,"contact_point_centroid":[0.59818,0.17174,0.12294],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0161,"mean_force":0.0105,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59777,0.17173,0.12069]},{"body_a":"left_finger","body_b":"right_finger","contact_count":227.0,"contact_point_centroid":[0.61852,0.19863,0.10741],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.00988,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61785,0.19862,0.1052]}],"total_contact_groups":16},"final_pose_error":0.01905,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.57928,0.12744,0.01602],"final_tcp_position":[0.62627,0.20637,0.24555],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.39691,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":483.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1928.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.45782,-0.02422,0.11648],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09049,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":269.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1076.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45428,-0.02585,0.03491],"tcp_start":[0.45782,-0.02422,0.11648],"tcp_to_object_dist_end":0.00988,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02563,0.02579],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30325,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13792,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11787.0,"raw_peak_contact_force":0.19383,"tcp_end":[0.44668,-0.02558,0.02769],"tcp_start":[0.45428,-0.02585,0.03491],"tcp_to_object_dist_end":0.01191,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.47096,-0.02552,0.11041],"object_pos_start":[0.45844,-0.02563,0.02579],"object_to_goal_dist_end":0.28281,"object_to_goal_dist_start":0.30325,"object_z_max":0.1103,"peak_contact_force":0.11399,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19624.0,"raw_peak_contact_force":0.61048,"tcp_end":[0.45379,-0.02546,0.11987],"tcp_start":[0.44668,-0.02558,0.02769],"tcp_to_object_dist_end":0.01961,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58078,0.13198,0.01268],"object_pos_start":[0.47096,-0.02552,0.11041],"object_to_goal_dist_end":0.13615,"object_to_goal_dist_start":0.28281,"object_z_max":0.11678,"peak_contact_force":0.16061,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21990.0,"raw_peak_contact_force":1.39691,"subtask_id":"reach_goal","tcp_end":[0.57011,0.13285,0.14529],"tcp_start":[0.45379,-0.02546,0.11987],"tcp_to_object_dist_end":0.13304,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57928,0.12744,0.01602],"object_pos_start":[0.58078,0.13198,0.01268],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.13615,"object_z_max":0.01679,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8150.0,"raw_peak_contact_force":0.15248,"subtask_id":"reach_goal","tcp_end":[0.61954,0.19901,0.10837],"tcp_start":[0.57011,0.13285,0.14529],"tcp_to_object_dist_end":0.12358,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57928,0.12744,0.01602],"object_pos_start":[0.57928,0.12744,0.01602],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.13687,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61259,0.1967,0.12783],"tcp_start":[0.61954,0.19901,0.10837],"tcp_to_object_dist_end":0.13568,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.57928,0.12744,0.01602],"object_pos_start":[0.57928,0.12744,0.01602],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.13687,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62627,0.20637,0.24555],"tcp_start":[0.61259,0.1967,0.12783],"tcp_to_object_dist_end":0.24723,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```