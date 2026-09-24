## Search State

- **Seed**: 5
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | -0.0792 | 0.39 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | -0.0229 | 0.32 | ❌ rejected |
| 0 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 0 | 0.2685 | 0.32 | ✅ accepted |

**Proposal policy**: task_score is 0.39 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.079) — your mutation base

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
        mode: add
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
    orientation:
      mode: keep_current
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.04
      default: 0.01
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
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.02
    orientation:
      mode: keep_current
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
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
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    lift_distance:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset_along_axis.distance
        mode: scale
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
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.2
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_z_offset:
      type: scalar
      range:
      - -0.15
      - 0.05
      default: -0.05
      binds_to:
      - path: target.offset.z
        mode: add
  subtask_id: transport_arc
- id: place_descend
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
    orientation:
      mode: keep_current
  parameters:
    place_z_offset:
      type: scalar
      range:
      - -0.15
      - 0.05
      default: -0.03
      binds_to:
      - path: target.offset.z
        mode: add
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    release_time:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (add)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02]
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_distance: status=consumed; consumers=target.offset_along_axis.distance (scale)
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_z_offset: status=consumed; consumers=target.offset.z (add)
- **place_descend** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (add)
- **release_1** (`release`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - release_time: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: -0.079
- **task_score** (E): 0.391
- **fitness_score**: 0.421  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.500

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0959 |
| descend_1 | 1.00 | 1.00 | 0.1732 |
| grasp_1 | 1.00 | 1.00 | 0.0124 |
| lift_1 | 1.00 | 1.00 | 0.0066 |
| transport_arc | 0.00 | 1.00 | 0.0983 |
| place_descend | 0.67 | 1.00 | 0.0852 |
| release_1 | 1.00 | 1.00 | 0.0228 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.211) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 11.096 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.510, 0.016, 0.211)→(0.511, 0.018, 0.038) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.511, 0.018, 0.038)→(0.502, 0.018, 0.029) | (0.516, 0.018, 0.026)→(0.515, 0.018, 0.026) | 0.236→0.237 | 1.00 / 41.333 | 0.141 | 0.216 |
| lift_1 | lift | 1.00 / step_budget | (0.502, 0.018, 0.029)→(0.498, 0.017, 0.034) | (0.515, 0.018, 0.026)→(0.511, 0.017, 0.031) | 0.237→0.235 | 1.00 / 41.333 | 0.078 | 0.421 |
| transport_arc | approach | 0.00 / step_budget | (0.498, 0.017, 0.034)→(0.545, 0.093, 0.059) | (0.511, 0.017, 0.031)→(0.557, 0.091, 0.043) | 0.235→0.160 | 1.00 / 24.333 | 0.376 | 0.597 |
| place_descend | descend | 0.67 / step_budget | (0.545, 0.093, 0.059)→(0.589, 0.160, 0.061) | (0.557, 0.091, 0.043)→(0.594, 0.153, 0.010) | 0.160→0.161 | 1.00 / 11.000 | 0.544 | 1.162 |
| release_1 | release | 1.00 / step_budget | (0.589, 0.160, 0.061)→(0.582, 0.158, 0.083) | (0.594, 0.153, 0.010)→(0.594, 0.161, 0.017) | 0.161→0.153 | 1.00 / 3.333 | 0.149 | 0.812 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.541
- phase_score: 0.374
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.495
- phase_breakdown.transport_arc_score: 0.120
- phase_breakdown.approach_1_score: 0.011
- phase_breakdown.descend_1_score: 0.835
- grasp_place_fitness: 0.496

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.496
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.541
- **Median Q (composite search score)**: -0.058
- **K-run variance**: 0.0051
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.276


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50388,"average_solve_count":129.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.22526,"descend_1.grasp_z_offset":0.00822,"lift_1.lift_distance":0.14816,"place_descend.place_z_offset":-0.04293,"release_1.release_time":0.61922,"transport_arc.arc_height":0.33179,"transport_arc.transport_z_offset":-0.11367},"optimized_scores":{"best_composite_score":-0.0039,"best_fitness_score":0.4961,"best_task_score":0.54087},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1662.0,"contact_point_centroid":[0.57539,0.13562,-0.00563],"force_p95":0.82305,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.94476,"mean_force":0.40626,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57596,0.14651,0.03908]},{"body_a":"world","body_b":"grasp_target","contact_count":2574.0,"contact_point_centroid":[0.54898,0.0738,-0.00324],"force_p95":0.7242,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.88651,"mean_force":0.34547,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53768,0.07874,0.03656]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8094.0,"contact_point_centroid":[0.57908,0.16444,0.03801],"force_p95":0.1811,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40916,"mean_force":0.08954,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57537,0.14569,0.03854]},{"body_a":"world","body_b":"grasp_target","contact_count":290.0,"contact_point_centroid":[0.5244,0.02885,-0.00131],"force_p95":0.33124,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38351,"mean_force":0.11099,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51449,0.02942,0.03438]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18402.0,"contact_point_centroid":[0.5381,0.05878,0.03855],"force_p95":0.15332,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3659,"mean_force":0.07839,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53734,0.07813,0.03683]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12873.0,"contact_point_centroid":[0.5742,0.12455,0.03739],"force_p95":0.16773,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3468,"mean_force":0.08142,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57434,0.14413,0.03764]},{"body_a":"world","body_b":"grasp_target","contact_count":731.0,"contact_point_centroid":[0.59974,0.18099,-0.00223],"force_p95":0.23162,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33212,"mean_force":0.13665,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58893,0.17305,0.05712]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13916.0,"contact_point_centroid":[0.53678,0.092,0.0399],"force_p95":0.13262,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2374,"mean_force":0.06611,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53433,0.0729,0.03723]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53054,0.03055,-0.00211],"force_p95":0.15404,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.223,"mean_force":0.13103,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51813,0.02966,0.03433]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2310.0,"contact_point_centroid":[0.51387,0.04852,0.03777],"force_p95":0.11169,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20897,"mean_force":0.05332,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51396,0.02938,0.03535]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2106.0,"contact_point_centroid":[0.51416,0.0102,0.03826],"force_p95":0.11147,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19949,"mean_force":0.05555,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51397,0.02938,0.03529]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4078.0,"contact_point_centroid":[0.51764,0.01038,0.03574],"force_p95":0.07984,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14433,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51692,0.02958,0.03297]},{"body_a":"world","body_b":"grasp_target","contact_count":904.0,"contact_point_centroid":[0.5305,0.03079,-0.00186],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12317,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51027,0.01245,0.27767]},{"body_a":"world","body_b":"grasp_target","contact_count":2588.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52271,0.0277,0.14865]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4976.0,"contact_point_centroid":[0.5176,0.04872,0.03478],"force_p95":0.07241,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08413,"mean_force":0.04466,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51693,0.02958,0.03297]},{"body_a":"left_finger","body_b":"right_finger","contact_count":209.0,"contact_point_centroid":[0.59327,0.17437,0.05494],"force_p95":0.01401,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01507,"mean_force":0.01116,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59298,0.17434,0.05282]}],"total_contact_groups":16},"final_pose_error":0.01224,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59976,0.18283,0.01602],"final_tcp_position":[0.59482,0.1748,0.05565],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.94476,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":227.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":904.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52239,0.02541,0.25693],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23111,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":647.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2588.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52534,0.03014,0.0426],"tcp_start":[0.52239,0.02541,0.25693],"tcp_to_object_dist_end":0.01738,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53041,0.02964,0.02563],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.1845,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14765,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10854.0,"raw_peak_contact_force":0.223,"subtask_id":"grasp_1","tcp_end":[0.51689,0.02958,0.03293],"tcp_start":[0.52534,0.03014,0.0426],"tcp_to_object_dist_end":0.01536,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":106.0,"n_steps_budget":600.0,"object_pos_end":[0.52615,0.02934,0.03169],"object_pos_start":[0.53041,0.02964,0.02563],"object_to_goal_dist_end":0.18382,"object_to_goal_dist_start":0.1845,"object_z_max":0.03165,"peak_contact_force":0.08372,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4706.0,"raw_peak_contact_force":0.38351,"tcp_end":[0.51254,0.02929,0.03876],"tcp_start":[0.51689,0.02958,0.03293],"tcp_to_object_dist_end":0.01534,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56799,0.11363,0.01558],"object_pos_start":[0.52615,0.02934,0.03169],"object_to_goal_dist_end":0.1179,"object_to_goal_dist_start":0.18382,"object_z_max":0.03169,"peak_contact_force":0.85964,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34892.0,"raw_peak_contact_force":0.88651,"subtask_id":"transport_arc","tcp_end":[0.56221,0.12001,0.02881],"tcp_start":[0.51254,0.02929,0.03876],"tcp_to_object_dist_end":0.01578,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60056,0.17102,0.0198],"object_pos_start":[0.56799,0.11363,0.01558],"object_to_goal_dist_end":0.08862,"object_to_goal_dist_start":0.1179,"object_z_max":0.03133,"peak_contact_force":0.2611,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":22629.0,"raw_peak_contact_force":0.94476,"tcp_end":[0.59482,0.1748,0.05565],"tcp_start":[0.56221,0.12001,0.02881],"tcp_to_object_dist_end":0.0365,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59976,0.18283,0.01602],"object_pos_start":[0.60056,0.17102,0.0198],"object_to_goal_dist_end":0.09219,"object_to_goal_dist_start":0.08862,"object_z_max":0.0198,"peak_contact_force":0.12273,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":940.0,"raw_peak_contact_force":0.33212,"subtask_id":"release_1","tcp_end":[0.5871,0.17247,0.0766],"tcp_start":[0.59482,0.1748,0.05565],"tcp_to_object_dist_end":0.06275,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55738,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14801,"descend_1.grasp_z_offset":0.00993,"lift_1.lift_distance":0.15023,"place_descend.place_z_offset":-0.11386,"release_1.release_time":1.59187,"transport_arc.arc_height":0.29038,"transport_arc.transport_z_offset":-0.14957},"optimized_scores":{"best_composite_score":-0.17561,"best_fitness_score":0.32439,"best_task_score":0.20008},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1684.0,"contact_point_centroid":[0.56108,0.12639,-0.00235],"force_p95":0.22992,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.01261,"mean_force":0.14036,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.55261,0.12965,0.11396]},{"body_a":"world","body_b":"grasp_target","contact_count":239.0,"contact_point_centroid":[0.49848,-0.01523,-0.00126],"force_p95":0.31969,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36092,"mean_force":0.10958,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48888,-0.01531,0.03715]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4312.0,"contact_point_centroid":[0.53457,0.0664,0.10357],"force_p95":0.15772,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29438,"mean_force":0.10735,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.52925,0.08471,0.10466]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4948.0,"contact_point_centroid":[0.53538,0.10387,0.10334],"force_p95":0.13495,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22174,"mean_force":0.09416,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.5298,0.0858,0.10486]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1846.0,"contact_point_centroid":[0.48823,0.00388,0.04087],"force_p95":0.11386,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2048,"mean_force":0.05653,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48831,-0.0153,0.03827]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1942.0,"contact_point_centroid":[0.48814,-0.03442,0.04037],"force_p95":0.11103,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1996,"mean_force":0.05465,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48832,-0.0153,0.03825]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15948.0,"contact_point_centroid":[0.50071,-0.00241,0.07513],"force_p95":0.10164,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17326,"mean_force":0.06229,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.4984,0.01649,0.07351]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01555,-0.00203],"force_p95":0.13317,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16088,"mean_force":0.1256,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4921,-0.01535,0.03712]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15460.0,"contact_point_centroid":[0.50195,0.03694,0.0766],"force_p95":0.09562,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14771,"mean_force":0.06399,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49917,0.01806,0.0749]},{"body_a":"world","body_b":"grasp_target","contact_count":1380.0,"contact_point_centroid":[0.50382,-0.01567,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12298,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49912,-0.00662,0.24398]},{"body_a":"world","body_b":"grasp_target","contact_count":1776.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49821,-0.01456,0.11513]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56137,0.12637,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55599,0.14365,0.1195]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4112.0,"contact_point_centroid":[0.49137,0.00387,0.03866],"force_p95":0.07628,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12226,"mean_force":0.05179,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49094,-0.01534,0.03589]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4884.0,"contact_point_centroid":[0.49144,-0.03441,0.03775],"force_p95":0.06859,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09047,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49094,-0.01534,0.0359]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1417.0,"contact_point_centroid":[0.55483,0.13295,0.1169],"force_p95":0.01208,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01624,"mean_force":0.01061,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.55436,0.13294,0.11469]},{"body_a":"left_finger","body_b":"right_finger","contact_count":214.0,"contact_point_centroid":[0.55968,0.14454,0.11716],"force_p95":0.0111,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01285,"mean_force":0.01034,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5591,0.14453,0.11488]}],"total_contact_groups":16},"final_pose_error":0.05289,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.56137,0.12637,0.01602],"final_tcp_position":[0.56063,0.14479,0.1173],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":33.04386,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":346.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":33.04386,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1380.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49999,-0.01375,0.18702],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16105,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":444.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1776.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49901,-0.01543,0.04458],"tcp_start":[0.49999,-0.01375,0.18702],"tcp_to_object_dist_end":0.01918,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50371,-0.01523,0.02587],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31208,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13099,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10796.0,"raw_peak_contact_force":0.16088,"subtask_id":"grasp_1","tcp_end":[0.49091,-0.01534,0.03586],"tcp_start":[0.49901,-0.01543,0.04458],"tcp_to_object_dist_end":0.01624,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":90.0,"n_steps_budget":600.0,"object_pos_end":[0.49971,-0.01528,0.032],"object_pos_start":[0.50371,-0.01523,0.02587],"object_to_goal_dist_end":0.30889,"object_to_goal_dist_start":0.31208,"object_z_max":0.03194,"peak_contact_force":0.07108,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4027.0,"raw_peak_contact_force":0.36092,"tcp_end":[0.48694,-0.01528,0.04172],"tcp_start":[0.49091,-0.01534,0.03586],"tcp_to_object_dist_end":0.01606,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53118,0.0596,0.08343],"object_pos_start":[0.49971,-0.01528,0.032],"object_to_goal_dist_end":0.21581,"object_to_goal_dist_start":0.30889,"object_z_max":0.08341,"peak_contact_force":0.1093,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31408.0,"raw_peak_contact_force":0.17326,"subtask_id":"transport_arc","tcp_end":[0.51973,0.05983,0.10411],"tcp_start":[0.48694,-0.01528,0.04172],"tcp_to_object_dist_end":0.02364,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56137,0.12637,0.01602],"object_pos_start":[0.53118,0.0596,0.08343],"object_to_goal_dist_end":0.24135,"object_to_goal_dist_start":0.21581,"object_z_max":0.08343,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12361.0,"raw_peak_contact_force":1.01261,"tcp_end":[0.56063,0.14479,0.1173],"tcp_start":[0.51973,0.05983,0.10411],"tcp_to_object_dist_end":0.10295,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56137,0.12637,0.01602],"object_pos_start":[0.56137,0.12637,0.01602],"object_to_goal_dist_end":0.24135,"object_to_goal_dist_start":0.24135,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1014.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.55414,0.14313,0.13974],"tcp_start":[0.56063,0.14479,0.1173],"tcp_to_object_dist_end":0.12506,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56452,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15164,"descend_1.grasp_z_offset":-0.00812,"lift_1.lift_distance":0.13378,"place_descend.place_z_offset":-0.13008,"release_1.release_time":1.4525,"transport_arc.arc_height":0.35189,"transport_arc.transport_z_offset":-0.11239},"optimized_scores":{"best_composite_score":-0.05817,"best_fitness_score":0.44183,"best_task_score":0.43279},"replay_outcomes":[{"contacts":{"omitted_contact_groups":6,"reported_contact_groups":[{"body_a":"world","body_b":"left_finger","contact_count":385.0,"contact_point_centroid":[0.61246,0.1476,-0.0005],"force_p95":1.87955,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1.98144,"mean_force":1.05328,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60754,0.15978,0.0061]},{"body_a":"world","body_b":"right_finger","contact_count":444.0,"contact_point_centroid":[0.6121,0.1719,-0.00058],"force_p95":1.73291,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1.85092,"mean_force":0.97278,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60754,0.15978,0.0062]},{"body_a":"world","body_b":"grasp_target","contact_count":2424.0,"contact_point_centroid":[0.59307,0.13305,-0.01104],"force_p95":1.15837,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.52758,"mean_force":0.75595,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.58187,0.13223,0.0243]},{"body_a":"world","body_b":"grasp_target","contact_count":641.0,"contact_point_centroid":[0.6215,0.15523,-0.01096],"force_p95":1.37219,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.4722,"mean_force":0.63687,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6069,0.15959,0.01128]},{"body_a":"world","body_b":"grasp_target","contact_count":523.0,"contact_point_centroid":[0.54207,0.07851,-0.00025],"force_p95":0.2078,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72991,"mean_force":0.11022,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53285,0.07968,0.03847]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1331.0,"contact_point_centroid":[0.61003,0.14891,0.00612],"force_p95":0.27155,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.518,"mean_force":0.14214,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60829,0.16,0.00748]},{"body_a":"world","body_b":"grasp_target","contact_count":264.0,"contact_point_centroid":[0.5089,0.03808,-0.00143],"force_p95":0.45191,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51799,"mean_force":0.15323,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49689,0.03807,0.01866]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11275.0,"contact_point_centroid":[0.58361,0.1231,0.0213],"force_p95":0.18388,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.48554,"mean_force":0.10511,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.58298,0.1333,0.0238]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1085.0,"contact_point_centroid":[0.60802,0.17364,0.00501],"force_p95":0.26918,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41676,"mean_force":0.14432,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60749,0.15977,0.00939]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6956.0,"contact_point_centroid":[0.5883,0.14831,0.0163],"force_p95":0.17155,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36897,"mean_force":0.08606,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.58781,0.13792,0.02173]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13866.0,"contact_point_centroid":[0.52229,0.04817,0.03577],"force_p95":0.12433,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36724,"mean_force":0.07633,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.51982,0.06703,0.03475]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15014.0,"contact_point_centroid":[0.52219,0.08511,0.03525],"force_p95":0.11437,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28964,"mean_force":0.06958,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.51924,0.06642,0.03447]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51252,0.03913,-0.00213],"force_p95":0.15446,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26472,"mean_force":0.13481,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50032,0.03837,0.0187]},{"body_a":"grasp_target","body_b":"hand","contact_count":71.0,"contact_point_centroid":[0.51449,0.05802,0.05697],"force_p95":0.19076,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19721,"mean_force":0.07899,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49679,0.03807,0.01884]},{"body_a":"grasp_target","body_b":"hand","contact_count":320.0,"contact_point_centroid":[0.51669,0.05845,0.05547],"force_p95":0.09413,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19487,"mean_force":0.02724,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49921,0.03828,0.01754]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1544.0,"contact_point_centroid":[0.49659,0.05716,0.02113],"force_p95":0.10854,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18492,"mean_force":0.05449,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49677,0.03806,0.01885]}],"total_contact_groups":22},"final_pose_error":0.02015,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62044,0.17335,0.0196],"final_tcp_position":[0.61163,0.16078,0.01118],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.98144,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":370.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1476.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50774,0.03508,0.18908],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16319,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":505.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2020.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50749,0.03896,0.0264],"tcp_start":[0.50774,0.03508,0.18908],"tcp_to_object_dist_end":0.00509,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51229,0.03821,0.02554],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21355,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14518,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11114.0,"raw_peak_contact_force":0.26472,"subtask_id":"grasp_1","tcp_end":[0.49909,0.03826,0.0174],"tcp_start":[0.50749,0.03896,0.0264],"tcp_to_object_dist_end":0.01551,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":71.0,"n_steps_budget":600.0,"object_pos_end":[0.50808,0.03803,0.02997],"object_pos_start":[0.51229,0.03821,0.02554],"object_to_goal_dist_end":0.21355,"object_to_goal_dist_start":0.21355,"object_z_max":0.0299,"peak_contact_force":0.07822,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3298.0,"raw_peak_contact_force":0.51799,"tcp_end":[0.49533,0.03795,0.02152],"tcp_start":[0.49909,0.03826,0.0174],"tcp_to_object_dist_end":0.01529,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57176,0.09953,0.02927],"object_pos_start":[0.50808,0.03803,0.02997],"object_to_goal_dist_end":0.14779,"object_to_goal_dist_start":0.21355,"object_z_max":0.03754,"peak_contact_force":0.15975,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29478.0,"raw_peak_contact_force":0.72991,"subtask_id":"transport_arc","tcp_end":[0.55242,0.10031,0.04538],"tcp_start":[0.49533,0.03795,0.02152],"tcp_to_object_dist_end":0.02518,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61973,0.16044,-0.00678],"object_pos_start":[0.57176,0.09953,0.02927],"object_to_goal_dist_end":0.15249,"object_to_goal_dist_start":0.14779,"object_z_max":0.02927,"peak_contact_force":1.24958,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":20655.0,"raw_peak_contact_force":1.52758,"tcp_end":[0.61163,0.16078,0.01118],"tcp_start":[0.55242,0.10031,0.04538],"tcp_to_object_dist_end":0.01971,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62044,0.17335,0.0196],"object_pos_start":[0.61973,0.16044,-0.00678],"object_to_goal_dist_end":0.12563,"object_to_goal_dist_start":0.15249,"object_z_max":0.01992,"peak_contact_force":0.20021,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":3886.0,"raw_peak_contact_force":1.98144,"subtask_id":"release_1","tcp_end":[0.60352,0.15864,0.03222],"tcp_start":[0.61163,0.16078,0.01118],"tcp_to_object_dist_end":0.02572,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```