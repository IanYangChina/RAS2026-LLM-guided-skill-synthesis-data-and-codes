## Search State

- **Seed**: 5
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.6056 | 0.93 | ❌ rejected |
| 11 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.2687 | 0.79 | ❌ rejected |
| 10 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 6 | 0.4320 | 0.10 | ❌ rejected |
| 9 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4556 | 0.65 | ❌ rejected |
| 8 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.6199 | 0.92 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.93). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

- Task name: peg_channel
- Frozen realised-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`
- Frozen object start: [0.5244002338996304, 0.1046352631789195, 0.04]
- Frozen task target: [0.5244002338996304, -0.05536473682108051, 0.04]
- Goal object position: (0.5244002338996304, -0.05536473682108051, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5244002338996304, 0.1046352631789195, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.2, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0.2, 0.3]
objects:
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    radius_m: 0.018
    half_length_m: 0.025
  - name: channel_structure
    role: fixture
    dynamics: static
    geometry: two_parallel_walls
    inner_gap_m: 0.05
    wall_thickness_m: 0.03
    wall_height_m: 0.05
task_landmarks:
  frozen_object_start: [0.5244, 0.1046, 0.04]
  frozen_task_target: [0.5244, -0.0554, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5244002338996304, 0.1046352631789195, 0.04]}
  frozen_targets: {'channel_exit': [0.5244002338996304, -0.05536473682108051, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach | object | (0.00, 0.04, 0.00) | distance | — |
| contact | object | (0.00, 0.02, 0.00) | distance | — |
| push | world | (0.50, -0.08, 0.04) | distance | push_depth |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.606) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: approach
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.04
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
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
- id: contact
  type: contact
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.02
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
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
- id: push
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.05
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
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

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.04, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.02, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **push** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.05, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.606
- **task_score** (E): 0.926
- **fitness_score**: 0.836  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2501 |
| contact | 1.00 | 1.00 | 0.0166 |
| push | 0.67 | 1.00 | 0.2128 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.140, 0.058) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.547 | 2.488 |
| contact | contact | 1.00 / step_budget | (0.508, 0.140, 0.058)→(0.505, 0.130, 0.046) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.538 | 0.574 |
| push | push | 0.67 / step_budget | (0.505, 0.130, 0.046)→(0.496, -0.083, 0.035) | (0.504, 0.095, 0.034)→(0.510, -0.168, 0.022) | 0.175→0.100 | 1.00 / 3.667 | 150.158 | 223.184 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.892
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.875
- phase_score: 0.841
- phase_breakdown.contact_score: 0.710
- phase_breakdown.push_score: 0.939
- phase_breakdown.approach_score: 0.677

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.854
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.597
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.317


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9b36d26f861d7a613dfb3d8c86d70470e42095a430c2befa4bd6e530468a8a7e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2af86d8f59685db6584febc0596b9044223ae39cea3120c112c665a54a1c4732`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20455,"average_solve_count":220.0,"average_success_count":220.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.speed":0.03339,"contact.speed":0.05672,"push.push_depth":0.05392,"push.speed":0.06926},"optimized_scores":{"best_composite_score":0.59553,"best_fitness_score":0.82553,"best_task_score":0.90446},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":235.0,"contact_point_centroid":[0.50494,-0.10016,0.065],"force_p95":216.61249,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":227.50779,"mean_force":203.99109,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50043,-0.08775,0.03608]},{"body_a":"peg","body_b":"channel_base_body","contact_count":171.0,"contact_point_centroid":[0.49439,-0.10827,0.03564],"force_p95":118.62275,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":132.79618,"mean_force":54.91844,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.4998,-0.07201,0.03649]},{"body_a":"attachment","body_b":"peg","contact_count":324.0,"contact_point_centroid":[0.49914,-0.02688,0.04145],"force_p95":97.89258,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":121.53833,"mean_force":34.51098,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50204,-0.01598,0.03796]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":317.0,"contact_point_centroid":[0.47463,-0.01992,0.03599],"force_p95":50.00817,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":75.43422,"mean_force":8.43766,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50294,0.00804,0.03843]},{"body_a":"peg","body_b":"channel_base_body","contact_count":331.0,"contact_point_centroid":[0.49613,-0.01065,0.00949],"force_p95":28.30403,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.36801,"mean_force":6.7406,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50378,0.02341,0.03907]},{"body_a":"peg","body_b":"world","contact_count":208.0,"contact_point_centroid":[0.51145,-0.24694,-0.00145],"force_p95":1.35054,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.5685,"mean_force":0.64127,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50049,-0.08761,0.03601]},{"body_a":"peg","body_b":"channel_base_body","contact_count":472.0,"contact_point_centroid":[0.50562,0.10457,0.00937],"force_p95":0.57807,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57031,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50907,0.17323,0.17405]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.5,0.19883,0.29555]},{"body_a":"peg","body_b":"channel_base_body","contact_count":38.0,"contact_point_centroid":[0.5063,0.1049,0.00939],"force_p95":0.57525,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57678,"mean_force":0.54622,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.51562,0.14492,0.05255]}],"total_contact_groups":9},"final_pose_error":0.04709,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.51739,-0.34018,0.01417],"final_tcp_position":[0.50156,-0.08709,0.03524],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":227.50779,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":499.0,"n_steps_budget":1000.0,"object_pos_end":[0.50583,0.10463,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18482,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54724,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":504.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.51893,0.14871,0.05848],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05218,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":38.0,"n_steps_budget":600.0,"object_pos_end":[0.50584,0.1046,0.03383],"object_pos_start":[0.50583,0.10463,0.03384],"object_to_goal_dist_end":0.18479,"object_to_goal_dist_start":0.18482,"object_z_max":0.03384,"peak_contact_force":0.55239,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":38.0,"raw_peak_contact_force":0.57678,"tcp_end":[0.51189,0.13929,0.04588],"tcp_start":[0.51893,0.14871,0.05848],"tcp_to_object_dist_end":0.03722,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":862.0,"n_steps_budget":1000.0,"object_pos_end":[0.51739,-0.34018,0.01417],"object_pos_start":[0.50584,0.1046,0.03383],"object_to_goal_dist_end":0.26203,"object_to_goal_dist_start":0.18479,"object_z_max":0.04,"peak_contact_force":216.72061,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1586.0,"raw_peak_contact_force":227.50779,"tcp_end":[0.50156,-0.08709,0.03524],"tcp_start":[0.51189,0.13929,0.04588],"tcp_to_object_dist_end":0.25445,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `314cefd2153cfe84bc0d0d2dfbeb7f4daf8feaf5f2c7ce7d396802b52a157f39`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77099,"average_solve_count":131.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.speed":0.09849,"contact.speed":0.03904,"push.push_depth":0.01778,"push.speed":0.0778},"optimized_scores":{"best_composite_score":0.62425,"best_fitness_score":0.85425,"best_task_score":0.87464},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":387.0,"contact_point_centroid":[0.50318,-0.01409,0.04056],"force_p95":115.27566,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":127.5389,"mean_force":61.58615,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49754,-0.00468,0.03964]},{"body_a":"peg","body_b":"channel_base_body","contact_count":454.0,"contact_point_centroid":[0.50581,-0.02378,0.00878],"force_p95":102.5736,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":108.24133,"mean_force":45.70835,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49751,0.00193,0.0398]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":312.0,"contact_point_centroid":[0.52547,-0.01535,0.02841],"force_p95":54.72333,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":58.33059,"mean_force":30.13562,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49712,0.00887,0.0397]},{"body_a":"peg","body_b":"channel_base_body","contact_count":27.0,"contact_point_centroid":[0.50048,-0.10017,0.02321],"force_p95":18.89982,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.80873,"mean_force":8.6179,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49891,-0.07139,0.03843]},{"body_a":"peg","body_b":"channel_base_body","contact_count":473.0,"contact_point_centroid":[0.50311,0.06744,0.00933],"force_p95":0.56216,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56483,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49927,0.1565,0.17566]},{"body_a":"peg","body_b":"channel_base_body","contact_count":42.0,"contact_point_centroid":[0.50238,0.0683,0.00938],"force_p95":0.55064,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55098,"mean_force":0.54666,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.49873,0.11007,0.05162]}],"total_contact_groups":6},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49766,-0.07527,0.0203],"final_tcp_position":[0.49868,-0.07803,0.03793],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":127.5389,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":489.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.5465,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":473.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.49971,0.11474,0.05781],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05316,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":42.0,"n_steps_budget":600.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.54359,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":42.0,"raw_peak_contact_force":0.55098,"tcp_end":[0.49878,0.10336,0.0448],"tcp_start":[0.49971,0.11474,0.05781],"tcp_to_object_dist_end":0.0378,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":515.0,"n_steps_budget":1000.0,"object_pos_end":[0.49766,-0.07527,0.0203],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.02039,"object_to_goal_dist_start":0.14762,"object_z_max":0.04007,"peak_contact_force":31.68413,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1180.0,"raw_peak_contact_force":127.5389,"tcp_end":[0.49868,-0.07803,0.03793],"tcp_start":[0.49878,0.10336,0.0448],"tcp_to_object_dist_end":0.01787,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7acce370299b32aeef0e4239da3e97eae076cb9602edead185a6cf774ee0bc4e`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.1619,"average_solve_count":210.0,"average_success_count":210.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.speed":0.06307,"contact.speed":0.04409,"push.push_depth":0.0734,"push.speed":0.05081},"optimized_scores":{"best_composite_score":0.59711,"best_fitness_score":0.82711,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":151.0,"contact_point_centroid":[0.53105,-0.10001,0.06492],"force_p95":194.80859,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":314.50677,"mean_force":131.17623,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.4876,-0.07763,0.03097]},{"body_a":"attachment","body_b":"peg","contact_count":842.0,"contact_point_centroid":[0.50226,-0.03115,0.0533],"force_p95":201.61378,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":212.83204,"mean_force":95.13726,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49504,-0.02203,0.03607]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":800.0,"contact_point_centroid":[0.52609,-0.04569,0.04361],"force_p95":174.28002,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":188.31528,"mean_force":47.89959,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49484,-0.0232,0.0359]},{"body_a":"peg","body_b":"channel_base_body","contact_count":479.0,"contact_point_centroid":[0.51016,-0.1031,0.05531],"force_p95":171.43856,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":185.08372,"mean_force":127.8041,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49246,-0.06927,0.03315]},{"body_a":"peg","body_b":"channel_base_body","contact_count":643.0,"contact_point_centroid":[0.5165,-0.06351,0.00954],"force_p95":50.65763,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.84514,"mean_force":22.5669,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49419,-0.03122,0.03525]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47499,-0.08252,0.03432],"force_p95":47.26262,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":47.50561,"mean_force":44.88336,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.4867,-0.08244,0.03175]},{"body_a":"peg","body_b":"channel_base_body","contact_count":458.0,"contact_point_centroid":[0.50356,0.11163,0.00937],"force_p95":0.61921,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56124,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50238,0.17672,0.17515]},{"body_a":"peg","body_b":"channel_base_body","contact_count":36.0,"contact_point_centroid":[0.50282,0.11178,0.0094],"force_p95":0.5882,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59561,"mean_force":0.54614,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.50417,0.15183,0.05332]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49988,0.19944,0.29867]}],"total_contact_groups":9},"final_pose_error":0.07258,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.51497,-0.08707,0.03285],"final_tcp_position":[0.48667,-0.08253,0.03175],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":314.50677,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":480.0,"n_steps_budget":1000.0,"object_pos_end":[0.50369,0.11175,0.03386],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.54664,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":474.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.50591,0.15523,0.05902],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05028,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":36.0,"n_steps_budget":600.0,"object_pos_end":[0.50373,0.11179,0.03379],"object_pos_start":[0.50369,0.11175,0.03386],"object_to_goal_dist_end":0.19193,"object_to_goal_dist_start":0.19189,"object_z_max":0.03386,"peak_contact_force":0.51902,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":36.0,"raw_peak_contact_force":0.59561,"tcp_end":[0.50298,0.14652,0.04679],"tcp_start":[0.50591,0.15523,0.05902],"tcp_to_object_dist_end":0.03709,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51497,-0.08707,0.03285],"object_pos_start":[0.50373,0.11179,0.03379],"object_to_goal_dist_end":0.01803,"object_to_goal_dist_start":0.19193,"object_z_max":0.03768,"peak_contact_force":202.06914,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2918.0,"raw_peak_contact_force":314.50677,"tcp_end":[0.48667,-0.08253,0.03175],"tcp_start":[0.50298,0.14652,0.04679],"tcp_to_object_dist_end":0.02868,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```