## Search State

- **Seed**: 1
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → align → grasp → lift → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | pose_tolerance | 8 | -0.0507 | 0.35 | ✅ accepted |
| 3 | approach → align → grasp → lift → approach → align → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | 0.2022 | 0.20 | ✅ accepted |
| 2 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |
| 1 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |
| 0 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ✅ accepted |

**Proposal policy**: task_score is 0.35 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.051) — your mutation base

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
  weight: 0.3
- id: reach_goal
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
    tolerance: 0.01
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
- **transport_to_goal** (`lift`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
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

- **Composite score**: -0.051
- **task_score** (E): 0.347
- **fitness_score**: 0.469  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1864 |
| descend_grasp | 1.00 | 1.00 | 0.0644 |
| grasp | 1.00 | 1.00 | 0.0110 |
| transport_to_goal | 0.33 | 1.00 | 0.2235 |
| release | 1.00 | 1.00 | 0.0226 |
| retract | 1.00 | 1.00 | 0.1426 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.476, -0.000, 0.119) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | align | 1.00 / step_budget | (0.476, -0.000, 0.119)→(0.474, -0.001, 0.055) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.474, -0.001, 0.055)→(0.466, -0.001, 0.047) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 44.667 | 0.146 | 0.197 |
| transport_to_goal | lift | 0.33 / step_budget | (0.466, -0.001, 0.047)→(0.575, 0.169, 0.132) | (0.479, -0.001, 0.026)→(0.572, 0.147, 0.052) | 0.278→0.127 | 1.00 / 10.667 | 94253.338 | 0.837 |
| release | release | 1.00 / step_budget | (0.575, 0.169, 0.132)→(0.569, 0.167, 0.153) | (0.572, 0.147, 0.052)→(0.566, 0.147, 0.019) | 0.127→0.159 | 1.00 / 3.667 | 0.131 | 0.525 |
| retract | retract | 1.00 / step_budget | (0.569, 0.167, 0.153)→(0.604, 0.201, 0.285) | (0.566, 0.147, 0.019)→(0.564, 0.147, 0.019) | 0.159→0.160 | 1.00 / 4.000 | 0.123 | 0.145 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.319
- phase_score: 0.549
- phase_breakdown.reach_object_score: 0.821
- phase_breakdown.grasp_object_score: 0.603
- phase_breakdown.reach_goal_score: 0.409
- grasp_place_fitness: 0.622

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.622
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.411
- **Median Q (composite search score)**: -0.102
- **K-run variance**: 0.0120
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.358


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67742,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.13873,"descend_grasp.descend_speed":0.05183,"release.release_time":0.33514,"retract.retract_speed":0.10004,"transport_to_goal.place_offset_x":-0.01491,"transport_to_goal.place_offset_y":-0.00432,"transport_to_goal.place_offset_z":-0.00179,"transport_to_goal.transport_speed":0.13519},"optimized_scores":{"best_composite_score":-0.10165,"best_fitness_score":0.41835,"best_task_score":0.41114},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1218.0,"contact_point_centroid":[0.53152,0.14951,-0.00237],"force_p95":0.46002,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.14671,"mean_force":0.22263,"phase_index":3.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.51655,0.14526,0.09216]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9609.0,"contact_point_centroid":[0.50638,0.12234,0.07086],"force_p95":0.15255,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28844,"mean_force":0.08349,"phase_index":3.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.50313,0.10383,0.0715]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10170.0,"contact_point_centroid":[0.50677,0.08482,0.07205],"force_p95":0.14163,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25914,"mean_force":0.08749,"phase_index":3.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.50303,0.10354,0.07135]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04492,-0.00215],"force_p95":0.16429,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22302,"mean_force":0.13355,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48925,0.04337,0.04706]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4330.0,"contact_point_centroid":[0.4884,0.02401,0.04758],"force_p95":0.07812,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1401,"mean_force":0.04967,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48812,0.04327,0.04583]},{"body_a":"world","body_b":"grasp_target","contact_count":2216.0,"contact_point_centroid":[0.50118,0.04505,-0.00194],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49755,0.02038,0.20875]},{"body_a":"world","body_b":"grasp_target","contact_count":884.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"align","tcp_position_centroid":[0.49542,0.04262,0.08624]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55304,0.22143,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.53885,0.22953,0.13581]},{"body_a":"world","body_b":"grasp_target","contact_count":3252.0,"contact_point_centroid":[0.55304,0.22143,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.5475,0.23526,0.21721]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5518.0,"contact_point_centroid":[0.48901,0.06244,0.04826],"force_p95":0.07073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07281,"mean_force":0.04035,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48813,0.04327,0.04584]},{"body_a":"left_finger","body_b":"right_finger","contact_count":394.0,"contact_point_centroid":[0.54064,0.22212,0.13162],"force_p95":0.01478,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0169,"mean_force":0.01129,"phase_index":3.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.54024,0.2221,0.12933]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.54189,0.2309,0.13347],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01103,"mean_force":0.00998,"phase_index":4.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.54167,0.23088,0.13135]}],"total_contact_groups":12},"final_pose_error":0.01506,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.55304,0.22143,0.01602],"final_tcp_position":[0.56081,0.24296,0.28227],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":273011.37364,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":555.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2216.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49709,0.0415,0.11818],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09232,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":221.0,"n_steps_budget":870.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":884.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.49599,0.04397,0.05447],"tcp_start":[0.49709,0.0415,0.11818],"tcp_to_object_dist_end":0.02894,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50115,0.04377,0.02546],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24322,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16099,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11648.0,"raw_peak_contact_force":0.22302,"tcp_end":[0.48809,0.04326,0.0458],"tcp_start":[0.49599,0.04397,0.05447],"tcp_to_object_dist_end":0.02418,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":992.0,"n_steps_budget":1000.0,"object_pos_end":[0.55304,0.22143,0.01602],"object_pos_start":[0.50115,0.04377,0.02546],"object_to_goal_dist_end":0.13333,"object_to_goal_dist_start":0.24322,"object_z_max":0.07914,"peak_contact_force":273011.37364,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21391.0,"raw_peak_contact_force":1.14671,"subtask_id":"reach_goal","tcp_end":[0.54309,0.23112,0.13375],"tcp_start":[0.48809,0.04326,0.0458],"tcp_to_object_dist_end":0.11855,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55304,0.22143,0.01602],"object_pos_start":[0.55304,0.22143,0.01602],"object_to_goal_dist_end":0.13332,"object_to_goal_dist_start":0.13333,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53717,0.22875,0.15593],"tcp_start":[0.54309,0.23112,0.13375],"tcp_to_object_dist_end":0.141,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":813.0,"n_steps_budget":900.0,"object_pos_end":[0.55304,0.22143,0.01602],"object_pos_start":[0.55304,0.22143,0.01602],"object_to_goal_dist_end":0.13332,"object_to_goal_dist_start":0.13332,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3252.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56081,0.24296,0.28227],"tcp_start":[0.53717,0.22875,0.15593],"tcp_to_object_dist_end":0.26724,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82,"average_solve_count":150.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.06461,"descend_grasp.descend_speed":0.06672,"release.release_time":0.60803,"retract.retract_speed":0.11655,"transport_to_goal.place_offset_x":0.00826,"transport_to_goal.place_offset_y":0.00289,"transport_to_goal.place_offset_z":0.00103,"transport_to_goal.transport_speed":0.14958},"optimized_scores":{"best_composite_score":0.10175,"best_fitness_score":0.62175,"best_task_score":0.31882},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":191.0,"contact_point_centroid":[0.59863,0.13159,-0.00648],"force_p95":1.09096,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.32982,"mean_force":0.35819,"phase_index":4.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60325,0.13217,0.17139]},{"body_a":"world","body_b":"grasp_target","contact_count":382.0,"contact_point_centroid":[0.48389,-0.01178,-0.0016],"force_p95":0.42369,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58403,"mean_force":0.27074,"phase_index":3.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.46853,-0.01216,0.05025]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13225.0,"contact_point_centroid":[0.5289,0.02808,0.09466],"force_p95":0.12776,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32913,"mean_force":0.08189,"phase_index":3.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.52465,0.04688,0.09444]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":601.0,"contact_point_centroid":[0.61259,0.15158,0.15383],"force_p95":0.12716,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27916,"mean_force":0.08513,"phase_index":4.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60737,0.13331,0.15763]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":564.0,"contact_point_centroid":[0.61242,0.11484,0.15316],"force_p95":0.13562,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25002,"mean_force":0.08875,"phase_index":4.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60725,0.13328,0.15742]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12966.0,"contact_point_centroid":[0.52851,0.06545,0.09398],"force_p95":0.1245,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21134,"mean_force":0.07629,"phase_index":3.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.5245,0.04674,0.09432]},{"body_a":"world","body_b":"grasp_target","contact_count":3240.0,"contact_point_centroid":[0.59052,0.13045,-0.00198],"force_p95":0.12851,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19023,"mean_force":0.12286,"phase_index":5.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61382,0.14416,0.24833]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02009,-0.00205],"force_p95":0.13757,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17753,"mean_force":0.12662,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.465,-0.01959,0.04818]},{"body_a":"world","body_b":"grasp_target","contact_count":2284.0,"contact_point_centroid":[0.47616,-0.02015,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48621,-0.00905,0.20981]},{"body_a":"world","body_b":"grasp_target","contact_count":880.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"align","tcp_position_centroid":[0.47169,-0.01908,0.0871]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4840.0,"contact_point_centroid":[0.46343,-0.00031,0.04915],"force_p95":0.06789,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09917,"mean_force":0.045,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46391,-0.01956,0.04707]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5390.0,"contact_point_centroid":[0.46348,-0.03878,0.04886],"force_p95":0.06505,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08187,"mean_force":0.04101,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46391,-0.01956,0.04707]}],"total_contact_groups":12},"final_pose_error":0.01688,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.59046,0.1304,0.02602],"final_tcp_position":[0.62828,0.15729,0.32354],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.32982,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":572.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2284.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47407,-0.01851,0.1195],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09352,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":220.0,"n_steps_budget":720.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":880.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.47153,-0.01974,0.05487],"tcp_start":[0.47407,-0.01851,0.1195],"tcp_to_object_dist_end":0.02922,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47609,-0.01971,0.02581],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28827,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13643,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12030.0,"raw_peak_contact_force":0.17753,"tcp_end":[0.46388,-0.01956,0.04704],"tcp_start":[0.47153,-0.01974,0.05487],"tcp_to_object_dist_end":0.02449,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61411,0.13232,0.1254],"object_pos_start":[0.47609,-0.01971,0.02581],"object_to_goal_dist_end":0.07209,"object_to_goal_dist_start":0.28827,"object_z_max":0.12528,"peak_contact_force":0.13735,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26573.0,"raw_peak_contact_force":0.58403,"subtask_id":"reach_goal","tcp_end":[0.60913,0.13336,0.16104],"tcp_start":[0.46388,-0.01956,0.04704],"tcp_to_object_dist_end":0.03601,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59622,0.13182,0.02641],"object_pos_start":[0.61411,0.13232,0.1254],"object_to_goal_dist_end":0.16957,"object_to_goal_dist_start":0.07209,"object_z_max":0.12545,"peak_contact_force":0.14855,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1356.0,"raw_peak_contact_force":1.32982,"tcp_end":[0.60317,0.13216,0.18171],"tcp_start":[0.60913,0.13336,0.16104],"tcp_to_object_dist_end":0.15546,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":812.0,"n_steps_budget":870.0,"object_pos_end":[0.59046,0.1304,0.02602],"object_pos_start":[0.59622,0.13182,0.02641],"object_to_goal_dist_end":0.17147,"object_to_goal_dist_start":0.16957,"object_z_max":0.02659,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3240.0,"raw_peak_contact_force":0.19023,"tcp_end":[0.62828,0.15729,0.32354],"tcp_start":[0.60317,0.13216,0.18171],"tcp_to_object_dist_end":0.30112,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.63758,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.065,"descend_grasp.descend_speed":0.06944,"release.release_time":0.50265,"retract.retract_speed":0.12816,"transport_to_goal.place_offset_x":-0.01582,"transport_to_goal.place_offset_y":-0.01995,"transport_to_goal.place_offset_z":0.00987,"transport_to_goal.transport_speed":0.13577},"optimized_scores":{"best_composite_score":-0.15211,"best_fitness_score":0.36789,"best_task_score":0.31162},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2232.0,"contact_point_centroid":[0.51733,0.05089,-0.00243],"force_p95":0.54839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.78053,"mean_force":0.23032,"phase_index":3.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.51607,0.06746,0.07551]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9285.0,"contact_point_centroid":[0.47983,0.00056,0.05928],"force_p95":0.17637,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37378,"mean_force":0.09782,"phase_index":3.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.4785,0.01968,0.0593]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6508.0,"contact_point_centroid":[0.47938,0.03614,0.05647],"force_p95":0.17336,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2986,"mean_force":0.10066,"phase_index":3.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.47668,0.01725,0.05855]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02625,-0.00207],"force_p95":0.14263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19098,"mean_force":0.12783,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44794,-0.02555,0.04855]},{"body_a":"world","body_b":"grasp_target","contact_count":2308.0,"contact_point_centroid":[0.45856,-0.02632,-0.00194],"force_p95":0.13136,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47826,-0.01185,0.20975]},{"body_a":"world","body_b":"grasp_target","contact_count":892.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"align","tcp_position_centroid":[0.455,-0.02493,0.08707]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54867,0.08851,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.56913,0.14015,0.1024]},{"body_a":"world","body_b":"grasp_target","contact_count":3128.0,"contact_point_centroid":[0.54867,0.08851,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.59339,0.17075,0.18138]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4354.0,"contact_point_centroid":[0.44707,-0.00629,0.04873],"force_p95":0.07274,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10351,"mean_force":0.04965,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44689,-0.02551,0.04753]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5200.0,"contact_point_centroid":[0.44661,-0.04466,0.04871],"force_p95":0.06704,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07675,"mean_force":0.04237,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44689,-0.02551,0.04753]},{"body_a":"left_finger","body_b":"right_finger","contact_count":996.0,"contact_point_centroid":[0.55829,0.12118,0.09578],"force_p95":0.01268,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0161,"mean_force":0.01077,"phase_index":3.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.55805,0.12118,0.09351]},{"body_a":"left_finger","body_b":"right_finger","contact_count":217.0,"contact_point_centroid":[0.57261,0.14112,0.10005],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0127,"mean_force":0.01023,"phase_index":4.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57239,0.14112,0.09793]}],"total_contact_groups":12},"final_pose_error":0.01742,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.54867,0.08851,0.01602],"final_tcp_position":[0.6244,0.20384,0.24826],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":9748.50328,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":578.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2308.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.45781,-0.0242,0.11946],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09347,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":223.0,"n_steps_budget":690.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":892.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.45429,-0.02577,0.05479],"tcp_start":[0.45781,-0.0242,0.11946],"tcp_to_object_dist_end":0.02909,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4585,-0.0257,0.02575],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30328,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14114,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11354.0,"raw_peak_contact_force":0.19098,"tcp_end":[0.44686,-0.0255,0.0475],"tcp_start":[0.45429,-0.02577,0.05479],"tcp_to_object_dist_end":0.02467,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54867,0.08851,0.01602],"object_pos_start":[0.4585,-0.0257,0.02575],"object_to_goal_dist_end":0.17489,"object_to_goal_dist_start":0.30328,"object_z_max":0.04717,"peak_contact_force":9748.50328,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19021.0,"raw_peak_contact_force":0.78053,"subtask_id":"reach_goal","tcp_end":[0.57401,0.1411,0.10043],"tcp_start":[0.44686,-0.0255,0.0475],"tcp_to_object_dist_end":0.10263,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54867,0.08851,0.01602],"object_pos_start":[0.54867,0.08851,0.01602],"object_to_goal_dist_end":0.17489,"object_to_goal_dist_start":0.17489,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56717,0.1396,0.12253],"tcp_start":[0.57401,0.1411,0.10043],"tcp_to_object_dist_end":0.11957,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":782.0,"n_steps_budget":840.0,"object_pos_end":[0.54867,0.08851,0.01602],"object_pos_start":[0.54867,0.08851,0.01602],"object_to_goal_dist_end":0.17489,"object_to_goal_dist_start":0.17489,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3128.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6244,0.20384,0.24826],"tcp_start":[0.56717,0.1396,0.12253],"tcp_to_object_dist_end":0.27013,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```