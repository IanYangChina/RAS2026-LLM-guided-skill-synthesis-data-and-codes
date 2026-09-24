## Search State

- **Seed**: 3
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | 0.1127 | 0.25 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | 0.1085 | 0.24 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | -0.0692 | 0.22 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.1643 | 0.25 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 0 | 0.1728 | 0.24 | ❌ rejected |

**Proposal policy**: task_score is 0.25 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.113) — your mutation base

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
    - 0.03
    tolerance: 0.01
    orientation:
      mode: keep_current
- id: grasp
  type: grasp
  control: position_control
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
    threshold: 0.5
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
    offset:
    - 0.0
    - 0.0
    - 0.12
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.18
      default: 0.12
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
    - 0.12
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
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
    - 0.03
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_offset_z:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
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
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_closed, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=repeat
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_offset_z: status=consumed; consumers=target.offset.z (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.113
- **task_score** (E): 0.249
- **fitness_score**: 0.493  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1681 |
| descend_to_grasp | 1.00 | 1.00 | 0.0735 |
| grasp | 1.00 | 1.00 | 0.0121 |
| lift | 1.00 | 1.00 | 0.1038 |
| transport_to_goal | 0.67 | 1.00 | 0.2039 |
| descend_to_place | 1.00 | 1.00 | 0.0824 |
| release | 1.00 | 1.00 | 0.0201 |
| retract | 1.00 | 1.00 | 0.0847 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, 0.002, 0.138) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.507, 0.002, 0.138)→(0.506, 0.002, 0.064) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 11.023 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.506, 0.002, 0.064)→(0.498, 0.002, 0.055) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 28.000 | 0.140 | 0.183 |
| lift | lift | 1.00 / step_budget | (0.496, 0.002, 0.134)→(0.493, 0.002, 0.238) | (0.511, 0.002, 0.026)→(0.498, 0.009, 0.081) | 0.246→0.227 | 1.00 / 15.333 | 0.117 | 0.403 |
| transport_to_goal | approach | 0.67 / step_budget | (0.493, 0.002, 0.238)→(0.593, 0.142, 0.261) | (0.498, 0.009, 0.081)→(0.516, 0.044, 0.016) | 0.227→0.222 | 1.00 / 9.000 | 181973.905 | 0.992 |
| descend_to_place | descend | 1.00 / step_budget | (0.593, 0.142, 0.261)→(0.619, 0.176, 0.192) | (0.516, 0.044, 0.016)→(0.516, 0.044, 0.016) | 0.222→0.222 | 1.00 / 8.333 | 91002.596 | 0.123 |
| release | release | 1.00 / step_budget | (0.619, 0.176, 0.192)→(0.614, 0.174, 0.211) | (0.516, 0.044, 0.016)→(0.516, 0.044, 0.016) | 0.222→0.222 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.614, 0.174, 0.211)→(0.612, 0.173, 0.296) | (0.516, 0.044, 0.016)→(0.516, 0.044, 0.016) | 0.222→0.222 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.383
- phase_score: 0.095
- phase_breakdown.approach_objective_score: 0.315
- phase_breakdown.placement_objective_score: 0.000
- grasp_place_fitness: 0.644

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.644
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.383
- **Median Q (composite search score)**: 0.186
- **K-run variance**: 0.0263
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.346


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89427,"average_solve_count":227.0,"average_success_count":227.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_place.place_offset_z":0.05058,"lift.lift_height":0.12931,"lift.lift_speed":0.09947,"transport_to_goal.transport_speed":0.10539},"optimized_scores":{"best_composite_score":-0.11218,"best_fitness_score":0.26782,"best_task_score":0.13675},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":7790.0,"contact_point_centroid":[0.44331,-0.00404,-0.00207],"force_p95":0.1366,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56709,"mean_force":0.1281,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4411,-0.02524,0.24928]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1506.0,"contact_point_centroid":[0.44393,-0.00669,0.06307],"force_p95":0.14726,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26553,"mean_force":0.09176,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44442,-0.0254,0.0675]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1764.0,"contact_point_centroid":[0.44409,-0.04385,0.06397],"force_p95":0.12224,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26213,"mean_force":0.07837,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44434,-0.02539,0.06833]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45859,-0.02629,-0.00206],"force_p95":0.14187,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1892,"mean_force":0.12741,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44829,-0.02555,0.05878]},{"body_a":"world","body_b":"grasp_target","contact_count":1956.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47879,-0.01168,0.22]},{"body_a":"world","body_b":"grasp_target","contact_count":976.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45549,-0.02481,0.10221]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.44298,-0.00254,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50137,0.05212,0.34719]},{"body_a":"world","body_b":"grasp_target","contact_count":2568.0,"contact_point_centroid":[0.44298,-0.00254,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59144,0.16465,0.22157]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.44298,-0.00254,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61806,0.20083,0.16236]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.44298,-0.00254,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61363,0.19911,0.22144]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3153.0,"contact_point_centroid":[0.44538,-0.00661,0.05385],"force_p95":0.0857,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09467,"mean_force":0.06628,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44725,-0.02551,0.05775]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3451.0,"contact_point_centroid":[0.44568,-0.04436,0.05383],"force_p95":0.08275,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08301,"mean_force":0.06125,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44725,-0.02551,0.05775]},{"body_a":"left_finger","body_b":"right_finger","contact_count":7865.0,"contact_point_centroid":[0.4413,-0.02524,0.25955],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01637,"mean_force":0.01061,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44096,-0.02523,0.25723]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4234.0,"contact_point_centroid":[0.50166,0.05203,0.34958],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.01052,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50131,0.05203,0.34726]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2732.0,"contact_point_centroid":[0.59195,0.16474,0.22365],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.01047,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5915,0.16473,0.22144]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.62144,0.20193,0.16138],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01275,"mean_force":0.01012,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62081,0.20192,0.15913]}],"total_contact_groups":16},"final_pose_error":0.01581,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.44298,-0.00254,0.01602],"final_tcp_position":[0.61394,0.19915,0.26605],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273004.35474,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":490.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1956.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_objective","tcp_end":[0.45846,-0.02397,0.13952],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11353,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":244.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":976.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45456,-0.02578,0.06506],"tcp_start":[0.45846,-0.02397,0.13952],"tcp_to_object_dist_end":0.03925,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45851,-0.0258,0.02577],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30335,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14088,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8404.0,"raw_peak_contact_force":0.1892,"tcp_end":[0.44722,-0.02551,0.05772],"tcp_start":[0.45456,-0.02578,0.06506],"tcp_to_object_dist_end":0.03389,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":2150.0,"n_steps_budget":810.0,"object_pos_end":[0.44298,-0.00254,0.01602],"object_pos_start":[0.45851,-0.0258,0.02577],"object_to_goal_dist_end":0.29844,"object_to_goal_dist_start":0.30335,"object_z_max":0.04254,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18925.0,"raw_peak_contact_force":0.56709,"tcp_end":[0.43992,-0.0252,0.41193],"tcp_start":[0.44127,-0.02524,0.29394],"tcp_to_object_dist_end":0.39657,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44298,-0.00254,0.01602],"object_pos_start":[0.44298,-0.00254,0.01602],"object_to_goal_dist_end":0.29844,"object_to_goal_dist_start":0.29844,"object_z_max":0.01602,"peak_contact_force":272912.32597,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8234.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56069,0.12544,0.28952],"tcp_start":[0.43992,-0.0252,0.41193],"tcp_to_object_dist_end":0.3241,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":642.0,"n_steps_budget":1000.0,"object_pos_end":[0.44298,-0.00254,0.01602],"object_pos_start":[0.44298,-0.00254,0.01602],"object_to_goal_dist_end":0.29844,"object_to_goal_dist_start":0.29844,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5300.0,"raw_peak_contact_force":0.12263,"subtask_id":"placement_objective","tcp_end":[0.62239,0.20226,0.1626],"tcp_start":[0.56069,0.12544,0.28952],"tcp_to_object_dist_end":0.30922,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.44298,-0.00254,0.01602],"object_pos_start":[0.44298,-0.00254,0.01602],"object_to_goal_dist_end":0.29844,"object_to_goal_dist_start":0.29844,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61645,0.20019,0.18162],"tcp_start":[0.62239,0.20226,0.1626],"tcp_to_object_dist_end":0.31403,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.44298,-0.00254,0.01602],"object_pos_start":[0.44298,-0.00254,0.01602],"object_to_goal_dist_end":0.29844,"object_to_goal_dist_start":0.29844,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61394,0.19915,0.26605],"tcp_start":[0.61645,0.20019,0.18162],"tcp_to_object_dist_end":0.3639,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85714,"average_solve_count":140.0,"average_success_count":140.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_place.place_offset_z":0.04801,"lift.lift_height":0.10629,"lift.lift_speed":0.09634,"transport_to_goal.transport_speed":0.28644},"optimized_scores":{"best_composite_score":0.18636,"best_fitness_score":0.56636,"best_task_score":0.2271},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3196.0,"contact_point_centroid":[0.56684,0.04725,-0.00226],"force_p95":0.12423,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.61229,"mean_force":0.13456,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5864,0.08241,0.22558]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6190.0,"contact_point_centroid":[0.52921,-0.0175,0.09363],"force_p95":0.13323,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30536,"mean_force":0.09711,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52589,0.00081,0.09705]},{"body_a":"world","body_b":"grasp_target","contact_count":155.0,"contact_point_centroid":[0.54178,0.00061,-0.00114],"force_p95":0.21857,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29148,"mean_force":0.05529,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52841,0.00085,0.05559]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6264.0,"contact_point_centroid":[0.5293,0.01913,0.09445],"force_p95":0.13253,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28457,"mean_force":0.09592,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52591,0.00081,0.09789]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1059.0,"contact_point_centroid":[0.53566,-0.01018,0.14785],"force_p95":0.1444,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21067,"mean_force":0.10432,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52943,0.00809,0.15201]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1212.0,"contact_point_centroid":[0.53635,0.02712,0.14865],"force_p95":0.14617,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18176,"mean_force":0.09816,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53012,0.00912,0.15287]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00109,-0.00203],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15317,"mean_force":0.12512,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53129,0.0009,0.05537]},{"body_a":"world","body_b":"grasp_target","contact_count":2180.0,"contact_point_centroid":[0.54431,0.00113,-0.00193],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51725,0.00048,0.21767]},{"body_a":"world","body_b":"grasp_target","contact_count":904.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53651,0.00099,0.10011]},{"body_a":"world","body_b":"grasp_target","contact_count":596.0,"contact_point_centroid":[0.56697,0.04725,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63405,0.14382,0.26059]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56697,0.04725,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63686,0.15104,0.2404]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.56697,0.04725,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.63382,0.15002,0.29922]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2674.0,"contact_point_centroid":[0.53109,-0.01786,0.05112],"force_p95":0.09709,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09918,"mean_force":0.07613,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5301,0.00088,0.05393]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2939.0,"contact_point_centroid":[0.53072,0.01956,0.05087],"force_p95":0.09167,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09177,"mean_force":0.06995,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5301,0.00088,0.05393]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3126.0,"contact_point_centroid":[0.59038,0.08703,0.23254],"force_p95":0.01116,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01606,"mean_force":0.01053,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.59003,0.08703,0.23028]},{"body_a":"left_finger","body_b":"right_finger","contact_count":643.0,"contact_point_centroid":[0.6345,0.14382,0.26272],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01094,"mean_force":0.01035,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63404,0.1438,0.26063]}],"total_contact_groups":17},"final_pose_error":0.01581,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.56697,0.04725,0.01602],"final_tcp_position":[0.63427,0.15008,0.34383],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273009.26576,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":546.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2180.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_objective","tcp_end":[0.53704,0.00099,0.13661],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11083,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":226.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":32.82503,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":904.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53839,0.00103,0.06407],"tcp_start":[0.53704,0.00099,0.13661],"tcp_to_object_dist_end":0.03851,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54423,0.0009,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25039,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13111,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7413.0,"raw_peak_contact_force":0.15317,"tcp_end":[0.53007,0.00088,0.05389],"tcp_start":[0.53839,0.00103,0.06407],"tcp_to_object_dist_end":0.03138,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.5318,0.00081,0.11163],"object_pos_start":[0.54423,0.0009,0.02588],"object_to_goal_dist_end":0.21087,"object_to_goal_dist_start":0.25039,"object_z_max":0.11152,"peak_contact_force":0.11352,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12609.0,"raw_peak_contact_force":0.30536,"tcp_end":[0.52601,0.00082,0.14794],"tcp_start":[0.53007,0.00088,0.05389],"tcp_to_object_dist_end":0.03677,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56697,0.04725,0.01602],"object_pos_start":[0.5318,0.00081,0.11163],"object_to_goal_dist_end":0.22236,"object_to_goal_dist_start":0.21087,"object_z_max":0.12063,"peak_contact_force":273009.26576,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8593.0,"raw_peak_contact_force":1.61229,"tcp_end":[0.62929,0.13691,0.28095],"tcp_start":[0.52601,0.00082,0.14794],"tcp_to_object_dist_end":0.28655,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":149.0,"n_steps_budget":1000.0,"object_pos_end":[0.56697,0.04725,0.01602],"object_pos_start":[0.56697,0.04725,0.01602],"object_to_goal_dist_end":0.22236,"object_to_goal_dist_start":0.22236,"object_z_max":0.01602,"peak_contact_force":273007.54167,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1239.0,"raw_peak_contact_force":0.12263,"subtask_id":"placement_objective","tcp_end":[0.64021,0.15186,0.24108],"tcp_start":[0.62929,0.13691,0.28095],"tcp_to_object_dist_end":0.25877,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56697,0.04725,0.01602],"object_pos_start":[0.56697,0.04725,0.01602],"object_to_goal_dist_end":0.22236,"object_to_goal_dist_start":0.22236,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63574,0.15065,0.25956],"tcp_start":[0.64021,0.15186,0.24108],"tcp_to_object_dist_end":0.27337,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.56697,0.04725,0.01602],"object_pos_start":[0.56697,0.04725,0.01602],"object_to_goal_dist_end":0.22236,"object_to_goal_dist_start":0.22236,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63427,0.15008,0.34383],"tcp_start":[0.63574,0.15065,0.25956],"tcp_to_object_dist_end":0.35009,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86525,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_place.place_offset_z":0.05879,"lift.lift_height":0.11133,"lift.lift_speed":0.09893,"transport_to_goal.transport_speed":0.28812},"optimized_scores":{"best_composite_score":0.26387,"best_fitness_score":0.64387,"best_task_score":0.38317},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3145.0,"contact_point_centroid":[0.53884,0.08745,-0.00227],"force_p95":0.12469,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.23965,"mean_force":0.13407,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55909,0.1124,0.18843]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6258.0,"contact_point_centroid":[0.51581,0.0109,0.09665],"force_p95":0.13054,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33552,"mean_force":0.09682,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51262,0.02925,0.10019]},{"body_a":"world","body_b":"grasp_target","contact_count":148.0,"contact_point_centroid":[0.52785,0.0288,-0.00119],"force_p95":0.21962,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29301,"mean_force":0.05456,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51512,0.0294,0.05615]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6380.0,"contact_point_centroid":[0.51574,0.04755,0.09691],"force_p95":0.13019,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2884,"mean_force":0.09523,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51267,0.02925,0.10049]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1143.0,"contact_point_centroid":[0.5231,0.02254,0.15047],"force_p95":0.16453,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2359,"mean_force":0.11304,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51746,0.04075,0.15564]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53054,0.03071,-0.0021],"force_p95":0.15207,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20527,"mean_force":0.12977,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51792,0.02959,0.05572]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1300.0,"contact_point_centroid":[0.52326,0.05951,0.15085],"force_p95":0.12549,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1808,"mean_force":0.09698,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51787,0.04159,0.15593]},{"body_a":"world","body_b":"grasp_target","contact_count":2136.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51092,0.01384,0.21815]},{"body_a":"world","body_b":"grasp_target","contact_count":920.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52342,0.02903,0.10038]},{"body_a":"world","body_b":"grasp_target","contact_count":552.0,"contact_point_centroid":[0.53885,0.08749,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59183,0.16828,0.193]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53885,0.08749,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59057,0.17215,0.17276]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.53885,0.08749,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.58625,0.17069,0.23308]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2477.0,"contact_point_centroid":[0.5181,0.01077,0.05159],"force_p95":0.10493,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11125,"mean_force":0.08118,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51675,0.02952,0.05436]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2993.0,"contact_point_centroid":[0.5172,0.04817,0.05124],"force_p95":0.09456,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09465,"mean_force":0.06918,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51676,0.02952,0.05436]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3045.0,"contact_point_centroid":[0.56258,0.11753,0.19321],"force_p95":0.01113,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01644,"mean_force":0.01052,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56217,0.11751,0.19091]},{"body_a":"left_finger","body_b":"right_finger","contact_count":584.0,"contact_point_centroid":[0.59248,0.16829,0.19528],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.01051,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59183,0.16827,0.19305]}],"total_contact_groups":17},"final_pose_error":0.01498,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.53885,0.08749,0.01602],"final_tcp_position":[0.58651,0.17072,0.27775],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.23965,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":535.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2136.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_objective","tcp_end":[0.52426,0.02818,0.13729],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11147,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":230.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":920.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52487,0.03005,0.06401],"tcp_start":[0.52426,0.02818,0.13729],"tcp_to_object_dist_end":0.03841,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53046,0.02988,0.02567],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18427,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14835,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7270.0,"raw_peak_contact_force":0.20527,"tcp_end":[0.51672,0.02952,0.05432],"tcp_start":[0.52487,0.03005,0.06401],"tcp_to_object_dist_end":0.03177,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.51828,0.02947,0.11655],"object_pos_start":[0.53046,0.02988,0.02567],"object_to_goal_dist_end":0.17099,"object_to_goal_dist_start":0.18427,"object_z_max":0.11644,"peak_contact_force":0.1141,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12786.0,"raw_peak_contact_force":0.33552,"tcp_end":[0.51278,0.02926,0.15337],"tcp_start":[0.51672,0.02952,0.05432],"tcp_to_object_dist_end":0.03723,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53885,0.08749,0.01602],"object_pos_start":[0.51828,0.02947,0.11655],"object_to_goal_dist_end":0.14389,"object_to_goal_dist_start":0.17099,"object_z_max":0.11912,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8633.0,"raw_peak_contact_force":1.23965,"tcp_end":[0.59019,0.16404,0.2134],"tcp_start":[0.51278,0.02926,0.15337],"tcp_to_object_dist_end":0.21784,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":138.0,"n_steps_budget":1000.0,"object_pos_end":[0.53885,0.08749,0.01602],"object_pos_start":[0.53885,0.08749,0.01602],"object_to_goal_dist_end":0.14389,"object_to_goal_dist_start":0.14389,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1136.0,"raw_peak_contact_force":0.12263,"subtask_id":"placement_objective","tcp_end":[0.59489,0.17341,0.17226],"tcp_start":[0.59019,0.16404,0.2134],"tcp_to_object_dist_end":0.18691,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53885,0.08749,0.01602],"object_pos_start":[0.53885,0.08749,0.01602],"object_to_goal_dist_end":0.14389,"object_to_goal_dist_start":0.14389,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58902,0.1716,0.19249],"tcp_start":[0.59489,0.17341,0.17226],"tcp_to_object_dist_end":0.20183,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.53885,0.08749,0.01602],"object_pos_start":[0.53885,0.08749,0.01602],"object_to_goal_dist_end":0.14389,"object_to_goal_dist_start":0.14389,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58651,0.17072,0.27775],"tcp_start":[0.58902,0.1716,0.19249],"tcp_to_object_dist_end":0.27875,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```