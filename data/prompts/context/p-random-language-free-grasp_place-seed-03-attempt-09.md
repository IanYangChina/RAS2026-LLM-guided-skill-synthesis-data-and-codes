## Search State

- **Seed**: 3
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.1009 | 0.27 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.2004 | 0.21 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | force_threshold_switch | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | -0.0209 | 0.21 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.1624 | 0.37 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.1324 | 0.24 | ✅ accepted |

**Proposal policy**: task_score is 0.27 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.101) — your mutation base

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

- **Composite score**: 0.101
- **task_score** (E): 0.268
- **fitness_score**: 0.501  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.400

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1383 |
| descend_to_object | 1.00 | 1.00 | 0.1028 |
| close_gripper | 1.00 | 1.00 | 0.0126 |
| lift_object | 1.00 | 1.00 | 0.0856 |
| move_to_goal | 1.00 | 1.00 | 0.2449 |
| descend_to_place | 1.00 | 1.00 | 0.1185 |
| release_object | 1.00 | 1.00 | 0.0196 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.168) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_object | descend | 1.00 / step_budget | (0.506, 0.002, 0.168)→(0.506, 0.002, 0.065) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| close_gripper | grasp | 1.00 / step_budget | (0.506, 0.002, 0.065)→(0.498, 0.002, 0.056) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.025) | 0.246→0.246 | 1.00 / 26.000 | 0.183 | 0.210 |
| lift_object | lift | 1.00 / step_budget | (0.498, 0.002, 0.056)→(0.506, 0.002, 0.141) | (0.511, 0.002, 0.025)→(0.512, 0.001, 0.088) | 0.246→0.223 | 1.00 / 14.667 | 3249.036 | 0.316 |
| move_to_goal | approach | 1.00 / step_budget | (0.506, 0.002, 0.141)→(0.617, 0.169, 0.276) | (0.512, 0.001, 0.088)→(0.533, 0.045, 0.019) | 0.223→0.215 | 1.00 / 8.000 | 0.123 | 1.048 |
| descend_to_place | descend | 1.00 / step_budget | (0.617, 0.169, 0.276)→(0.621, 0.178, 0.158) | (0.533, 0.045, 0.019)→(0.533, 0.045, 0.019) | 0.215→0.215 | 1.00 / 8.000 | 6499.187 | 0.123 |
| release_object | release | 1.00 / step_budget | (0.621, 0.178, 0.158)→(0.615, 0.176, 0.176) | (0.533, 0.045, 0.019)→(0.533, 0.045, 0.019) | 0.215→0.215 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.429
- phase_score: 0.226
- phase_breakdown.place_at_goal_score: 0.061
- phase_breakdown.approach_grasp_score: 0.611
- grasp_place_fitness: 0.666

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.666
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.429
- **Median Q (composite search score)**: 0.173
- **K-run variance**: 0.0298
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.307


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.2906,"average_solve_count":117.0,"average_success_count":117.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.18081,"descend_to_object.descend_speed":0.19104,"descend_to_place.place_offset_z":0.00349,"lift_object.lift_offset_z":0.11127,"move_to_goal.goal_speed":0.25039},"optimized_scores":{"best_composite_score":-0.13727,"best_fitness_score":0.26273,"best_task_score":0.13112},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":592.0,"contact_point_centroid":[0.45842,-0.02293,-0.00222],"force_p95":0.25322,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35194,"mean_force":0.13902,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4499,-0.02485,0.0888]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":138.0,"contact_point_centroid":[0.45133,-0.00861,0.05286],"force_p95":0.211,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28218,"mean_force":0.12436,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44769,-0.02499,0.05912]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45863,-0.02659,-0.00229],"force_p95":0.24073,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26205,"mean_force":0.14604,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.44938,-0.02508,0.05878]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":416.0,"contact_point_centroid":[0.44741,-0.04001,0.05699],"force_p95":0.17035,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25944,"mean_force":0.06556,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44752,-0.02496,0.06165]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2517.0,"contact_point_centroid":[0.44875,-0.00651,0.05278],"force_p95":0.12279,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14017,"mean_force":0.08592,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.44837,-0.02503,0.05779]},{"body_a":"world","body_b":"grasp_target","contact_count":952.0,"contact_point_centroid":[0.45856,-0.02632,-0.00186],"force_p95":0.13699,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12314,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48136,-0.01058,0.23556]},{"body_a":"world","body_b":"grasp_target","contact_count":3252.0,"contact_point_centroid":[0.45835,-0.02759,-0.00199],"force_p95":0.12317,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12566,"mean_force":0.12263,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.52991,0.07926,0.20152]},{"body_a":"world","body_b":"grasp_target","contact_count":784.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.45847,-0.02359,0.11766]},{"body_a":"world","body_b":"grasp_target","contact_count":816.0,"contact_point_centroid":[0.45835,-0.02759,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62092,0.19968,0.19631]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.45835,-0.02759,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61903,0.20254,0.13421]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2990.0,"contact_point_centroid":[0.4482,-0.04283,0.05358],"force_p95":0.08685,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09313,"mean_force":0.06156,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.44838,-0.02503,0.0578]},{"body_a":"left_finger","body_b":"right_finger","contact_count":87.0,"contact_point_centroid":[0.45258,-0.02479,0.11428],"force_p95":0.01565,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01612,"mean_force":0.01315,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45256,-0.02479,0.11227]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3433.0,"contact_point_centroid":[0.53056,0.07988,0.2042],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.01056,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.53039,0.07989,0.20197]},{"body_a":"left_finger","body_b":"right_finger","contact_count":873.0,"contact_point_centroid":[0.62115,0.19969,0.19855],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0127,"mean_force":0.01043,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62093,0.19968,0.19627]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.62192,0.20366,0.13269],"force_p95":0.01086,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01088,"mean_force":0.00991,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62188,0.20364,0.13047]}],"total_contact_groups":15},"final_pose_error":0.01948,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.45835,-0.02759,0.02602],"final_tcp_position":[0.62428,0.20435,0.13578],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":9746.87643,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":239.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":952.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_grasp","tcp_end":[0.46241,-0.022,0.16889],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14298,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":196.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":784.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45592,-0.0253,0.06558],"tcp_start":[0.46241,-0.022,0.16889],"tcp_to_object_dist_end":0.03966,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45863,-0.02493,0.02368],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30323,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.26273,"phase_name":"close_gripper","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7307.0,"raw_peak_contact_force":0.26205,"tcp_end":[0.44836,-0.02503,0.05778],"tcp_start":[0.45592,-0.0253,0.06558],"tcp_to_object_dist_end":0.03561,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":185.0,"n_steps_budget":600.0,"object_pos_end":[0.45831,-0.02812,0.02603],"object_pos_start":[0.45863,-0.02493,0.02368],"object_to_goal_dist_end":0.30519,"object_to_goal_dist_start":0.30323,"object_z_max":0.03125,"peak_contact_force":9746.87643,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1233.0,"raw_peak_contact_force":0.35194,"subtask_id":"approach_grasp","tcp_end":[0.45306,-0.02478,0.11575],"tcp_start":[0.44836,-0.02503,0.05778],"tcp_to_object_dist_end":0.08993,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":813.0,"n_steps_budget":1000.0,"object_pos_end":[0.45835,-0.02759,0.02602],"object_pos_start":[0.45831,-0.02812,0.02603],"object_to_goal_dist_end":0.30475,"object_to_goal_dist_start":0.30519,"object_z_max":0.02603,"peak_contact_force":0.12263,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6685.0,"raw_peak_contact_force":0.12566,"subtask_id":"place_at_goal","tcp_end":[0.61881,0.1956,0.25361],"tcp_start":[0.45306,-0.02478,0.11575],"tcp_to_object_dist_end":0.35687,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":204.0,"n_steps_budget":1000.0,"object_pos_end":[0.45835,-0.02759,0.02602],"object_pos_start":[0.45835,-0.02759,0.02602],"object_to_goal_dist_end":0.30475,"object_to_goal_dist_start":0.30475,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1689.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62428,0.20435,0.13578],"tcp_start":[0.61881,0.1956,0.25361],"tcp_to_object_dist_end":0.30557,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45835,-0.02759,0.02602],"object_pos_start":[0.45835,-0.02759,0.02602],"object_to_goal_dist_end":0.30475,"object_to_goal_dist_start":0.30475,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61728,0.20187,0.15364],"tcp_start":[0.62428,0.20435,0.13578],"tcp_to_object_dist_end":0.30691,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.25862,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.35496,"descend_to_object.descend_speed":0.27364,"descend_to_place.place_offset_z":0.00685,"lift_object.lift_offset_z":0.14587,"move_to_goal.goal_speed":0.24179},"optimized_scores":{"best_composite_score":0.17344,"best_fitness_score":0.57344,"best_task_score":0.24246},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2167.0,"contact_point_centroid":[0.57315,0.06331,-0.00241],"force_p95":0.17514,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.44481,"mean_force":0.14307,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.59329,0.08238,0.27258]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":729.0,"contact_point_centroid":[0.54732,0.02438,0.16088],"force_p95":0.20655,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33822,"mean_force":0.11753,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.54123,0.00674,0.16482]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3167.0,"contact_point_centroid":[0.53548,-0.01744,0.09559],"force_p95":0.14723,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28497,"mean_force":0.10679,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53219,0.00082,0.09884]},{"body_a":"world","body_b":"grasp_target","contact_count":81.0,"contact_point_centroid":[0.54324,0.00075,-0.00131],"force_p95":0.23798,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26975,"mean_force":0.05194,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52881,0.00085,0.05562]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3171.0,"contact_point_centroid":[0.53572,0.01907,0.09643],"force_p95":0.14463,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26583,"mean_force":0.10647,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5323,0.00082,0.09961]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":548.0,"contact_point_centroid":[0.54628,-0.01291,0.15822],"force_p95":0.18441,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23362,"mean_force":0.12306,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.54048,0.00529,0.16189]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00109,-0.00203],"force_p95":0.13216,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15333,"mean_force":0.12514,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.53096,0.00089,0.05566]},{"body_a":"world","body_b":"grasp_target","contact_count":1004.0,"contact_point_centroid":[0.54431,0.00113,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12311,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51606,0.00045,0.23431]},{"body_a":"world","body_b":"grasp_target","contact_count":752.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.53547,0.00096,0.11642]},{"body_a":"world","body_b":"grasp_target","contact_count":748.0,"contact_point_centroid":[0.57319,0.06334,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64101,0.15114,0.27364]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57319,0.06334,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.63925,0.15391,0.21491]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2676.0,"contact_point_centroid":[0.531,-0.01787,0.05144],"force_p95":0.09704,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09854,"mean_force":0.07607,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.5298,0.00087,0.05428]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2934.0,"contact_point_centroid":[0.53064,0.01955,0.05119],"force_p95":0.09162,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09173,"mean_force":0.07007,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.5298,0.00087,0.05428]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2117.0,"contact_point_centroid":[0.59678,0.08701,0.2805],"force_p95":0.01145,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0165,"mean_force":0.01058,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.59657,0.08701,0.27811]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.64185,0.15464,0.21361],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.01013,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.64146,0.15462,0.21138]},{"body_a":"left_finger","body_b":"right_finger","contact_count":801.0,"contact_point_centroid":[0.64128,0.15114,0.27608],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01269,"mean_force":0.01041,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.641,0.15113,0.27384]}],"total_contact_groups":16},"final_pose_error":0.01943,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.57319,0.06334,0.01602],"final_tcp_position":[0.64328,0.15502,0.21664],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":9748.82581,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":252.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1004.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_grasp","tcp_end":[0.53434,0.00092,0.16718],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14151,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":188.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":752.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53837,0.00102,0.06497],"tcp_start":[0.53434,0.00092,0.16718],"tcp_to_object_dist_end":0.0394,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54423,0.0009,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25039,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13121,"phase_name":"close_gripper","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7410.0,"raw_peak_contact_force":0.15333,"tcp_end":[0.52977,0.00087,0.05424],"tcp_start":[0.53837,0.00102,0.06497],"tcp_to_object_dist_end":0.03183,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":342.0,"n_steps_budget":750.0,"object_pos_end":[0.54606,0.00098,0.11831],"object_pos_start":[0.54423,0.0009,0.02588],"object_to_goal_dist_end":0.20074,"object_to_goal_dist_start":0.25039,"object_z_max":0.11806,"peak_contact_force":0.11528,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6419.0,"raw_peak_contact_force":0.28497,"subtask_id":"approach_grasp","tcp_end":[0.53878,0.00083,0.15274],"tcp_start":[0.52977,0.00087,0.05424],"tcp_to_object_dist_end":0.03519,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":716.0,"n_steps_budget":1000.0,"object_pos_end":[0.57319,0.06334,0.01602],"object_pos_start":[0.54606,0.00098,0.11831],"object_to_goal_dist_end":0.21254,"object_to_goal_dist_start":0.20074,"object_z_max":0.13988,"peak_contact_force":0.12263,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5561.0,"raw_peak_contact_force":1.44481,"subtask_id":"place_at_goal","tcp_end":[0.6392,0.14758,0.32664],"tcp_start":[0.53878,0.00083,0.15274],"tcp_to_object_dist_end":0.32854,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":187.0,"n_steps_budget":1000.0,"object_pos_end":[0.57319,0.06334,0.01602],"object_pos_start":[0.57319,0.06334,0.01602],"object_to_goal_dist_end":0.21254,"object_to_goal_dist_start":0.21254,"object_z_max":0.01602,"peak_contact_force":9748.82581,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1549.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.64328,0.15502,0.21664],"tcp_start":[0.6392,0.14758,0.32664],"tcp_to_object_dist_end":0.23145,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57319,0.06334,0.01602],"object_pos_start":[0.57319,0.06334,0.01602],"object_to_goal_dist_end":0.21254,"object_to_goal_dist_start":0.21254,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63795,0.15348,0.23418],"tcp_start":[0.64328,0.15502,0.21664],"tcp_to_object_dist_end":0.24478,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.22414,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.38504,"descend_to_object.descend_speed":0.21503,"descend_to_place.place_offset_z":-0.00636,"lift_object.lift_offset_z":0.14752,"move_to_goal.goal_speed":0.44505},"optimized_scores":{"best_composite_score":0.26645,"best_fitness_score":0.66645,"best_task_score":0.42928},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1195.0,"contact_point_centroid":[0.56746,0.09789,-0.00284],"force_p95":0.40807,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.57345,"mean_force":0.16319,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.56853,0.11863,0.22779]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3306.0,"contact_point_centroid":[0.52216,0.01078,0.09713],"force_p95":0.14076,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31209,"mean_force":0.10229,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51892,0.02903,0.10027]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3151.0,"contact_point_centroid":[0.52215,0.04734,0.09722],"force_p95":0.15132,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29038,"mean_force":0.10697,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51899,0.02903,0.10059]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.52938,0.02847,-0.0014],"force_p95":0.25136,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26961,"mean_force":0.0516,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51571,0.02893,0.05616]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":783.0,"contact_point_centroid":[0.53447,0.02107,0.16114],"force_p95":0.1901,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23234,"mean_force":0.11762,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.52869,0.03926,0.16475]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53056,0.03069,-0.00213],"force_p95":0.1613,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21495,"mean_force":0.13197,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.51786,0.02908,0.05594]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":940.0,"contact_point_centroid":[0.53553,0.05925,0.16321],"force_p95":0.13151,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18776,"mean_force":0.09897,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.52958,0.04134,0.16698]},{"body_a":"world","body_b":"grasp_target","contact_count":992.0,"contact_point_centroid":[0.5305,0.03079,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12312,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51044,0.01247,0.23436]},{"body_a":"world","body_b":"grasp_target","contact_count":760.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.52305,0.02761,0.11638]},{"body_a":"world","body_b":"grasp_target","contact_count":900.0,"contact_point_centroid":[0.56759,0.0982,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59362,0.16952,0.18533]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56759,0.0982,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59067,0.17318,0.1201]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2434.0,"contact_point_centroid":[0.5183,0.01033,0.05186],"force_p95":0.10445,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11763,"mean_force":0.082,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.51672,0.02901,0.05462]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2824.0,"contact_point_centroid":[0.5178,0.04769,0.05127],"force_p95":0.10024,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10037,"mean_force":0.07325,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.51673,0.02901,0.05463]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1050.0,"contact_point_centroid":[0.57255,0.1259,0.23431],"force_p95":0.01236,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0182,"mean_force":0.01076,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.5723,0.12588,0.23203]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.59377,0.1742,0.11806],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.01013,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5936,0.17417,0.11566]},{"body_a":"left_finger","body_b":"right_finger","contact_count":954.0,"contact_point_centroid":[0.59392,0.16951,0.18805],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01268,"mean_force":0.01051,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5936,0.16949,0.18572]}],"total_contact_groups":16},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.56759,0.0982,0.01602],"final_tcp_position":[0.59607,0.17479,0.12046],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":9748.61322,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":249.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":992.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_grasp","tcp_end":[0.52269,0.02582,0.16733],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14161,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":190.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":760.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52509,0.02953,0.06479],"tcp_start":[0.52269,0.02582,0.16733],"tcp_to_object_dist_end":0.03917,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53047,0.02964,0.02557],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.1845,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15565,"phase_name":"close_gripper","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7058.0,"raw_peak_contact_force":0.21495,"tcp_end":[0.51669,0.02901,0.05459],"tcp_start":[0.52509,0.02953,0.06479],"tcp_to_object_dist_end":0.03212,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":337.0,"n_steps_budget":750.0,"object_pos_end":[0.53259,0.0296,0.11922],"object_pos_start":[0.53047,0.02964,0.02557],"object_to_goal_dist_end":0.16454,"object_to_goal_dist_start":0.1845,"object_z_max":0.11897,"peak_contact_force":0.11736,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6541.0,"raw_peak_contact_force":0.31209,"subtask_id":"approach_grasp","tcp_end":[0.52516,0.02931,0.15398],"tcp_start":[0.51669,0.02901,0.05459],"tcp_to_object_dist_end":0.03554,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":496.0,"n_steps_budget":1000.0,"object_pos_end":[0.56759,0.0982,0.01602],"object_pos_start":[0.53259,0.0296,0.11922],"object_to_goal_dist_end":0.12685,"object_to_goal_dist_start":0.16454,"object_z_max":0.14274,"peak_contact_force":0.12263,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3968.0,"raw_peak_contact_force":1.57345,"subtask_id":"place_at_goal","tcp_end":[0.59237,0.1648,0.24697],"tcp_start":[0.52516,0.02931,0.15398],"tcp_to_object_dist_end":0.24164,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":225.0,"n_steps_budget":1000.0,"object_pos_end":[0.56759,0.0982,0.01602],"object_pos_start":[0.56759,0.0982,0.01602],"object_to_goal_dist_end":0.12685,"object_to_goal_dist_start":0.12685,"object_z_max":0.01602,"peak_contact_force":9748.61322,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1854.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59607,0.17479,0.12046],"tcp_start":[0.59237,0.1648,0.24697],"tcp_to_object_dist_end":0.13261,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56759,0.0982,0.01602],"object_pos_start":[0.56759,0.0982,0.01602],"object_to_goal_dist_end":0.12685,"object_to_goal_dist_start":0.12685,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58886,0.17257,0.14001],"tcp_start":[0.59607,0.17479,0.12046],"tcp_to_object_dist_end":0.14614,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```