## Search State

- **Seed**: 3
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | -0.2148 | 0.20 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.2851 | 0.27 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | 0.2595 | 0.32 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.3553 | 0.42 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.2541 | 0.39 | ❌ rejected |

**Proposal policy**: task_score is 0.20 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.215) — your mutation base

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

- **Composite score**: -0.215
- **task_score** (E): 0.201
- **fitness_score**: 0.165  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.1309 |
| descend_1 | 0.00 | 1.00 | 0.0377 |
| grasp_1 | 1.00 | 1.00 | 0.0000 |
| lift_1 | 0.33 | 1.00 | 0.1403 |
| transport_arc | 0.00 | 1.00 | 0.1497 |
| descend_place | 0.00 | 1.00 | 0.0687 |
| release_1 | 1.00 | 1.00 | 0.0269 |
| retract_1 | 1.00 | 1.00 | 0.1302 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.428, 0.000, 0.191) | (0.511, 0.002, 0.030)→(0.474, 0.012, 0.016) | 0.244→0.263 | 1.00 / 5.000 | 192.165 | 1386.135 |
| descend_1 | descend | 0.00 / step_budget | (0.428, 0.000, 0.191)→(0.451, 0.005, 0.215) | (0.474, 0.012, 0.016)→(0.474, 0.012, 0.016) | 0.263→0.263 | 1.00 / 5.000 | 381.924 | 853.848 |
| grasp_1 | grasp | 1.00 / step_budget | (0.451, 0.005, 0.214)→(0.451, 0.005, 0.214) | (0.474, 0.012, 0.016)→(0.474, 0.012, 0.016) | 0.263→0.263 | 1.00 / 9.333 | 91048.944 | 239.042 |
| lift_1 | lift | 0.33 / step_budget | (0.451, 0.005, 0.214)→(0.442, 0.005, 0.354) | (0.474, 0.012, 0.016)→(0.474, 0.012, 0.016) | 0.263→0.263 | 1.00 / 8.667 | 91002.840 | 156.814 |
| transport_arc | approach | 0.00 / step_budget | (0.442, 0.005, 0.354)→(0.539, 0.113, 0.323) | (0.474, 0.012, 0.016)→(0.474, 0.012, 0.016) | 0.263→0.263 | 1.00 / 9.000 | 241.560 | 774.686 |
| descend_place | descend | 0.00 / step_budget | (0.539, 0.113, 0.323)→(0.588, 0.143, 0.294) | (0.474, 0.012, 0.016)→(0.495, 0.009, 0.019) | 0.263→0.253 | 1.00 / 9.333 | 217.706 | 707.537 |
| release_1 | release | 1.00 / step_budget | (0.588, 0.143, 0.294)→(0.589, 0.143, 0.321) | (0.495, 0.009, 0.019)→(0.494, 0.008, 0.019) | 0.253→0.253 | 1.00 / 4.333 | 29.444 | 129.483 |
| retract_1 | retract | 1.00 / step_budget | (0.589, 0.143, 0.321)→(0.590, 0.143, 0.451) | (0.494, 0.008, 0.019)→(0.494, 0.008, 0.019) | 0.253→0.253 | 1.00 / 4.000 | 0.123 | 17.771 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.306
- phase_score: 0.159
- phase_breakdown.release_1_score: 0.013
- phase_breakdown.descend_1_score: 0.027
- phase_breakdown.transport_arc_score: 0.007
- phase_breakdown.approach_1_score: 0.020
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.218

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.218
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.306
- **Median Q (composite search score)**: -0.220
- **K-run variance**: 0.0017
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.7
- **Final σ (mean)**: 0.254


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":12.0,"average_failure_rate":0.08696,"average_mean_iterations":22.54348,"average_solve_count":138.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_place.descend_offset":0.01278,"lift_1.lift_height":0.13519,"transport_arc.arc_height":0.35802,"transport_arc.transport_speed":0.56918},"optimized_scores":{"best_composite_score":-0.26275,"best_fitness_score":0.11725,"best_task_score":0.10998},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.62967,-0.00281,-0.00046],"force_p95":199.53814,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1336.46311,"mean_force":200.19129,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39372,-0.00292,0.13228]},{"body_a":"world","body_b":"link6","contact_count":999.0,"contact_point_centroid":[0.60805,-0.00886,-0.00024],"force_p95":405.38906,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":822.90498,"mean_force":238.04488,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4103,-0.01144,0.18841]},{"body_a":"link5","body_b":"hand","contact_count":74.0,"contact_point_centroid":[0.54375,0.03864,0.23872],"force_p95":632.14955,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":755.41558,"mean_force":396.3758,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52284,0.12726,0.2769]},{"body_a":"world","body_b":"link6","contact_count":925.0,"contact_point_centroid":[0.57334,0.133,-0.00029],"force_p95":546.90796,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":706.28896,"mean_force":394.30424,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56412,0.14061,0.29349]},{"body_a":"world","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.52707,0.00312,-0.00299],"force_p95":21.1865,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":423.73007,"mean_force":21.1865,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37155,-0.00131,0.0513]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.61504,-0.01519,-0.00014],"force_p95":107.35506,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":277.82577,"mean_force":80.05988,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44523,-0.01943,0.2226]},{"body_a":"link5","body_b":"hand","contact_count":3.0,"contact_point_centroid":[0.54632,0.04668,0.22631],"force_p95":205.3765,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":205.43005,"mean_force":185.491,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.54093,0.12935,0.28694]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.61518,-0.01522,-0.00011],"force_p95":135.41496,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":138.24098,"mean_force":112.31137,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44523,-0.01945,0.22257]},{"body_a":"world","body_b":"link6","contact_count":84.0,"contact_point_centroid":[0.60443,0.14862,-0.00013],"force_p95":77.74435,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":122.44844,"mean_force":57.37776,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58899,0.15988,0.2936]},{"body_a":"grasp_target","body_b":"hand","contact_count":38.0,"contact_point_centroid":[0.44072,-0.02354,0.04351],"force_p95":3.52082,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.9217,"mean_force":1.46141,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38197,-0.00127,0.05348]},{"body_a":"world","body_b":"grasp_target","contact_count":3919.0,"contact_point_centroid":[0.42224,-0.0256,-0.00212],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.24299,"mean_force":0.13758,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40548,-0.00268,0.14109]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.41705,-0.02548,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.41031,-0.01145,0.18844]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.41705,-0.02548,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44523,-0.01943,0.2226]},{"body_a":"world","body_b":"grasp_target","contact_count":2488.0,"contact_point_centroid":[0.41705,-0.02548,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44064,-0.01966,0.28286]},{"body_a":"world","body_b":"grasp_target","contact_count":1496.0,"contact_point_centroid":[0.41705,-0.02548,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.47552,0.04867,0.28051]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.41705,-0.02548,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56356,0.13947,0.29327]}],"total_contact_groups":23},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.41705,-0.02548,0.01602],"final_tcp_position":[0.5907,0.15886,0.45019],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273004.12078,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41705,-0.02548,0.01602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.33112,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":192.69641,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4863.0,"raw_peak_contact_force":1336.46311,"subtask_id":"approach_1","tcp_end":[0.40829,-0.00554,0.16849],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15402,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41705,-0.02548,0.01602],"object_pos_start":[0.41705,-0.02548,0.01602],"object_to_goal_dist_end":0.33112,"object_to_goal_dist_start":0.33112,"object_z_max":0.01602,"peak_contact_force":392.06494,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4999.0,"raw_peak_contact_force":822.90498,"subtask_id":"descend_1","tcp_end":[0.44543,-0.01938,0.2233],"tcp_start":[0.40829,-0.00554,0.16849],"tcp_to_object_dist_end":0.2093,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.41705,-0.02548,0.01602],"object_pos_start":[0.41705,-0.02548,0.01602],"object_to_goal_dist_end":0.33112,"object_to_goal_dist_start":0.33112,"object_z_max":0.01602,"peak_contact_force":273004.12078,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3499.0,"raw_peak_contact_force":277.82577,"subtask_id":"grasp_1","tcp_end":[0.44524,-0.01945,0.22254],"tcp_start":[0.44524,-0.01944,0.22254],"tcp_to_object_dist_end":0.20852,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":622.0,"n_steps_budget":870.0,"object_pos_end":[0.41705,-0.02548,0.01602],"object_pos_start":[0.41705,-0.02548,0.01602],"object_to_goal_dist_end":0.33112,"object_to_goal_dist_start":0.33112,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5112.0,"raw_peak_contact_force":138.24098,"tcp_end":[0.43704,-0.01992,0.3262],"tcp_start":[0.44524,-0.01945,0.22254],"tcp_to_object_dist_end":0.31087,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":374.0,"n_steps_budget":1000.0,"object_pos_end":[0.41705,-0.02548,0.01602],"object_pos_start":[0.41705,-0.02548,0.01602],"object_to_goal_dist_end":0.33112,"object_to_goal_dist_start":0.33112,"object_z_max":0.01602,"peak_contact_force":162.82149,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3180.0,"raw_peak_contact_force":755.41558,"subtask_id":"transport_arc","tcp_end":[0.54039,0.12944,0.28658],"tcp_start":[0.43704,-0.01992,0.3262],"tcp_to_object_dist_end":0.33529,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41705,-0.02548,0.01602],"object_pos_start":[0.41705,-0.02548,0.01602],"object_to_goal_dist_end":0.33112,"object_to_goal_dist_start":0.33112,"object_z_max":0.01602,"peak_contact_force":135.26809,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9252.0,"raw_peak_contact_force":706.28896,"tcp_end":[0.58891,0.16022,0.29321],"tcp_start":[0.54039,0.12944,0.28658],"tcp_to_object_dist_end":0.3753,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.41705,-0.02548,0.01602],"object_pos_start":[0.41705,-0.02548,0.01602],"object_to_goal_dist_end":0.33112,"object_to_goal_dist_start":0.33112,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1105.0,"raw_peak_contact_force":122.44844,"subtask_id":"release_1","tcp_end":[0.58922,0.15964,0.32006],"tcp_start":[0.58891,0.16022,0.29321],"tcp_to_object_dist_end":0.39541,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":456.0,"n_steps_budget":930.0,"object_pos_end":[0.41705,-0.02548,0.01602],"object_pos_start":[0.41705,-0.02548,0.01602],"object_to_goal_dist_end":0.33112,"object_to_goal_dist_start":0.33112,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1824.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5907,0.15886,0.45019],"tcp_start":[0.58922,0.15964,0.32006],"tcp_to_object_dist_end":0.50263,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":12.0,"average_failure_rate":0.07643,"average_mean_iterations":21.11465,"average_solve_count":157.0,"average_success_count":145.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_place.descend_offset":0.00909,"lift_1.lift_height":0.23698,"transport_arc.arc_height":0.2842,"transport_arc.transport_speed":0.59103},"optimized_scores":{"best_composite_score":-0.21956,"best_fitness_score":0.16044,"best_task_score":0.18753},"replay_outcomes":[{"contacts":{"omitted_contact_groups":12,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.63375,0.00084,-0.00045],"force_p95":206.40882,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1409.13685,"mean_force":199.93692,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40977,2e-05,0.15025]},{"body_a":"world","body_b":"link6","contact_count":999.0,"contact_point_centroid":[0.60957,0.00266,-0.00023],"force_p95":465.37872,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":883.79351,"mean_force":287.47668,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.42525,0.0019,0.20682]},{"body_a":"link5","body_b":"hand","contact_count":140.0,"contact_point_centroid":[0.55137,0.01635,0.29883],"force_p95":663.73766,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":814.87665,"mean_force":410.42395,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52797,0.08615,0.34372]},{"body_a":"world","body_b":"link6","contact_count":779.0,"contact_point_centroid":[0.59812,0.12453,-0.00036],"force_p95":591.04762,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":748.03716,"mean_force":360.68508,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.53683,0.11533,0.24551]},{"body_a":"link5","body_b":"hand","contact_count":335.0,"contact_point_centroid":[0.57314,0.18719,0.21842],"force_p95":249.67499,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":527.87027,"mean_force":102.95063,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.46408,0.18839,0.18196]},{"body_a":"world","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.50393,0.09511,-0.00021],"force_p95":396.81847,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":432.54888,"mean_force":310.09188,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.40606,0.14271,0.11618]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.64313,0.01238,-0.00014],"force_p95":95.10085,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":205.36107,"mean_force":75.6128,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45522,0.00504,0.2075]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.64327,0.01236,-0.0001],"force_p95":168.20348,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":171.40463,"mean_force":129.22559,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45521,0.00503,0.20744]},{"body_a":"world","body_b":"link6","contact_count":83.0,"contact_point_centroid":[0.59429,0.12782,-9e-05],"force_p95":80.0269,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":137.74866,"mean_force":53.62022,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60222,0.12266,0.29418]},{"body_a":"grasp_target","body_b":"link6","contact_count":333.0,"contact_point_centroid":[0.53854,0.01746,0.03214],"force_p95":0.7777,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.63692,"mean_force":0.35907,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39273,-6e-05,0.1137]},{"body_a":"grasp_target","body_b":"link7","contact_count":338.0,"contact_point_centroid":[0.5258,0.00499,0.03324],"force_p95":1.14674,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.95831,"mean_force":0.44976,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39321,-6e-05,0.11084]},{"body_a":"grasp_target","body_b":"hand","contact_count":84.0,"contact_point_centroid":[0.49658,0.01268,0.04459],"force_p95":2.52081,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.02905,"mean_force":1.05127,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38472,-0.00015,0.07449]},{"body_a":"world","body_b":"grasp_target","contact_count":3749.0,"contact_point_centroid":[0.51258,0.009,-0.00218],"force_p95":0.25821,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.57454,"mean_force":0.1489,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.42164,5e-05,0.15999]},{"body_a":"grasp_target","body_b":"link7","contact_count":76.0,"contact_point_centroid":[0.49103,0.01295,0.03869],"force_p95":0.98782,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.23681,"mean_force":0.65221,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.40746,-0.0052,0.15777]},{"body_a":"world","body_b":"grasp_target","contact_count":3828.0,"contact_point_centroid":[0.53022,0.00258,-0.00212],"force_p95":0.256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73899,"mean_force":0.13795,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5288,0.12509,0.2394]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5067,0.01066,-0.00199],"force_p95":0.13971,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15026,"mean_force":0.12293,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.42528,0.0019,0.20682]}],"total_contact_groups":28},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.55055,-0.00428,0.02602],"final_tcp_position":[0.6033,0.12451,0.45122],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273004.12076,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5071,0.0106,0.01602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.26862,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":190.70521,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5410.0,"raw_peak_contact_force":1409.13685,"subtask_id":"approach_1","tcp_end":[0.44091,0.00018,0.2053],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20079,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50661,0.01068,0.01602],"object_pos_start":[0.5071,0.0106,0.01602],"object_to_goal_dist_end":0.26883,"object_to_goal_dist_start":0.26862,"object_z_max":0.0161,"peak_contact_force":371.36103,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5147.0,"raw_peak_contact_force":883.79351,"subtask_id":"descend_1","tcp_end":[0.45535,0.00504,0.20836],"tcp_start":[0.44091,0.00018,0.2053],"tcp_to_object_dist_end":0.19914,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50661,0.01068,0.01602],"object_pos_start":[0.50661,0.01068,0.01602],"object_to_goal_dist_end":0.26883,"object_to_goal_dist_start":0.26883,"object_z_max":0.01602,"peak_contact_force":71.2028,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3502.0,"raw_peak_contact_force":205.36107,"subtask_id":"grasp_1","tcp_end":[0.45522,0.00503,0.2074],"tcp_start":[0.45522,0.00503,0.2074],"tcp_to_object_dist_end":0.19824,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50661,0.01068,0.01602],"object_pos_start":[0.50661,0.01068,0.01602],"object_to_goal_dist_end":0.26883,"object_to_goal_dist_start":0.26883,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8235.0,"raw_peak_contact_force":171.40463,"tcp_end":[0.44602,0.0052,0.3673],"tcp_start":[0.45522,0.00503,0.2074],"tcp_to_object_dist_end":0.35651,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":362.0,"n_steps_budget":1000.0,"object_pos_end":[0.50661,0.01068,0.01602],"object_pos_start":[0.50661,0.01068,0.01602],"object_to_goal_dist_end":0.26883,"object_to_goal_dist_start":0.26883,"object_z_max":0.01602,"peak_contact_force":278.75716,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3145.0,"raw_peak_contact_force":814.87665,"subtask_id":"transport_arc","tcp_end":[0.54338,0.08883,0.34214],"tcp_start":[0.44602,0.0052,0.3673],"tcp_to_object_dist_end":0.33736,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55055,-0.00428,0.02602],"object_pos_start":[0.50661,0.01068,0.01602],"object_to_goal_dist_end":0.25107,"object_to_goal_dist_start":0.26883,"object_z_max":0.02969,"peak_contact_force":103.67313,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9306.0,"raw_peak_contact_force":748.03716,"tcp_end":[0.60225,0.1225,0.29386],"tcp_start":[0.54338,0.08883,0.34214],"tcp_to_object_dist_end":0.30081,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55055,-0.00428,0.02602],"object_pos_start":[0.55055,-0.00428,0.02602],"object_to_goal_dist_end":0.25107,"object_to_goal_dist_start":0.25107,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1101.0,"raw_peak_contact_force":137.74866,"subtask_id":"release_1","tcp_end":[0.60229,0.12306,0.32093],"tcp_start":[0.60225,0.1225,0.29386],"tcp_to_object_dist_end":0.32537,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":449.0,"n_steps_budget":960.0,"object_pos_end":[0.55055,-0.00428,0.02602],"object_pos_start":[0.55055,-0.00428,0.02602],"object_to_goal_dist_end":0.25107,"object_to_goal_dist_start":0.25107,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1796.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6033,0.12451,0.45122],"tcp_start":[0.60229,0.12306,0.32093],"tcp_to_object_dist_end":0.4474,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":12.0,"average_failure_rate":0.07595,"average_mean_iterations":20.50633,"average_solve_count":158.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_place.descend_offset":0.00883,"lift_1.lift_height":0.21803,"transport_arc.arc_height":0.22341,"transport_arc.transport_speed":0.75259},"optimized_scores":{"best_composite_score":-0.16203,"best_fitness_score":0.21797,"best_task_score":0.30582},"replay_outcomes":[{"contacts":{"omitted_contact_groups":15,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.63264,0.00381,-0.00046],"force_p95":207.004,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1412.80358,"mean_force":201.21912,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40716,0.00332,0.14783]},{"body_a":"world","body_b":"link6","contact_count":996.0,"contact_point_centroid":[0.60594,0.01286,-0.00023],"force_p95":442.97099,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":854.84522,"mean_force":290.42019,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.42244,0.01542,0.20793]},{"body_a":"link5","body_b":"hand","contact_count":149.0,"contact_point_centroid":[0.54902,0.04503,0.30769],"force_p95":576.10626,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":753.76455,"mean_force":383.95115,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52607,0.11712,0.35273]},{"body_a":"world","body_b":"link6","contact_count":681.0,"contact_point_centroid":[0.55175,0.12598,-0.00032],"force_p95":597.85444,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":668.28437,"mean_force":463.90811,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.561,0.13883,0.2936]},{"body_a":"link5","body_b":"hand","contact_count":963.0,"contact_point_centroid":[0.48229,0.07528,0.24936],"force_p95":249.31396,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":302.30986,"mean_force":135.47842,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55239,0.13434,0.30353]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.63839,0.02159,-0.00014],"force_p95":97.03343,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":233.93881,"mean_force":76.35969,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45219,0.0283,0.21159]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.63854,0.02152,-0.0001],"force_p95":157.71416,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":160.79647,"mean_force":122.33992,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45218,0.02826,0.21153]},{"body_a":"world","body_b":"link6","contact_count":83.0,"contact_point_centroid":[0.5745,0.13553,-0.00011],"force_p95":78.86348,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":128.25068,"mean_force":55.87534,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57269,0.14473,0.29446]},{"body_a":"link5","body_b":"hand","contact_count":164.0,"contact_point_centroid":[0.50366,0.07862,0.24342],"force_p95":87.64108,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":88.08634,"mean_force":44.25108,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57305,0.14482,0.30226]},{"body_a":"link5","body_b":"hand","contact_count":16.0,"contact_point_centroid":[0.50705,0.07963,0.26034],"force_p95":24.59159,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":53.06719,"mean_force":9.50672,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.57419,0.14529,0.32228]},{"body_a":"grasp_target","body_b":"link7","contact_count":128.0,"contact_point_centroid":[0.49647,0.01846,0.03696],"force_p95":3.64482,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.53844,"mean_force":0.7972,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38577,0.00117,0.08589]},{"body_a":"grasp_target","body_b":"hand","contact_count":123.0,"contact_point_centroid":[0.49534,0.03831,0.05485],"force_p95":2.20243,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.80798,"mean_force":0.86827,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.3853,0.00116,0.08523]},{"body_a":"world","body_b":"grasp_target","contact_count":3619.0,"contact_point_centroid":[0.50303,0.04641,-0.00223],"force_p95":0.34799,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.22838,"mean_force":0.15755,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4203,0.00324,0.15937]},{"body_a":"grasp_target","body_b":"link6","contact_count":710.0,"contact_point_centroid":[0.491,0.08391,0.03156],"force_p95":0.23331,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.11646,"mean_force":0.17634,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56026,0.13847,0.29378]},{"body_a":"grasp_target","body_b":"link6","contact_count":108.0,"contact_point_centroid":[0.53717,0.03406,0.0314],"force_p95":0.92947,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.04425,"mean_force":0.47403,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38296,0.00117,0.08937]},{"body_a":"grasp_target","body_b":"link5","contact_count":696.0,"contact_point_centroid":[0.52036,0.03195,0.03142],"force_p95":0.29045,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.76251,"mean_force":0.25014,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56063,0.13865,0.29365]}],"total_contact_groups":31},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.51478,0.05376,0.01602],"final_tcp_position":[0.57545,0.1454,0.45113],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273008.27577,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49796,0.04978,0.01602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18919,"object_to_goal_dist_start":0.18162,"object_z_max":0.03017,"peak_contact_force":193.09404,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4884.0,"raw_peak_contact_force":1412.80358,"subtask_id":"approach_1","tcp_end":[0.4357,0.00678,0.20038],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19929,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49796,0.04978,0.01602],"object_pos_start":[0.49796,0.04978,0.01602],"object_to_goal_dist_end":0.18919,"object_to_goal_dist_start":0.18919,"object_z_max":0.01602,"peak_contact_force":382.34747,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4996.0,"raw_peak_contact_force":854.84522,"subtask_id":"descend_1","tcp_end":[0.45233,0.02836,0.2124],"tcp_start":[0.4357,0.00678,0.20038],"tcp_to_object_dist_end":0.20275,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.49796,0.04978,0.01602],"object_pos_start":[0.49796,0.04978,0.01602],"object_to_goal_dist_end":0.18919,"object_to_goal_dist_start":0.18919,"object_z_max":0.01602,"peak_contact_force":71.5078,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3508.0,"raw_peak_contact_force":233.93881,"subtask_id":"grasp_1","tcp_end":[0.45219,0.02826,0.21149],"tcp_start":[0.45219,0.02827,0.21149],"tcp_to_object_dist_end":0.20191,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49796,0.04978,0.01602],"object_pos_start":[0.49796,0.04978,0.01602],"object_to_goal_dist_end":0.18919,"object_to_goal_dist_start":0.18919,"object_z_max":0.01602,"peak_contact_force":273008.27577,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8223.0,"raw_peak_contact_force":160.79647,"tcp_end":[0.44204,0.02999,0.368],"tcp_start":[0.45219,0.02826,0.21149],"tcp_to_object_dist_end":0.35694,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":396.0,"n_steps_budget":1000.0,"object_pos_end":[0.49796,0.04978,0.01602],"object_pos_start":[0.49796,0.04978,0.01602],"object_to_goal_dist_end":0.18919,"object_to_goal_dist_start":0.18919,"object_z_max":0.01602,"peak_contact_force":283.10179,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3449.0,"raw_peak_contact_force":753.76455,"subtask_id":"transport_arc","tcp_end":[0.53386,0.1214,0.34088],"tcp_start":[0.44204,0.02999,0.368],"tcp_to_object_dist_end":0.33459,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51725,0.05572,0.01397],"object_pos_start":[0.49796,0.04978,0.01602],"object_to_goal_dist_end":0.17623,"object_to_goal_dist_start":0.18919,"object_z_max":0.01602,"peak_contact_force":414.17759,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10986.0,"raw_peak_contact_force":668.28437,"tcp_end":[0.57267,0.14487,0.29414],"tcp_start":[0.53386,0.1214,0.34088],"tcp_to_object_dist_end":0.29919,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51475,0.05372,0.01604],"object_pos_start":[0.51725,0.05572,0.01397],"object_to_goal_dist_end":0.17775,"object_to_goal_dist_start":0.17623,"object_z_max":0.01606,"peak_contact_force":88.08634,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1408.0,"raw_peak_contact_force":128.25068,"subtask_id":"release_1","tcp_end":[0.57415,0.14526,0.32087],"tcp_start":[0.57267,0.14487,0.29414],"tcp_to_object_dist_end":0.32377,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":454.0,"n_steps_budget":960.0,"object_pos_end":[0.51478,0.05376,0.01602],"object_pos_start":[0.51475,0.05372,0.01604],"object_to_goal_dist_end":0.17772,"object_to_goal_dist_start":0.17775,"object_z_max":0.01604,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1832.0,"raw_peak_contact_force":53.06719,"tcp_end":[0.57545,0.1454,0.45113],"tcp_start":[0.57415,0.14526,0.32087],"tcp_to_object_dist_end":0.44878,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```