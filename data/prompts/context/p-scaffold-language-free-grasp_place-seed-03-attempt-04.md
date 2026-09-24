## Search State

- **Seed**: 3
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | 7 | 0.2125 | 0.47 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | 7 | 0.2215 | 0.49 | ✅ accepted |
| 2 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | 5 | 0.2342 | 0.20 | ❌ rejected |
| 1 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | 5 | 0.2342 | 0.20 | ❌ rejected |
| 0 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | 5 | 0.2349 | 0.20 | ✅ accepted |

**Proposal policy**: task_score is 0.47 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.213) — your mutation base

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

- **Composite score**: 0.213
- **task_score** (E): 0.475
- **fitness_score**: 0.713  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.500

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1574 |
| descend_1 | 1.00 | 1.00 | 0.1094 |
| grasp_1 | 1.00 | 1.00 | 0.0119 |
| lift_1 | 1.00 | 1.00 | 0.1841 |
| transport_1 | 1.00 | 1.00 | 0.2111 |
| descend_2 | 1.00 | 1.00 | 0.1028 |
| release_1 | 1.00 | 1.00 | 0.0206 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.148) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.002, 0.148)→(0.505, 0.002, 0.039) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.505, 0.002, 0.039)→(0.497, 0.001, 0.030) | (0.511, 0.002, 0.026)→(0.511, 0.001, 0.026) | 0.246→0.246 | 1.00 / 42.333 | 0.141 | 0.196 |
| lift_1 | lift | 1.00 / step_budget | (0.497, 0.001, 0.030)→(0.507, 0.001, 0.214) | (0.511, 0.001, 0.026)→(0.518, 0.001, 0.204) | 0.246→0.232 | 1.00 / 36.667 | 0.084 | 0.549 |
| transport_1 | approach | 1.00 / step_budget | (0.507, 0.001, 0.214)→(0.616, 0.169, 0.238) | (0.518, 0.001, 0.204)→(0.625, 0.169, 0.222) | 0.232→0.086 | 1.00 / 34.000 | 0.081 | 0.098 |
| descend_2 | descend | 1.00 / step_budget | (0.616, 0.169, 0.238)→(0.622, 0.180, 0.136) | (0.625, 0.169, 0.222)→(0.621, 0.179, 0.115) | 0.086→0.024 | 1.00 / 38.000 | 0.079 | 0.172 |
| release_1 | release | 1.00 / step_budget | (0.622, 0.180, 0.136)→(0.615, 0.177, 0.156) | (0.621, 0.179, 0.115)→(0.613, 0.181, 0.023) | 0.024→0.116 | 1.00 / 2.667 | 0.186 | 1.308 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.573
- phase_score: 0.583
- phase_breakdown.place_at_goal_score: 0.517
- phase_breakdown.transport_to_goal_score: 0.583
- phase_breakdown.reach_object_score: 0.673
- phase_breakdown.grasp_object_score: 0.739
- phase_breakdown.lift_object_score: 0.288
- grasp_place_fitness: 0.760

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.760
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.573
- **Median Q (composite search score)**: 0.241
- **K-run variance**: 0.0029
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.277


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.04523,"average_solve_count":398.0,"average_success_count":398.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.02739,"descend_1.speed":0.0525,"descend_2.speed":0.08167,"lift_1.lift_height":0.22144,"lift_1.speed":0.03169,"transport_1.speed":0.06767,"transport_1.transport_height":0.06672},"optimized_scores":{"best_composite_score":0.24063,"best_fitness_score":0.74063,"best_task_score":0.52111},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":327.0,"contact_point_centroid":[0.62809,0.20799,-0.00395],"force_p95":0.74106,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16767,"mean_force":0.22087,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61809,0.20362,0.11416]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.45475,-0.02535,-0.00146],"force_p95":0.65414,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6824,"mean_force":0.28572,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4459,-0.02564,0.02238]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14026.0,"contact_point_centroid":[0.4491,-0.04464,0.1274],"force_p95":0.07379,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25963,"mean_force":0.05047,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44903,-0.02552,0.12545]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13462.0,"contact_point_centroid":[0.44902,-0.00636,0.12427],"force_p95":0.07449,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25612,"mean_force":0.05207,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44885,-0.02552,0.1221]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45856,-0.02613,-0.00205],"force_p95":0.13828,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19149,"mean_force":0.12706,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44789,-0.02571,0.02247]},{"body_a":"world","body_b":"grasp_target","contact_count":1252.0,"contact_point_centroid":[0.45856,-0.02632,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48087,-0.01064,0.22702]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19003.0,"contact_point_centroid":[0.62079,0.18153,0.13361],"force_p95":0.07285,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12637,"mean_force":0.04938,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62023,0.20066,0.1324]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19437.0,"contact_point_centroid":[0.62081,0.21969,0.1338],"force_p95":0.07153,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12457,"mean_force":0.04876,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62016,0.20057,0.1329]},{"body_a":"world","body_b":"grasp_target","contact_count":3008.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45612,-0.02416,0.086]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1080.0,"contact_point_centroid":[0.62407,0.1863,0.10414],"force_p95":0.07327,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11074,"mean_force":0.04693,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62305,0.20544,0.10336]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1305.0,"contact_point_centroid":[0.62417,0.22454,0.10388],"force_p95":0.07129,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10399,"mean_force":0.04053,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62297,0.20541,0.10322]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15436.0,"contact_point_centroid":[0.5384,0.10807,0.20033],"force_p95":0.07464,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09805,"mean_force":0.05104,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53815,0.0889,0.19858]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16664.0,"contact_point_centroid":[0.53473,0.06527,0.20104],"force_p95":0.07059,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09595,"mean_force":0.04796,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53479,0.08439,0.19961]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4811.0,"contact_point_centroid":[0.4468,-0.00646,0.0238],"force_p95":0.0677,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09274,"mean_force":0.04484,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44679,-0.02567,0.02144]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5172.0,"contact_point_centroid":[0.44665,-0.04491,0.02328],"force_p95":0.06647,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08663,"mean_force":0.04305,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44679,-0.02567,0.02145]}],"total_contact_groups":15},"final_pose_error":0.00907,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.63021,0.20823,0.01635],"final_tcp_position":[0.62493,0.20607,0.10699],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.16767,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":314.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1252.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.46133,-0.02243,0.1494],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12347,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":752.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3008.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.45427,-0.02594,0.02847],"tcp_start":[0.46133,-0.02243,0.1494],"tcp_to_object_dist_end":0.00496,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45842,-0.02566,0.02582],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30328,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13562,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11783.0,"raw_peak_contact_force":0.19149,"subtask_id":"grasp_object","tcp_end":[0.44676,-0.02567,0.02142],"tcp_start":[0.45427,-0.02594,0.02847],"tcp_to_object_dist_end":0.01246,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":687.0,"n_steps_budget":1000.0,"object_pos_end":[0.46606,-0.02532,0.2273],"object_pos_start":[0.45842,-0.02566,0.02582],"object_to_goal_dist_end":0.30703,"object_to_goal_dist_start":0.30328,"object_z_max":0.22702,"peak_contact_force":0.07843,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27572.0,"raw_peak_contact_force":0.6824,"subtask_id":"lift_object","tcp_end":[0.45476,-0.02553,0.2278],"tcp_start":[0.44676,-0.02567,0.02142],"tcp_to_object_dist_end":0.01132,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":779.0,"n_steps_budget":1000.0,"object_pos_end":[0.62822,0.19431,0.16698],"object_pos_start":[0.46606,-0.02532,0.2273],"object_to_goal_dist_end":0.05469,"object_to_goal_dist_start":0.30703,"object_z_max":0.2275,"peak_contact_force":0.07123,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32100.0,"raw_peak_contact_force":0.09805,"subtask_id":"transport_to_goal","tcp_end":[0.61725,0.19437,0.17477],"tcp_start":[0.45476,-0.02553,0.2278],"tcp_to_object_dist_end":0.01346,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":940.0,"n_steps_budget":1000.0,"object_pos_end":[0.63124,0.20597,0.09267],"object_pos_start":[0.62822,0.19431,0.16698],"object_to_goal_dist_end":0.0216,"object_to_goal_dist_start":0.05469,"object_z_max":0.16698,"peak_contact_force":0.07249,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":38440.0,"raw_peak_contact_force":0.12637,"subtask_id":"place_at_goal","tcp_end":[0.62493,0.20607,0.10699],"tcp_start":[0.61725,0.19437,0.17477],"tcp_to_object_dist_end":0.01565,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63021,0.20823,0.01635],"object_pos_start":[0.63124,0.20597,0.09267],"object_to_goal_dist_end":0.09777,"object_to_goal_dist_start":0.0216,"object_z_max":0.09267,"peak_contact_force":0.12055,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2712.0,"raw_peak_contact_force":1.16767,"subtask_id":"place_at_goal","tcp_end":[0.61797,0.20357,0.12613],"tcp_start":[0.62493,0.20607,0.10699],"tcp_to_object_dist_end":0.11056,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.9209,"average_solve_count":354.0,"average_success_count":354.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05324,"descend_1.speed":0.08297,"descend_2.speed":0.08515,"lift_1.lift_height":0.16575,"lift_1.speed":0.01156,"transport_1.speed":0.02789,"transport_1.transport_height":0.08354},"optimized_scores":{"best_composite_score":0.13664,"best_fitness_score":0.63664,"best_task_score":0.32989},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":185.0,"contact_point_centroid":[0.62485,0.15613,-0.00776],"force_p95":1.29521,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.64862,"mean_force":0.39798,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63798,0.15512,0.19307]},{"body_a":"world","body_b":"grasp_target","contact_count":110.0,"contact_point_centroid":[0.54086,0.00076,-0.0015],"force_p95":0.36971,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42509,"mean_force":0.16202,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52793,0.00083,0.03634]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9855.0,"contact_point_centroid":[0.53321,-0.01836,0.1061],"force_p95":0.08151,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24648,"mean_force":0.05704,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53226,0.00073,0.10378]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10236.0,"contact_point_centroid":[0.53294,0.01978,0.10328],"force_p95":0.07885,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2394,"mean_force":0.05562,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53202,0.00074,0.10118]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11185.0,"contact_point_centroid":[0.6424,0.13471,0.20831],"force_p95":0.08082,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20179,"mean_force":0.0499,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.64133,0.15382,0.2064]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10626.0,"contact_point_centroid":[0.64237,0.17276,0.20921],"force_p95":0.07801,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19677,"mean_force":0.05153,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.64122,0.15366,0.20775]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00102,-0.00203],"force_p95":0.13232,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15467,"mean_force":0.12539,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53029,0.00088,0.03708]},{"body_a":"world","body_b":"grasp_target","contact_count":1288.0,"contact_point_centroid":[0.54431,0.00113,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51596,0.00044,0.2251]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5348,0.00095,0.08353]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53035,-0.01835,0.0383],"force_p95":0.07624,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12021,"mean_force":0.05179,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52905,0.00086,0.03563]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53024,0.01993,0.03742],"force_p95":0.06831,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.095,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52905,0.00086,0.03564]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13850.0,"contact_point_centroid":[0.58874,0.05524,0.2147],"force_p95":0.0796,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09452,"mean_force":0.0526,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58725,0.07415,0.21333]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1296.0,"contact_point_centroid":[0.6426,0.13716,0.18204],"force_p95":0.06561,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09333,"mean_force":0.03966,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64196,0.15631,0.17987]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12273.0,"contact_point_centroid":[0.59022,0.09528,0.21654],"force_p95":0.08633,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09229,"mean_force":0.05878,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58868,0.07621,0.21462]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1239.0,"contact_point_centroid":[0.64275,0.17559,0.18185],"force_p95":0.06857,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08706,"mean_force":0.04154,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64192,0.1563,0.17978]}],"total_contact_groups":15},"final_pose_error":0.00863,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.62961,0.15268,0.02582],"final_tcp_position":[0.64353,0.15673,0.18363],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.64862,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":323.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1288.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53468,0.00093,0.14752],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12188,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.53738,0.001,0.04543],"tcp_start":[0.53468,0.00093,0.14752],"tcp_to_object_dist_end":0.02061,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54419,0.00075,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25051,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13045,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15467,"subtask_id":"grasp_object","tcp_end":[0.52902,0.00086,0.0356],"tcp_start":[0.53738,0.001,0.04543],"tcp_to_object_dist_end":0.01802,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":543.0,"n_steps_budget":1000.0,"object_pos_end":[0.54998,0.00072,0.15779],"object_pos_start":[0.54419,0.00075,0.02587],"object_to_goal_dist_end":0.18817,"object_to_goal_dist_start":0.25051,"object_z_max":0.15755,"peak_contact_force":0.08229,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20201.0,"raw_peak_contact_force":0.42509,"subtask_id":"lift_object","tcp_end":[0.53922,0.00069,0.17237],"tcp_start":[0.52902,0.00086,0.0356],"tcp_to_object_dist_end":0.01811,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":738.0,"n_steps_budget":1000.0,"object_pos_end":[0.64538,0.14825,0.23954],"object_pos_start":[0.54998,0.00072,0.15779],"object_to_goal_dist_end":0.04948,"object_to_goal_dist_start":0.18817,"object_z_max":0.23944,"peak_contact_force":0.08636,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26123.0,"raw_peak_contact_force":0.09452,"subtask_id":"transport_to_goal","tcp_end":[0.63893,0.14836,0.2597],"tcp_start":[0.53922,0.00069,0.17237],"tcp_to_object_dist_end":0.02117,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":544.0,"n_steps_budget":1000.0,"object_pos_end":[0.64171,0.1565,0.16125],"object_pos_start":[0.64538,0.14825,0.23954],"object_to_goal_dist_end":0.03047,"object_to_goal_dist_start":0.04948,"object_z_max":0.23954,"peak_contact_force":0.06884,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":21811.0,"raw_peak_contact_force":0.20179,"subtask_id":"place_at_goal","tcp_end":[0.64353,0.15673,0.18363],"tcp_start":[0.63893,0.14836,0.2597],"tcp_to_object_dist_end":0.02245,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62961,0.15268,0.02582],"object_pos_start":[0.64171,0.1565,0.16125],"object_to_goal_dist_end":0.16635,"object_to_goal_dist_start":0.03047,"object_z_max":0.16125,"peak_contact_force":0.22504,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2720.0,"raw_peak_contact_force":1.64862,"subtask_id":"place_at_goal","tcp_end":[0.63794,0.1551,0.20236],"tcp_start":[0.64353,0.15673,0.18363],"tcp_to_object_dist_end":0.17676,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18571,"average_solve_count":280.0,"average_success_count":280.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05485,"descend_1.speed":0.06923,"descend_2.speed":0.05999,"lift_1.lift_height":0.23602,"lift_1.speed":0.05788,"transport_1.speed":0.0733,"transport_1.transport_height":0.18417},"optimized_scores":{"best_composite_score":0.26033,"best_fitness_score":0.76033,"best_task_score":0.5731},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":162.0,"contact_point_centroid":[0.57633,0.1915,-0.00653],"force_p95":0.898,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.10675,"mean_force":0.39605,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58953,0.17369,0.12654]},{"body_a":"world","body_b":"grasp_target","contact_count":91.0,"contact_point_centroid":[0.52761,0.02833,-0.00147],"force_p95":0.45292,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54048,"mean_force":0.12743,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5149,0.029,0.03503]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14061.0,"contact_point_centroid":[0.52025,0.04799,0.1365],"force_p95":0.08082,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30594,"mean_force":0.05649,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51907,0.02893,0.13448]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13814.0,"contact_point_centroid":[0.52059,0.00986,0.1414],"force_p95":0.08346,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29519,"mean_force":0.05682,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51937,0.02893,0.13918]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1033.0,"contact_point_centroid":[0.59283,0.19459,0.11225],"force_p95":0.13994,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27145,"mean_force":0.07306,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59373,0.17507,0.11371]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53057,0.03052,-0.00215],"force_p95":0.16659,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2409,"mean_force":0.13411,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5172,0.02917,0.03506]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17550.0,"contact_point_centroid":[0.59464,0.19067,0.17879],"force_p95":0.08744,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18929,"mean_force":0.05825,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59412,0.17157,0.17748]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20088.0,"contact_point_centroid":[0.59411,0.15253,0.17921],"force_p95":0.08149,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18745,"mean_force":0.05249,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59411,0.17155,0.17767]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4066.0,"contact_point_centroid":[0.51703,0.00988,0.03642],"force_p95":0.08163,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1524,"mean_force":0.05188,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51598,0.02909,0.03368]},{"body_a":"world","body_b":"grasp_target","contact_count":1276.0,"contact_point_centroid":[0.5305,0.03079,-0.0019],"force_p95":0.13575,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51029,0.01264,0.22521]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5223,0.02832,0.08026]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":964.0,"contact_point_centroid":[0.59281,0.1565,0.11399],"force_p95":0.08317,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12147,"mean_force":0.05065,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59423,0.17523,0.11443]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7592.0,"contact_point_centroid":[0.56057,0.07734,0.25979],"force_p95":0.08842,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1021,"mean_force":0.06122,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55835,0.09625,0.25861]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7608.0,"contact_point_centroid":[0.56108,0.11601,0.25947],"force_p95":0.08631,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0946,"mean_force":0.06112,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55877,0.09712,0.25884]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5027.0,"contact_point_centroid":[0.51694,0.04827,0.03547],"force_p95":0.07451,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08147,"mean_force":0.04454,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51598,0.02909,0.03369]}],"total_contact_groups":15},"final_pose_error":0.01145,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.58027,0.18137,0.02739],"final_tcp_position":[0.59611,0.1758,0.11778],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.10675,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":320.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1276.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52281,0.0263,0.14772],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12203,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.5241,0.02963,0.04294],"tcp_start":[0.52281,0.0263,0.14772],"tcp_to_object_dist_end":0.01813,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53043,0.02927,0.02549],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18485,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15793,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10893.0,"raw_peak_contact_force":0.2409,"subtask_id":"grasp_object","tcp_end":[0.51595,0.02909,0.03365],"tcp_start":[0.5241,0.02963,0.04294],"tcp_to_object_dist_end":0.01662,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":758.0,"n_steps_budget":1000.0,"object_pos_end":[0.53655,0.02897,0.22632],"object_pos_start":[0.53043,0.02927,0.02549],"object_to_goal_dist_end":0.20146,"object_to_goal_dist_start":0.18485,"object_z_max":0.22607,"peak_contact_force":0.09085,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27966.0,"raw_peak_contact_force":0.54048,"subtask_id":"lift_object","tcp_end":[0.52664,0.02906,0.24207],"tcp_start":[0.51595,0.02909,0.03365],"tcp_to_object_dist_end":0.01861,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":481.0,"n_steps_budget":1000.0,"object_pos_end":[0.60024,0.1653,0.26063],"object_pos_start":[0.53655,0.02897,0.22632],"object_to_goal_dist_end":0.15312,"object_to_goal_dist_start":0.20146,"object_z_max":0.26057,"peak_contact_force":0.0858,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15200.0,"raw_peak_contact_force":0.1021,"subtask_id":"transport_to_goal","tcp_end":[0.59308,0.16542,0.28006],"tcp_start":[0.52664,0.02906,0.24207],"tcp_to_object_dist_end":0.02071,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58865,0.17526,0.09202],"object_pos_start":[0.60024,0.1653,0.26063],"object_to_goal_dist_end":0.02086,"object_to_goal_dist_start":0.15312,"object_z_max":0.26063,"peak_contact_force":0.09547,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":37638.0,"raw_peak_contact_force":0.18929,"subtask_id":"place_at_goal","tcp_end":[0.59611,0.1758,0.11778],"tcp_start":[0.59308,0.16542,0.28006],"tcp_to_object_dist_end":0.02683,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58027,0.18137,0.02739],"object_pos_start":[0.58865,0.17526,0.09202],"object_to_goal_dist_end":0.0835,"object_to_goal_dist_start":0.02086,"object_z_max":0.09202,"peak_contact_force":0.21256,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2159.0,"raw_peak_contact_force":1.10675,"subtask_id":"place_at_goal","tcp_end":[0.58941,0.17365,0.13841],"tcp_start":[0.59611,0.1758,0.11778],"tcp_to_object_dist_end":0.11167,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```