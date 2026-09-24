## Search State

- **Seed**: 3
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | 7 | 0.2215 | 0.49 | ✅ accepted |
| 2 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | 5 | 0.2342 | 0.20 | ❌ rejected |
| 1 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | 5 | 0.2342 | 0.20 | ❌ rejected |
| 0 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | 5 | 0.2349 | 0.20 | ✅ accepted |

**Proposal policy**: task_score is 0.49 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.222) — your mutation base

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
  - 0.1
  weight: 0.2
- id: grasp_object
  anchor: object
  target_entity: object
  weight: 0.2
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.1
- id: transport_to_goal
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: place_at_goal
  target_entity: object
  weight: 0.3
phases:
- id: approach_1
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: grasp_object
- id: grasp_1
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
    orientation:
      mode: keep_current
  subtask_id: grasp_object
- id: lift_1
  type: lift
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
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: lift_object
- id: transport_1
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
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    transport_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: transport_to_goal
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
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
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal
- id: release_1
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
    orientation:
      mode: keep_current
  subtask_id: place_at_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
    - transport_height: status=consumed; consumers=target.offset.z (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.222
- **task_score** (E): 0.487
- **fitness_score**: 0.722  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.500

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1575 |
| descend_1 | 1.00 | 1.00 | 0.1139 |
| grasp_1 | 1.00 | 1.00 | 0.0119 |
| lift_1 | 1.00 | 1.00 | 0.1733 |
| transport_1 | 1.00 | 1.00 | 0.2378 |
| descend_2 | 1.00 | 1.00 | 0.1641 |
| release_1 | 1.00 | 1.00 | 0.0205 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.148) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.002, 0.148)→(0.505, 0.002, 0.034) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.505, 0.002, 0.034)→(0.497, 0.001, 0.026) | (0.511, 0.002, 0.026)→(0.511, 0.001, 0.026) | 0.246→0.246 | 1.00 / 42.333 | 0.140 | 0.198 |
| lift_1 | lift | 1.00 / step_budget | (0.497, 0.001, 0.026)→(0.507, 0.001, 0.199) | (0.511, 0.001, 0.026)→(0.519, 0.001, 0.193) | 0.246→0.225 | 1.00 / 37.667 | 0.081 | 0.615 |
| transport_1 | approach | 1.00 / step_budget | (0.507, 0.001, 0.199)→(0.615, 0.167, 0.301) | (0.519, 0.001, 0.193)→(0.626, 0.167, 0.287) | 0.225→0.150 | 1.00 / 31.667 | 0.096 | 0.116 |
| descend_2 | descend | 1.00 / step_budget | (0.615, 0.167, 0.301)→(0.622, 0.179, 0.137) | (0.626, 0.167, 0.287)→(0.614, 0.179, 0.119) | 0.150→0.023 | 1.00 / 44.333 | 0.069 | 0.174 |
| release_1 | release | 1.00 / step_budget | (0.622, 0.179, 0.137)→(0.615, 0.177, 0.157) | (0.614, 0.179, 0.119)→(0.616, 0.177, 0.026) | 0.023→0.112 | 1.00 / 2.000 | 0.212 | 1.309 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.579
- phase_score: 0.597
- phase_breakdown.place_at_goal_score: 0.621
- phase_breakdown.transport_to_goal_score: 0.459
- phase_breakdown.reach_object_score: 0.671
- phase_breakdown.grasp_object_score: 0.748
- phase_breakdown.lift_object_score: 0.346
- grasp_place_fitness: 0.766

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.766
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.579
- **Median Q (composite search score)**: 0.257
- **K-run variance**: 0.0032
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.342


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.19505,"average_solve_count":364.0,"average_success_count":364.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0514,"descend_1.speed":0.05684,"descend_2.speed":0.09999,"lift_1.lift_height":0.27497,"lift_1.speed":0.04432,"transport_1.speed":0.06623,"transport_1.transport_height":0.19517},"optimized_scores":{"best_composite_score":0.25679,"best_fitness_score":0.75679,"best_task_score":0.5535},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":182.0,"contact_point_centroid":[0.60589,0.20724,-0.00634],"force_p95":0.90756,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.13035,"mean_force":0.37453,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61829,0.2036,0.11859]},{"body_a":"world","body_b":"grasp_target","contact_count":81.0,"contact_point_centroid":[0.45581,-0.02561,-0.00141],"force_p95":0.66033,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72387,"mean_force":0.20514,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44578,-0.02564,0.02247]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17989.0,"contact_point_centroid":[0.44888,-0.0447,0.15126],"force_p95":0.0722,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27358,"mean_force":0.04959,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4491,-0.02553,0.14981]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17991.0,"contact_point_centroid":[0.44903,-0.00635,0.15495],"force_p95":0.07131,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27082,"mean_force":0.04926,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44927,-0.02553,0.15319]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45856,-0.02613,-0.00205],"force_p95":0.13812,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19147,"mean_force":0.12702,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44788,-0.02571,0.02244]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20669.0,"contact_point_centroid":[0.62245,0.18288,0.17521],"force_p95":0.07658,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17463,"mean_force":0.04987,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62244,0.20211,0.17277]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21003.0,"contact_point_centroid":[0.6227,0.22068,0.18259],"force_p95":0.07057,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16274,"mean_force":0.04802,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62213,0.20163,0.18039]},{"body_a":"world","body_b":"grasp_target","contact_count":1232.0,"contact_point_centroid":[0.45856,-0.02632,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48087,-0.01074,0.22641]},{"body_a":"world","body_b":"grasp_target","contact_count":3000.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45617,-0.02417,0.08592]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14714.0,"contact_point_centroid":[0.53571,0.06439,0.28918],"force_p95":0.08495,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12084,"mean_force":0.05579,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53525,0.08353,0.28833]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15821.0,"contact_point_centroid":[0.5383,0.10571,0.28936],"force_p95":0.07615,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10963,"mean_force":0.05181,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53761,0.08671,0.28861]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1284.0,"contact_point_centroid":[0.62394,0.22472,0.1118],"force_p95":0.07181,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09996,"mean_force":0.04135,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62307,0.20537,0.10878]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4811.0,"contact_point_centroid":[0.44679,-0.00647,0.02377],"force_p95":0.06767,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09232,"mean_force":0.04484,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44678,-0.02567,0.02141]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1437.0,"contact_point_centroid":[0.62314,0.1862,0.11203],"force_p95":0.06404,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08815,"mean_force":0.0373,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62311,0.20538,0.10885]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5172.0,"contact_point_centroid":[0.44664,-0.04491,0.02326],"force_p95":0.06645,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08664,"mean_force":0.04305,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44678,-0.02567,0.02141]}],"total_contact_groups":15},"final_pose_error":0.00579,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62122,0.20419,0.02594],"final_tcp_position":[0.625,0.20603,0.11254],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.13035,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":309.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1232.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.46146,-0.02245,0.14935],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12342,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":750.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3000.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.45426,-0.02594,0.02844],"tcp_start":[0.46146,-0.02245,0.14935],"tcp_to_object_dist_end":0.00495,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45842,-0.02566,0.02582],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30328,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13548,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11783.0,"raw_peak_contact_force":0.19147,"subtask_id":"grasp_object","tcp_end":[0.44675,-0.02567,0.02138],"tcp_start":[0.45426,-0.02594,0.02844],"tcp_to_object_dist_end":0.01248,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":859.0,"n_steps_budget":1000.0,"object_pos_end":[0.46821,-0.02568,0.27793],"object_pos_start":[0.45842,-0.02566,0.02582],"object_to_goal_dist_end":0.32827,"object_to_goal_dist_start":0.30328,"object_z_max":0.27766,"peak_contact_force":0.07781,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36061.0,"raw_peak_contact_force":0.72387,"subtask_id":"lift_object","tcp_end":[0.45537,-0.02555,0.28129],"tcp_start":[0.44675,-0.02567,0.02138],"tcp_to_object_dist_end":0.01327,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":803.0,"n_steps_budget":1000.0,"object_pos_end":[0.62974,0.19504,0.2873],"object_pos_start":[0.46821,-0.02568,0.27793],"object_to_goal_dist_end":0.17368,"object_to_goal_dist_start":0.32827,"object_z_max":0.28731,"peak_contact_force":0.09155,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":30535.0,"raw_peak_contact_force":0.12084,"subtask_id":"transport_to_goal","tcp_end":[0.61905,0.19502,0.29915],"tcp_start":[0.45537,-0.02555,0.28129],"tcp_to_object_dist_end":0.01596,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61491,0.20577,0.09422],"object_pos_start":[0.62974,0.19504,0.2873],"object_to_goal_dist_end":0.02518,"object_to_goal_dist_start":0.17368,"object_z_max":0.2873,"peak_contact_force":0.07175,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":41672.0,"raw_peak_contact_force":0.17463,"subtask_id":"place_at_goal","tcp_end":[0.625,0.20603,0.11254],"tcp_start":[0.61905,0.19502,0.29915],"tcp_to_object_dist_end":0.02092,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62122,0.20419,0.02594],"object_pos_start":[0.61491,0.20577,0.09422],"object_to_goal_dist_end":0.08872,"object_to_goal_dist_start":0.02518,"object_z_max":0.09422,"peak_contact_force":0.20635,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2903.0,"raw_peak_contact_force":1.13035,"subtask_id":"place_at_goal","tcp_end":[0.61814,0.20354,0.13166],"tcp_start":[0.625,0.20603,0.11254],"tcp_to_object_dist_end":0.10577,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.00694,"average_solve_count":432.0,"average_success_count":432.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.02856,"descend_1.speed":0.09582,"descend_2.speed":0.06143,"lift_1.lift_height":0.18083,"lift_1.speed":0.03218,"transport_1.speed":0.03679,"transport_1.transport_height":0.22835},"optimized_scores":{"best_composite_score":0.14147,"best_fitness_score":0.64147,"best_task_score":0.32999},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":155.0,"contact_point_centroid":[0.6222,0.15875,-0.00845],"force_p95":1.30459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.72459,"mean_force":0.48242,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63775,0.15439,0.20059]},{"body_a":"world","body_b":"grasp_target","contact_count":98.0,"contact_point_centroid":[0.54028,0.00072,-0.00148],"force_p95":0.49892,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53201,"mean_force":0.21012,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52835,0.00083,0.02793]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11212.0,"contact_point_centroid":[0.5333,-0.01837,0.10909],"force_p95":0.0801,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25698,"mean_force":0.05637,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53249,0.00073,0.10673]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11640.0,"contact_point_centroid":[0.533,0.01979,0.10587],"force_p95":0.07825,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24946,"mean_force":0.0549,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53224,0.00073,0.10371]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14424.0,"contact_point_centroid":[0.63905,0.16647,0.28238],"force_p95":0.07944,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19477,"mean_force":0.05283,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.63818,0.14734,0.2808]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15486.0,"contact_point_centroid":[0.63907,0.12838,0.28094],"force_p95":0.07702,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18179,"mean_force":0.05022,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.63828,0.14752,0.27906]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00099,-0.00203],"force_p95":0.13194,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15886,"mean_force":0.12531,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53068,0.00088,0.02862]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1265.0,"contact_point_centroid":[0.64175,0.17489,0.1904],"force_p95":0.07097,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15403,"mean_force":0.0424,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64151,0.15555,0.18798]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1385.0,"contact_point_centroid":[0.64138,0.13638,0.19062],"force_p95":0.06746,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15188,"mean_force":0.03902,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64153,0.15556,0.18802]},{"body_a":"world","body_b":"grasp_target","contact_count":1320.0,"contact_point_centroid":[0.54431,0.00113,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.123,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51576,0.00044,0.2256]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53513,0.00096,0.0796]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53059,-0.01834,0.02985],"force_p95":0.0761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11346,"mean_force":0.05172,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52942,0.00086,0.02718]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15636.0,"contact_point_centroid":[0.58631,0.08789,0.28264],"force_p95":0.09038,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1054,"mean_force":0.06273,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58442,0.06888,0.28115]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17701.0,"contact_point_centroid":[0.58669,0.0507,0.28321],"force_p95":0.08343,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10335,"mean_force":0.05605,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58491,0.06956,0.28215]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53051,0.01994,0.02898],"force_p95":0.06814,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09622,"mean_force":0.04478,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52942,0.00086,0.02718]}],"total_contact_groups":15},"final_pose_error":0.00498,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.62927,0.1535,0.02588],"final_tcp_position":[0.64326,0.15598,0.19226],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.72459,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":331.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1320.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53474,0.00093,0.1472],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12156,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.53782,0.00101,0.03691],"tcp_start":[0.53474,0.00093,0.1472],"tcp_to_object_dist_end":0.01267,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54416,0.00073,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25052,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.1299,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15886,"subtask_id":"grasp_object","tcp_end":[0.52939,0.00086,0.02714],"tcp_start":[0.53782,0.00101,0.03691],"tcp_to_object_dist_end":0.01482,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":612.0,"n_steps_budget":1000.0,"object_pos_end":[0.55176,0.0007,0.18017],"object_pos_start":[0.54416,0.00073,0.02588],"object_to_goal_dist_end":0.1846,"object_to_goal_dist_start":0.25052,"object_z_max":0.17992,"peak_contact_force":0.08176,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22950.0,"raw_peak_contact_force":0.53201,"subtask_id":"lift_object","tcp_end":[0.53953,0.00068,0.18729],"tcp_start":[0.52939,0.00086,0.02714],"tcp_to_object_dist_end":0.01415,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.64268,0.13891,0.36612],"object_pos_start":[0.55176,0.0007,0.18017],"object_to_goal_dist_end":0.17613,"object_to_goal_dist_start":0.1846,"object_z_max":0.36591,"peak_contact_force":0.1054,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":33337.0,"raw_peak_contact_force":0.1054,"subtask_id":"transport_to_goal","tcp_end":[0.63354,0.1385,0.38223],"tcp_start":[0.53953,0.00068,0.18729],"tcp_to_object_dist_end":0.01853,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":729.0,"n_steps_budget":1000.0,"object_pos_end":[0.63337,0.15549,0.17221],"object_pos_start":[0.64268,0.13891,0.36612],"object_to_goal_dist_end":0.02381,"object_to_goal_dist_start":0.17613,"object_z_max":0.36621,"peak_contact_force":0.07126,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":29910.0,"raw_peak_contact_force":0.19477,"subtask_id":"place_at_goal","tcp_end":[0.64326,0.15598,0.19226],"tcp_start":[0.63354,0.1385,0.38223],"tcp_to_object_dist_end":0.02236,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62927,0.1535,0.02588],"object_pos_start":[0.63337,0.15549,0.17221],"object_to_goal_dist_end":0.1663,"object_to_goal_dist_start":0.02381,"object_z_max":0.17221,"peak_contact_force":0.24211,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2805.0,"raw_peak_contact_force":1.72459,"subtask_id":"place_at_goal","tcp_end":[0.63771,0.15438,0.21066],"tcp_start":[0.64326,0.15598,0.19226],"tcp_to_object_dist_end":0.18497,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4065,"average_solve_count":246.0,"average_success_count":246.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04539,"descend_1.speed":0.07662,"descend_2.speed":0.07685,"lift_1.lift_height":0.12068,"lift_1.speed":0.04799,"transport_1.speed":0.07255,"transport_1.transport_height":0.12821},"optimized_scores":{"best_composite_score":0.26637,"best_fitness_score":0.76637,"best_task_score":0.57884},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":183.0,"contact_point_centroid":[0.58249,0.17565,-0.00618],"force_p95":0.86753,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.07293,"mean_force":0.36765,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58964,0.1743,0.11494]},{"body_a":"world","body_b":"grasp_target","contact_count":93.0,"contact_point_centroid":[0.52646,0.02873,-0.00151],"force_p95":0.55999,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58899,"mean_force":0.18773,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51528,0.02919,0.02953]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7624.0,"contact_point_centroid":[0.5191,0.04807,0.07793],"force_p95":0.07835,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29352,"mean_force":0.05282,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51868,0.02903,0.07598]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6584.0,"contact_point_centroid":[0.51916,0.00984,0.0781],"force_p95":0.08405,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28429,"mean_force":0.05884,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51862,0.02903,0.07529]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53056,0.03048,-0.00214],"force_p95":0.16355,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2442,"mean_force":0.13345,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51741,0.02935,0.02972]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18983.0,"contact_point_centroid":[0.59411,0.15418,0.14582],"force_p95":0.077,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15162,"mean_force":0.05259,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59447,0.1734,0.14363]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21485.0,"contact_point_centroid":[0.59437,0.19228,0.1471],"force_p95":0.06845,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14941,"mean_force":0.04639,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59438,0.17326,0.14527]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4057.0,"contact_point_centroid":[0.51717,0.01007,0.03108],"force_p95":0.08118,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14815,"mean_force":0.05192,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51618,0.02927,0.02834]},{"body_a":"world","body_b":"grasp_target","contact_count":1280.0,"contact_point_centroid":[0.5305,0.03079,-0.0019],"force_p95":0.13566,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51018,0.01259,0.22543]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11638.0,"contact_point_centroid":[0.55829,0.07839,0.17306],"force_p95":0.08288,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12299,"mean_force":0.05461,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55698,0.09739,0.1712]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52244,0.02841,0.07758]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1349.0,"contact_point_centroid":[0.59416,0.1951,0.10649],"force_p95":0.06486,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11709,"mean_force":0.03891,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5944,0.17585,0.10408]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1275.0,"contact_point_centroid":[0.59398,0.15661,0.10699],"force_p95":0.06528,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10824,"mean_force":0.04056,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5944,0.17585,0.10407]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10913.0,"contact_point_centroid":[0.5604,0.12037,0.17583],"force_p95":0.08075,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09805,"mean_force":0.05715,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.559,0.10131,0.17396]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5010.0,"contact_point_centroid":[0.51708,0.04844,0.03013],"force_p95":0.0738,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08601,"mean_force":0.04472,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51619,0.02927,0.02835]}],"total_contact_groups":15},"final_pose_error":0.00559,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59733,0.17472,0.02628],"final_tcp_position":[0.59639,0.17645,0.10755],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.07293,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":321.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1280.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52279,0.02628,0.14783],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12214,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.52437,0.02981,0.03759],"tcp_start":[0.52279,0.02628,0.14783],"tcp_to_object_dist_end":0.01313,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5304,0.02931,0.02554],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18481,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15491,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10867.0,"raw_peak_contact_force":0.2442,"subtask_id":"grasp_object","tcp_end":[0.51615,0.02927,0.02831],"tcp_start":[0.52437,0.02981,0.03759],"tcp_to_object_dist_end":0.01451,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":372.0,"n_steps_budget":1000.0,"object_pos_end":[0.53728,0.02894,0.1211],"object_pos_start":[0.5304,0.02931,0.02554],"object_to_goal_dist_end":0.16337,"object_to_goal_dist_start":0.18481,"object_z_max":0.12085,"peak_contact_force":0.08348,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14301.0,"raw_peak_contact_force":0.58899,"subtask_id":"lift_object","tcp_end":[0.5248,0.02904,0.12726],"tcp_start":[0.51615,0.02927,0.02831],"tcp_to_object_dist_end":0.01392,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":627.0,"n_steps_budget":1000.0,"object_pos_end":[0.6041,0.16811,0.20838],"object_pos_start":[0.53728,0.02894,0.1211],"object_to_goal_dist_end":0.10087,"object_to_goal_dist_start":0.16337,"object_z_max":0.20826,"peak_contact_force":0.09029,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22551.0,"raw_peak_contact_force":0.12299,"subtask_id":"transport_to_goal","tcp_end":[0.59368,0.16826,0.22133],"tcp_start":[0.5248,0.02904,0.12726],"tcp_to_object_dist_end":0.01663,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59285,0.1762,0.08979],"object_pos_start":[0.6041,0.16811,0.20838],"object_to_goal_dist_end":0.0204,"object_to_goal_dist_start":0.10087,"object_z_max":0.20841,"peak_contact_force":0.06547,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":40468.0,"raw_peak_contact_force":0.15162,"subtask_id":"place_at_goal","tcp_end":[0.59639,0.17645,0.10755],"tcp_start":[0.59368,0.16826,0.22133],"tcp_to_object_dist_end":0.01811,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59733,0.17472,0.02628],"object_pos_start":[0.59285,0.1762,0.08979],"object_to_goal_dist_end":0.08201,"object_to_goal_dist_start":0.0204,"object_z_max":0.08979,"peak_contact_force":0.18703,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2807.0,"raw_peak_contact_force":1.07293,"subtask_id":"place_at_goal","tcp_end":[0.58947,0.17425,0.12812],"tcp_start":[0.59639,0.17645,0.10755],"tcp_to_object_dist_end":0.10215,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```