## Search State

- **Seed**: 3
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.3732 | 0.48 | ✅ accepted |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.3285 | 0.39 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.2857 | 0.30 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.2712 | 0.28 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.3081 | 0.35 | ❌ rejected |

**Proposal policy**: task_score is 0.48 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `51caab5aeef033bda3880e250ac3d834b494dfd11f1563b679caeea40811318b`
- Frozen object start: [0.45856491671436245, -0.02631894934039003, 0.03]
- Frozen task target: [0.6301274465206397, 0.20821620360643678, 0.11411929633605988]
- Goal object position: (0.6301274465206397, 0.20821620360643678, 0.11411929633605988)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6301274465206397, 0.20821620360643678, 0.11411929633605988)
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
  frozen_targets: {'place_target': [0.6301274465206397, 0.20821620360643678, 0.11411929633605988]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 51caab5aeef033bda3880e250ac3d834b494dfd11f1563b679caeea40811318b

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
| `goal` | offset from task goal position (0.6301274465206397, 0.20821620360643678, 0.11411929633605988) | final destination targets |
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

## Current Skill (Q=0.373) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_objective
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: placement_objective
  target_entity: object
  metric: goal_progress
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
    - 0.05
    tolerance: 0.01
    orientation:
      mode: keep_current
  subtask_id: approach_objective
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
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
- id: grasp
  type: grasp
  control: impedance_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  guards:
  - id: grasp_closed
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.3
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
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
    - 0.15
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
- id: transport_to_goal
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: object_held_after
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.3
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
- id: descend_to_place
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
  subtask_id: placement_objective
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
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_closed, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.3
  - retries: max_attempts=2, strategy=repeat
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=object_held_after, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.3
  - retries: max_attempts=1, strategy=repeat
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.373
- **task_score** (E): 0.480
- **fitness_score**: 0.703  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.2168 |
| descend_to_grasp | 1.00 | 1.00 | 0.0341 |
| grasp | 1.00 | 1.00 | 0.0121 |
| lift | 1.00 | 1.00 | 0.1037 |
| transport_to_goal | 1.00 | 1.00 | 0.2267 |
| descend_to_place | 1.00 | 1.00 | 0.0667 |
| release | 1.00 | 1.00 | 0.0194 |
| retract | 1.00 | 1.00 | 0.0848 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.088) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, 0.002, 0.088)→(0.505, 0.002, 0.054) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.505, 0.002, 0.054)→(0.497, 0.002, 0.045) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 43.333 | 0.142 | 0.189 |
| lift | lift | 1.00 / step_budget | (0.497, 0.002, 0.045)→(0.494, 0.002, 0.149) | (0.511, 0.002, 0.026)→(0.507, 0.002, 0.124) | 0.246→0.223 | 1.00 / 24.667 | 0.102 | 0.427 |
| transport_to_goal | approach | 1.00 / step_budget | (0.494, 0.002, 0.149)→(0.617, 0.171, 0.222) | (0.507, 0.002, 0.124)→(0.623, 0.171, 0.191) | 0.223→0.054 | 1.00 / 18.000 | 0.132 | 0.168 |
| descend_to_place | descend | 1.00 / step_budget | (0.617, 0.171, 0.222)→(0.620, 0.177, 0.156) | (0.623, 0.171, 0.191)→(0.623, 0.177, 0.123) | 0.054→0.017 | 1.00 / 19.667 | 55983.998 | 0.281 |
| release | release | 1.00 / step_budget | (0.620, 0.177, 0.156)→(0.614, 0.175, 0.174) | (0.623, 0.177, 0.123)→(0.608, 0.174, 0.024) | 0.017→0.116 | 1.00 / 4.000 | 0.152 | 1.182 |
| retract | retract | 1.00 / step_budget | (0.614, 0.175, 0.174)→(0.611, 0.174, 0.259) | (0.608, 0.174, 0.024)→(0.604, 0.174, 0.026) | 0.116→0.114 | 1.00 / 4.000 | 0.123 | 0.161 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.566
- phase_score: 0.787
- phase_breakdown.approach_objective_score: 0.820
- phase_breakdown.placement_objective_score: 0.773
- grasp_place_fitness: 0.747

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.747
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.566
- **Median Q (composite search score)**: 0.404
- **K-run variance**: 0.0028
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.442


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `952d4e9e12c194d228cf63d10b31c959edc327920598c352d26dcf1284463776`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ab36b663de63a40a5839be0af4fc1d53d37f9e78d4183a3de7f11063534632b8`; realized-scene SHA-256: `51caab5aeef033bda3880e250ac3d834b494dfd11f1563b679caeea40811318b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82488,"average_solve_count":217.0,"average_success_count":217.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift.lift_height":0.1223,"transport_to_goal.transport_height":0.09549,"transport_to_goal.transport_speed":0.07483},"optimized_scores":{"best_composite_score":0.40434,"best_fitness_score":0.73434,"best_task_score":0.54502},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":314.0,"contact_point_centroid":[0.60876,0.2026,-0.00369],"force_p95":0.77909,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.09159,"mean_force":0.22088,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61616,0.201,0.13806]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.45591,-0.0247,-0.00128],"force_p95":0.34591,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39474,"mean_force":0.06616,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44576,-0.02531,0.04931]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":500.0,"contact_point_centroid":[0.62511,0.221,0.12071],"force_p95":0.15702,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38781,"mean_force":0.10267,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62035,0.20259,0.12586]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":557.0,"contact_point_centroid":[0.62489,0.18437,0.12135],"force_p95":0.12999,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36892,"mean_force":0.09134,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62042,0.20261,0.12596]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7408.0,"contact_point_centroid":[0.44527,-0.00617,0.09686],"force_p95":0.10541,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28711,"mean_force":0.06582,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44338,-0.0252,0.09614]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8277.0,"contact_point_centroid":[0.44502,-0.04415,0.09683],"force_p95":0.09929,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2646,"mean_force":0.06,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44339,-0.0252,0.09602]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1147.0,"contact_point_centroid":[0.62563,0.1816,0.16212],"force_p95":0.1676,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25835,"mean_force":0.10741,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62044,0.19987,0.16603]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1063.0,"contact_point_centroid":[0.62585,0.21808,0.1626],"force_p95":0.16718,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25136,"mean_force":0.11457,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6204,0.19982,0.16657]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45859,-0.02624,-0.00208],"force_p95":0.14598,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19694,"mean_force":0.12868,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44798,-0.02539,0.04873]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9879.0,"contact_point_centroid":[0.53055,0.06207,0.17345],"force_p95":0.12195,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16406,"mean_force":0.08219,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52522,0.08044,0.17428]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9134.0,"contact_point_centroid":[0.52779,0.09559,0.1726],"force_p95":0.13407,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15963,"mean_force":0.0883,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52253,0.07706,0.17358]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.60785,0.20271,-0.00198],"force_p95":0.12823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15449,"mean_force":0.12266,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61284,0.19977,0.18946]},{"body_a":"world","body_b":"grasp_target","contact_count":2556.0,"contact_point_centroid":[0.45856,-0.02632,-0.00194],"force_p95":0.13017,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4779,-0.01207,0.19433]},{"body_a":"world","body_b":"grasp_target","contact_count":500.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45512,-0.025,0.0725]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4350.0,"contact_point_centroid":[0.4471,-0.00611,0.04881],"force_p95":0.0731,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10647,"mean_force":0.04975,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44693,-0.02535,0.04771]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5419.0,"contact_point_centroid":[0.44632,-0.04451,0.04877],"force_p95":0.06576,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0692,"mean_force":0.04078,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44693,-0.02535,0.04771]}],"total_contact_groups":16},"final_pose_error":0.01587,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.60785,0.20271,0.02602],"final_tcp_position":[0.61309,0.19981,0.23407],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.09159,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":640.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2556.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_objective","tcp_end":[0.45734,-0.02446,0.08964],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06366,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":125.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":500.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45432,-0.02562,0.05496],"tcp_start":[0.45734,-0.02446,0.08964],"tcp_to_object_dist_end":0.02926,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45851,-0.02561,0.02571],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30322,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14391,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11569.0,"raw_peak_contact_force":0.19694,"tcp_end":[0.4469,-0.02535,0.04768],"tcp_start":[0.45432,-0.02562,0.05496],"tcp_to_object_dist_end":0.02485,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":463.0,"n_steps_budget":780.0,"object_pos_end":[0.45602,-0.02552,0.12883],"object_pos_start":[0.45851,-0.02561,0.02571],"object_to_goal_dist_end":0.29183,"object_to_goal_dist_start":0.30322,"object_z_max":0.12865,"peak_contact_force":0.10436,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15773.0,"raw_peak_contact_force":0.39474,"tcp_end":[0.44334,-0.02519,0.15553],"tcp_start":[0.4469,-0.02535,0.04768],"tcp_to_object_dist_end":0.02956,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":881.0,"n_steps_budget":1000.0,"object_pos_end":[0.62387,0.19598,0.16325],"object_pos_start":[0.45602,-0.02552,0.12883],"object_to_goal_dist_end":0.05102,"object_to_goal_dist_start":0.29183,"object_z_max":0.16322,"peak_contact_force":0.11566,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":19013.0,"raw_peak_contact_force":0.16406,"tcp_end":[0.6185,0.19651,0.1984],"tcp_start":[0.44334,-0.02519,0.15553],"tcp_to_object_dist_end":0.03556,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":120.0,"n_steps_budget":1000.0,"object_pos_end":[0.62653,0.20258,0.09538],"object_pos_start":[0.62387,0.19598,0.16325],"object_to_goal_dist_end":0.01989,"object_to_goal_dist_start":0.05102,"object_z_max":0.16325,"peak_contact_force":0.12235,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2210.0,"raw_peak_contact_force":0.25835,"subtask_id":"placement_objective","tcp_end":[0.62321,0.20343,0.13192],"tcp_start":[0.6185,0.19651,0.1984],"tcp_to_object_dist_end":0.0367,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60821,0.20252,0.02653],"object_pos_start":[0.62653,0.20258,0.09538],"object_to_goal_dist_end":0.09048,"object_to_goal_dist_start":0.01989,"object_z_max":0.09538,"peak_contact_force":0.14668,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1371.0,"raw_peak_contact_force":1.09159,"tcp_end":[0.61606,0.20095,0.14961],"tcp_start":[0.62321,0.20343,0.13192],"tcp_to_object_dist_end":0.12335,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.60785,0.20271,0.02602],"object_pos_start":[0.60821,0.20252,0.02653],"object_to_goal_dist_end":0.09104,"object_to_goal_dist_start":0.09048,"object_z_max":0.02653,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.15449,"tcp_end":[0.61309,0.19981,0.23407],"tcp_start":[0.61606,0.20095,0.14961],"tcp_to_object_dist_end":0.20813,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3745,"average_solve_count":251.0,"average_success_count":251.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift.lift_height":0.10494,"transport_to_goal.transport_height":0.08903,"transport_to_goal.transport_speed":0.03333},"optimized_scores":{"best_composite_score":0.29882,"best_fitness_score":0.62882,"best_task_score":0.3286},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":174.0,"contact_point_centroid":[0.62594,0.14814,-0.00733],"force_p95":1.34316,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.52478,"mean_force":0.40125,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63686,0.15294,0.22021]},{"body_a":"world","body_b":"grasp_target","contact_count":94.0,"contact_point_centroid":[0.54115,0.00038,-0.00124],"force_p95":0.38462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44344,"mean_force":0.07987,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.528,0.00084,0.0448]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":651.0,"contact_point_centroid":[0.64514,0.17234,0.20223],"force_p95":0.19701,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33631,"mean_force":0.09651,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.64003,0.15396,0.2033]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6485.0,"contact_point_centroid":[0.52834,-0.01806,0.08601],"force_p95":0.10832,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31217,"mean_force":0.07264,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52526,0.00079,0.08388]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":770.0,"contact_point_centroid":[0.64505,0.13572,0.20147],"force_p95":0.19516,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30172,"mean_force":0.09118,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.64001,0.15395,0.20324]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":912.0,"contact_point_centroid":[0.6469,0.17049,0.2366],"force_p95":0.19065,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29417,"mean_force":0.11249,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64074,0.15223,0.23727]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6806.0,"contact_point_centroid":[0.52845,0.01958,0.08436],"force_p95":0.10645,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28988,"mean_force":0.07002,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52531,0.00079,0.08251]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1153.0,"contact_point_centroid":[0.64662,0.13408,0.23792],"force_p95":0.17514,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26598,"mean_force":0.10065,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64064,0.15209,0.23909]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11600.0,"contact_point_centroid":[0.58719,0.05751,0.19842],"force_p95":0.09477,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18651,"mean_force":0.07163,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58111,0.07615,0.19736]},{"body_a":"world","body_b":"grasp_target","contact_count":2244.0,"contact_point_centroid":[0.62534,0.14816,-0.00204],"force_p95":0.14622,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18063,"mean_force":0.12274,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.63443,0.1522,0.26744]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10802.0,"contact_point_centroid":[0.5868,0.09428,0.19803],"force_p95":0.1007,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16957,"mean_force":0.07639,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58061,0.07555,0.19679]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00103,-0.00203],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15387,"mean_force":0.12543,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53057,0.00088,0.04482]},{"body_a":"world","body_b":"grasp_target","contact_count":2780.0,"contact_point_centroid":[0.54431,0.00113,-0.00195],"force_p95":0.12911,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51744,0.00049,0.19253]},{"body_a":"world","body_b":"grasp_target","contact_count":464.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53672,0.00099,0.07033]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4119.0,"contact_point_centroid":[0.53054,-0.01834,0.04607],"force_p95":0.07627,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11847,"mean_force":0.05178,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52936,0.00086,0.04339]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53046,0.01994,0.04518],"force_p95":0.06833,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09378,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52936,0.00086,0.04339]}],"total_contact_groups":16},"final_pose_error":0.01561,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.62491,0.14815,0.02602],"final_tcp_position":[0.63488,0.15227,0.31147],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.52478,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":696.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2780.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_objective","tcp_end":[0.5373,0.00099,0.08712],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0615,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":116.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":464.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53775,0.00101,0.05343],"tcp_start":[0.5373,0.00099,0.08712],"tcp_to_object_dist_end":0.02819,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54421,0.00077,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25049,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13058,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10797.0,"raw_peak_contact_force":0.15387,"tcp_end":[0.52933,0.00086,0.04335],"tcp_start":[0.53775,0.00101,0.05343],"tcp_to_object_dist_end":0.02296,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":456.0,"n_steps_budget":660.0,"object_pos_end":[0.53874,0.00082,0.11067],"object_pos_start":[0.54421,0.00077,0.02587],"object_to_goal_dist_end":0.20751,"object_to_goal_dist_start":0.25049,"object_z_max":0.11052,"peak_contact_force":0.11212,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13385.0,"raw_peak_contact_force":0.44344,"tcp_end":[0.52519,0.0008,0.13398],"tcp_start":[0.52933,0.00086,0.04335],"tcp_to_object_dist_end":0.02696,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":885.0,"n_steps_budget":1000.0,"object_pos_end":[0.6456,0.15007,0.23371],"object_pos_start":[0.53874,0.00082,0.11067],"object_to_goal_dist_end":0.0434,"object_to_goal_dist_start":0.20751,"object_z_max":0.2336,"peak_contact_force":0.14142,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22402.0,"raw_peak_contact_force":0.18651,"tcp_end":[0.63936,0.1499,0.26405],"tcp_start":[0.52519,0.0008,0.13398],"tcp_to_object_dist_end":0.03098,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":98.0,"n_steps_budget":1000.0,"object_pos_end":[0.64443,0.15403,0.1778],"object_pos_start":[0.6456,0.15007,0.23371],"object_to_goal_dist_end":0.01427,"object_to_goal_dist_start":0.0434,"object_z_max":0.23372,"peak_contact_force":0.14125,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2065.0,"raw_peak_contact_force":0.29417,"subtask_id":"placement_objective","tcp_end":[0.64235,0.15448,0.2096],"tcp_start":[0.63936,0.1499,0.26405],"tcp_to_object_dist_end":0.03187,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63515,0.14828,0.02028],"object_pos_start":[0.64443,0.15403,0.1778],"object_to_goal_dist_end":0.17156,"object_to_goal_dist_start":0.01427,"object_z_max":0.1778,"peak_contact_force":0.16825,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1595.0,"raw_peak_contact_force":1.52478,"tcp_end":[0.63684,0.15294,0.22694],"tcp_start":[0.64235,0.15448,0.2096],"tcp_to_object_dist_end":0.20671,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.62491,0.14815,0.02602],"object_pos_start":[0.63515,0.14828,0.02028],"object_to_goal_dist_end":0.16694,"object_to_goal_dist_start":0.17156,"object_z_max":0.02687,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2244.0,"raw_peak_contact_force":0.18063,"tcp_end":[0.63488,0.15227,0.31147],"tcp_start":[0.63684,0.15294,0.22694],"tcp_to_object_dist_end":0.28565,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46083,"average_solve_count":217.0,"average_success_count":217.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift.lift_height":0.12683,"transport_to_goal.transport_height":0.10896,"transport_to_goal.transport_speed":0.04639},"optimized_scores":{"best_composite_score":0.41656,"best_fitness_score":0.74656,"best_task_score":0.56569},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":309.0,"contact_point_centroid":[0.57985,0.17107,-0.00377],"force_p95":0.83181,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.93001,"mean_force":0.22572,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58825,0.17205,0.13446]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":654.0,"contact_point_centroid":[0.59724,0.15519,0.11899],"force_p95":0.14099,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44526,"mean_force":0.08431,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59249,0.17347,0.12114]},{"body_a":"world","body_b":"grasp_target","contact_count":102.0,"contact_point_centroid":[0.52816,0.02869,-0.0013],"force_p95":0.34013,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44342,"mean_force":0.06245,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51471,0.02922,0.04587]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":650.0,"contact_point_centroid":[0.59724,0.19171,0.11845],"force_p95":0.14118,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43388,"mean_force":0.08266,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59249,0.17347,0.12115]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8540.0,"contact_point_centroid":[0.51581,0.04797,0.09835],"force_p95":0.10408,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29967,"mean_force":0.06728,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5121,0.02905,0.09612]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1362.0,"contact_point_centroid":[0.59898,0.18835,0.16598],"force_p95":0.17521,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28982,"mean_force":0.1058,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59305,0.17019,0.16709]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8408.0,"contact_point_centroid":[0.51562,0.0102,0.09677],"force_p95":0.10122,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.275,"mean_force":0.06795,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51212,0.02905,0.09432]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1562.0,"contact_point_centroid":[0.59877,0.15199,0.16576],"force_p95":0.17804,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26161,"mean_force":0.10494,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59303,0.17016,0.16727]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03066,-0.00212],"force_p95":0.1556,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21741,"mean_force":0.13167,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51728,0.02939,0.04555]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7259.0,"contact_point_centroid":[0.55691,0.11676,0.17905],"force_p95":0.09671,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15331,"mean_force":0.07379,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5507,0.09807,0.1786]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7173.0,"contact_point_centroid":[0.55821,0.08168,0.1799],"force_p95":0.09863,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15315,"mean_force":0.07436,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55207,0.10039,0.17945]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.57895,0.17102,-0.00198],"force_p95":0.12951,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14909,"mean_force":0.12264,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.58485,0.17096,0.18654]},{"body_a":"world","body_b":"grasp_target","contact_count":2736.0,"contact_point_centroid":[0.5305,0.03079,-0.00195],"force_p95":0.12911,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51101,0.0142,0.19279]},{"body_a":"world","body_b":"grasp_target","contact_count":468.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52355,0.0292,0.07075]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4890.0,"contact_point_centroid":[0.51712,0.01015,0.04698],"force_p95":0.07097,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10968,"mean_force":0.04414,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51609,0.02932,0.04419]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4994.0,"contact_point_centroid":[0.51702,0.04861,0.04597],"force_p95":0.07309,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07492,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51609,0.02932,0.04419]}],"total_contact_groups":16},"final_pose_error":0.01504,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57895,0.17102,0.02602],"final_tcp_position":[0.58506,0.17099,0.23121],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":685.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2736.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_objective","tcp_end":[0.52437,0.02866,0.08754],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06186,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":117.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":468.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52431,0.02985,0.05377],"tcp_start":[0.52437,0.02866,0.08754],"tcp_to_object_dist_end":0.02845,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53046,0.02981,0.02556],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18438,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.1511,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11684.0,"raw_peak_contact_force":0.21741,"tcp_end":[0.51606,0.02932,0.04415],"tcp_start":[0.52431,0.02985,0.05377],"tcp_to_object_dist_end":0.02352,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":551.0,"n_steps_budget":810.0,"object_pos_end":[0.52609,0.02925,0.13176],"object_pos_start":[0.53046,0.02981,0.02556],"object_to_goal_dist_end":0.16897,"object_to_goal_dist_start":0.18438,"object_z_max":0.1316,"peak_contact_force":0.08831,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17050.0,"raw_peak_contact_force":0.44342,"tcp_end":[0.51218,0.02906,0.15665],"tcp_start":[0.51606,0.02932,0.04415],"tcp_to_object_dist_end":0.02851,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":571.0,"n_steps_budget":1000.0,"object_pos_end":[0.59843,0.16658,0.17456],"object_pos_start":[0.52609,0.02925,0.13176],"object_to_goal_dist_end":0.06762,"object_to_goal_dist_start":0.16897,"object_z_max":0.1745,"peak_contact_force":0.13937,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14432.0,"raw_peak_contact_force":0.15331,"tcp_end":[0.5917,0.16652,0.20456],"tcp_start":[0.51218,0.02906,0.15665],"tcp_to_object_dist_end":0.03075,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":142.0,"n_steps_budget":1000.0,"object_pos_end":[0.59677,0.17352,0.09439],"object_pos_start":[0.59843,0.16658,0.17456],"object_to_goal_dist_end":0.01537,"object_to_goal_dist_start":0.06762,"object_z_max":0.17456,"peak_contact_force":167951.73011,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2924.0,"raw_peak_contact_force":0.28982,"subtask_id":"placement_objective","tcp_end":[0.59531,0.17419,0.12655],"tcp_start":[0.5917,0.16652,0.20456],"tcp_to_object_dist_end":0.0322,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5794,0.17102,0.02653],"object_pos_start":[0.59677,0.17352,0.09439],"object_to_goal_dist_end":0.08484,"object_to_goal_dist_start":0.01537,"object_z_max":0.09439,"peak_contact_force":0.14086,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1613.0,"raw_peak_contact_force":0.93001,"tcp_end":[0.58814,0.17201,0.1459],"tcp_start":[0.59531,0.17419,0.12655],"tcp_to_object_dist_end":0.11969,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.57895,0.17102,0.02602],"object_pos_start":[0.5794,0.17102,0.02653],"object_to_goal_dist_end":0.08546,"object_to_goal_dist_start":0.08484,"object_z_max":0.02653,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.14909,"tcp_end":[0.58506,0.17099,0.23121],"tcp_start":[0.58814,0.17201,0.1459],"tcp_to_object_dist_end":0.20529,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```