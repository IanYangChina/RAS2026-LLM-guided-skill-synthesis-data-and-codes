## Search State

- **Seed**: 3
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.3147 | 0.94 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3802 | 0.95 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.4008 | 1.00 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.0777 | 0.48 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3766 | 0.95 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.94). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.315) — your mutation base

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
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_1
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
    - 0.02
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_z_offset:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: descend_1
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: place_object
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
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    place_z_offset:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **place_object** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.315
- **task_score** (E): 0.944
- **fitness_score**: 0.935  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.620

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0942 |
| descend_1 | 1.00 | 1.00 | 0.1597 |
| grasp_1 | 1.00 | 1.00 | 0.0128 |
| lift_1 | 1.00 | 1.00 | 0.1787 |
| transport_to_goal | 1.00 | 1.00 | 0.2194 |
| place_object | 1.00 | 1.00 | 0.1135 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.504, -0.001, 0.215) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.504, -0.001, 0.215)→(0.506, 0.002, 0.056) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 40.114 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.002, 0.056)→(0.498, 0.001, 0.046) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 44.000 | 0.148 | 0.199 |
| lift_1 | lift | 1.00 / step_budget | (0.498, 0.001, 0.046)→(0.495, 0.001, 0.225) | (0.511, 0.002, 0.026)→(0.502, 0.002, 0.199) | 0.246→0.237 | 1.00 / 38.333 | 0.086 | 0.406 |
| transport_to_goal | approach | 1.00 / step_budget | (0.495, 0.001, 0.225)→(0.616, 0.170, 0.276) | (0.502, 0.002, 0.199)→(0.621, 0.170, 0.246) | 0.237→0.110 | 1.00 / 26.667 | 0.100 | 0.134 |
| place_object | descend | 1.00 / step_budget | (0.616, 0.170, 0.276)→(0.621, 0.178, 0.163) | (0.621, 0.170, 0.246)→(0.624, 0.178, 0.131) | 0.110→0.019 | 1.00 / 25.667 | 0.109 | 0.248 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.322
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.362
- phase_breakdown.approach_1_score: 0.006
- phase_breakdown.release_1_score: 0.635
- phase_breakdown.descend_1_score: 0.862
- phase_breakdown.transport_arc_score: 0.055
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.963

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.963
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.343
- **K-run variance**: 0.0016
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at upper bound**: approach_1.approach_height
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.15634,"average_solve_count":339.0,"average_success_count":339.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12882,"approach_1.approach_speed":0.06159,"descend_1.descend_speed":0.03056,"descend_1.grasp_z_offset":0.01119,"grasp_1.grasp_time":0.76248,"lift_1.lift_height":0.11816,"lift_1.lift_speed":0.05743,"place_object.place_speed":0.05342,"place_object.place_z_offset":-0.00958,"transport_to_goal.transport_speed":0.06738},"optimized_scores":{"best_composite_score":0.25759,"best_fitness_score":0.87759,"best_task_score":0.8331},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.45615,-0.02503,-0.00147],"force_p95":0.32707,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38026,"mean_force":0.10008,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44679,-0.0251,0.04994]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2014.0,"contact_point_centroid":[0.6261,0.21938,0.18359],"force_p95":0.13716,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28878,"mean_force":0.10643,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.62145,0.20106,0.18745]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2094.0,"contact_point_centroid":[0.62606,0.18283,0.18593],"force_p95":0.13918,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2874,"mean_force":0.10319,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.6214,0.20097,0.18951]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6420.0,"contact_point_centroid":[0.44465,-0.04398,0.09769],"force_p95":0.08629,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27428,"mean_force":0.05578,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44456,-0.025,0.09695]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5496.0,"contact_point_centroid":[0.44543,-0.00583,0.09784],"force_p95":0.09217,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2703,"mean_force":0.06397,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44456,-0.025,0.09728]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45859,-0.02624,-0.0021],"force_p95":0.15133,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20697,"mean_force":0.1301,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44883,-0.02517,0.04968]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12174.0,"contact_point_centroid":[0.52681,0.09908,0.19264],"force_p95":0.11735,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20204,"mean_force":0.0789,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52566,0.08022,0.19434]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15689.0,"contact_point_centroid":[0.52448,0.05987,0.19258],"force_p95":0.09922,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16604,"mean_force":0.06103,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5241,0.07834,0.19339]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4099.0,"contact_point_centroid":[0.44871,-0.00592,0.04935],"force_p95":0.07939,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14705,"mean_force":0.05217,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44779,-0.02513,0.04868]},{"body_a":"world","body_b":"grasp_target","contact_count":1004.0,"contact_point_centroid":[0.45856,-0.02632,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12311,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48164,-0.01036,0.24048]},{"body_a":"world","body_b":"grasp_target","contact_count":1012.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45823,-0.0235,0.11857]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4956.0,"contact_point_centroid":[0.4479,-0.04422,0.04958],"force_p95":0.07072,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07346,"mean_force":0.04413,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4478,-0.02513,0.04869]}],"total_contact_groups":12},"final_pose_error":0.0196,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62955,0.20416,0.08704],"final_tcp_position":[0.62438,0.20486,0.12297],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.38026,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":252.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1004.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.46261,-0.02183,0.17745],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15155,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":253.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1012.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45554,-0.02539,0.05651],"tcp_start":[0.46261,-0.02183,0.17745],"tcp_to_object_dist_end":0.03065,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45851,-0.02548,0.02563],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30315,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14858,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10855.0,"raw_peak_contact_force":0.20697,"subtask_id":"grasp_1","tcp_end":[0.44776,-0.02513,0.04865],"tcp_start":[0.45554,-0.02539,0.05651],"tcp_to_object_dist_end":0.02541,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":321.0,"n_steps_budget":1000.0,"object_pos_end":[0.45225,-0.02525,0.12191],"object_pos_start":[0.45851,-0.02548,0.02563],"object_to_goal_dist_end":0.29361,"object_to_goal_dist_start":0.30315,"object_z_max":0.12163,"peak_contact_force":0.10548,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11996.0,"raw_peak_contact_force":0.38026,"tcp_end":[0.44434,-0.02497,0.14724],"tcp_start":[0.44776,-0.02513,0.04865],"tcp_to_object_dist_end":0.02653,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62548,0.19764,0.21696],"object_pos_start":[0.45225,-0.02525,0.12191],"object_to_goal_dist_end":0.10349,"object_to_goal_dist_start":0.29361,"object_z_max":0.21689,"peak_contact_force":0.12994,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27863.0,"raw_peak_contact_force":0.20204,"subtask_id":"transport_arc","tcp_end":[0.61999,0.19789,0.25053],"tcp_start":[0.44434,-0.02497,0.14724],"tcp_to_object_dist_end":0.03402,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":230.0,"n_steps_budget":1000.0,"object_pos_end":[0.62955,0.20416,0.08704],"object_pos_start":[0.62548,0.19764,0.21696],"object_to_goal_dist_end":0.02739,"object_to_goal_dist_start":0.10349,"object_z_max":0.21696,"peak_contact_force":0.12521,"phase_name":"place_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4108.0,"raw_peak_contact_force":0.28878,"subtask_id":"release_1","tcp_end":[0.62438,0.20486,0.12297],"tcp_start":[0.61999,0.19789,0.25053],"tcp_to_object_dist_end":0.03631,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.92889,"average_solve_count":450.0,"average_success_count":450.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13655,"approach_1.approach_speed":0.08363,"descend_1.descend_speed":0.03051,"descend_1.grasp_z_offset":0.01056,"grasp_1.grasp_time":0.85821,"lift_1.lift_height":0.2268,"lift_1.lift_speed":0.03637,"place_object.place_speed":0.02348,"place_object.place_z_offset":0.02693,"transport_to_goal.transport_speed":0.04333},"optimized_scores":{"best_composite_score":0.34309,"best_fitness_score":0.96309,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":94.0,"contact_point_centroid":[0.54054,0.00099,-0.00145],"force_p95":0.37995,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3949,"mean_force":0.15125,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52821,0.00083,0.04558]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15606.0,"contact_point_centroid":[0.52653,0.01992,0.14536],"force_p95":0.07597,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25305,"mean_force":0.05189,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52575,0.00079,0.14324]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14784.0,"contact_point_centroid":[0.52637,-0.01836,0.14715],"force_p95":0.07796,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25213,"mean_force":0.05418,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52576,0.00079,0.145]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2177.0,"contact_point_centroid":[0.64379,0.13214,0.28573],"force_p95":0.10125,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22326,"mean_force":0.07299,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.6402,0.15079,0.28668]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2319.0,"contact_point_centroid":[0.6444,0.16958,0.28559],"force_p95":0.09816,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22145,"mean_force":0.07053,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.64022,0.15082,0.28618]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.0011,-0.00204],"force_p95":0.1327,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16048,"mean_force":0.12567,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53059,0.00088,0.04609]},{"body_a":"world","body_b":"grasp_target","contact_count":968.0,"contact_point_centroid":[0.54431,0.00113,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12313,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5157,0.00043,0.24272]},{"body_a":"world","body_b":"grasp_target","contact_count":1032.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53467,0.00094,0.12073]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5076.0,"contact_point_centroid":[0.5303,-0.01839,0.04774],"force_p95":0.06561,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09929,"mean_force":0.04308,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52939,0.00086,0.04468]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12281.0,"contact_point_centroid":[0.58177,0.05443,0.28668],"force_p95":0.08286,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09374,"mean_force":0.05487,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58068,0.0734,0.2864]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11972.0,"contact_point_centroid":[0.58222,0.09185,0.28667],"force_p95":0.08265,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09373,"mean_force":0.05597,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58027,0.07286,0.28612]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5366.0,"contact_point_centroid":[0.52993,0.02009,0.04733],"force_p95":0.06408,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08154,"mean_force":0.04108,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52939,0.00086,0.04468]}],"total_contact_groups":12},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64938,0.1547,0.20749],"final_tcp_position":[0.64296,0.15468,0.23702],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":243.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":968.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.5336,0.0009,0.18326],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1576,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":258.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1032.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.5382,0.00102,0.05543],"tcp_start":[0.5336,0.0009,0.18326],"tcp_to_object_dist_end":0.03004,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54422,0.00093,0.02585],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.2504,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13197,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12242.0,"raw_peak_contact_force":0.16048,"subtask_id":"grasp_1","tcp_end":[0.52936,0.00086,0.04465],"tcp_start":[0.5382,0.00102,0.05543],"tcp_to_object_dist_end":0.02396,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":764.0,"n_steps_budget":1000.0,"object_pos_end":[0.53369,0.00092,0.22745],"object_pos_start":[0.54422,0.00093,0.02585],"object_to_goal_dist_end":0.19749,"object_to_goal_dist_start":0.2504,"object_z_max":0.22719,"peak_contact_force":0.07588,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":30484.0,"raw_peak_contact_force":0.3949,"tcp_end":[0.52648,0.0008,0.2519],"tcp_start":[0.52936,0.00086,0.04465],"tcp_to_object_dist_end":0.02549,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":692.0,"n_steps_budget":1000.0,"object_pos_end":[0.6424,0.1478,0.29868],"object_pos_start":[0.53369,0.00092,0.22745],"object_to_goal_dist_end":0.10819,"object_to_goal_dist_start":0.19749,"object_z_max":0.2986,"peak_contact_force":0.08537,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24253.0,"raw_peak_contact_force":0.09374,"subtask_id":"transport_arc","tcp_end":[0.63869,0.14783,0.32661],"tcp_start":[0.52648,0.0008,0.2519],"tcp_to_object_dist_end":0.02818,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":169.0,"n_steps_budget":1000.0,"object_pos_end":[0.64938,0.1547,0.20749],"object_pos_start":[0.6424,0.1478,0.29868],"object_to_goal_dist_end":0.01683,"object_to_goal_dist_start":0.10819,"object_z_max":0.29868,"peak_contact_force":0.09544,"phase_name":"place_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4496.0,"raw_peak_contact_force":0.22326,"subtask_id":"release_1","tcp_end":[0.64296,0.15468,0.23702],"tcp_start":[0.63869,0.14783,0.32661],"tcp_to_object_dist_end":0.03022,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95325,"average_solve_count":385.0,"average_success_count":385.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.24999,"approach_1.approach_speed":0.05297,"descend_1.descend_speed":0.01054,"descend_1.grasp_z_offset":0.01001,"grasp_1.grasp_time":0.4852,"lift_1.lift_height":0.24979,"lift_1.lift_speed":0.05524,"place_object.place_speed":0.08998,"place_object.place_z_offset":0.00331,"transport_to_goal.transport_speed":0.01116},"optimized_scores":{"best_composite_score":0.34342,"best_fitness_score":0.96342,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.52748,0.02836,-0.00153],"force_p95":0.39683,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44356,"mean_force":0.11654,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.515,0.02862,0.04572]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16768.0,"contact_point_centroid":[0.51356,0.04756,0.15707],"force_p95":0.07962,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29893,"mean_force":0.05279,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51276,0.02847,0.15519]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15148.0,"contact_point_centroid":[0.51353,0.00932,0.15985],"force_p95":0.08105,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27121,"mean_force":0.05675,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51278,0.02847,0.15808]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3478.0,"contact_point_centroid":[0.59313,0.18739,0.18835],"force_p95":0.1272,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23307,"mean_force":0.07226,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.59252,0.16882,0.18933]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53057,0.03061,-0.00217],"force_p95":0.16843,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23004,"mean_force":0.13493,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51741,0.02878,0.04572]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3510.0,"contact_point_centroid":[0.59231,0.14974,0.18975],"force_p95":0.13308,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21801,"mean_force":0.08125,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.59245,0.16871,0.19041]},{"body_a":"world","body_b":"grasp_target","contact_count":304.0,"contact_point_centroid":[0.5305,0.03079,-0.00159],"force_p95":0.13831,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12444,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50721,0.00804,0.29272]},{"body_a":"world","body_b":"grasp_target","contact_count":1816.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12259,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51953,0.02344,0.17007]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4625.0,"contact_point_centroid":[0.51711,0.00954,0.04694],"force_p95":0.07442,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11595,"mean_force":0.04645,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51624,0.02871,0.04439]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7276.0,"contact_point_centroid":[0.5523,0.11219,0.26138],"force_p95":0.08489,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10598,"mean_force":0.06016,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5497,0.09329,0.26148]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7405.0,"contact_point_centroid":[0.55131,0.07425,0.26101],"force_p95":0.08571,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10343,"mean_force":0.05957,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54962,0.09316,0.26149]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5054.0,"contact_point_centroid":[0.51713,0.04802,0.04618],"force_p95":0.07523,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07788,"mean_force":0.04442,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51625,0.02871,0.0444]}],"total_contact_groups":12},"final_pose_error":0.01957,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59197,0.17374,0.0998],"final_tcp_position":[0.59574,0.17449,0.12964],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":39.07825,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":77.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02594],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.1834,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.1223,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":304.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.51618,0.01788,0.28406],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25884,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":454.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02594],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.1834,"object_z_max":0.02602,"peak_contact_force":39.07825,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1816.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.52487,0.02923,0.05461],"tcp_start":[0.51618,0.01788,0.28406],"tcp_to_object_dist_end":0.02919,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53048,0.02939,0.0254],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18478,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.16265,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11479.0,"raw_peak_contact_force":0.23004,"subtask_id":"grasp_1","tcp_end":[0.51621,0.02871,0.04435],"tcp_start":[0.52487,0.02923,0.05461],"tcp_to_object_dist_end":0.02373,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":819.0,"n_steps_budget":1000.0,"object_pos_end":[0.52021,0.02884,0.24912],"object_pos_start":[0.53048,0.02939,0.0254],"object_to_goal_dist_end":0.22119,"object_to_goal_dist_start":0.18478,"object_z_max":0.24886,"peak_contact_force":0.0765,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32008.0,"raw_peak_contact_force":0.44356,"tcp_end":[0.51361,0.02852,0.27457],"tcp_start":[0.51621,0.02871,0.04435],"tcp_to_object_dist_end":0.02629,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":460.0,"n_steps_budget":1000.0,"object_pos_end":[0.59486,0.16336,0.22373],"object_pos_start":[0.52021,0.02884,0.24912],"object_to_goal_dist_end":0.11683,"object_to_goal_dist_start":0.22119,"object_z_max":0.24929,"peak_contact_force":0.08608,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14681.0,"raw_peak_contact_force":0.10598,"subtask_id":"transport_arc","tcp_end":[0.59051,0.16332,0.25181],"tcp_start":[0.51361,0.02852,0.27457],"tcp_to_object_dist_end":0.02841,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":218.0,"n_steps_budget":1000.0,"object_pos_end":[0.59197,0.17374,0.0998],"object_pos_start":[0.59486,0.16336,0.22373],"object_to_goal_dist_end":0.01355,"object_to_goal_dist_start":0.11683,"object_z_max":0.22373,"peak_contact_force":0.10782,"phase_name":"place_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6988.0,"raw_peak_contact_force":0.23307,"subtask_id":"release_1","tcp_end":[0.59574,0.17449,0.12964],"tcp_start":[0.59051,0.16332,0.25181],"tcp_to_object_dist_end":0.03009,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```