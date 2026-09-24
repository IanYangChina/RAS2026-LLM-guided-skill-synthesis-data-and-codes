## Search State

- **Seed**: 5
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1731 | 0.41 | ✅ accepted |
| 0 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.2807 | 0.21 | ✅ accepted |

**Proposal policy**: task_score is 0.41 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.173) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
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
    orientation:
      mode: none
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
    - 0.1
    orientation:
      mode: none
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
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
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
      - 0.02
      - 0.1
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
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
      mode: none

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
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15]
  - orientation: mode=none
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=none
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
    - transport_height: status=consumed; consumers=target.offset.z (replace)
- **descend_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03]
  - orientation: mode=none
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.173
- **task_score** (E): 0.407
- **fitness_score**: 0.673  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.500

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0482 |
| descend_1 | 1.00 | 1.00 | 0.2266 |
| grasp_1 | 1.00 | 1.00 | 0.0129 |
| lift_1 | 0.00 | 1.00 | 0.1230 |
| transport_1 | 0.00 | 1.00 | 0.0754 |
| descend_goal | 0.67 | 1.00 | 0.1233 |
| release_1 | 1.00 | 1.00 | 0.0221 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, 0.018, 0.275) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.511, 0.018, 0.275)→(0.511, 0.018, 0.049) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.511, 0.018, 0.049)→(0.502, 0.018, 0.039) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 44.333 | 0.146 | 0.189 |
| lift_1 | lift | 0.00 / step_budget | (0.502, 0.018, 0.039)→(0.498, 0.017, 0.162) | (0.516, 0.018, 0.026)→(0.506, 0.018, 0.141) | 0.236→0.203 | 1.00 / 37.333 | 0.079 | 0.517 |
| transport_1 | approach | 0.00 / step_budget | (0.498, 0.017, 0.162)→(0.526, 0.063, 0.214) | (0.506, 0.018, 0.141)→(0.530, 0.064, 0.189) | 0.203→0.153 | 1.00 / 35.667 | 0.086 | 0.144 |
| descend_goal | descend | 0.67 / step_budget | (0.526, 0.063, 0.214)→(0.588, 0.154, 0.195) | (0.530, 0.064, 0.189)→(0.584, 0.165, 0.085) | 0.153→0.095 | 1.00 / 17.667 | 91002.026 | 0.851 |
| release_1 | release | 1.00 / step_budget | (0.588, 0.154, 0.195)→(0.583, 0.153, 0.217) | (0.584, 0.165, 0.085)→(0.578, 0.164, 0.023) | 0.095→0.148 | 1.00 / 4.000 | 0.114 | 1.180 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.569
- phase_score: 0.283
- phase_breakdown.transport_arc_score: 0.000
- phase_breakdown.descend_1_score: 0.896
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.284
- phase_breakdown.approach_1_score: 0.021
- grasp_place_fitness: 0.755

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.755
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.569
- **Median Q (composite search score)**: 0.197
- **K-run variance**: 0.0061
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.364


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55696,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18591,"descend_1.depth":0.01387,"descend_goal.place_z_offset":0.04746,"lift_1.lift_height":0.19772,"lift_1.speed":0.0623,"transport_1.speed":0.04941,"transport_1.transport_height":0.23441},"optimized_scores":{"best_composite_score":0.25501,"best_fitness_score":0.75501,"best_task_score":0.56879},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":292.0,"contact_point_centroid":[0.58115,0.17038,-0.00465],"force_p95":0.72467,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.1709,"mean_force":0.2322,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58953,0.17277,0.15875]},{"body_a":"world","body_b":"grasp_target","contact_count":191.0,"contact_point_centroid":[0.52579,0.0294,-0.00119],"force_p95":0.3195,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51451,"mean_force":0.09525,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51472,0.02959,0.04002]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.51254,0.04863,0.09114],"force_p95":0.08256,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31416,"mean_force":0.05834,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51217,0.02944,0.08839]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20720.0,"contact_point_centroid":[0.51367,0.01048,0.08908],"force_p95":0.07655,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28643,"mean_force":0.04922,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51216,0.02944,0.08739]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18295.0,"contact_point_centroid":[0.56674,0.10488,0.16464],"force_p95":0.09029,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.234,"mean_force":0.05468,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.56371,0.12354,0.16553]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16232.0,"contact_point_centroid":[0.56032,0.14253,0.16621],"force_p95":0.09628,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23224,"mean_force":0.0603,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.56391,0.12385,0.16542]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":707.0,"contact_point_centroid":[0.58919,0.19249,0.14289],"force_p95":0.10716,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20776,"mean_force":0.07048,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59369,0.17407,0.14508]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53054,0.03082,-0.00209],"force_p95":0.14885,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1933,"mean_force":0.12957,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51784,0.02981,0.03972]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":781.0,"contact_point_centroid":[0.5981,0.15629,0.13961],"force_p95":0.10081,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19138,"mean_force":0.066,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59361,0.17405,0.14495]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5294.0,"contact_point_centroid":[0.51762,0.01068,0.04017],"force_p95":0.06863,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14593,"mean_force":0.04109,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5166,0.02972,0.0383]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18359.0,"contact_point_centroid":[0.52254,0.07117,0.16779],"force_p95":0.07782,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14188,"mean_force":0.05255,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5223,0.05195,0.16507]},{"body_a":"world","body_b":"grasp_target","contact_count":1192.0,"contact_point_centroid":[0.5305,0.03079,-0.00189],"force_p95":0.13623,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51368,0.01605,0.26492]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20790.0,"contact_point_centroid":[0.5253,0.03283,0.16633],"force_p95":0.06922,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12886,"mean_force":0.04676,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52216,0.05171,0.16476]},{"body_a":"world","body_b":"grasp_target","contact_count":2108.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.524,0.02935,0.13539]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4191.0,"contact_point_centroid":[0.51703,0.04903,0.04111],"force_p95":0.0826,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08396,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5166,0.02972,0.0383]}],"total_contact_groups":15},"final_pose_error":0.01016,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.58104,0.17012,0.02641],"final_tcp_position":[0.59551,0.17449,0.14847],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.1709,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":299.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1192.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.52528,0.02856,0.22412],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19818,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":527.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2108.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52527,0.0303,0.04833],"tcp_start":[0.52528,0.02856,0.22412],"tcp_to_object_dist_end":0.02292,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53045,0.03033,0.02567],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18391,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.1476,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11285.0,"raw_peak_contact_force":0.1933,"tcp_end":[0.51657,0.02972,0.03826],"tcp_start":[0.52527,0.0303,0.04833],"tcp_to_object_dist_end":0.01876,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51985,0.03009,0.12002],"object_pos_start":[0.53045,0.03033,0.02567],"object_to_goal_dist_end":0.1699,"object_to_goal_dist_start":0.18391,"object_z_max":0.11991,"peak_contact_force":0.07949,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37911.0,"raw_peak_contact_force":0.51451,"tcp_end":[0.51237,0.02945,0.13983],"tcp_start":[0.51657,0.02972,0.03826],"tcp_to_object_dist_end":0.02118,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53798,0.07101,0.16479],"object_pos_start":[0.51985,0.03009,0.12002],"object_to_goal_dist_end":0.1372,"object_to_goal_dist_start":0.1699,"object_z_max":0.16474,"peak_contact_force":0.08373,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":39149.0,"raw_peak_contact_force":0.14188,"tcp_end":[0.53311,0.0699,0.18905],"tcp_start":[0.51237,0.02945,0.13983],"tcp_to_object_dist_end":0.02477,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59211,0.17539,0.11705],"object_pos_start":[0.53798,0.07101,0.16479],"object_to_goal_dist_end":0.01339,"object_to_goal_dist_start":0.1372,"object_z_max":0.16479,"peak_contact_force":0.10881,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":34527.0,"raw_peak_contact_force":0.234,"tcp_end":[0.59551,0.17449,0.14847],"tcp_start":[0.53311,0.0699,0.18905],"tcp_to_object_dist_end":0.03161,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58104,0.17012,0.02641],"object_pos_start":[0.59211,0.17539,0.11705],"object_to_goal_dist_end":0.08464,"object_to_goal_dist_start":0.01339,"object_z_max":0.11705,"peak_contact_force":0.1178,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1780.0,"raw_peak_contact_force":1.1709,"tcp_end":[0.58944,0.17274,0.16958],"tcp_start":[0.59551,0.17449,0.14847],"tcp_to_object_dist_end":0.14345,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53659,"average_solve_count":164.0,"average_success_count":164.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.24674,"descend_1.depth":0.01902,"descend_goal.place_z_offset":0.07057,"lift_1.lift_height":0.26324,"lift_1.speed":0.06455,"transport_1.speed":0.03781,"transport_1.transport_height":0.18711},"optimized_scores":{"best_composite_score":0.06762,"best_fitness_score":0.56762,"best_task_score":0.20538},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":36.0,"contact_point_centroid":[0.55053,0.14326,-0.00973],"force_p95":2.04615,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.07651,"mean_force":1.3277,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.54813,0.11741,0.2651]},{"body_a":"world","body_b":"grasp_target","contact_count":786.0,"contact_point_centroid":[0.54637,0.15775,-0.00315],"force_p95":0.37523,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.11651,"mean_force":0.14722,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5455,0.1175,0.2682]},{"body_a":"world","body_b":"grasp_target","contact_count":161.0,"contact_point_centroid":[0.49966,-0.01477,-0.00111],"force_p95":0.29434,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43747,"mean_force":0.08471,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48894,-0.01523,0.04596]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10183.0,"contact_point_centroid":[0.5276,0.05291,0.23199],"force_p95":0.13743,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41618,"mean_force":0.08256,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.52395,0.07105,0.23472]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21418.0,"contact_point_centroid":[0.48728,0.00395,0.09683],"force_p95":0.072,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28114,"mean_force":0.04788,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48629,-0.01519,0.09498]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20375.0,"contact_point_centroid":[0.48646,-0.03438,0.09887],"force_p95":0.07173,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26907,"mean_force":0.04952,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48628,-0.01519,0.09588]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10620.0,"contact_point_centroid":[0.52297,0.09067,0.233],"force_p95":0.11131,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19321,"mean_force":0.07597,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.52461,0.07235,0.23555]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01574,-0.00204],"force_p95":0.13708,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1692,"mean_force":0.12634,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49175,-0.01525,0.04556]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18627.0,"contact_point_centroid":[0.49761,-0.00743,0.18375],"force_p95":0.07562,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14117,"mean_force":0.0519,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49631,0.0116,0.18298]},{"body_a":"world","body_b":"grasp_target","contact_count":296.0,"contact_point_centroid":[0.50382,-0.01567,-0.00158],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1245,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49989,-0.00457,0.29311]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18664.0,"contact_point_centroid":[0.49633,0.0307,0.18334],"force_p95":0.07914,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13469,"mean_force":0.05245,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49633,0.01164,0.18305]},{"body_a":"world","body_b":"grasp_target","contact_count":2808.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.1226,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49857,-0.01252,0.16757]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5572.0,"contact_point_centroid":[0.49137,0.004,0.04669],"force_p95":0.06327,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09401,"mean_force":0.03982,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49055,-0.01524,0.04426]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5131.0,"contact_point_centroid":[0.49034,-0.03451,0.04817],"force_p95":0.06791,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08128,"mean_force":0.04272,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49055,-0.01524,0.04426]},{"body_a":"left_finger","body_b":"right_finger","contact_count":99.0,"contact_point_centroid":[0.54661,0.11773,0.26444],"force_p95":0.01516,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01611,"mean_force":0.01125,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54686,0.11785,0.26191]}],"total_contact_groups":15},"final_pose_error":0.0955,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.54629,0.15816,0.01602],"final_tcp_position":[0.54846,0.11805,0.26553],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273005.84927,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":75.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02593],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31229,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12241,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":296.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.50035,-0.00978,0.28396],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25812,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":702.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02593],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31229,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2808.0,"raw_peak_contact_force":0.12264,"tcp_end":[0.49893,-0.01529,0.05343],"tcp_start":[0.50035,-0.00978,0.28396],"tcp_to_object_dist_end":0.02785,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50374,-0.01558,0.02582],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31234,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13712,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12503.0,"raw_peak_contact_force":0.1692,"tcp_end":[0.49052,-0.01524,0.04423],"tcp_start":[0.49893,-0.01529,0.05343],"tcp_to_object_dist_end":0.02267,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49289,-0.01562,0.12611],"object_pos_start":[0.50374,-0.01558,0.02582],"object_to_goal_dist_end":0.25488,"object_to_goal_dist_start":0.31234,"object_z_max":0.12599,"peak_contact_force":0.07743,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41954.0,"raw_peak_contact_force":0.43747,"tcp_end":[0.4865,-0.01519,0.15055],"tcp_start":[0.49052,-0.01524,0.04423],"tcp_to_object_dist_end":0.02527,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51119,0.03567,0.18678],"object_pos_start":[0.49289,-0.01562,0.12611],"object_to_goal_dist_end":0.18036,"object_to_goal_dist_start":0.25488,"object_z_max":0.18671,"peak_contact_force":0.09868,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37291.0,"raw_peak_contact_force":0.14117,"tcp_end":[0.50836,0.03561,0.21635],"tcp_start":[0.4865,-0.01519,0.15055],"tcp_to_object_dist_end":0.0297,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54168,0.15025,-0.00383],"object_pos_start":[0.51119,0.03567,0.18678],"object_to_goal_dist_end":0.25867,"object_to_goal_dist_start":0.18036,"object_z_max":0.22238,"peak_contact_force":273005.84927,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":20839.0,"raw_peak_contact_force":2.07651,"tcp_end":[0.54846,0.11805,0.26553],"tcp_start":[0.50836,0.03561,0.21635],"tcp_to_object_dist_end":0.27136,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54629,0.15816,0.01602],"object_pos_start":[0.54168,0.15025,-0.00383],"object_to_goal_dist_end":0.23744,"object_to_goal_dist_start":0.25867,"object_z_max":0.01711,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":885.0,"raw_peak_contact_force":1.11651,"tcp_end":[0.54446,0.11723,0.28845],"tcp_start":[0.54846,0.11805,0.26553],"tcp_to_object_dist_end":0.27549,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.59043,"average_solve_count":188.0,"average_success_count":188.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.29544,"descend_1.depth":0.01007,"descend_goal.place_z_offset":0.034,"lift_1.lift_height":0.29977,"lift_1.speed":0.09963,"transport_1.speed":0.01028,"transport_1.transport_height":0.19261},"optimized_scores":{"best_composite_score":0.19665,"best_fitness_score":0.69665,"best_task_score":0.44582},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":256.0,"contact_point_centroid":[0.60534,0.16533,-0.00551],"force_p95":0.83492,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.25109,"mean_force":0.26828,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61567,0.16765,0.18256]},{"body_a":"world","body_b":"grasp_target","contact_count":143.0,"contact_point_centroid":[0.50926,0.0378,-0.00122],"force_p95":0.3309,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59851,"mean_force":0.08836,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49735,0.03822,0.03711]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.49532,0.05724,0.11727],"force_p95":0.08351,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34188,"mean_force":0.05888,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49489,0.03803,0.11456]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20501.0,"contact_point_centroid":[0.49701,0.01912,0.11473],"force_p95":0.07884,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3175,"mean_force":0.05034,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49488,0.03803,0.11322]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16618.0,"contact_point_centroid":[0.5779,0.14822,0.20075],"force_p95":0.08613,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24374,"mean_force":0.05635,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.58137,0.12951,0.19934]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":661.0,"contact_point_centroid":[0.61604,0.18754,0.16615],"force_p95":0.11736,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.224,"mean_force":0.0756,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61958,0.16884,0.16824]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18448.0,"contact_point_centroid":[0.584,0.11012,0.19932],"force_p95":0.07853,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22357,"mean_force":0.05218,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.5807,0.12885,0.19978]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.03971,-0.00212],"force_p95":0.15572,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20589,"mean_force":0.13129,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50019,0.03846,0.0366]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":869.0,"contact_point_centroid":[0.62324,0.15092,0.16396],"force_p95":0.09818,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20561,"mean_force":0.05952,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61964,0.16885,0.16836]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5037.0,"contact_point_centroid":[0.50055,0.01935,0.03671],"force_p95":0.07334,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17614,"mean_force":0.04306,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49896,0.03836,0.03525]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16702.0,"contact_point_centroid":[0.51657,0.08168,0.21888],"force_p95":0.08839,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14854,"mean_force":0.0583,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51653,0.0625,0.21657]},{"body_a":"world","body_b":"grasp_target","contact_count":1480.0,"contact_point_centroid":[0.51251,0.03972,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50299,0.01654,0.30998]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19402.0,"contact_point_centroid":[0.51992,0.04365,0.21743],"force_p95":0.07549,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13556,"mean_force":0.05064,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51631,0.06228,0.21633]},{"body_a":"world","body_b":"grasp_target","contact_count":3300.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50703,0.03658,0.18028]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4207.0,"contact_point_centroid":[0.49912,0.05766,0.03791],"force_p95":0.08458,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08967,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49896,0.03837,0.03526]}],"total_contact_groups":15},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60577,0.16522,0.02605],"final_tcp_position":[0.62134,0.16925,0.17193],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.25109,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":371.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1480.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.50843,0.03423,0.31818],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.29224,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":825.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3300.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50753,0.03906,0.04473],"tcp_start":[0.50843,0.03423,0.31818],"tcp_to_object_dist_end":0.01937,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51249,0.03901,0.02559],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21291,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15371,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11044.0,"raw_peak_contact_force":0.20589,"tcp_end":[0.49893,0.03836,0.03522],"tcp_start":[0.50753,0.03906,0.04473],"tcp_to_object_dist_end":0.01664,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50422,0.03889,0.17797],"object_pos_start":[0.51249,0.03901,0.02559],"object_to_goal_dist_end":0.18482,"object_to_goal_dist_start":0.21291,"object_z_max":0.17778,"peak_contact_force":0.08135,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37644.0,"raw_peak_contact_force":0.59851,"tcp_end":[0.49534,0.03807,0.19626],"tcp_start":[0.49893,0.03836,0.03522],"tcp_to_object_dist_end":0.02034,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54233,0.08397,0.21398],"object_pos_start":[0.50422,0.03889,0.17797],"object_to_goal_dist_end":0.14094,"object_to_goal_dist_start":0.18482,"object_z_max":0.21395,"peak_contact_force":0.07572,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36104.0,"raw_peak_contact_force":0.14854,"tcp_end":[0.53657,0.08278,0.23726],"tcp_start":[0.49534,0.03807,0.19626],"tcp_to_object_dist_end":0.02401,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":945.0,"n_steps_budget":1000.0,"object_pos_end":[0.61689,0.17011,0.1415],"object_pos_start":[0.54233,0.08397,0.21398],"object_to_goal_dist_end":0.0115,"object_to_goal_dist_start":0.14094,"object_z_max":0.21398,"peak_contact_force":0.11966,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":35066.0,"raw_peak_contact_force":0.24374,"tcp_end":[0.62134,0.16925,0.17193],"tcp_start":[0.53657,0.08278,0.23726],"tcp_to_object_dist_end":0.03077,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60577,0.16522,0.02605],"object_pos_start":[0.61689,0.17011,0.1415],"object_to_goal_dist_end":0.12118,"object_to_goal_dist_start":0.0115,"object_z_max":0.1415,"peak_contact_force":0.1021,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1786.0,"raw_peak_contact_force":1.25109,"tcp_end":[0.6156,0.16764,0.19216],"tcp_start":[0.62134,0.16925,0.17193],"tcp_to_object_dist_end":0.16642,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```