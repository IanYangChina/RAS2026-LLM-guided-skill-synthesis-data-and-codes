## Search State

- **Seed**: 3
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → align → push → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 7 | 0.0600 | 0.06 | ❌ rejected |
| 9 | approach → push → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.2022 | 0.10 | ✅ accepted |
| 8 | approach → push → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 8 | 0.0435 | 0.00 | ❌ rejected |
| 7 | approach → push → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.2025 | 0.10 | ✅ accepted |
| 6 | approach → push → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 6 | 0.1335 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.06 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`
- Frozen object start: [0.46685193337148995, 0.058944840527687975, 0.04]
- Frozen task target: [0.46685193337148995, -0.10105515947231203, 0.04]
- Goal object position: (0.46685193337148995, -0.10105515947231203, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.46685193337148995, 0.058944840527687975, 0.04)
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
  frozen_object_start: [0.4669, 0.0589, 0.04]
  frozen_task_target: [0.4669, -0.1011, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.46685193337148995, 0.058944840527687975, 0.04]}
  frozen_targets: {'channel_exit': [0.46685193337148995, -0.10105515947231203, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834

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

## Current Skill (Q=0.060) — your mutation base

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
    entity: peg
    offset:
    - 0.0
    - 0.02
    - 0.02
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: engage_contact
  type: push
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.02
    - 0.0
    offset_along_axis:
      distance: 0.02
      axis: channel_axis
      mode: add_to_offset
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    engage_force_threshold:
      type: scalar
      range:
      - 2.0
      - 8.0
      default: 4.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    engage_speed:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: push_through_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
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
      - 0.1
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_max_time:
      type: scalar
      range:
      - 2.0
      - 8.0
      default: 4.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_maintained
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: abort
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.02], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **engage_contact** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], offset_along_axis={axis=channel_axis, distance=0.02, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - engage_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - engage_speed: status=consumed; consumers=generator.speed (replace)
- **push_through_channel** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_max_time: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_maintained, when=during_phase, predicate=contact_detected, on_failure=abort, threshold=1.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.005]

## Design Metrics

- **Composite score**: 0.060
- **task_score** (E): 0.062
- **fitness_score**: 0.137  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2079 |
| align_behind | 1.00 | 1.00 | 0.0564 |
| engage_contact | 1.00 | 1.00 | 0.0000 |
| push_through_channel | 1.00 | 1.00 | 0.0319 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.129, 0.107) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.548 | 3.954 |
| align_behind | align | 1.00 / step_budget | (0.505, 0.129, 0.107)→(0.501, 0.111, 0.057) | (0.502, 0.081, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.162 | 1.00 / 2.000 | 297.032 | 752.781 |
| engage_contact | push | 1.00 / force_exceeded | (0.501, 0.111, 0.057)→(0.501, 0.111, 0.057) | (0.502, 0.081, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.162 | 1.00 / 2.000 | 65.020 | 65.020 |
| push_through_channel | push | 1.00 / time_limit | (0.501, 0.111, 0.057)→(0.505, 0.080, 0.052) | (0.502, 0.081, 0.034)→(0.503, 0.060, 0.035) | 0.162→0.141 | 1.00 / 4.000 | 184.331 | 316.880 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.269
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.145
- phase_score: 0.193
- phase_breakdown.push_score: 0.041
- phase_breakdown.contact_score: 0.589
- phase_breakdown.approach_score: 0.254

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.174
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.145
- **Median Q (composite search score)**: 0.048
- **K-run variance**: 0.0007
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.388


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `cc7283febf3c95cef1fde4c5a16cbcb134186cb6faf3a169717a9aa53375931d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `178d67757a065da6e29d31070e25f6065dc7e42bdbf58dfbff0deec513214033`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.85542,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.align_speed":0.02127,"approach.approach_speed":0.10471,"engage_contact.engage_force_threshold":4.49111,"engage_contact.engage_speed":0.00684,"push_through_channel.push_depth":0.13924,"push_through_channel.push_max_time":5.31123,"push_through_channel.push_speed":0.01248},"optimized_scores":{"best_composite_score":0.03452,"best_fitness_score":0.11119,"best_task_score":0.0006},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":321.0,"contact_point_centroid":[0.47384,0.11299,0.05726],"force_p95":265.30836,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1031.88585,"mean_force":139.08051,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.48256,0.10333,0.06142]},{"body_a":"world","body_b":"link7","contact_count":360.0,"contact_point_centroid":[0.49007,0.14724,-0.00012],"force_p95":335.35381,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":509.91364,"mean_force":304.51294,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.48708,0.08816,0.05716]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":830.0,"contact_point_centroid":[0.45769,0.11995,0.05983],"force_p95":247.8921,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":327.21736,"mean_force":184.70041,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48881,0.08103,0.05283]},{"body_a":"world","body_b":"link7","contact_count":422.0,"contact_point_centroid":[0.48833,0.1454,-1e-05],"force_p95":105.88615,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":155.50607,"mean_force":80.44536,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48968,0.08163,0.05222]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":170.0,"contact_point_centroid":[0.47499,0.10612,0.05539],"force_p95":54.08402,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":76.43869,"mean_force":40.24713,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48714,0.08281,0.0555]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.49141,0.14626,-8e-05],"force_p95":75.04941,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":75.04941,"mean_force":75.04941,"phase_index":2.0,"phase_name":"engage_contact","phase_type":"push","tcp_position_centroid":[0.48735,0.08903,0.05905]},{"body_a":"peg","body_b":"channel_base_body","contact_count":379.0,"contact_point_centroid":[0.49453,0.05907,0.00934],"force_p95":0.59782,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.5848,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48249,0.15182,0.19716]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49877,0.19714,0.29398]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49412,0.05899,0.0094],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55392,"mean_force":0.54516,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48851,0.0815,0.05338]},{"body_a":"peg","body_b":"channel_base_body","contact_count":871.0,"contact_point_centroid":[0.49403,0.0589,0.00939],"force_p95":0.55036,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54594,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.48319,0.09839,0.06254]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49588,0.04105,0.0094],"force_p95":0.53814,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53814,"mean_force":0.53814,"phase_index":2.0,"phase_name":"engage_contact","phase_type":"push","tcp_position_centroid":[0.48735,0.08903,0.05905]}],"total_contact_groups":11},"final_pose_error":0.16381,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49407,0.05866,0.03404],"final_tcp_position":[0.49072,0.08228,0.05208],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":1031.88585,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":408.0,"n_steps_budget":1000.0,"object_pos_end":[0.49402,0.05897,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13923,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54713,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":414.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach","tcp_end":[0.46763,0.10859,0.10709],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09232,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":871.0,"n_steps_budget":1000.0,"object_pos_end":[0.49416,0.05873,0.03397],"object_pos_start":[0.49402,0.05897,0.03385],"object_to_goal_dist_end":0.13898,"object_to_goal_dist_start":0.13923,"object_z_max":0.03397,"peak_contact_force":330.33277,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1552.0,"raw_peak_contact_force":1031.88585,"subtask_id":"contact","tcp_end":[0.48735,0.08903,0.05905],"tcp_start":[0.46763,0.10859,0.10709],"tcp_to_object_dist_end":0.03992,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49422,0.05875,0.03397],"object_pos_start":[0.49416,0.05873,0.03397],"object_to_goal_dist_end":0.139,"object_to_goal_dist_start":0.13898,"object_z_max":0.03397,"peak_contact_force":75.04941,"phase_name":"engage_contact","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":75.04941,"tcp_end":[0.48736,0.08903,0.05905],"tcp_start":[0.48735,0.08903,0.05905],"tcp_to_object_dist_end":0.03991,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49407,0.05866,0.03404],"object_pos_start":[0.49422,0.05875,0.03397],"object_to_goal_dist_end":0.13891,"object_to_goal_dist_start":0.139,"object_z_max":0.03404,"peak_contact_force":235.09578,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2422.0,"raw_peak_contact_force":327.21736,"subtask_id":"push","tcp_end":[0.49072,0.08228,0.05208],"tcp_start":[0.48736,0.08903,0.05905],"tcp_to_object_dist_end":0.02991,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1ee374347cb6f80436633ebcb956aaa73ea8a10685d65b21d5c3814cf0c53498`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.62441,"average_solve_count":213.0,"average_success_count":213.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.align_speed":0.02,"approach.approach_speed":0.05004,"engage_contact.engage_force_threshold":2.13307,"engage_contact.engage_speed":0.00563,"push_through_channel.push_depth":0.19955,"push_through_channel.push_max_time":5.62906,"push_through_channel.push_speed":0.03493},"optimized_scores":{"best_composite_score":0.0482,"best_fitness_score":0.12486,"best_task_score":0.03925},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":42.0,"contact_point_centroid":[0.54228,0.1195,0.05911],"force_p95":712.91268,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":911.49384,"mean_force":269.24652,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.53165,0.11718,0.06125]},{"body_a":"world","body_b":"link7","contact_count":362.0,"contact_point_centroid":[0.51086,0.17025,-0.00011],"force_p95":277.31648,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":284.62372,"mean_force":256.05906,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.50948,0.10943,0.05541]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":369.0,"contact_point_centroid":[0.525,0.11994,0.06],"force_p95":217.56094,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":234.53302,"mean_force":179.04937,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51156,0.07931,0.05243]},{"body_a":"world","body_b":"link7","contact_count":952.0,"contact_point_centroid":[0.51023,0.15196,-2e-05],"force_p95":149.9978,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":201.94159,"mean_force":107.82391,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51024,0.08893,0.05309]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.51154,0.16961,-8e-05],"force_p95":58.86138,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":58.86138,"mean_force":58.86138,"phase_index":2.0,"phase_name":"engage_contact","phase_type":"push","tcp_position_centroid":[0.50921,0.10936,0.05609]},{"body_a":"peg","body_b":"channel_base_body","contact_count":969.0,"contact_point_centroid":[0.50551,0.06236,0.00964],"force_p95":1.99031,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.62997,"mean_force":0.95156,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51021,0.08934,0.05313]},{"body_a":"attachment","body_b":"peg","contact_count":454.0,"contact_point_centroid":[0.50557,0.08422,0.0557],"force_p95":3.25004,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.57973,"mean_force":1.14512,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51069,0.08439,0.05277]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":143.0,"contact_point_centroid":[0.5251,0.06324,0.05112],"force_p95":2.77955,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.45878,"mean_force":0.49777,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51097,0.08158,0.05268]},{"body_a":"peg","body_b":"channel_base_body","contact_count":395.0,"contact_point_centroid":[0.50556,0.08086,0.00935],"force_p95":0.56157,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.58539,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51426,0.16252,0.19795]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50033,0.19798,0.2947]},{"body_a":"peg","body_b":"channel_base_body","contact_count":697.0,"contact_point_centroid":[0.50598,0.0809,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5501,"mean_force":0.54677,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.51666,0.11392,0.06361]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52106,0.09068,0.00938],"force_p95":0.54458,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54458,"mean_force":0.54458,"phase_index":2.0,"phase_name":"engage_contact","phase_type":"push","tcp_position_centroid":[0.50921,0.10936,0.05609]}],"total_contact_groups":12},"final_pose_error":0.19873,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50696,0.06058,0.03441],"final_tcp_position":[0.51255,0.07911,0.05203],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":911.49384,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":424.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54534,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":431.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach","tcp_end":[0.52875,0.12844,0.10673],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":697.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.50598,0.0809,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":275.93523,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1101.0,"raw_peak_contact_force":911.49384,"subtask_id":"contact","tcp_end":[0.50921,0.10936,0.05609],"tcp_start":[0.52875,0.12844,0.10673],"tcp_to_object_dist_end":0.03632,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":58.86138,"phase_name":"engage_contact","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":58.86138,"tcp_end":[0.50921,0.10937,0.05608],"tcp_start":[0.50921,0.10936,0.05609],"tcp_to_object_dist_end":0.03633,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50696,0.06058,0.03441],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.14087,"object_to_goal_dist_start":0.1611,"object_z_max":0.03587,"peak_contact_force":160.26185,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2887.0,"raw_peak_contact_force":234.53302,"subtask_id":"push","tcp_end":[0.51255,0.07911,0.05203],"tcp_start":[0.50921,0.10937,0.05608],"tcp_to_object_dist_end":0.02616,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e082b57d1be6744ae6d3993c25b90215f3fc56dc7131af62e0630c4f325e4b04`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.54206,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.align_speed":0.06627,"approach.approach_speed":0.10277,"engage_contact.engage_force_threshold":3.97444,"engage_contact.engage_speed":0.01315,"push_through_channel.push_depth":0.19023,"push_through_channel.push_max_time":4.2166,"push_through_channel.push_speed":0.04965},"optimized_scores":{"best_composite_score":0.09719,"best_fitness_score":0.17386,"best_task_score":0.14499},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":110.0,"contact_point_centroid":[0.525,0.1199,0.06],"force_p95":340.54013,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":388.88883,"mean_force":215.80998,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51038,0.07924,0.05214]},{"body_a":"world","body_b":"link7","contact_count":935.0,"contact_point_centroid":[0.5081,0.16706,-3e-05],"force_p95":234.03609,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":372.34918,"mean_force":148.0903,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50734,0.10397,0.05301]},{"body_a":"world","body_b":"link7","contact_count":94.0,"contact_point_centroid":[0.50775,0.1939,-0.00025],"force_p95":289.37743,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":314.96433,"mean_force":274.60339,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.50604,0.13255,0.05454]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50836,0.1938,-8e-05],"force_p95":61.14955,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":61.14955,"mean_force":61.14955,"phase_index":2.0,"phase_name":"engage_contact","phase_type":"push","tcp_position_centroid":[0.50544,0.13361,0.05612]},{"body_a":"attachment","body_b":"peg","contact_count":423.0,"contact_point_centroid":[0.50594,0.09624,0.04703],"force_p95":4.43316,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.05597,"mean_force":1.58344,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50814,0.09607,0.05265]},{"body_a":"peg","body_b":"channel_base_body","contact_count":904.0,"contact_point_centroid":[0.50388,0.07582,0.0097],"force_p95":3.18665,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.67713,"mean_force":1.13538,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.5073,0.10459,0.05304]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":392.0,"contact_point_centroid":[0.5251,0.07794,0.02733],"force_p95":1.66865,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70102,"mean_force":0.48283,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50812,0.09586,0.05264]},{"body_a":"peg","body_b":"channel_base_body","contact_count":353.0,"contact_point_centroid":[0.50558,0.10462,0.00936],"force_p95":0.58976,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57839,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50929,0.17353,0.19823]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50033,0.19842,0.29449]},{"body_a":"peg","body_b":"channel_base_body","contact_count":343.0,"contact_point_centroid":[0.5057,0.10461,0.00939],"force_p95":0.57555,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57865,"mean_force":0.54631,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.51006,0.13729,0.05772]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49683,0.12,0.00939],"force_p95":0.52943,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52943,"mean_force":0.52943,"phase_index":2.0,"phase_name":"engage_contact","phase_type":"push","tcp_position_centroid":[0.50544,0.13361,0.05612]}],"total_contact_groups":11},"final_pose_error":0.16583,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50704,0.06159,0.03571],"final_tcp_position":[0.5108,0.07924,0.05214],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":388.88883,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":380.0,"n_steps_budget":1000.0,"object_pos_end":[0.50587,0.10457,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.55109,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":385.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach","tcp_end":[0.51891,0.1499,0.10806],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08795,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":343.0,"n_steps_budget":750.0,"object_pos_end":[0.50589,0.10472,0.03384],"object_pos_start":[0.50587,0.10457,0.03384],"object_to_goal_dist_end":0.18491,"object_to_goal_dist_start":0.18476,"object_z_max":0.03384,"peak_contact_force":284.8266,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":437.0,"raw_peak_contact_force":314.96433,"subtask_id":"contact","tcp_end":[0.50544,0.13361,0.05612],"tcp_start":[0.51891,0.1499,0.10806],"tcp_to_object_dist_end":0.03649,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.10472,0.03383],"object_pos_start":[0.50589,0.10472,0.03384],"object_to_goal_dist_end":0.18492,"object_to_goal_dist_start":0.18491,"object_z_max":0.03384,"peak_contact_force":61.14955,"phase_name":"engage_contact","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":61.14955,"tcp_end":[0.50547,0.13363,0.0561],"tcp_start":[0.50544,0.13361,0.05612],"tcp_to_object_dist_end":0.03649,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50704,0.06159,0.03571],"object_pos_start":[0.50593,0.10472,0.03383],"object_to_goal_dist_end":0.14183,"object_to_goal_dist_start":0.18492,"object_z_max":0.03645,"peak_contact_force":157.63679,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2764.0,"raw_peak_contact_force":388.88883,"subtask_id":"push","tcp_end":[0.5108,0.07924,0.05214],"tcp_start":[0.50547,0.13363,0.0561],"tcp_to_object_dist_end":0.02441,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```