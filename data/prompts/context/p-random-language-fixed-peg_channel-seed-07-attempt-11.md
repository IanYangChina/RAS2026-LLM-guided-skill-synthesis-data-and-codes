## Search State

- **Seed**: 7
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.3576 | 0.74 | ✅ accepted |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2720 | 0.02 | ❌ rejected |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.0244 | 0.54 | ❌ rejected |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1262 | 0.54 | ✅ accepted |
| 7 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.1314 | 0.26 | ✅ accepted |

**Proposal policy**: task_score is 0.74 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: peg_channel
- Frozen realised-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`
- Frozen object start: [0.5100076373283734, 0.11177710407756605, 0.04]
- Frozen task target: [0.5100076373283734, -0.04822289592243395, 0.04]
- Goal object position: (0.5100076373283734, -0.04822289592243395, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5100076373283734, 0.11177710407756605, 0.04)
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
  frozen_object_start: [0.51, 0.1118, 0.04]
  frozen_task_target: [0.51, -0.0482, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5100076373283734, 0.11177710407756605, 0.04]}
  frozen_targets: {'channel_exit': [0.5100076373283734, -0.04822289592243395, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415

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

## Current Skill (Q=0.358) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: approach_to_peg
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
    - 0.08
    tolerance: 0.01
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
  subtask_id: approach
- id: descend_behind_peg
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.0
    tolerance: 0.005
    orientation:
      mode: none
  subtask_id: contact
- id: push_through_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push
- id: retract_from_channel
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.01
    orientation:
      mode: none

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_to_peg** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.04, 0.08], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_behind_peg** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.0], tolerance=0.005
  - orientation: mode=none
  - parameter_bindings: none
- **push_through_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_from_channel** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.358
- **task_score** (E): 0.739
- **fitness_score**: 0.568  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_peg | 1.00 | 1.00 | 0.1838 |
| descend_behind_peg | 1.00 | 1.00 | 0.0916 |
| push_through_channel | 1.00 | 1.00 | 0.1605 |
| retract_from_channel | 1.00 | 1.00 | 0.0689 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.141, 0.128) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.556 | 2.732 |
| descend_behind_peg | descend | 1.00 / step_budget | (0.505, 0.141, 0.128)→(0.498, 0.128, 0.038) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 | 1.00 / 1.333 | 109.584 | 135.008 |
| push_through_channel | push | 1.00 / step_budget | (0.498, 0.128, 0.038)→(0.498, -0.032, 0.037) | (0.502, 0.098, 0.034)→(0.498, -0.050, 0.035) | 0.178→0.035 | 1.00 / 4.333 | 133.298 | 168.249 |
| retract_from_channel | retract | 1.00 / step_budget | (0.498, -0.032, 0.037)→(0.496, -0.076, 0.081) | (0.498, -0.050, 0.035)→(0.502, -0.068, 0.025) | 0.035→0.021 | 1.00 / 2.000 | 0.812 | 65.961 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.972
- phase_score: 0.373
- phase_breakdown.approach_score: 0.169
- phase_breakdown.push_score: 0.316
- phase_breakdown.contact_score: 0.746

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.613
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.972
- **Median Q (composite search score)**: 0.352
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.292


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `474e87cb3f7f98c9c8d99c8760356b7c026b70b97898f68d5a6c39ba94bca956`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a79e5fd8fc80d9ecadd30a274b12d8d7e7d0841df5ca68ae512c46dc86b114e6`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3785,"average_solve_count":214.0,"average_success_count":214.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_peg.speed":0.07321,"push_through_channel.push_distance":0.18415,"push_through_channel.push_speed":0.03108},"optimized_scores":{"best_composite_score":0.40261,"best_fitness_score":0.61261,"best_task_score":0.97224},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":339.0,"contact_point_centroid":[0.54322,0.05745,0.05999],"force_p95":110.64946,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":119.41511,"mean_force":97.38716,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4988,0.05545,0.03543]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.54373,-0.01974,0.05997],"force_p95":55.23835,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":55.85341,"mean_force":50.22727,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49961,-0.02293,0.03543]},{"body_a":"attachment","body_b":"peg","contact_count":227.0,"contact_point_centroid":[0.50263,0.06127,0.04214],"force_p95":24.8472,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.34828,"mean_force":5.02591,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49867,0.07285,0.03546]},{"body_a":"attachment","body_b":"peg","contact_count":315.0,"contact_point_centroid":[0.49724,-0.05828,0.05559],"force_p95":29.82677,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.90876,"mean_force":13.50152,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49676,-0.0465,0.05556]},{"body_a":"peg","body_b":"channel_base_body","contact_count":374.0,"contact_point_centroid":[0.5011,0.01553,0.00955],"force_p95":22.34277,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.64878,"mean_force":3.37303,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49885,0.0563,0.03546]},{"body_a":"peg","body_b":"channel_base_body","contact_count":228.0,"contact_point_centroid":[0.49331,-0.10031,0.04545],"force_p95":27.79637,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.76248,"mean_force":15.36508,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49666,-0.05673,0.06556]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":300.0,"contact_point_centroid":[0.47491,-0.0758,0.04833],"force_p95":8.06565,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.72783,"mean_force":3.25187,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49697,-0.04525,0.05463]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":101.0,"contact_point_centroid":[0.47482,-0.03469,0.03514],"force_p95":3.36586,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.05038,"mean_force":0.82509,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49944,-0.00305,0.03548]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":175.0,"contact_point_centroid":[0.52519,0.06571,0.0208],"force_p95":5.1973,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.24728,"mean_force":1.04383,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4984,0.09476,0.03543]},{"body_a":"peg","body_b":"channel_base_body","contact_count":247.0,"contact_point_centroid":[0.4942,-0.06819,0.00976],"force_p95":4.56633,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.60054,"mean_force":1.33993,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.4966,-0.04545,0.05344]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":10.0,"contact_point_centroid":[0.5252,-0.09464,0.02544],"force_p95":5.29068,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.36298,"mean_force":1.90669,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49641,-0.07483,0.08095]},{"body_a":"peg","body_b":"channel_base_body","contact_count":534.0,"contact_point_centroid":[0.50361,0.11166,0.00937],"force_p95":0.61005,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55941,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.50225,0.17649,0.21109]},{"body_a":"peg","body_b":"channel_base_body","contact_count":435.0,"contact_point_centroid":[0.50368,0.11174,0.00939],"force_p95":0.60131,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64005,"mean_force":0.54524,"phase_index":1.0,"phase_name":"descend_behind_peg","phase_type":"descend","tcp_position_centroid":[0.5017,0.14788,0.08144]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.49974,0.1994,0.29896]}],"total_contact_groups":14},"final_pose_error":0.01045,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50444,-0.07227,0.02527],"final_tcp_position":[0.4964,-0.07533,0.08137],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":119.41511,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":556.0,"n_steps_budget":1000.0,"object_pos_end":[0.50376,0.1118,0.03382],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19194,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.53576,"phase_name":"approach_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":550.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach","tcp_end":[0.50604,0.15455,0.12868],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10407,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":435.0,"n_steps_budget":630.0,"object_pos_end":[0.50371,0.11175,0.03376],"object_pos_start":[0.50376,0.1118,0.03382],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19194,"object_z_max":0.03387,"peak_contact_force":0.57909,"phase_name":"descend_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":435.0,"raw_peak_contact_force":0.64005,"subtask_id":"contact","tcp_end":[0.49983,0.1418,0.03685],"tcp_start":[0.50604,0.15455,0.12868],"tcp_to_object_dist_end":0.03045,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":604.0,"n_steps_budget":1000.0,"object_pos_end":[0.49264,-0.05368,0.03819],"object_pos_start":[0.50371,0.11175,0.03376],"object_to_goal_dist_end":0.02739,"object_to_goal_dist_start":0.19189,"object_z_max":0.04073,"peak_contact_force":117.29983,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1216.0,"raw_peak_contact_force":119.41511,"subtask_id":"push","tcp_end":[0.49965,-0.02261,0.03545],"tcp_start":[0.49983,0.1418,0.03685],"tcp_to_object_dist_end":0.03196,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":498.0,"n_steps_budget":600.0,"object_pos_end":[0.50444,-0.07227,0.02527],"object_pos_start":[0.49264,-0.05368,0.03819],"object_to_goal_dist_end":0.01722,"object_to_goal_dist_start":0.02739,"object_z_max":0.0513,"peak_contact_force":0.50962,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1104.0,"raw_peak_contact_force":55.85341,"tcp_end":[0.4964,-0.07533,0.08137],"tcp_start":[0.49965,-0.02261,0.03545],"tcp_to_object_dist_end":0.05675,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3ca2e925d364d2c0fe81fb71ee31d40f947a20e349a0720e1c44a2dd2bc628da`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4375,"average_solve_count":192.0,"average_success_count":192.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_peg.speed":0.07144,"push_through_channel.push_distance":0.15862,"push_through_channel.push_speed":0.03409},"optimized_scores":{"best_composite_score":0.31795,"best_fitness_score":0.52795,"best_task_score":0.88655},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":525.0,"contact_point_centroid":[0.5367,0.0766,0.05998],"force_p95":130.06703,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":133.94889,"mean_force":115.54682,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49134,0.07635,0.03575]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.53627,0.01419,0.05999],"force_p95":78.12542,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":81.52855,"mean_force":55.0553,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49199,0.01,0.03593]},{"body_a":"peg","body_b":"channel_base_body","contact_count":584.0,"contact_point_centroid":[0.50131,0.03353,0.00963],"force_p95":59.31735,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":66.57681,"mean_force":10.84945,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49143,0.07061,0.03577]},{"body_a":"attachment","body_b":"peg","contact_count":366.0,"contact_point_centroid":[0.49698,0.04796,0.03708],"force_p95":60.51441,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":66.06731,"mean_force":19.81661,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49157,0.05803,0.03579]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":182.0,"contact_point_centroid":[0.47478,0.06356,0.03551],"force_p95":23.7237,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":52.98505,"mean_force":4.20161,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4911,0.09533,0.03579]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":250.0,"contact_point_centroid":[0.52524,0.00554,0.02801],"force_p95":29.142,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.58312,"mean_force":15.54568,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49196,0.03078,0.03591]},{"body_a":"peg","body_b":"link7","contact_count":214.0,"contact_point_centroid":[0.51696,-0.00299,0.06917],"force_p95":28.46176,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.65678,"mean_force":9.01681,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49199,0.02595,0.03591]},{"body_a":"attachment","body_b":"peg","contact_count":184.0,"contact_point_centroid":[0.49853,-0.01069,0.03759],"force_p95":22.04823,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.281,"mean_force":10.85666,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.4903,-0.00329,0.04114]},{"body_a":"peg","body_b":"channel_base_body","contact_count":583.0,"contact_point_centroid":[0.50085,-0.04789,0.00874],"force_p95":12.06812,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.22784,"mean_force":3.09844,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49231,-0.0337,0.05809]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":188.0,"contact_point_centroid":[0.52512,-0.02293,0.02676],"force_p95":11.60694,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.52421,"mean_force":7.51623,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49029,-0.00396,0.04146]},{"body_a":"peg","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.51578,-0.0207,0.06983],"force_p95":7.99142,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.53068,"mean_force":3.61764,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49186,0.00954,0.03608]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":10.0,"contact_point_centroid":[0.47498,-0.08183,0.02431],"force_p95":8.74128,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.82194,"mean_force":2.84036,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49465,-0.0622,0.07464]},{"body_a":"peg","body_b":"channel_base_body","contact_count":531.0,"contact_point_centroid":[0.49612,0.11885,0.00947],"force_p95":0.60144,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.92282,"mean_force":0.54598,"phase_index":1.0,"phase_name":"descend_behind_peg","phase_type":"descend","tcp_position_centroid":[0.48641,0.15451,0.0797]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.49558,0.13694,0.04497],"force_p95":2.5951,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.6799,"mean_force":1.73403,"phase_index":1.0,"phase_name":"descend_behind_peg","phase_type":"descend","tcp_position_centroid":[0.49108,0.14884,0.0358]},{"body_a":"peg","body_b":"channel_base_body","contact_count":515.0,"contact_point_centroid":[0.49622,0.11904,0.00939],"force_p95":0.61576,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55806,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.49113,0.17981,0.21114]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.49943,0.19918,0.29774]}],"total_contact_groups":16},"final_pose_error":0.01087,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49357,-0.05751,0.02434],"final_tcp_position":[0.4958,-0.07419,0.08183],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":133.94889,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":540.0,"n_steps_budget":1000.0,"object_pos_end":[0.49605,0.11911,0.03388],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19924,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.58031,"phase_name":"approach_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":539.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48416,0.16125,0.12944],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10512,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":531.0,"n_steps_budget":630.0,"object_pos_end":[0.49602,0.11884,0.03415],"object_pos_start":[0.49605,0.11911,0.03388],"object_to_goal_dist_end":0.19896,"object_to_goal_dist_start":0.19924,"object_z_max":0.03433,"peak_contact_force":0.49613,"phase_name":"descend_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":534.0,"raw_peak_contact_force":2.92282,"subtask_id":"contact","tcp_end":[0.49113,0.14875,0.03515],"tcp_start":[0.48416,0.16125,0.12944],"tcp_to_object_dist_end":0.03033,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":722.0,"n_steps_budget":1000.0,"object_pos_end":[0.50762,-0.02023,0.04013],"object_pos_start":[0.49602,0.11884,0.03415],"object_to_goal_dist_end":0.06026,"object_to_goal_dist_start":0.19896,"object_z_max":0.04129,"peak_contact_force":113.88324,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2121.0,"raw_peak_contact_force":133.94889,"subtask_id":"push","tcp_end":[0.49199,0.01009,0.03593],"tcp_start":[0.49113,0.14875,0.03515],"tcp_to_object_dist_end":0.03436,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.49357,-0.05751,0.02434],"object_pos_start":[0.50762,-0.02023,0.04013],"object_to_goal_dist_end":0.02815,"object_to_goal_dist_start":0.06026,"object_z_max":0.04095,"peak_contact_force":0.59848,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":979.0,"raw_peak_contact_force":81.52855,"tcp_end":[0.4958,-0.07419,0.08183],"tcp_start":[0.49199,0.01009,0.03593],"tcp_to_object_dist_end":0.0599,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f85f1938a541e3d507519c8f918b8ca98f1f9baf6ab2f6f3ba2c32478e079e47`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36207,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_peg.speed":0.08186,"push_through_channel.push_distance":0.19983,"push_through_channel.push_speed":0.05},"optimized_scores":{"best_composite_score":0.35209,"best_fitness_score":0.56209,"best_task_score":0.35912},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":48.0,"contact_point_centroid":[0.52513,0.09483,0.05994],"force_p95":368.79019,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":401.46023,"mean_force":288.48641,"phase_index":1.0,"phase_name":"descend_behind_peg","phase_type":"descend","tcp_position_centroid":[0.50474,0.09476,0.04342]},{"body_a":"channel_base_body","body_b":"link7","contact_count":58.0,"contact_point_centroid":[0.55153,-0.1,0.06498],"force_p95":207.57775,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":251.38153,"mean_force":121.44638,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.5025,-0.0803,0.04023]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":185.0,"contact_point_centroid":[0.52501,-0.04955,0.06],"force_p95":157.05229,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":205.51119,"mean_force":102.82121,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50276,-0.04966,0.04064]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,-0.08356,0.06],"force_p95":60.50001,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":60.50001,"mean_force":60.50001,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.50263,-0.08364,0.0406]},{"body_a":"peg","body_b":"channel_base_body","contact_count":499.0,"contact_point_centroid":[0.49586,-0.03899,0.00922],"force_p95":47.72937,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.36392,"mean_force":22.8592,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50217,-0.0209,0.04003]},{"body_a":"attachment","body_b":"peg","contact_count":468.0,"contact_point_centroid":[0.50106,-0.02955,0.04255],"force_p95":55.10787,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.19701,"mean_force":28.38643,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50217,-0.02399,0.04003]},{"body_a":"channel_base_body","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.55109,-0.1,0.06498],"force_p95":43.16499,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":43.3652,"mean_force":39.85934,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.50256,-0.08382,0.04058]},{"body_a":"peg","body_b":"channel_base_body","contact_count":171.0,"contact_point_centroid":[0.48878,-0.10028,0.02119],"force_p95":27.56705,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.12299,"mean_force":10.11109,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50251,-0.07121,0.04021]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":356.0,"contact_point_centroid":[0.47479,-0.04915,0.02566],"force_p95":27.49444,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.86392,"mean_force":16.10528,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50236,-0.04261,0.04017]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":33.0,"contact_point_centroid":[0.4747,-0.0751,0.02638],"force_p95":21.46217,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.74375,"mean_force":8.47059,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.50163,-0.08374,0.04198]},{"body_a":"attachment","body_b":"peg","contact_count":17.0,"contact_point_centroid":[0.49986,-0.07235,0.04228],"force_p95":19.38541,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.4518,"mean_force":8.96001,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.50217,-0.08388,0.04111]},{"body_a":"peg","body_b":"channel_base_body","contact_count":422.0,"contact_point_centroid":[0.50137,-0.07443,0.00826],"force_p95":9.3691,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.86281,"mean_force":1.38286,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49786,-0.08148,0.06085]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":22.0,"contact_point_centroid":[0.52503,-0.0697,0.02423],"force_p95":9.98083,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.08878,"mean_force":5.72288,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49664,-0.0802,0.07613]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":39.0,"contact_point_centroid":[0.52513,0.03634,0.03149],"force_p95":5.59752,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.74536,"mean_force":1.07158,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50145,0.06649,0.03961]},{"body_a":"peg","body_b":"channel_base_body","contact_count":172.0,"contact_point_centroid":[0.4937,-0.10003,0.03648],"force_p95":2.71054,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.38691,"mean_force":0.41717,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49839,-0.0819,0.05637]},{"body_a":"peg","body_b":"channel_base_body","contact_count":621.0,"contact_point_centroid":[0.50581,0.06297,0.00936],"force_p95":0.56101,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56835,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.51167,0.15259,0.20873]}],"total_contact_groups":18},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50714,-0.07478,0.02455],"final_tcp_position":[0.49645,-0.07987,0.08071],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":401.46023,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":649.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.06295,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.55196,"phase_name":"approach_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":655.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach","tcp_end":[0.52437,0.10851,0.12622],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10467,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":403.0,"n_steps_budget":630.0,"object_pos_end":[0.50595,0.06303,0.03381],"object_pos_start":[0.50596,0.06295,0.03381],"object_to_goal_dist_end":0.14328,"object_to_goal_dist_start":0.14321,"object_z_max":0.03381,"peak_contact_force":327.67678,"phase_name":"descend_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":451.0,"raw_peak_contact_force":401.46023,"subtask_id":"contact","tcp_end":[0.50426,0.09475,0.04313],"tcp_start":[0.52437,0.10851,0.12622],"tcp_to_object_dist_end":0.03311,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":607.0,"n_steps_budget":1000.0,"object_pos_end":[0.49227,-0.07544,0.0259],"object_pos_start":[0.50595,0.06303,0.03381],"object_to_goal_dist_end":0.01672,"object_to_goal_dist_start":0.14328,"object_z_max":0.04094,"peak_contact_force":168.70987,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1776.0,"raw_peak_contact_force":251.38153,"subtask_id":"push","tcp_end":[0.50263,-0.08364,0.0406],"tcp_start":[0.50426,0.09475,0.04313],"tcp_to_object_dist_end":0.01977,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":422.0,"n_steps_budget":600.0,"object_pos_end":[0.50714,-0.07478,0.02455],"object_pos_start":[0.49227,-0.07544,0.0259],"object_to_goal_dist_end":0.0178,"object_to_goal_dist_start":0.01672,"object_z_max":0.02674,"peak_contact_force":1.32791,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":670.0,"raw_peak_contact_force":60.50001,"tcp_end":[0.49645,-0.07987,0.08071],"tcp_start":[0.50263,-0.08364,0.0406],"tcp_to_object_dist_end":0.0574,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```