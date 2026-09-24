## Search State

- **Seed**: 2
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.1659 | 0.02 | ❌ rejected |
| 6 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.1663 | 0.02 | ✅ accepted |
| 5 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | -0.0803 | 0.02 | ❌ rejected |
| 4 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.2039 | 0.00 | ❌ rejected |
| 3 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.0451 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.02 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.166) — your mutation base

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
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.05
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
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.05
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
    contact_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
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
      mode: keep_current
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
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.07]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.01, 0.0]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.166
- **task_score** (E): 0.017
- **fitness_score**: 0.113  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2041 |
| contact_1 | 1.00 | 1.00 | 0.0599 |
| push_1 | 0.67 | 1.00 | 0.0192 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.492, 0.113, 0.118) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.545 | 3.659 |
| contact_1 | contact | 1.00 / force_exceeded | (0.492, 0.113, 0.118)→(0.491, 0.091, 0.064) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 2.000 | 42.395 | 42.395 |
| push_1 | push | 0.67 / step_budget | (0.491, 0.091, 0.064)→(0.499, 0.081, 0.054) | (0.498, 0.068, 0.034)→(0.499, 0.059, 0.034) | 0.148→0.140 | 1.00 / 3.000 | 277.794 | 320.718 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.139
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.042
- phase_score: 0.179
- phase_breakdown.push_score: 0.041
- phase_breakdown.approach_score: 0.211
- phase_breakdown.contact_score: 0.561

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.124
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.042
- **Median Q (composite search score)**: 0.167
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.492


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.5935,"average_solve_count":246.0,"average_success_count":246.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.03033,"contact_1.contact_force":18.68437,"contact_1.contact_speed":0.00808,"push_1.push_depth":0.02204,"push_1.push_speed":0.02456},"optimized_scores":{"best_composite_score":0.16693,"best_fitness_score":0.11359,"best_task_score":0.01013},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":771.0,"contact_point_centroid":[0.49133,0.1427,-7e-05],"force_p95":335.18705,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":344.19771,"mean_force":282.04147,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49128,0.08073,0.05423]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":896.0,"contact_point_centroid":[0.46217,0.11996,0.04979],"force_p95":157.81549,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":197.54224,"mean_force":128.14846,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49089,0.08063,0.05442]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":40.0,"contact_point_centroid":[0.47499,0.11999,0.05989],"force_p95":92.57605,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":132.73144,"mean_force":65.58957,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48647,0.08456,0.06313]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.475,0.12,0.06],"force_p95":22.38978,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":22.38978,"mean_force":22.38978,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48548,0.08752,0.06599]},{"body_a":"attachment","body_b":"peg","contact_count":55.0,"contact_point_centroid":[0.49493,0.08027,0.04578],"force_p95":12.01076,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.75161,"mean_force":1.77361,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48849,0.0801,0.05585]},{"body_a":"peg","body_b":"channel_base_body","contact_count":956.0,"contact_point_centroid":[0.49649,0.05963,0.00946],"force_p95":0.69674,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.28112,"mean_force":0.62842,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49062,0.08085,0.05495]},{"body_a":"peg","body_b":"channel_base_body","contact_count":748.0,"contact_point_centroid":[0.49527,0.06382,0.00938],"force_p95":0.56471,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55691,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48746,0.16213,0.20984]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50423,0.21548,0.29311]},{"body_a":"peg","body_b":"channel_base_body","contact_count":376.0,"contact_point_centroid":[0.49504,0.064,0.0094],"force_p95":0.55081,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55289,"mean_force":0.54528,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48151,0.09794,0.09107]}],"total_contact_groups":9},"final_pose_error":0.04574,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49657,0.06112,0.03401],"final_tcp_position":[0.49368,0.08161,0.05603],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":344.19771,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":775.0,"n_steps_budget":1000.0,"object_pos_end":[0.49529,0.06372,0.03398],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14392,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54656,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":776.0,"raw_peak_contact_force":2.44546,"subtask_id":"approach","tcp_end":[0.47974,0.10898,0.1183],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09695,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":376.0,"n_steps_budget":1000.0,"object_pos_end":[0.49511,0.06359,0.03402],"object_pos_start":[0.49529,0.06372,0.03398],"object_to_goal_dist_end":0.14379,"object_to_goal_dist_start":0.14392,"object_z_max":0.03402,"peak_contact_force":22.38978,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":377.0,"raw_peak_contact_force":22.38978,"subtask_id":"contact","tcp_end":[0.48551,0.08746,0.06587],"tcp_start":[0.47974,0.10898,0.1183],"tcp_to_object_dist_end":0.04095,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":960.0,"n_steps_budget":1000.0,"object_pos_end":[0.49657,0.06112,0.03401],"object_pos_start":[0.49511,0.06359,0.03402],"object_to_goal_dist_end":0.14129,"object_to_goal_dist_start":0.14379,"object_z_max":0.03615,"peak_contact_force":317.39721,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2718.0,"raw_peak_contact_force":344.19771,"subtask_id":"push","tcp_end":[0.49368,0.08161,0.05603],"tcp_start":[0.48551,0.08746,0.06587],"tcp_to_object_dist_end":0.03022,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.02041,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06107,"contact_1.contact_force":4.08493,"contact_1.contact_speed":0.03623,"push_1.push_depth":0.02015,"push_1.push_speed":0.02558},"optimized_scores":{"best_composite_score":0.1534,"best_fitness_score":0.10007,"best_task_score":0.00038},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":305.0,"contact_point_centroid":[0.48952,0.14411,-8e-05],"force_p95":347.25871,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":348.799,"mean_force":300.0543,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48997,0.081,0.05291]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":844.0,"contact_point_centroid":[0.45786,0.11994,0.05869],"force_p95":238.71061,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":301.41586,"mean_force":159.13437,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48819,0.08053,0.05785]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":367.0,"contact_point_centroid":[0.47497,0.11995,0.05997],"force_p95":196.83967,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":241.66964,"mean_force":140.11707,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4839,0.08095,0.06711]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47499,0.12,0.05995],"force_p95":37.40286,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":37.40286,"mean_force":37.40286,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4773,0.08514,0.07184]},{"body_a":"peg","body_b":"channel_base_body","contact_count":720.0,"contact_point_centroid":[0.49426,0.059,0.00936],"force_p95":0.55963,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.5665,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48113,0.15889,0.20741]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50278,0.22095,0.28777]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49403,0.05899,0.0094],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55392,"mean_force":0.54526,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48708,0.08081,0.05971]},{"body_a":"peg","body_b":"channel_base_body","contact_count":352.0,"contact_point_centroid":[0.49439,0.05894,0.00939],"force_p95":0.55016,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54588,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.471,0.09418,0.09354]}],"total_contact_groups":8},"final_pose_error":0.04668,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49388,0.05876,0.03404],"final_tcp_position":[0.491,0.08117,0.0537],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":348.799,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":749.0,"n_steps_budget":1000.0,"object_pos_end":[0.49406,0.05883,0.03389],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13909,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54447,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":755.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach","tcp_end":[0.46664,0.10424,0.11824],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09964,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":352.0,"n_steps_budget":1000.0,"object_pos_end":[0.49402,0.05913,0.03394],"object_pos_start":[0.49406,0.05883,0.03389],"object_to_goal_dist_end":0.13939,"object_to_goal_dist_start":0.13909,"object_z_max":0.03394,"peak_contact_force":37.40286,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":353.0,"raw_peak_contact_force":37.40286,"subtask_id":"contact","tcp_end":[0.47733,0.08511,0.07174],"tcp_start":[0.46664,0.10424,0.11824],"tcp_to_object_dist_end":0.04881,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49388,0.05876,0.03404],"object_pos_start":[0.49402,0.05913,0.03394],"object_to_goal_dist_end":0.13902,"object_to_goal_dist_start":0.13939,"object_z_max":0.03404,"peak_contact_force":342.99283,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2516.0,"raw_peak_contact_force":348.799,"subtask_id":"push","tcp_end":[0.491,0.08117,0.0537],"tcp_start":[0.47733,0.08511,0.07174],"tcp_to_object_dist_end":0.02995,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.88398,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.04852,"contact_1.contact_force":12.5924,"contact_1.contact_speed":0.03126,"push_1.push_depth":0.129,"push_1.push_speed":0.01339},"optimized_scores":{"best_composite_score":0.17727,"best_fitness_score":0.12394,"best_task_score":0.04183},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":982.0,"contact_point_centroid":[0.51127,0.15068,-5e-05],"force_p95":190.88264,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":269.15776,"mean_force":146.02109,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51107,0.08761,0.053]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":256.0,"contact_point_centroid":[0.525,0.11994,0.06],"force_p95":236.61721,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":264.53593,"mean_force":182.68953,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51196,0.07936,0.05264]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.51131,0.16172,-8e-05],"force_p95":67.39165,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":67.39165,"mean_force":67.39165,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51014,0.0996,0.05406]},{"body_a":"attachment","body_b":"peg","contact_count":431.0,"contact_point_centroid":[0.5059,0.09053,0.05204],"force_p95":2.73319,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.1702,"mean_force":1.39704,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51077,0.09055,0.05315]},{"body_a":"peg","body_b":"channel_base_body","contact_count":958.0,"contact_point_centroid":[0.50521,0.06074,0.00964],"force_p95":2.23005,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.11316,"mean_force":1.04531,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51107,0.08766,0.05301]},{"body_a":"peg","body_b":"channel_base_body","contact_count":731.0,"contact_point_centroid":[0.50575,0.08087,0.00936],"force_p95":0.55291,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.56764,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50994,0.16861,0.2082]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50301,0.22179,0.2872]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":167.0,"contact_point_centroid":[0.52514,0.06759,0.03754],"force_p95":2.31056,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.44224,"mean_force":0.46376,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51104,0.08676,0.05295]},{"body_a":"peg","body_b":"channel_base_body","contact_count":319.0,"contact_point_centroid":[0.50598,0.08093,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54678,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5198,0.11239,0.08559]}],"total_contact_groups":9},"final_pose_error":0.12893,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50637,0.0586,0.03393],"final_tcp_position":[0.5124,0.07929,0.05247],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":269.15776,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":760.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54527,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":767.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach","tcp_end":[0.53032,0.12487,0.11748],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":319.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":67.39165,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":320.0,"raw_peak_contact_force":67.39165,"subtask_id":"contact","tcp_end":[0.51009,0.09954,0.05389],"tcp_start":[0.53032,0.12487,0.11748],"tcp_to_object_dist_end":0.02774,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50637,0.0586,0.03393],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.13888,"object_to_goal_dist_start":0.16112,"object_z_max":0.03581,"peak_contact_force":172.99269,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2794.0,"raw_peak_contact_force":269.15776,"subtask_id":"push","tcp_end":[0.5124,0.07929,0.05247],"tcp_start":[0.51009,0.09954,0.05389],"tcp_to_object_dist_end":0.02842,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```