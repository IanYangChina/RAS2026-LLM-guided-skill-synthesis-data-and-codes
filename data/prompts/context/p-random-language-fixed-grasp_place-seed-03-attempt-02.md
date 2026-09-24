## Search State

- **Seed**: 3
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | 0.1848 | 0.48 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | 0.1851 | 0.48 | ✅ accepted |
| 0 | rotate → retract → descend → pull → rotate | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.0374 | 0.17 | ✅ accepted |

**Proposal policy**: task_score is 0.48 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.185) — your mutation base

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

- **Composite score**: 0.185
- **task_score** (E): 0.482
- **fitness_score**: 0.715  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.530

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1759 |
| descend_1 | 1.00 | 1.00 | 0.0857 |
| grasp_1 | 0.00 | 1.00 | 0.0000 |
| lift_1 | 0.67 | 1.00 | 0.1254 |
| transport_1 | 1.00 | 1.00 | 0.2204 |
| descend_2 | 1.00 | 1.00 | 0.0985 |
| release_1 | 1.00 | 1.00 | 0.0206 |
| retract_1 | 1.00 | 1.00 | 0.0753 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.130) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.002, 0.130)→(0.506, 0.002, 0.044) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 0.00 / guard_failure | (0.500, 0.002, 0.038)→(0.500, 0.002, 0.038) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 43.333 | 0.139 | 0.172 |
| lift_1 | lift | 0.67 / step_budget | (0.500, 0.002, 0.038)→(0.505, 0.002, 0.164) | (0.511, 0.002, 0.026)→(0.514, 0.002, 0.146) | 0.246→0.223 | 1.00 / 41.667 | 0.072 | 0.545 |
| transport_1 | approach | 1.00 / step_budget | (0.505, 0.002, 0.164)→(0.606, 0.155, 0.273) | (0.514, 0.002, 0.146)→(0.608, 0.156, 0.249) | 0.223→0.116 | 1.00 / 36.000 | 0.083 | 0.281 |
| descend_2 | descend | 1.00 / step_budget | (0.606, 0.155, 0.273)→(0.620, 0.177, 0.179) | (0.608, 0.156, 0.249)→(0.619, 0.179, 0.152) | 0.116→0.017 | 1.00 / 37.000 | 0.089 | 0.262 |
| release_1 | release | 1.00 / step_budget | (0.620, 0.177, 0.179)→(0.614, 0.175, 0.198) | (0.619, 0.179, 0.152)→(0.611, 0.174, 0.025) | 0.017→0.114 | 1.00 / 3.333 | 0.134 | 1.334 |
| retract_1 | retract | 1.00 / step_budget | (0.614, 0.175, 0.198)→(0.623, 0.180, 0.273) | (0.611, 0.174, 0.025)→(0.607, 0.174, 0.026) | 0.114→0.114 | 1.00 / 4.000 | 0.123 | 0.178 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.564
- phase_score: 0.315
- phase_breakdown.release_1_score: 0.258
- phase_breakdown.transport_arc_score: 0.057
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.839
- phase_breakdown.approach_1_score: 0.229
- grasp_place_fitness: 0.756

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.756
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.564
- **Median Q (composite search score)**: 0.220
- **K-run variance**: 0.0029
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.399


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.10458,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07312,"descend_1.grasp_z_offset":0.01031,"descend_2.place_z_offset":0.03363,"lift_1.lift_height":0.14634,"release_1.release_duration":0.40444,"retract_1.retract_speed":0.40907,"transport_1.transport_speed":0.36469},"optimized_scores":{"best_composite_score":0.21973,"best_fitness_score":0.74973,"best_task_score":0.55347},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":287.0,"contact_point_centroid":[0.62147,0.20172,-0.00456],"force_p95":0.84403,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.12867,"mean_force":0.24005,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61668,0.20089,0.16051]},{"body_a":"world","body_b":"grasp_target","contact_count":133.0,"contact_point_centroid":[0.45609,-0.02543,-0.00111],"force_p95":0.27801,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49049,"mean_force":0.05766,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4477,-0.02567,0.04192]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":592.0,"contact_point_centroid":[0.61753,0.2212,0.14525],"force_p95":0.12708,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38618,"mean_force":0.0866,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6207,0.20233,0.14729]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19644.0,"contact_point_centroid":[0.52105,0.04504,0.21909],"force_p95":0.08134,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36938,"mean_force":0.05151,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51923,0.06396,0.21817]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3470.0,"contact_point_centroid":[0.60699,0.20534,0.20344],"force_p95":0.13791,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34195,"mean_force":0.09608,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61052,0.18681,0.20491]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18468.0,"contact_point_centroid":[0.51494,0.07919,0.21796],"force_p95":0.08113,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33282,"mean_force":0.05388,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51638,0.06019,0.21624]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":786.0,"contact_point_centroid":[0.6258,0.18509,0.14176],"force_p95":0.09803,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32789,"mean_force":0.06854,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62071,0.20233,0.1473]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15956.0,"contact_point_centroid":[0.4505,-0.00664,0.10051],"force_p95":0.07153,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30009,"mean_force":0.04802,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44955,-0.02579,0.0992]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15633.0,"contact_point_centroid":[0.44858,-0.04493,0.10329],"force_p95":0.07262,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28616,"mean_force":0.04865,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44971,-0.0258,0.10145]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4072.0,"contact_point_centroid":[0.61608,0.1701,0.19784],"force_p95":0.13188,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2658,"mean_force":0.08674,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61107,0.18754,0.20245]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.45858,-0.02638,-0.00206],"force_p95":0.13886,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17422,"mean_force":0.12756,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44935,-0.02571,0.04045]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.62169,0.20182,-0.00198],"force_p95":0.13079,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14372,"mean_force":0.12246,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.62009,0.20336,0.20782]},{"body_a":"world","body_b":"grasp_target","contact_count":2264.0,"contact_point_centroid":[0.45856,-0.02632,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47809,-0.0119,0.20631]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5831.0,"contact_point_centroid":[0.45048,-0.0066,0.04149],"force_p95":0.07239,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13302,"mean_force":0.04543,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44891,-0.0257,0.04002]},{"body_a":"world","body_b":"grasp_target","contact_count":896.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45451,-0.02502,0.07864]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5303.0,"contact_point_centroid":[0.4473,-0.04486,0.04247],"force_p95":0.07961,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09045,"mean_force":0.04953,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44891,-0.0257,0.04002]}],"total_contact_groups":16},"final_pose_error":0.01576,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.6217,0.20183,0.02602],"final_tcp_position":[0.62633,0.20669,0.24889],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.12867,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":567.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2264.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45751,-0.02429,0.11264],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08665,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":224.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":896.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.4538,-0.02584,0.04485],"tcp_start":[0.45751,-0.02429,0.11264],"tcp_to_object_dist_end":0.01943,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45849,-0.02613,0.02581],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.3036,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13796,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12938.0,"raw_peak_contact_force":0.17422,"tcp_end":[0.44889,-0.0257,0.04],"tcp_start":[0.44889,-0.0257,0.04],"tcp_to_object_dist_end":0.01714,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.46235,-0.02645,0.14191],"object_pos_start":[0.45849,-0.02616,0.02582],"object_to_goal_dist_end":0.28981,"object_to_goal_dist_start":0.30362,"object_z_max":0.1418,"peak_contact_force":0.0715,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":31722.0,"raw_peak_contact_force":0.49049,"tcp_end":[0.45431,-0.026,0.16075],"tcp_start":[0.44889,-0.0257,0.04],"tcp_to_object_dist_end":0.02048,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59959,0.17424,0.22799],"object_pos_start":[0.46235,-0.02645,0.14191],"object_to_goal_dist_end":0.12269,"object_to_goal_dist_start":0.28981,"object_z_max":0.22838,"peak_contact_force":0.10891,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38112.0,"raw_peak_contact_force":0.36938,"subtask_id":"transport_arc","tcp_end":[0.60174,0.17343,0.2559],"tcp_start":[0.45431,-0.026,0.16075],"tcp_to_object_dist_end":0.028,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":339.0,"n_steps_budget":1000.0,"object_pos_end":[0.61786,0.20422,0.11916],"object_pos_start":[0.59959,0.17424,0.22799],"object_to_goal_dist_end":0.01386,"object_to_goal_dist_start":0.12269,"object_z_max":0.22799,"peak_contact_force":0.13354,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7542.0,"raw_peak_contact_force":0.34195,"subtask_id":"release_1","tcp_end":[0.62284,0.20289,0.15168],"tcp_start":[0.60174,0.17343,0.2559],"tcp_to_object_dist_end":0.03293,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62071,0.20153,0.02645],"object_pos_start":[0.61786,0.20422,0.11916],"object_to_goal_dist_end":0.08842,"object_to_goal_dist_start":0.01386,"object_z_max":0.11916,"peak_contact_force":0.12315,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1665.0,"raw_peak_contact_force":1.12867,"tcp_end":[0.61659,0.20087,0.17115],"tcp_start":[0.62284,0.20289,0.15168],"tcp_to_object_dist_end":0.14476,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.6217,0.20183,0.02602],"object_pos_start":[0.62071,0.20153,0.02645],"object_to_goal_dist_end":0.08873,"object_to_goal_dist_start":0.08842,"object_z_max":0.02655,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.14372,"tcp_end":[0.62633,0.20669,0.24889],"tcp_start":[0.61659,0.20087,0.17115],"tcp_to_object_dist_end":0.22298,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.04965,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13744,"descend_1.grasp_z_offset":0.01,"descend_2.place_z_offset":0.03442,"lift_1.lift_height":0.11928,"release_1.release_duration":0.40801,"retract_1.retract_speed":0.27217,"transport_1.transport_speed":0.32844},"optimized_scores":{"best_composite_score":0.10862,"best_fitness_score":0.63862,"best_task_score":0.32788},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":182.0,"contact_point_centroid":[0.62449,0.14864,-0.00805],"force_p95":1.45932,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.63849,"mean_force":0.42099,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63617,0.15142,0.24187]},{"body_a":"world","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.54115,0.00103,-0.00112],"force_p95":0.45184,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56417,"mean_force":0.08346,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53198,0.00088,0.03921]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11764.0,"contact_point_centroid":[0.53434,0.02012,0.08639],"force_p95":0.07493,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33113,"mean_force":0.05185,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53426,0.00093,0.08466]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12600.0,"contact_point_centroid":[0.53407,-0.01817,0.08402],"force_p95":0.07185,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30098,"mean_force":0.04876,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53405,0.00093,0.08239]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1279.0,"contact_point_centroid":[0.63443,0.17091,0.22945],"force_p95":0.06655,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26385,"mean_force":0.04218,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63939,0.15239,0.226]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20270.0,"contact_point_centroid":[0.57698,0.03788,0.23156],"force_p95":0.07589,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24636,"mean_force":0.04993,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57513,0.05692,0.22975]},{"body_a":"world","body_b":"grasp_target","contact_count":1968.0,"contact_point_centroid":[0.6232,0.14887,-0.00207],"force_p95":0.16577,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23802,"mean_force":0.12493,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.63955,0.15409,0.28681]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5296.0,"contact_point_centroid":[0.62764,0.15823,0.27433],"force_p95":0.08217,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23721,"mean_force":0.05134,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.63202,0.13959,0.27111]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19415.0,"contact_point_centroid":[0.57267,0.0743,0.23039],"force_p95":0.07664,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22469,"mean_force":0.05143,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57398,0.05527,0.2278]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1454.0,"contact_point_centroid":[0.64215,0.13321,0.22704],"force_p95":0.06326,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21458,"mean_force":0.03775,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6394,0.15239,0.22601]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6063.0,"contact_point_centroid":[0.63481,0.12052,0.27239],"force_p95":0.07764,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17535,"mean_force":0.04641,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.632,0.13957,0.27121]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.5443,0.00116,-0.00203],"force_p95":0.13,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14516,"mean_force":0.12538,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5337,0.00092,0.03812]},{"body_a":"world","body_b":"grasp_target","contact_count":1760.0,"contact_point_centroid":[0.54431,0.00113,-0.00192],"force_p95":0.13362,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51687,0.00047,0.23629]},{"body_a":"world","body_b":"grasp_target","contact_count":1568.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53612,0.00097,0.10817]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5292.0,"contact_point_centroid":[0.53338,0.0202,0.03947],"force_p95":0.07442,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09564,"mean_force":0.0497,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53322,0.00091,0.03754]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6430.0,"contact_point_centroid":[0.5329,-0.01816,0.03908],"force_p95":0.06277,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08788,"mean_force":0.04104,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53322,0.00091,0.03754]}],"total_contact_groups":16},"final_pose_error":0.01553,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.62237,0.14871,0.02602],"final_tcp_position":[0.64481,0.15702,0.32587],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.63849,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":441.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1760.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53643,0.00097,0.17354],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14773,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":392.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1568.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53855,0.00101,0.04396],"tcp_start":[0.53643,0.00097,0.17354],"tcp_to_object_dist_end":0.01884,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5442,0.00113,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25025,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12984,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13526.0,"raw_peak_contact_force":0.14516,"tcp_end":[0.53319,0.00091,0.03751],"tcp_start":[0.53319,0.00091,0.03752],"tcp_to_object_dist_end":0.01602,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.54838,0.00104,0.11734],"object_pos_start":[0.54421,0.00113,0.02589],"object_to_goal_dist_end":0.19988,"object_to_goal_dist_start":0.25025,"object_z_max":0.11723,"peak_contact_force":0.07161,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24509.0,"raw_peak_contact_force":0.56417,"tcp_end":[0.53932,0.00104,0.13228],"tcp_start":[0.53319,0.00091,0.03751],"tcp_to_object_dist_end":0.01747,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.63132,0.1298,0.29115],"object_pos_start":[0.54838,0.00104,0.11734],"object_to_goal_dist_end":0.10523,"object_to_goal_dist_start":0.19988,"object_z_max":0.29105,"peak_contact_force":0.07118,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":39685.0,"raw_peak_contact_force":0.24636,"subtask_id":"transport_arc","tcp_end":[0.62494,0.12782,0.31311],"tcp_start":[0.53932,0.00104,0.13228],"tcp_to_object_dist_end":0.02296,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":258.0,"n_steps_budget":1000.0,"object_pos_end":[0.6436,0.15451,0.20601],"object_pos_start":[0.63132,0.1298,0.29115],"object_to_goal_dist_end":0.01584,"object_to_goal_dist_start":0.10523,"object_z_max":0.29115,"peak_contact_force":0.06655,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11359.0,"raw_peak_contact_force":0.23721,"subtask_id":"release_1","tcp_end":[0.64104,0.15264,0.23029],"tcp_start":[0.62494,0.12782,0.31311],"tcp_to_object_dist_end":0.02449,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63426,0.14994,0.02177],"object_pos_start":[0.6436,0.15451,0.20601],"object_to_goal_dist_end":0.17006,"object_to_goal_dist_start":0.01584,"object_z_max":0.20601,"peak_contact_force":0.15849,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2915.0,"raw_peak_contact_force":1.63849,"tcp_end":[0.63613,0.15141,0.24943],"tcp_start":[0.64104,0.15264,0.23029],"tcp_to_object_dist_end":0.22767,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.62237,0.14871,0.02602],"object_pos_start":[0.63426,0.14994,0.02177],"object_to_goal_dist_end":0.16727,"object_to_goal_dist_start":0.17006,"object_z_max":0.02855,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1968.0,"raw_peak_contact_force":0.23802,"tcp_end":[0.64481,0.15702,0.32587],"tcp_start":[0.63613,0.15141,0.24943],"tcp_to_object_dist_end":0.3008,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.99383,"average_solve_count":162.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.06621,"descend_1.grasp_z_offset":0.0101,"descend_2.place_z_offset":0.03846,"lift_1.lift_height":0.28695,"release_1.release_duration":0.43966,"retract_1.retract_speed":0.32665,"transport_1.transport_speed":0.21755},"optimized_scores":{"best_composite_score":0.22595,"best_fitness_score":0.75595,"best_task_score":0.564},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":282.0,"contact_point_centroid":[0.57752,0.17104,-0.00489],"force_p95":0.95376,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.23619,"mean_force":0.25528,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58991,0.17335,0.16409]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.52718,0.02911,-0.00121],"force_p95":0.39686,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57912,"mean_force":0.08253,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51762,0.02958,0.03943]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17517.0,"contact_point_centroid":[0.51801,0.04879,0.11842],"force_p95":0.08016,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33957,"mean_force":0.05693,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51845,0.02959,0.11578]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21822.0,"contact_point_centroid":[0.51906,0.01059,0.11756],"force_p95":0.07291,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30639,"mean_force":0.04703,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51847,0.02959,0.11615]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1274.0,"contact_point_centroid":[0.58839,0.19295,0.15313],"force_p95":0.06773,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24041,"mean_force":0.04224,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59399,0.17463,0.15007]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":22342.0,"contact_point_centroid":[0.5571,0.0764,0.23375],"force_p95":0.06769,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22734,"mean_force":0.04491,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55454,0.09538,0.23198]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1447.0,"contact_point_centroid":[0.59741,0.15553,0.15108],"force_p95":0.06364,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21498,"mean_force":0.03776,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.594,0.17464,0.15008]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5775.0,"contact_point_centroid":[0.58681,0.18684,0.20599],"force_p95":0.07197,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20818,"mean_force":0.04878,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59234,0.1686,0.20229]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53055,0.0308,-0.00212],"force_p95":0.15033,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.198,"mean_force":0.13122,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5196,0.02972,0.03819]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19585.0,"contact_point_centroid":[0.55217,0.11509,0.23541],"force_p95":0.07205,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19745,"mean_force":0.04993,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55498,0.0962,0.2322]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6390.0,"contact_point_centroid":[0.596,0.14974,0.2024],"force_p95":0.06922,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16745,"mean_force":0.04553,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59239,0.16872,0.20129]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.57736,0.17088,-0.00197],"force_p95":0.13245,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15133,"mean_force":0.1224,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5924,0.17493,0.2074]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6389.0,"contact_point_centroid":[0.51963,0.0106,0.0388],"force_p95":0.06884,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14627,"mean_force":0.04135,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51912,0.02969,0.03763]},{"body_a":"world","body_b":"grasp_target","contact_count":2540.0,"contact_point_centroid":[0.5305,0.03079,-0.00194],"force_p95":0.13053,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51088,0.01408,0.20105]},{"body_a":"world","body_b":"grasp_target","contact_count":764.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5231,0.0292,0.07335]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5343.0,"contact_point_centroid":[0.51873,0.04895,0.04019],"force_p95":0.08194,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08312,"mean_force":0.04951,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51913,0.02969,0.03764]}],"total_contact_groups":16},"final_pose_error":0.01439,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57735,0.17088,0.02602],"final_tcp_position":[0.59774,0.1773,0.24427],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.23619,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":636.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2540.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52416,0.02853,0.10347],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07774,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":191.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":764.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52437,0.03002,0.04378],"tcp_start":[0.52416,0.02853,0.10347],"tcp_to_object_dist_end":0.0188,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53047,0.03025,0.02565],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18398,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14851,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13536.0,"raw_peak_contact_force":0.198,"tcp_end":[0.5191,0.02968,0.03761],"tcp_start":[0.5191,0.02968,0.03761],"tcp_to_object_dist_end":0.01651,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5301,0.03042,0.17955],"object_pos_start":[0.53047,0.03026,0.02567],"object_to_goal_dist_end":0.17934,"object_to_goal_dist_start":0.18396,"object_z_max":0.17937,"peak_contact_force":0.07279,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39485.0,"raw_peak_contact_force":0.57912,"tcp_end":[0.52237,0.02979,0.19804],"tcp_start":[0.5191,0.02968,0.03761],"tcp_to_object_dist_end":0.02004,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59231,0.16448,0.22715],"object_pos_start":[0.5301,0.03042,0.17955],"object_to_goal_dist_end":0.12025,"object_to_goal_dist_start":0.17934,"object_z_max":0.22732,"peak_contact_force":0.06744,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":41927.0,"raw_peak_contact_force":0.22734,"subtask_id":"transport_arc","tcp_end":[0.5907,0.16305,0.25035],"tcp_start":[0.52237,0.02979,0.19804],"tcp_to_object_dist_end":0.0233,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":275.0,"n_steps_budget":1000.0,"object_pos_end":[0.59601,0.17691,0.12959],"object_pos_start":[0.59231,0.16448,0.22715],"object_to_goal_dist_end":0.02226,"object_to_goal_dist_start":0.12025,"object_z_max":0.22715,"peak_contact_force":0.06753,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12165.0,"raw_peak_contact_force":0.20818,"subtask_id":"release_1","tcp_end":[0.59605,0.17517,0.15401],"tcp_start":[0.5907,0.16305,0.25035],"tcp_to_object_dist_end":0.02449,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57894,0.17091,0.0265],"object_pos_start":[0.59601,0.17691,0.12959],"object_to_goal_dist_end":0.08501,"object_to_goal_dist_start":0.02226,"object_z_max":0.12959,"peak_contact_force":0.12156,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":3003.0,"raw_peak_contact_force":1.23619,"tcp_end":[0.58982,0.17333,0.17459],"tcp_start":[0.59605,0.17517,0.15401],"tcp_to_object_dist_end":0.14851,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.57735,0.17088,0.02602],"object_pos_start":[0.57894,0.17091,0.0265],"object_to_goal_dist_end":0.08591,"object_to_goal_dist_start":0.08501,"object_z_max":0.02665,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.15133,"tcp_end":[0.59774,0.1773,0.24427],"tcp_start":[0.58982,0.17333,0.17459],"tcp_to_object_dist_end":0.2193,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```