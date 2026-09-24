## Search State

- **Seed**: 8
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 0.9533 | 1.00 | ❌ rejected |
| 9 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 0.7867 | 1.00 | ❌ rejected |
| 8 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 1.1200 | 1.00 | ❌ rejected |
| 7 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 1.1200 | 1.00 | ❌ rejected |
| 6 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 1.1200 | 1.00 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (1.00). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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
- Frozen realised-scene SHA-256: `03ad88d640dcd23384857b752dfa12af63a722a6c6b9379a358f8168d1c71e09`
- Frozen initial hinge angle: -0.060 rad
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
  frozen_initial_hinge_angle_rad: -0.0604
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: 03ad88d640dcd23384857b752dfa12af63a722a6c6b9379a358f8168d1c71e09

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

## Current Skill (Q=0.953) — your mutation base

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
- id: approach_handle
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
    - 0.35
    orientation:
      mode: none
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: reach_handle
- id: make_contact
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
    - 0.0
    offset_along_axis:
      distance: 0.03
      axis: world_x
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    contact_distance:
      type: scalar
      range:
      - 0.005
      - 0.08
      default: 0.03
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 25.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
- id: push_door
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.25
      axis: world_x
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_duration:
      type: scalar
      range:
      - 1.0
      - 5.0
      default: 3.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: repeat
  subtask_id: open_door

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_handle** (`approach`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[-0.4, -0.02, 0.35]
  - orientation: mode=none
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **make_contact** (`contact`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_x, distance=0.03, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **push_door** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_x, distance=0.25, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_duration: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=repeat

## Design Metrics

- **Composite score**: 0.953
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_handle | 1.00 | 1.00 | 0.1972 |
| make_contact | 1.00 | 1.00 | 0.0248 |
| push_door | 1.00 | 0.67 | 0.2633 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_handle | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.100, 0.202, 0.349) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 3.667 | 19.229 | 20.113 |
| make_contact | contact | 1.00 / force_exceeded | (0.100, 0.202, 0.349)→(0.125, 0.201, 0.347) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 3.667 | 217.063 | 431.639 |
| push_door | push | 1.00 / time_limit | (0.125, 0.201, 0.347)→(0.388, 0.206, 0.344) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 3.333 | 3.248 | 29.091 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 1.120
- **K-run variance**: 0.0556
- **Stagnated**: no
- **Stop reason**: tolflatfitness
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.302


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `ea6bae111f14debb91f5aac35e1b236c8a3b6c6e55761aa2eab002718511c500`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `4672b672dcc6ffecf2b710096d1b05b46bb79ca3304db4877275d5463822e477`; realized-scene SHA-256: `03ad88d640dcd23384857b752dfa12af63a722a6c6b9379a358f8168d1c71e09`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.0604,"panel":{"name":"door_panel","orientation":[0.99954,0.0,0.0,-0.03019],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99954,0.0,0.0,-0.03019],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.45205,"average_solve_count":73.0,"average_success_count":73.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.17571,"approach_handle.approach_tolerance":0.0262,"make_contact.contact_distance":0.0395,"make_contact.contact_force_threshold":14.73047,"push_door.push_distance":0.28261,"push_door.push_duration":3.39706,"push_door.push_speed":0.18287},"optimized_scores":{"best_composite_score":1.12,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_frame","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.4754,0.19287,0.37291],"force_p95":323.46614,"geom_a":"door_frame_hinge_post","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":323.59198,"mean_force":298.10401,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.38811,0.20741,0.34293]},{"body_a":"door_panel","body_b":"link7","contact_count":379.0,"contact_point_centroid":[0.33432,0.14849,0.39378],"force_p95":114.66554,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":186.49861,"mean_force":50.31678,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.28491,0.2052,0.34461]},{"body_a":"door_panel","body_b":"link7","contact_count":107.0,"contact_point_centroid":[0.15093,0.18538,0.39475],"force_p95":41.30072,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.29345,"mean_force":18.60143,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10015,0.24277,0.34874]},{"body_a":"door_panel","body_b":"link6","contact_count":14.0,"contact_point_centroid":[0.10083,0.2219,0.47214],"force_p95":40.89505,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.71787,"mean_force":20.36512,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09997,0.27686,0.34853]},{"body_a":"door_panel","body_b":"link7","contact_count":41.0,"contact_point_centroid":[0.1647,0.14715,0.39746],"force_p95":18.5278,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.63875,"mean_force":10.7533,"phase_index":1.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.11665,0.20481,0.34744]},{"body_a":"world","body_b":"door_panel","contact_count":296.0,"contact_point_centroid":[0.30042,0.19224,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09999,0.29969,0.34871]},{"body_a":"world","body_b":"door_panel","contact_count":284.0,"contact_point_centroid":[0.30396,0.15916,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.11358,0.20485,0.3476]},{"body_a":"world","body_b":"door_panel","contact_count":936.0,"contact_point_centroid":[0.31318,0.13257,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.25008,0.20477,0.34498]}],"total_contact_groups":8},"final_pose_error":0.01838,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.38843,0.20744,0.34302],"hinge_angle":0.68048,"initial_hinge_angle":-0.0604,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.0604,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":323.59198,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":311.0,"n_steps_budget":780.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":33.25171,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":325.0,"raw_peak_contact_force":19.63875,"subtask_id":"reach_handle","tcp_end":[0.10054,0.20604,0.34913],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.41768,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":269.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"make_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1326.0,"raw_peak_contact_force":323.59198,"tcp_end":[0.12349,0.2048,0.34735],"tcp_start":[0.10054,0.20604,0.34913],"tcp_to_object_dist_end":0.42171,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":931.0,"n_steps_budget":960.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":4.96198,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":417.0,"raw_peak_contact_force":49.29345,"subtask_id":"open_door","tcp_end":[0.38843,0.20744,0.34302],"tcp_start":[0.12349,0.2048,0.34735],"tcp_to_object_dist_end":0.55818,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `6091bac9443f311cc90f1388d6700bb5b9c315c724ba8069ca061d7c4a07c1f1`; realized-scene SHA-256: `8483aeff51d0063ec1cf7a724dac4352cd76049b8e216b9602c279ab004268b5`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.12924,"panel":{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.55556,"average_solve_count":72.0,"average_success_count":72.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.16727,"approach_handle.approach_tolerance":0.01514,"make_contact.contact_distance":0.04506,"make_contact.contact_force_threshold":12.72459,"push_door.push_distance":0.33122,"push_door.push_duration":2.51447,"push_door.push_speed":0.21006},"optimized_scores":{"best_composite_score":1.12,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_frame","body_b":"link7","contact_count":129.0,"contact_point_centroid":[0.4753,0.18108,0.3722],"force_p95":426.48584,"geom_a":"door_frame_hinge_post","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":497.43079,"mean_force":333.83502,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.388,0.19965,0.34433]},{"body_a":"door_panel","body_b":"link7","contact_count":364.0,"contact_point_centroid":[0.33684,0.13966,0.39202],"force_p95":153.73266,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":221.08563,"mean_force":57.77961,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.28522,0.19405,0.34434]},{"body_a":"door_panel","body_b":"link7","contact_count":40.0,"contact_point_centroid":[0.14791,0.14654,0.39863],"force_p95":26.98961,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.97913,"mean_force":17.13166,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10007,0.20425,0.34872]},{"body_a":"door_panel","body_b":"link7","contact_count":55.0,"contact_point_centroid":[0.15659,0.13593,0.39828],"force_p95":15.0179,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.7751,"mean_force":11.32565,"phase_index":1.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.10966,0.19374,0.34738]},{"body_a":"world","body_b":"door_panel","contact_count":560.0,"contact_point_centroid":[0.30299,0.16418,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09977,0.30373,0.34837]},{"body_a":"world","body_b":"door_panel","contact_count":172.0,"contact_point_centroid":[0.30524,0.15346,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.10959,0.19377,0.34742]},{"body_a":"world","body_b":"door_panel","contact_count":848.0,"contact_point_centroid":[0.32178,0.117,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.25663,0.19397,0.34475]}],"total_contact_groups":7},"final_pose_error":0.06263,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.38848,0.20482,0.34608],"hinge_angle":0.8191,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":497.43079,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":520.0,"n_steps_budget":840.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.14151,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":227.0,"raw_peak_contact_force":20.7751,"subtask_id":"reach_handle","tcp_end":[0.10009,0.19477,0.34876],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.41182,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":211.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":302.3037,"phase_name":"make_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1341.0,"raw_peak_contact_force":497.43079,"tcp_end":[0.11885,0.19353,0.34704],"tcp_start":[0.10009,0.19477,0.34876],"tcp_to_object_dist_end":0.41475,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":961.0,"n_steps_budget":990.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":4.7833,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":600.0,"raw_peak_contact_force":37.97913,"subtask_id":"open_door","tcp_end":[0.38848,0.20482,0.34608],"tcp_start":[0.11885,0.19353,0.34704],"tcp_to_object_dist_end":0.55914,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `3d62b54ff2d8b84e841b6e4711bcf5c00d2771c3332b770c71c3a72dad860645`; realized-scene SHA-256: `0f1da74cddf6e66211f4104e2813e757573c0ccccbad31f53b6672ec96f686dd`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.15917,"panel":{"name":"door_panel","orientation":[0.99683,0.0,0.0,0.0795],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99683,0.0,0.0,0.0795],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.05618,"average_solve_count":89.0,"average_success_count":89.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.13598,"approach_handle.approach_tolerance":0.02555,"make_contact.contact_distance":0.03673,"make_contact.contact_force_threshold":19.18943,"push_door.push_distance":0.39561,"push_door.push_duration":2.96996,"push_door.push_speed":0.16535},"optimized_scores":{"best_composite_score":0.62,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_frame","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.47539,0.19192,0.372],"force_p95":473.63123,"geom_a":"door_frame_hinge_post","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":473.89407,"mean_force":336.09269,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.38798,0.20663,0.3424]},{"body_a":"door_panel","body_b":"link7","contact_count":409.0,"contact_point_centroid":[0.3355,0.14764,0.39339],"force_p95":108.54211,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":220.29549,"mean_force":49.98104,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.28616,0.20438,0.34417]},{"body_a":"door_panel","body_b":"link7","contact_count":63.0,"contact_point_centroid":[0.16873,0.14648,0.39698],"force_p95":19.13512,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.92621,"mean_force":11.23683,"phase_index":1.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.12069,0.2041,0.34692]},{"body_a":"world","body_b":"door_panel","contact_count":404.0,"contact_point_centroid":[0.30406,0.15866,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09995,0.30615,0.34842]},{"body_a":"world","body_b":"door_panel","contact_count":424.0,"contact_point_centroid":[0.30413,0.15835,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.11709,0.20416,0.34709]},{"body_a":"world","body_b":"door_panel","contact_count":868.0,"contact_point_centroid":[0.31381,0.1312,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.25171,0.20402,0.34449]}],"total_contact_groups":6},"final_pose_error":0.14057,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.38782,0.20682,0.34267],"hinge_angle":0.69435,"initial_hinge_angle":0.15917,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15917,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":473.89407,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":334.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":11.29494,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":487.0,"raw_peak_contact_force":19.92621,"subtask_id":"reach_handle","tcp_end":[0.10043,0.20536,0.34868],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.41694,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":384.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":348.88478,"phase_name":"make_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1296.0,"raw_peak_contact_force":473.89407,"tcp_end":[0.13269,0.2041,0.34685],"tcp_start":[0.10043,0.20536,0.34868],"tcp_to_object_dist_end":0.42375,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":404.0,"raw_peak_contact_force":0.0,"subtask_id":"open_door","tcp_end":[0.38782,0.20682,0.34267],"tcp_start":[0.13269,0.2041,0.34685],"tcp_to_object_dist_end":0.55731,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```