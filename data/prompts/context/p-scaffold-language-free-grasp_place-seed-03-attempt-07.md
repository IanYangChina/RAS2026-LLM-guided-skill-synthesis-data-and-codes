## Search State

- **Seed**: 3
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.2455 | 0.46 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.2493 | 0.46 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | 0.1512 | 0.46 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | 7 | 0.2125 | 0.47 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | 7 | 0.2215 | 0.49 | ✅ accepted |

**Proposal policy**: task_score is 0.46 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.246) — your mutation base

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

- **Composite score**: 0.246
- **task_score** (E): 0.456
- **fitness_score**: 0.696  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.450

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1576 |
| descend_1 | 1.00 | 1.00 | 0.1020 |
| grasp_1 | 1.00 | 1.00 | 0.0118 |
| lift_1 | 1.00 | 1.00 | 0.1290 |
| transport_1 | 1.00 | 0.67 | 0.2003 |
| descend_2 | 0.33 | 1.00 | 0.1184 |
| release_1 | 1.00 | 1.00 | 0.0231 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.148) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 11.892 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.002, 0.148)→(0.505, 0.001, 0.046) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.505, 0.001, 0.046)→(0.497, 0.001, 0.037) | (0.511, 0.002, 0.026)→(0.511, 0.001, 0.026) | 0.246→0.246 | 1.00 / 40.667 | 0.147 | 0.191 |
| lift_1 | lift | 1.00 / step_budget | (0.497, 0.001, 0.037)→(0.506, 0.001, 0.166) | (0.511, 0.001, 0.026)→(0.518, 0.002, 0.149) | 0.246→0.211 | 1.00 / 26.667 | 0.111 | 0.497 |
| transport_1 | approach | 1.00 / step_budget | (0.506, 0.001, 0.166)→(0.615, 0.168, 0.150) | (0.518, 0.002, 0.149)→(0.620, 0.166, 0.085) | 0.211→0.057 | 0.67 / 11.000 | 0.323 | 0.612 |
| descend_2 | descend | 0.33 / step_budget | (0.615, 0.168, 0.150)→(0.654, 0.148, 0.259) | (0.620, 0.166, 0.085)→(0.620, 0.171, 0.070) | 0.057→0.072 | 1.00 / 16.667 | 146.064 | 717.568 |
| release_1 | release | 1.00 / step_budget | (0.654, 0.148, 0.259)→(0.652, 0.148, 0.282) | (0.620, 0.171, 0.070)→(0.617, 0.170, 0.018) | 0.072→0.121 | 1.00 / 3.333 | 0.131 | 80.951 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.505
- phase_score: 0.366
- phase_breakdown.place_at_goal_score: 0.014
- phase_breakdown.grasp_object_score: 0.747
- phase_breakdown.reach_pregrasp_score: 0.676
- grasp_place_fitness: 0.733

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.733
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.539
- **Median Q (composite search score)**: 0.274
- **K-run variance**: 0.0022
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.274


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":4.0,"average_failure_rate":0.01778,"average_mean_iterations":7.38667,"average_solve_count":225.0,"average_success_count":221.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.098,"descend_1.speed":0.04792,"descend_2.speed":0.03435,"lift_1.lift_height":0.12095,"lift_1.speed":0.07197,"transport_1.speed":0.0764},"optimized_scores":{"best_composite_score":0.28276,"best_fitness_score":0.73276,"best_task_score":0.50523},"replay_outcomes":[{"contacts":{"omitted_contact_groups":8,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":358.0,"contact_point_centroid":[0.72684,0.13849,-0.00043],"force_p95":587.361,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1489.87975,"mean_force":310.48725,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.67881,0.17904,0.27197]},{"body_a":"world","body_b":"hand","contact_count":28.0,"contact_point_centroid":[0.68624,0.35721,-0.0043],"force_p95":1165.50296,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1270.61685,"mean_force":327.28205,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58658,0.3441,0.01261]},{"body_a":"world","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.67481,0.22403,-0.00061],"force_p95":249.80201,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":356.86001,"mean_force":50.98,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59828,0.35317,0.05313]},{"body_a":"world","body_b":"link6","contact_count":89.0,"contact_point_centroid":[0.72972,0.14444,-0.00015],"force_p95":84.87631,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":159.34765,"mean_force":54.6914,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.67584,0.14782,0.28955]},{"body_a":"world","body_b":"left_finger","contact_count":164.0,"contact_point_centroid":[0.58308,0.33154,-0.0038],"force_p95":35.73269,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":42.78554,"mean_force":13.08383,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58559,0.33588,-0.00205]},{"body_a":"world","body_b":"right_finger","contact_count":178.0,"contact_point_centroid":[0.5884,0.33652,-0.00405],"force_p95":32.82465,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":41.38646,"mean_force":11.84806,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58549,0.33632,-0.00168]},{"body_a":"grasp_target","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.64411,0.1974,0.03241],"force_p95":2.996,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.01837,"mean_force":2.26494,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59479,0.35122,0.04239]},{"body_a":"grasp_target","body_b":"link6","contact_count":283.0,"contact_point_centroid":[0.65633,0.16803,0.034],"force_p95":1.09602,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.65795,"mean_force":0.26058,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.6715,0.16766,0.26909]},{"body_a":"world","body_b":"grasp_target","contact_count":24.0,"contact_point_centroid":[0.62925,0.18672,-0.00458],"force_p95":1.34454,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.37071,"mean_force":0.92627,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.61681,0.19451,0.12514]},{"body_a":"world","body_b":"grasp_target","contact_count":1951.0,"contact_point_centroid":[0.62393,0.1758,-0.00262],"force_p95":0.38293,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.32402,"mean_force":0.16907,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.66838,0.20496,0.23107]},{"body_a":"world","body_b":"grasp_target","contact_count":75.0,"contact_point_centroid":[0.45648,-0.02561,-0.00138],"force_p95":0.62173,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73008,"mean_force":0.17196,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44588,-0.02564,0.02269]},{"body_a":"grasp_target","body_b":"link6","contact_count":149.0,"contact_point_centroid":[0.65478,0.17444,0.03534],"force_p95":0.22797,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37796,"mean_force":0.20541,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.67593,0.14797,0.29106]},{"body_a":"world","body_b":"grasp_target","contact_count":734.0,"contact_point_centroid":[0.62503,0.18097,-0.00242],"force_p95":0.28903,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.31553,"mean_force":0.15864,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.67604,0.14809,0.29464]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8903.0,"contact_point_centroid":[0.52955,0.05574,0.12388],"force_p95":0.13579,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29854,"mean_force":0.08915,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52569,0.0742,0.12464]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5419.0,"contact_point_centroid":[0.44967,-0.00648,0.07055],"force_p95":0.10721,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27849,"mean_force":0.06492,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44796,-0.02553,0.0681]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5912.0,"contact_point_centroid":[0.44965,-0.04448,0.06915],"force_p95":0.10354,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27537,"mean_force":0.06071,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44789,-0.02553,0.06745]}],"total_contact_groups":24},"final_pose_error":0.20048,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62436,0.17998,0.01585],"final_tcp_position":[0.67615,0.14779,0.28966],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1489.87975,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":294.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1172.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pregrasp","tcp_end":[0.46148,-0.0225,0.14899],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12307,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":749.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2996.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.45431,-0.02594,0.02852],"tcp_start":[0.46148,-0.0225,0.14899],"tcp_to_object_dist_end":0.00496,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45842,-0.02566,0.02582],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30328,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13545,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11782.0,"raw_peak_contact_force":0.19138,"subtask_id":"grasp_object","tcp_end":[0.4468,-0.02567,0.02147],"tcp_start":[0.45431,-0.02594,0.02852],"tcp_to_object_dist_end":0.01241,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":337.0,"n_steps_budget":1000.0,"object_pos_end":[0.47392,-0.02547,0.12773],"object_pos_start":[0.45842,-0.02566,0.02582],"object_to_goal_dist_end":0.28142,"object_to_goal_dist_start":0.30328,"object_z_max":0.12746,"peak_contact_force":0.11178,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11406.0,"raw_peak_contact_force":0.73008,"subtask_id":"place_at_goal","tcp_end":[0.45328,-0.02549,0.1275],"tcp_start":[0.4468,-0.02567,0.02147],"tcp_to_object_dist_end":0.02064,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":826.0,"n_steps_budget":1000.0,"object_pos_end":[0.62496,0.18185,0.00778],"object_pos_start":[0.47392,-0.02547,0.12773],"object_to_goal_dist_end":0.10968,"object_to_goal_dist_start":0.28142,"object_z_max":0.12802,"peak_contact_force":0.88261,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17589.0,"raw_peak_contact_force":1.37071,"subtask_id":"place_at_goal","tcp_end":[0.61769,0.19571,0.12513],"tcp_start":[0.45328,-0.02549,0.1275],"tcp_to_object_dist_end":0.11839,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":488.0,"n_steps_budget":1000.0,"object_pos_end":[0.62404,0.18096,0.01466],"object_pos_start":[0.62496,0.18185,0.00778],"object_to_goal_dist_end":0.10331,"object_to_goal_dist_start":0.10968,"object_z_max":0.01656,"peak_contact_force":212.30307,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4754.0,"raw_peak_contact_force":1489.87975,"subtask_id":"place_at_goal","tcp_end":[0.67615,0.14779,0.28966],"tcp_start":[0.61769,0.19571,0.12513],"tcp_to_object_dist_end":0.28185,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62436,0.17998,0.01585],"object_pos_start":[0.62404,0.18096,0.01466],"object_to_goal_dist_end":0.10241,"object_to_goal_dist_start":0.10331,"object_z_max":0.0171,"peak_contact_force":0.13495,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1198.0,"raw_peak_contact_force":159.34765,"subtask_id":"place_at_goal","tcp_end":[0.6765,0.14858,0.31351],"tcp_start":[0.67615,0.14779,0.28966],"tcp_to_object_dist_end":0.30382,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":25.0,"average_failure_rate":0.08741,"average_mean_iterations":20.37063,"average_solve_count":286.0,"average_success_count":261.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06306,"descend_1.speed":0.07894,"descend_2.speed":0.02471,"lift_1.lift_height":0.21824,"lift_1.speed":0.04338,"transport_1.speed":0.04761},"optimized_scores":{"best_composite_score":0.18013,"best_fitness_score":0.63013,"best_task_score":0.32383},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":114.0,"contact_point_centroid":[0.63273,0.14127,-0.01123],"force_p95":1.4082,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.47045,"mean_force":0.65854,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63033,0.14323,0.21382]},{"body_a":"world","body_b":"grasp_target","contact_count":91.0,"contact_point_centroid":[0.54066,0.00056,-0.00142],"force_p95":0.40791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43403,"mean_force":0.15125,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52785,0.00083,0.04025]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12886.0,"contact_point_centroid":[0.53361,-0.01834,0.13496],"force_p95":0.07979,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27197,"mean_force":0.05639,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53253,0.00074,0.13274]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12940.0,"contact_point_centroid":[0.53331,0.01981,0.1312],"force_p95":0.07984,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25934,"mean_force":0.05647,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53226,0.00074,0.12903]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1030.0,"contact_point_centroid":[0.63763,0.12547,0.20107],"force_p95":0.0781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23178,"mean_force":0.0512,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63391,0.14444,0.19935]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1085.0,"contact_point_centroid":[0.63717,0.16347,0.20026],"force_p95":0.08805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21364,"mean_force":0.05168,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63391,0.14443,0.19936]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00102,-0.00203],"force_p95":0.13241,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15373,"mean_force":0.12543,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53008,0.00087,0.04075]},{"body_a":"world","body_b":"grasp_target","contact_count":1268.0,"contact_point_centroid":[0.54431,0.00113,-0.00189],"force_p95":0.13591,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51608,0.00045,0.2248]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53473,0.00095,0.0852]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53022,-0.01835,0.04196],"force_p95":0.07628,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12245,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52885,0.00085,0.03931]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8722.0,"contact_point_centroid":[0.58727,0.05116,0.21268],"force_p95":0.08486,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09946,"mean_force":0.0582,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58503,0.07,0.21195]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8030.0,"contact_point_centroid":[0.58853,0.09077,0.21296],"force_p95":0.0875,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09684,"mean_force":0.06175,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58626,0.07181,0.21172]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53011,0.01993,0.04109],"force_p95":0.06836,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09456,"mean_force":0.04471,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52885,0.00085,0.03931]}],"total_contact_groups":13},"final_pose_error":0.02884,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.63143,0.14182,0.02354],"final_tcp_position":[0.63559,0.14424,0.20335],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.47045,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":318.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1268.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pregrasp","tcp_end":[0.5348,0.00093,0.14712],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12147,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.53712,0.001,0.04909],"tcp_start":[0.5348,0.00093,0.14712],"tcp_to_object_dist_end":0.02416,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5442,0.00075,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.2505,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13062,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15373,"subtask_id":"grasp_object","tcp_end":[0.52882,0.00085,0.03927],"tcp_start":[0.53712,0.001,0.04909],"tcp_to_object_dist_end":0.0204,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":698.0,"n_steps_budget":1000.0,"object_pos_end":[0.54894,0.00077,0.20498],"object_pos_start":[0.5442,0.00075,0.02587],"object_to_goal_dist_end":0.18622,"object_to_goal_dist_start":0.2505,"object_z_max":0.20473,"peak_contact_force":0.08008,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25917.0,"raw_peak_contact_force":0.43403,"subtask_id":"place_at_goal","tcp_end":[0.54005,0.0007,0.22455],"tcp_start":[0.52882,0.00085,0.03927],"tcp_to_object_dist_end":0.0215,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":519.0,"n_steps_budget":1000.0,"object_pos_end":[0.64173,0.14419,0.18024],"object_pos_start":[0.54894,0.00077,0.20498],"object_to_goal_dist_end":0.0186,"object_to_goal_dist_start":0.18622,"object_z_max":0.20516,"peak_contact_force":0.08552,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16752.0,"raw_peak_contact_force":0.09946,"subtask_id":"place_at_goal","tcp_end":[0.63559,0.14424,0.20335],"tcp_start":[0.54005,0.0007,0.22455],"tcp_to_object_dist_end":0.02391,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":0.0,"n_steps_budget":1000.0,"object_pos_end":[0.64173,0.14419,0.18024],"object_pos_start":[0.64173,0.14419,0.18024],"object_to_goal_dist_end":0.0186,"object_to_goal_dist_start":0.0186,"peak_contact_force":0.08534,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"place_at_goal","tcp_end":[0.63559,0.14424,0.20335],"tcp_start":[0.63559,0.14424,0.20335],"tcp_to_object_dist_end":0.02391,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63143,0.14182,0.02354],"object_pos_start":[0.64173,0.14419,0.18024],"object_to_goal_dist_end":0.16913,"object_to_goal_dist_start":0.0186,"object_z_max":0.18024,"peak_contact_force":0.13433,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2229.0,"raw_peak_contact_force":1.47045,"subtask_id":"place_at_goal","tcp_end":[0.63029,0.14323,0.22243],"tcp_start":[0.63559,0.14424,0.20335],"tcp_to_object_dist_end":0.1989,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":6.0,"average_failure_rate":0.02479,"average_mean_iterations":8.60744,"average_solve_count":242.0,"average_success_count":236.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06605,"descend_1.speed":0.04002,"descend_2.speed":0.02407,"lift_1.lift_height":0.13952,"lift_1.speed":0.05968,"transport_1.speed":0.04468},"optimized_scores":{"best_composite_score":0.27374,"best_fitness_score":0.72374,"best_task_score":0.53912},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":523.0,"contact_point_centroid":[0.70404,0.12292,-0.00034],"force_p95":356.57872,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":662.8253,"mean_force":273.17411,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.64698,0.14969,0.28433]},{"body_a":"world","body_b":"link6","contact_count":85.0,"contact_point_centroid":[0.70847,0.13253,-0.00014],"force_p95":80.43383,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":82.03368,"mean_force":56.67486,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.65021,0.15083,0.2852]},{"body_a":"world","body_b":"grasp_target","contact_count":3514.0,"contact_point_centroid":[0.59491,0.18686,-0.00217],"force_p95":0.12368,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.70535,"mean_force":0.13152,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.63269,0.18331,0.29012]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3184.0,"contact_point_centroid":[0.55683,0.07122,0.12871],"force_p95":0.15212,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36619,"mean_force":0.11638,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55309,0.08937,0.13272]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3970.0,"contact_point_centroid":[0.52034,0.00981,0.0918],"force_p95":0.14159,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32798,"mean_force":0.09142,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51826,0.02847,0.09496]},{"body_a":"world","body_b":"grasp_target","contact_count":98.0,"contact_point_centroid":[0.52936,0.02772,-0.00157],"force_p95":0.27043,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30583,"mean_force":0.06731,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51437,0.02841,0.05282]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5558.0,"contact_point_centroid":[0.51896,0.04656,0.09259],"force_p95":0.12474,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26785,"mean_force":0.0692,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51809,0.02846,0.09364]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53061,0.03062,-0.0022],"force_p95":0.17826,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22778,"mean_force":0.13706,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51647,0.02856,0.05273]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3781.0,"contact_point_centroid":[0.55801,0.11047,0.12802],"force_p95":0.12917,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17643,"mean_force":0.09973,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55467,0.0925,0.13227]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3095.0,"contact_point_centroid":[0.51802,0.00956,0.04959],"force_p95":0.12103,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15482,"mean_force":0.07139,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51529,0.02849,0.05135]},{"body_a":"world","body_b":"grasp_target","contact_count":1252.0,"contact_point_centroid":[0.5305,0.03079,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51029,0.01265,0.22516]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52189,0.02806,0.0874]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59492,0.1868,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.65017,0.15115,0.29114]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4875.0,"contact_point_centroid":[0.51658,0.04711,0.05137],"force_p95":0.08052,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08824,"mean_force":0.04512,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5153,0.02849,0.05136]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3386.0,"contact_point_centroid":[0.64383,0.15932,0.2949],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01644,"mean_force":0.01044,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.64307,0.15959,0.29709]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.65101,0.15084,0.2827],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01269,"mean_force":0.0101,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.65023,0.15095,0.28514]}],"total_contact_groups":16},"final_pose_error":0.19509,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59492,0.1868,0.01602],"final_tcp_position":[0.65025,0.15131,0.28502],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":662.8253,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":314.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":35.42938,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1252.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pregrasp","tcp_end":[0.52283,0.02629,0.14776],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12206,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.52318,0.02899,0.06062],"tcp_start":[0.52283,0.02629,0.14776],"tcp_to_object_dist_end":0.03541,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53078,0.02902,0.02522],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18505,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.17508,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9770.0,"raw_peak_contact_force":0.22778,"subtask_id":"grasp_object","tcp_end":[0.51526,0.02849,0.05132],"tcp_start":[0.52318,0.02899,0.06062],"tcp_to_object_dist_end":0.03037,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":354.0,"n_steps_budget":1000.0,"object_pos_end":[0.5313,0.02935,0.11348],"object_pos_start":[0.53078,0.02902,0.02522],"object_to_goal_dist_end":0.16501,"object_to_goal_dist_start":0.18505,"object_z_max":0.11324,"peak_contact_force":0.14168,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9626.0,"raw_peak_contact_force":0.32798,"subtask_id":"place_at_goal","tcp_end":[0.52516,0.0287,0.14581],"tcp_start":[0.51526,0.02849,0.05132],"tcp_to_object_dist_end":0.03292,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":454.0,"n_steps_budget":1000.0,"object_pos_end":[0.59299,0.17342,0.06588],"object_pos_start":[0.5313,0.02935,0.11348],"object_to_goal_dist_end":0.04337,"object_to_goal_dist_start":0.16501,"object_z_max":0.11365,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6965.0,"raw_peak_contact_force":0.36619,"subtask_id":"place_at_goal","tcp_end":[0.59035,0.16342,0.12191],"tcp_start":[0.52516,0.0287,0.14581],"tcp_to_object_dist_end":0.05698,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":906.0,"n_steps_budget":1000.0,"object_pos_end":[0.59492,0.1868,0.01602],"object_pos_start":[0.59299,0.17342,0.06588],"object_to_goal_dist_end":0.09267,"object_to_goal_dist_start":0.04337,"object_z_max":0.06588,"peak_contact_force":225.80275,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7423.0,"raw_peak_contact_force":662.8253,"subtask_id":"place_at_goal","tcp_end":[0.65025,0.15131,0.28502],"tcp_start":[0.59035,0.16342,0.12191],"tcp_to_object_dist_end":0.27691,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59492,0.1868,0.01602],"object_pos_start":[0.59492,0.1868,0.01602],"object_to_goal_dist_end":0.09267,"object_to_goal_dist_start":0.09267,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1105.0,"raw_peak_contact_force":82.03368,"subtask_id":"place_at_goal","tcp_end":[0.65025,0.15167,0.31067],"tcp_start":[0.65025,0.15131,0.28502],"tcp_to_object_dist_end":0.30185,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```