## Search State

- **Seed**: 2
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.0027 | 0.27 | ❌ rejected |
| 12 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.0027 | 0.28 | ❌ rejected |
| 11 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.1098 | 0.00 | ❌ rejected |
| 10 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.1448 | 0.00 | ❌ rejected |
| 9 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.1981 | 0.27 | ❌ rejected |

**Proposal policy**: task_score is 0.27 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`
- Frozen object start: [0.48092897073994534, 0.06387929147312987, 0.04]
- Frozen task target: [0.48092897073994534, -0.09612070852687013, 0.04]
- Goal object position: (0.48092897073994534, -0.09612070852687013, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48092897073994534, 0.06387929147312987, 0.04)
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
  frozen_object_start: [0.4809, 0.0639, 0.04]
  frozen_task_target: [0.4809, -0.0961, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48092897073994534, 0.06387929147312987, 0.04]}
  frozen_targets: {'channel_exit': [0.48092897073994534, -0.09612070852687013, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7

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

## Current Skill (Q=-0.003) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.04
    - 0.07
    orientation:
      mode: none
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.02
    - 0.0
    orientation:
      mode: none
  parameters:
    contact_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_made
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: continue
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
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.07]
  - orientation: mode=none
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0]
  - orientation: mode=none
  - parameter_bindings:
    - contact_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_made, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=1.0
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=2, strategy=reduce_speed

## Design Metrics

- **Composite score**: -0.003
- **task_score** (E): 0.266
- **fitness_score**: 0.227  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2044 |
| contact_1 | 1.00 | 1.00 | 0.0788 |
| push_1 | 0.00 | 1.00 | 0.0501 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.491, 0.113, 0.118) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.543 | 3.659 |
| contact_1 | contact | 1.00 / step_budget | (0.491, 0.113, 0.118)→(0.495, 0.092, 0.044) | (0.498, 0.068, 0.034)→(0.500, 0.063, 0.035) | 0.148→0.143 | 1.00 / 2.000 | 112.315 | 216.122 |
| push_1 | push | 0.00 / step_budget | (0.495, 0.092, 0.044)→(0.522, 0.076, 0.075) | (0.500, 0.063, 0.035)→(0.496, -0.028, 0.027) | 0.143→0.054 | 1.00 / 2.667 | 385.405 | 826.530 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.734
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.474
- phase_score: 0.232
- phase_breakdown.push_score: 0.038
- phase_breakdown.approach_score: 0.209
- phase_breakdown.contact_score: 0.840

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.329
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.474
- **Median Q (composite search score)**: -0.011
- **K-run variance**: 0.0064
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.421


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `6269840a353345700ffa70ea476a3ad730b138bf2ec3c52304c054f0e194e023`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a2936262b79fcd5a49fda15d77b54223f43c58bfee2e71dc505f8a2f79369706`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0,"average_solve_count":184.0,"average_success_count":184.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06265,"contact_1.contact_speed":0.0258,"push_1.push_depth":0.10186,"push_1.push_speed":0.04507},"optimized_scores":{"best_composite_score":0.09921,"best_fitness_score":0.32921,"best_task_score":0.47429},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":973.0,"contact_point_centroid":[0.52623,0.11896,0.05993],"force_p95":318.43739,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":803.64102,"mean_force":280.46188,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51809,0.0742,0.08466]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.49973,0.07036,0.0489],"force_p95":72.63817,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":82.53078,"mean_force":19.1673,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49318,0.08133,0.03791]},{"body_a":"peg","body_b":"channel_base_body","contact_count":947.0,"contact_point_centroid":[0.49709,-0.0468,0.00847],"force_p95":0.7764,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.0546,"mean_force":0.83931,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51857,0.07425,0.08591]},{"body_a":"peg","body_b":"channel_base_body","contact_count":305.0,"contact_point_centroid":[0.49621,0.06026,0.00946],"force_p95":0.88264,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.48973,"mean_force":1.12031,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48237,0.09866,0.08055]},{"body_a":"attachment","body_b":"peg","contact_count":29.0,"contact_point_centroid":[0.49241,0.07756,0.05126],"force_p95":16.12413,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.09533,"mean_force":6.36898,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48771,0.08898,0.04827]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47494,-0.03158,0.03682],"force_p95":8.14975,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.47728,"mean_force":1.98818,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5172,0.07215,0.08418]},{"body_a":"peg","body_b":"channel_base_body","contact_count":636.0,"contact_point_centroid":[0.49529,0.06384,0.00937],"force_p95":0.56793,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55893,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4884,0.15334,0.20495]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":31.0,"contact_point_centroid":[0.5261,0.01071,0.03082],"force_p95":1.72118,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.07096,"mean_force":0.60221,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50302,0.07203,0.05142]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49928,0.19861,0.29743]}],"total_contact_groups":9},"final_pose_error":0.13155,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49465,-0.05351,0.02414],"final_tcp_position":[0.52201,0.076,0.08514],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":803.64102,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":663.0,"n_steps_budget":1000.0,"object_pos_end":[0.49522,0.06369,0.03396],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14389,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54006,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":664.0,"raw_peak_contact_force":2.44546,"subtask_id":"approach","tcp_end":[0.47895,0.10956,0.11798],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0971,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":316.0,"n_steps_budget":1000.0,"object_pos_end":[0.4979,0.05832,0.03579],"object_pos_start":[0.49522,0.06369,0.03396],"object_to_goal_dist_end":0.1384,"object_to_goal_dist_start":0.14389,"object_z_max":0.03704,"peak_contact_force":1.81506,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":334.0,"raw_peak_contact_force":17.48973,"subtask_id":"contact","tcp_end":[0.48904,0.08687,0.0411],"tcp_start":[0.47895,0.10956,0.11798],"tcp_to_object_dist_end":0.03036,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49465,-0.05351,0.02414],"object_pos_start":[0.4979,0.05832,0.03579],"object_to_goal_dist_end":0.03133,"object_to_goal_dist_start":0.1384,"object_z_max":0.04484,"peak_contact_force":275.19791,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1989.0,"raw_peak_contact_force":803.64102,"subtask_id":"push","tcp_end":[0.52201,0.076,0.08514],"tcp_start":[0.48904,0.08687,0.0411],"tcp_to_object_dist_end":0.14575,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `78f29ebb38dd2df9149fb0cd7c7c33d55e802bb94eee599b284bb0b197a04fb7`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.66942,"average_solve_count":242.0,"average_success_count":242.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.0533,"contact_1.contact_speed":0.01193,"push_1.push_depth":0.11931,"push_1.push_speed":0.07957},"optimized_scores":{"best_composite_score":-0.01075,"best_fitness_score":0.21925,"best_task_score":0.25274},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":977.0,"contact_point_centroid":[0.52595,0.11878,0.05993],"force_p95":322.02667,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":772.55456,"mean_force":290.76767,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52246,0.06722,0.09063]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":31.0,"contact_point_centroid":[0.47496,0.09389,0.05993],"force_p95":273.60606,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":280.20515,"mean_force":222.9472,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48315,0.08664,0.05589]},{"body_a":"peg","body_b":"channel_base_body","contact_count":922.0,"contact_point_centroid":[0.49411,-0.05821,0.0094],"force_p95":0.64379,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":114.07722,"mean_force":0.89717,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52378,0.06752,0.09289]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.50085,0.06627,0.05551],"force_p95":109.07559,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":112.54082,"mean_force":31.79006,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4914,0.07701,0.0379]},{"body_a":"peg","body_b":"channel_base_body","contact_count":368.0,"contact_point_centroid":[0.49493,0.05536,0.00947],"force_p95":1.75016,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.72265,"mean_force":0.86709,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47499,0.09352,0.07892]},{"body_a":"attachment","body_b":"peg","contact_count":36.0,"contact_point_centroid":[0.49079,0.0736,0.05467],"force_p95":11.70673,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.62361,"mean_force":3.53892,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48503,0.08497,0.05022]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":54.0,"contact_point_centroid":[0.47454,-0.04936,0.04417],"force_p95":4.40784,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.38681,"mean_force":1.04603,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51171,0.06097,0.08282]},{"body_a":"peg","body_b":"channel_base_body","contact_count":663.0,"contact_point_centroid":[0.4944,0.05899,0.00936],"force_p95":0.56071,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56827,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48161,0.15075,0.20456]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49893,0.1982,0.29656]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":52.0,"contact_point_centroid":[0.52695,0.00261,0.04477],"force_p95":1.89276,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.55558,"mean_force":0.64247,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50032,0.0651,0.05267]},{"body_a":"peg","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.52657,0.04354,0.07045],"force_p95":0.87023,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.88285,"mean_force":0.75671,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4951,0.07088,0.03688]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.475,0.05483,0.06],"force_p95":0.21204,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21204,"mean_force":0.21204,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48627,0.08537,0.05136]}],"total_contact_groups":12},"final_pose_error":0.15123,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49342,-0.05993,0.0338],"final_tcp_position":[0.53046,0.06991,0.09226],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":772.55456,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":692.0,"n_steps_budget":1000.0,"object_pos_end":[0.49405,0.05908,0.03389],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13934,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54201,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":698.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach","tcp_end":[0.46579,0.10481,0.1179],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09974,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":378.0,"n_steps_budget":1000.0,"object_pos_end":[0.49733,0.05316,0.03517],"object_pos_start":[0.49405,0.05908,0.03389],"object_to_goal_dist_end":0.13328,"object_to_goal_dist_start":0.13934,"object_z_max":0.03703,"peak_contact_force":0.7266,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":436.0,"raw_peak_contact_force":280.20515,"subtask_id":"contact","tcp_end":[0.48763,0.08212,0.04066],"tcp_start":[0.46579,0.10481,0.1179],"tcp_to_object_dist_end":0.03102,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49342,-0.05993,0.0338],"object_pos_start":[0.49733,0.05316,0.03517],"object_to_goal_dist_end":0.02201,"object_to_goal_dist_start":0.13328,"object_z_max":0.05631,"peak_contact_force":317.03824,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2016.0,"raw_peak_contact_force":772.55456,"subtask_id":"push","tcp_end":[0.53046,0.06991,0.09226],"tcp_start":[0.48763,0.08212,0.04066],"tcp_to_object_dist_end":0.14714,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ecba62e37d233197bb248f7fe6e722b45204af5e83240a6f27138a89bcccfe42`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43871,"average_solve_count":155.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06639,"contact_1.contact_speed":0.03409,"push_1.push_depth":0.15832,"push_1.push_speed":0.09961},"optimized_scores":{"best_composite_score":-0.09653,"best_fitness_score":0.13347,"best_task_score":0.07245},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":206.0,"contact_point_centroid":[0.52855,0.1199,0.05989],"force_p95":414.65041,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":903.39475,"mean_force":151.96729,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50608,0.0854,0.04789]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":599.0,"contact_point_centroid":[0.47495,0.11991,0.05556],"force_p95":620.36596,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":662.51829,"mean_force":495.48979,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51325,0.08084,0.04874]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":557.0,"contact_point_centroid":[0.52512,0.08259,0.0488],"force_p95":402.79554,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":478.78914,"mean_force":353.03356,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51324,0.08132,0.0486]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":227.0,"contact_point_centroid":[0.52504,0.10791,0.05998],"force_p95":335.34286,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":350.67231,"mean_force":326.84969,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50863,0.10787,0.05234]},{"body_a":"world","body_b":"link7","contact_count":863.0,"contact_point_centroid":[0.49662,0.1454,-7e-05],"force_p95":271.87564,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":308.95345,"mean_force":205.07012,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51191,0.08129,0.04885]},{"body_a":"peg","body_b":"channel_base_body","contact_count":434.0,"contact_point_centroid":[0.50379,0.07103,0.00964],"force_p95":3.39078,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":63.90045,"mean_force":1.93741,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51382,0.11219,0.0687]},{"body_a":"attachment","body_b":"peg","contact_count":145.0,"contact_point_centroid":[0.50761,0.09613,0.05249],"force_p95":28.64025,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.61615,"mean_force":4.40957,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50837,0.10794,0.05208]},{"body_a":"attachment","body_b":"peg","contact_count":19.0,"contact_point_centroid":[0.50172,0.09449,0.04982],"force_p95":49.19034,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.10128,"mean_force":11.90512,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49675,0.10344,0.04712]},{"body_a":"peg","body_b":"channel_base_body","contact_count":977.0,"contact_point_centroid":[0.50109,0.03365,0.00838],"force_p95":0.72446,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.88185,"mean_force":0.81898,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51008,0.08343,0.0483]},{"body_a":"peg","body_b":"channel_base_body","contact_count":644.0,"contact_point_centroid":[0.50577,0.08089,0.00936],"force_p95":0.55568,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57046,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5144,0.16118,0.20393]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49997,0.19837,0.29616]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":39.0,"contact_point_centroid":[0.52519,0.07056,0.04473],"force_p95":1.47775,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.8582,"mean_force":0.38934,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49618,0.10196,0.04407]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.47499,0.00765,0.02424],"force_p95":0.43623,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.439,"mean_force":0.41128,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5117,0.07939,0.05047]}],"total_contact_groups":13},"final_pose_error":0.16339,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50031,0.0286,0.02417],"final_tcp_position":[0.51333,0.0828,0.04638],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":903.39475,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":673.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54612,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":680.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach","tcp_end":[0.52972,0.1252,0.11672],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.097,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":436.0,"n_steps_budget":1000.0,"object_pos_end":[0.50548,0.07829,0.03536],"object_pos_start":[0.50597,0.08086,0.03378],"object_to_goal_dist_end":0.15845,"object_to_goal_dist_start":0.16109,"object_z_max":0.03899,"peak_contact_force":334.40324,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":806.0,"raw_peak_contact_force":350.67231,"subtask_id":"contact","tcp_end":[0.50745,0.10785,0.05018],"tcp_start":[0.52972,0.1252,0.11672],"tcp_to_object_dist_end":0.03313,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50031,0.0286,0.02417],"object_pos_start":[0.50548,0.07829,0.03536],"object_to_goal_dist_end":0.10975,"object_to_goal_dist_start":0.15845,"object_z_max":0.04077,"peak_contact_force":563.97866,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3262.0,"raw_peak_contact_force":903.39475,"subtask_id":"push","tcp_end":[0.51333,0.0828,0.04638],"tcp_start":[0.50745,0.10785,0.05018],"tcp_to_object_dist_end":0.06,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```