## Search State

- **Seed**: 1
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → align → grasp → lift → lift → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0791 | 0.43 | ✅ accepted |
| 4 | approach → align → grasp → lift → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | pose_tolerance | 8 | -0.0507 | 0.35 | ✅ accepted |
| 3 | approach → align → grasp → lift → approach → align → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | 0.2022 | 0.20 | ✅ accepted |
| 2 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |
| 1 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |

**Proposal policy**: task_score is 0.43 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.079) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.08
  weight: 0.2
- id: grasp_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.02
  weight: 0.3
- id: lift_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.2
  weight: 0.2
- id: reach_goal
  weight: 0.3
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
    - 0.08
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_object
- id: descend_grasp
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: grasp_object
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
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.003
- id: lift_to_clear
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
    - 0.2
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: lift_object
- id: transport_to_goal
  type: lift
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
    place_offset_x:
      type: scalar
      range:
      - -0.03
      - 0.01
      default: -0.013
      binds_to:
      - path: target.offset.x
        mode: replace
    place_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: replace
    place_offset_z:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: -0.001
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
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
    release_time:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.3
      binds_to:
      - path: duration.max_time
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
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
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.08], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_grasp** (`align`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.003]
- **lift_to_clear** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.2], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **transport_to_goal** (`lift`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_offset_x: status=consumed; consumers=target.offset.x (replace)
    - place_offset_y: status=consumed; consumers=target.offset.y (replace)
    - place_offset_z: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_time: status=consumed; consumers=duration.max_time (replace)
  - retries: max_attempts=0, strategy=repeat
- **retract** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: 0.079
- **task_score** (E): 0.433
- **fitness_score**: 0.679  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.600

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1863 |
| descend_grasp | 1.00 | 1.00 | 0.0645 |
| grasp | 1.00 | 1.00 | 0.0110 |
| lift_to_clear | 0.00 | 1.00 | 0.0972 |
| transport_to_goal | 1.00 | 1.00 | 0.2397 |
| release | 1.00 | 1.00 | 0.0213 |
| retract | 1.00 | 1.00 | 0.1260 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.476, -0.000, 0.119) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | align | 1.00 / step_budget | (0.476, -0.000, 0.119)→(0.474, -0.001, 0.055) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.474, -0.001, 0.055)→(0.466, -0.001, 0.047) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 44.333 | 0.146 | 0.197 |
| lift_to_clear | lift | 0.00 / step_budget | (0.466, -0.001, 0.047)→(0.462, -0.001, 0.144) | (0.479, -0.001, 0.026)→(0.466, -0.001, 0.116) | 0.278→0.258 | 1.00 / 39.000 | 0.080 | 0.410 |
| transport_to_goal | lift | 1.00 / step_budget | (0.462, -0.001, 0.144)→(0.601, 0.188, 0.140) | (0.466, -0.001, 0.116)→(0.603, 0.188, 0.107) | 0.258→0.047 | 1.00 / 23.667 | 0.124 | 0.197 |
| release | release | 1.00 / step_budget | (0.601, 0.188, 0.140)→(0.594, 0.186, 0.160) | (0.603, 0.188, 0.107)→(0.586, 0.194, 0.027) | 0.047→0.127 | 1.00 / 3.333 | 0.193 | 1.148 |
| retract | retract | 1.00 / step_budget | (0.594, 0.186, 0.160)→(0.606, 0.202, 0.284) | (0.586, 0.194, 0.027)→(0.582, 0.199, 0.026) | 0.127→0.128 | 1.00 / 4.000 | 0.123 | 0.219 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.535
- phase_score: 0.658
- phase_breakdown.lift_object_score: 0.203
- phase_breakdown.reach_object_score: 0.823
- phase_breakdown.grasp_object_score: 0.877
- phase_breakdown.reach_goal_score: 0.632
- grasp_place_fitness: 0.729

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.729
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.535
- **Median Q (composite search score)**: 0.083
- **K-run variance**: 0.0018
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.376


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38265,"average_solve_count":196.0,"average_success_count":196.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.05111,"descend_grasp.descend_speed":0.17504,"lift_to_clear.lift_speed":0.05641,"release.release_time":0.68194,"retract.retract_speed":0.14166,"transport_to_goal.place_offset_x":0.0035,"transport_to_goal.place_offset_y":0.00999,"transport_to_goal.place_offset_z":-0.00395,"transport_to_goal.transport_speed":0.12164},"optimized_scores":{"best_composite_score":0.0829,"best_fitness_score":0.6829,"best_task_score":0.43988},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":284.0,"contact_point_centroid":[0.54141,0.23898,-0.00418],"force_p95":0.90777,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.19922,"mean_force":0.24249,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.55255,0.23702,0.1456]},{"body_a":"world","body_b":"grasp_target","contact_count":193.0,"contact_point_centroid":[0.49727,0.0421,-0.00127],"force_p95":0.2446,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47125,"mean_force":0.0806,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.48633,0.0431,0.04748]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":594.0,"contact_point_centroid":[0.55962,0.22053,0.12768],"force_p95":0.14991,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31449,"mean_force":0.08682,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.55655,0.23904,0.13149]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":957.0,"contact_point_centroid":[0.55705,0.25724,0.12966],"force_p95":0.13164,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30434,"mean_force":0.0661,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.55655,0.23905,0.13148]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19678.0,"contact_point_centroid":[0.48481,0.06199,0.09258],"force_p95":0.07764,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29544,"mean_force":0.0521,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.48402,0.0429,0.09108]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18747.0,"contact_point_centroid":[0.48423,0.02378,0.0938],"force_p95":0.07956,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26923,"mean_force":0.05385,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.484,0.0429,0.0928]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04492,-0.00215],"force_p95":0.16397,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.223,"mean_force":0.1335,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48927,0.04338,0.04692]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7693.0,"contact_point_centroid":[0.51797,0.11284,0.13387],"force_p95":0.13673,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20819,"mean_force":0.07667,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.51643,0.13182,0.13531]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10032.0,"contact_point_centroid":[0.51886,0.15498,0.13494],"force_p95":0.09985,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18487,"mean_force":0.05617,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.51826,0.13659,0.13524]},{"body_a":"world","body_b":"grasp_target","contact_count":2288.0,"contact_point_centroid":[0.54077,0.23904,-0.00198],"force_p95":0.1315,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1525,"mean_force":0.12249,"phase_index":6.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.55522,0.23933,0.21386]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4330.0,"contact_point_centroid":[0.48842,0.02404,0.0475],"force_p95":0.07795,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13946,"mean_force":0.0496,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48814,0.04327,0.0457]},{"body_a":"world","body_b":"grasp_target","contact_count":2496.0,"contact_point_centroid":[0.50118,0.04505,-0.00194],"force_p95":0.13053,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49751,0.02038,0.20872]},{"body_a":"world","body_b":"grasp_target","contact_count":832.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"align","tcp_position_centroid":[0.49549,0.04263,0.08617]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5271.0,"contact_point_centroid":[0.48881,0.06245,0.04779],"force_p95":0.07191,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07404,"mean_force":0.04219,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48814,0.04327,0.04571]}],"total_contact_groups":14},"final_pose_error":0.0175,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.54076,0.23904,0.02602],"final_tcp_position":[0.5614,0.24321,0.27962],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.19922,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":625.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2496.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49717,0.0415,0.11824],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09238,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":208.0,"n_steps_budget":600.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":832.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.49602,0.04398,0.05434],"tcp_start":[0.49717,0.0415,0.11824],"tcp_to_object_dist_end":0.02881,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50115,0.04379,0.02547],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24321,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16031,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11401.0,"raw_peak_contact_force":0.223,"tcp_end":[0.48811,0.04327,0.04567],"tcp_start":[0.49602,0.04398,0.05434],"tcp_to_object_dist_end":0.02405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48814,0.04324,0.11202],"object_pos_start":[0.50115,0.04379,0.02547],"object_to_goal_dist_end":0.21835,"object_to_goal_dist_start":0.24321,"object_z_max":0.11193,"peak_contact_force":0.08482,"phase_name":"lift_to_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38618.0,"raw_peak_contact_force":0.47125,"subtask_id":"lift_object","tcp_end":[0.48411,0.04292,0.1393],"tcp_start":[0.48811,0.04327,0.04567],"tcp_to_object_dist_end":0.02758,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":583.0,"n_steps_budget":1000.0,"object_pos_end":[0.56151,0.24031,0.1032],"object_pos_start":[0.48814,0.04324,0.11202],"object_to_goal_dist_end":0.04391,"object_to_goal_dist_start":0.21835,"object_z_max":0.11204,"peak_contact_force":0.13945,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17725.0,"raw_peak_contact_force":0.20819,"subtask_id":"reach_goal","tcp_end":[0.5586,0.2393,0.13489],"tcp_start":[0.48411,0.04292,0.1393],"tcp_to_object_dist_end":0.03185,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54226,0.23875,0.02649],"object_pos_start":[0.56151,0.24031,0.1032],"object_to_goal_dist_end":0.12246,"object_to_goal_dist_start":0.04391,"object_z_max":0.1032,"peak_contact_force":0.12867,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1835.0,"raw_peak_contact_force":1.19922,"tcp_end":[0.55246,0.23698,0.15622],"tcp_start":[0.5586,0.2393,0.13489],"tcp_to_object_dist_end":0.13014,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":572.0,"n_steps_budget":630.0,"object_pos_end":[0.54076,0.23904,0.02602],"object_pos_start":[0.54226,0.23875,0.02649],"object_to_goal_dist_end":0.12319,"object_to_goal_dist_start":0.12246,"object_z_max":0.02659,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2288.0,"raw_peak_contact_force":0.1525,"tcp_end":[0.5614,0.24321,0.27962],"tcp_start":[0.55246,0.23698,0.15622],"tcp_to_object_dist_end":0.25448,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26937,"average_solve_count":271.0,"average_success_count":271.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.10849,"descend_grasp.descend_speed":0.11025,"lift_to_clear.lift_speed":0.02041,"release.release_time":0.43402,"retract.retract_speed":0.10081,"transport_to_goal.place_offset_x":0.00436,"transport_to_goal.place_offset_y":-0.01301,"transport_to_goal.place_offset_z":-0.00294,"transport_to_goal.transport_speed":0.03671},"optimized_scores":{"best_composite_score":0.02529,"best_fitness_score":0.62529,"best_task_score":0.3258},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":243.0,"contact_point_centroid":[0.60442,0.13378,-0.00566],"force_p95":1.16693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.32086,"mean_force":0.29271,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.6169,0.13506,0.18635]},{"body_a":"world","body_b":"grasp_target","contact_count":166.0,"contact_point_centroid":[0.47152,-0.01919,-0.00121],"force_p95":0.32235,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36704,"mean_force":0.09115,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.46235,-0.01952,0.04844]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":776.0,"contact_point_centroid":[0.62213,0.15509,0.16921],"force_p95":0.10455,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25325,"mean_force":0.06847,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62088,0.13621,0.17241]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":833.0,"contact_point_centroid":[0.62182,0.11751,0.16926],"force_p95":0.09417,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25312,"mean_force":0.06236,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.6209,0.13622,0.17244]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21673.0,"contact_point_centroid":[0.45945,-0.03854,0.09508],"force_p95":0.07043,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24383,"mean_force":0.0473,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.4599,-0.01945,0.09432]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18904.0,"contact_point_centroid":[0.45969,-0.00026,0.0953],"force_p95":0.07663,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24357,"mean_force":0.05378,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.4599,-0.01945,0.09431]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02009,-0.00205],"force_p95":0.13761,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17761,"mean_force":0.12663,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46499,-0.01959,0.04812]},{"body_a":"world","body_b":"grasp_target","contact_count":3372.0,"contact_point_centroid":[0.6035,0.13423,-0.00198],"force_p95":0.12606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16233,"mean_force":0.1223,"phase_index":6.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.62135,0.14605,0.25782]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10992.0,"contact_point_centroid":[0.53495,0.07257,0.15427],"force_p95":0.10191,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16066,"mean_force":0.06707,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.53469,0.05363,0.15541]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13179.0,"contact_point_centroid":[0.53409,0.03504,0.1543],"force_p95":0.09112,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15828,"mean_force":0.05657,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.53482,0.05377,0.15543]},{"body_a":"world","body_b":"grasp_target","contact_count":2148.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13215,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48635,-0.00905,0.2099]},{"body_a":"world","body_b":"grasp_target","contact_count":856.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"align","tcp_position_centroid":[0.47183,-0.01908,0.08719]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4840.0,"contact_point_centroid":[0.46342,-0.00031,0.04913],"force_p95":0.06793,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09916,"mean_force":0.045,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4639,-0.01956,0.04702]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5391.0,"contact_point_centroid":[0.46347,-0.03878,0.04884],"force_p95":0.06506,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08195,"mean_force":0.041,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4639,-0.01956,0.04702]}],"total_contact_groups":14},"final_pose_error":0.01567,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.60349,0.13423,0.02602],"final_tcp_position":[0.62897,0.15748,0.32464],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.32086,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":538.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2148.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47418,-0.0185,0.11966],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09367,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":214.0,"n_steps_budget":600.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":856.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.47153,-0.01974,0.05483],"tcp_start":[0.47418,-0.0185,0.11966],"tcp_to_object_dist_end":0.02918,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47609,-0.0197,0.0258],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28827,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13646,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12031.0,"raw_peak_contact_force":0.17761,"tcp_end":[0.46387,-0.01956,0.04699],"tcp_start":[0.47153,-0.01974,0.05483],"tcp_to_object_dist_end":0.02446,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46331,-0.0196,0.11314],"object_pos_start":[0.47609,-0.0197,0.0258],"object_to_goal_dist_end":0.25717,"object_to_goal_dist_start":0.28827,"object_z_max":0.11304,"peak_contact_force":0.08014,"phase_name":"lift_to_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40743.0,"raw_peak_contact_force":0.36704,"subtask_id":"lift_object","tcp_end":[0.45997,-0.01944,0.14065],"tcp_start":[0.46387,-0.01956,0.04699],"tcp_to_object_dist_end":0.02771,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":771.0,"n_steps_budget":1000.0,"object_pos_end":[0.62418,0.1357,0.14343],"object_pos_start":[0.46331,-0.0196,0.11314],"object_to_goal_dist_end":0.05268,"object_to_goal_dist_start":0.25717,"object_z_max":0.14339,"peak_contact_force":0.09926,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24171.0,"raw_peak_contact_force":0.16066,"subtask_id":"reach_goal","tcp_end":[0.62261,0.13625,0.17602],"tcp_start":[0.45997,-0.01944,0.14065],"tcp_to_object_dist_end":0.03264,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60794,0.13397,0.026],"object_pos_start":[0.62418,0.1357,0.14343],"object_to_goal_dist_end":0.1676,"object_to_goal_dist_start":0.05268,"object_z_max":0.14343,"peak_contact_force":0.104,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1852.0,"raw_peak_contact_force":1.32086,"tcp_end":[0.61684,0.13505,0.19596],"tcp_start":[0.62261,0.13625,0.17602],"tcp_to_object_dist_end":0.1702,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.60349,0.13423,0.02602],"object_pos_start":[0.60794,0.13397,0.026],"object_to_goal_dist_end":0.16822,"object_to_goal_dist_start":0.1676,"object_z_max":0.02674,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3372.0,"raw_peak_contact_force":0.16233,"tcp_end":[0.62897,0.15748,0.32464],"tcp_start":[0.61684,0.13505,0.19596],"tcp_to_object_dist_end":0.3006,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68586,"average_solve_count":191.0,"average_success_count":191.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.12184,"descend_grasp.descend_speed":0.12079,"lift_to_clear.lift_speed":0.05227,"release.release_time":0.87443,"retract.retract_speed":0.10855,"transport_to_goal.place_offset_x":0.00401,"transport_to_goal.place_offset_y":-0.00714,"transport_to_goal.place_offset_z":0.00029,"transport_to_goal.transport_speed":0.09355},"optimized_scores":{"best_composite_score":0.12917,"best_fitness_score":0.72917,"best_task_score":0.53456},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":176.0,"contact_point_centroid":[0.59882,0.20639,-0.00559],"force_p95":0.86182,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.92393,"mean_force":0.36286,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.6135,0.18651,0.11439]},{"body_a":"world","body_b":"grasp_target","contact_count":156.0,"contact_point_centroid":[0.45545,-0.02503,-0.0012],"force_p95":0.3077,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39303,"mean_force":0.07349,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.44544,-0.02545,0.04927]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":755.0,"contact_point_centroid":[0.6183,0.2075,0.09863],"force_p95":0.21396,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36482,"mean_force":0.10791,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61767,0.18802,0.10289]},{"body_a":"world","body_b":"grasp_target","contact_count":2840.0,"contact_point_centroid":[0.60159,0.22349,-0.00203],"force_p95":0.14596,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34359,"mean_force":0.12576,"phase_index":6.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61822,0.19598,0.18612]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":742.0,"contact_point_centroid":[0.6191,0.17023,0.10015],"force_p95":0.09864,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28113,"mean_force":0.06412,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61836,0.18829,0.10387]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18878.0,"contact_point_centroid":[0.44254,-0.00617,0.10084],"force_p95":0.07857,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27252,"mean_force":0.05431,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.44304,-0.02534,0.10033]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21305.0,"contact_point_centroid":[0.44244,-0.04441,0.10012],"force_p95":0.07439,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2613,"mean_force":0.04875,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.44304,-0.02534,0.09967]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11546.0,"contact_point_centroid":[0.52695,0.05847,0.12719],"force_p95":0.1009,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2223,"mean_force":0.06718,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.52667,0.07709,0.12909]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02624,-0.00207],"force_p95":0.14284,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1911,"mean_force":0.12785,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44796,-0.02554,0.04871]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9831.0,"contact_point_centroid":[0.52912,0.09762,0.12653],"force_p95":0.11181,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19,"mean_force":0.07757,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.52815,0.07885,0.12875]},{"body_a":"world","body_b":"grasp_target","contact_count":2152.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13212,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47841,-0.01184,0.20989]},{"body_a":"world","body_b":"grasp_target","contact_count":864.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"align","tcp_position_centroid":[0.45515,-0.02493,0.08725]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4354.0,"contact_point_centroid":[0.44708,-0.00626,0.04884],"force_p95":0.07271,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1042,"mean_force":0.04972,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4469,-0.0255,0.04769]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5407.0,"contact_point_centroid":[0.4463,-0.04465,0.04879],"force_p95":0.06532,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0767,"mean_force":0.0408,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4469,-0.0255,0.04769]}],"total_contact_groups":14},"final_pose_error":0.01681,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.60155,0.22394,0.02602],"final_tcp_position":[0.62651,0.20603,0.24785],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.92393,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":539.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2152.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.45789,-0.0242,0.11949],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0935,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":216.0,"n_steps_budget":600.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":864.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.45431,-0.02577,0.05496],"tcp_start":[0.45789,-0.0242,0.11949],"tcp_to_object_dist_end":0.02925,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4585,-0.0257,0.02575],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30328,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14109,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11561.0,"raw_peak_contact_force":0.1911,"tcp_end":[0.44688,-0.0255,0.04766],"tcp_start":[0.45431,-0.02577,0.05496],"tcp_to_object_dist_end":0.02481,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44553,-0.02566,0.12313],"object_pos_start":[0.4585,-0.0257,0.02575],"object_to_goal_dist_end":0.29808,"object_to_goal_dist_start":0.30328,"object_z_max":0.12304,"peak_contact_force":0.07609,"phase_name":"lift_to_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40339.0,"raw_peak_contact_force":0.39303,"subtask_id":"lift_object","tcp_end":[0.44313,-0.02534,0.15183],"tcp_start":[0.44688,-0.0255,0.04766],"tcp_to_object_dist_end":0.02881,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":793.0,"n_steps_budget":1000.0,"object_pos_end":[0.62218,0.18825,0.07355],"object_pos_start":[0.44553,-0.02566,0.12313],"object_to_goal_dist_end":0.04591,"object_to_goal_dist_start":0.29808,"object_z_max":0.12315,"peak_contact_force":0.13423,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21377.0,"raw_peak_contact_force":0.2223,"subtask_id":"reach_goal","tcp_end":[0.62043,0.18843,0.10759],"tcp_start":[0.44313,-0.02534,0.15183],"tcp_to_object_dist_end":0.03408,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60752,0.21027,0.02714],"object_pos_start":[0.62218,0.18825,0.07355],"object_to_goal_dist_end":0.0899,"object_to_goal_dist_start":0.04591,"object_z_max":0.07355,"peak_contact_force":0.34512,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1673.0,"raw_peak_contact_force":0.92393,"tcp_end":[0.61335,0.18647,0.12709],"tcp_start":[0.62043,0.18843,0.10759],"tcp_to_object_dist_end":0.10291,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":726.0,"n_steps_budget":810.0,"object_pos_end":[0.60155,0.22394,0.02602],"object_pos_start":[0.60752,0.21027,0.02714],"object_to_goal_dist_end":0.09395,"object_to_goal_dist_start":0.0899,"object_z_max":0.02724,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2840.0,"raw_peak_contact_force":0.34359,"tcp_end":[0.62651,0.20603,0.24785],"tcp_start":[0.61335,0.18647,0.12709],"tcp_to_object_dist_end":0.22395,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```