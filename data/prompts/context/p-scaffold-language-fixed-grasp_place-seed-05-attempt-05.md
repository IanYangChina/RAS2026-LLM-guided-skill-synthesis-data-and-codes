## Search State

- **Seed**: 5
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.4108 | 0.82 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.5034 | 1.00 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.4745 | 0.95 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1790 | 0.41 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1731 | 0.41 | ✅ accepted |

**Proposal policy**: task_score is 0.82 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`
- Frozen object start: [0.530500292374538, 0.030794078973649372, 0.03]
- Frozen task target: [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]
- Goal object position: (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.530500292374538, 0.030794078973649372, 0.03)
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
  frozen_object_start: [0.5305, 0.0308, 0.03]
  frozen_task_target: [0.6015, 0.1786, 0.1081]
  frozen_object_starts: {'grasp_target': [0.530500292374538, 0.030794078973649372, 0.03]}
  frozen_targets: {'place_target': [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d

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

## Current Skill (Q=0.411) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_1
  anchor: object
- id: descend_1
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.02
- id: grasp_1
  anchor: object
  metric: contact
  offset:
  - 0.0
  - 0.0
  - 0.02
- id: transport_arc
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.15
    orientation:
      mode: none
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
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
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.05
    orientation:
      mode: none
  parameters:
    depth:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
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
    orientation:
      mode: none
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
    - 0.2
    orientation:
      mode: none
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.35
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.3
      default: 0.12
      binds_to:
      - path: generator.speed
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
    orientation:
      mode: none
  parameters:
    speed:
      type: scalar
      range:
      - 0.02
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    transport_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: transport_arc
- id: descend_goal
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
    orientation:
      mode: none
  parameters:
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: placement_force
    when: during_phase
    predicate: force_below
    threshold: 15.0
    on_failure: abort

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15]
  - orientation: mode=none
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.05]
  - orientation: mode=none
  - parameter_bindings:
    - depth: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.2]
  - orientation: mode=none
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15]
  - orientation: mode=none
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
    - transport_height: status=consumed; consumers=target.offset.z (replace)
- **descend_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03]
  - orientation: mode=none
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=placement_force, when=during_phase, predicate=force_below, on_failure=abort, threshold=15.0

## Design Metrics

- **Composite score**: 0.411
- **task_score** (E): 0.816
- **fitness_score**: 0.881  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.470

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1068 |
| descend_1 | 1.00 | 1.00 | 0.1534 |
| grasp_1 | 1.00 | 1.00 | 0.0129 |
| lift_1 | 1.00 | 1.00 | 0.1159 |
| transport_1 | 0.33 | 1.00 | 0.1483 |
| descend_goal | 1.00 | 0.67 | 0.1263 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, 0.020, 0.199) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.511, 0.020, 0.199)→(0.510, 0.018, 0.046) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.510, 0.018, 0.046)→(0.502, 0.018, 0.036) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 42.667 | 0.144 | 0.186 |
| lift_1 | lift | 1.00 / step_budget | (0.502, 0.018, 0.036)→(0.498, 0.018, 0.152) | (0.516, 0.018, 0.026)→(0.513, 0.018, 0.133) | 0.236→0.196 | 1.00 / 25.333 | 0.108 | 0.592 |
| transport_1 | approach | 0.33 / step_budget | (0.498, 0.018, 0.152)→(0.553, 0.100, 0.259) | (0.513, 0.018, 0.133)→(0.561, 0.101, 0.233) | 0.196→0.141 | 1.00 / 28.000 | 0.092 | 0.264 |
| descend_goal | descend | 1.00 / step_budget | (0.553, 0.100, 0.259)→(0.594, 0.166, 0.189) | (0.561, 0.101, 0.233)→(0.598, 0.162, 0.130) | 0.141→0.048 | 0.67 / 20.000 | 0.070 | 0.309 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.234
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.297
- phase_breakdown.transport_arc_score: 0.104
- phase_breakdown.descend_1_score: 0.864
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.000
- phase_breakdown.approach_1_score: 0.063
- grasp_place_fitness: 0.973

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.973
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.501
- **K-run variance**: 0.0168
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.349


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `181fdad61feb8a6d3dd6561c82dc2730a5598964bf30fa08b43615687239c379`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `eed1fc17ff57094d5189888f0dc8540ea7c165c4c73333e7487a550c7ded377e`; realized-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0229,"average_solve_count":131.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18684,"descend_1.depth":0.01314,"descend_goal.place_z_offset":0.0322,"lift_1.lift_height":0.11633,"lift_1.speed":0.18125,"transport_1.speed":0.29998,"transport_1.transport_height":0.20712},"optimized_scores":{"best_composite_score":0.50139,"best_fitness_score":0.97139,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":173.0,"contact_point_centroid":[0.52745,0.02973,-0.00126],"force_p95":0.28994,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55314,"mean_force":0.08864,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51474,0.02959,0.03907]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15496.0,"contact_point_centroid":[0.54834,0.06553,0.2233],"force_p95":0.09689,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3344,"mean_force":0.06561,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54208,0.08347,0.22262]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8579.0,"contact_point_centroid":[0.51393,0.04866,0.08553],"force_p95":0.10842,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33426,"mean_force":0.06548,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51238,0.02944,0.08276]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11108.0,"contact_point_centroid":[0.51444,0.01076,0.08579],"force_p95":0.08446,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31169,"mean_force":0.0521,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51239,0.02944,0.08428]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6047.0,"contact_point_centroid":[0.59716,0.14573,0.22028],"force_p95":0.1062,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26575,"mean_force":0.07233,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.58857,0.16285,0.22133]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13147.0,"contact_point_centroid":[0.54667,0.1073,0.23085],"force_p95":0.10863,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25912,"mean_force":0.07387,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5449,0.08817,0.22874]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5955.0,"contact_point_centroid":[0.58835,0.18197,0.22252],"force_p95":0.11168,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2537,"mean_force":0.07122,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.58855,0.1628,0.2216]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53054,0.03081,-0.00209],"force_p95":0.14903,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1957,"mean_force":0.12961,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51783,0.0298,0.0389]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5293.0,"contact_point_centroid":[0.51761,0.01068,0.03936],"force_p95":0.06859,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14404,"mean_force":0.04108,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51658,0.02972,0.03748]},{"body_a":"world","body_b":"grasp_target","contact_count":1176.0,"contact_point_centroid":[0.5305,0.03079,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51365,0.016,0.26531]},{"body_a":"world","body_b":"grasp_target","contact_count":2136.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52398,0.02932,0.13538]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4193.0,"contact_point_centroid":[0.51703,0.04902,0.04029],"force_p95":0.08257,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08395,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51659,0.02972,0.03749]}],"total_contact_groups":12},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.60036,0.17789,0.11753],"final_tcp_position":[0.59582,0.17485,0.14757],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.55314,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":295.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1176.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52526,0.02851,0.22503],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19909,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":534.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2136.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52526,0.0303,0.04751],"tcp_start":[0.52526,0.02851,0.22503],"tcp_to_object_dist_end":0.02212,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53045,0.03032,0.02567],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18392,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14778,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11286.0,"raw_peak_contact_force":0.1957,"subtask_id":"grasp_1","tcp_end":[0.51655,0.02972,0.03745],"tcp_start":[0.52526,0.0303,0.04751],"tcp_to_object_dist_end":0.01823,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.52548,0.03036,0.12083],"object_pos_start":[0.53045,0.03032,0.02567],"object_to_goal_dist_end":0.16708,"object_to_goal_dist_start":0.18392,"object_z_max":0.12069,"peak_contact_force":0.10987,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19860.0,"raw_peak_contact_force":0.55314,"tcp_end":[0.51258,0.02946,0.13983],"tcp_start":[0.51655,0.02972,0.03745],"tcp_to_object_dist_end":0.02298,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59316,0.15539,0.2671],"object_pos_start":[0.52548,0.03036,0.12083],"object_to_goal_dist_end":0.16091,"object_to_goal_dist_start":0.16708,"object_z_max":0.26705,"peak_contact_force":0.09273,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28643.0,"raw_peak_contact_force":0.3344,"subtask_id":"transport_arc","tcp_end":[0.58378,0.15246,0.29309],"tcp_start":[0.51258,0.02946,0.13983],"tcp_to_object_dist_end":0.02779,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":421.0,"n_steps_budget":1000.0,"object_pos_end":[0.60036,0.17789,0.11753],"object_pos_start":[0.59316,0.15539,0.2671],"object_to_goal_dist_end":0.00953,"object_to_goal_dist_start":0.16091,"object_z_max":0.2671,"peak_contact_force":0.11904,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12002.0,"raw_peak_contact_force":0.26575,"tcp_end":[0.59582,0.17485,0.14757],"tcp_start":[0.58378,0.15246,0.29309],"tcp_to_object_dist_end":0.03054,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5dcdc1a4e2a8d4c3bb30f9ac92fb306bea0b16a8f449f4d02b0333754e50f910`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02326,"average_solve_count":129.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16761,"descend_1.depth":0.01092,"descend_goal.place_z_offset":0.01672,"lift_1.lift_height":0.14464,"lift_1.speed":0.15509,"transport_1.speed":0.1179,"transport_1.transport_height":0.16742},"optimized_scores":{"best_composite_score":0.22775,"best_fitness_score":0.69775,"best_task_score":0.44899},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":128.0,"contact_point_centroid":[0.50058,-0.0149,-0.00111],"force_p95":0.3447,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6359,"mean_force":0.0854,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48877,-0.0151,0.03803]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7817.0,"contact_point_centroid":[0.53759,0.10962,0.25579],"force_p95":0.15271,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38294,"mean_force":0.10743,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.53469,0.09074,0.25675]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8270.0,"contact_point_centroid":[0.48786,-0.03418,0.09514],"force_p95":0.10458,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33306,"mean_force":0.06712,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48623,-0.01507,0.09263]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9843.0,"contact_point_centroid":[0.48869,0.00373,0.09215],"force_p95":0.09747,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33034,"mean_force":0.05819,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48624,-0.01507,0.09046]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9174.0,"contact_point_centroid":[0.54319,0.07449,0.25454],"force_p95":0.13462,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26405,"mean_force":0.09451,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.535,0.09136,0.25671]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11916.0,"contact_point_centroid":[0.50044,-0.01104,0.2168],"force_p95":0.10533,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20061,"mean_force":0.07806,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49452,0.00745,0.21527]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11610.0,"contact_point_centroid":[0.49991,0.02605,0.21642],"force_p95":0.10828,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18368,"mean_force":0.08022,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.4945,0.00736,0.21498]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01573,-0.00205],"force_p95":0.13756,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17305,"mean_force":0.12642,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49146,-0.01512,0.03744]},{"body_a":"world","body_b":"grasp_target","contact_count":1192.0,"contact_point_centroid":[0.50382,-0.01567,-0.00189],"force_p95":0.13623,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49912,-2e-05,0.25194]},{"body_a":"world","body_b":"grasp_target","contact_count":1968.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49808,-0.01249,0.1242]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5171.0,"contact_point_centroid":[0.49116,0.00394,0.03794],"force_p95":0.06663,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10196,"mean_force":0.0422,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49024,-0.01511,0.03614]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4166.0,"contact_point_centroid":[0.48962,-0.03437,0.03869],"force_p95":0.07844,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09106,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49024,-0.01511,0.03614]}],"total_contact_groups":12},"final_pose_error":0.04013,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.5749,0.13853,0.13907],"final_tcp_position":[0.56704,0.15349,0.25692],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":0.6359,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":299.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1192.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49995,-0.00986,0.20449],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17861,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":492.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1968.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49874,-0.01516,0.04529],"tcp_start":[0.49995,-0.00986,0.20449],"tcp_to_object_dist_end":0.01993,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50371,-0.01558,0.02582],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31234,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13713,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11137.0,"raw_peak_contact_force":0.17305,"subtask_id":"grasp_1","tcp_end":[0.49021,-0.01511,0.03611],"tcp_start":[0.49874,-0.01516,0.04529],"tcp_to_object_dist_end":0.01697,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.50193,-0.01565,0.14714],"object_pos_start":[0.50371,-0.01558,0.02582],"object_to_goal_dist_end":0.24221,"object_to_goal_dist_start":0.31234,"object_z_max":0.14697,"peak_contact_force":0.10604,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18241.0,"raw_peak_contact_force":0.6359,"tcp_end":[0.48654,-0.01506,0.16582],"tcp_start":[0.49021,-0.01511,0.03611],"tcp_to_object_dist_end":0.02421,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51488,0.03206,0.23522],"object_pos_start":[0.50193,-0.01565,0.14714],"object_to_goal_dist_end":0.17175,"object_to_goal_dist_start":0.24221,"object_z_max":0.23516,"peak_contact_force":0.09298,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23526.0,"raw_peak_contact_force":0.20061,"subtask_id":"transport_arc","tcp_end":[0.50673,0.03146,0.26163],"tcp_start":[0.48654,-0.01506,0.16582],"tcp_to_object_dist_end":0.02765,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5749,0.13853,0.13907],"object_pos_start":[0.51488,0.03206,0.23522],"object_to_goal_dist_end":0.12011,"object_to_goal_dist_start":0.17175,"object_z_max":0.23523,"peak_contact_force":0.0,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":16991.0,"raw_peak_contact_force":0.38294,"tcp_end":[0.56704,0.15349,0.25692],"tcp_start":[0.50673,0.03146,0.26163],"tcp_to_object_dist_end":0.11905,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `53da4dc33bcb1151bde99c46f4ec5d44dda63d23acc62ec623c12d4d0fb32574`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.01681,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12965,"descend_1.depth":0.01068,"descend_goal.place_z_offset":0.0243,"lift_1.lift_height":0.12999,"lift_1.speed":0.14176,"transport_1.speed":0.15716,"transport_1.transport_height":0.10283},"optimized_scores":{"best_composite_score":0.50325,"best_fitness_score":0.97325,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":152.0,"contact_point_centroid":[0.50976,0.03868,-0.00121],"force_p95":0.32887,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58628,"mean_force":0.09155,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49699,0.03851,0.03727]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7745.0,"contact_point_centroid":[0.49654,0.05752,0.08677],"force_p95":0.10936,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34042,"mean_force":0.07139,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49454,0.03832,0.08415]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9918.0,"contact_point_centroid":[0.49753,0.0197,0.08488],"force_p95":0.09862,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31756,"mean_force":0.05781,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49453,0.03832,0.08349]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9084.0,"contact_point_centroid":[0.60185,0.12689,0.18479],"force_p95":0.09141,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27889,"mean_force":0.06336,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.59637,0.14485,0.18665]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14164.0,"contact_point_centroid":[0.53826,0.06029,0.19283],"force_p95":0.09774,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25735,"mean_force":0.06954,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53114,0.07807,0.1922]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8042.0,"contact_point_centroid":[0.59367,0.16264,0.18808],"force_p95":0.09783,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24781,"mean_force":0.06892,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.5952,0.1437,0.1878]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11742.0,"contact_point_centroid":[0.53466,0.09822,0.19487],"force_p95":0.11116,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21878,"mean_force":0.08059,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53214,0.07905,0.19294]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51255,0.03974,-0.00209],"force_p95":0.14859,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19074,"mean_force":0.12936,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49988,0.03876,0.03687]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5047.0,"contact_point_centroid":[0.50031,0.01964,0.03701],"force_p95":0.07294,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15559,"mean_force":0.04309,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49865,0.03866,0.03552]},{"body_a":"world","body_b":"grasp_target","contact_count":1776.0,"contact_point_centroid":[0.51251,0.03972,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50242,0.02643,0.23713]},{"body_a":"world","body_b":"grasp_target","contact_count":1524.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50607,0.03959,0.10612]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4187.0,"contact_point_centroid":[0.49893,0.05794,0.03827],"force_p95":0.08497,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08913,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49866,0.03866,0.03553]}],"total_contact_groups":12},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.6192,0.17,0.13246],"final_tcp_position":[0.62053,0.16857,0.16346],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.58628,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":445.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1776.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50759,0.04002,0.16833],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14239,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":381.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1524.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50721,0.03936,0.04497],"tcp_start":[0.50759,0.04002,0.16833],"tcp_to_object_dist_end":0.01968,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51247,0.03924,0.02568],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21273,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14763,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11034.0,"raw_peak_contact_force":0.19074,"subtask_id":"grasp_1","tcp_end":[0.49863,0.03865,0.03549],"tcp_start":[0.50721,0.03936,0.04497],"tcp_to_object_dist_end":0.01697,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.5103,0.03924,0.13245],"object_pos_start":[0.51247,0.03924,0.02568],"object_to_goal_dist_end":0.17797,"object_to_goal_dist_start":0.21273,"object_z_max":0.1323,"peak_contact_force":0.10671,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17815.0,"raw_peak_contact_force":0.58628,"tcp_end":[0.49476,0.03834,0.15086],"tcp_start":[0.49863,0.03865,0.03549],"tcp_to_object_dist_end":0.02411,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5754,0.11695,0.19584],"object_pos_start":[0.5103,0.03924,0.13245],"object_to_goal_dist_end":0.09161,"object_to_goal_dist_start":0.17797,"object_z_max":0.19581,"peak_contact_force":0.09149,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25906.0,"raw_peak_contact_force":0.25735,"subtask_id":"transport_arc","tcp_end":[0.56789,0.11499,0.2218],"tcp_start":[0.49476,0.03834,0.15086],"tcp_to_object_dist_end":0.02709,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":558.0,"n_steps_budget":1000.0,"object_pos_end":[0.6192,0.17,0.13246],"object_pos_start":[0.5754,0.11695,0.19584],"object_to_goal_dist_end":0.01531,"object_to_goal_dist_start":0.09161,"object_z_max":0.19584,"peak_contact_force":0.09139,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":17126.0,"raw_peak_contact_force":0.27889,"tcp_end":[0.62053,0.16857,0.16346],"tcp_start":[0.56789,0.11499,0.2218],"tcp_to_object_dist_end":0.03107,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```