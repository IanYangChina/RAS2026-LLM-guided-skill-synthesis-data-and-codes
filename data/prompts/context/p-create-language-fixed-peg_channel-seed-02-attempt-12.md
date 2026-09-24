## Search State

- **Seed**: 2
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.0027 | 0.28 | ❌ rejected |
| 11 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.1098 | 0.00 | ❌ rejected |
| 10 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.1448 | 0.00 | ❌ rejected |
| 9 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.1981 | 0.27 | ❌ rejected |
| 8 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.0068 | 0.29 | ✅ accepted |

**Proposal policy**: task_score is 0.28 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.003) — your mutation base

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

- **Composite score**: 0.003
- **task_score** (E): 0.279
- **fitness_score**: 0.233  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2044 |
| contact_1 | 1.00 | 1.00 | 0.0789 |
| push_1 | 0.00 | 1.00 | 0.0529 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.491, 0.113, 0.118) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.546 | 3.659 |
| contact_1 | contact | 1.00 / step_budget | (0.491, 0.113, 0.118)→(0.495, 0.092, 0.044) | (0.498, 0.068, 0.034)→(0.500, 0.063, 0.035) | 0.148→0.143 | 1.00 / 1.667 | 111.973 | 212.845 |
| push_1 | push | 0.00 / step_budget | (0.495, 0.092, 0.044)→(0.523, 0.074, 0.077) | (0.500, 0.063, 0.035)→(0.498, -0.021, 0.031) | 0.143→0.062 | 1.00 / 2.667 | 371.971 | 835.869 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.781
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.535
- phase_score: 0.233
- phase_breakdown.push_score: 0.038
- phase_breakdown.approach_score: 0.210
- phase_breakdown.contact_score: 0.838

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.353
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.535
- **Median Q (composite search score)**: -0.008
- **K-run variance**: 0.0089
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.341


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.06075,"average_solve_count":214.0,"average_success_count":214.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.03297,"contact_1.contact_speed":0.03464,"push_1.push_depth":0.11444,"push_1.push_speed":0.06122},"optimized_scores":{"best_composite_score":0.12342,"best_fitness_score":0.35342,"best_task_score":0.5345},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":974.0,"contact_point_centroid":[0.52624,0.11898,0.05993],"force_p95":313.91138,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":804.63309,"mean_force":281.19285,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51988,0.0721,0.08622]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.50007,0.0716,0.05113],"force_p95":110.58348,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":126.15729,"mean_force":33.02327,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4924,0.08273,0.03859]},{"body_a":"peg","body_b":"channel_base_body","contact_count":944.0,"contact_point_centroid":[0.49517,-0.05793,0.0082],"force_p95":0.78627,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":126.14587,"mean_force":1.00771,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52047,0.07215,0.08749]},{"body_a":"peg","body_b":"channel_base_body","contact_count":297.0,"contact_point_centroid":[0.49577,0.06048,0.00944],"force_p95":0.97123,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.30742,"mean_force":0.8711,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48251,0.09856,0.08005]},{"body_a":"attachment","body_b":"peg","contact_count":23.0,"contact_point_centroid":[0.49194,0.07789,0.0518],"force_p95":15.71738,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.21447,"mean_force":4.45658,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48757,0.08942,0.04938]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":30.0,"contact_point_centroid":[0.47498,-0.05747,0.02668],"force_p95":9.45452,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.65776,"mean_force":3.26906,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5204,0.07213,0.0883]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":43.0,"contact_point_centroid":[0.52685,0.0103,0.03233],"force_p95":1.85475,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.58172,"mean_force":0.79996,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50216,0.07026,0.05118]},{"body_a":"peg","body_b":"channel_base_body","contact_count":661.0,"contact_point_centroid":[0.49535,0.06379,0.00937],"force_p95":0.56651,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55843,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4884,0.15342,0.2051]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4993,0.19872,0.29766]}],"total_contact_groups":9},"final_pose_error":0.14281,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4935,-0.061,0.02409],"final_tcp_position":[0.52521,0.07377,0.08751],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":804.63309,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":688.0,"n_steps_budget":1000.0,"object_pos_end":[0.49533,0.06387,0.03396],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14408,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.55065,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":689.0,"raw_peak_contact_force":2.44546,"subtask_id":"approach","tcp_end":[0.47893,0.1095,0.11788],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09691,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":305.0,"n_steps_budget":1000.0,"object_pos_end":[0.49751,0.05809,0.03558],"object_pos_start":[0.49533,0.06387,0.03396],"object_to_goal_dist_end":0.13818,"object_to_goal_dist_start":0.14408,"object_z_max":0.037,"peak_contact_force":0.53662,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":320.0,"raw_peak_contact_force":18.30742,"subtask_id":"contact","tcp_end":[0.4891,0.08697,0.04114],"tcp_start":[0.47893,0.1095,0.11788],"tcp_to_object_dist_end":0.03059,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4935,-0.061,0.02409],"object_pos_start":[0.49751,0.05809,0.03558],"object_to_goal_dist_end":0.02562,"object_to_goal_dist_start":0.13818,"object_z_max":0.04157,"peak_contact_force":284.81934,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2000.0,"raw_peak_contact_force":804.63309,"subtask_id":"push","tcp_end":[0.52521,0.07377,0.08751],"tcp_start":[0.4891,0.08697,0.04114],"tcp_to_object_dist_end":0.15228,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.65289,"average_solve_count":242.0,"average_success_count":242.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.05085,"contact_1.contact_speed":0.01528,"push_1.push_depth":0.10656,"push_1.push_speed":0.08068},"optimized_scores":{"best_composite_score":-0.00847,"best_fitness_score":0.22153,"best_task_score":0.25793},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":865.0,"contact_point_centroid":[0.52608,0.11863,0.05993],"force_p95":317.61952,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":772.77004,"mean_force":287.1726,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52245,0.0666,0.09077]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":31.0,"contact_point_centroid":[0.47496,0.0939,0.05993],"force_p95":273.42562,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":280.00111,"mean_force":222.72595,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48315,0.08664,0.0559]},{"body_a":"peg","body_b":"channel_base_body","contact_count":810.0,"contact_point_centroid":[0.49428,-0.0581,0.00943],"force_p95":0.65958,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":114.24362,"mean_force":0.94368,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52395,0.06691,0.09336]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.50085,0.06626,0.05549],"force_p95":109.05661,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":112.6886,"mean_force":31.68261,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4914,0.07701,0.0379]},{"body_a":"peg","body_b":"channel_base_body","contact_count":368.0,"contact_point_centroid":[0.49493,0.05536,0.00947],"force_p95":1.76117,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.56055,"mean_force":0.86527,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47499,0.09353,0.07894]},{"body_a":"attachment","body_b":"peg","contact_count":36.0,"contact_point_centroid":[0.49079,0.07361,0.05468],"force_p95":11.70395,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.46086,"mean_force":3.52022,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48503,0.08497,0.05023]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":101.0,"contact_point_centroid":[0.47473,-0.05422,0.05097],"force_p95":3.37543,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.50661,"mean_force":0.61056,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5166,0.06372,0.08905]},{"body_a":"peg","body_b":"channel_base_body","contact_count":663.0,"contact_point_centroid":[0.4944,0.05899,0.00936],"force_p95":0.56071,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56827,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48162,0.15078,0.20463]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49893,0.19821,0.29659]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":57.0,"contact_point_centroid":[0.52682,-0.00067,0.04546],"force_p95":1.82629,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.54921,"mean_force":0.5962,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50131,0.06469,0.05518]},{"body_a":"peg","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.52663,0.04354,0.07041],"force_p95":0.87164,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.88427,"mean_force":0.75796,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4951,0.07088,0.03688]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.475,0.05486,0.06],"force_p95":0.21211,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21211,"mean_force":0.21211,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48627,0.08537,0.05136]}],"total_contact_groups":12},"final_pose_error":0.13928,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49304,-0.06008,0.03379],"final_tcp_position":[0.53072,0.06862,0.09343],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":772.77004,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":692.0,"n_steps_budget":1000.0,"object_pos_end":[0.49405,0.05908,0.03389],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13934,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54201,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":698.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach","tcp_end":[0.46579,0.10483,0.11793],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09977,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":378.0,"n_steps_budget":1000.0,"object_pos_end":[0.49733,0.05315,0.03517],"object_pos_start":[0.49405,0.05908,0.03389],"object_to_goal_dist_end":0.13327,"object_to_goal_dist_start":0.13934,"object_z_max":0.03704,"peak_contact_force":0.72644,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":436.0,"raw_peak_contact_force":280.00111,"subtask_id":"contact","tcp_end":[0.48763,0.08212,0.04066],"tcp_start":[0.46579,0.10483,0.11793],"tcp_to_object_dist_end":0.03103,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":887.0,"n_steps_budget":1000.0,"object_pos_end":[0.49304,-0.06008,0.03379],"object_pos_start":[0.49733,0.05315,0.03517],"object_to_goal_dist_end":0.02199,"object_to_goal_dist_start":0.13327,"object_z_max":0.05627,"peak_contact_force":299.48489,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1844.0,"raw_peak_contact_force":772.77004,"subtask_id":"push","tcp_end":[0.53072,0.06862,0.09343],"tcp_start":[0.48763,0.08212,0.04066],"tcp_to_object_dist_end":0.14677,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20382,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06692,"contact_1.contact_speed":0.03459,"push_1.push_depth":0.14262,"push_1.push_speed":0.04462},"optimized_scores":{"best_composite_score":-0.10682,"best_fitness_score":0.12318,"best_task_score":0.04425},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":381.0,"contact_point_centroid":[0.5261,0.11993,0.05994],"force_p95":342.96946,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":930.20311,"mean_force":160.98885,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51115,0.08163,0.04984]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":95.0,"contact_point_centroid":[0.47496,0.11994,0.05059],"force_p95":443.18789,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":531.60763,"mean_force":322.83071,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51316,0.07907,0.05062]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":293.0,"contact_point_centroid":[0.52503,0.08071,0.05091],"force_p95":296.41673,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":479.50364,"mean_force":168.00283,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51294,0.07994,0.05062]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":215.0,"contact_point_centroid":[0.52505,0.10768,0.05998],"force_p95":335.43548,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":340.22607,"mean_force":326.79402,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50845,0.10764,0.05193]},{"body_a":"world","body_b":"link7","contact_count":874.0,"contact_point_centroid":[0.49666,0.14928,-7e-05],"force_p95":261.41387,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":281.31077,"mean_force":221.31316,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51039,0.08549,0.05011]},{"body_a":"peg","body_b":"channel_base_body","contact_count":425.0,"contact_point_centroid":[0.50315,0.07129,0.00962],"force_p95":2.51358,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.34749,"mean_force":1.74229,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51384,0.11216,0.06885]},{"body_a":"attachment","body_b":"peg","contact_count":159.0,"contact_point_centroid":[0.50752,0.09585,0.05224],"force_p95":6.53873,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.98944,"mean_force":3.41572,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50829,0.1077,0.05184]},{"body_a":"peg","body_b":"channel_base_body","contact_count":963.0,"contact_point_centroid":[0.50569,0.06317,0.00949],"force_p95":1.64133,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.43558,"mean_force":0.80852,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50845,0.08767,0.04916]},{"body_a":"attachment","body_b":"peg","contact_count":135.0,"contact_point_centroid":[0.5053,0.08684,0.04999],"force_p95":7.34034,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.17025,"mean_force":2.65958,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50658,0.08822,0.04749]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":107.0,"contact_point_centroid":[0.52515,0.06916,0.0378],"force_p95":5.45853,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.37186,"mean_force":1.17843,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50134,0.08981,0.04393]},{"body_a":"peg","body_b":"channel_base_body","contact_count":644.0,"contact_point_centroid":[0.50577,0.08089,0.00936],"force_p95":0.55568,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57046,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5144,0.16118,0.20393]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49997,0.19837,0.29616]}],"total_contact_groups":12},"final_pose_error":0.14474,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.506,0.05687,0.03399],"final_tcp_position":[0.51321,0.07916,0.05057],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":930.20311,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":673.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54612,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":680.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach","tcp_end":[0.52972,0.1252,0.11672],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.097,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":425.0,"n_steps_budget":1000.0,"object_pos_end":[0.50545,0.07805,0.03537],"object_pos_start":[0.50597,0.08086,0.03378],"object_to_goal_dist_end":0.15821,"object_to_goal_dist_start":0.16109,"object_z_max":0.03756,"peak_contact_force":334.65733,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":799.0,"raw_peak_contact_force":340.22607,"subtask_id":"contact","tcp_end":[0.50732,0.10762,0.04989],"tcp_start":[0.52972,0.1252,0.11672],"tcp_to_object_dist_end":0.033,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.506,0.05687,0.03399],"object_pos_start":[0.50545,0.07805,0.03537],"object_to_goal_dist_end":0.13713,"object_to_goal_dist_start":0.15821,"object_z_max":0.03699,"peak_contact_force":531.60763,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2848.0,"raw_peak_contact_force":930.20311,"subtask_id":"push","tcp_end":[0.51321,0.07916,0.05057],"tcp_start":[0.50732,0.10762,0.04989],"tcp_to_object_dist_end":0.0287,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```