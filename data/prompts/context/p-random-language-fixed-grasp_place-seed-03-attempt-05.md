## Search State

- **Seed**: 3
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | 0.1426 | 0.46 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | -0.1155 | 0.43 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | 0.2522 | 0.47 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | 0.1848 | 0.48 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | 0.1851 | 0.48 | ❌ rejected |

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

## Current Skill (Q=0.143) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
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
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: approach_1
- id: descend_1
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
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
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
  guards:
  - id: grasp_check
    when: during_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
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
- id: transport_1
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
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: descend_2
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
  parameters:
    place_z_offset:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: release_1
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
  parameters:
    release_duration:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: duration.max_time
        mode: add
- id: retract_1
  type: retract
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
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1]
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03]
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=repeat
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15]
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15]
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03]
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (add)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15]
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.143
- **task_score** (E): 0.460
- **fitness_score**: 0.698  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.680

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1581 |
| descend_1 | 1.00 | 1.00 | 0.0973 |
| grasp_1 | 1.00 | 1.00 | 0.0127 |
| lift_1 | 0.67 | 1.00 | 0.1703 |
| transport_1 | 0.67 | 0.67 | 0.2139 |
| descend_2 | 1.00 | 1.00 | 0.0157 |
| release_1 | 1.00 | 1.00 | 0.0206 |
| retract_1 | 1.00 | 1.00 | 0.0347 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.148) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.002, 0.148)→(0.506, 0.002, 0.051) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.002, 0.051)→(0.497, 0.002, 0.042) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 43.000 | 0.141 | 0.179 |
| lift_1 | lift | 0.67 / step_budget | (0.497, 0.002, 0.042)→(0.505, 0.002, 0.212) | (0.511, 0.002, 0.026)→(0.515, 0.002, 0.188) | 0.246→0.223 | 1.00 / 35.333 | 0.080 | 0.494 |
| transport_1 | approach | 0.67 / step_budget | (0.505, 0.002, 0.212)→(0.609, 0.159, 0.302) | (0.515, 0.002, 0.188)→(0.605, 0.166, 0.207) | 0.223→0.095 | 0.67 / 13.333 | 0.082 | 0.521 |
| descend_2 | descend | 1.00 / force_exceeded | (0.609, 0.159, 0.302)→(0.610, 0.162, 0.287) | (0.605, 0.166, 0.207)→(0.606, 0.170, 0.173) | 0.095→0.096 | 1.00 / 14.000 | 57709.446 | 1.060 |
| release_1 | release | 1.00 / step_budget | (0.610, 0.162, 0.287)→(0.606, 0.161, 0.307) | (0.606, 0.170, 0.173)→(0.603, 0.174, 0.008) | 0.096→0.133 | 1.00 / 2.667 | 0.504 | 2.089 |
| retract_1 | retract | 1.00 / step_budget | (0.606, 0.161, 0.307)→(0.620, 0.177, 0.286) | (0.603, 0.174, 0.008)→(0.617, 0.174, 0.020) | 0.133→0.121 | 1.00 / 3.333 | 0.156 | 0.485 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.577
- phase_score: 0.278
- phase_breakdown.release_1_score: 0.037
- phase_breakdown.descend_1_score: 0.891
- phase_breakdown.transport_arc_score: 0.052
- phase_breakdown.approach_1_score: 0.085
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.756

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.756
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.577
- **Median Q (composite search score)**: 0.162
- **K-run variance**: 0.0033
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.323


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.05634,"average_solve_count":142.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.06651,"descend_1.grasp_z_offset":0.01433,"descend_2.place_force_threshold":8.24312,"descend_2.place_z_offset":0.02536,"lift_1.lift_height":0.25976,"lift_1.lift_speed":0.09562,"release_1.release_duration":0.25963,"retract_1.retract_speed":0.34665,"transport_1.arc_height":0.18471,"transport_1.transport_speed":0.32947},"optimized_scores":{"best_composite_score":0.16212,"best_fitness_score":0.71712,"best_task_score":0.49675},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2.0,"contact_point_centroid":[0.58216,0.19377,-0.00119],"force_p95":2.28106,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.33397,"mean_force":1.80484,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60621,0.18006,0.30011]},{"body_a":"world","body_b":"grasp_target","contact_count":756.0,"contact_point_centroid":[0.59456,0.21698,-0.00399],"force_p95":0.93143,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.0469,"mean_force":0.21169,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60345,0.17915,0.30032]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12860.0,"contact_point_centroid":[0.49713,0.01543,0.29244],"force_p95":0.12121,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.54671,"mean_force":0.07379,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49475,0.03423,0.29292]},{"body_a":"world","body_b":"grasp_target","contact_count":138.0,"contact_point_centroid":[0.45631,-0.02536,-0.00112],"force_p95":0.2489,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46757,"mean_force":0.06411,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44448,-0.02553,0.04314]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14055.0,"contact_point_centroid":[0.49738,0.05562,0.29437],"force_p95":0.09952,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42379,"mean_force":0.06414,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49696,0.03709,0.29446]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18772.0,"contact_point_centroid":[0.44587,-0.0448,0.12129],"force_p95":0.07877,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28705,"mean_force":0.05359,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44614,-0.02562,0.11849]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21285.0,"contact_point_centroid":[0.44753,-0.00658,0.11941],"force_p95":0.07272,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28548,"mean_force":0.04836,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44609,-0.02562,0.11758]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02638,-0.00206],"force_p95":0.14123,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17642,"mean_force":0.12728,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44693,-0.0256,0.04237]},{"body_a":"world","body_b":"grasp_target","contact_count":2352.0,"contact_point_centroid":[0.45856,-0.02632,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47802,-0.01192,0.20316]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5280.0,"contact_point_centroid":[0.44683,-0.00647,0.04274],"force_p95":0.06797,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13128,"mean_force":0.04153,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44578,-0.02556,0.04126]},{"body_a":"world","body_b":"grasp_target","contact_count":848.0,"contact_point_centroid":[0.59404,0.21763,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.61179,0.18978,0.29215]},{"body_a":"world","body_b":"grasp_target","contact_count":772.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45452,-0.02503,0.07747]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4408.0,"contact_point_centroid":[0.44521,-0.04483,0.04404],"force_p95":0.07951,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08352,"mean_force":0.04918,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44578,-0.02556,0.04127]},{"body_a":"left_finger","body_b":"right_finger","contact_count":69.0,"contact_point_centroid":[0.60405,0.17927,0.2971],"force_p95":0.01601,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0162,"mean_force":0.01121,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60458,0.17958,0.29445]}],"total_contact_groups":14},"final_pose_error":0.00991,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.59404,0.21763,0.01602],"final_tcp_position":[0.62258,0.20202,0.26579],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":5120.06626,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":589.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2352.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45735,-0.02435,0.10602],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08004,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":193.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":772.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.4538,-0.02579,0.04906],"tcp_start":[0.45735,-0.02435,0.10602],"tcp_to_object_dist_end":0.02353,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45849,-0.02611,0.02578],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30359,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14106,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11488.0,"raw_peak_contact_force":0.17642,"tcp_end":[0.44575,-0.02556,0.04123],"tcp_start":[0.4538,-0.02579,0.04906],"tcp_to_object_dist_end":0.02004,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45839,-0.02629,0.17388],"object_pos_start":[0.45849,-0.02611,0.02578],"object_to_goal_dist_end":0.29675,"object_to_goal_dist_start":0.30359,"object_z_max":0.1737,"peak_contact_force":0.07073,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40195.0,"raw_peak_contact_force":0.46757,"tcp_end":[0.45056,-0.02579,0.19572],"tcp_start":[0.44575,-0.02556,0.04123],"tcp_to_object_dist_end":0.0232,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59329,0.19765,0.08845],"object_pos_start":[0.45839,-0.02629,0.17388],"object_to_goal_dist_end":0.04612,"object_to_goal_dist_start":0.29675,"object_z_max":0.31713,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26915.0,"raw_peak_contact_force":0.54671,"subtask_id":"transport_arc","tcp_end":[0.60651,0.17954,0.30369],"tcp_start":[0.45056,-0.02579,0.19572],"tcp_to_object_dist_end":0.2164,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":14.0,"n_steps_budget":1000.0,"object_pos_end":[0.59498,0.20334,0.02945],"object_pos_start":[0.59329,0.19765,0.08845],"object_to_goal_dist_end":0.0918,"object_to_goal_dist_start":0.04612,"object_z_max":0.08845,"peak_contact_force":5120.06626,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2.0,"raw_peak_contact_force":2.33397,"subtask_id":"release_1","tcp_end":[0.60618,0.18008,0.29969],"tcp_start":[0.60651,0.17954,0.30369],"tcp_to_object_dist_end":0.27146,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59404,0.21763,0.01602],"object_pos_start":[0.59498,0.20334,0.02945],"object_to_goal_dist_end":0.10495,"object_to_goal_dist_start":0.0918,"object_z_max":0.02945,"peak_contact_force":0.12264,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":825.0,"raw_peak_contact_force":2.0469,"tcp_end":[0.60274,0.17887,0.31988],"tcp_start":[0.60618,0.18008,0.29969],"tcp_to_object_dist_end":0.30644,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":212.0,"n_steps_budget":600.0,"object_pos_end":[0.59404,0.21763,0.01602],"object_pos_start":[0.59404,0.21763,0.01602],"object_to_goal_dist_end":0.10495,"object_to_goal_dist_start":0.10495,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":848.0,"raw_peak_contact_force":0.12264,"tcp_end":[0.62258,0.20202,0.26579],"tcp_start":[0.60274,0.17887,0.31988],"tcp_to_object_dist_end":0.25188,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9078,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14955,"descend_1.grasp_z_offset":0.0185,"descend_2.place_force_threshold":4.17577,"descend_2.place_z_offset":0.0306,"lift_1.lift_height":0.23369,"lift_1.lift_speed":0.10762,"release_1.release_duration":0.19549,"retract_1.retract_speed":0.23963,"transport_1.arc_height":0.07349,"transport_1.transport_speed":0.32062},"optimized_scores":{"best_composite_score":0.06508,"best_fitness_score":0.62008,"best_task_score":0.30774},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.61071,0.12608,-0.01322],"force_p95":1.88289,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.22846,"mean_force":0.97845,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62483,0.13361,0.32404]},{"body_a":"world","body_b":"grasp_target","contact_count":1284.0,"contact_point_centroid":[0.64135,0.13267,-0.00278],"force_p95":0.34754,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.77232,"mean_force":0.14878,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.63682,0.14801,0.32807]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13332.0,"contact_point_centroid":[0.56525,0.01908,0.29569],"force_p95":0.11783,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.60121,"mean_force":0.07667,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56154,0.03757,0.29675]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13170.0,"contact_point_centroid":[0.56433,0.05773,0.29661],"force_p95":0.11507,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.55438,"mean_force":0.07463,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56253,0.03898,0.29705]},{"body_a":"world","body_b":"grasp_target","contact_count":169.0,"contact_point_centroid":[0.54043,0.00103,-0.00123],"force_p95":0.24635,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48997,"mean_force":0.07913,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52835,0.00081,0.04375]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1540.0,"contact_point_centroid":[0.61785,0.14784,0.32325],"force_p95":0.11132,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40723,"mean_force":0.09177,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62589,0.1307,0.32732]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18356.0,"contact_point_centroid":[0.53323,0.02002,0.13011],"force_p95":0.08001,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33369,"mean_force":0.05532,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53186,0.00088,0.12776]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1386.0,"contact_point_centroid":[0.62483,0.1119,0.32178],"force_p95":0.11674,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32845,"mean_force":0.10164,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62589,0.1307,0.32732]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":597.0,"contact_point_centroid":[0.6186,0.15149,0.29939],"force_p95":0.11506,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31339,"mean_force":0.08277,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62692,0.13424,0.30404]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19850.0,"contact_point_centroid":[0.53255,-0.01817,0.12499],"force_p95":0.0757,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30777,"mean_force":0.05194,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53155,0.00087,0.12313]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":606.0,"contact_point_centroid":[0.62589,0.11539,0.29769],"force_p95":0.116,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26015,"mean_force":0.08208,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62691,0.13424,0.30399]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00116,-0.00203],"force_p95":0.13136,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15458,"mean_force":0.12546,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53117,0.00086,0.04378]},{"body_a":"world","body_b":"grasp_target","contact_count":1616.0,"contact_point_centroid":[0.54431,0.00113,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51679,0.00047,0.24213]},{"body_a":"world","body_b":"grasp_target","contact_count":1604.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53607,0.00097,0.11854]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4149.0,"contact_point_centroid":[0.53108,0.02014,0.04487],"force_p95":0.07646,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09633,"mean_force":0.05215,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52992,0.00084,0.0423]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5327.0,"contact_point_centroid":[0.53039,-0.0182,0.04491],"force_p95":0.06263,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08954,"mean_force":0.04075,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52991,0.00084,0.0423]}],"total_contact_groups":16},"final_pose_error":0.01088,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64611,0.13375,0.01602],"final_tcp_position":[0.64376,0.15554,0.33125],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":56.54168,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":405.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1616.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53621,0.00096,0.18541],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15959,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":401.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1604.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53863,0.00102,0.05275],"tcp_start":[0.53621,0.00096,0.18541],"tcp_to_object_dist_end":0.02732,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54421,0.00112,0.02586],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25028,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13108,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11276.0,"raw_peak_contact_force":0.15458,"tcp_end":[0.52988,0.00084,0.04226],"tcp_start":[0.53863,0.00102,0.05275],"tcp_to_object_dist_end":0.02178,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54637,0.00117,0.18867],"object_pos_start":[0.54421,0.00112,0.02586],"object_to_goal_dist_end":0.18677,"object_to_goal_dist_start":0.25028,"object_z_max":0.18851,"peak_contact_force":0.07442,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38375.0,"raw_peak_contact_force":0.48997,"tcp_end":[0.53813,0.00101,0.21292],"tcp_start":[0.52988,0.00084,0.04226],"tcp_to_object_dist_end":0.02561,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62243,0.12819,0.31041],"object_pos_start":[0.54637,0.00117,0.18867],"object_to_goal_dist_end":0.12555,"object_to_goal_dist_start":0.18677,"object_z_max":0.3183,"peak_contact_force":0.11583,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26502.0,"raw_peak_contact_force":0.60121,"subtask_id":"transport_arc","tcp_end":[0.62474,0.12745,0.34716],"tcp_start":[0.53813,0.00101,0.21292],"tcp_to_object_dist_end":0.03683,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":154.0,"n_steps_budget":1000.0,"object_pos_end":[0.62283,0.13499,0.27036],"object_pos_start":[0.62243,0.12819,0.31041],"object_to_goal_dist_end":0.0862,"object_to_goal_dist_start":0.12555,"object_z_max":0.31041,"peak_contact_force":56.54168,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2926.0,"raw_peak_contact_force":0.40723,"subtask_id":"release_1","tcp_end":[0.62818,0.13446,0.30826],"tcp_start":[0.62474,0.12745,0.34716],"tcp_to_object_dist_end":0.03827,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61682,0.13352,-0.00011],"object_pos_start":[0.62283,0.13499,0.27036],"object_to_goal_dist_end":0.19523,"object_to_goal_dist_start":0.0862,"object_z_max":0.27036,"peak_contact_force":0.80692,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1280.0,"raw_peak_contact_force":2.22846,"tcp_end":[0.62481,0.13361,0.32804],"tcp_start":[0.62818,0.13446,0.30826],"tcp_to_object_dist_end":0.32825,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":397.0,"n_steps_budget":600.0,"object_pos_end":[0.64611,0.13375,0.01602],"object_pos_start":[0.61682,0.13352,-0.00011],"object_to_goal_dist_end":0.17677,"object_to_goal_dist_start":0.19523,"object_z_max":0.03153,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1284.0,"raw_peak_contact_force":0.77232,"tcp_end":[0.64376,0.15554,0.33125],"tcp_start":[0.62481,0.13361,0.32804],"tcp_to_object_dist_end":0.31599,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.95276,"average_solve_count":127.0,"average_success_count":127.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11609,"descend_1.grasp_z_offset":0.0171,"descend_2.place_force_threshold":11.44968,"descend_2.place_z_offset":0.04648,"lift_1.lift_height":0.217,"lift_1.lift_speed":0.16826,"release_1.release_duration":0.31739,"retract_1.retract_speed":0.32451,"transport_1.arc_height":0.1911,"transport_1.transport_speed":0.34488},"optimized_scores":{"best_composite_score":0.20074,"best_fitness_score":0.75574,"best_task_score":0.57677},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":96.0,"contact_point_centroid":[0.58823,0.1622,-0.0101],"force_p95":1.5722,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.99307,"mean_force":0.74352,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59,0.16914,0.26738]},{"body_a":"world","body_b":"grasp_target","contact_count":110.0,"contact_point_centroid":[0.59639,0.15963,-0.00584],"force_p95":0.44917,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55869,"mean_force":0.16442,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5917,0.17086,0.26798]},{"body_a":"world","body_b":"grasp_target","contact_count":130.0,"contact_point_centroid":[0.52822,0.02922,-0.00119],"force_p95":0.26607,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52506,"mean_force":0.06584,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51499,0.02946,0.04303]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":140.0,"contact_point_centroid":[0.60259,0.15379,0.24937],"force_p95":0.1601,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43952,"mean_force":0.10873,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59463,0.17043,0.25407]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":154.0,"contact_point_centroid":[0.59363,0.18902,0.25144],"force_p95":0.14166,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4173,"mean_force":0.09684,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59463,0.17043,0.25407]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13174.0,"contact_point_centroid":[0.56258,0.07476,0.26042],"force_p95":0.12103,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41526,"mean_force":0.07489,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55565,0.09244,0.26107]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9828.0,"contact_point_centroid":[0.52167,0.04871,0.12661],"force_p95":0.10938,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34641,"mean_force":0.07434,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51865,0.0296,0.12408]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11710.0,"contact_point_centroid":[0.52225,0.01102,0.12143],"force_p95":0.10206,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31656,"mean_force":0.06417,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51833,0.02959,0.11978]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":822.0,"contact_point_centroid":[0.60055,0.15317,0.24305],"force_p95":0.1886,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31184,"mean_force":0.08719,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59259,0.17002,0.2477]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12102.0,"contact_point_centroid":[0.55836,0.11281,0.26087],"force_p95":0.1207,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31017,"mean_force":0.07847,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55632,0.09375,0.26098]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":698.0,"contact_point_centroid":[0.59152,0.18886,0.24493],"force_p95":0.23543,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2958,"mean_force":0.0927,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59269,0.17005,0.24792]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53054,0.03081,-0.0021],"force_p95":0.1514,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20522,"mean_force":0.13034,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51751,0.02964,0.04251]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5289.0,"contact_point_centroid":[0.51738,0.01052,0.04306],"force_p95":0.06798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14878,"mean_force":0.04108,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51627,0.02956,0.04108]},{"body_a":"world","body_b":"grasp_target","contact_count":1956.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51079,0.0137,0.22618]},{"body_a":"world","body_b":"grasp_target","contact_count":1256.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52314,0.02896,0.10169]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4208.0,"contact_point_centroid":[0.51682,0.04887,0.04389],"force_p95":0.082,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08426,"mean_force":0.05173,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51627,0.02956,0.04109]}],"total_contact_groups":16},"final_pose_error":0.00987,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.61087,0.16975,0.02655],"final_tcp_position":[0.5939,0.17315,0.26119],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":490.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1956.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52404,0.02797,0.15308],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12726,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":314.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1256.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52488,0.03012,0.05108],"tcp_start":[0.52404,0.02797,0.15308],"tcp_to_object_dist_end":0.0257,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53047,0.03025,0.02563],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18399,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14973,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11297.0,"raw_peak_contact_force":0.20522,"tcp_end":[0.51624,0.02956,0.04105],"tcp_start":[0.52488,0.03012,0.05108],"tcp_to_object_dist_end":0.02099,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":722.0,"n_steps_budget":780.0,"object_pos_end":[0.53943,0.03069,0.20128],"object_pos_start":[0.53047,0.03025,0.02563],"object_to_goal_dist_end":0.1855,"object_to_goal_dist_start":0.18399,"object_z_max":0.20108,"peak_contact_force":0.09576,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21668.0,"raw_peak_contact_force":0.52506,"tcp_end":[0.52665,0.03001,0.22637],"tcp_start":[0.51624,0.02956,0.04105],"tcp_to_object_dist_end":0.02816,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59963,0.17233,0.22177],"object_pos_start":[0.53943,0.03069,0.20128],"object_to_goal_dist_end":0.11386,"object_to_goal_dist_start":0.1855,"object_z_max":0.24406,"peak_contact_force":0.12991,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25276.0,"raw_peak_contact_force":0.41526,"subtask_id":"transport_arc","tcp_end":[0.59482,0.17012,0.25542],"tcp_start":[0.52665,0.03001,0.22637],"tcp_to_object_dist_end":0.03407,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":14.0,"n_steps_budget":1000.0,"object_pos_end":[0.59939,0.17289,0.21787],"object_pos_start":[0.59963,0.17233,0.22177],"object_to_goal_dist_end":0.10995,"object_to_goal_dist_start":0.11386,"object_z_max":0.22177,"peak_contact_force":167951.73011,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":294.0,"raw_peak_contact_force":0.43952,"subtask_id":"release_1","tcp_end":[0.59434,0.17054,0.25207],"tcp_start":[0.59482,0.17012,0.25542],"tcp_to_object_dist_end":0.03465,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59765,0.16946,0.00855],"object_pos_start":[0.59939,0.17289,0.21787],"object_to_goal_dist_end":0.10003,"object_to_goal_dist_start":0.10995,"object_z_max":0.21787,"peak_contact_force":0.58211,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1616.0,"raw_peak_contact_force":1.99307,"tcp_end":[0.58996,0.16914,0.27274],"tcp_start":[0.59434,0.17054,0.25207],"tcp_to_object_dist_end":0.2643,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":55.0,"n_steps_budget":600.0,"object_pos_end":[0.61087,0.16975,0.02655],"object_pos_start":[0.59765,0.16946,0.00855],"object_to_goal_dist_end":0.08255,"object_to_goal_dist_start":0.10003,"object_z_max":0.02753,"peak_contact_force":0.22268,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":110.0,"raw_peak_contact_force":0.55869,"tcp_end":[0.5939,0.17315,0.26119],"tcp_start":[0.58996,0.16914,0.27274],"tcp_to_object_dist_end":0.23528,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```