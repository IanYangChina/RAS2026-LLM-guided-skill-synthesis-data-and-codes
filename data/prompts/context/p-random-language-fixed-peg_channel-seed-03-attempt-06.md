## Search State

- **Seed**: 3
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 5 | 0.2780 | 0.02 | ❌ rejected |
| 5 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.2701 | 0.12 | ✅ accepted |
| 4 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | force_exceeded | 5 | 0.0574 | 0.00 | ❌ rejected |
| 3 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.1946 | 0.11 | ✅ accepted |
| 2 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | -0.1168 | 0.09 | ❌ rejected |

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

## Current Skill (Q=0.278) — your mutation base

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
    - 0.04
    - 0.05
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: add
- id: contact
  type: descend
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
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 1.0
      - 15.0
      default: 5
      binds_to:
      - path: termination.force_threshold
        mode: add
  guards:
  - id: contact_guard
    when: after_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: contact
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
      distance: 0.02
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.05], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (add)
- **contact** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (add)
  - guards:
    - id=contact_guard, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=reduce_speed
- **push** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.02, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.278
- **task_score** (E): 0.020
- **fitness_score**: 0.114  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.444
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2077 |
| contact | 0.33 | 1.00 | 0.0642 |
| push | 1.00 | 1.00 | 0.0168 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.129, 0.107) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.546 | 3.954 |
| contact | descend | 0.33 / step_budget | (0.505, 0.129, 0.107)→(0.498, 0.086, 0.064) | (0.502, 0.081, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.162 | 1.00 / 1.333 | 6.299 | 6.311 |
| push | push | 1.00 / force_exceeded | (0.498, 0.086, 0.064)→(0.497, 0.070, 0.061) | (0.502, 0.081, 0.034)→(0.502, 0.073, 0.034) | 0.162→0.154 | 1.00 / 2.000 | 50.032 | 50.032 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.028
- alignment_error: None
- force_efficiency: 0.029
- terminal_score: 0.010
- phase_score: 0.188
- phase_breakdown.push_score: 0.062
- phase_breakdown.approach_score: 0.257
- phase_breakdown.contact_score: 0.498

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.117
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.032
- **Median Q (composite search score)**: 0.168
- **K-run variance**: 0.0254
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.302


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11111,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.05916,"contact.contact_force_threshold":7.35746,"push.push_force_threshold":38.12816,"push.push_speed":0.04372,"push.push_stroke":0.15845},"optimized_scores":{"best_composite_score":0.50348,"best_fitness_score":0.11682,"best_task_score":0.00956},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":95.0,"contact_point_centroid":[0.49349,0.04773,0.00917],"force_p95":46.64671,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.52689,"mean_force":36.90784,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48641,0.06045,0.06264]},{"body_a":"attachment","body_b":"peg","contact_count":95.0,"contact_point_centroid":[0.49708,0.06121,0.05778],"force_p95":46.12814,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.00951,"mean_force":36.43204,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48641,0.06045,0.06264]},{"body_a":"peg","body_b":"channel_base_body","contact_count":501.0,"contact_point_centroid":[0.49401,0.05904,0.00939],"force_p95":0.55039,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.80551,"mean_force":0.58053,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.47582,0.08614,0.08383]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49774,0.06532,0.05895],"force_p95":17.33414,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.33414,"mean_force":17.33414,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.48707,0.06446,0.06435]},{"body_a":"peg","body_b":"channel_base_body","contact_count":402.0,"contact_point_centroid":[0.49448,0.05886,0.00934],"force_p95":0.59589,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.58261,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48241,0.15219,0.198]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49875,0.19752,0.29481]}],"total_contact_groups":6},"final_pose_error":0.29603,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49334,0.05447,0.0328],"final_tcp_position":[0.48615,0.05646,0.06176],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":48.52689,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":431.0,"n_steps_budget":1000.0,"object_pos_end":[0.49423,0.05898,0.03386],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13924,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54735,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":437.0,"raw_peak_contact_force":4.20518,"tcp_end":[0.46736,0.10871,0.10727],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09265,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":501.0,"n_steps_budget":600.0,"object_pos_end":[0.49415,0.05877,0.03392],"object_pos_start":[0.49423,0.05898,0.03386],"object_to_goal_dist_end":0.13902,"object_to_goal_dist_start":0.13924,"object_z_max":0.03392,"peak_contact_force":17.80551,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":502.0,"raw_peak_contact_force":17.80551,"subtask_id":"contact","tcp_end":[0.48715,0.06438,0.06428],"tcp_start":[0.46736,0.10871,0.10727],"tcp_to_object_dist_end":0.03166,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":95.0,"n_steps_budget":1000.0,"object_pos_end":[0.49334,0.05447,0.0328],"object_pos_start":[0.49415,0.05877,0.03392],"object_to_goal_dist_end":0.13482,"object_to_goal_dist_start":0.13902,"object_z_max":0.03402,"peak_contact_force":48.52689,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":190.0,"raw_peak_contact_force":48.52689,"subtask_id":"push","tcp_end":[0.48615,0.05646,0.06176],"tcp_start":[0.48715,0.06438,0.06428],"tcp_to_object_dist_end":0.0299,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72603,"average_solve_count":73.0,"average_success_count":73.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.11172,"contact.contact_force_threshold":6.35116,"push.push_force_threshold":39.92891,"push.push_speed":0.04951,"push.push_stroke":0.18445},"optimized_scores":{"best_composite_score":0.16295,"best_fitness_score":0.10962,"best_task_score":0.01793},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":223.0,"contact_point_centroid":[0.51359,0.06286,0.00939],"force_p95":48.54347,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.69569,"mean_force":39.97572,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50342,0.07556,0.06131]},{"body_a":"attachment","body_b":"peg","contact_count":212.0,"contact_point_centroid":[0.51472,0.07498,0.05807],"force_p95":48.07778,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.19414,"mean_force":41.54859,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50337,0.07506,0.06122]},{"body_a":"peg","body_b":"channel_base_body","contact_count":370.0,"contact_point_centroid":[0.50558,0.08084,0.00935],"force_p95":0.56435,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.588,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51436,0.16231,0.19731]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.5005,0.19765,0.2937]},{"body_a":"peg","body_b":"channel_base_body","contact_count":328.0,"contact_point_centroid":[0.50603,0.08096,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55014,"mean_force":0.54677,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.51548,0.10702,0.0833]}],"total_contact_groups":5},"final_pose_error":0.33014,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50602,0.07118,0.03406],"final_tcp_position":[0.50367,0.06501,0.06091],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":50.69569,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":399.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54626,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":406.0,"raw_peak_contact_force":4.32595,"tcp_end":[0.52863,0.12852,0.1068],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09008,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":328.0,"n_steps_budget":600.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.54611,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":328.0,"raw_peak_contact_force":0.55014,"subtask_id":"contact","tcp_end":[0.50474,0.08573,0.06368],"tcp_start":[0.52863,0.12852,0.1068],"tcp_to_object_dist_end":0.03032,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":223.0,"n_steps_budget":1000.0,"object_pos_end":[0.50602,0.07118,0.03406],"object_pos_start":[0.50597,0.08086,0.03378],"object_to_goal_dist_end":0.15142,"object_to_goal_dist_start":0.16109,"object_z_max":0.03406,"peak_contact_force":50.69569,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":435.0,"raw_peak_contact_force":50.69569,"subtask_id":"push","tcp_end":[0.50367,0.06501,0.06091],"tcp_start":[0.50474,0.08573,0.06368],"tcp_to_object_dist_end":0.02765,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.02128,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.04049,"contact.contact_force_threshold":7.32985,"push.push_force_threshold":39.59061,"push.push_speed":0.02535,"push.push_stroke":0.16449},"optimized_scores":{"best_composite_score":0.16771,"best_fitness_score":0.11437,"best_task_score":0.03168},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":223.0,"contact_point_centroid":[0.51243,0.08585,0.00939],"force_p95":48.80727,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.87473,"mean_force":40.26369,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50223,0.09866,0.06144]},{"body_a":"attachment","body_b":"peg","contact_count":213.0,"contact_point_centroid":[0.51349,0.09825,0.05807],"force_p95":48.33724,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.37241,"mean_force":41.65539,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50219,0.0982,0.06135]},{"body_a":"peg","body_b":"channel_base_body","contact_count":377.0,"contact_point_centroid":[0.50558,0.10472,0.00936],"force_p95":0.5831,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57632,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50893,0.17389,0.19959]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49998,0.19873,0.29577]},{"body_a":"peg","body_b":"channel_base_body","contact_count":339.0,"contact_point_centroid":[0.50593,0.1046,0.00939],"force_p95":0.57556,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57724,"mean_force":0.54632,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.50977,0.1292,0.08402]}],"total_contact_groups":5},"final_pose_error":0.33318,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50596,0.09471,0.03403],"final_tcp_position":[0.50248,0.08801,0.06102],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":50.87473,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":404.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.10458,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18478,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54319,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":409.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.51862,0.14999,0.10832],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08815,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":339.0,"n_steps_budget":600.0,"object_pos_end":[0.50591,0.10456,0.03384],"object_pos_start":[0.50596,0.10458,0.03384],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.18478,"object_z_max":0.03384,"peak_contact_force":0.54406,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":339.0,"raw_peak_contact_force":0.57724,"subtask_id":"contact","tcp_end":[0.50353,0.10893,0.06378],"tcp_start":[0.51862,0.14999,0.10832],"tcp_to_object_dist_end":0.03036,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":223.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.09471,0.03403],"object_pos_start":[0.50591,0.10456,0.03384],"object_to_goal_dist_end":0.17491,"object_to_goal_dist_start":0.18476,"object_z_max":0.03406,"peak_contact_force":50.87473,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":436.0,"raw_peak_contact_force":50.87473,"subtask_id":"push","tcp_end":[0.50248,0.08801,0.06102],"tcp_start":[0.50353,0.10893,0.06378],"tcp_to_object_dist_end":0.02803,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```