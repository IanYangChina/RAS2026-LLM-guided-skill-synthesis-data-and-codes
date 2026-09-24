## Search State

- **Seed**: 3
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | 0.2595 | 0.32 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.3553 | 0.42 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.2541 | 0.39 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.2890 | 0.28 | ❌ rejected |
| 4 | approach → descend → grasp → approach → release | linear_cartesian | linear_cartesian | — | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 1 | 0.4518 | 0.39 | ✅ accepted |

**Proposal policy**: task_score is 0.32 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach_1 | object | (0.00, 0.00, 0.00) | distance | approach_height |
| descend_1 | object | (0.00, 0.00, 0.02) | distance | grasp_z_offset |
| grasp_1 | object | (0.00, 0.00, 0.02) | contact | — |
| transport_arc | goal | (0.00, 0.00, 0.00) | distance | — |
| release_1 | goal | (0.00, 0.00, 0.00) | distance | — |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.259) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
phases:
- id: approach_1
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  subtask_id: approach_1
- id: descend_1
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
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  subtask_id: descend_1
- id: grasp_1
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
  subtask_id: grasp_1
- id: lift_1
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
- id: transport_arc
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.arc_height
        mode: replace
  subtask_id: transport_arc
- id: descend_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_offset:
      type: scalar
      range:
      - -0.02
      - 0.04
      default: 0.01
      binds_to:
      - path: target.offset.z
        mode: replace
- id: release_1
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
  subtask_id: release_1
- id: retract_1
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_offset: status=consumed; consumers=target.offset.z (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.259
- **task_score** (E): 0.324
- **fitness_score**: 0.639  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2662 |
| descend_1 | 1.00 | 1.00 | 0.0017 |
| grasp_1 | 1.00 | 1.00 | 0.0117 |
| lift_1 | 1.00 | 1.00 | 0.0968 |
| transport_arc | 1.00 | 1.00 | 0.2179 |
| descend_place | 1.00 | 1.00 | 0.1337 |
| release_1 | 1.00 | 1.00 | 0.0221 |
| retract_1 | 1.00 | 1.00 | 0.1304 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.038) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.002, 0.038)→(0.506, 0.002, 0.038) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.002, 0.038)→(0.498, 0.002, 0.030) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 43.333 | 0.147 | 0.212 |
| lift_1 | lift | 1.00 / step_budget | (0.498, 0.002, 0.030)→(0.494, 0.002, 0.126) | (0.511, 0.002, 0.026)→(0.512, 0.002, 0.118) | 0.246→0.219 | 1.00 / 24.667 | 524.436 | 0.644 |
| transport_arc | approach | 1.00 / step_budget | (0.494, 0.002, 0.126)→(0.614, 0.167, 0.187) | (0.512, 0.002, 0.118)→(0.549, 0.089, 0.016) | 0.219→0.175 | 1.00 / 8.000 | 0.123 | 1.689 |
| descend_place | descend | 1.00 / step_budget | (0.614, 0.167, 0.187)→(0.620, 0.178, 0.054) | (0.549, 0.089, 0.016)→(0.549, 0.089, 0.016) | 0.175→0.175 | 1.00 / 22.333 | 182124.111 | 1.980 |
| release_1 | release | 1.00 / step_budget | (0.620, 0.178, 0.054)→(0.613, 0.176, 0.075) | (0.549, 0.089, 0.016)→(0.549, 0.089, 0.016) | 0.175→0.175 | 1.00 / 5.333 | 0.162 | 1.618 |
| retract_1 | retract | 1.00 / step_budget | (0.613, 0.176, 0.075)→(0.610, 0.174, 0.205) | (0.549, 0.089, 0.016)→(0.549, 0.089, 0.016) | 0.175→0.176 | 1.00 / 4.000 | 0.123 | 0.359 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.462
- phase_score: 0.483
- phase_breakdown.release_1_score: 0.170
- phase_breakdown.descend_1_score: 0.766
- phase_breakdown.transport_arc_score: 0.345
- phase_breakdown.approach_1_score: 0.819
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.708

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.708
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.462
- **Median Q (composite search score)**: 0.233
- **K-run variance**: 0.0024
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.374


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71616,"average_solve_count":229.0,"average_success_count":229.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_place.place_z_offset":-0.10654,"lift_1.lift_height":0.11508,"transport_arc.arc_height":0.44833,"transport_arc.transport_height":0.05552},"optimized_scores":{"best_composite_score":0.23339,"best_fitness_score":0.61339,"best_task_score":0.26694},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1948.0,"contact_point_centroid":[0.52309,0.07318,-0.00251],"force_p95":0.18047,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.80152,"mean_force":0.15105,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.56121,0.12523,0.18771]},{"body_a":"world","body_b":"grasp_target","contact_count":75.0,"contact_point_centroid":[0.45559,-0.02434,-0.00145],"force_p95":0.59297,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62803,"mean_force":0.15096,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44627,-0.02469,0.033]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5759.0,"contact_point_centroid":[0.44488,-0.04368,0.07868],"force_p95":0.08558,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3052,"mean_force":0.05442,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44413,-0.02459,0.07692]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2965.0,"contact_point_centroid":[0.46821,-0.01632,0.15098],"force_p95":0.16159,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27627,"mean_force":0.09476,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.46258,0.00219,0.15002]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5333.0,"contact_point_centroid":[0.44482,-0.00543,0.07921],"force_p95":0.09168,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27181,"mean_force":0.05763,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44416,-0.02459,0.07683]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3007.0,"contact_point_centroid":[0.4705,0.0235,0.15309],"force_p95":0.14137,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27173,"mean_force":0.09387,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.46477,0.00502,0.15218]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45861,-0.02609,-0.00214],"force_p95":0.16345,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2389,"mean_force":0.13356,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44855,-0.02477,0.03255]},{"body_a":"world","body_b":"grasp_target","contact_count":3172.0,"contact_point_centroid":[0.45856,-0.02632,-0.00195],"force_p95":0.12742,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47724,-0.01234,0.16848]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5256.0,"contact_point_centroid":[0.44681,-0.00548,0.03288],"force_p95":0.06889,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12752,"mean_force":0.04118,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44746,-0.02473,0.03151]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45536,-0.02487,0.03859]},{"body_a":"world","body_b":"grasp_target","contact_count":996.0,"contact_point_centroid":[0.52295,0.07354,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61857,0.19866,0.09834]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52295,0.07354,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61579,0.20183,0.02409]},{"body_a":"world","body_b":"grasp_target","contact_count":2104.0,"contact_point_centroid":[0.52295,0.07354,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.60937,0.19955,0.10842]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5471.0,"contact_point_centroid":[0.44689,-0.04406,0.03279],"force_p95":0.06861,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08396,"mean_force":0.04137,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44747,-0.02473,0.03151]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1853.0,"contact_point_centroid":[0.56742,0.13241,0.1901],"force_p95":0.01154,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01633,"mean_force":0.01063,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.56699,0.13241,0.18782]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1076.0,"contact_point_centroid":[0.61908,0.1987,0.10042],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01262,"mean_force":0.01033,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61859,0.19869,0.09799]}],"total_contact_groups":17},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.52295,0.07354,0.01602],"final_tcp_position":[0.60972,0.19962,0.17404],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273006.8648,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":794.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3172.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45654,-0.0248,0.03961],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01383,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":80.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45465,-0.02496,0.03838],"tcp_start":[0.45654,-0.0248,0.03961],"tcp_to_object_dist_end":0.01304,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45847,-0.02497,0.02549],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30281,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.15768,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12527.0,"raw_peak_contact_force":0.2389,"subtask_id":"grasp_1","tcp_end":[0.44743,-0.02473,0.03148],"tcp_start":[0.45465,-0.02496,0.03838],"tcp_to_object_dist_end":0.01256,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":286.0,"n_steps_budget":750.0,"object_pos_end":[0.46058,-0.02459,0.11888],"object_pos_start":[0.45847,-0.02497,0.02549],"object_to_goal_dist_end":0.28804,"object_to_goal_dist_start":0.30281,"object_z_max":0.11859,"peak_contact_force":1573.09317,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11167.0,"raw_peak_contact_force":0.62803,"tcp_end":[0.4439,-0.02456,0.12707],"tcp_start":[0.44743,-0.02473,0.03148],"tcp_to_object_dist_end":0.01859,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":858.0,"n_steps_budget":1000.0,"object_pos_end":[0.52295,0.07354,0.01602],"object_pos_start":[0.46058,-0.02459,0.11888],"object_to_goal_dist_end":0.19811,"object_to_goal_dist_start":0.28804,"object_z_max":0.15591,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9773.0,"raw_peak_contact_force":1.80152,"subtask_id":"transport_arc","tcp_end":[0.61643,0.19404,0.16893],"tcp_start":[0.4439,-0.02456,0.12707],"tcp_to_object_dist_end":0.21596,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":249.0,"n_steps_budget":1000.0,"object_pos_end":[0.52295,0.07354,0.01602],"object_pos_start":[0.52295,0.07354,0.01602],"object_to_goal_dist_end":0.19811,"object_to_goal_dist_start":0.19811,"object_z_max":0.01602,"peak_contact_force":273006.8648,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2072.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62295,0.20416,0.02579],"tcp_start":[0.61643,0.19404,0.16893],"tcp_to_object_dist_end":0.16479,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52295,0.07354,0.01602],"object_pos_start":[0.52295,0.07354,0.01602],"object_to_goal_dist_end":0.19811,"object_to_goal_dist_start":0.19811,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1029.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.61341,0.20098,0.04357],"tcp_start":[0.62295,0.20416,0.02579],"tcp_to_object_dist_end":0.1587,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":526.0,"n_steps_budget":930.0,"object_pos_end":[0.52295,0.07354,0.01602],"object_pos_start":[0.52295,0.07354,0.01602],"object_to_goal_dist_end":0.19811,"object_to_goal_dist_start":0.19811,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2104.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60972,0.19962,0.17404],"tcp_start":[0.61341,0.20098,0.04357],"tcp_to_object_dist_end":0.21999,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71921,"average_solve_count":203.0,"average_success_count":203.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_place.place_z_offset":-0.0658,"lift_1.lift_height":0.11154,"transport_arc.arc_height":0.4197,"transport_arc.transport_height":0.05437},"optimized_scores":{"best_composite_score":0.21727,"best_fitness_score":0.59727,"best_task_score":0.24134},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1676.0,"contact_point_centroid":[0.56308,0.07087,-0.00254],"force_p95":0.28249,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.63501,"mean_force":0.15123,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.59603,0.0951,0.21858]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.54096,0.00074,-0.00133],"force_p95":0.58609,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65589,"mean_force":0.1453,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52843,0.00084,0.02994]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4523.0,"contact_point_centroid":[0.52859,-0.01812,0.07166],"force_p95":0.10893,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33616,"mean_force":0.07207,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52579,0.00079,0.06935]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4811.0,"contact_point_centroid":[0.52865,0.01962,0.06958],"force_p95":0.10808,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31732,"mean_force":0.06863,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52584,0.00079,0.06765]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2529.0,"contact_point_centroid":[0.54012,-0.00271,0.14513],"force_p95":0.17414,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28875,"mean_force":0.09826,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53428,0.0157,0.1451]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2430.0,"contact_point_centroid":[0.54099,0.03546,0.14713],"force_p95":0.18599,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27457,"mean_force":0.10387,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53525,0.017,0.14701]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.001,-0.00203],"force_p95":0.13207,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15816,"mean_force":0.12536,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53097,0.00089,0.0301]},{"body_a":"world","body_b":"grasp_target","contact_count":3396.0,"contact_point_centroid":[0.54431,0.00113,-0.00195],"force_p95":0.12666,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51757,0.0005,0.16671]},{"body_a":"world","body_b":"grasp_target","contact_count":460.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53687,0.00098,0.03671]},{"body_a":"world","body_b":"grasp_target","contact_count":644.0,"contact_point_centroid":[0.56279,0.07081,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.63788,0.14937,0.19146]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56279,0.07081,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63591,0.15263,0.14181]},{"body_a":"world","body_b":"grasp_target","contact_count":2112.0,"contact_point_centroid":[0.56279,0.07081,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.63137,0.1513,0.22568]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4114.0,"contact_point_centroid":[0.53077,-0.01834,0.03134],"force_p95":0.07612,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11516,"mean_force":0.05176,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52971,0.00087,0.02865]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4879.0,"contact_point_centroid":[0.53071,0.01994,0.03046],"force_p95":0.06816,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09124,"mean_force":0.04476,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52971,0.00087,0.02865]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1538.0,"contact_point_centroid":[0.60141,0.10129,0.22465],"force_p95":0.01178,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01652,"mean_force":0.01062,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.60092,0.10129,0.22224]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.6394,0.1535,0.14008],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.00999,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63879,0.15348,0.1382]}],"total_contact_groups":17},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.56279,0.07081,0.01602],"final_tcp_position":[0.63196,0.15139,0.29131],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273006.30534,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":850.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3396.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53728,0.00099,0.03696],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.013,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":115.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":460.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.538,0.00101,0.03829],"tcp_start":[0.53728,0.00099,0.03696],"tcp_to_object_dist_end":0.01379,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54417,0.00074,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25052,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13006,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15816,"subtask_id":"grasp_1","tcp_end":[0.52968,0.00086,0.02862],"tcp_start":[0.538,0.00101,0.03829],"tcp_to_object_dist_end":0.01474,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":309.0,"n_steps_budget":720.0,"object_pos_end":[0.5443,0.00083,0.11315],"object_pos_start":[0.54417,0.00074,0.02588],"object_to_goal_dist_end":0.20367,"object_to_goal_dist_start":0.25052,"object_z_max":0.1129,"peak_contact_force":0.10918,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9412.0,"raw_peak_contact_force":0.65589,"tcp_end":[0.52553,0.0008,0.12074],"tcp_start":[0.52968,0.00086,0.02862],"tcp_to_object_dist_end":0.02025,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":741.0,"n_steps_budget":1000.0,"object_pos_end":[0.56279,0.07081,0.01602],"object_pos_start":[0.5443,0.00083,0.11315],"object_to_goal_dist_end":0.21323,"object_to_goal_dist_start":0.20367,"object_z_max":0.15378,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8173.0,"raw_peak_contact_force":1.63501,"subtask_id":"transport_arc","tcp_end":[0.63576,0.14521,0.23603],"tcp_start":[0.52553,0.0008,0.12074],"tcp_to_object_dist_end":0.24344,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":161.0,"n_steps_budget":1000.0,"object_pos_end":[0.56279,0.07081,0.01602],"object_pos_start":[0.56279,0.07081,0.01602],"object_to_goal_dist_end":0.21323,"object_to_goal_dist_start":0.21323,"object_z_max":0.01602,"peak_contact_force":273006.30534,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1323.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6412,0.15395,0.14365],"tcp_start":[0.63576,0.14521,0.23603],"tcp_to_object_dist_end":0.17133,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56279,0.07081,0.01602],"object_pos_start":[0.56279,0.07081,0.01602],"object_to_goal_dist_end":0.21323,"object_to_goal_dist_start":0.21323,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.63415,0.15211,0.16113],"tcp_start":[0.6412,0.15395,0.14365],"tcp_to_object_dist_end":0.18099,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":528.0,"n_steps_budget":930.0,"object_pos_end":[0.56279,0.07081,0.01602],"object_pos_start":[0.56279,0.07081,0.01602],"object_to_goal_dist_end":0.21323,"object_to_goal_dist_start":0.21323,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2112.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63196,0.15139,0.29131],"tcp_start":[0.63415,0.15211,0.16113],"tcp_to_object_dist_end":0.29507,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72727,"average_solve_count":209.0,"average_success_count":209.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_place.place_z_offset":-0.13313,"lift_1.lift_height":0.12195,"transport_arc.arc_height":0.34743,"transport_arc.transport_height":0.05307},"optimized_scores":{"best_composite_score":0.3278,"best_fitness_score":0.7078,"best_task_score":0.4623},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"right_finger","contact_count":370.0,"contact_point_centroid":[0.59485,0.17734,-0.00295],"force_p95":4.77779,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5.6955,"mean_force":3.30809,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59488,0.17431,-0.00083]},{"body_a":"world","body_b":"left_finger","contact_count":367.0,"contact_point_centroid":[0.59483,0.17102,-0.00294],"force_p95":4.76852,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5.66707,"mean_force":3.30132,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59488,0.17431,-0.00086]},{"body_a":"world","body_b":"right_finger","contact_count":2446.0,"contact_point_centroid":[0.59597,0.17781,-0.00396],"force_p95":2.9184,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4.60763,"mean_force":1.47791,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59617,0.17459,-0.00441]},{"body_a":"world","body_b":"left_finger","contact_count":2438.0,"contact_point_centroid":[0.59597,0.17132,-0.00394],"force_p95":2.90544,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4.57821,"mean_force":1.49999,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59617,0.17459,-0.00443]},{"body_a":"world","body_b":"grasp_target","contact_count":740.0,"contact_point_centroid":[0.56126,0.12352,-0.00327],"force_p95":0.66594,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.63011,"mean_force":0.18784,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.57237,0.1347,0.16192]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":277.0,"contact_point_centroid":[0.58467,0.13949,0.02338],"force_p95":0.4564,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.83105,"mean_force":0.10669,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.59014,0.17282,0.02693]},{"body_a":"world","body_b":"grasp_target","contact_count":1752.0,"contact_point_centroid":[0.56051,0.11907,-0.00223],"force_p95":0.29207,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.78721,"mean_force":0.14724,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58795,0.17208,0.09152]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.52743,0.0284,-0.00143],"force_p95":0.60986,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64781,"mean_force":0.1383,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5148,0.02929,0.03056]},{"body_a":"grasp_target","body_b":"hand","contact_count":78.0,"contact_point_centroid":[0.59346,0.10756,0.03476],"force_p95":0.05344,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33801,"mean_force":0.03922,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59623,0.17464,-0.00676]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4844.0,"contact_point_centroid":[0.5152,0.01022,0.07681],"force_p95":0.11024,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32835,"mean_force":0.07277,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51231,0.02912,0.07448]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5197.0,"contact_point_centroid":[0.51519,0.04796,0.07439],"force_p95":0.10835,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32732,"mean_force":0.06933,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51234,0.02912,0.07252]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2267.0,"contact_point_centroid":[0.52969,0.03425,0.14317],"force_p95":0.1899,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32613,"mean_force":0.10025,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52373,0.05261,0.14351]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2150.0,"contact_point_centroid":[0.53102,0.07382,0.14416],"force_p95":0.17351,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26819,"mean_force":0.10612,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52532,0.05538,0.14473]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56109,0.12382,-0.00204],"force_p95":0.14416,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24069,"mean_force":0.12544,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59535,0.17434,0.00101]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.0305,-0.00213],"force_p95":0.16074,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23973,"mean_force":0.13272,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51739,0.02947,0.03052]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":30.0,"contact_point_centroid":[0.58669,0.14616,0.01937],"force_p95":0.19212,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1985,"mean_force":0.13904,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59239,0.17345,0.0188]}],"total_contact_groups":25},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.56054,0.12169,0.01602],"final_tcp_position":[0.58824,0.17214,0.15079],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":359.16192,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":839.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3352.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52425,0.02897,0.03757],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01326,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":81.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":324.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52424,0.02992,0.03829],"tcp_start":[0.52425,0.02897,0.03757],"tcp_to_object_dist_end":0.01381,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5304,0.02943,0.02557],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18471,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15272,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10859.0,"raw_peak_contact_force":0.23973,"subtask_id":"grasp_1","tcp_end":[0.51612,0.02938,0.0291],"tcp_start":[0.52424,0.02992,0.03829],"tcp_to_object_dist_end":0.01471,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":336.0,"n_steps_budget":780.0,"object_pos_end":[0.53097,0.02932,0.12272],"object_pos_start":[0.5304,0.02943,0.02557],"object_to_goal_dist_end":0.16575,"object_to_goal_dist_start":0.18471,"object_z_max":0.12246,"peak_contact_force":0.10711,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10121.0,"raw_peak_contact_force":0.64781,"tcp_end":[0.51215,0.02912,0.13157],"tcp_start":[0.51612,0.02938,0.0291],"tcp_to_object_dist_end":0.02079,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":481.0,"n_steps_budget":1000.0,"object_pos_end":[0.56118,0.12377,0.01602],"object_pos_start":[0.53097,0.02932,0.12272],"object_to_goal_dist_end":0.1145,"object_to_goal_dist_start":0.16575,"object_z_max":0.13678,"peak_contact_force":0.12268,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5657.0,"raw_peak_contact_force":1.63011,"subtask_id":"transport_arc","tcp_end":[0.58945,0.16316,0.15749],"tcp_start":[0.51215,0.02912,0.13157],"tcp_to_object_dist_end":0.14955,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":49.0,"n_steps":297.0,"n_steps_budget":1000.0,"object_pos_end":[0.56122,0.12378,0.01597],"object_pos_start":[0.56118,0.12377,0.01602],"object_to_goal_dist_end":0.11452,"object_to_goal_dist_start":0.1145,"object_z_max":0.01602,"peak_contact_force":359.16192,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3206.0,"raw_peak_contact_force":5.6955,"tcp_end":[0.59582,0.17475,-0.0065],"tcp_start":[0.58945,0.16316,0.15749],"tcp_to_object_dist_end":0.06557,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56089,0.12298,0.01649],"object_pos_start":[0.56122,0.12378,0.01597],"object_to_goal_dist_end":0.11461,"object_to_goal_dist_start":0.11452,"object_z_max":0.01642,"peak_contact_force":0.24069,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":6145.0,"raw_peak_contact_force":4.60763,"subtask_id":"release_1","tcp_end":[0.59224,0.17341,0.02027],"tcp_start":[0.59582,0.17475,-0.0065],"tcp_to_object_dist_end":0.0595,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":502.0,"n_steps_budget":960.0,"object_pos_end":[0.56054,0.12169,0.01602],"object_pos_start":[0.56089,0.12298,0.01649],"object_to_goal_dist_end":0.11573,"object_to_goal_dist_start":0.11461,"object_z_max":0.02089,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2029.0,"raw_peak_contact_force":0.83105,"tcp_end":[0.58824,0.17214,0.15079],"tcp_start":[0.59224,0.17341,0.02027],"tcp_to_object_dist_end":0.14655,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```