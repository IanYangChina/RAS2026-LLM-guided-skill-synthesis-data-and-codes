## Search State

- **Seed**: 3
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.1946 | 0.11 | ✅ accepted |
| 2 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | -0.1168 | 0.09 | ❌ rejected |
| 1 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.1599 | 0.00 | ❌ rejected |
| 0 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | -0.1168 | 0.09 | ✅ accepted |

**Proposal policy**: task_score is 0.11 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.195) — your mutation base

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

- **Composite score**: 0.195
- **task_score** (E): 0.107
- **fitness_score**: 0.165  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.259
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2182 |
| contact | 0.67 | 1.00 | 0.0489 |
| push | 0.00 | 1.00 | 0.0383 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.125, 0.098) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.546 | 3.954 |
| contact | descend | 0.67 / force_exceeded | (0.505, 0.125, 0.098)→(0.499, 0.110, 0.053) | (0.502, 0.081, 0.034)→(0.502, 0.079, 0.034) | 0.162→0.159 | 1.00 / 2.000 | 42.839 | 48.431 |
| push | push | 0.00 / step_budget | (0.499, 0.110, 0.053)→(0.510, 0.082, 0.062) | (0.502, 0.079, 0.034)→(0.502, 0.034, 0.024) | 0.159→0.116 | 1.00 / 2.667 | 303.290 | 742.801 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.270
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.088
- phase_score: 0.208
- phase_breakdown.push_score: 0.039
- phase_breakdown.approach_score: 0.310
- phase_breakdown.contact_score: 0.614

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.191
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.153
- **Median Q (composite search score)**: 0.249
- **K-run variance**: 0.0076
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.447


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.075,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.05054,"contact.contact_force_threshold":7.15867,"push.push_distance":0.03042,"push.push_speed":0.01484},"optimized_scores":{"best_composite_score":0.26349,"best_fitness_score":0.16016,"best_task_score":0.08772},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":49.0,"contact_point_centroid":[0.47487,0.08584,0.0599],"force_p95":447.49078,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":577.61272,"mean_force":290.03245,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48434,0.0796,0.05746]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":137.0,"contact_point_centroid":[0.52502,0.11995,0.05995],"force_p95":307.09193,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":431.34646,"mean_force":248.89115,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49413,0.07162,0.0778]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":812.0,"contact_point_centroid":[0.47497,0.11993,0.05996],"force_p95":277.99223,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":300.68893,"mean_force":271.38199,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50306,0.07399,0.08385]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47499,0.10192,0.05997],"force_p95":52.66092,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":52.66092,"mean_force":52.66092,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.47685,0.0901,0.05937]},{"body_a":"peg","body_b":"channel_base_body","contact_count":977.0,"contact_point_centroid":[0.49854,0.01733,0.00819],"force_p95":0.77359,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.20076,"mean_force":0.76113,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50097,0.07406,0.08174]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.4876,0.07415,0.05913],"force_p95":28.79221,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.16012,"mean_force":20.83777,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.4819,0.08446,0.0581]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":30.0,"contact_point_centroid":[0.47496,0.04357,0.02543],"force_p95":8.38971,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.57648,"mean_force":2.21678,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49478,0.0747,0.07247]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":26.0,"contact_point_centroid":[0.52543,0.01851,0.04634],"force_p95":6.57158,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.34089,"mean_force":1.16266,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48988,0.07751,0.06515]},{"body_a":"peg","body_b":"channel_base_body","contact_count":718.0,"contact_point_centroid":[0.4943,0.05903,0.00936],"force_p95":0.55964,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56656,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48146,0.15053,0.19457]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49897,0.1983,0.29653]},{"body_a":"peg","body_b":"channel_base_body","contact_count":303.0,"contact_point_centroid":[0.49397,0.05875,0.00939],"force_p95":0.55014,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.5459,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.46991,0.09693,0.07731]}],"total_contact_groups":11},"final_pose_error":0.19118,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49431,0.0158,0.02443],"final_tcp_position":[0.50586,0.0759,0.08247],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":577.61272,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":747.0,"n_steps_budget":1000.0,"object_pos_end":[0.49399,0.0589,0.03389],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13916,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54852,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":753.0,"raw_peak_contact_force":4.20518,"tcp_end":[0.46549,0.10433,0.09827],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08379,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":303.0,"n_steps_budget":600.0,"object_pos_end":[0.49419,0.05878,0.03393],"object_pos_start":[0.49399,0.0589,0.03389],"object_to_goal_dist_end":0.13903,"object_to_goal_dist_start":0.13916,"object_z_max":0.03393,"peak_contact_force":52.66092,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":304.0,"raw_peak_contact_force":52.66092,"subtask_id":"contact","tcp_end":[0.4769,0.09006,0.05926],"tcp_start":[0.46549,0.10433,0.09827],"tcp_to_object_dist_end":0.04381,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49431,0.0158,0.02443],"object_pos_start":[0.49419,0.05878,0.03393],"object_to_goal_dist_end":0.09722,"object_to_goal_dist_start":0.13903,"object_z_max":0.04119,"peak_contact_force":139.08903,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2035.0,"raw_peak_contact_force":577.61272,"subtask_id":"push","tcp_end":[0.50586,0.0759,0.08247],"tcp_start":[0.4769,0.09006,0.05926],"tcp_to_object_dist_end":0.08434,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.52459,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.09052,"contact.contact_force_threshold":8.85286,"push.push_distance":0.02198,"push.push_speed":0.02379},"optimized_scores":{"best_composite_score":0.24852,"best_fitness_score":0.14519,"best_task_score":0.07912},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":374.0,"contact_point_centroid":[0.52518,0.08381,0.0527],"force_p95":303.31036,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":561.76475,"mean_force":256.02283,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51343,0.08255,0.05303]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":482.0,"contact_point_centroid":[0.47495,0.11992,0.05845],"force_p95":512.60168,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":523.20996,"mean_force":379.28096,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51299,0.07983,0.05221]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":434.0,"contact_point_centroid":[0.52684,0.11992,0.06],"force_p95":176.12482,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":181.38421,"mean_force":146.49711,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51045,0.07959,0.05282]},{"body_a":"peg","body_b":"channel_base_body","contact_count":983.0,"contact_point_centroid":[0.50479,0.04019,0.0082],"force_p95":0.72571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":100.78769,"mean_force":0.81411,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.5112,0.08258,0.05272]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50789,0.09756,0.05847],"force_p95":88.32431,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":100.28801,"mean_force":36.86871,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50307,0.10533,0.05112]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52683,0.11333,0.05998],"force_p95":74.43734,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":74.43734,"mean_force":74.43734,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.51549,0.1134,0.06388]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":18.0,"contact_point_centroid":[0.525,0.061,0.02432],"force_p95":8.50821,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.56464,"mean_force":3.83763,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51322,0.08059,0.05205]},{"body_a":"peg","body_b":"channel_base_body","contact_count":669.0,"contact_point_centroid":[0.50578,0.08087,0.00936],"force_p95":0.55533,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.56958,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51441,0.16097,0.19384]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49997,0.1984,0.29594]},{"body_a":"peg","body_b":"channel_base_body","contact_count":153.0,"contact_point_centroid":[0.50578,0.08098,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55007,"mean_force":0.54678,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.52225,0.1193,0.08039]}],"total_contact_groups":10},"final_pose_error":0.18399,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50592,0.03775,0.02428],"final_tcp_position":[0.51323,0.08113,0.05205],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":561.76475,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":698.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54819,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":705.0,"raw_peak_contact_force":4.32595,"tcp_end":[0.52972,0.12483,0.09712],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08069,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":153.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":74.43734,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":154.0,"raw_peak_contact_force":74.43734,"subtask_id":"contact","tcp_end":[0.51542,0.11333,0.06369],"tcp_start":[0.52972,0.12483,0.09712],"tcp_to_object_dist_end":0.04513,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50592,0.03775,0.02428],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.11894,"object_to_goal_dist_start":0.16112,"object_z_max":0.04085,"peak_contact_force":514.53683,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2295.0,"raw_peak_contact_force":561.76475,"subtask_id":"push","tcp_end":[0.51323,0.08113,0.05205],"tcp_start":[0.51542,0.11333,0.06369],"tcp_to_object_dist_end":0.05203,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37956,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.06782,"contact.contact_force_threshold":13.83581,"push.push_distance":0.03109,"push.push_speed":0.02997},"optimized_scores":{"best_composite_score":0.07183,"best_fitness_score":0.19072,"best_task_score":0.15339},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52625,0.11928,0.05957],"force_p95":1018.96598,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1089.02479,"mean_force":404.09847,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50668,0.12221,0.03476]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.54729,0.11996,0.05992],"force_p95":530.11498,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":630.38186,"mean_force":432.84054,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49506,0.12167,0.02968]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":8.0,"contact_point_centroid":[0.48841,0.11287,0.00977],"force_p95":472.0479,"geom_a":"pusher_tip","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":559.11852,"mean_force":320.20125,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48662,0.10774,0.02024]},{"body_a":"world","body_b":"link7","contact_count":906.0,"contact_point_centroid":[0.49864,0.16522,-6e-05],"force_p95":321.04217,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":483.2385,"mean_force":270.40331,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50934,0.1003,0.04884]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.475,0.11098,0.02171],"force_p95":387.23925,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":387.23925,"mean_force":387.23925,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48646,0.10787,0.02001]},{"body_a":"peg","body_b":"channel_base_body","contact_count":985.0,"contact_point_centroid":[0.50499,0.05226,0.00827],"force_p95":0.65198,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":57.29604,"mean_force":0.7329,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.5084,0.1018,0.04745]},{"body_a":"attachment","body_b":"peg","contact_count":20.0,"contact_point_centroid":[0.49513,0.10383,0.03336],"force_p95":9.55671,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.83189,"mean_force":3.93501,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49188,0.11087,0.0251]},{"body_a":"peg","body_b":"channel_base_body","contact_count":277.0,"contact_point_centroid":[0.50578,0.0987,0.0095],"force_p95":13.24016,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.19342,"mean_force":1.78113,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.5108,0.13742,0.06792]},{"body_a":"attachment","body_b":"peg","contact_count":40.0,"contact_point_centroid":[0.50606,0.11837,0.04649],"force_p95":16.62308,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.94506,"mean_force":8.7814,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.50572,0.13019,0.04639]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.52513,0.07501,0.02737],"force_p95":11.09065,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.1733,"mean_force":3.84777,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50507,0.10876,0.04367]},{"body_a":"peg","body_b":"channel_base_body","contact_count":657.0,"contact_point_centroid":[0.50562,0.10462,0.00937],"force_p95":0.57584,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56355,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50901,0.17259,0.19487]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49979,0.19889,0.2966]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.47485,0.06009,0.05715],"force_p95":0.84012,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.02797,"mean_force":0.42387,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48665,0.10833,0.02027]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.52534,0.0984,0.05999],"force_p95":0.56787,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70656,"mean_force":0.14924,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.50592,0.13041,0.04742]}],"total_contact_groups":14},"final_pose_error":0.20059,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50591,0.04968,0.02415],"final_tcp_position":[0.5103,0.08897,0.05028],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":1089.02479,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":684.0,"n_steps_budget":1000.0,"object_pos_end":[0.50589,0.10472,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18492,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54271,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":689.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.51931,0.14718,0.09794],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07806,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":286.0,"n_steps_budget":600.0,"object_pos_end":[0.5048,0.09727,0.03383],"object_pos_start":[0.50589,0.10472,0.03384],"object_to_goal_dist_end":0.17744,"object_to_goal_dist_start":0.18492,"object_z_max":0.03674,"peak_contact_force":1.4199,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":337.0,"raw_peak_contact_force":18.19342,"subtask_id":"contact","tcp_end":[0.50375,0.12716,0.03751],"tcp_start":[0.51931,0.14718,0.09794],"tcp_to_object_dist_end":0.03014,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50591,0.04968,0.02415],"object_pos_start":[0.5048,0.09727,0.03383],"object_to_goal_dist_end":0.13077,"object_to_goal_dist_start":0.17744,"object_z_max":0.0408,"peak_contact_force":256.24483,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1986.0,"raw_peak_contact_force":1089.02479,"subtask_id":"push","tcp_end":[0.5103,0.08897,0.05028],"tcp_start":[0.50375,0.12716,0.03751],"tcp_to_object_dist_end":0.04739,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```