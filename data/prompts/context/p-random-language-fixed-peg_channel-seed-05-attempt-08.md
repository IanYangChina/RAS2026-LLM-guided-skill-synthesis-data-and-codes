## Search State

- **Seed**: 5
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.6199 | 0.92 | ❌ rejected |
| 7 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.1849 | 0.40 | ❌ rejected |
| 6 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.5812 | 0.90 | ❌ rejected |
| 5 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.6025 | 0.95 | ❌ rejected |
| 4 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.6042 | 0.99 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.92). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.620) — your mutation base

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

- **Composite score**: 0.620
- **task_score** (E): 0.924
- **fitness_score**: 0.850  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2501 |
| contact | 1.00 | 1.00 | 0.0180 |
| push | 0.67 | 1.00 | 0.2137 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.140, 0.058) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.563 | 2.488 |
| contact | contact | 1.00 / step_budget | (0.508, 0.140, 0.058)→(0.504, 0.129, 0.045) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.560 | 0.575 |
| push | push | 0.67 / step_budget | (0.504, 0.129, 0.045)→(0.501, -0.085, 0.037) | (0.504, 0.095, 0.034)→(0.512, -0.144, 0.018) | 0.175→0.083 | 1.00 / 2.000 | 170.380 | 189.565 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 1.000
- phase_score: 0.780
- phase_breakdown.contact_score: 0.739
- phase_breakdown.push_score: 0.829
- phase_breakdown.approach_score: 0.674

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.868
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.631
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.230


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.96875,"average_solve_count":224.0,"average_success_count":224.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.speed":0.05981,"contact.speed":0.0499,"push.push_depth":0.06456,"push.speed":0.04958},"optimized_scores":{"best_composite_score":0.63124,"best_fitness_score":0.86124,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":346.0,"contact_point_centroid":[0.50468,-0.10014,0.065],"force_p95":218.37459,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":225.60244,"mean_force":207.66785,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49998,-0.08763,0.03543]},{"body_a":"peg","body_b":"channel_base_body","contact_count":170.0,"contact_point_centroid":[0.49392,-0.10828,0.0391],"force_p95":113.79499,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":142.73448,"mean_force":56.79666,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50016,-0.0717,0.03661]},{"body_a":"attachment","body_b":"peg","contact_count":358.0,"contact_point_centroid":[0.49966,-0.01833,0.04427],"force_p95":96.54796,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":114.32719,"mean_force":36.75007,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50293,-0.0075,0.03851]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":392.0,"contact_point_centroid":[0.47446,-0.02084,0.03736],"force_p95":51.42062,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":92.23092,"mean_force":13.36994,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50345,0.00669,0.03878]},{"body_a":"peg","body_b":"channel_base_body","contact_count":289.0,"contact_point_centroid":[0.49821,-0.01658,0.00959],"force_p95":19.76324,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.61636,"mean_force":6.22851,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50406,0.01875,0.03922]},{"body_a":"peg","body_b":"channel_base_body","contact_count":469.0,"contact_point_centroid":[0.50566,0.10467,0.00937],"force_p95":0.57823,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57044,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50907,0.17316,0.17375]},{"body_a":"peg","body_b":"world","contact_count":313.0,"contact_point_centroid":[0.51064,-0.18373,-0.00158],"force_p95":1.04993,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98956,"mean_force":0.63373,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50007,-0.08753,0.03535]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50008,0.19877,0.2952]},{"body_a":"peg","body_b":"channel_base_body","contact_count":38.0,"contact_point_centroid":[0.50568,0.10501,0.00939],"force_p95":0.57525,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57678,"mean_force":0.54629,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.51563,0.14492,0.05257]}],"total_contact_groups":9},"final_pose_error":0.05777,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.52723,-0.19027,0.01411],"final_tcp_position":[0.50172,-0.08708,0.03454],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":225.60244,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":496.0,"n_steps_budget":1000.0,"object_pos_end":[0.50591,0.10456,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54674,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":501.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.51893,0.14871,0.05848],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05221,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":38.0,"n_steps_budget":600.0,"object_pos_end":[0.50595,0.10457,0.03384],"object_pos_start":[0.50591,0.10456,0.03384],"object_to_goal_dist_end":0.18477,"object_to_goal_dist_start":0.18476,"object_z_max":0.03384,"peak_contact_force":0.5413,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":38.0,"raw_peak_contact_force":0.57678,"tcp_end":[0.51192,0.13927,0.04589],"tcp_start":[0.51893,0.14871,0.05848],"tcp_to_object_dist_end":0.03721,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52723,-0.19027,0.01411],"object_pos_start":[0.50595,0.10457,0.03384],"object_to_goal_dist_end":0.11649,"object_to_goal_dist_start":0.18477,"object_z_max":0.0404,"peak_contact_force":218.22541,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1868.0,"raw_peak_contact_force":225.60244,"tcp_end":[0.50172,-0.08708,0.03454],"tcp_start":[0.51192,0.13927,0.04589],"tcp_to_object_dist_end":0.10824,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36269,"average_solve_count":193.0,"average_success_count":193.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.speed":0.07099,"contact.speed":0.08801,"push.push_depth":0.01867,"push.speed":0.04384},"optimized_scores":{"best_composite_score":0.5906,"best_fitness_score":0.8206,"best_task_score":0.77074},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":477.0,"contact_point_centroid":[0.50264,-0.00202,0.04133],"force_p95":98.24552,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":108.52395,"mean_force":62.55277,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49855,0.00515,0.04087]},{"body_a":"peg","body_b":"channel_base_body","contact_count":528.0,"contact_point_centroid":[0.50356,-0.0124,0.0088],"force_p95":89.08416,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":94.35294,"mean_force":53.95623,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.4985,0.00903,0.04097]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":201.0,"contact_point_centroid":[0.52525,0.01526,0.02856],"force_p95":43.30422,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.55717,"mean_force":26.28518,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49757,0.0375,0.04132]},{"body_a":"peg","body_b":"channel_base_body","contact_count":482.0,"contact_point_centroid":[0.50311,0.06744,0.00933],"force_p95":0.56001,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56449,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49914,0.15653,0.17579]},{"body_a":"peg","body_b":"channel_base_body","contact_count":42.0,"contact_point_centroid":[0.50239,0.0683,0.00938],"force_p95":0.55064,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55098,"mean_force":0.54664,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.49865,0.11007,0.05163]}],"total_contact_groups":5},"final_pose_error":0.0197,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49761,-0.05863,0.02689],"final_tcp_position":[0.50162,-0.07904,0.0406],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":108.52395,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":498.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54648,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":482.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.4996,0.11474,0.05782],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05317,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":42.0,"n_steps_budget":600.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.54397,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":42.0,"raw_peak_contact_force":0.55098,"tcp_end":[0.49873,0.10337,0.04481],"tcp_start":[0.4996,0.11474,0.05782],"tcp_to_object_dist_end":0.03782,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":551.0,"n_steps_budget":1000.0,"object_pos_end":[0.49761,-0.05863,0.02689],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.02518,"object_to_goal_dist_start":0.14762,"object_z_max":0.04008,"peak_contact_force":76.1039,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1206.0,"raw_peak_contact_force":108.52395,"tcp_end":[0.50162,-0.07904,0.0406],"tcp_start":[0.49873,0.10337,0.04481],"tcp_to_object_dist_end":0.02491,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.15301,"average_solve_count":183.0,"average_success_count":183.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.speed":0.09565,"contact.speed":0.01002,"push.push_depth":0.04715,"push.speed":0.09955},"optimized_scores":{"best_composite_score":0.63801,"best_fitness_score":0.86801,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":120.0,"contact_point_centroid":[0.50272,-0.10028,0.065],"force_p95":220.55428,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":234.56882,"mean_force":208.58445,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49793,-0.08808,0.03518]},{"body_a":"peg","body_b":"channel_base_body","contact_count":249.0,"contact_point_centroid":[0.49629,-0.10576,0.04362],"force_p95":94.81543,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":141.72497,"mean_force":59.29415,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49807,-0.06204,0.0364]},{"body_a":"attachment","body_b":"peg","contact_count":480.0,"contact_point_centroid":[0.49857,-0.01838,0.04108],"force_p95":98.60442,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":117.58818,"mean_force":45.38572,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49829,-0.00715,0.0375]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":58.0,"contact_point_centroid":[0.47463,-0.03549,0.0315],"force_p95":53.14765,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":88.62845,"mean_force":12.50976,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49784,-0.00569,0.03684]},{"body_a":"peg","body_b":"channel_base_body","contact_count":409.0,"contact_point_centroid":[0.50051,-0.02236,0.00961],"force_p95":51.34774,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":57.33362,"mean_force":22.58004,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49855,0.01379,0.03812]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":38.0,"contact_point_centroid":[0.5256,0.03368,0.04505],"force_p95":32.64914,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.5496,"mean_force":8.84404,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49805,0.06212,0.03808]},{"body_a":"peg","body_b":"world","contact_count":88.0,"contact_point_centroid":[0.51137,-0.17506,-0.00152],"force_p95":2.22341,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.29229,"mean_force":0.7419,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.4981,-0.08788,0.03507]},{"body_a":"peg","body_b":"channel_base_body","contact_count":445.0,"contact_point_centroid":[0.50359,0.11168,0.00937],"force_p95":0.61615,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.5615,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.5025,0.17667,0.17478]},{"body_a":"peg","body_b":"channel_base_body","contact_count":70.0,"contact_point_centroid":[0.5038,0.11173,0.00939],"force_p95":0.59359,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59633,"mean_force":0.54652,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.50338,0.15099,0.05185]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49996,0.19941,0.29839]}],"total_contact_groups":10},"final_pose_error":0.0399,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.51203,-0.18226,0.0138],"final_tcp_position":[0.49899,-0.08763,0.03465],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":234.56882,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":467.0,"n_steps_budget":1000.0,"object_pos_end":[0.50368,0.11176,0.03385],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.59452,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":461.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.50594,0.15523,0.05898],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05025,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":70.0,"n_steps_budget":1000.0,"object_pos_end":[0.50367,0.11178,0.0338],"object_pos_start":[0.50368,0.11176,0.03385],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.1919,"object_z_max":0.03385,"peak_contact_force":0.59469,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":70.0,"raw_peak_contact_force":0.59633,"tcp_end":[0.50194,0.14408,0.04357],"tcp_start":[0.50594,0.15523,0.05898],"tcp_to_object_dist_end":0.0338,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":800.0,"n_steps_budget":1000.0,"object_pos_end":[0.51203,-0.18226,0.0138],"object_pos_start":[0.50367,0.11178,0.0338],"object_to_goal_dist_end":0.10625,"object_to_goal_dist_start":0.19191,"object_z_max":0.04081,"peak_contact_force":216.81086,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1442.0,"raw_peak_contact_force":234.56882,"tcp_end":[0.49899,-0.08763,0.03465],"tcp_start":[0.50194,0.14408,0.04357],"tcp_to_object_dist_end":0.09777,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```