## Search State

- **Seed**: 7
- **Iteration**: 15 / 15

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

- Task name: door_push
- Frozen realised-scene SHA-256: `82ce57ad272540c243cfe7c86f1faba3a732bddf0a834ea70613e69de7a6ff57`
- Frozen initial hinge angle: 0.044 rad
- target_hinge_angle: 0.524 rad (task success = realised hinge-angle delta ratio; not TCP proximity)
- Goal tolerance: 0.05 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 30.0 N
- Robot initial TCP position: (0.1, 0.4, 0.35)
- Primary evaluation target: **hinge angle delta ratio (realised hinge motion / target_hinge_angle)**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.1, 0.4, 0.35]
objects:
  - name: door_panel
    role: fixture
    dynamics: hinged
    geometry: box
    dimensions_m: [0.4, 0.02, 0.7]
    hinge_axis: Z
    hinge_joint_name: door_hinge
  - name: door_handle
    role: grasp_site
    dynamics: hinged_with_panel
    geometry: site
    body_frame_offset_m: [-0.4, -0.02, 0.35]
  - name: door_frame
    role: fixture
    dynamics: static
    geometry: box
task_landmarks:
  frozen_fixture_position: [0.5, 0.2, 0]
  frozen_initial_hinge_angle_rad: 0.0437
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: 82ce57ad272540c243cfe7c86f1faba3a732bddf0a834ea70613e69de7a6ff57

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 1.000, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position | approach/contact targets near object |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose (0.5, 0.2, 0.0) | approach/contact targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.590) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: reach_handle
  anchor: fixture
  offset:
  - -0.4
  - -0.02
  - 0.35
  weight: 0.3
- id: open_door
  anchor: fixture
  target_entity: hinge
  metric: hinge_angle
  weight: 0.7
phases:
- id: approach_surface
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: door_panel
    offset:
    - -0.4
    - -0.02
    - 0.4
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_handle
- id: descend_contact
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.05
      axis: world_z
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 3.0
      - 15.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_distance:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: reach_handle
- id: push_door
  type: push
  generator: impedance_motion
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: world_y
      mode: add_to_offset
      sign: negative
    tolerance: 0.05
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.35
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.005
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: open_door

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_surface** (`approach`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[-0.4, -0.02, 0.4], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_contact** (`descend`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.05, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - descend_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **push_door** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.2, mode=add_to_offset, sign=negative}, tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.590
- **task_score** (E): 0.920
- **fitness_score**: 0.920  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_surface | 1.00 | 1.00 | 0.2052 |
| descend_contact | 0.00 | 0.67 | 0.0269 |
| push_door | 1.00 | 0.67 | 0.1511 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_surface | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.100, 0.199, 0.394) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 3.667 | 10.577 | 36.931 |
| descend_contact | descend | 0.00 / step_budget | (0.100, 0.199, 0.394)→(0.100, 0.198, 0.367) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 2.667 | 0.000 | 4.796 |
| push_door | push | 1.00 / time_limit | (0.100, 0.198, 0.367)→(0.096, 0.053, 0.409) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 2.000 | 14.319 | 28.608 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 0.667

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.629
- **K-run variance**: 0.0073
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.7
- **Final σ (mean)**: 0.423


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2fa9c04e562df03eff32cc7f63abe386d265bbd85d42dcee2df7f90a42e2de0a`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `fb31b2d7951f101afe3533d0babe40d387e4396f53837e61e543f2cfc46b7e19`; realized-scene SHA-256: `82ce57ad272540c243cfe7c86f1faba3a732bddf0a834ea70613e69de7a6ff57`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.04367,"panel":{"name":"door_panel","orientation":[0.99976,0.0,0.0,0.02183],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99976,0.0,0.0,0.02183],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86538,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_surface.approach_speed":0.0975,"descend_contact.contact_force":7.39791,"descend_contact.descend_distance":0.02111,"push_door.push_distance":0.26771,"push_door.push_speed":0.09795,"push_door.push_timeout":4.24204},"optimized_scores":{"best_composite_score":0.629,"best_fitness_score":0.959,"best_task_score":0.959},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":89.0,"contact_point_centroid":[0.14584,0.16078,0.43494],"force_p95":34.79402,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.70003,"mean_force":17.86965,"phase_index":0.0,"phase_name":"approach_surface","phase_type":"approach","tcp_position_centroid":[0.10014,0.22277,0.38823]},{"body_a":"door_panel","body_b":"link7","contact_count":715.0,"contact_point_centroid":[0.14421,0.06098,0.43048],"force_p95":18.07511,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.73925,"mean_force":12.66872,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.0994,0.12239,0.38297]},{"body_a":"world","body_b":"door_panel","contact_count":428.0,"contact_point_centroid":[0.30111,0.17785,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_surface","phase_type":"approach","tcp_position_centroid":[0.09994,0.29723,0.37119]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.14265,0.1353,0.44192],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.10022,0.19863,0.39384]},{"body_a":"world","body_b":"door_panel","contact_count":128.0,"contact_point_centroid":[0.30516,0.15376,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.09999,0.19791,0.38652]},{"body_a":"world","body_b":"door_panel","contact_count":1024.0,"contact_point_centroid":[0.31788,0.11961,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09939,0.12363,0.38303]}],"total_contact_groups":6},"final_pose_error":0.1159,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09646,0.04023,0.41267],"hinge_angle":0.54618,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":38.70003,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":462.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.75854,"phase_name":"approach_surface","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":517.0,"raw_peak_contact_force":38.70003,"subtask_id":"reach_handle","tcp_end":[0.10022,0.19863,0.39384],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.45234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":129.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":129.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_handle","tcp_end":[0.1,0.19754,0.37754],"tcp_start":[0.10022,0.19863,0.39384],"tcp_to_object_dist_end":0.43768,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1739.0,"raw_peak_contact_force":28.73925,"subtask_id":"open_door","tcp_end":[0.09646,0.04023,0.41267],"tcp_start":[0.1,0.19754,0.37754],"tcp_to_object_dist_end":0.4257,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2fe1c8aab50c64fd16f940100e2036790f2ea8f75271c649e6989441e8f9191e`; realized-scene SHA-256: `03ad88d640dcd23384857b752dfa12af63a722a6c6b9379a358f8168d1c71e09`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.0604,"panel":{"name":"door_panel","orientation":[0.99954,0.0,0.0,-0.03019],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99954,0.0,0.0,-0.03019],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51079,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_surface.approach_speed":0.05734,"descend_contact.contact_force":6.13477,"descend_contact.descend_distance":0.04543,"push_door.push_distance":0.20318,"push_door.push_speed":0.07255,"push_door.push_timeout":6.95125},"optimized_scores":{"best_composite_score":0.67,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":153.0,"contact_point_centroid":[0.14745,0.17947,0.42919],"force_p95":28.55748,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.74156,"mean_force":17.86733,"phase_index":0.0,"phase_name":"approach_surface","phase_type":"approach","tcp_position_centroid":[0.1,0.24062,0.384]},{"body_a":"door_panel","body_b":"link7","contact_count":689.0,"contact_point_centroid":[0.14154,0.07701,0.41125],"force_p95":18.10383,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.31541,"mean_force":12.44223,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09919,0.14028,0.36305]},{"body_a":"door_panel","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.14248,0.13467,0.41431],"force_p95":14.27595,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.38739,"mean_force":10.15658,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.09997,0.19787,0.366]},{"body_a":"world","body_b":"door_panel","contact_count":476.0,"contact_point_centroid":[0.30031,0.19341,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_surface","phase_type":"approach","tcp_position_centroid":[0.0999,0.30171,0.37011]},{"body_a":"world","body_b":"door_panel","contact_count":264.0,"contact_point_centroid":[0.30507,0.15415,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.09996,0.19795,0.37436]},{"body_a":"world","body_b":"door_panel","contact_count":928.0,"contact_point_centroid":[0.31576,0.1232,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09901,0.13346,0.3658]}],"total_contact_groups":6},"final_pose_error":0.099,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09609,0.0819,0.39951],"hinge_angle":0.46383,"initial_hinge_angle":-0.0604,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.0604,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":32.74156,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":491.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":5.02886,"phase_name":"approach_surface","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":629.0,"raw_peak_contact_force":32.74156,"subtask_id":"reach_handle","tcp_end":[0.10015,0.19891,0.39374],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.45236,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":291.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":275.0,"raw_peak_contact_force":14.38739,"subtask_id":"reach_handle","tcp_end":[0.09996,0.19771,0.35315],"tcp_start":[0.10015,0.19891,0.39374],"tcp_to_object_dist_end":0.41689,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":3.40398,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1617.0,"raw_peak_contact_force":27.31541,"subtask_id":"open_door","tcp_end":[0.09609,0.0819,0.39951],"tcp_start":[0.09996,0.19771,0.35315],"tcp_to_object_dist_end":0.41899,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `356d1c9659b48b76a1cff255b134bf18d0729848f67621b991467785bdaaef44`; realized-scene SHA-256: `8483aeff51d0063ec1cf7a724dac4352cd76049b8e216b9602c279ab004268b5`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.12924,"panel":{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.08163,"average_solve_count":98.0,"average_success_count":98.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_surface.approach_speed":0.11123,"descend_contact.contact_force":7.53238,"descend_contact.descend_distance":0.0286,"push_door.push_distance":0.2591,"push_door.push_speed":0.09992,"push_door.push_timeout":6.29624},"optimized_scores":{"best_composite_score":0.47152,"best_fitness_score":0.80152,"best_task_score":0.80152},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":38.0,"contact_point_centroid":[0.14404,0.14564,0.43936],"force_p95":25.86155,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.35088,"mean_force":17.22873,"phase_index":0.0,"phase_name":"approach_surface","phase_type":"approach","tcp_position_centroid":[0.10034,0.20834,0.39179]},{"body_a":"door_panel","body_b":"link7","contact_count":700.0,"contact_point_centroid":[0.1442,0.06093,0.42722],"force_p95":16.99918,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.76851,"mean_force":12.84556,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.0992,0.12215,0.37978]},{"body_a":"world","body_b":"door_panel","contact_count":512.0,"contact_point_centroid":[0.30302,0.16401,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_surface","phase_type":"approach","tcp_position_centroid":[0.09998,0.30258,0.37007]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.14278,0.13548,0.44208],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.10036,0.19888,0.39402]},{"body_a":"world","body_b":"door_panel","contact_count":184.0,"contact_point_centroid":[0.30516,0.15379,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.10013,0.19807,0.38343]},{"body_a":"world","body_b":"door_panel","contact_count":900.0,"contact_point_centroid":[0.31782,0.11965,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09925,0.12364,0.37898]}],"total_contact_groups":6},"final_pose_error":0.10856,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09509,0.03698,0.41594],"hinge_angle":0.54924,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":39.55439,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":455.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.94427,"phase_name":"approach_surface","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":550.0,"raw_peak_contact_force":39.35088,"subtask_id":"reach_handle","tcp_end":[0.10036,0.19888,0.39402],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.45263,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":174.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":185.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_handle","tcp_end":[0.10014,0.19772,0.37027],"tcp_start":[0.10036,0.19888,0.39402],"tcp_to_object_dist_end":0.43153,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":39.55439,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1600.0,"raw_peak_contact_force":29.76851,"subtask_id":"open_door","tcp_end":[0.09509,0.03698,0.41594],"tcp_start":[0.10014,0.19772,0.37027],"tcp_to_object_dist_end":0.42827,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```