## Search State

- **Seed**: 1
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | 0.0256 | 0.44 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.0121 | 0.19 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | 0.2785 | 0.41 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.3531 | 0.41 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.2507 | 0.20 | ❌ rejected |

**Proposal policy**: task_score is 0.44 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.026) — your mutation base

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
  - 0.15
  weight: 0.3
- id: reach_goal
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.7
phases:
- id: approach_object
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  subtask_id: reach_object
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_xy_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    grasp_xy_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: replace
  subtask_id: reach_object
- id: grasp
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
  - id: grasp_hold
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
- id: lift
  type: lift
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.18
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.18
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
- id: approach_goal
  type: approach
  generator: arc_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
  subtask_id: reach_goal
- id: descend_place
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
    - 0.03
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    place_xy_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    place_xy_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: replace
  subtask_id: reach_goal
- id: release
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
    release_wait_time:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace
- id: retract
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
    - 0.3
    tolerance: 0.02
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_xy_offset_x: status=consumed; consumers=target.offset.x (replace)
    - grasp_xy_offset_y: status=consumed; consumers=target.offset.y (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_hold, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.18], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_xy_offset_x: status=consumed; consumers=target.offset.x (replace)
    - place_xy_offset_y: status=consumed; consumers=target.offset.y (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_wait_time: status=consumed; consumers=duration.max_time (replace)
- **retract** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.3], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.026
- **task_score** (E): 0.445
- **fitness_score**: 0.706  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.680

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1084 |
| descend_to_grasp | 1.00 | 1.00 | 0.1538 |
| grasp | 1.00 | 1.00 | 0.0121 |
| lift | 1.00 | 1.00 | 0.1630 |
| approach_goal | 1.00 | 1.00 | 0.2538 |
| descend_place | 1.00 | 1.00 | 0.1133 |
| release | 1.00 | 1.00 | 0.0192 |
| retract | 1.00 | 1.00 | 0.2149 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.480, -0.000, 0.198) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.480, -0.000, 0.198)→(0.487, -0.000, 0.045) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 44.000 | 0.143 | 0.190 |
| grasp | grasp | 1.00 / step_budget | (0.487, -0.000, 0.045)→(0.479, -0.000, 0.036) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 40.000 | 0.070 | 0.529 |
| lift | lift | 1.00 / step_budget | (0.479, -0.000, 0.036)→(0.475, -0.000, 0.199) | (0.479, -0.000, 0.026)→(0.475, -0.000, 0.187) | 0.278→0.253 | 1.00 / 40.000 | 0.071 | 0.109 |
| approach_goal | approach | 1.00 / step_budget | (0.475, -0.000, 0.199)→(0.594, 0.185, 0.308) | (0.475, -0.000, 0.187)→(0.600, 0.185, 0.292) | 0.253→0.143 | 1.00 / 40.000 | 0.076 | 0.231 |
| descend_place | descend | 1.00 / step_budget | (0.594, 0.185, 0.308)→(0.611, 0.200, 0.197) | (0.600, 0.185, 0.292)→(0.607, 0.199, 0.180) | 0.143→0.031 | 1.00 / 4.000 | 0.089 | 1.739 |
| release | release | 1.00 / step_budget | (0.611, 0.200, 0.197)→(0.606, 0.198, 0.216) | (0.607, 0.199, 0.180)→(0.599, 0.199, 0.024) | 0.031→0.127 | 1.00 / 4.000 | 0.123 | 0.137 |
| retract | retract | 1.00 / step_budget | (0.606, 0.198, 0.216)→(0.609, 0.203, 0.430) | (0.599, 0.199, 0.024)→(0.600, 0.201, 0.026) | 0.127→0.125 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.555
- phase_score: 0.501
- phase_breakdown.reach_goal_score: 0.687
- phase_breakdown.reach_object_score: 0.067
- grasp_place_fitness: 0.759

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.759
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.555
- **Median Q (composite search score)**: 0.028
- **K-run variance**: 0.0020
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.350


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20283,"average_solve_count":424.0,"average_success_count":424.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_speed":0.01351,"approach_goal.arc_height":0.13041,"descend_place.place_xy_offset_x":0.00271,"descend_place.place_xy_offset_y":0.00118,"descend_to_grasp.descend_speed":0.03534,"descend_to_grasp.grasp_xy_offset_x":0.01357,"descend_to_grasp.grasp_xy_offset_y":0.0023,"lift.lift_height":0.18414,"lift.lift_speed":0.03672,"release.release_wait_time":0.32816},"optimized_scores":{"best_composite_score":0.02773,"best_fitness_score":0.70773,"best_task_score":0.44499},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":222.0,"contact_point_centroid":[0.55167,0.24317,-0.00681],"force_p95":1.02643,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.75477,"mean_force":0.32597,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.55737,0.23882,0.20689]},{"body_a":"world","body_b":"grasp_target","contact_count":98.0,"contact_point_centroid":[0.49685,0.04432,-0.00153],"force_p95":0.49907,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51863,"mean_force":0.18921,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49858,0.0445,0.03599]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11600.0,"contact_point_centroid":[0.49635,0.06343,0.11757],"force_p95":0.07141,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28625,"mean_force":0.05081,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49614,0.04427,0.11578]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11600.0,"contact_point_centroid":[0.49638,0.02514,0.11775],"force_p95":0.0708,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25461,"mean_force":0.05028,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49614,0.04427,0.11578]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3940.0,"contact_point_centroid":[0.55993,0.25379,0.25364],"force_p95":0.07936,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24563,"mean_force":0.05259,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55969,0.23485,0.25202]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3940.0,"contact_point_centroid":[0.56,0.21551,0.25417],"force_p95":0.07799,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18868,"mean_force":0.05195,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55969,0.23485,0.25202]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1214.0,"contact_point_centroid":[0.56098,0.22129,0.19278],"force_p95":0.07729,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16948,"mean_force":0.04546,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.56066,0.24053,0.19059]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50116,0.04497,-0.00205],"force_p95":0.1349,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16176,"mean_force":0.12642,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50095,0.04473,0.03613]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1239.0,"contact_point_centroid":[0.56091,0.25967,0.19211],"force_p95":0.07639,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16009,"mean_force":0.04458,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.56064,0.24052,0.19054]},{"body_a":"world","body_b":"grasp_target","contact_count":3132.0,"contact_point_centroid":[0.5515,0.24314,-0.00198],"force_p95":0.12412,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14519,"mean_force":0.12175,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.5592,0.24083,0.32023]},{"body_a":"world","body_b":"grasp_target","contact_count":836.0,"contact_point_centroid":[0.50118,0.04505,-0.00185],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12321,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49872,0.0172,0.25009]},{"body_a":"world","body_b":"grasp_target","contact_count":1264.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50198,0.04059,0.12202]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4836.0,"contact_point_centroid":[0.5,0.02544,0.03684],"force_p95":0.06962,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10673,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49979,0.04462,0.03488]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18820.0,"contact_point_centroid":[0.5138,0.1193,0.30068],"force_p95":0.07011,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10659,"mean_force":0.0489,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51357,0.10015,0.29894]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18820.0,"contact_point_centroid":[0.51383,0.08103,0.30096],"force_p95":0.0705,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09942,"mean_force":0.04884,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51357,0.10015,0.29894]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4892.0,"contact_point_centroid":[0.49998,0.06384,0.0367],"force_p95":0.06991,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08905,"mean_force":0.04485,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49979,0.04462,0.03488]}],"total_contact_groups":16},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.5515,0.24314,0.02602],"final_tcp_position":[0.56382,0.24409,0.42687],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.75477,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":210.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1264.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49827,0.03619,0.19753],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17176,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":316.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.13332,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11528.0,"raw_peak_contact_force":0.16176,"subtask_id":"reach_object","tcp_end":[0.50829,0.04539,0.04448],"tcp_start":[0.49827,0.03619,0.19753],"tcp_to_object_dist_end":0.01978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50105,0.04469,0.02581],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24232,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.07016,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":23298.0,"raw_peak_contact_force":0.51863,"tcp_end":[0.49976,0.04462,0.03484],"tcp_start":[0.50829,0.04539,0.04448],"tcp_to_object_dist_end":0.00913,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":580.0,"n_steps_budget":1000.0,"object_pos_end":[0.4975,0.04429,0.18847],"object_pos_start":[0.50105,0.04469,0.02581],"object_to_goal_dist_end":0.21551,"object_to_goal_dist_start":0.24232,"object_z_max":0.18819,"peak_contact_force":0.07167,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37640.0,"raw_peak_contact_force":0.10659,"tcp_end":[0.49646,0.0443,0.19927],"tcp_start":[0.49976,0.04462,0.03484],"tcp_to_object_dist_end":0.01085,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":941.0,"n_steps_budget":1000.0,"object_pos_end":[0.5632,0.22896,0.29201],"object_pos_start":[0.4975,0.04429,0.18847],"object_to_goal_dist_end":0.14611,"object_to_goal_dist_start":0.21551,"object_z_max":0.33225,"peak_contact_force":0.07848,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7880.0,"raw_peak_contact_force":0.24563,"subtask_id":"reach_goal","tcp_end":[0.55771,0.22907,0.30682],"tcp_start":[0.49646,0.0443,0.19927],"tcp_to_object_dist_end":0.01579,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":197.0,"n_steps_budget":1000.0,"object_pos_end":[0.55503,0.24007,0.17901],"object_pos_start":[0.5632,0.22896,0.29201],"object_to_goal_dist_end":0.03391,"object_to_goal_dist_start":0.14611,"object_z_max":0.29201,"peak_contact_force":0.0851,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2675.0,"raw_peak_contact_force":1.75477,"subtask_id":"reach_goal","tcp_end":[0.56269,0.24129,0.19551],"tcp_start":[0.55771,0.22907,0.30682],"tcp_to_object_dist_end":0.01823,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54969,0.24138,0.02468],"object_pos_start":[0.55503,0.24007,0.17901],"object_to_goal_dist_end":0.12303,"object_to_goal_dist_start":0.03391,"object_z_max":0.17901,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":3132.0,"raw_peak_contact_force":0.14519,"tcp_end":[0.55732,0.23881,0.21532],"tcp_start":[0.56269,0.24129,0.19551],"tcp_to_object_dist_end":0.19081,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":783.0,"n_steps_budget":1000.0,"object_pos_end":[0.5515,0.24314,0.02602],"object_pos_start":[0.54969,0.24138,0.02468],"object_to_goal_dist_end":0.12146,"object_to_goal_dist_start":0.12303,"object_z_max":0.02667,"peak_contact_force":0.12262,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":836.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.56382,0.24409,0.42687],"tcp_start":[0.55732,0.23881,0.21532],"tcp_to_object_dist_end":0.40104,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21078,"average_solve_count":408.0,"average_success_count":408.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_speed":0.02402,"approach_goal.arc_height":0.09521,"descend_place.place_xy_offset_x":0.01282,"descend_place.place_xy_offset_y":0.00265,"descend_to_grasp.descend_speed":0.02692,"descend_to_grasp.grasp_xy_offset_x":0.0156,"descend_to_grasp.grasp_xy_offset_y":-0.00167,"lift.lift_height":0.1652,"lift.lift_speed":0.04831,"release.release_wait_time":0.77657},"optimized_scores":{"best_composite_score":-0.02982,"best_fitness_score":0.65018,"best_task_score":0.33457},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":180.0,"contact_point_centroid":[0.62307,0.15617,-0.00869],"force_p95":1.175,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.96786,"mean_force":0.41712,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62986,0.15398,0.24656]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.47215,-0.02077,-0.0015],"force_p95":0.52399,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54624,"mean_force":0.17178,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47655,-0.0207,0.03769]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9880.0,"contact_point_centroid":[0.47434,-0.00148,0.10987],"force_p95":0.07087,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29157,"mean_force":0.05145,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47413,-0.02063,0.10795]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9880.0,"contact_point_centroid":[0.47437,-0.03978,0.1098],"force_p95":0.0707,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2914,"mean_force":0.05135,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47413,-0.02063,0.10795]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1220.0,"contact_point_centroid":[0.63321,0.13587,0.23216],"force_p95":0.07159,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22345,"mean_force":0.04469,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63288,0.15505,0.23016]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1236.0,"contact_point_centroid":[0.63313,0.17426,0.23186],"force_p95":0.07347,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20897,"mean_force":0.04462,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63287,0.15505,0.23012]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4200.0,"contact_point_centroid":[0.62036,0.12407,0.29476],"force_p95":0.08694,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17972,"mean_force":0.05375,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62007,0.14329,0.2928]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47613,-0.02022,-0.00206],"force_p95":0.13905,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17653,"mean_force":0.12754,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47878,-0.02075,0.03743]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4200.0,"contact_point_centroid":[0.62032,0.16235,0.2946],"force_p95":0.08347,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17332,"mean_force":0.05398,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62007,0.14329,0.2928]},{"body_a":"world","body_b":"grasp_target","contact_count":776.0,"contact_point_centroid":[0.47616,-0.02015,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12326,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48942,-0.00754,0.25146]},{"body_a":"world","body_b":"grasp_target","contact_count":3392.0,"contact_point_centroid":[0.62306,0.15608,-0.002],"force_p95":0.12342,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13626,"mean_force":0.12093,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.62966,0.15602,0.35952]},{"body_a":"world","body_b":"grasp_target","contact_count":1304.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.48093,-0.01832,0.1237]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.51478,0.04674,0.30134],"force_p95":0.07012,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11407,"mean_force":0.04935,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51455,0.02761,0.29944]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.51481,0.00847,0.30131],"force_p95":0.07122,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11248,"mean_force":0.04944,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51455,0.02761,0.29944]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4828.0,"contact_point_centroid":[0.47787,-0.03992,0.03816],"force_p95":0.06934,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10907,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47766,-0.02072,0.0363]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4908.0,"contact_point_centroid":[0.47785,-0.00152,0.03822],"force_p95":0.06962,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0903,"mean_force":0.04472,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47766,-0.02072,0.0363]}],"total_contact_groups":16},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62306,0.15608,0.02602],"final_tcp_position":[0.63239,0.15891,0.47011],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.96786,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":195.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1304.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47852,-0.01598,0.19941],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17346,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":326.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13693,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11536.0,"raw_peak_contact_force":0.17653,"subtask_id":"reach_object","tcp_end":[0.48591,-0.0209,0.04507],"tcp_start":[0.47852,-0.01598,0.19941],"tcp_to_object_dist_end":0.02141,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.02061,0.02575],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28889,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.06945,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":19852.0,"raw_peak_contact_force":0.54624,"tcp_end":[0.47763,-0.02072,0.03627],"tcp_start":[0.48591,-0.0209,0.04507],"tcp_to_object_dist_end":0.01063,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":494.0,"n_steps_budget":1000.0,"object_pos_end":[0.47313,-0.02056,0.16939],"object_pos_start":[0.47603,-0.02061,0.02575],"object_to_goal_dist_end":0.2404,"object_to_goal_dist_start":0.28889,"object_z_max":0.16911,"peak_contact_force":0.07035,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40000.0,"raw_peak_contact_force":0.11407,"tcp_end":[0.47428,-0.02062,0.18183],"tcp_start":[0.47763,-0.02072,0.03627],"tcp_to_object_dist_end":0.01249,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61435,0.13223,0.33184],"object_pos_start":[0.47313,-0.02056,0.16939],"object_to_goal_dist_end":0.14537,"object_to_goal_dist_start":0.2404,"object_z_max":0.34225,"peak_contact_force":0.07395,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8400.0,"raw_peak_contact_force":0.17972,"subtask_id":"reach_goal","tcp_end":[0.60721,0.13231,0.34845],"tcp_start":[0.47428,-0.02062,0.18183],"tcp_to_object_dist_end":0.01808,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":210.0,"n_steps_budget":1000.0,"object_pos_end":[0.63224,0.15488,0.21817],"object_pos_start":[0.61435,0.13223,0.33184],"object_to_goal_dist_end":0.0285,"object_to_goal_dist_start":0.14537,"object_z_max":0.33184,"peak_contact_force":0.07768,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2636.0,"raw_peak_contact_force":1.96786,"subtask_id":"reach_goal","tcp_end":[0.63468,0.15535,0.23573],"tcp_start":[0.60721,0.13231,0.34845],"tcp_to_object_dist_end":0.01773,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62396,0.15415,0.02106],"object_pos_start":[0.63224,0.15488,0.21817],"object_to_goal_dist_end":0.1692,"object_to_goal_dist_start":0.0285,"object_z_max":0.21817,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":3392.0,"raw_peak_contact_force":0.13626,"tcp_end":[0.62984,0.15397,0.25347],"tcp_start":[0.63468,0.15535,0.23573],"tcp_to_object_dist_end":0.23249,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":848.0,"n_steps_budget":1000.0,"object_pos_end":[0.62306,0.15608,0.02602],"object_pos_start":[0.62396,0.15415,0.02106],"object_to_goal_dist_end":0.16424,"object_to_goal_dist_start":0.1692,"object_z_max":0.02673,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":776.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.63239,0.15891,0.47011],"tcp_start":[0.62984,0.15397,0.25347],"tcp_to_object_dist_end":0.4442,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20375,"average_solve_count":427.0,"average_success_count":427.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_speed":0.02103,"approach_goal.arc_height":0.07148,"descend_place.place_xy_offset_x":0.01543,"descend_place.place_xy_offset_y":-0.00087,"descend_to_grasp.descend_speed":0.03471,"descend_to_grasp.grasp_xy_offset_x":0.01274,"descend_to_grasp.grasp_xy_offset_y":0.00079,"lift.lift_height":0.19849,"lift.lift_speed":0.0394,"release.release_wait_time":0.49789},"optimized_scores":{"best_composite_score":0.07887,"best_fitness_score":0.75887,"best_task_score":0.55469},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":272.0,"contact_point_centroid":[0.62493,0.20324,-0.00539],"force_p95":0.84106,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.4929,"mean_force":0.25719,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62996,0.20087,0.16802]},{"body_a":"world","body_b":"grasp_target","contact_count":96.0,"contact_point_centroid":[0.45468,-0.02443,-0.00165],"force_p95":0.48162,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52144,"mean_force":0.17618,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45732,-0.02452,0.03827]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11880.0,"contact_point_centroid":[0.45531,-0.04356,0.12725],"force_p95":0.0743,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28889,"mean_force":0.05133,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45508,-0.02441,0.12538]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11880.0,"contact_point_centroid":[0.45529,-0.00526,0.12729],"force_p95":0.0737,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26813,"mean_force":0.05072,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45508,-0.02441,0.12538]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1216.0,"contact_point_centroid":[0.63431,0.18326,0.15715],"force_p95":0.07319,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26721,"mean_force":0.04544,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63399,0.20243,0.15509]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3800.0,"contact_point_centroid":[0.62615,0.21712,0.21729],"force_p95":0.08653,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26693,"mean_force":0.05523,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62592,0.19805,0.21551]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3800.0,"contact_point_centroid":[0.62623,0.17884,0.21751],"force_p95":0.08997,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26254,"mean_force":0.05478,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62592,0.19805,0.21551]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1239.0,"contact_point_centroid":[0.6342,0.22165,0.15674],"force_p95":0.07359,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25774,"mean_force":0.045,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63396,0.20242,0.15503]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45854,-0.02614,-0.00217],"force_p95":0.16696,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23228,"mean_force":0.13536,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45951,-0.02458,0.03795]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4786.0,"contact_point_centroid":[0.45862,-0.00536,0.03883],"force_p95":0.07419,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14037,"mean_force":0.04483,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45844,-0.02455,0.03691]},{"body_a":"world","body_b":"grasp_target","contact_count":824.0,"contact_point_centroid":[0.45856,-0.02632,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12322,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48245,-0.01007,0.25052]},{"body_a":"world","body_b":"grasp_target","contact_count":3552.0,"contact_point_centroid":[0.62481,0.20319,-0.00198],"force_p95":0.12316,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13036,"mean_force":0.12243,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.62805,0.2036,0.28538]},{"body_a":"world","body_b":"grasp_target","contact_count":1280.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4641,-0.02293,0.12277]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18520.0,"contact_point_centroid":[0.52561,0.05205,0.28164],"force_p95":0.07085,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10595,"mean_force":0.04892,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52536,0.07119,0.27975]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18520.0,"contact_point_centroid":[0.52559,0.09033,0.28163],"force_p95":0.07047,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09739,"mean_force":0.04867,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52536,0.07119,0.27975]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5033.0,"contact_point_centroid":[0.45865,-0.04383,0.0388],"force_p95":0.07487,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07894,"mean_force":0.04447,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45844,-0.02455,0.03691]}],"total_contact_groups":16},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62481,0.20319,0.02602],"final_tcp_position":[0.62971,0.20744,0.39433],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.4929,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":207.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1280.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.46401,-0.02124,0.19803],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17218,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":320.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.15954,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11619.0,"raw_peak_contact_force":0.23228,"subtask_id":"reach_object","tcp_end":[0.46644,-0.02479,0.04505],"tcp_start":[0.46401,-0.02124,0.19803],"tcp_to_object_dist_end":0.02065,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45843,-0.02494,0.02537],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30285,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.07158,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":23856.0,"raw_peak_contact_force":0.52144,"tcp_end":[0.45841,-0.02455,0.03688],"tcp_start":[0.46644,-0.02479,0.04505],"tcp_to_object_dist_end":0.01152,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":594.0,"n_steps_budget":1000.0,"object_pos_end":[0.45571,-0.02453,0.20228],"object_pos_start":[0.45843,-0.02494,0.02537],"object_to_goal_dist_end":0.30392,"object_to_goal_dist_start":0.30285,"object_z_max":0.20199,"peak_contact_force":0.07104,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37040.0,"raw_peak_contact_force":0.10595,"tcp_end":[0.4554,-0.02441,0.21581],"tcp_start":[0.45841,-0.02455,0.03688],"tcp_to_object_dist_end":0.01353,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":926.0,"n_steps_budget":1000.0,"object_pos_end":[0.62178,0.19334,0.25151],"object_pos_start":[0.45571,-0.02453,0.20228],"object_to_goal_dist_end":0.13845,"object_to_goal_dist_start":0.30392,"object_z_max":0.28977,"peak_contact_force":0.07523,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7600.0,"raw_peak_contact_force":0.26693,"subtask_id":"reach_goal","tcp_end":[0.6176,0.19343,0.26839],"tcp_start":[0.4554,-0.02441,0.21581],"tcp_to_object_dist_end":0.01738,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":190.0,"n_steps_budget":1000.0,"object_pos_end":[0.63459,0.20271,0.14352],"object_pos_start":[0.62178,0.19334,0.25151],"object_to_goal_dist_end":0.03024,"object_to_goal_dist_start":0.13845,"object_z_max":0.25151,"peak_contact_force":0.10537,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2727.0,"raw_peak_contact_force":1.4929,"subtask_id":"reach_goal","tcp_end":[0.63638,0.20319,0.16107],"tcp_start":[0.6176,0.19343,0.26839],"tcp_to_object_dist_end":0.01765,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62465,0.20274,0.02629],"object_pos_start":[0.63459,0.20271,0.14352],"object_to_goal_dist_end":0.08817,"object_to_goal_dist_start":0.03024,"object_z_max":0.14352,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":3552.0,"raw_peak_contact_force":0.13036,"tcp_end":[0.6299,0.20085,0.17812],"tcp_start":[0.63638,0.20319,0.16107],"tcp_to_object_dist_end":0.15192,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":888.0,"n_steps_budget":1000.0,"object_pos_end":[0.62481,0.20319,0.02602],"object_pos_start":[0.62465,0.20274,0.02629],"object_to_goal_dist_end":0.0884,"object_to_goal_dist_start":0.08817,"object_z_max":0.02653,"peak_contact_force":0.12262,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":824.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.62971,0.20744,0.39433],"tcp_start":[0.6299,0.20085,0.17812],"tcp_to_object_dist_end":0.36837,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```