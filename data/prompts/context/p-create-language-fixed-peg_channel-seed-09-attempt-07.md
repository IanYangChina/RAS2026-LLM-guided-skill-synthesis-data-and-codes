## Search State

- **Seed**: 9
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | align → approach → descend → contact → push | joint_interpolation | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 5 | 0.1917 | 0.22 | ✅ accepted |
| 6 | align → approach → contact → push | joint_interpolation | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 4 | 0.1554 | 0.13 | ✅ accepted |
| 5 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.0859 | 0.04 | ✅ accepted |
| 4 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.0746 | 0.00 | ✅ accepted |
| 3 | approach → descend → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.0852 | 0.04 | ✅ accepted |

**Proposal policy**: task_score is 0.22 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`
- Frozen object start: [0.5296199363176067, 0.06294537672700443, 0.04]
- Frozen task target: [0.5296199363176067, -0.09705462327299558, 0.04]
- Goal object position: (0.5296199363176067, -0.09705462327299558, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5296199363176067, 0.06294537672700443, 0.04)
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
  frozen_object_start: [0.5296, 0.0629, 0.04]
  frozen_task_target: [0.5296, -0.0971, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5296199363176067, 0.06294537672700443, 0.04]}
  frozen_targets: {'channel_exit': [0.5296199363176067, -0.09705462327299558, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9

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

## Current Skill (Q=0.192) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: align
  type: align
  generator: joint_interpolation
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.05
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
- id: approach_high
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
    - 0.05
    - 0.05
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.5
      binds_to:
      - path: generator.speed
        mode: replace
- id: descend
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.018
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
- id: contact
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
    - 0.018
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
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
  subtask_id: contact
- id: push
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.018
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
    push_depth:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_duration:
      type: scalar
      range:
      - 1.0
      - 3.0
      default: 2.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: push_force_guard
    when: during_phase
    predicate: force_below
    threshold: 45.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.001
    - 0.0
    - 0.0
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **align** (`align`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.05
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings: none
- **approach_high** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.05], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.018, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **contact** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.018, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.018, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_duration: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=push_force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=45.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.001, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.192
- **task_score** (E): 0.217
- **fitness_score**: 0.332  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.340

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align | 1.00 | 1.00 | 0.0041 |
| approach_high | 1.00 | 1.00 | 0.2088 |
| descend | 1.00 | 1.00 | 0.0636 |
| contact | 1.00 | 1.00 | 0.0071 |
| push | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.498, 0.203, 0.299) | (0.512, 0.067, 0.040)→(0.507, 0.067, 0.038) | 0.150→0.148 | 1.00 / 1.000 | 0.133 | 3.257 |
| approach_high | approach | 1.00 / step_budget | (0.498, 0.203, 0.299)→(0.503, 0.125, 0.106) | (0.507, 0.067, 0.038)→(0.502, 0.067, 0.034) | 0.148→0.147 | 1.00 / 1.000 | 0.540 | 4.034 |
| descend | descend | 1.00 / step_budget | (0.503, 0.125, 0.106)→(0.499, 0.095, 0.050) | (0.502, 0.067, 0.034)→(0.502, 0.066, 0.034) | 0.147→0.146 | 1.00 / 1.667 | 10.895 | 79.101 |
| contact | contact | 1.00 / force_exceeded | (0.499, 0.095, 0.050)→(0.497, 0.092, 0.044) | (0.502, 0.066, 0.034)→(0.502, 0.064, 0.037) | 0.146→0.144 | 1.00 / 2.000 | 1307.868 | 17.546 |
| push | push | 0.00 / guard_failure | (0.496, -0.001, 0.037)→(0.496, -0.001, 0.037) | (0.502, 0.064, 0.037)→(0.503, -0.030, 0.035) | 0.144→0.059 | 1.00 / 3.000 | 59.416 | 82.522 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.913
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.386
- phase_score: 0.520
- phase_breakdown.approach_score: 0.246
- phase_breakdown.push_score: 0.594
- phase_breakdown.contact_score: 0.572

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.466
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.386
- **Median Q (composite search score)**: 0.265
- **K-run variance**: 0.0223
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.7
- **Final σ (mean)**: 0.281


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `bf8103833c1e96f48e87b3ce39b3b3bf17e268470bd7b5c037546fb78b5150b8`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `98954a34ee744fa939070f7dadee8a411de43cdcfeddcf3b4bfc5c3a4c536020`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76136,"average_solve_count":88.0,"average_success_count":88.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_speed":0.37482,"contact.contact_force":6.37801,"descend.descend_speed":0.14679,"push.push_depth":0.19984,"push.push_duration":2.64634},"optimized_scores":{"best_composite_score":0.32631,"best_fitness_score":0.46631,"best_task_score":0.38591},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":711.0,"contact_point_centroid":[0.50344,0.00387,0.04388],"force_p95":11.69005,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.60478,"mean_force":4.42738,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49985,0.01558,0.03616]},{"body_a":"peg","body_b":"channel_base_body","contact_count":30.0,"contact_point_centroid":[0.50744,-0.10051,0.05989],"force_p95":44.11728,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.99367,"mean_force":29.74767,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50077,-0.05374,0.03399]},{"body_a":"peg","body_b":"channel_base_body","contact_count":45.0,"contact_point_centroid":[0.50493,0.04504,0.00972],"force_p95":0.6047,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.43395,"mean_force":1.01432,"phase_index":3.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.50305,0.09022,0.04585]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50448,0.07848,0.04608],"force_p95":17.6223,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.09931,"mean_force":13.32921,"phase_index":3.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.50346,0.09036,0.04627]},{"body_a":"peg","body_b":"channel_base_body","contact_count":505.0,"contact_point_centroid":[0.50618,-0.02979,0.00991],"force_p95":9.68578,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.93791,"mean_force":4.77385,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49988,0.01571,0.03619]},{"body_a":"peg","body_b":"channel_base_body","contact_count":122.0,"contact_point_centroid":[0.50591,0.06268,0.00938],"force_p95":0.552,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.14964,"mean_force":0.69109,"phase_index":2.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.5079,0.10758,0.07801]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50581,0.08067,0.05749],"force_p95":13.3636,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.826,"mean_force":9.20201,"phase_index":2.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50465,0.09255,0.05064]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":491.0,"contact_point_centroid":[0.52508,-0.01771,0.02622],"force_p95":4.71862,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.74014,"mean_force":1.23823,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49979,0.01096,0.03588]},{"body_a":"peg","body_b":"channel_base_body","contact_count":351.0,"contact_point_centroid":[0.50568,0.06297,0.00934],"force_p95":0.59723,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.58511,"phase_index":1.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.50444,0.16239,0.20035]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.53373,0.06295,0.0362],"force_p95":1.36479,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.64647,"phase_index":0.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.49923,0.20034,0.29957]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.52714,0.06295,0.02495],"force_p95":0.76857,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.85654,"mean_force":0.24853,"phase_index":1.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49763,0.20301,0.29659]}],"total_contact_groups":11},"final_pose_error":0.0678,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5074,-0.0831,0.03517],"final_tcp_position":[0.50067,-0.05472,0.03371],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":53.60478,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.5166,0.06295,0.03827],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14392,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.18909,"phase_name":"align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":20.0,"raw_peak_contact_force":2.98455,"tcp_end":[0.49787,0.20278,0.29862],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.29613,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":359.0,"n_steps_budget":600.0,"object_pos_end":[0.50596,0.06295,0.03381],"object_pos_start":[0.5166,0.06295,0.03827],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14392,"object_z_max":0.03827,"peak_contact_force":0.55423,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":365.0,"raw_peak_contact_force":3.88411,"tcp_end":[0.51189,0.1216,0.10512],"tcp_start":[0.49787,0.20278,0.29862],"tcp_to_object_dist_end":0.09252,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":122.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.06256,0.03399],"object_pos_start":[0.50596,0.06295,0.03381],"object_to_goal_dist_end":0.14282,"object_to_goal_dist_start":0.1432,"object_z_max":0.03384,"peak_contact_force":14.14964,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":124.0,"raw_peak_contact_force":14.14964,"tcp_end":[0.50458,0.09219,0.04999],"tcp_start":[0.51189,0.1216,0.10512],"tcp_to_object_dist_end":0.0337,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":45.0,"n_steps_budget":600.0,"object_pos_end":[0.50574,0.0596,0.03704],"object_pos_start":[0.50599,0.06256,0.03399],"object_to_goal_dist_end":0.13975,"object_to_goal_dist_start":0.14282,"object_z_max":0.03767,"peak_contact_force":8.59536,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":47.0,"raw_peak_contact_force":18.43395,"subtask_id":"contact","tcp_end":[0.50232,0.08846,0.04242],"tcp_start":[0.50458,0.09219,0.04999],"tcp_to_object_dist_end":0.02956,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":906.0,"n_steps_budget":1000.0,"object_pos_end":[0.50739,-0.083,0.03522],"object_pos_start":[0.50574,0.0596,0.03704],"object_to_goal_dist_end":0.0093,"object_to_goal_dist_start":0.13975,"object_z_max":0.03704,"peak_contact_force":25.99611,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1737.0,"raw_peak_contact_force":53.60478,"subtask_id":"push","tcp_end":[0.50067,-0.05472,0.03371],"tcp_start":[0.50071,-0.05472,0.03376],"tcp_to_object_dist_end":0.0291,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `cae0d95026bac46aa2e5d95cffd531753a79751757c4f25fa56c1ec6e19c2175`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,0.05661,0.04]},{"name":"goal","value":[0.53648,-0.10339,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53648,-0.10339,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77907,"average_solve_count":86.0,"average_success_count":86.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_speed":0.70957,"contact.contact_force":7.6633,"descend.descend_speed":0.22389,"push.push_depth":0.1447,"push.push_duration":2.67807},"optimized_scores":{"best_composite_score":0.26528,"best_fitness_score":0.40528,"best_task_score":0.25847},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":616.0,"contact_point_centroid":[0.50304,-0.0014,0.04376],"force_p95":15.56108,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.60789,"mean_force":4.94849,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50081,0.01037,0.03574]},{"body_a":"peg","body_b":"channel_base_body","contact_count":31.0,"contact_point_centroid":[0.50712,-0.1005,0.05844],"force_p95":41.21395,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.80108,"mean_force":29.34184,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50152,-0.05359,0.03261]},{"body_a":"peg","body_b":"channel_base_body","contact_count":540.0,"contact_point_centroid":[0.50232,-0.02415,0.00983],"force_p95":10.71908,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.30078,"mean_force":4.27823,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.5007,0.01847,0.03609]},{"body_a":"peg","body_b":"channel_base_body","contact_count":38.0,"contact_point_centroid":[0.5035,0.03878,0.00963],"force_p95":1.92254,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.14499,"mean_force":1.1299,"phase_index":3.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.50415,0.08422,0.04616]},{"body_a":"peg","body_b":"channel_base_body","contact_count":123.0,"contact_point_centroid":[0.50619,0.05612,0.00938],"force_p95":0.55769,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.96272,"mean_force":0.71479,"phase_index":2.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.51016,0.10158,0.07796]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50624,0.07438,0.05399],"force_p95":17.13221,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.82627,"mean_force":10.88562,"phase_index":2.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50575,0.08628,0.0504]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.5051,0.07242,0.04637],"force_p95":17.31827,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.76397,"mean_force":13.307,"phase_index":3.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.5045,0.08434,0.0465]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":342.0,"contact_point_centroid":[0.52508,-0.04204,0.02917],"force_p95":4.67942,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.58562,"mean_force":1.2973,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50097,-0.01291,0.03452]},{"body_a":"peg","body_b":"channel_base_body","contact_count":355.0,"contact_point_centroid":[0.50574,0.05667,0.00934],"force_p95":0.60204,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.59135,"phase_index":1.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.50611,0.15939,0.2001]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":53.0,"contact_point_centroid":[0.4749,0.03397,0.02738],"force_p95":3.55374,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.18675,"mean_force":0.83051,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50004,0.06289,0.03795]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.5365,0.05661,0.03623],"force_p95":1.44525,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.75988,"phase_index":0.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.49923,0.20034,0.29957]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":17.0,"contact_point_centroid":[0.52781,0.05661,0.01411],"force_p95":0.88065,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.04601,"mean_force":0.25192,"phase_index":1.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49768,0.20275,0.29592]}],"total_contact_groups":12},"final_pose_error":0.01926,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50709,-0.0834,0.03503],"final_tcp_position":[0.50149,-0.05472,0.03234],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":51.60789,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.52027,0.05661,0.03869],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13812,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.14277,"phase_name":"align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":20.0,"raw_peak_contact_force":3.83578,"tcp_end":[0.49787,0.20278,0.29862],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.29905,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":364.0,"n_steps_budget":600.0,"object_pos_end":[0.50615,0.05661,0.03377],"object_pos_start":[0.52027,0.05661,0.03869],"object_to_goal_dist_end":0.13689,"object_to_goal_dist_start":0.13812,"object_z_max":0.03869,"peak_contact_force":0.53735,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":372.0,"raw_peak_contact_force":4.44541,"tcp_end":[0.51519,0.11585,0.10523],"tcp_start":[0.49787,0.20278,0.29862],"tcp_to_object_dist_end":0.09326,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":123.0,"n_steps_budget":600.0,"object_pos_end":[0.50608,0.05624,0.0339],"object_pos_start":[0.50615,0.05661,0.03377],"object_to_goal_dist_end":0.13651,"object_to_goal_dist_start":0.13689,"object_z_max":0.0338,"peak_contact_force":17.96272,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":125.0,"raw_peak_contact_force":17.96272,"tcp_end":[0.50565,0.08592,0.04975],"tcp_start":[0.51519,0.11585,0.10523],"tcp_to_object_dist_end":0.03365,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":38.0,"n_steps_budget":600.0,"object_pos_end":[0.50573,0.05369,0.03667],"object_pos_start":[0.50608,0.05624,0.0339],"object_to_goal_dist_end":0.13386,"object_to_goal_dist_start":0.13651,"object_z_max":0.03703,"peak_contact_force":8.92334,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":40.0,"raw_peak_contact_force":18.14499,"subtask_id":"contact","tcp_end":[0.50332,0.08269,0.04311],"tcp_start":[0.50565,0.08592,0.04975],"tcp_to_object_dist_end":0.0298,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":876.0,"n_steps_budget":990.0,"object_pos_end":[0.50709,-0.08332,0.03506],"object_pos_start":[0.50573,0.05369,0.03667],"object_to_goal_dist_end":0.00926,"object_to_goal_dist_start":0.13386,"object_z_max":0.03676,"peak_contact_force":25.70449,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1582.0,"raw_peak_contact_force":51.60789,"subtask_id":"push","tcp_end":[0.50149,-0.05472,0.03234],"tcp_start":[0.50152,-0.05471,0.03238],"tcp_to_object_dist_end":0.02928,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `fd7ada9a67242f1adcdb6e23860d1223cdc8a17daf859e94e1687ff0564d9575`; realized-scene SHA-256: `8df62a5afc1e0110114ab6e06b493b5783d0c746729f7f7f1f2cb046babeda91`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47029,0.07994,0.04]},{"name":"goal","value":[0.47029,-0.08006,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.47029,0.07994,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.47029,-0.08006,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73077,"average_solve_count":52.0,"average_success_count":52.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_speed":0.626,"contact.contact_force":11.24884,"descend.descend_speed":0.21773,"push.push_depth":0.1412,"push.push_duration":1.89078},"optimized_scores":{"best_composite_score":-0.01663,"best_fitness_score":0.12337,"best_task_score":0.00582},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47493,0.11163,0.05926],"force_p95":181.13214,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":205.1892,"mean_force":74.997,"phase_index":2.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.48665,0.11231,0.05746]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.475,0.10613,0.0473],"force_p95":141.5632,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":142.35347,"mean_force":134.45071,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48686,0.10614,0.04545]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.475,0.10654,0.04816],"force_p95":15.8157,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":16.05904,"mean_force":13.6256,"phase_index":3.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.48686,0.10654,0.04632]},{"body_a":"peg","body_b":"channel_base_body","contact_count":131.0,"contact_point_centroid":[0.49401,0.07946,0.00938],"force_p95":0.58227,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.8953,"mean_force":0.66191,"phase_index":2.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.4843,0.12317,0.07836]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.49077,0.0976,0.05877],"force_p95":13.73503,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.39249,"mean_force":7.81786,"phase_index":2.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.4877,0.10941,0.05208]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.50239,0.06409,0.00952],"force_p95":6.87646,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.47027,"mean_force":1.63429,"phase_index":3.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.48715,0.10713,0.0476]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.49076,0.09499,0.05297],"force_p95":7.60894,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.19037,"mean_force":3.16044,"phase_index":3.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.48686,0.10643,0.04607]},{"body_a":"peg","body_b":"channel_base_body","contact_count":335.0,"contact_point_centroid":[0.49434,0.07989,0.00936],"force_p95":0.61343,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.58461,"phase_index":1.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.48977,0.17019,0.20135]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":20.0,"contact_point_centroid":[0.46621,0.07994,0.03877],"force_p95":1.38176,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.64457,"phase_index":0.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.49923,0.20034,0.29957]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":15.0,"contact_point_centroid":[0.47289,0.07995,0.02378],"force_p95":0.64934,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.74814,"mean_force":0.21246,"phase_index":1.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49734,0.20303,0.29638]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.49145,0.0947,0.06096],"force_p95":0.17958,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18104,"mean_force":0.1583,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48686,0.10612,0.04541]}],"total_contact_groups":11},"final_pose_error":0.15192,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49545,0.07739,0.03568],"final_tcp_position":[0.48682,0.10604,0.04522],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":3906.0865,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.4833,0.07995,0.03833],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.16082,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.06788,"phase_name":"align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":20.0,"raw_peak_contact_force":2.95027,"tcp_end":[0.49787,0.20278,0.29862],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.28819,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":343.0,"n_steps_budget":600.0,"object_pos_end":[0.49381,0.07996,0.03378],"object_pos_start":[0.4833,0.07995,0.03833],"object_to_goal_dist_end":0.1602,"object_to_goal_dist_start":0.16082,"object_z_max":0.03833,"peak_contact_force":0.52908,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":350.0,"raw_peak_contact_force":3.77147,"tcp_end":[0.48237,0.13717,0.10677],"tcp_start":[0.49787,0.20278,0.29862],"tcp_to_object_dist_end":0.09344,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":131.0,"n_steps_budget":600.0,"object_pos_end":[0.4943,0.07898,0.0343],"object_pos_start":[0.49381,0.07996,0.03378],"object_to_goal_dist_end":0.15918,"object_to_goal_dist_start":0.1602,"object_z_max":0.03418,"peak_contact_force":0.57276,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":137.0,"raw_peak_contact_force":205.1892,"tcp_end":[0.48798,0.10816,0.04971],"tcp_start":[0.48237,0.13717,0.10677],"tcp_to_object_dist_end":0.03359,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":24.0,"n_steps_budget":600.0,"object_pos_end":[0.49517,0.07783,0.03593],"object_pos_start":[0.4943,0.07898,0.0343],"object_to_goal_dist_end":0.15796,"object_to_goal_dist_start":0.15918,"object_z_max":0.03595,"peak_contact_force":3906.0865,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":30.0,"raw_peak_contact_force":16.05904,"subtask_id":"contact","tcp_end":[0.48686,0.10616,0.04551],"tcp_start":[0.48798,0.10816,0.04971],"tcp_to_object_dist_end":0.03104,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":960.0,"object_pos_end":[0.49527,0.07769,0.03588],"object_pos_start":[0.49517,0.07783,0.03593],"object_to_goal_dist_end":0.15782,"object_to_goal_dist_start":0.15796,"object_z_max":0.03593,"peak_contact_force":126.54794,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":142.35347,"subtask_id":"push","tcp_end":[0.48682,0.10604,0.04522],"tcp_start":[0.48686,0.10608,0.04531],"tcp_to_object_dist_end":0.03101,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```