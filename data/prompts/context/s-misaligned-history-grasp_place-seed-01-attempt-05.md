## Search State

- **Seed**: 1
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9  | -0.0517 | 0.23 | ❌ rejected |
| 4 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9  | -0.0330 | 0.33 | ✅ accepted |
| 3 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8  | -0.0552 | 0.29 | ✅ accepted |
| 2 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8  | -0.3662 | 0.14 | ❌ rejected |
| 1 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7  | 0.0115 | 0.36 | ✅ accepted |

**Proposal policy**: task_score is 0.36 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.012) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: place_goal
  target_entity: object
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
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: align_grasp
  type: align
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
    - 0.03
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
  subtask_id: reach_object
- id: grasp
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
    orientation:
      mode: keep_current
  guards:
  - id: bilateral_grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: lift
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
    - 0.0
    offset_along_axis:
      distance: 0.12
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 0.8
      default: 0.4
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_goal
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
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.1
      - 0.8
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_goal
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
    orientation:
      mode: keep_current
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
- id: retract
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **align_grasp** (`align`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=bilateral_grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=repeat
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.12, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.012
- **task_score** (E): 0.358
- **fitness_score**: 0.642  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1668 |
| align_grasp | 1.00 | 1.00 | 0.0822 |
| grasp | 1.00 | 1.00 | 0.0110 |
| lift | 0.67 | 1.00 | 0.1013 |
| approach_goal | 1.00 | 0.67 | 0.2526 |
| descend_place | 1.00 | 1.00 | 0.0833 |
| release | 1.00 | 1.00 | 0.0198 |
| retract | 1.00 | 1.00 | 0.0851 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.477, -0.000, 0.139) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| align_grasp | align | 1.00 / step_budget | (0.477, -0.000, 0.139)→(0.480, -0.000, 0.057) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.480, -0.000, 0.057)→(0.473, -0.000, 0.049) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 41.333 | 0.142 | 0.170 |
| lift | lift | 0.67 / step_budget | (0.473, -0.000, 0.049)→(0.473, -0.000, 0.150) | (0.479, -0.000, 0.026)→(0.476, -0.000, 0.120) | 0.278→0.251 | 1.00 / 27.333 | 0.107 | 0.380 |
| approach_goal | approach | 1.00 / step_budget | (0.473, -0.000, 0.150)→(0.597, 0.188, 0.251) | (0.476, -0.000, 0.120)→(0.570, 0.136, 0.039) | 0.251→0.140 | 0.67 / 5.333 | 3249.634 | 1.357 |
| descend_place | descend | 1.00 / step_budget | (0.597, 0.188, 0.251)→(0.603, 0.199, 0.168) | (0.570, 0.136, 0.039)→(0.573, 0.143, 0.016) | 0.140→0.163 | 1.00 / 8.333 | 94253.422 | 0.706 |
| release | release | 1.00 / step_budget | (0.603, 0.199, 0.168)→(0.596, 0.197, 0.187) | (0.573, 0.143, 0.016)→(0.572, 0.143, 0.016) | 0.163→0.163 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.596, 0.197, 0.187)→(0.594, 0.196, 0.272) | (0.572, 0.143, 0.016)→(0.572, 0.143, 0.016) | 0.163→0.163 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.455
- phase_score: 0.662
- phase_breakdown.place_goal_score: 0.671
- phase_breakdown.reach_object_score: 0.642
- grasp_place_fitness: 0.687

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.687
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.455
- **Median Q (composite search score)**: 0.043
- **K-run variance**: 0.0030
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.308


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88957,"average_solve_count":163.0,"average_success_count":163.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_grasp.lateral_offset_x":0.00853,"align_grasp.lateral_offset_y":0.00074,"approach_goal.arc_height":0.05726,"approach_goal.transport_speed":0.43515,"approach_object.approach_speed":0.08359,"descend_place.descend_speed":0.63191,"lift.lift_height":0.16515,"lift.lift_speed":0.06325,"release.release_duration":1.63398},"optimized_scores":{"best_composite_score":0.043,"best_fitness_score":0.673,"best_task_score":0.41549},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":503.0,"contact_point_centroid":[0.5647,0.26036,-0.0044],"force_p95":0.99246,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.86352,"mean_force":0.22872,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55767,0.23337,0.20072]},{"body_a":"world","body_b":"grasp_target","contact_count":184.0,"contact_point_centroid":[0.49811,0.04378,-0.00121],"force_p95":0.23626,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40689,"mean_force":0.05905,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49467,0.04413,0.04943]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5265.0,"contact_point_centroid":[0.51367,0.07773,0.20955],"force_p95":0.13625,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3429,"mean_force":0.0898,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51152,0.09625,0.21242]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.4941,0.06282,0.09944],"force_p95":0.07635,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30051,"mean_force":0.05017,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49401,0.04396,0.09875]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16725.0,"contact_point_centroid":[0.49307,0.02481,0.09828],"force_p95":0.09851,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28381,"mean_force":0.06021,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49397,0.04396,0.09766]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6143.0,"contact_point_centroid":[0.51225,0.10892,0.20584],"force_p95":0.13298,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22536,"mean_force":0.07891,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5096,0.09056,0.20725]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50118,0.04495,-0.00207],"force_p95":0.14231,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18183,"mean_force":0.12812,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49748,0.04441,0.04896]},{"body_a":"world","body_b":"grasp_target","contact_count":2096.0,"contact_point_centroid":[0.50118,0.04505,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49772,0.0201,0.21902]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4105.0,"contact_point_centroid":[0.49561,0.02509,0.04902],"force_p95":0.0783,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13521,"mean_force":0.05201,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49633,0.0443,0.04768]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56444,0.26098,-0.00199],"force_p95":0.12342,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12409,"mean_force":0.12269,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.55506,0.23702,0.16508]},{"body_a":"world","body_b":"grasp_target","contact_count":2076.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.49927,0.043,0.09464]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.56444,0.26098,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.55087,0.23503,0.22601]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4910.0,"contact_point_centroid":[0.49645,0.06338,0.04884],"force_p95":0.071,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07936,"mean_force":0.0445,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49633,0.0443,0.04769]},{"body_a":"left_finger","body_b":"right_finger","contact_count":333.0,"contact_point_centroid":[0.55859,0.2353,0.18964],"force_p95":0.0138,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01642,"mean_force":0.01125,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55828,0.23527,0.18733]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.55781,0.23826,0.16285],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01264,"mean_force":0.01012,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.55748,0.23822,0.16051]}],"total_contact_groups":15},"final_pose_error":0.01465,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.56444,0.26098,0.01602],"final_tcp_position":[0.55111,0.23507,0.27071],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":273011.36008,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":525.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2096.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49737,0.04112,0.13827],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11238,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":519.0,"n_steps_budget":600.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2076.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50413,0.04502,0.05641],"tcp_start":[0.49737,0.04112,0.13827],"tcp_to_object_dist_end":0.03053,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50109,0.0444,0.02572],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24259,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.14028,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10815.0,"raw_peak_contact_force":0.18183,"tcp_end":[0.4963,0.0443,0.04765],"tcp_start":[0.50413,0.04502,0.05641],"tcp_to_object_dist_end":0.02244,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50008,0.0448,0.12273],"object_pos_start":[0.50109,0.0444,0.02572],"object_to_goal_dist_end":0.21153,"object_to_goal_dist_start":0.24259,"object_z_max":0.12261,"peak_contact_force":0.11935,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36909.0,"raw_peak_contact_force":0.40689,"tcp_end":[0.49585,0.04401,0.15044],"tcp_start":[0.4963,0.0443,0.04765],"tcp_to_object_dist_end":0.02804,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":584.0,"n_steps_budget":1000.0,"object_pos_end":[0.55776,0.2408,0.08552],"object_pos_start":[0.50008,0.0448,0.12273],"object_to_goal_dist_end":0.06175,"object_to_goal_dist_start":0.21153,"object_z_max":0.21863,"peak_contact_force":0.0,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11408.0,"raw_peak_contact_force":0.3429,"subtask_id":"place_goal","tcp_end":[0.55647,0.2269,0.24549],"tcp_start":[0.49585,0.04401,0.15044],"tcp_to_object_dist_end":0.16058,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":146.0,"n_steps_budget":1000.0,"object_pos_end":[0.56451,0.26099,0.01602],"object_pos_start":[0.55776,0.2408,0.08552],"object_to_goal_dist_end":0.13175,"object_to_goal_dist_start":0.06175,"object_z_max":0.08552,"peak_contact_force":273011.36008,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":836.0,"raw_peak_contact_force":1.86352,"subtask_id":"place_goal","tcp_end":[0.55957,0.2389,0.16503],"tcp_start":[0.55647,0.2269,0.24549],"tcp_to_object_dist_end":0.15072,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56444,0.26098,0.01602],"object_pos_start":[0.56451,0.26099,0.01602],"object_to_goal_dist_end":0.13175,"object_to_goal_dist_start":0.13175,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12409,"tcp_end":[0.55359,0.23629,0.1851],"tcp_start":[0.55957,0.2389,0.16503],"tcp_to_object_dist_end":0.17121,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.56444,0.26098,0.01602],"object_pos_start":[0.56444,0.26098,0.01602],"object_to_goal_dist_end":0.13175,"object_to_goal_dist_start":0.13175,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55111,0.23507,0.27071],"tcp_start":[0.55359,0.23629,0.1851],"tcp_to_object_dist_end":0.25635,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34167,"average_solve_count":240.0,"average_success_count":240.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_grasp.lateral_offset_x":0.00761,"align_grasp.lateral_offset_y":0.00049,"approach_goal.arc_height":0.0908,"approach_goal.transport_speed":0.40816,"approach_object.approach_speed":0.02568,"descend_place.descend_speed":0.26262,"lift.lift_height":0.16979,"lift.lift_speed":0.0632,"release.release_duration":1.36771},"optimized_scores":{"best_composite_score":-0.06566,"best_fitness_score":0.56434,"best_task_score":0.20263},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1237.0,"contact_point_centroid":[0.53855,0.02328,-0.00303],"force_p95":0.49998,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.90089,"mean_force":0.16484,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56748,0.08937,0.30516]},{"body_a":"world","body_b":"grasp_target","contact_count":173.0,"contact_point_centroid":[0.47336,-0.01885,-0.00122],"force_p95":0.24084,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37859,"mean_force":0.05215,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4696,-0.01926,0.05106]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13778.0,"contact_point_centroid":[0.4694,-0.00027,0.0948],"force_p95":0.11091,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27557,"mean_force":0.07171,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46883,-0.01926,0.096]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18019.0,"contact_point_centroid":[0.46847,-0.0379,0.09721],"force_p95":0.09536,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27508,"mean_force":0.05518,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46886,-0.01926,0.09736]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2409.0,"contact_point_centroid":[0.47879,0.00663,0.20105],"force_p95":0.15988,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24307,"mean_force":0.10814,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47554,-0.01175,0.20439]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2748.0,"contact_point_centroid":[0.47892,-0.02918,0.20223],"force_p95":0.14396,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21297,"mean_force":0.09519,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47618,-0.01106,0.20574]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02008,-0.00208],"force_p95":0.14475,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1865,"mean_force":0.12867,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47222,-0.01932,0.05036]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4104.0,"contact_point_centroid":[0.47202,-8e-05,0.04977],"force_p95":0.07823,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14,"mean_force":0.05215,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47111,-0.01929,0.04921]},{"body_a":"world","body_b":"grasp_target","contact_count":2148.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13215,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48644,-0.00891,0.22009]},{"body_a":"world","body_b":"grasp_target","contact_count":2056.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.47506,-0.01888,0.09559]},{"body_a":"world","body_b":"grasp_target","contact_count":580.0,"contact_point_centroid":[0.53865,0.02334,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62092,0.14969,0.25063]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53865,0.02334,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62118,0.15363,0.20672]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.53865,0.02334,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61744,0.15244,0.26629]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4924.0,"contact_point_centroid":[0.4712,-0.03837,0.04995],"force_p95":0.06968,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07179,"mean_force":0.0443,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47111,-0.01929,0.04921]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1179.0,"contact_point_centroid":[0.57295,0.09514,0.30848],"force_p95":0.01213,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01614,"mean_force":0.01062,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57271,0.09514,0.30616]},{"body_a":"left_finger","body_b":"right_finger","contact_count":625.0,"contact_point_centroid":[0.62143,0.14969,0.25294],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01098,"mean_force":0.01035,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62091,0.14968,0.25072]}],"total_contact_groups":17},"final_pose_error":0.01519,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.53865,0.02334,0.01602],"final_tcp_position":[0.61781,0.15248,0.31116],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":9748.77018,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":538.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2148.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.4744,-0.01834,0.13941],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11342,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":514.0,"n_steps_budget":600.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2056.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47862,-0.01946,0.05705],"tcp_start":[0.4744,-0.01834,0.13941],"tcp_to_object_dist_end":0.03114,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47608,-0.01949,0.0257],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.2882,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.1427,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10828.0,"raw_peak_contact_force":0.1865,"tcp_end":[0.47108,-0.01929,0.04918],"tcp_start":[0.47862,-0.01946,0.05705],"tcp_to_object_dist_end":0.02401,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47413,-0.02001,0.12224],"object_pos_start":[0.47608,-0.01949,0.0257],"object_to_goal_dist_end":0.24788,"object_to_goal_dist_start":0.2882,"object_z_max":0.12212,"peak_contact_force":0.09737,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":31970.0,"raw_peak_contact_force":0.37859,"tcp_end":[0.47083,-0.01933,0.15282],"tcp_start":[0.47108,-0.01929,0.04918],"tcp_to_object_dist_end":0.03077,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":698.0,"n_steps_budget":1000.0,"object_pos_end":[0.53865,0.02334,0.01602],"object_pos_start":[0.47413,-0.02001,0.12224],"object_to_goal_dist_end":0.23946,"object_to_goal_dist_start":0.24788,"object_z_max":0.22692,"peak_contact_force":9748.77018,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7573.0,"raw_peak_contact_force":1.90089,"subtask_id":"place_goal","tcp_end":[0.61756,0.14499,0.29133],"tcp_start":[0.47083,-0.01933,0.15282],"tcp_to_object_dist_end":0.31116,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":145.0,"n_steps_budget":1000.0,"object_pos_end":[0.53865,0.02334,0.01602],"object_pos_start":[0.53865,0.02334,0.01602],"object_to_goal_dist_end":0.23946,"object_to_goal_dist_start":0.23946,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1205.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.62534,0.15474,0.20797],"tcp_start":[0.61756,0.14499,0.29133],"tcp_to_object_dist_end":0.24825,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53865,0.02334,0.01602],"object_pos_start":[0.53865,0.02334,0.01602],"object_to_goal_dist_end":0.23946,"object_to_goal_dist_start":0.23946,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61984,0.15319,0.2262],"tcp_start":[0.62534,0.15474,0.20797],"tcp_to_object_dist_end":0.26006,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.53865,0.02334,0.01602],"object_pos_start":[0.53865,0.02334,0.01602],"object_to_goal_dist_end":0.23946,"object_to_goal_dist_start":0.23946,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61781,0.15248,0.31116],"tcp_start":[0.61984,0.15319,0.2262],"tcp_to_object_dist_end":0.33175,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41245,"average_solve_count":257.0,"average_success_count":257.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_grasp.lateral_offset_x":0.00352,"align_grasp.lateral_offset_y":-0.00067,"approach_goal.arc_height":0.06607,"approach_goal.transport_speed":0.10047,"approach_object.approach_speed":0.04615,"descend_place.descend_speed":0.55518,"lift.lift_height":0.18193,"lift.lift_speed":0.04007,"release.release_duration":1.02346},"optimized_scores":{"best_composite_score":0.0572,"best_fitness_score":0.6872,"best_task_score":0.45468},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":410.0,"contact_point_centroid":[0.61412,0.14413,-0.00505],"force_p95":1.23915,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.828,"mean_force":0.25848,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.60503,0.17774,0.22509]},{"body_a":"world","body_b":"grasp_target","contact_count":169.0,"contact_point_centroid":[0.45416,-0.02541,-0.00123],"force_p95":0.2627,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.354,"mean_force":0.06701,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44886,-0.02624,0.05232]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12113.0,"contact_point_centroid":[0.44975,-0.00729,0.09391],"force_p95":0.10846,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30335,"mean_force":0.07901,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44901,-0.0261,0.09605]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14188.0,"contact_point_centroid":[0.4488,-0.04465,0.09315],"force_p95":0.10051,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25483,"mean_force":0.06828,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44895,-0.0261,0.09507]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6305.0,"contact_point_centroid":[0.50384,0.05997,0.20574],"force_p95":0.14364,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20606,"mean_force":0.10125,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50065,0.04155,0.20967]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7261.0,"contact_point_centroid":[0.50193,0.0213,0.20461],"force_p95":0.12812,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20078,"mean_force":0.08882,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49909,0.03953,0.20852]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02632,-0.00203],"force_p95":0.13614,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14255,"mean_force":0.12575,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45129,-0.02635,0.05171]},{"body_a":"world","body_b":"grasp_target","contact_count":2128.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47879,-0.01165,0.22016]},{"body_a":"world","body_b":"grasp_target","contact_count":584.0,"contact_point_centroid":[0.61442,0.14414,-0.00199],"force_p95":0.12646,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13077,"mean_force":0.12312,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61936,0.19795,0.17479]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.61441,0.14413,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61783,0.2013,0.13044]},{"body_a":"world","body_b":"grasp_target","contact_count":1896.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.45654,-0.02524,0.0966]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.61441,0.14413,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61284,0.19943,0.1897]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4245.0,"contact_point_centroid":[0.45085,-0.00711,0.05095],"force_p95":0.08622,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09953,"mean_force":0.05376,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45023,-0.02631,0.05066]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4864.0,"contact_point_centroid":[0.45027,-0.04525,0.05095],"force_p95":0.06699,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08614,"mean_force":0.04372,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45023,-0.02631,0.05066]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.61127,0.18544,0.22309],"force_p95":0.0154,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01628,"mean_force":0.01171,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.61089,0.18543,0.22079]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.62129,0.20242,0.12876],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01099,"mean_force":0.00995,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.6207,0.2024,0.12669]}],"total_contact_groups":17},"final_pose_error":0.01586,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.61441,0.14413,0.01602],"final_tcp_position":[0.61309,0.19947,0.23431],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":9748.78452,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":533.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2128.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.4585,-0.02396,0.13966],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11367,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":474.0,"n_steps_budget":600.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1896.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.45748,-0.02659,0.05786],"tcp_start":[0.4585,-0.02396,0.13966],"tcp_to_object_dist_end":0.03186,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45851,-0.02615,0.02573],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30363,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14266,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10909.0,"raw_peak_contact_force":0.14255,"tcp_end":[0.4502,-0.02631,0.05063],"tcp_start":[0.45748,-0.02659,0.05786],"tcp_to_object_dist_end":0.02625,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45245,-0.02609,0.11552],"object_pos_start":[0.45851,-0.02615,0.02573],"object_to_goal_dist_end":0.29406,"object_to_goal_dist_start":0.30363,"object_z_max":0.11543,"peak_contact_force":0.10344,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26470.0,"raw_peak_contact_force":0.354,"tcp_end":[0.45178,-0.02604,0.14798],"tcp_start":[0.4502,-0.02631,0.05063],"tcp_to_object_dist_end":0.03247,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":891.0,"n_steps_budget":1000.0,"object_pos_end":[0.61439,0.14389,0.01629],"object_pos_start":[0.45245,-0.02609,0.11552],"object_to_goal_dist_end":0.11814,"object_to_goal_dist_start":0.29406,"object_z_max":0.20528,"peak_contact_force":0.13106,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14196.0,"raw_peak_contact_force":1.828,"subtask_id":"place_goal","tcp_end":[0.61687,0.19332,0.21548],"tcp_start":[0.45178,-0.02604,0.14798],"tcp_to_object_dist_end":0.20525,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":146.0,"n_steps_budget":1000.0,"object_pos_end":[0.61441,0.14413,0.01602],"object_pos_start":[0.61439,0.14389,0.01629],"object_to_goal_dist_end":0.11822,"object_to_goal_dist_start":0.11814,"object_z_max":0.01629,"peak_contact_force":9748.78452,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1212.0,"raw_peak_contact_force":0.13077,"subtask_id":"place_goal","tcp_end":[0.62317,0.20306,0.13208],"tcp_start":[0.61687,0.19332,0.21548],"tcp_to_object_dist_end":0.13046,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61441,0.14413,0.01602],"object_pos_start":[0.61441,0.14413,0.01602],"object_to_goal_dist_end":0.11822,"object_to_goal_dist_start":0.11822,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12264,"tcp_end":[0.61606,0.20061,0.14984],"tcp_start":[0.62317,0.20306,0.13208],"tcp_to_object_dist_end":0.14527,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.61441,0.14413,0.01602],"object_pos_start":[0.61441,0.14413,0.01602],"object_to_goal_dist_end":0.11822,"object_to_goal_dist_start":0.11822,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61309,0.19947,0.23431],"tcp_start":[0.61606,0.20061,0.14984],"tcp_to_object_dist_end":0.2252,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```