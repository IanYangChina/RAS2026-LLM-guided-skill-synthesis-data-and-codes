## Search State

- **Seed**: 7
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → contact → push | arc_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.3374 | 0.57 | ✅ accepted |
| 2 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.3097 | 0.49 | ✅ accepted |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1068 | 0.23 | ❌ rejected |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.3019 | 0.39 | ✅ accepted |

**Proposal policy**: task_score is 0.57 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.337) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.06
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.04
      - 0.12
      default: 0.08
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.01
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 8.0
      default: 3.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.18
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.025
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: push_contact
    when: during_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.06, 0.0]
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.01, 0.0]
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=push_contact, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=reduce_speed

## Design Metrics

- **Composite score**: 0.337
- **task_score** (E): 0.574
- **fitness_score**: 0.606  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.111
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2627 |
| contact_1 | 1.00 | 1.00 | 0.0384 |
| push_1 | 1.00 | 1.00 | 0.1937 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.168, 0.041) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.556 | 2.732 |
| contact_1 | contact | 1.00 / step_budget | (0.505, 0.168, 0.041)→(0.504, 0.131, 0.032) | (0.502, 0.098, 0.034)→(0.504, 0.089, 0.035) | 0.178→0.169 | 1.00 / 2.000 | 9.339 | 10.811 |
| push_1 | push | 1.00 / step_budget | (0.504, 0.131, 0.032)→(0.501, -0.062, 0.030) | (0.504, 0.089, 0.035)→(0.504, -0.089, 0.037) | 0.169→0.013 | 1.00 / 2.000 | 50.793 | 154.869 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.271
- phase_score: 0.633
- phase_breakdown.approach_score: 0.512
- phase_breakdown.contact_score: 0.371
- phase_breakdown.push_score: 0.761

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.791
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.411
- **K-run variance**: 0.0160
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.316


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24138,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.05476,"approach_1.speed":0.12763,"contact_1.contact_force":7.5294,"contact_1.speed":0.03259,"push_1.push_distance":0.17873,"push_1.push_speed":0.04559,"push_1.push_tolerance":0.01862},"optimized_scores":{"best_composite_score":0.41069,"best_fitness_score":0.79069,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":161.0,"contact_point_centroid":[0.50637,-0.10193,0.05986],"force_p95":132.85067,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":133.54589,"mean_force":104.22831,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50149,-0.05937,0.02946]},{"body_a":"attachment","body_b":"peg","contact_count":514.0,"contact_point_centroid":[0.50465,-0.00657,0.05021],"force_p95":131.311,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":133.53244,"mean_force":35.63786,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49971,0.00458,0.02833]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":296.0,"contact_point_centroid":[0.52523,0.01296,0.03069],"force_p95":18.45479,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.06806,"mean_force":2.80455,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49864,0.04173,0.02749]},{"body_a":"peg","body_b":"channel_base_body","contact_count":223.0,"contact_point_centroid":[0.50807,-0.025,0.00987],"force_p95":15.48648,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.70315,"mean_force":4.97728,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49932,0.01753,0.02818]},{"body_a":"peg","body_b":"channel_base_body","contact_count":943.0,"contact_point_centroid":[0.50364,0.10293,0.00958],"force_p95":3.50168,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.07841,"mean_force":1.3572,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50116,0.14983,0.03411]},{"body_a":"attachment","body_b":"peg","contact_count":338.0,"contact_point_centroid":[0.50299,0.12092,0.04195],"force_p95":3.95385,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.69692,"mean_force":2.45014,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50032,0.13282,0.03113]},{"body_a":"peg","body_b":"channel_base_body","contact_count":854.0,"contact_point_centroid":[0.50364,0.11167,0.00936],"force_p95":0.62067,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55455,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50256,0.2206,0.17063]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49997,0.19987,0.29897]}],"total_contact_groups":8},"final_pose_error":0.02346,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50647,-0.08716,0.03518],"final_tcp_position":[0.50225,-0.06217,0.02942],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":133.54589,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":876.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.11184,0.03394],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19197,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.60754,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":870.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach","tcp_end":[0.50596,0.18007,0.04378],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06897,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":979.0,"n_steps_budget":1000.0,"object_pos_end":[0.50532,0.09403,0.03518],"object_pos_start":[0.50373,0.11184,0.03394],"object_to_goal_dist_end":0.17418,"object_to_goal_dist_start":0.19197,"object_z_max":0.03532,"peak_contact_force":2.69446,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1281.0,"raw_peak_contact_force":6.07841,"subtask_id":"contact","tcp_end":[0.49995,0.12358,0.02961],"tcp_start":[0.50596,0.18007,0.04378],"tcp_to_object_dist_end":0.03055,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":664.0,"n_steps_budget":1000.0,"object_pos_end":[0.50647,-0.08716,0.03518],"object_pos_start":[0.50532,0.09403,0.03518],"object_to_goal_dist_end":0.01079,"object_to_goal_dist_start":0.17418,"object_z_max":0.03655,"peak_contact_force":133.54589,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1194.0,"raw_peak_contact_force":133.54589,"subtask_id":"push","tcp_end":[0.50225,-0.06217,0.02942],"tcp_start":[0.49995,0.12358,0.02961],"tcp_to_object_dist_end":0.026,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37838,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.08244,"approach_1.speed":0.14174,"contact_1.contact_force":5.45525,"contact_1.speed":0.02822,"push_1.push_distance":0.1783,"push_1.push_speed":0.05964,"push_1.push_tolerance":0.01812},"optimized_scores":{"best_composite_score":0.15957,"best_fitness_score":0.53957,"best_task_score":0.45032},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":15.0,"contact_point_centroid":[0.47499,0.1027,0.02892],"force_p95":75.10268,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":79.05538,"mean_force":50.62439,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48681,0.10268,0.02692]},{"body_a":"attachment","body_b":"peg","contact_count":685.0,"contact_point_centroid":[0.49892,0.03716,0.05226],"force_p95":54.97258,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.25588,"mean_force":38.19616,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48875,0.04678,0.02787]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":685.0,"contact_point_centroid":[0.52555,0.01891,0.0525],"force_p95":50.17502,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.30669,"mean_force":33.47324,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48882,0.04352,0.02786]},{"body_a":"peg","body_b":"channel_base_body","contact_count":456.0,"contact_point_centroid":[0.50821,0.01831,0.00986],"force_p95":33.34982,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.23017,"mean_force":21.69399,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4885,0.05592,0.02789]},{"body_a":"peg","body_b":"link7","contact_count":333.0,"contact_point_centroid":[0.5205,0.05117,0.06289],"force_p95":17.19499,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.41697,"mean_force":12.88166,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48766,0.0624,0.0275]},{"body_a":"peg","body_b":"channel_base_body","contact_count":982.0,"contact_point_centroid":[0.49662,0.11475,0.00954],"force_p95":2.66715,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.55233,"mean_force":0.88409,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48492,0.1618,0.03322]},{"body_a":"attachment","body_b":"peg","contact_count":202.0,"contact_point_centroid":[0.49365,0.13233,0.04582],"force_p95":2.68306,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.2327,"mean_force":1.84584,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48871,0.14396,0.0311]},{"body_a":"peg","body_b":"channel_base_body","contact_count":889.0,"contact_point_centroid":[0.49615,0.1191,0.00941],"force_p95":0.60781,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55097,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49121,0.24109,0.16805]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50027,0.20007,0.29796]}],"total_contact_groups":9},"final_pose_error":0.018,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50711,-0.07855,0.03665],"final_tcp_position":[0.49494,-0.05119,0.03059],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":79.05538,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":914.0,"n_steps_budget":1000.0,"object_pos_end":[0.49603,0.11898,0.03403],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19911,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.51314,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":913.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48291,0.1882,0.04053],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07075,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49948,0.11042,0.03562],"object_pos_start":[0.49603,0.11898,0.03403],"object_to_goal_dist_end":0.19047,"object_to_goal_dist_start":0.19911,"object_z_max":0.03567,"peak_contact_force":2.51956,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1184.0,"raw_peak_contact_force":3.55233,"subtask_id":"contact","tcp_end":[0.48981,0.1391,0.03059],"tcp_start":[0.48291,0.1882,0.04053],"tcp_to_object_dist_end":0.03068,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":750.0,"n_steps_budget":1000.0,"object_pos_end":[0.50711,-0.07855,0.03665],"object_pos_start":[0.49948,0.11042,0.03562],"object_to_goal_dist_end":0.00799,"object_to_goal_dist_start":0.19047,"object_z_max":0.03773,"peak_contact_force":2.05112,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2174.0,"raw_peak_contact_force":79.05538,"subtask_id":"push","tcp_end":[0.49494,-0.05119,0.03059],"tcp_start":[0.48981,0.1391,0.03059],"tcp_to_object_dist_end":0.03055,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45763,"average_solve_count":118.0,"average_success_count":118.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.08504,"approach_1.speed":0.19984,"contact_1.contact_force":4.79983,"contact_1.speed":0.0284,"push_1.push_distance":0.16599,"push_1.push_speed":0.05931,"push_1.push_tolerance":0.03066},"optimized_scores":{"best_composite_score":0.4418,"best_fitness_score":0.48847,"best_task_score":0.27134},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":418.0,"contact_point_centroid":[0.52504,0.10366,0.05985],"force_p95":218.49628,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":252.00688,"mean_force":163.45229,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51317,0.11025,0.03382]},{"body_a":"attachment","body_b":"peg","contact_count":249.0,"contact_point_centroid":[0.50723,-0.01019,0.04023],"force_p95":136.93286,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":163.52425,"mean_force":21.42828,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50688,0.00131,0.02878]},{"body_a":"peg","body_b":"channel_base_body","contact_count":56.0,"contact_point_centroid":[0.50253,-0.10501,0.02906],"force_p95":155.5228,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":161.04842,"mean_force":91.10452,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50565,-0.06316,0.02945]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.11996,0.0526],"force_p95":22.80309,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":22.80309,"mean_force":22.80309,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52226,0.13188,0.03587]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":5.0,"contact_point_centroid":[0.4748,-0.09752,0.05964],"force_p95":18.3746,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.67748,"mean_force":7.94469,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50622,-0.06969,0.03023]},{"body_a":"peg","body_b":"channel_base_body","contact_count":486.0,"contact_point_centroid":[0.50419,0.04376,0.00945],"force_p95":3.89079,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.59784,"mean_force":1.04644,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51252,0.09884,0.03348]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":48.0,"contact_point_centroid":[0.52509,-0.00741,0.03176],"force_p95":6.89689,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.98172,"mean_force":1.31782,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50713,0.02307,0.02858]},{"body_a":"peg","body_b":"channel_base_body","contact_count":796.0,"contact_point_centroid":[0.50578,0.063,0.00937],"force_p95":0.55629,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56356,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51391,0.21536,0.1533]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50063,0.2002,0.29644]},{"body_a":"peg","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.51386,0.02471,0.06754],"force_p95":0.77147,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.8739,"mean_force":0.31916,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5072,0.05281,0.02784]},{"body_a":"peg","body_b":"channel_base_body","contact_count":36.0,"contact_point_centroid":[0.50719,0.06203,0.00938],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55117,"mean_force":0.54663,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52381,0.1339,0.03726]}],"total_contact_groups":11},"final_pose_error":0.03062,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49853,-0.10156,0.03926],"final_tcp_position":[0.50648,-0.07257,0.03056],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":252.00688,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":824.0,"n_steps_budget":870.0,"object_pos_end":[0.50602,0.06302,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14328,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54859,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":830.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach","tcp_end":[0.52533,0.13616,0.03892],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07582,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":36.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,0.06297,0.03381],"object_pos_start":[0.50602,0.06302,0.03381],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14328,"object_z_max":0.03381,"peak_contact_force":22.80309,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":37.0,"raw_peak_contact_force":22.80309,"subtask_id":"contact","tcp_end":[0.52219,0.13178,0.03581],"tcp_start":[0.52533,0.13616,0.03892],"tcp_to_object_dist_end":0.07073,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":701.0,"n_steps_budget":1000.0,"object_pos_end":[0.49853,-0.10156,0.03926],"object_pos_start":[0.50594,0.06297,0.03381],"object_to_goal_dist_end":0.02162,"object_to_goal_dist_start":0.14323,"object_z_max":0.03994,"peak_contact_force":16.78321,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1270.0,"raw_peak_contact_force":252.00688,"subtask_id":"push","tcp_end":[0.50648,-0.07257,0.03056],"tcp_start":[0.52219,0.13178,0.03581],"tcp_to_object_dist_end":0.03129,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```