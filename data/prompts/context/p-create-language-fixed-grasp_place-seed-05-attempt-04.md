## Search State

- **Seed**: 5
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | -0.0911 | 0.38 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1279 | 0.31 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | -0.0792 | 0.39 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | -0.0229 | 0.32 | ❌ rejected |
| 0 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 0 | 0.2685 | 0.32 | ✅ accepted |

**Proposal policy**: task_score is 0.38 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.091) — your mutation base

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

- **Composite score**: -0.091
- **task_score** (E): 0.376
- **fitness_score**: 0.409  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.500

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0673 |
| descend_1 | 1.00 | 1.00 | 0.1946 |
| grasp_1 | 1.00 | 1.00 | 0.0123 |
| lift_1 | 1.00 | 1.00 | 0.0066 |
| transport_approach | 0.00 | 1.00 | 0.0900 |
| place_descend | 0.67 | 1.00 | 0.0993 |
| release_1 | 1.00 | 1.00 | 0.0230 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.015, 0.241) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.510, 0.015, 0.241)→(0.511, 0.018, 0.047) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.511, 0.018, 0.047)→(0.503, 0.017, 0.038) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.237 | 1.00 / 43.000 | 0.143 | 0.198 |
| lift_1 | lift | 1.00 / step_budget | (0.503, 0.017, 0.038)→(0.499, 0.017, 0.043) | (0.516, 0.018, 0.026)→(0.512, 0.018, 0.031) | 0.237→0.235 | 1.00 / 44.333 | 0.089 | 0.359 |
| transport_approach | approach | 0.00 / step_budget | (0.499, 0.017, 0.043)→(0.524, 0.062, 0.116) | (0.512, 0.018, 0.031)→(0.535, 0.062, 0.094) | 0.235→0.163 | 1.00 / 25.333 | 0.099 | 0.287 |
| place_descend | descend | 0.67 / step_budget | (0.524, 0.062, 0.116)→(0.573, 0.137, 0.117) | (0.535, 0.062, 0.094)→(0.573, 0.131, 0.025) | 0.163→0.154 | 1.00 / 11.333 | 0.120 | 0.848 |
| release_1 | release | 1.00 / step_budget | (0.573, 0.137, 0.117)→(0.567, 0.135, 0.139) | (0.573, 0.131, 0.025)→(0.565, 0.131, 0.019) | 0.154→0.161 | 1.00 / 4.000 | 0.138 | 0.179 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.544
- phase_score: 0.360
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.531
- phase_breakdown.transport_arc_score: 0.075
- phase_breakdown.approach_1_score: 0.025
- phase_breakdown.descend_1_score: 0.881
- grasp_place_fitness: 0.487

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.487
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.544
- **Median Q (composite search score)**: -0.081
- **K-run variance**: 0.0047
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.336


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55738,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17873,"descend_1.grasp_z_offset":0.01923,"lift_1.lift_distance":0.09587,"place_descend.place_z_offset":-0.02812,"release_1.release_time":1.31258,"transport_approach.transport_height":0.23247,"transport_approach.transport_speed":0.31598},"optimized_scores":{"best_composite_score":-0.01295,"best_fitness_score":0.48705,"best_task_score":0.54435},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":200.0,"contact_point_centroid":[0.52452,0.03167,-0.00099],"force_p95":0.253,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56142,"mean_force":0.12851,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.51436,0.0313,0.04595]},{"body_a":"world","body_b":"grasp_target","contact_count":360.0,"contact_point_centroid":[0.57932,0.15935,-0.00271],"force_p95":0.28517,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29111,"mean_force":0.19071,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57951,0.15858,0.08355]},{"body_a":"world","body_b":"grasp_target","contact_count":100.0,"contact_point_centroid":[0.5303,0.03033,-0.00226],"force_p95":0.27176,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2778,"mean_force":0.19101,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51611,0.02954,0.04355]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16190.0,"contact_point_centroid":[0.52382,0.02923,0.07808],"force_p95":0.09913,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27113,"mean_force":0.06209,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.52172,0.04819,0.07643]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17171.0,"contact_point_centroid":[0.52426,0.06742,0.07877],"force_p95":0.0916,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26346,"mean_force":0.05889,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.5219,0.04852,0.07705]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11485.0,"contact_point_centroid":[0.5666,0.1003,0.09169],"force_p95":0.11402,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26158,"mean_force":0.08102,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.56085,0.11887,0.09265]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11790.0,"contact_point_centroid":[0.56703,0.138,0.09146],"force_p95":0.11302,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23322,"mean_force":0.07901,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.56122,0.11948,0.09243]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53053,0.03068,-0.0021],"force_p95":0.15001,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21102,"mean_force":0.13042,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51827,0.02968,0.04536]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":605.0,"contact_point_centroid":[0.58935,0.17831,0.06992],"force_p95":0.11941,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18495,"mean_force":0.08162,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58403,0.15996,0.07416]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":557.0,"contact_point_centroid":[0.58943,0.14159,0.07034],"force_p95":0.13117,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17615,"mean_force":0.08663,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5841,0.15999,0.07427]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":526.0,"contact_point_centroid":[0.51623,0.04877,0.04569],"force_p95":0.13485,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17574,"mean_force":0.07975,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51609,0.02954,0.04355]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":525.0,"contact_point_centroid":[0.51592,0.01042,0.04716],"force_p95":0.12683,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16365,"mean_force":0.07551,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51611,0.02954,0.04355]},{"body_a":"world","body_b":"grasp_target","contact_count":1252.0,"contact_point_centroid":[0.5305,0.03079,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51059,0.01298,0.2568]},{"body_a":"world","body_b":"grasp_target","contact_count":1948.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52314,0.02835,0.1332]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5060.0,"contact_point_centroid":[0.51746,0.01043,0.04713],"force_p95":0.06796,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10849,"mean_force":0.04274,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51708,0.0296,0.04399]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4964.0,"contact_point_centroid":[0.51772,0.0489,0.04579],"force_p95":0.07227,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07381,"mean_force":0.04488,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51708,0.0296,0.04399]}],"total_contact_groups":16},"final_pose_error":0.02381,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.56718,0.15935,0.0258],"final_tcp_position":[0.58631,0.16041,0.07764],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.56142,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":314.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1252.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52344,0.02673,0.21429],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18844,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":487.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1948.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52535,0.03015,0.05365],"tcp_start":[0.52344,0.02673,0.21429],"tcp_to_object_dist_end":0.02811,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53044,0.02998,0.02562],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18422,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14628,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11824.0,"raw_peak_contact_force":0.21102,"subtask_id":"grasp_1","tcp_end":[0.51705,0.0296,0.04395],"tcp_start":[0.52535,0.03015,0.05365],"tcp_to_object_dist_end":0.02271,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":25.0,"n_steps_budget":600.0,"object_pos_end":[0.52844,0.02986,0.0261],"object_pos_start":[0.53044,0.02998,0.02562],"object_to_goal_dist_end":0.18488,"object_to_goal_dist_start":0.18422,"object_z_max":0.02602,"peak_contact_force":0.12282,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1151.0,"raw_peak_contact_force":0.2778,"tcp_end":[0.515,0.02946,0.04381],"tcp_start":[0.51705,0.0296,0.04395],"tcp_to_object_dist_end":0.02223,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54284,0.06863,0.08929],"object_pos_start":[0.52844,0.02986,0.0261],"object_to_goal_dist_end":0.12605,"object_to_goal_dist_start":0.18488,"object_z_max":0.08925,"peak_contact_force":0.09783,"phase_name":"transport_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":33561.0,"raw_peak_contact_force":0.56142,"subtask_id":"transport_arc","tcp_end":[0.53357,0.06847,0.11631],"tcp_start":[0.515,0.02946,0.04381],"tcp_to_object_dist_end":0.02857,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59165,0.16043,0.04278],"object_pos_start":[0.54284,0.06863,0.08929],"object_to_goal_dist_end":0.0685,"object_to_goal_dist_start":0.12605,"object_z_max":0.08929,"peak_contact_force":0.11531,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":23275.0,"raw_peak_contact_force":0.26158,"tcp_end":[0.58631,0.16041,0.07764],"tcp_start":[0.53357,0.06847,0.11631],"tcp_to_object_dist_end":0.03527,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56718,0.15935,0.0258],"object_pos_start":[0.59165,0.16043,0.04278],"object_to_goal_dist_end":0.09122,"object_to_goal_dist_start":0.0685,"object_z_max":0.04278,"peak_contact_force":0.1702,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1522.0,"raw_peak_contact_force":0.29111,"subtask_id":"release_1","tcp_end":[0.57894,0.15842,0.09896],"tcp_start":[0.58631,0.16041,0.07764],"tcp_to_object_dist_end":0.0741,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56693,"average_solve_count":127.0,"average_success_count":127.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19697,"descend_1.grasp_z_offset":0.00165,"lift_1.lift_distance":0.14091,"place_descend.place_z_offset":-0.01482,"release_1.release_time":1.33546,"transport_approach.transport_height":0.05713,"transport_approach.transport_speed":0.35456},"optimized_scores":{"best_composite_score":-0.1799,"best_fitness_score":0.3201,"best_task_score":0.18149},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2618.0,"contact_point_centroid":[0.52966,0.09586,-0.00226],"force_p95":0.12793,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.22481,"mean_force":0.13603,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.53282,0.09112,0.14285]},{"body_a":"world","body_b":"grasp_target","contact_count":240.0,"contact_point_centroid":[0.49841,-0.0151,-0.00127],"force_p95":0.37349,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41514,"mean_force":0.12456,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48881,-0.01529,0.02879]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2912.0,"contact_point_centroid":[0.51913,0.0754,0.11082],"force_p95":0.15178,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24319,"mean_force":0.09713,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.51566,0.05742,0.11449]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2644.0,"contact_point_centroid":[0.51839,0.03825,0.11019],"force_p95":0.17428,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2272,"mean_force":0.09784,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.51525,0.05641,0.11377]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1580.0,"contact_point_centroid":[0.48836,0.0039,0.03205],"force_p95":0.11745,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20054,"mean_force":0.05738,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48845,-0.01528,0.02941]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1665.0,"contact_point_centroid":[0.48828,-0.03439,0.03154],"force_p95":0.11356,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19869,"mean_force":0.05547,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48847,-0.01528,0.0294]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01552,-0.00203],"force_p95":0.13357,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16261,"mean_force":0.1257,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49206,-0.01533,0.02879]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16129.0,"contact_point_centroid":[0.49983,-0.00448,0.06867],"force_p95":0.10004,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15243,"mean_force":0.06312,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.49737,0.01433,0.06748]},{"body_a":"world","body_b":"grasp_target","contact_count":820.0,"contact_point_centroid":[0.50382,-0.01567,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12322,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49945,-0.00589,0.26869]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15530.0,"contact_point_centroid":[0.49984,0.03312,0.06896],"force_p95":0.10239,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13239,"mean_force":0.06521,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.49731,0.01421,0.0673]},{"body_a":"world","body_b":"grasp_target","contact_count":2468.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49843,-0.01397,0.13478]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5296,0.09594,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.53906,0.10973,0.16246]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4110.0,"contact_point_centroid":[0.49134,0.00389,0.03033],"force_p95":0.07621,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11542,"mean_force":0.05173,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49089,-0.01532,0.02756]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4890.0,"contact_point_centroid":[0.49141,-0.0344,0.02941],"force_p95":0.06852,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08824,"mean_force":0.04477,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49089,-0.01532,0.02756]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2462.0,"contact_point_centroid":[0.53438,0.09344,0.14713],"force_p95":0.01127,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01584,"mean_force":0.01058,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.53405,0.09343,0.14486]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.54192,0.11036,0.15971],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01094,"mean_force":0.00997,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54181,0.11036,0.15745]}],"total_contact_groups":16},"final_pose_error":0.11511,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.5296,0.09594,0.01602],"final_tcp_position":[0.54315,0.11052,0.15969],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.22481,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":206.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":820.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50024,-0.01258,0.23576],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":617.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2468.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49905,-0.01541,0.03623],"tcp_start":[0.50024,-0.01258,0.23576],"tcp_to_object_dist_end":0.01127,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50368,-0.01518,0.02587],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31206,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.131,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10800.0,"raw_peak_contact_force":0.16261,"subtask_id":"grasp_1","tcp_end":[0.49086,-0.01531,0.02753],"tcp_start":[0.49905,-0.01541,0.03623],"tcp_to_object_dist_end":0.01293,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":77.0,"n_steps_budget":600.0,"object_pos_end":[0.49962,-0.01525,0.03114],"object_pos_start":[0.50368,-0.01518,0.02587],"object_to_goal_dist_end":0.30949,"object_to_goal_dist_start":0.31206,"object_z_max":0.03108,"peak_contact_force":0.07055,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3485.0,"raw_peak_contact_force":0.41514,"tcp_end":[0.48707,-0.01526,0.03243],"tcp_start":[0.49086,-0.01531,0.02753],"tcp_to_object_dist_end":0.01262,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52693,0.04455,0.09237],"object_pos_start":[0.49962,-0.01525,0.03114],"object_to_goal_dist_end":0.21972,"object_to_goal_dist_start":0.30949,"object_z_max":0.09232,"peak_contact_force":0.11405,"phase_name":"transport_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31659.0,"raw_peak_contact_force":0.15243,"subtask_id":"transport_arc","tcp_end":[0.51222,0.04439,0.10749],"tcp_start":[0.48707,-0.01526,0.03243],"tcp_to_object_dist_end":0.02109,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5296,0.09594,0.01602],"object_pos_start":[0.52693,0.04455,0.09237],"object_to_goal_dist_end":0.25598,"object_to_goal_dist_start":0.21972,"object_z_max":0.09814,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10636.0,"raw_peak_contact_force":1.22481,"tcp_end":[0.54315,0.11052,0.15969],"tcp_start":[0.51222,0.04439,0.10749],"tcp_to_object_dist_end":0.14504,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5296,0.09594,0.01602],"object_pos_start":[0.5296,0.09594,0.01602],"object_to_goal_dist_end":0.25598,"object_to_goal_dist_start":0.25598,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.53744,0.10937,0.18293],"tcp_start":[0.54315,0.11052,0.15969],"tcp_to_object_dist_end":0.16763,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47328,"average_solve_count":131.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.24413,"descend_1.grasp_z_offset":0.01601,"lift_1.lift_distance":0.19444,"place_descend.place_z_offset":-0.02689,"release_1.release_time":0.54413,"transport_approach.transport_height":0.21568,"transport_approach.transport_speed":0.1492},"optimized_scores":{"best_composite_score":-0.08059,"best_fitness_score":0.41941,"best_task_score":0.40252},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":810.0,"contact_point_centroid":[0.59839,0.13829,-0.00272],"force_p95":0.46674,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.05668,"mean_force":0.16041,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.58475,0.13393,0.11329]},{"body_a":"world","body_b":"grasp_target","contact_count":248.0,"contact_point_centroid":[0.50706,0.03733,-0.00131],"force_p95":0.30229,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38309,"mean_force":0.09987,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4975,0.03802,0.043]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8081.0,"contact_point_centroid":[0.55546,0.08046,0.11813],"force_p95":0.14654,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27522,"mean_force":0.08416,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.54936,0.09909,0.11741]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3430.0,"contact_point_centroid":[0.49603,0.05709,0.0486],"force_p95":0.0907,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2249,"mean_force":0.05182,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49627,0.03793,0.04645]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51255,0.03951,-0.00213],"force_p95":0.15853,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22075,"mean_force":0.13217,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50079,0.0383,0.04276]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9012.0,"contact_point_centroid":[0.55724,0.11918,0.1172],"force_p95":0.11856,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21547,"mean_force":0.07603,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.55099,0.10074,0.11714]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3277.0,"contact_point_centroid":[0.4962,0.01873,0.04921],"force_p95":0.08848,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2033,"mean_force":0.05234,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49626,0.03793,0.04646]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15959.0,"contact_point_centroid":[0.51131,0.03637,0.08921],"force_p95":0.09263,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14638,"mean_force":0.06131,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.50832,0.05516,0.08742]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4081.0,"contact_point_centroid":[0.50009,0.01896,0.04429],"force_p95":0.08179,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14591,"mean_force":0.05201,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49963,0.0382,0.04148]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15597.0,"contact_point_centroid":[0.51069,0.07365,0.08819],"force_p95":0.10034,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14188,"mean_force":0.06343,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.50792,0.05471,0.08644]},{"body_a":"world","body_b":"grasp_target","contact_count":740.0,"contact_point_centroid":[0.51251,0.03972,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12329,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50281,0.01528,0.28621]},{"body_a":"world","body_b":"grasp_target","contact_count":2724.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50637,0.03502,0.16098]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59918,0.13811,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58604,0.13876,0.11407]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5264.0,"contact_point_centroid":[0.4997,0.05733,0.04378],"force_p95":0.07047,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07718,"mean_force":0.04235,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49964,0.0382,0.04149]},{"body_a":"left_finger","body_b":"right_finger","contact_count":487.0,"contact_point_centroid":[0.58792,0.13648,0.11515],"force_p95":0.01457,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01646,"mean_force":0.01099,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.58734,0.13646,0.11303]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.58975,0.13966,0.11219],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01103,"mean_force":0.0101,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58929,0.13964,0.10995]}],"total_contact_groups":16},"final_pose_error":0.04944,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.59918,0.13811,0.01602],"final_tcp_position":[0.59085,0.13987,0.11266],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.05668,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":186.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":740.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50717,0.03134,0.27387],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.24805,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":681.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2724.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50772,0.03885,0.05052],"tcp_start":[0.50717,0.03134,0.27387],"tcp_to_object_dist_end":0.02498,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51246,0.03843,0.02556],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21331,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15317,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11145.0,"raw_peak_contact_force":0.22075,"subtask_id":"grasp_1","tcp_end":[0.4996,0.0382,0.04145],"tcp_start":[0.50772,0.03885,0.05052],"tcp_to_object_dist_end":0.02044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":158.0,"n_steps_budget":600.0,"object_pos_end":[0.50767,0.03814,0.03567],"object_pos_start":[0.51246,0.03843,0.02556],"object_to_goal_dist_end":0.2107,"object_to_goal_dist_start":0.21331,"object_z_max":0.03562,"peak_contact_force":0.07461,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6955.0,"raw_peak_contact_force":0.38309,"tcp_end":[0.4951,0.03783,0.05198],"tcp_start":[0.4996,0.0382,0.04145],"tcp_to_object_dist_end":0.02059,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5352,0.07203,0.10024],"object_pos_start":[0.50767,0.03814,0.03567],"object_to_goal_dist_end":0.14365,"object_to_goal_dist_start":0.2107,"object_z_max":0.10016,"peak_contact_force":0.08497,"phase_name":"transport_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31556.0,"raw_peak_contact_force":0.14638,"subtask_id":"transport_arc","tcp_end":[0.52499,0.07204,0.12565],"tcp_start":[0.4951,0.03783,0.05198],"tcp_to_object_dist_end":0.02738,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59918,0.1381,0.01602],"object_pos_start":[0.5352,0.07203,0.10024],"object_to_goal_dist_end":0.1365,"object_to_goal_dist_start":0.14365,"object_z_max":0.10026,"peak_contact_force":0.12262,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":18390.0,"raw_peak_contact_force":1.05668,"tcp_end":[0.59085,0.13987,0.11266],"tcp_start":[0.52499,0.07204,0.12565],"tcp_to_object_dist_end":0.09701,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59918,0.13811,0.01602],"object_pos_start":[0.59918,0.1381,0.01602],"object_to_goal_dist_end":0.1365,"object_to_goal_dist_start":0.1365,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.5841,0.13823,0.13397],"tcp_start":[0.59085,0.13987,0.11266],"tcp_to_object_dist_end":0.11891,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```