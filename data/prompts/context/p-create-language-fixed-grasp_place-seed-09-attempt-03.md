## Search State

- **Seed**: 9
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → contact → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | 0.2256 | 0.18 | ❌ rejected |
| 2 | approach → descend → contact → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.2773 | 0.28 | ✅ accepted |
| 1 | approach → descend → contact → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.2489 | 0.23 | ✅ accepted |
| 0 | approach → descend → contact → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.2442 | 0.22 | ✅ accepted |

**Proposal policy**: task_score is 0.18 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`
- Frozen object start: [0.5370249203970084, -0.021318279091244466, 0.03]
- Frozen task target: [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]
- Goal object position: (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5370249203970084, -0.021318279091244466, 0.03)
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
  frozen_object_start: [0.537, -0.0213, 0.03]
  frozen_task_target: [0.6103, 0.2278, 0.2074]
  frozen_object_starts: {'grasp_target': [0.5370249203970084, -0.021318279091244466, 0.03]}
  frozen_targets: {'place_target': [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8

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

## Current Skill (Q=0.226) — your mutation base

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
    - 0.08
    tolerance: 0.005
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
    tolerance: 0.005
    orientation:
      mode: keep_current
  subtask_id: descend_1
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - -0.015
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: grasp_1
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
    orientation:
      mode: keep_current
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.12
      binds_to:
      - path: target.offset_along_axis.distance
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: place_descend
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
    tolerance: 0.005
    orientation:
      mode: keep_current
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
    orientation:
      mode: keep_current
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.08], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **contact_1** (`contact`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, -0.015]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **place_descend** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.226
- **task_score** (E): 0.180
- **fitness_score**: 0.481  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.67 | 1.00 | 0.1633 |
| descend_1 | 1.00 | 1.00 | 0.0981 |
| contact_1 | 1.00 | 1.00 | 0.0068 |
| grasp_1 | 1.00 | 1.00 | 0.0120 |
| lift_1 | 1.00 | 1.00 | 0.1187 |
| transport_1 | 1.00 | 1.00 | 0.2339 |
| place_descend | 1.00 | 1.00 | 0.1027 |
| release_1 | 1.00 | 1.00 | 0.0207 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.67 / step_budget | (0.500, -0.000, 0.301)→(0.504, -0.012, 0.141) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.504, -0.012, 0.141)→(0.508, -0.016, 0.043) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| contact_1 | contact | 1.00 / force_exceeded | (0.508, -0.016, 0.043)→(0.507, -0.016, 0.037) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 113.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.507, -0.016, 0.037)→(0.499, -0.016, 0.028) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 36.333 | 0.145 | 0.212 |
| lift_1 | lift | 1.00 / step_budget | (0.499, -0.016, 0.028)→(0.495, -0.016, 0.147) | (0.515, -0.016, 0.026)→(0.511, -0.014, 0.098) | 0.270→0.246 | 1.00 / 15.667 | 0.125 | 0.654 |
| transport_1 | approach | 1.00 / step_budget | (0.495, -0.016, 0.147)→(0.595, 0.148, 0.273) | (0.511, -0.014, 0.098)→(0.511, 0.001, 0.019) | 0.246→0.262 | 1.00 / 8.667 | 90999.574 | 1.153 |
| place_descend | descend | 1.00 / step_budget | (0.595, 0.148, 0.273)→(0.611, 0.176, 0.176) | (0.511, 0.001, 0.019)→(0.511, 0.001, 0.019) | 0.262→0.262 | 1.00 / 8.000 | 0.123 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.611, 0.176, 0.176)→(0.605, 0.174, 0.196) | (0.511, 0.001, 0.019)→(0.511, 0.001, 0.019) | 0.262→0.262 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.239
- phase_score: 0.373
- phase_breakdown.approach_1_score: 0.185
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.114
- phase_breakdown.descend_1_score: 0.700
- phase_breakdown.release_1_score: 0.540
- grasp_place_fitness: 0.600

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.600
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.239
- **Median Q (composite search score)**: 0.282
- **K-run variance**: 0.0162
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.422


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `425c48e82220fc6e1b680086671cf7dd2586733ee271dec2149f96a25d69d0c6`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `58e88c03db0a62276863b22a53636bc89fead3e4bc7f4d35fd72d2282ace32bf`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.125,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":18.32585,"lift_1.lift_height":0.14808,"transport_1.arc_height":0.05068,"transport_1.transport_speed":0.82113},"optimized_scores":{"best_composite_score":0.2822,"best_fitness_score":0.5372,"best_task_score":0.12329},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3273.0,"contact_point_centroid":[0.52668,-0.00668,-0.00228],"force_p95":0.12691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.69123,"mean_force":0.13674,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55488,0.08483,0.26591]},{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.53373,-0.01986,-0.00115],"force_p95":0.45719,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67108,"mean_force":0.0891,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52043,-0.02044,0.03166]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10249.0,"contact_point_centroid":[0.52203,-0.00168,0.09035],"force_p95":0.12612,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33448,"mean_force":0.08189,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51785,-0.02038,0.08882]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10950.0,"contact_point_centroid":[0.522,-0.03901,0.08854],"force_p95":0.12205,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3133,"mean_force":0.07765,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51787,-0.02038,0.08742]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":666.0,"contact_point_centroid":[0.52271,0.00167,0.16632],"force_p95":0.19297,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22046,"mean_force":0.1272,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51779,-0.01636,0.171]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53705,-0.02111,-0.00208],"force_p95":0.14626,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21641,"mean_force":0.12897,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52332,-0.0205,0.03133]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":850.0,"contact_point_centroid":[0.52236,-0.03297,0.16784],"force_p95":0.16183,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20857,"mean_force":0.10754,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51795,-0.0153,0.17266]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.53702,-0.02132,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51307,-0.00943,0.21064]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4087.0,"contact_point_centroid":[0.52326,-0.00127,0.03261],"force_p95":0.0785,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13322,"mean_force":0.05185,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52208,-0.02048,0.02992]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52657,-0.0189,0.08242]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53051,-0.02063,0.03957]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.52665,-0.00667,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.59874,0.20532,0.24642]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52665,-0.00667,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60151,0.22017,0.20934]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4940.0,"contact_point_centroid":[0.5232,-0.03958,0.0317],"force_p95":0.07062,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08549,"mean_force":0.0447,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52208,-0.02048,0.02993]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3231.0,"contact_point_centroid":[0.55739,0.09061,0.27262],"force_p95":0.01113,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01656,"mean_force":0.01059,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55708,0.09061,0.27031]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4285.0,"contact_point_centroid":[0.59926,0.20533,0.24863],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01279,"mean_force":0.01041,"phase_index":6.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.59874,0.20531,0.24644]}],"total_contact_groups":17},"final_pose_error":0.00828,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.52665,-0.00667,0.01602],"final_tcp_position":[0.60507,0.2216,0.20921],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":122.18679,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.5248,-0.01661,0.1456],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1203,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53051,-0.02063,0.03957],"tcp_start":[0.5248,-0.01661,0.1456],"tcp_to_object_dist_end":0.01505,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":122.18679,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_1","tcp_end":[0.53041,-0.02063,0.03947],"tcp_start":[0.53051,-0.02063,0.03957],"tcp_to_object_dist_end":0.015,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53691,-0.02044,0.02573],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31622,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14139,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10827.0,"raw_peak_contact_force":0.21641,"tcp_end":[0.52205,-0.02047,0.02989],"tcp_start":[0.53041,-0.02063,0.03947],"tcp_to_object_dist_end":0.01543,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.52982,-0.02041,0.14472],"object_pos_start":[0.53691,-0.02044,0.02573],"object_to_goal_dist_end":0.26832,"object_to_goal_dist_start":0.31622,"object_z_max":0.14463,"peak_contact_force":0.13883,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21341.0,"raw_peak_contact_force":0.67108,"tcp_end":[0.51819,-0.02038,0.16543],"tcp_start":[0.52205,-0.02047,0.02989],"tcp_to_object_dist_end":0.02374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52665,-0.00667,0.01602],"object_pos_start":[0.52982,-0.02041,0.14472],"object_to_goal_dist_end":0.31398,"object_to_goal_dist_start":0.26832,"object_z_max":0.15514,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8020.0,"raw_peak_contact_force":1.69123,"subtask_id":"transport_arc","tcp_end":[0.59265,0.18496,0.30177],"tcp_start":[0.51819,-0.02038,0.16543],"tcp_to_object_dist_end":0.35033,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52665,-0.00667,0.01602],"object_pos_start":[0.52665,-0.00667,0.01602],"object_to_goal_dist_end":0.31398,"object_to_goal_dist_start":0.31398,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8285.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60507,0.2216,0.20921],"tcp_start":[0.59265,0.18496,0.30177],"tcp_to_object_dist_end":0.30916,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52665,-0.00667,0.01602],"object_pos_start":[0.52665,-0.00667,0.01602],"object_to_goal_dist_end":0.31398,"object_to_goal_dist_start":0.31398,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.60022,0.21957,0.2287],"tcp_start":[0.60507,0.2216,0.20921],"tcp_to_object_dist_end":0.31911,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1e57d18e69439f9d4839513252d085a45363faa5c1c2b52093c9c8149b88bb68`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.00752,"average_solve_count":133.0,"average_success_count":133.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":12.26259,"lift_1.lift_height":0.12153,"transport_1.arc_height":0.18104,"transport_1.transport_speed":0.72292},"optimized_scores":{"best_composite_score":0.04941,"best_fitness_score":0.30441,"best_task_score":0.1785},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2082.0,"contact_point_centroid":[0.53966,-0.02254,-0.00211],"force_p95":0.29186,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60854,"mean_force":0.13551,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51891,-0.02629,0.09315]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1308.0,"contact_point_centroid":[0.526,-0.00822,0.04213],"force_p95":0.17795,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.45501,"mean_force":0.11106,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5197,-0.02633,0.03901]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1870.0,"contact_point_centroid":[0.5256,-0.04431,0.03978],"force_p95":0.14638,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37661,"mean_force":0.09097,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51963,-0.02632,0.03866]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5458,-0.0286,-0.0022],"force_p95":0.19754,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28003,"mean_force":0.13899,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52448,-0.02647,0.02976]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2081.0,"contact_point_centroid":[0.52905,-0.00754,0.03277],"force_p95":0.12777,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15752,"mean_force":0.09152,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52324,-0.02644,0.02835]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.5456,-0.02923,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51493,-0.01166,0.21886]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53085,-0.02382,0.10127]},{"body_a":"world","body_b":"grasp_target","contact_count":404.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53345,-0.02672,0.04796]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53771,-0.02212,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54565,0.02245,0.24506]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53771,-0.02212,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61699,0.1442,0.23048]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53771,-0.02212,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62066,0.15574,0.18994]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3259.0,"contact_point_centroid":[0.52867,-0.04517,0.02941],"force_p95":0.10006,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1032,"mean_force":0.06716,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52325,-0.02644,0.02836]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1720.0,"contact_point_centroid":[0.51912,-0.02629,0.10739],"force_p95":0.01193,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0163,"mean_force":0.01053,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51877,-0.02629,0.10503]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4298.0,"contact_point_centroid":[0.61746,0.14423,0.2327],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01286,"mean_force":0.01038,"phase_index":6.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61701,0.14422,0.23038]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4268.0,"contact_point_centroid":[0.54599,0.02235,0.24742],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.01045,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54558,0.02235,0.24515]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.62387,0.15654,0.1889],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01259,"mean_force":0.01008,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62323,0.15653,0.18657]}],"total_contact_groups":16},"final_pose_error":0.01728,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.53771,-0.02212,0.02602],"final_tcp_position":[0.6246,0.15686,0.18979],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":17.76009,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52722,-0.01997,0.16384],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13934,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53612,-0.0268,0.05783],"tcp_start":[0.52722,-0.01997,0.16384],"tcp_to_object_dist_end":0.03328,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":101.0,"n_steps_budget":600.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":17.76009,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":404.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_1","tcp_end":[0.53173,-0.02667,0.03806],"tcp_start":[0.53612,-0.0268,0.05783],"tcp_to_object_dist_end":0.01855,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54554,-0.02657,0.02547],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.25929,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.16714,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7140.0,"raw_peak_contact_force":0.28003,"tcp_end":[0.52321,-0.02643,0.02831],"tcp_start":[0.53173,-0.02667,0.03806],"tcp_to_object_dist_end":0.02251,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.53771,-0.02212,0.02602],"object_pos_start":[0.54554,-0.02657,0.02547],"object_to_goal_dist_end":0.25847,"object_to_goal_dist_start":0.25929,"object_z_max":0.04014,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6980.0,"raw_peak_contact_force":0.60854,"tcp_end":[0.51913,-0.0263,0.13747],"tcp_start":[0.52321,-0.02643,0.02831],"tcp_to_object_dist_end":0.11307,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53771,-0.02212,0.02602],"object_pos_start":[0.53771,-0.02212,0.02602],"object_to_goal_dist_end":0.25847,"object_to_goal_dist_start":0.25847,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8268.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_arc","tcp_end":[0.60899,0.12782,0.29193],"tcp_start":[0.51913,-0.0263,0.13747],"tcp_to_object_dist_end":0.31348,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53771,-0.02212,0.02602],"object_pos_start":[0.53771,-0.02212,0.02602],"object_to_goal_dist_end":0.25847,"object_to_goal_dist_start":0.25847,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8298.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6246,0.15686,0.18979],"tcp_start":[0.60899,0.12782,0.29193],"tcp_to_object_dist_end":0.25769,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53771,-0.02212,0.02602],"object_pos_start":[0.53771,-0.02212,0.02602],"object_to_goal_dist_end":0.25847,"object_to_goal_dist_start":0.25847,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.61917,0.15527,0.20928],"tcp_start":[0.6246,0.15686,0.18979],"tcp_to_object_dist_end":0.26774,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `5836f8a66456087ed82e2e1accc6472c2a7681a19bf8e3d54637158aadaafc47`; realized-scene SHA-256: `776f3cbcac69f75f44cb26f0b1a492bbf1ced59f3c5fca79400c3f557c2ce565`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46286,-7e-05,0.03]},{"name":"goal","value":[0.61015,0.15287,0.12219]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.46286,-7e-05,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61015,0.15287,0.12219]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0,"average_solve_count":127.0,"average_success_count":127.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":1.24826,"lift_1.lift_height":0.12218,"transport_1.arc_height":0.28881,"transport_1.transport_speed":0.45614},"optimized_scores":{"best_composite_score":0.3453,"best_fitness_score":0.6003,"best_task_score":0.2394},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2870.0,"contact_point_centroid":[0.4687,0.0317,-0.00229],"force_p95":0.13078,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.64465,"mean_force":0.13959,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5251,0.07561,0.21776]},{"body_a":"world","body_b":"grasp_target","contact_count":118.0,"contact_point_centroid":[0.45958,-4e-05,-0.00109],"force_p95":0.51667,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68377,"mean_force":0.07692,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44932,-0.00024,0.02726]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10324.0,"contact_point_centroid":[0.44946,0.01867,0.07746],"force_p95":0.10534,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32961,"mean_force":0.06844,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4468,-0.00025,0.07553]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1572.0,"contact_point_centroid":[0.45666,-0.01198,0.14855],"force_p95":0.19868,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31259,"mean_force":0.12071,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.45144,0.00627,0.15039]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1941.0,"contact_point_centroid":[0.45743,0.02561,0.15064],"force_p95":0.18244,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29541,"mean_force":0.10881,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.45274,0.00764,0.15318]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10885.0,"contact_point_centroid":[0.44938,-0.01907,0.0746],"force_p95":0.10639,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29366,"mean_force":0.06534,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44681,-0.00025,0.07317]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46284,-3e-05,-0.00201],"force_p95":0.12763,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13962,"mean_force":0.12426,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45174,-0.0002,0.02663]},{"body_a":"world","body_b":"grasp_target","contact_count":3216.0,"contact_point_centroid":[0.46286,-7e-05,-0.00195],"force_p95":0.12703,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47924,-5e-05,0.20559]},{"body_a":"world","body_b":"grasp_target","contact_count":1904.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45793,-0.00012,0.07141]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.45822,-0.00013,0.03282]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.46858,0.03174,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.59239,0.13994,0.16858]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.46858,0.03174,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59736,0.14735,0.12889]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4146.0,"contact_point_centroid":[0.45084,0.01908,0.02778],"force_p95":0.07655,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09386,"mean_force":0.0521,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45064,-0.00022,0.02559]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5332.0,"contact_point_centroid":[0.45024,-0.01926,0.02785],"force_p95":0.06293,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08443,"mean_force":0.04076,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45064,-0.00022,0.02559]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2821.0,"contact_point_centroid":[0.53005,0.0799,0.22259],"force_p95":0.01129,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0165,"mean_force":0.01052,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52971,0.07989,0.22034]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4245.0,"contact_point_centroid":[0.59276,0.13995,0.17089],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.0105,"phase_index":6.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.59238,0.13993,0.16864]}],"total_contact_groups":17},"final_pose_error":0.01078,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.46858,0.03174,0.01602],"final_tcp_position":[0.60213,0.14861,0.128],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":272998.47613,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":805.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3216.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.46064,-9e-05,0.11433],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08834,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":476.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1904.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45822,-0.00013,0.03282],"tcp_start":[0.46064,-9e-05,0.11433],"tcp_to_object_dist_end":0.00823,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":199.42248,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_1","tcp_end":[0.45812,-0.00013,0.0327],"tcp_start":[0.45822,-0.00013,0.03282],"tcp_to_object_dist_end":0.00819,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46273,2e-05,0.02592],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23316,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.1275,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11278.0,"raw_peak_contact_force":0.13962,"tcp_end":[0.45061,-0.00022,0.02556],"tcp_start":[0.45812,-0.00013,0.0327],"tcp_to_object_dist_end":0.01212,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.46424,-0.00012,0.12465],"object_pos_start":[0.46273,2e-05,0.02592],"object_to_goal_dist_end":0.21142,"object_to_goal_dist_start":0.23316,"object_z_max":0.12454,"peak_contact_force":0.11323,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21327.0,"raw_peak_contact_force":0.68377,"tcp_end":[0.44684,-0.00024,0.13672],"tcp_start":[0.45061,-0.00022,0.02556],"tcp_to_object_dist_end":0.02118,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46858,0.03174,0.01602],"object_pos_start":[0.46424,-0.00012,0.12465],"object_to_goal_dist_end":0.21444,"object_to_goal_dist_start":0.21142,"object_z_max":0.14732,"peak_contact_force":272998.47613,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9204.0,"raw_peak_contact_force":1.64465,"subtask_id":"transport_arc","tcp_end":[0.58346,0.13003,0.22493],"tcp_start":[0.44684,-0.00024,0.13672],"tcp_to_object_dist_end":0.25788,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46858,0.03174,0.01602],"object_pos_start":[0.46858,0.03174,0.01602],"object_to_goal_dist_end":0.21444,"object_to_goal_dist_start":0.21444,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8245.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60213,0.14861,0.128],"tcp_start":[0.58346,0.13003,0.22493],"tcp_to_object_dist_end":0.20983,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46858,0.03174,0.01602],"object_pos_start":[0.46858,0.03174,0.01602],"object_to_goal_dist_end":0.21444,"object_to_goal_dist_start":0.21444,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.59551,0.14683,0.14863],"tcp_start":[0.60213,0.14861,0.128],"tcp_to_object_dist_end":0.21666,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```