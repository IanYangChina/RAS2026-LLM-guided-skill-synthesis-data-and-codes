## Search State

- **Seed**: 3
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.1553 | 0.36 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.0993 | 0.21 | ✅ accepted |
| 2 | rotate → retract → descend → pull → rotate | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.0374 | 0.17 | ❌ rejected |
| 1 | rotate → retract → descend → pull → rotate | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.0374 | 0.17 | ❌ rejected |
| 0 | rotate → retract → descend → pull → rotate | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.0374 | 0.17 | ✅ accepted |

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

## Current Skill (Q=0.155) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: approach_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: place_at_goal
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
    - 0.12
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.1
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
  subtask_id: approach_grasp
- id: descend_to_object
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
    - 0.025
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    grasp_offset_z:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.025
      binds_to:
      - path: target.offset.z
        mode: replace
- id: close_gripper
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
- id: lift_object
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
    - 0.12
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_offset_z:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: approach_grasp
- id: move_to_goal
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    goal_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: admittance_control
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
    place_offset_z:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
- id: release_object
  type: release
  control: position_control
  termination: pose_tolerance
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.12], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_object** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.025], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_offset_z: status=consumed; consumers=target.offset.z (replace)
- **close_gripper** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.12], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_offset_z: status=consumed; consumers=target.offset.z (replace)
- **move_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - goal_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_offset_z: status=consumed; consumers=target.offset.z (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.155
- **task_score** (E): 0.359
- **fitness_score**: 0.555  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.400

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1383 |
| descend_to_object | 1.00 | 1.00 | 0.1091 |
| close_gripper | 1.00 | 1.00 | 0.0127 |
| lift_object | 1.00 | 1.00 | 0.0768 |
| move_to_goal | 1.00 | 1.00 | 0.2562 |
| descend_to_place | 1.00 | 1.00 | 0.1264 |
| release_object | 1.00 | 1.00 | 0.0196 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.168) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_object | descend | 1.00 / step_budget | (0.506, 0.002, 0.168)→(0.506, 0.002, 0.059) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 17.420 | 0.123 |
| close_gripper | grasp | 1.00 / step_budget | (0.506, 0.002, 0.059)→(0.498, 0.002, 0.049) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 35.667 | 0.145 | 0.192 |
| lift_object | lift | 1.00 / step_budget | (0.498, 0.002, 0.049)→(0.505, 0.002, 0.126) | (0.511, 0.002, 0.026)→(0.518, 0.002, 0.099) | 0.246→0.217 | 1.00 / 26.000 | 0.106 | 0.350 |
| move_to_goal | approach | 1.00 / step_budget | (0.505, 0.002, 0.126)→(0.617, 0.170, 0.275) | (0.518, 0.002, 0.099)→(0.571, 0.097, 0.016) | 0.217→0.162 | 1.00 / 8.000 | 6499.263 | 1.777 |
| descend_to_place | descend | 1.00 / step_budget | (0.617, 0.170, 0.275)→(0.621, 0.178, 0.149) | (0.571, 0.097, 0.016)→(0.571, 0.097, 0.016) | 0.162→0.162 | 1.00 / 8.333 | 91002.084 | 0.123 |
| release_object | release | 1.00 / step_budget | (0.621, 0.178, 0.149)→(0.614, 0.176, 0.167) | (0.571, 0.097, 0.016)→(0.571, 0.097, 0.016) | 0.162→0.162 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.337
- phase_score: 0.293
- phase_breakdown.approach_grasp_score: 0.838
- phase_breakdown.place_at_goal_score: 0.059
- grasp_place_fitness: 0.630

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.630
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.514
- **Median Q (composite search score)**: 0.177
- **K-run variance**: 0.0051
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.619


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.3629,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.40246,"descend_to_object.grasp_offset_z":0.01128,"descend_to_place.place_offset_z":-0.01605,"lift_object.lift_offset_z":0.13079,"move_to_goal.goal_speed":0.45535},"optimized_scores":{"best_composite_score":0.22962,"best_fitness_score":0.62962,"best_task_score":0.33732},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1309.0,"contact_point_centroid":[0.54689,0.10783,-0.00286],"force_p95":0.39436,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.88176,"mean_force":0.1647,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.57592,0.13893,0.24363]},{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.4567,-0.02497,-0.00143],"force_p95":0.32555,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36548,"mean_force":0.07419,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4473,-0.02508,0.05036]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3099.0,"contact_point_centroid":[0.48319,-0.00939,0.17005],"force_p95":0.15086,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33019,"mean_force":0.08641,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.47764,0.00922,0.17]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3299.0,"contact_point_centroid":[0.48725,0.03295,0.17426],"force_p95":0.13762,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30272,"mean_force":0.08646,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.4815,0.01443,0.17447]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5450.0,"contact_point_centroid":[0.45012,-0.04417,0.09264],"force_p95":0.08978,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27051,"mean_force":0.05655,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44948,-0.02512,0.09187]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4922.0,"contact_point_centroid":[0.45038,-0.006,0.09321],"force_p95":0.09618,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26876,"mean_force":0.0613,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44953,-0.02513,0.09254]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45859,-0.02624,-0.0021],"force_p95":0.15157,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20708,"mean_force":0.13019,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.44927,-0.02516,0.04993]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4098.0,"contact_point_centroid":[0.44913,-0.0059,0.04957],"force_p95":0.07933,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14699,"mean_force":0.05218,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.44825,-0.02512,0.04895]},{"body_a":"world","body_b":"grasp_target","contact_count":952.0,"contact_point_centroid":[0.45856,-0.02632,-0.00186],"force_p95":0.13699,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12314,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48136,-0.01058,0.23556]},{"body_a":"world","body_b":"grasp_target","contact_count":876.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.45842,-0.02362,0.11336]},{"body_a":"world","body_b":"grasp_target","contact_count":948.0,"contact_point_centroid":[0.54701,0.10802,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62071,0.19951,0.18712]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54701,0.10802,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61869,0.20258,0.11517]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4960.0,"contact_point_centroid":[0.4483,-0.04421,0.04976],"force_p95":0.0711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07325,"mean_force":0.04411,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.44826,-0.02512,0.04895]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1250.0,"contact_point_centroid":[0.58116,0.14548,0.24807],"force_p95":0.01184,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01512,"mean_force":0.01049,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.58091,0.14548,0.24577]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1002.0,"contact_point_centroid":[0.62083,0.1995,0.1897],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01277,"mean_force":0.01054,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62069,0.19949,0.18747]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.62199,0.20373,0.11386],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.011,"mean_force":0.00998,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62166,0.20371,0.11132]}],"total_contact_groups":16},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.54701,0.10802,0.01602],"final_tcp_position":[0.62425,0.20449,0.11678],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.88176,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":239.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":952.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_grasp","tcp_end":[0.46241,-0.022,0.16889],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14298,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":219.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":876.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45589,-0.02538,0.05671],"tcp_start":[0.46241,-0.022,0.16889],"tcp_to_object_dist_end":0.03082,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45851,-0.02547,0.02563],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30314,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14879,"phase_name":"close_gripper","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10858.0,"raw_peak_contact_force":0.20708,"tcp_end":[0.44823,-0.02511,0.04892],"tcp_start":[0.45589,-0.02538,0.05671],"tcp_to_object_dist_end":0.02547,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":273.0,"n_steps_budget":690.0,"object_pos_end":[0.46766,-0.02565,0.11213],"object_pos_start":[0.45851,-0.02547,0.02563],"object_to_goal_dist_end":0.28477,"object_to_goal_dist_start":0.30314,"object_z_max":0.11185,"peak_contact_force":0.09791,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10446.0,"raw_peak_contact_force":0.36548,"subtask_id":"approach_grasp","tcp_end":[0.45363,-0.02525,0.13727],"tcp_start":[0.44823,-0.02511,0.04892],"tcp_to_object_dist_end":0.02878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":700.0,"n_steps_budget":1000.0,"object_pos_end":[0.54701,0.10802,0.01602],"object_pos_start":[0.46766,-0.02565,0.11213],"object_to_goal_dist_end":0.16301,"object_to_goal_dist_start":0.28477,"object_z_max":0.17259,"peak_contact_force":0.12263,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8957.0,"raw_peak_contact_force":1.88176,"subtask_id":"place_at_goal","tcp_end":[0.61858,0.19522,0.25443],"tcp_start":[0.45363,-0.02525,0.13727],"tcp_to_object_dist_end":0.26375,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":237.0,"n_steps_budget":1000.0,"object_pos_end":[0.54701,0.10802,0.01602],"object_pos_start":[0.54701,0.10802,0.01602],"object_to_goal_dist_end":0.16301,"object_to_goal_dist_start":0.16301,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1950.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62425,0.20449,0.11678],"tcp_start":[0.61858,0.19522,0.25443],"tcp_to_object_dist_end":0.15945,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54701,0.10802,0.01602],"object_pos_start":[0.54701,0.10802,0.01602],"object_to_goal_dist_end":0.16301,"object_to_goal_dist_start":0.16301,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61683,0.20188,0.13462],"tcp_start":[0.62425,0.20449,0.11678],"tcp_to_object_dist_end":0.16658,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.2126,"average_solve_count":127.0,"average_success_count":127.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.46932,"descend_to_object.grasp_offset_z":0.01002,"descend_to_place.place_offset_z":-0.01499,"lift_object.lift_offset_z":0.14476,"move_to_goal.goal_speed":0.34823},"optimized_scores":{"best_composite_score":0.17737,"best_fitness_score":0.57737,"best_task_score":0.22704},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1946.0,"contact_point_centroid":[0.57393,0.04253,-0.00246],"force_p95":0.21702,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.84065,"mean_force":0.1492,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.59588,0.08591,0.27635]},{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.54268,0.00056,-0.00134],"force_p95":0.35328,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40971,"mean_force":0.07497,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52862,0.00084,0.04549]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1099.0,"contact_point_centroid":[0.5484,0.02624,0.16612],"force_p95":0.16737,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34256,"mean_force":0.09832,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.5421,0.00782,0.16634]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5131.0,"contact_point_centroid":[0.53535,-0.01805,0.09387],"force_p95":0.11422,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2884,"mean_force":0.07622,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53191,0.00077,0.09177]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":967.0,"contact_point_centroid":[0.5483,-0.01039,0.16726],"force_p95":0.18439,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28098,"mean_force":0.10828,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.5422,0.00806,0.16682]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5236.0,"contact_point_centroid":[0.53522,0.01956,0.09258],"force_p95":0.11306,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27304,"mean_force":0.07506,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53181,0.00077,0.09052]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00104,-0.00203],"force_p95":0.132,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15376,"mean_force":0.12535,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.53081,0.00089,0.0456]},{"body_a":"world","body_b":"grasp_target","contact_count":1004.0,"contact_point_centroid":[0.54431,0.00113,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12311,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51606,0.00045,0.23431]},{"body_a":"world","body_b":"grasp_target","contact_count":840.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.53548,0.00096,0.11142]},{"body_a":"world","body_b":"grasp_target","contact_count":888.0,"contact_point_centroid":[0.57376,0.04255,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64095,0.15125,0.26287]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57376,0.04255,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.63873,0.15402,0.19346]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4124.0,"contact_point_centroid":[0.53062,-0.01833,0.04695],"force_p95":0.07629,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10074,"mean_force":0.05172,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.52964,0.00087,0.04422]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4869.0,"contact_point_centroid":[0.53059,0.01994,0.04609],"force_p95":0.06833,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09365,"mean_force":0.04475,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.52964,0.00087,0.04422]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1837.0,"contact_point_centroid":[0.60031,0.09192,0.2854],"force_p95":0.01137,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01645,"mean_force":0.01065,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.60013,0.09191,0.28309]},{"body_a":"left_finger","body_b":"right_finger","contact_count":933.0,"contact_point_centroid":[0.64121,0.15127,0.26509],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0127,"mean_force":0.01059,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64095,0.15126,0.2628]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.64159,0.1548,0.19224],"force_p95":0.01091,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01092,"mean_force":0.01,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.64114,0.15477,0.18991]}],"total_contact_groups":16},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.57376,0.04255,0.01602],"final_tcp_position":[0.64313,0.15522,0.19523],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273006.00684,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":252.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1004.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_grasp","tcp_end":[0.53434,0.00092,0.16718],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14151,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":210.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":52.01391,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":840.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53834,0.00102,0.05489],"tcp_start":[0.53434,0.00092,0.16718],"tcp_to_object_dist_end":0.02948,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54421,0.00077,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25048,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13045,"phase_name":"close_gripper","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15376,"tcp_end":[0.52961,0.00087,0.04418],"tcp_start":[0.53834,0.00102,0.05489],"tcp_to_object_dist_end":0.02342,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":372.0,"n_steps_budget":810.0,"object_pos_end":[0.55457,0.00087,0.12837],"object_pos_start":[0.54421,0.00077,0.02587],"object_to_goal_dist_end":0.19316,"object_to_goal_dist_start":0.25048,"object_z_max":0.12812,"peak_contact_force":0.11172,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10446.0,"raw_peak_contact_force":0.40971,"subtask_id":"approach_grasp","tcp_end":[0.53885,0.00072,0.15161],"tcp_start":[0.52961,0.00087,0.04418],"tcp_to_object_dist_end":0.02806,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":687.0,"n_steps_budget":1000.0,"object_pos_end":[0.57376,0.04255,0.01602],"object_pos_start":[0.55457,0.00087,0.12837],"object_to_goal_dist_end":0.22239,"object_to_goal_dist_start":0.19316,"object_z_max":0.1583,"peak_contact_force":9748.84765,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5849.0,"raw_peak_contact_force":1.84065,"subtask_id":"place_at_goal","tcp_end":[0.63932,0.14766,0.32631],"tcp_start":[0.53885,0.00072,0.15161],"tcp_to_object_dist_end":0.33411,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":222.0,"n_steps_budget":1000.0,"object_pos_end":[0.57376,0.04255,0.01602],"object_pos_start":[0.57376,0.04255,0.01602],"object_to_goal_dist_end":0.22239,"object_to_goal_dist_start":0.22239,"object_z_max":0.01602,"peak_contact_force":273006.00684,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1821.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.64313,0.15522,0.19523],"tcp_start":[0.63932,0.14766,0.32631],"tcp_to_object_dist_end":0.22276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57376,0.04255,0.01602],"object_pos_start":[0.57376,0.04255,0.01602],"object_to_goal_dist_end":0.22239,"object_to_goal_dist_start":0.22239,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63729,0.15357,0.21275],"tcp_start":[0.64313,0.15522,0.19523],"tcp_to_object_dist_end":0.23466,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.06195,"average_solve_count":113.0,"average_success_count":113.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.35531,"descend_to_object.grasp_offset_z":0.01964,"descend_to_place.place_offset_z":0.00828,"lift_object.lift_offset_z":0.08074,"move_to_goal.goal_speed":0.40786},"optimized_scores":{"best_composite_score":0.05877,"best_fitness_score":0.45877,"best_task_score":0.51366},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":603.0,"contact_point_centroid":[0.59172,0.14081,-0.00369],"force_p95":0.78586,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.60806,"mean_force":0.20226,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.58191,0.14553,0.2314]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3586.0,"contact_point_centroid":[0.54055,0.04138,0.13711],"force_p95":0.13447,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30169,"mean_force":0.0973,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.5363,0.05968,0.14039]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1386.0,"contact_point_centroid":[0.52059,0.01048,0.06786],"force_p95":0.13337,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27495,"mean_force":0.10102,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51898,0.02904,0.07059]},{"body_a":"world","body_b":"grasp_target","contact_count":101.0,"contact_point_centroid":[0.52981,0.02857,-0.00144],"force_p95":0.24144,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26483,"mean_force":0.05295,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51623,0.02895,0.05595]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1532.0,"contact_point_centroid":[0.51985,0.04746,0.06717],"force_p95":0.13073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25705,"mean_force":0.0944,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51897,0.02904,0.07056]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53056,0.03069,-0.00213],"force_p95":0.16134,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21502,"mean_force":0.13199,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.51793,0.02908,0.05586]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3588.0,"contact_point_centroid":[0.54182,0.0803,0.14012],"force_p95":0.13191,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19319,"mean_force":0.09773,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.53753,0.06199,0.14367]},{"body_a":"world","body_b":"grasp_target","contact_count":992.0,"contact_point_centroid":[0.5305,0.03079,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12312,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51044,0.01247,0.23436]},{"body_a":"world","body_b":"grasp_target","contact_count":776.0,"contact_point_centroid":[0.5919,0.14095,-0.00199],"force_p95":0.12279,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12316,"mean_force":0.12261,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5943,0.17082,0.1913]},{"body_a":"world","body_b":"grasp_target","contact_count":776.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.52308,0.02761,0.11655]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5919,0.14095,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59109,0.17344,0.13456]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2434.0,"contact_point_centroid":[0.51835,0.01033,0.0518],"force_p95":0.1045,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11766,"mean_force":0.082,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.5168,0.02901,0.05455]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2824.0,"contact_point_centroid":[0.51785,0.04769,0.05121],"force_p95":0.10026,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10039,"mean_force":0.07325,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.51681,0.02901,0.05455]},{"body_a":"left_finger","body_b":"right_finger","contact_count":417.0,"contact_point_centroid":[0.58617,0.15305,0.2387],"force_p95":0.01364,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01608,"mean_force":0.01098,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.58593,0.15303,0.23635]},{"body_a":"left_finger","body_b":"right_finger","contact_count":839.0,"contact_point_centroid":[0.5945,0.1708,0.19417],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01261,"mean_force":0.01032,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59429,0.17078,0.19181]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.59442,0.17443,0.13248],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01102,"mean_force":0.01015,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5939,0.1744,0.13015]}],"total_contact_groups":16},"final_pose_error":0.01964,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.5919,0.14095,0.01602],"final_tcp_position":[0.59628,0.17501,0.13495],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":9748.81847,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":249.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":992.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_grasp","tcp_end":[0.52269,0.02582,0.16733],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14161,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":194.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":776.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52518,0.02953,0.06475],"tcp_start":[0.52269,0.02582,0.16733],"tcp_to_object_dist_end":0.03912,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53047,0.02964,0.02557],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18451,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15568,"phase_name":"close_gripper","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7058.0,"raw_peak_contact_force":0.21502,"tcp_end":[0.51677,0.029,0.05451],"tcp_start":[0.52518,0.02953,0.06475],"tcp_to_object_dist_end":0.03202,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":135.0,"n_steps_budget":600.0,"object_pos_end":[0.53258,0.02958,0.05653],"object_pos_start":[0.53047,0.02964,0.02557],"object_to_goal_dist_end":0.17208,"object_to_goal_dist_start":0.18451,"object_z_max":0.0563,"peak_contact_force":0.10787,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3019.0,"raw_peak_contact_force":0.27495,"subtask_id":"approach_grasp","tcp_end":[0.52305,0.0292,0.08798],"tcp_start":[0.51677,0.029,0.05451],"tcp_to_object_dist_end":0.03286,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":616.0,"n_steps_budget":1000.0,"object_pos_end":[0.59191,0.14096,0.016],"object_pos_start":[0.53258,0.02958,0.05653],"object_to_goal_dist_end":0.09994,"object_to_goal_dist_start":0.17208,"object_z_max":0.15785,"peak_contact_force":9748.81847,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8194.0,"raw_peak_contact_force":1.60806,"subtask_id":"place_at_goal","tcp_end":[0.59326,0.16705,0.2443],"tcp_start":[0.52305,0.0292,0.08798],"tcp_to_object_dist_end":0.22979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":194.0,"n_steps_budget":1000.0,"object_pos_end":[0.5919,0.14095,0.01602],"object_pos_start":[0.59191,0.14096,0.016],"object_to_goal_dist_end":0.09993,"object_to_goal_dist_start":0.09994,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1615.0,"raw_peak_contact_force":0.12316,"tcp_end":[0.59628,0.17501,0.13495],"tcp_start":[0.59326,0.16705,0.2443],"tcp_to_object_dist_end":0.12379,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5919,0.14095,0.01602],"object_pos_start":[0.5919,0.14095,0.01602],"object_to_goal_dist_end":0.09993,"object_to_goal_dist_start":0.09993,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58935,0.17285,0.15445],"tcp_start":[0.59628,0.17501,0.13495],"tcp_to_object_dist_end":0.14208,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```