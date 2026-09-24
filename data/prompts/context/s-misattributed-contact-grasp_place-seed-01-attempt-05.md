## Search State

- **Seed**: 1
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.2507 | 0.20 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.3380 | 0.43 | ✅ accepted |
| 3 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |
| 2 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |
| 1 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |

**Proposal policy**: task_score is 0.20 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.251) — your mutation base

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
    offset_along_axis:
      distance: 0.03
      axis: world_z
      mode: add_to_offset
      sign: negative
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    grasp_descend_dist:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset_along_axis.distance
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
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
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
    - 0.25
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
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.03, mode=add_to_offset, sign=negative}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_descend_dist: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_hold, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_xy_offset_x: status=consumed; consumers=target.offset.x (replace)
    - place_xy_offset_y: status=consumed; consumers=target.offset.y (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.25], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.251
- **task_score** (E): 0.199
- **fitness_score**: 0.581  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1084 |
| descend_to_grasp | 1.00 | 1.00 | 0.1647 |
| grasp | 1.00 | 1.00 | 0.0119 |
| lift | 1.00 | 1.00 | 0.1304 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.480, -0.000, 0.198) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.480, -0.000, 0.198)→(0.475, -0.001, 0.034) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 43.333 | 0.153 | 0.236 |
| grasp | grasp | 1.00 / step_budget | (0.475, -0.001, 0.034)→(0.467, -0.001, 0.025) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 23.667 | 0.108 | 0.717 |
| lift | lift | 1.00 / step_budget | (0.467, -0.001, 0.025)→(0.463, -0.001, 0.156) | (0.479, -0.001, 0.026)→(0.483, -0.001, 0.151) | 0.278→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.245
- phase_score: 0.016
- phase_breakdown.reach_goal_score: 0.000
- phase_breakdown.reach_object_score: 0.055
- grasp_place_fitness: 0.602

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.602
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.245
- **Median Q (composite search score)**: 0.254
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.174


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90722,"average_solve_count":97.0,"average_success_count":97.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_place.place_xy_offset_x":0.00919,"descend_place.place_xy_offset_y":0.00783,"descend_to_grasp.grasp_descend_dist":0.04021},"optimized_scores":{"best_composite_score":0.27221,"best_fitness_score":0.60221,"best_task_score":0.24523},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":81.0,"contact_point_centroid":[0.49796,0.04144,-0.00152],"force_p95":0.6764,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70031,"mean_force":0.15582,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48703,0.04262,0.02722]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6098.0,"contact_point_centroid":[0.48719,0.02343,0.08574],"force_p95":0.11104,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36895,"mean_force":0.07006,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48466,0.0424,0.08327]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6763.0,"contact_point_centroid":[0.48697,0.06128,0.08292],"force_p95":0.10722,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33309,"mean_force":0.0653,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48468,0.0424,0.08107]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50128,0.04457,-0.00222],"force_p95":0.18737,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27385,"mean_force":0.13951,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48951,0.04286,0.02681]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3592.0,"contact_point_centroid":[0.48976,0.0235,0.02883],"force_p95":0.09207,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16548,"mean_force":0.05789,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48836,0.04275,0.02562]},{"body_a":"world","body_b":"grasp_target","contact_count":836.0,"contact_point_centroid":[0.50118,0.04505,-0.00185],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12321,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49872,0.0172,0.25009]},{"body_a":"world","body_b":"grasp_target","contact_count":1236.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49665,0.03974,0.1165]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5428.0,"contact_point_centroid":[0.48831,0.06191,0.02829],"force_p95":0.07524,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08461,"mean_force":0.04207,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48837,0.04275,0.02563]}],"total_contact_groups":8},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.5046,0.04271,0.14939],"final_tcp_position":[0.48472,0.04241,0.15593],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.70031,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":210.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1236.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49827,0.03619,0.19753],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17176,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":309.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.17244,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10820.0,"raw_peak_contact_force":0.27385,"subtask_id":"reach_object","tcp_end":[0.4969,0.04349,0.03484],"tcp_start":[0.49827,0.03619,0.19753],"tcp_to_object_dist_end":0.00993,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5011,0.04268,0.02529],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24422,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.10678,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12942.0,"raw_peak_contact_force":0.70031,"tcp_end":[0.48833,0.04275,0.02559],"tcp_start":[0.4969,0.04349,0.03484],"tcp_to_object_dist_end":0.01277,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":410.0,"n_steps_budget":960.0,"object_pos_end":[0.5046,0.04271,0.14939],"object_pos_start":[0.5011,0.04268,0.02529],"object_to_goal_dist_end":0.21084,"object_to_goal_dist_start":0.24422,"object_z_max":0.14912,"peak_contact_force":0.12262,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":836.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.48472,0.04241,0.15593],"tcp_start":[0.48833,0.04275,0.02559],"tcp_to_object_dist_end":0.02093,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90722,"average_solve_count":97.0,"average_success_count":97.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_place.place_xy_offset_x":0.00154,"descend_place.place_xy_offset_y":0.0091,"descend_to_grasp.grasp_descend_dist":0.04188},"optimized_scores":{"best_composite_score":0.25445,"best_fitness_score":0.58445,"best_task_score":0.20608},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.47318,-0.01913,-0.00136],"force_p95":0.68455,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71744,"mean_force":0.17371,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46326,-0.01932,0.02671]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6454.0,"contact_point_centroid":[0.46263,-0.0002,0.08508],"force_p95":0.1061,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30381,"mean_force":0.06446,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46095,-0.01925,0.08269]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7006.0,"contact_point_centroid":[0.46267,-0.03821,0.08372],"force_p95":0.10285,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29304,"mean_force":0.0605,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46094,-0.01925,0.08203]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.01996,-0.00207],"force_p95":0.1434,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20928,"mean_force":0.12839,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46558,-0.01937,0.0264]},{"body_a":"world","body_b":"grasp_target","contact_count":776.0,"contact_point_centroid":[0.47616,-0.02015,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12326,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48942,-0.00754,0.25146]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4807.0,"contact_point_centroid":[0.46448,-0.00014,0.02763],"force_p95":0.0683,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12502,"mean_force":0.04488,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46448,-0.01935,0.02533]},{"body_a":"world","body_b":"grasp_target","contact_count":1272.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47475,-0.01769,0.1169]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5186.0,"contact_point_centroid":[0.46432,-0.03859,0.02714],"force_p95":0.06711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08256,"mean_force":0.04301,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46448,-0.01935,0.02533]}],"total_contact_groups":8},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.48053,-0.01925,0.151],"final_tcp_position":[0.46095,-0.01923,0.15562],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.71744,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":195.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1272.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47852,-0.01598,0.19941],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17346,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":318.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14012,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11793.0,"raw_peak_contact_force":0.20928,"subtask_id":"reach_object","tcp_end":[0.47274,-0.01951,0.03369],"tcp_start":[0.47852,-0.01598,0.19941],"tcp_to_object_dist_end":0.00842,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01937,0.02575],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28813,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.11048,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13534.0,"raw_peak_contact_force":0.71744,"tcp_end":[0.46445,-0.01935,0.0253],"tcp_start":[0.47274,-0.01951,0.03369],"tcp_to_object_dist_end":0.01159,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":398.0,"n_steps_budget":960.0,"object_pos_end":[0.48053,-0.01925,0.151],"object_pos_start":[0.47603,-0.01937,0.02575],"object_to_goal_dist_end":0.23692,"object_to_goal_dist_start":0.28813,"object_z_max":0.15073,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":776.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.46095,-0.01923,0.15562],"tcp_start":[0.46445,-0.01935,0.0253],"tcp_to_object_dist_end":0.02012,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90816,"average_solve_count":98.0,"average_success_count":98.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_place.place_xy_offset_x":0.00536,"descend_place.place_xy_offset_y":-0.0057,"descend_to_grasp.grasp_descend_dist":0.04284},"optimized_scores":{"best_composite_score":0.22531,"best_fitness_score":0.55531,"best_task_score":0.14543},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":72.0,"contact_point_centroid":[0.45551,-0.02466,-0.0014],"force_p95":0.69648,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73411,"mean_force":0.17962,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44646,-0.02522,0.02645]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7074.0,"contact_point_centroid":[0.44567,-0.04412,0.0847],"force_p95":0.10029,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30559,"mean_force":0.0586,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44425,-0.02512,0.083]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6574.0,"contact_point_centroid":[0.44562,-0.00605,0.08555],"force_p95":0.10453,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30381,"mean_force":0.06207,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44427,-0.02512,0.08323]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.0261,-0.00209],"force_p95":0.15014,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22497,"mean_force":0.13023,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44872,-0.0253,0.02604]},{"body_a":"world","body_b":"grasp_target","contact_count":824.0,"contact_point_centroid":[0.45856,-0.02632,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12322,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48245,-0.01007,0.25052]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4826.0,"contact_point_centroid":[0.44775,-0.00608,0.02691],"force_p95":0.07087,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13311,"mean_force":0.04443,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44765,-0.02526,0.02505]},{"body_a":"world","body_b":"grasp_target","contact_count":1280.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45899,-0.02331,0.11583]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4964.0,"contact_point_centroid":[0.44786,-0.04451,0.02693],"force_p95":0.07134,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09036,"mean_force":0.04486,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44766,-0.02526,0.02506]}],"total_contact_groups":8},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.46344,-0.02513,0.15162],"final_tcp_position":[0.44426,-0.02509,0.15554],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.73411,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":207.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1280.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.46401,-0.02124,0.19803],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17218,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":320.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14624,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11590.0,"raw_peak_contact_force":0.22497,"subtask_id":"reach_object","tcp_end":[0.45568,-0.02552,0.03285],"tcp_start":[0.46401,-0.02124,0.19803],"tcp_to_object_dist_end":0.00746,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45843,-0.02533,0.02567],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30306,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.1076,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13720.0,"raw_peak_contact_force":0.73411,"tcp_end":[0.44763,-0.02525,0.02503],"tcp_start":[0.45568,-0.02552,0.03285],"tcp_to_object_dist_end":0.01083,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":389.0,"n_steps_budget":930.0,"object_pos_end":[0.46344,-0.02513,0.15162],"object_pos_start":[0.45843,-0.02533,0.02567],"object_to_goal_dist_end":0.28921,"object_to_goal_dist_start":0.30306,"object_z_max":0.15134,"peak_contact_force":0.12262,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":824.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.44426,-0.02509,0.15554],"tcp_start":[0.44763,-0.02525,0.02503],"tcp_to_object_dist_end":0.01958,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```