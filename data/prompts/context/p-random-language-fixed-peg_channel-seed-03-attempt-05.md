## Search State

- **Seed**: 3
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.2701 | 0.12 | ✅ accepted |
| 4 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | force_exceeded | 5 | 0.0574 | 0.00 | ❌ rejected |
| 3 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.1946 | 0.11 | ✅ accepted |
| 2 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | -0.1168 | 0.09 | ❌ rejected |
| 1 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.1599 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.12 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.270) — your mutation base

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

- **Composite score**: 0.270
- **task_score** (E): 0.117
- **fitness_score**: 0.167  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2182 |
| contact | 1.00 | 1.00 | 0.0413 |
| push | 0.00 | 1.00 | 0.0413 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.125, 0.098) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.547 | 3.954 |
| contact | descend | 1.00 / force_exceeded | (0.505, 0.125, 0.098)→(0.500, 0.113, 0.061) | (0.502, 0.081, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.162 | 1.00 / 2.000 | 48.715 | 48.715 |
| push | push | 0.00 / step_budget | (0.500, 0.113, 0.061)→(0.511, 0.081, 0.061) | (0.502, 0.081, 0.034)→(0.503, 0.032, 0.024) | 0.162→0.113 | 1.00 / 2.667 | 436.041 | 618.763 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.375
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.194
- phase_score: 0.203
- phase_breakdown.push_score: 0.037
- phase_breakdown.approach_score: 0.312
- phase_breakdown.contact_score: 0.590

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.199
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.194
- **Median Q (composite search score)**: 0.260
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.304


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56,"average_solve_count":125.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.08025,"contact.contact_force_threshold":7.87715,"push.push_distance":0.02373,"push.push_speed":0.03406},"optimized_scores":{"best_composite_score":0.25969,"best_fitness_score":0.15636,"best_task_score":0.07835},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":38.0,"contact_point_centroid":[0.47477,0.08561,0.05974],"force_p95":477.29719,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":610.10092,"mean_force":297.61112,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48426,0.08048,0.05565]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":120.0,"contact_point_centroid":[0.52503,0.11992,0.0599],"force_p95":376.48577,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":523.58242,"mean_force":271.12058,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49304,0.07359,0.07286]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":824.0,"contact_point_centroid":[0.47497,0.11993,0.05996],"force_p95":278.60408,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":305.13095,"mean_force":272.79765,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50266,0.07491,0.08268]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.48769,0.07443,0.05932],"force_p95":66.54789,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":66.55199,"mean_force":65.28662,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48181,0.08487,0.05834]},{"body_a":"peg","body_b":"channel_base_body","contact_count":969.0,"contact_point_centroid":[0.49781,0.01361,0.00802],"force_p95":0.72606,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":66.50351,"mean_force":0.84141,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50092,0.07497,0.08073]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47499,0.10186,0.05997],"force_p95":52.56711,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":52.56711,"mean_force":52.56711,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.47698,0.09007,0.0593]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.475,0.03534,0.02422],"force_p95":6.8694,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.92472,"mean_force":3.97882,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50333,0.07515,0.08236]},{"body_a":"peg","body_b":"channel_base_body","contact_count":673.0,"contact_point_centroid":[0.49429,0.0589,0.00936],"force_p95":0.56039,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56792,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48146,0.15042,0.19435]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49893,0.19818,0.29625]},{"body_a":"peg","body_b":"channel_base_body","contact_count":303.0,"contact_point_centroid":[0.4942,0.05927,0.00939],"force_p95":0.55005,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54595,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.46997,0.09688,0.0772]}],"total_contact_groups":10},"final_pose_error":0.18536,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49753,0.01369,0.02409],"final_tcp_position":[0.50537,0.07687,0.08139],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":610.10092,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":702.0,"n_steps_budget":1000.0,"object_pos_end":[0.49425,0.0589,0.03389],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13915,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54263,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":708.0,"raw_peak_contact_force":4.20518,"tcp_end":[0.46548,0.10426,0.09812],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":303.0,"n_steps_budget":600.0,"object_pos_end":[0.49394,0.05891,0.03393],"object_pos_start":[0.49425,0.0589,0.03389],"object_to_goal_dist_end":0.13918,"object_to_goal_dist_start":0.13915,"object_z_max":0.03393,"peak_contact_force":52.56711,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":304.0,"raw_peak_contact_force":52.56711,"subtask_id":"contact","tcp_end":[0.47703,0.09002,0.05919],"tcp_start":[0.46548,0.10426,0.09812],"tcp_to_object_dist_end":0.0435,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49753,0.01369,0.02409],"object_pos_start":[0.49394,0.05891,0.03393],"object_to_goal_dist_end":0.09506,"object_to_goal_dist_start":0.13918,"object_z_max":0.04153,"peak_contact_force":275.16836,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1961.0,"raw_peak_contact_force":610.10092,"subtask_id":"push","tcp_end":[0.50537,0.07687,0.08139],"tcp_start":[0.47703,0.09002,0.05919],"tcp_to_object_dist_end":0.08565,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45283,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.13118,"contact.contact_force_threshold":4.08719,"push.push_distance":0.02244,"push.push_speed":0.0307},"optimized_scores":{"best_composite_score":0.24828,"best_fitness_score":0.14494,"best_task_score":0.07846},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":361.0,"contact_point_centroid":[0.52519,0.08391,0.05239],"force_p95":300.38614,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":561.93545,"mean_force":253.55463,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51343,0.08264,0.05271]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":500.0,"contact_point_centroid":[0.47495,0.11992,0.05822],"force_p95":511.76187,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":522.84632,"mean_force":363.85794,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51291,0.07988,0.05191]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":419.0,"contact_point_centroid":[0.52684,0.11993,0.06],"force_p95":174.5085,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":179.2944,"mean_force":141.89756,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51021,0.07961,0.05254]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52685,0.11335,0.05998],"force_p95":74.53121,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":74.53121,"mean_force":74.53121,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.51551,0.11341,0.06387]},{"body_a":"peg","body_b":"channel_base_body","contact_count":981.0,"contact_point_centroid":[0.50469,0.04014,0.00817],"force_p95":0.72563,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.56645,"mean_force":0.64909,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51105,0.08255,0.05237]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50704,0.09794,0.05829],"force_p95":21.61868,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.81553,"mean_force":15.13361,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50285,0.10607,0.05094]},{"body_a":"peg","body_b":"channel_base_body","contact_count":641.0,"contact_point_centroid":[0.50572,0.08087,0.00936],"force_p95":0.55572,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57057,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51447,0.16092,0.19369]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49999,0.19836,0.29581]},{"body_a":"peg","body_b":"channel_base_body","contact_count":153.0,"contact_point_centroid":[0.50619,0.081,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55007,"mean_force":0.54677,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.52229,0.1193,0.08039]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.06044,0.02416],"force_p95":0.37702,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37702,"mean_force":0.37702,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.5132,0.08046,0.05169]}],"total_contact_groups":10},"final_pose_error":0.18449,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50514,0.03642,0.02409],"final_tcp_position":[0.51323,0.0812,0.0517],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":561.93545,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":670.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54527,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":677.0,"raw_peak_contact_force":4.32595,"tcp_end":[0.52974,0.12482,0.09711],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08065,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":153.0,"n_steps_budget":600.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":74.53121,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":154.0,"raw_peak_contact_force":74.53121,"subtask_id":"contact","tcp_end":[0.51544,0.11334,0.06368],"tcp_start":[0.52974,0.12482,0.09711],"tcp_to_object_dist_end":0.04516,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50514,0.03642,0.02409],"object_pos_start":[0.50597,0.08086,0.03378],"object_to_goal_dist_end":0.11762,"object_to_goal_dist_start":0.16109,"object_z_max":0.04089,"peak_contact_force":512.95118,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2265.0,"raw_peak_contact_force":561.93545,"subtask_id":"push","tcp_end":[0.51323,0.0812,0.0517],"tcp_start":[0.51544,0.11334,0.06368],"tcp_to_object_dist_end":0.05323,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61905,"average_solve_count":105.0,"average_success_count":105.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.11428,"contact.contact_force_threshold":9.0035,"push.push_distance":0.02802,"push.push_speed":0.06041},"optimized_scores":{"best_composite_score":0.30238,"best_fitness_score":0.19905,"best_task_score":0.19367},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":155.0,"contact_point_centroid":[0.52511,0.08801,0.05095],"force_p95":318.13143,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":684.25183,"mean_force":249.17412,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51359,0.08698,0.05023]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":59.0,"contact_point_centroid":[0.53256,0.11966,0.05974],"force_p95":545.80072,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":605.75041,"mean_force":238.09187,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50483,0.09387,0.04412]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":731.0,"contact_point_centroid":[0.47495,0.11992,0.05699],"force_p95":475.52939,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":604.7296,"mean_force":268.27221,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51074,0.08183,0.05072]},{"body_a":"world","body_b":"link7","contact_count":376.0,"contact_point_centroid":[0.49482,0.15284,-3e-05],"force_p95":365.39914,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":542.44819,"mean_force":125.86063,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.5087,0.08837,0.04821]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":16.0,"contact_point_centroid":[0.49506,0.11973,0.00967],"force_p95":177.1123,"geom_a":"pusher_tip","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":183.60244,"mean_force":155.24214,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48818,0.11656,0.01828]},{"body_a":"attachment","body_b":"peg","contact_count":22.0,"contact_point_centroid":[0.49923,0.10304,0.03991],"force_p95":38.59822,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":78.7822,"mean_force":18.12323,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50401,0.10295,0.0494]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":217.0,"contact_point_centroid":[0.52544,0.07784,0.04245],"force_p95":41.12134,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":69.8168,"mean_force":17.32077,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50044,0.10634,0.03717]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":179.0,"contact_point_centroid":[0.47427,0.07273,0.03569],"force_p95":41.3145,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.55026,"mean_force":20.99881,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49819,0.11471,0.03373]},{"body_a":"peg","body_b":"channel_base_body","contact_count":805.0,"contact_point_centroid":[0.5049,0.0464,0.00824],"force_p95":1.12314,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.82673,"mean_force":0.93952,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51038,0.08312,0.05081]},{"body_a":"peg","body_b":"channel_base_body","contact_count":181.0,"contact_point_centroid":[0.50594,0.10473,0.00939],"force_p95":0.57566,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.04778,"mean_force":0.64849,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.51322,0.14084,0.07811]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50819,0.1223,0.05888],"force_p95":18.63778,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.63778,"mean_force":18.63778,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.5084,0.13426,0.05883]},{"body_a":"peg","body_b":"channel_base_body","contact_count":614.0,"contact_point_centroid":[0.50571,0.10461,0.00937],"force_p95":0.57604,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56476,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50907,0.17253,0.19464]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49984,0.19884,0.29636]}],"total_contact_groups":13},"final_pose_error":0.19271,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50619,0.04466,0.02415],"final_tcp_position":[0.51326,0.08396,0.05037],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":684.25183,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":641.0,"n_steps_budget":1000.0,"object_pos_end":[0.50584,0.10459,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18479,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.552,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":646.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.51932,0.14718,0.09793],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07812,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":181.0,"n_steps_budget":600.0,"object_pos_end":[0.50587,0.10454,0.03384],"object_pos_start":[0.50584,0.10459,0.03383],"object_to_goal_dist_end":0.18474,"object_to_goal_dist_start":0.18479,"object_z_max":0.03384,"peak_contact_force":19.04778,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":182.0,"raw_peak_contact_force":19.04778,"subtask_id":"contact","tcp_end":[0.50835,0.1342,0.05864],"tcp_start":[0.51932,0.14718,0.09793],"tcp_to_object_dist_end":0.03874,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50619,0.04466,0.02415],"object_pos_start":[0.50587,0.10454,0.03384],"object_to_goal_dist_end":0.12582,"object_to_goal_dist_start":0.18474,"object_z_max":0.0431,"peak_contact_force":520.00313,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2560.0,"raw_peak_contact_force":684.25183,"subtask_id":"push","tcp_end":[0.51326,0.08396,0.05037],"tcp_start":[0.50835,0.1342,0.05864],"tcp_to_object_dist_end":0.04776,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```