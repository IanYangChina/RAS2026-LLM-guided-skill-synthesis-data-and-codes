## Search State

- **Seed**: 5
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.3292 | 0.95 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | 0.0259 | 0.41 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.2014 | 0.22 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.1205 | 0.22 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.1203 | 0.22 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.95). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.329) — your mutation base

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

- **Composite score**: 0.329
- **task_score** (E): 0.952
- **fitness_score**: 0.949  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.620

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0748 |
| descend_1 | 1.00 | 1.00 | 0.1873 |
| grasp_1 | 1.00 | 1.00 | 0.0129 |
| lift_1 | 0.67 | 1.00 | 0.1526 |
| transport_1 | 0.33 | 1.00 | 0.1639 |
| descend_goal | 1.00 | 1.00 | 0.1213 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, 0.019, 0.232) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.122 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.511, 0.019, 0.232)→(0.510, 0.018, 0.045) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.510, 0.018, 0.045)→(0.502, 0.018, 0.036) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 42.333 | 0.143 | 0.183 |
| lift_1 | lift | 0.67 / step_budget | (0.502, 0.018, 0.036)→(0.498, 0.018, 0.188) | (0.516, 0.018, 0.026)→(0.511, 0.018, 0.169) | 0.236→0.202 | 1.00 / 29.667 | 0.110 | 0.588 |
| transport_1 | approach | 0.33 / step_budget | (0.498, 0.018, 0.188)→(0.570, 0.122, 0.287) | (0.511, 0.018, 0.169)→(0.575, 0.124, 0.260) | 0.202→0.122 | 1.00 / 32.000 | 0.101 | 0.269 |
| descend_goal | descend | 1.00 / step_budget | (0.570, 0.122, 0.287)→(0.599, 0.174, 0.189) | (0.575, 0.124, 0.260)→(0.597, 0.176, 0.158) | 0.122→0.016 | 1.00 / 25.667 | 56008.447 | 0.304 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.444
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.255
- phase_breakdown.transport_arc_score: 0.031
- phase_breakdown.descend_1_score: 0.852
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.000
- phase_breakdown.approach_1_score: 0.047
- grasp_place_fitness: 0.974

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.974
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.354
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: descend_1.depth
- **Final σ (mean)**: 0.326


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13182,"average_solve_count":220.0,"average_success_count":220.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14615,"approach_1.approach_speed":0.02242,"descend_1.depth":0.01001,"descend_1.descend_speed":0.09543,"descend_goal.descend_goal_speed":0.18549,"descend_goal.place_z_offset":0.02965,"lift_1.lift_height":0.15745,"lift_1.lift_speed":0.11159,"transport_1.transport_height":0.19179,"transport_1.transport_speed":0.14013},"optimized_scores":{"best_composite_score":0.35396,"best_fitness_score":0.97396,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":157.0,"contact_point_centroid":[0.52566,0.02938,-0.00126],"force_p95":0.37027,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63009,"mean_force":0.10726,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51455,0.02984,0.03568]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14282.0,"contact_point_centroid":[0.51289,0.04891,0.10637],"force_p95":0.10116,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3514,"mean_force":0.06048,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5121,0.02969,0.10406]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17048.0,"contact_point_centroid":[0.51398,0.0109,0.10416],"force_p95":0.08085,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33093,"mean_force":0.05056,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51211,0.02969,0.10255]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8600.0,"contact_point_centroid":[0.57859,0.11998,0.193],"force_p95":0.09238,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28896,"mean_force":0.05954,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.5732,0.13797,0.19368]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6785.0,"contact_point_centroid":[0.57194,0.15603,0.19666],"force_p95":0.11073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27425,"mean_force":0.07353,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.57248,0.13677,0.19563]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53052,0.03081,-0.00207],"force_p95":0.14334,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18713,"mean_force":0.12793,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51751,0.03005,0.03562]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12418.0,"contact_point_centroid":[0.53173,0.0833,0.22039],"force_p95":0.11476,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17829,"mean_force":0.07783,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53014,0.06407,0.21906]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16538.0,"contact_point_centroid":[0.53432,0.04546,0.21865],"force_p95":0.08829,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17267,"mean_force":0.058,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5298,0.06349,0.21837]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5292.0,"contact_point_centroid":[0.51737,0.01093,0.03615],"force_p95":0.06993,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1414,"mean_force":0.0411,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51626,0.02996,0.0342]},{"body_a":"world","body_b":"grasp_target","contact_count":1908.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13338,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50982,0.02162,0.24386]},{"body_a":"world","body_b":"grasp_target","contact_count":1700.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52297,0.03104,0.11306]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4182.0,"contact_point_centroid":[0.51684,0.04927,0.03701],"force_p95":0.08263,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08549,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51626,0.02996,0.03421]}],"total_contact_groups":12},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59186,0.17334,0.10967],"final_tcp_position":[0.59398,0.17213,0.13815],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":478.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1908.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52368,0.0317,0.18311],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15724,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":425.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1700.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52498,0.03056,0.04421],"tcp_start":[0.52368,0.0317,0.18311],"tcp_to_object_dist_end":0.01901,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53041,0.03045,0.02575],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18379,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14281,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11274.0,"raw_peak_contact_force":0.18713,"subtask_id":"grasp_1","tcp_end":[0.51623,0.02996,0.03417],"tcp_start":[0.52498,0.03056,0.04421],"tcp_to_object_dist_end":0.0165,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":829.0,"n_steps_budget":900.0,"object_pos_end":[0.52406,0.03039,0.16107],"object_pos_start":[0.53041,0.03045,0.02575],"object_to_goal_dist_end":0.17542,"object_to_goal_dist_start":0.18379,"object_z_max":0.16094,"peak_contact_force":0.11189,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":31487.0,"raw_peak_contact_force":0.63009,"tcp_end":[0.51255,0.02972,0.17847],"tcp_start":[0.51623,0.02996,0.03417],"tcp_to_object_dist_end":0.02087,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56099,0.10463,0.23249],"object_pos_start":[0.52406,0.03039,0.16107],"object_to_goal_dist_end":0.1503,"object_to_goal_dist_start":0.17542,"object_z_max":0.23246,"peak_contact_force":0.11676,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28956.0,"raw_peak_contact_force":0.17829,"subtask_id":"transport_arc","tcp_end":[0.55346,0.10266,0.25674],"tcp_start":[0.51255,0.02972,0.17847],"tcp_to_object_dist_end":0.02547,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":485.0,"n_steps_budget":1000.0,"object_pos_end":[0.59186,0.17334,0.10967],"object_pos_start":[0.56099,0.10463,0.23249],"object_to_goal_dist_end":0.01111,"object_to_goal_dist_start":0.1503,"object_z_max":0.23249,"peak_contact_force":167951.73011,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":15385.0,"raw_peak_contact_force":0.28896,"tcp_end":[0.59398,0.17213,0.13815],"tcp_start":[0.55346,0.10266,0.25674],"tcp_to_object_dist_end":0.02858,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.15179,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.23821,"approach_1.approach_speed":0.17065,"descend_1.depth":0.01206,"descend_1.descend_speed":0.15228,"descend_goal.descend_goal_speed":0.23971,"descend_goal.place_z_offset":0.01452,"lift_1.lift_height":0.14625,"lift_1.lift_speed":0.27752,"transport_1.transport_height":0.10491,"transport_1.transport_speed":0.23456},"optimized_scores":{"best_composite_score":0.2799,"best_fitness_score":0.8999,"best_task_score":0.85531},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":124.0,"contact_point_centroid":[0.5005,-0.01528,-0.00111],"force_p95":0.3289,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56254,"mean_force":0.08235,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48895,-0.01532,0.0393]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9940.0,"contact_point_centroid":[0.48876,0.00355,0.09449],"force_p95":0.09729,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3305,"mean_force":0.0577,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4864,-0.01529,0.0928]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8588.0,"contact_point_centroid":[0.48798,-0.0344,0.0964],"force_p95":0.10395,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32872,"mean_force":0.06492,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48638,-0.01529,0.09385]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5633.0,"contact_point_centroid":[0.56121,0.16189,0.28021],"force_p95":0.13498,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30966,"mean_force":0.08598,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.56187,0.14303,0.28089]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12065.0,"contact_point_centroid":[0.5197,0.02484,0.24569],"force_p95":0.10602,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28948,"mean_force":0.07819,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51278,0.04298,0.24429]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5946.0,"contact_point_centroid":[0.57002,0.12704,0.27825],"force_p95":0.12584,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28891,"mean_force":0.08268,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.56245,0.14418,0.28018]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12085.0,"contact_point_centroid":[0.51688,0.06162,0.24542],"force_p95":0.10827,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22209,"mean_force":0.07829,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51266,0.0427,0.24388]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01575,-0.00203],"force_p95":0.13367,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15681,"mean_force":0.12545,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49161,-0.01534,0.03876]},{"body_a":"world","body_b":"grasp_target","contact_count":388.0,"contact_point_centroid":[0.50382,-0.01567,-0.00168],"force_p95":0.1382,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12394,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49994,-0.0057,0.2895]},{"body_a":"world","body_b":"grasp_target","contact_count":2628.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49863,-0.01341,0.16053]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5086.0,"contact_point_centroid":[0.49141,0.00372,0.03916],"force_p95":0.06786,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09664,"mean_force":0.04296,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49039,-0.01533,0.03746]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4149.0,"contact_point_centroid":[0.48971,-0.03457,0.03997],"force_p95":0.07851,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09351,"mean_force":0.05179,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49039,-0.01533,0.03746]}],"total_contact_groups":12},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.58544,0.18385,0.225],"final_tcp_position":[0.58103,0.18083,0.25812],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":0.56254,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":98.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02601],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31224,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.1222,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":388.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50048,-0.01146,0.27648],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25053,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":657.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02601],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31224,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2628.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.49888,-0.01539,0.04663],"tcp_start":[0.50048,-0.01146,0.27648],"tcp_to_object_dist_end":0.0212,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5037,-0.01573,0.02587],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31241,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13365,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11035.0,"raw_peak_contact_force":0.15681,"subtask_id":"grasp_1","tcp_end":[0.49036,-0.01533,0.03743],"tcp_start":[0.49888,-0.01539,0.04663],"tcp_to_object_dist_end":0.01765,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.50191,-0.01586,0.14895],"object_pos_start":[0.5037,-0.01573,0.02587],"object_to_goal_dist_end":0.24164,"object_to_goal_dist_start":0.31241,"object_z_max":0.14877,"peak_contact_force":0.10571,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18652.0,"raw_peak_contact_force":0.56254,"tcp_end":[0.48672,-0.01528,0.16864],"tcp_start":[0.49036,-0.01533,0.03743],"tcp_to_object_dist_end":0.02488,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55354,0.10985,0.2798],"object_pos_start":[0.50191,-0.01586,0.14895],"object_to_goal_dist_end":0.09021,"object_to_goal_dist_start":0.24164,"object_z_max":0.27968,"peak_contact_force":0.09441,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24150.0,"raw_peak_contact_force":0.28948,"subtask_id":"transport_arc","tcp_end":[0.54558,0.10798,0.30693],"tcp_start":[0.48672,-0.01528,0.16864],"tcp_to_object_dist_end":0.02833,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":462.0,"n_steps_budget":1000.0,"object_pos_end":[0.58544,0.18385,0.225],"object_pos_start":[0.55354,0.10985,0.2798],"object_to_goal_dist_end":0.02344,"object_to_goal_dist_start":0.09021,"object_z_max":0.27983,"peak_contact_force":0.12583,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11579.0,"raw_peak_contact_force":0.30966,"tcp_end":[0.58103,0.18083,0.25812],"tcp_start":[0.54558,0.10798,0.30693],"tcp_to_object_dist_end":0.03355,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.09524,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19957,"approach_1.approach_speed":0.16675,"descend_1.depth":0.01,"descend_1.descend_speed":0.13908,"descend_goal.descend_goal_speed":0.2502,"descend_goal.place_z_offset":0.01854,"lift_1.lift_height":0.24785,"lift_1.lift_speed":0.11426,"transport_1.transport_height":0.16093,"transport_1.transport_speed":0.27985},"optimized_scores":{"best_composite_score":0.35372,"best_fitness_score":0.97372,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":161.0,"contact_point_centroid":[0.5088,0.03774,-0.00132],"force_p95":0.30694,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57256,"mean_force":0.09364,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49708,0.03821,0.03668]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19631.0,"contact_point_centroid":[0.55409,0.07773,0.26657],"force_p95":0.0876,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34017,"mean_force":0.0525,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55032,0.09609,0.26602]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16337.0,"contact_point_centroid":[0.4957,0.05726,0.12184],"force_p95":0.10965,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32656,"mean_force":0.06263,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49483,0.03804,0.11976]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5281.0,"contact_point_centroid":[0.60883,0.18022,0.23835],"force_p95":0.11072,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3144,"mean_force":0.06413,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.61435,0.16197,0.23858]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20467.0,"contact_point_centroid":[0.49712,0.01937,0.1231],"force_p95":0.08252,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30529,"mean_force":0.0505,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49484,0.03804,0.12162]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14975.0,"contact_point_centroid":[0.55057,0.11615,0.26795],"force_p95":0.11077,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29344,"mean_force":0.06962,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55125,0.09705,0.26654]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5487.0,"contact_point_centroid":[0.61701,0.14329,0.23544],"force_p95":0.10693,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27731,"mean_force":0.06485,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.61448,0.16209,0.23753]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.03971,-0.00212],"force_p95":0.15577,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20589,"mean_force":0.13129,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50004,0.03846,0.03642]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5037.0,"contact_point_centroid":[0.50044,0.01935,0.03655],"force_p95":0.07343,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17644,"mean_force":0.04305,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49881,0.03836,0.03508]},{"body_a":"world","body_b":"grasp_target","contact_count":1004.0,"contact_point_centroid":[0.51251,0.03972,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12311,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50392,0.01948,0.27132]},{"body_a":"world","body_b":"grasp_target","contact_count":2280.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50664,0.03734,0.1402]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4208.0,"contact_point_centroid":[0.49903,0.05766,0.03778],"force_p95":0.08441,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08955,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49882,0.03836,0.03508]}],"total_contact_groups":12},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.61503,0.16981,0.13955],"final_tcp_position":[0.62179,0.16956,0.17112],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":73.4845,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":252.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1004.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50831,0.03581,0.23771],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21177,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":570.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2280.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50738,0.03906,0.04453],"tcp_start":[0.50831,0.03581,0.23771],"tcp_to_object_dist_end":0.01922,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51249,0.03901,0.02559],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21291,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15377,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11045.0,"raw_peak_contact_force":0.20589,"subtask_id":"grasp_1","tcp_end":[0.49878,0.03836,0.03504],"tcp_start":[0.50738,0.03906,0.04453],"tcp_to_object_dist_end":0.01666,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50574,0.03879,0.19716],"object_pos_start":[0.51249,0.03901,0.02559],"object_to_goal_dist_end":0.18826,"object_to_goal_dist_start":0.21291,"object_z_max":0.19699,"peak_contact_force":0.11121,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36965.0,"raw_peak_contact_force":0.57256,"tcp_end":[0.49546,0.03809,0.21705],"tcp_start":[0.49878,0.03836,0.03504],"tcp_to_object_dist_end":0.0224,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61158,0.15719,0.26809],"object_pos_start":[0.50574,0.03879,0.19716],"object_to_goal_dist_end":0.12504,"object_to_goal_dist_start":0.18826,"object_z_max":0.26809,"peak_contact_force":0.09128,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34606.0,"raw_peak_contact_force":0.34017,"subtask_id":"transport_arc","tcp_end":[0.6101,0.1564,0.29589],"tcp_start":[0.49546,0.03809,0.21705],"tcp_to_object_dist_end":0.02785,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":329.0,"n_steps_budget":1000.0,"object_pos_end":[0.61503,0.16981,0.13955],"object_pos_start":[0.61158,0.15719,0.26809],"object_to_goal_dist_end":0.01395,"object_to_goal_dist_start":0.12504,"object_z_max":0.26809,"peak_contact_force":73.4845,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10768.0,"raw_peak_contact_force":0.3144,"tcp_end":[0.62179,0.16956,0.17112],"tcp_start":[0.6101,0.1564,0.29589],"tcp_to_object_dist_end":0.03229,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```