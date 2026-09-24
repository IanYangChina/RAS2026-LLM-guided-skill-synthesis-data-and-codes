## Search State

- **Seed**: 1
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8  | -0.3662 | 0.14 | ❌ rejected |
| 1 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7  | -0.0465 | 0.16 | ✅ accepted |
| 0 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3  | -0.0552 | 0.29 | ✅ accepted |

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

## Current Skill (Q=-0.055) — your mutation base

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
      default: 0.12
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.1
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
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    placement_offset_z:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: add
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
  - target: source=yaml, anchor=task_goal, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - placement_offset_z: status=consumed; consumers=target.offset.z (add)
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

- **Composite score**: -0.055
- **task_score** (E): 0.292
- **fitness_score**: 0.525  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1668 |
| align_grasp | 1.00 | 1.00 | 0.0821 |
| grasp | 1.00 | 1.00 | 0.0110 |
| lift | 1.00 | 1.00 | 0.0850 |
| approach_goal | 0.00 | 1.00 | 0.1129 |
| descend_place | 0.33 | 1.00 | 0.0832 |
| release | 1.00 | 1.00 | 0.0229 |
| retract | 1.00 | 1.00 | 0.0863 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.477, -0.000, 0.139) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| align_grasp | align | 1.00 / step_budget | (0.477, -0.000, 0.139)→(0.479, -0.000, 0.057) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.479, -0.000, 0.057)→(0.472, -0.001, 0.049) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 41.000 | 0.133 | 0.144 |
| lift | lift | 1.00 / step_budget | (0.472, -0.001, 0.049)→(0.474, -0.001, 0.134) | (0.479, -0.001, 0.026)→(0.477, -0.000, 0.105) | 0.278→0.257 | 1.00 / 27.000 | 0.115 | 0.367 |
| approach_goal | approach | 0.00 / step_budget | (0.474, -0.001, 0.134)→(0.526, 0.087, 0.174) | (0.477, -0.000, 0.105)→(0.523, 0.083, 0.095) | 0.257→0.163 | 1.00 / 15.333 | 3249.615 | 0.568 |
| descend_place | descend | 0.33 / step_budget | (0.526, 0.087, 0.174)→(0.565, 0.151, 0.151) | (0.523, 0.083, 0.095)→(0.530, 0.112, 0.016) | 0.163→0.188 | 1.00 / 8.333 | 182004.250 | 0.834 |
| release | release | 1.00 / step_budget | (0.565, 0.151, 0.151)→(0.559, 0.149, 0.173) | (0.530, 0.112, 0.016)→(0.530, 0.112, 0.016) | 0.188→0.188 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.559, 0.149, 0.173)→(0.557, 0.148, 0.259) | (0.530, 0.112, 0.016)→(0.530, 0.112, 0.016) | 0.188→0.188 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.374
- phase_score: 0.512
- phase_breakdown.place_goal_score: 0.465
- phase_breakdown.reach_object_score: 0.624
- grasp_place_fitness: 0.650

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.650
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.374
- **Median Q (composite search score)**: 0.009
- **K-run variance**: 0.0186
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.259


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67816,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_grasp.lateral_offset_x":0.00336,"align_grasp.lateral_offset_y":0.00166,"approach_goal.transport_speed":0.10239,"approach_object.approach_speed":0.0731,"descend_place.placement_offset_z":-0.0104,"lift.lift_height":0.15089,"lift.lift_speed":0.05681,"release.release_duration":1.50641},"optimized_scores":{"best_composite_score":0.07017,"best_fitness_score":0.65017,"best_task_score":0.37419},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2927.0,"contact_point_centroid":[0.53748,0.18225,-0.0023],"force_p95":0.12543,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.31906,"mean_force":0.13556,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.53813,0.18465,0.15647]},{"body_a":"world","body_b":"grasp_target","contact_count":192.0,"contact_point_centroid":[0.49774,0.0448,-0.00115],"force_p95":0.22193,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39232,"mean_force":0.06176,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49006,0.04497,0.04954]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19478.0,"contact_point_centroid":[0.49098,0.06351,0.0934],"force_p95":0.0774,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28284,"mean_force":0.05141,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49112,0.04468,0.09295]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16022.0,"contact_point_centroid":[0.48995,0.02557,0.09222],"force_p95":0.10494,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27808,"mean_force":0.06282,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49104,0.04468,0.09181]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1711.0,"contact_point_centroid":[0.5295,0.12851,0.17101],"force_p95":0.14696,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24642,"mean_force":0.10403,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52466,0.14683,0.17629]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1863.0,"contact_point_centroid":[0.52939,0.16538,0.17081],"force_p95":0.11717,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21925,"mean_force":0.09421,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5248,0.14734,0.17594]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12089.0,"contact_point_centroid":[0.50748,0.10721,0.15647],"force_p95":0.12403,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18112,"mean_force":0.07712,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50667,0.08875,0.15887]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10499.0,"contact_point_centroid":[0.50963,0.07323,0.1572],"force_p95":0.12187,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1732,"mean_force":0.08743,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50772,0.09176,0.16041]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50118,0.04499,-0.00202],"force_p95":0.12903,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14377,"mean_force":0.12471,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49273,0.04526,0.04918]},{"body_a":"world","body_b":"grasp_target","contact_count":2116.0,"contact_point_centroid":[0.50118,0.04505,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49754,0.02013,0.21882]},{"body_a":"world","body_b":"grasp_target","contact_count":2000.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.49683,0.04347,0.09406]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5375,0.18226,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.54362,0.20881,0.14609]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.5375,0.18226,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.539,0.20693,0.20768]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4137.0,"contact_point_centroid":[0.49088,0.02594,0.04935],"force_p95":0.07583,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09231,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49159,0.04515,0.04792]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4852.0,"contact_point_centroid":[0.4917,0.06422,0.04897],"force_p95":0.0677,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09092,"mean_force":0.04466,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49159,0.04515,0.04792]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2775.0,"contact_point_centroid":[0.53957,0.18728,0.15742],"force_p95":0.01124,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01642,"mean_force":0.01066,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.53911,0.18725,0.15523]}],"total_contact_groups":17},"final_pose_error":0.01393,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.5375,0.18226,0.01602],"final_tcp_position":[0.5392,0.20697,0.25264],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.31906,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":530.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2116.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.4972,0.04112,0.13816],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11228,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":500.0,"n_steps_budget":600.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49934,0.04588,0.05649],"tcp_start":[0.4972,0.04112,0.13816],"tcp_to_object_dist_end":0.03054,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50109,0.04493,0.02589],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24206,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12912,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10789.0,"raw_peak_contact_force":0.14377,"tcp_end":[0.49156,0.04515,0.04789],"tcp_start":[0.49934,0.04588,0.05649],"tcp_to_object_dist_end":0.02397,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49642,0.04526,0.11157],"object_pos_start":[0.50109,0.04493,0.02589],"object_to_goal_dist_end":0.21379,"object_to_goal_dist_start":0.24206,"object_z_max":0.11148,"peak_contact_force":0.11201,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":35692.0,"raw_peak_contact_force":0.39232,"tcp_end":[0.49477,0.04462,0.14059],"tcp_start":[0.49156,0.04515,0.04789],"tcp_to_object_dist_end":0.02907,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52948,0.13956,0.14782],"object_pos_start":[0.49642,0.04526,0.11157],"object_to_goal_dist_end":0.11095,"object_to_goal_dist_start":0.21379,"object_z_max":0.14777,"peak_contact_force":0.11725,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22588.0,"raw_peak_contact_force":0.18112,"subtask_id":"place_goal","tcp_end":[0.52426,0.13928,0.18483],"tcp_start":[0.49477,0.04462,0.14059],"tcp_to_object_dist_end":0.03737,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5375,0.18226,0.01602],"object_pos_start":[0.52948,0.13956,0.14782],"object_to_goal_dist_end":0.14745,"object_to_goal_dist_start":0.11095,"object_z_max":0.14782,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9276.0,"raw_peak_contact_force":1.31906,"subtask_id":"place_goal","tcp_end":[0.54786,0.21039,0.14417],"tcp_start":[0.52426,0.13928,0.18483],"tcp_to_object_dist_end":0.13161,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5375,0.18226,0.01602],"object_pos_start":[0.5375,0.18226,0.01602],"object_to_goal_dist_end":0.14745,"object_to_goal_dist_start":0.14745,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54198,0.20812,0.16625],"tcp_start":[0.54786,0.21039,0.14417],"tcp_to_object_dist_end":0.1525,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.5375,0.18226,0.01602],"object_pos_start":[0.5375,0.18226,0.01602],"object_to_goal_dist_end":0.14745,"object_to_goal_dist_start":0.14745,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5392,0.20697,0.25264],"tcp_start":[0.54198,0.20812,0.16625],"tcp_to_object_dist_end":0.23792,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42353,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_grasp.lateral_offset_x":0.00881,"align_grasp.lateral_offset_y":-0.00067,"approach_goal.transport_speed":0.08261,"approach_object.approach_speed":0.05866,"descend_place.placement_offset_z":-0.0018,"lift.lift_height":0.08019,"lift.lift_speed":0.05843,"release.release_duration":1.29161},"optimized_scores":{"best_composite_score":-0.24468,"best_fitness_score":0.33532,"best_task_score":0.24338},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2597.0,"contact_point_centroid":[0.53817,0.08194,-0.00232],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.06136,"mean_force":0.13593,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55452,0.07961,0.15937]},{"body_a":"world","body_b":"grasp_target","contact_count":181.0,"contact_point_centroid":[0.47275,-0.02065,-0.00118],"force_p95":0.23647,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36762,"mean_force":0.0521,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47075,-0.02031,0.05086]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2352.0,"contact_point_centroid":[0.52748,0.02992,0.1474],"force_p95":0.15045,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32063,"mean_force":0.10744,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52586,0.04801,0.15223]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8693.0,"contact_point_centroid":[0.46962,-0.03943,0.07365],"force_p95":0.09662,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28082,"mean_force":0.05921,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47015,-0.02028,0.07318]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10046.0,"contact_point_centroid":[0.47021,-0.00141,0.07343],"force_p95":0.07302,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26852,"mean_force":0.05021,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47014,-0.02028,0.07292]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11319.0,"contact_point_centroid":[0.49504,-0.0075,0.1232],"force_p95":0.10856,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17953,"mean_force":0.08159,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49571,0.01116,0.12572]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2692.0,"contact_point_centroid":[0.52843,0.06566,0.14765],"force_p95":0.12625,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16929,"mean_force":0.09152,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52578,0.04788,0.15226]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13288.0,"contact_point_centroid":[0.49385,0.02749,0.12126],"force_p95":0.10258,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16902,"mean_force":0.07176,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49375,0.00892,0.1234]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47615,-0.02021,-0.00203],"force_p95":0.13141,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14584,"mean_force":0.12522,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47331,-0.02037,0.05031]},{"body_a":"world","body_b":"grasp_target","contact_count":2084.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48652,-0.00891,0.22016]},{"body_a":"world","body_b":"grasp_target","contact_count":2072.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.47563,-0.01941,0.09578]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53816,0.082,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.56818,0.09814,0.16633]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.53816,0.082,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.56358,0.09725,0.22795]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4119.0,"contact_point_centroid":[0.47145,-0.03956,0.05003],"force_p95":0.07581,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11299,"mean_force":0.052,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4722,-0.02035,0.04916]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4876.0,"contact_point_centroid":[0.47227,-0.00128,0.04994],"force_p95":0.06772,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08344,"mean_force":0.0445,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4722,-0.02035,0.04916]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2414.0,"contact_point_centroid":[0.55699,0.08192,0.16218],"force_p95":0.01143,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01653,"mean_force":0.01067,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55666,0.08192,0.15996]}],"total_contact_groups":17},"final_pose_error":0.01386,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.53816,0.082,0.01602],"final_tcp_position":[0.56381,0.09727,0.27291],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273006.17139,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":522.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2084.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47446,-0.01832,0.13955],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11356,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":518.0,"n_steps_budget":600.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2072.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47974,-0.02053,0.05704],"tcp_start":[0.47446,-0.01832,0.13955],"tcp_to_object_dist_end":0.03123,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47607,-0.02043,0.02587],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28869,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13071,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10795.0,"raw_peak_contact_force":0.14584,"tcp_end":[0.47218,-0.02035,0.04913],"tcp_start":[0.47974,-0.02053,0.05704],"tcp_to_object_dist_end":0.02358,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":504.0,"n_steps_budget":630.0,"object_pos_end":[0.47391,-0.02,0.07081],"object_pos_start":[0.47607,-0.02043,0.02587],"object_to_goal_dist_end":0.2667,"object_to_goal_dist_start":0.28869,"object_z_max":0.07075,"peak_contact_force":0.10943,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18920.0,"raw_peak_contact_force":0.36762,"tcp_end":[0.47156,-0.02031,0.09687],"tcp_start":[0.47218,-0.02035,0.04913],"tcp_to_object_dist_end":0.02616,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52428,0.03882,0.12061],"object_pos_start":[0.47391,-0.02,0.07081],"object_to_goal_dist_end":0.17545,"object_to_goal_dist_start":0.2667,"object_z_max":0.12056,"peak_contact_force":0.12615,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24607.0,"raw_peak_contact_force":0.17953,"subtask_id":"place_goal","tcp_end":[0.52019,0.03857,0.15455],"tcp_start":[0.47156,-0.02031,0.09687],"tcp_to_object_dist_end":0.03419,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53816,0.082,0.01602],"object_pos_start":[0.52428,0.03882,0.12061],"object_to_goal_dist_end":0.21197,"object_to_goal_dist_start":0.17545,"object_z_max":0.12061,"peak_contact_force":273006.17139,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10055.0,"raw_peak_contact_force":1.06136,"subtask_id":"place_goal","tcp_end":[0.57238,0.09885,0.1643],"tcp_start":[0.52019,0.03857,0.15455],"tcp_to_object_dist_end":0.15311,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53816,0.082,0.01602],"object_pos_start":[0.53816,0.082,0.01602],"object_to_goal_dist_end":0.21197,"object_to_goal_dist_start":0.21197,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56654,0.09781,0.18649],"tcp_start":[0.57238,0.09885,0.1643],"tcp_to_object_dist_end":0.17354,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.53816,0.082,0.01602],"object_pos_start":[0.53816,0.082,0.01602],"object_to_goal_dist_end":0.21197,"object_to_goal_dist_start":0.21197,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56381,0.09727,0.27291],"tcp_start":[0.56654,0.09781,0.18649],"tcp_to_object_dist_end":0.25862,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88095,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_grasp.lateral_offset_x":0.00424,"align_grasp.lateral_offset_y":-0.00081,"approach_goal.transport_speed":0.13067,"approach_object.approach_speed":0.07194,"descend_place.placement_offset_z":0.0062,"lift.lift_height":0.1491,"lift.lift_speed":0.07663,"release.release_duration":1.10325},"optimized_scores":{"best_composite_score":0.00903,"best_fitness_score":0.58903,"best_task_score":0.25735},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1489.0,"contact_point_centroid":[0.51502,0.07181,-0.0026],"force_p95":0.31086,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.34373,"mean_force":0.14858,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5192,0.06462,0.1782]},{"body_a":"world","body_b":"grasp_target","contact_count":147.0,"contact_point_centroid":[0.45628,-0.02721,-0.00123],"force_p95":0.22553,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34162,"mean_force":0.04529,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44952,-0.02639,0.05209]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11046.0,"contact_point_centroid":[0.45129,-0.04514,0.09793],"force_p95":0.12349,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32983,"mean_force":0.08128,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45029,-0.02634,0.09975]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14484.0,"contact_point_centroid":[0.45069,-0.00784,0.09866],"force_p95":0.11691,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27416,"mean_force":0.06364,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45023,-0.02634,0.09933]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4688.0,"contact_point_centroid":[0.48131,-0.01058,0.16363],"force_p95":0.12982,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25584,"mean_force":0.10483,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47668,0.00762,0.16755]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4948.0,"contact_point_centroid":[0.48208,0.02658,0.16358],"force_p95":0.12369,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19342,"mean_force":0.099,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47729,0.00846,0.16769]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02635,-0.00204],"force_p95":0.13662,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14314,"mean_force":0.12584,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45193,-0.02649,0.05158]},{"body_a":"world","body_b":"grasp_target","contact_count":2012.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47864,-0.01168,0.21994]},{"body_a":"world","body_b":"grasp_target","contact_count":1920.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.45676,-0.02532,0.09632]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51503,0.0719,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.553,0.11287,0.15958]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51503,0.0719,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57167,0.14183,0.14563]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.51503,0.0719,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.56684,0.14052,0.20685]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4146.0,"contact_point_centroid":[0.45037,-0.04561,0.05082],"force_p95":0.08594,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09755,"mean_force":0.05477,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45087,-0.02644,0.05052]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4842.0,"contact_point_centroid":[0.45093,-0.00748,0.0509],"force_p95":0.06763,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09219,"mean_force":0.04415,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45087,-0.02644,0.05052]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1280.0,"contact_point_centroid":[0.52208,0.06798,0.18114],"force_p95":0.01204,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01624,"mean_force":0.01071,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52172,0.06798,0.17884]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4242.0,"contact_point_centroid":[0.55346,0.11293,0.16183],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01288,"mean_force":0.0105,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55304,0.11292,0.15955]}],"total_contact_groups":17},"final_pose_error":0.01443,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.51503,0.0719,0.01602],"final_tcp_position":[0.56703,0.14054,0.25156],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273006.45649,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":504.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2012.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.4583,-0.02397,0.13943],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11344,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":480.0,"n_steps_budget":600.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1920.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.45813,-0.02673,0.05774],"tcp_start":[0.4583,-0.02397,0.13943],"tcp_to_object_dist_end":0.03173,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45851,-0.02658,0.02576],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30396,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13965,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10788.0,"raw_peak_contact_force":0.14314,"tcp_end":[0.45084,-0.02645,0.0505],"tcp_start":[0.45813,-0.02673,0.05774],"tcp_to_object_dist_end":0.0259,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":920.0,"n_steps_budget":1000.0,"object_pos_end":[0.46061,-0.02592,0.1315],"object_pos_start":[0.45851,-0.02658,0.02576],"object_to_goal_dist_end":0.28958,"object_to_goal_dist_start":0.30396,"object_z_max":0.13142,"peak_contact_force":0.12456,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25677.0,"raw_peak_contact_force":0.34162,"tcp_end":[0.4545,-0.02641,0.16508],"tcp_start":[0.45084,-0.02645,0.0505],"tcp_to_object_dist_end":0.03413,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51503,0.0719,0.01602],"object_pos_start":[0.46061,-0.02592,0.1315],"object_to_goal_dist_end":0.2036,"object_to_goal_dist_start":0.28958,"object_z_max":0.13406,"peak_contact_force":9748.60173,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12405.0,"raw_peak_contact_force":1.34373,"subtask_id":"place_goal","tcp_end":[0.53217,0.08192,0.18151],"tcp_start":[0.4545,-0.02641,0.16508],"tcp_to_object_dist_end":0.16668,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51503,0.0719,0.01602],"object_pos_start":[0.51503,0.0719,0.01602],"object_to_goal_dist_end":0.2036,"object_to_goal_dist_start":0.2036,"object_z_max":0.01602,"peak_contact_force":273006.45649,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8242.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.57611,0.14292,0.14392],"tcp_start":[0.53217,0.08192,0.18151],"tcp_to_object_dist_end":0.15853,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51503,0.0719,0.01602],"object_pos_start":[0.51503,0.0719,0.01602],"object_to_goal_dist_end":0.2036,"object_to_goal_dist_start":0.2036,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56994,0.14135,0.16567],"tcp_start":[0.57611,0.14292,0.14392],"tcp_to_object_dist_end":0.17388,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.51503,0.0719,0.01602],"object_pos_start":[0.51503,0.0719,0.01602],"object_to_goal_dist_end":0.2036,"object_to_goal_dist_start":0.2036,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56703,0.14054,0.25156],"tcp_start":[0.56994,0.14135,0.16567],"tcp_to_object_dist_end":0.25079,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```