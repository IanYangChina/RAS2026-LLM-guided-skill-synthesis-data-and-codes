## Search State

- **Seed**: 9
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | align → approach → descend → contact → push | joint_interpolation | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 7 | 0.2295 | 0.09 | ❌ rejected |
| 9 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 5 | 0.1992 | 0.00 | ❌ rejected |
| 8 | align → approach → approach → descend → contact → push | joint_interpolation | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 7 | 0.0611 | 0.34 | ✅ accepted |
| 7 | align → approach → descend → contact → push | joint_interpolation | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 5 | 0.1917 | 0.22 | ✅ accepted |
| 6 | align → approach → contact → push | joint_interpolation | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 4 | 0.1554 | 0.13 | ✅ accepted |

**Proposal policy**: task_score is 0.09 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.229) — your mutation base

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
- id: approach_entry
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.16
    - -0.01
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    entry_speed:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.5
      binds_to:
      - path: generator.speed
        mode: replace
- id: approach_peg
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
    - 0.0
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
  subtask_id: approach
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
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: push_force_guard
    when: during_phase
    predicate: force_below
    threshold: 50.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
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
- **approach_entry** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.16, -0.01], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - entry_speed: status=consumed; consumers=generator.speed (replace)
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.0], tolerance=0.02
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
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=push_force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=50.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.229
- **task_score** (E): 0.087
- **fitness_score**: 0.419  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align | 1.00 | 1.00 | 0.0041 |
| approach_entry | 1.00 | 1.00 | 0.2276 |
| descend | 1.00 | 1.00 | 0.0569 |
| contact | 1.00 | 1.00 | 0.0004 |
| push | 1.00 | 1.00 | 0.1562 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.498, 0.203, 0.299) | (0.512, 0.067, 0.040)→(0.507, 0.067, 0.038) | 0.150→0.148 | 1.00 / 1.000 | 0.133 | 3.257 |
| approach_entry | approach | 1.00 / step_budget | (0.498, 0.203, 0.299)→(0.498, 0.068, 0.115) | (0.507, 0.067, 0.038)→(0.502, 0.067, 0.034) | 0.148→0.147 | 1.00 / 1.000 | 0.557 | 4.034 |
| descend | descend | 1.00 / step_budget | (0.498, 0.068, 0.115)→(0.496, 0.076, 0.059) | (0.502, 0.067, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 2.000 | 87.265 | 87.265 |
| contact | contact | 1.00 / force_exceeded | (0.496, 0.076, 0.059)→(0.496, 0.076, 0.059) | (0.502, 0.067, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 2.000 | 82.152 | 82.152 |
| push | push | 1.00 / time_limit | (0.496, 0.076, 0.059)→(0.496, -0.078, 0.035) | (0.502, 0.067, 0.034)→(0.496, 0.009, 0.024) | 0.147→0.090 | 1.00 / 1.000 | 0.587 | 109.338 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.388
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.095
- phase_score: 0.668
- phase_breakdown.approach_score: 0.168
- phase_breakdown.push_score: 0.904
- phase_breakdown.contact_score: 0.460

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.438
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.096
- **Median Q (composite search score)**: 0.241
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.449


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.33766,"average_solve_count":77.0,"average_success_count":77.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_entry.arc_height":0.09013,"approach_entry.entry_speed":0.68031,"contact.contact_force":9.92323,"descend.descend_speed":0.09531,"push.push_depth":0.19466,"push.push_duration":1.85443,"push.push_speed":0.09571},"optimized_scores":{"best_composite_score":0.24848,"best_fitness_score":0.43848,"best_task_score":0.09466},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":996.0,"contact_point_centroid":[0.50472,0.02265,0.0086],"force_p95":112.79217,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.73981,"mean_force":48.86035,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49953,-0.00028,0.04848]},{"body_a":"attachment","body_b":"peg","contact_count":657.0,"contact_point_centroid":[0.50906,0.03077,0.0537],"force_p95":112.8419,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":116.51679,"mean_force":73.16989,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50001,0.02692,0.05356]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50287,0.08055,0.0093],"force_p95":99.0935,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":99.0935,"mean_force":99.0935,"phase_index":3.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.49642,0.07603,0.05902]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50826,0.07531,0.05793],"force_p95":98.66533,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":98.66533,"mean_force":98.66533,"phase_index":3.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.49642,0.07603,0.05902]},{"body_a":"peg","body_b":"channel_base_body","contact_count":115.0,"contact_point_centroid":[0.50647,0.06319,0.00938],"force_p95":0.55251,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":77.41954,"mean_force":2.22853,"phase_index":2.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49646,0.07195,0.08804]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.5082,0.07533,0.05844],"force_p95":76.10759,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":76.9979,"mean_force":64.67882,"phase_index":2.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49635,0.07584,0.05991]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":253.0,"contact_point_centroid":[0.5251,0.03631,0.05409],"force_p95":12.5789,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.58115,"mean_force":7.30662,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.5015,0.02563,0.05468]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.47499,-0.02158,0.02433],"force_p95":7.53981,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.55166,"mean_force":3.44703,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49857,-0.05673,0.03794]},{"body_a":"peg","body_b":"channel_base_body","contact_count":476.0,"contact_point_centroid":[0.50564,0.06301,0.00935],"force_p95":0.5787,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.57498,"phase_index":1.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.49814,0.0981,0.23686]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.53373,0.06295,0.0362],"force_p95":1.36479,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.64647,"phase_index":0.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.49923,0.20034,0.29957]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.52714,0.06295,0.02495],"force_p95":0.76857,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.85654,"mean_force":0.24853,"phase_index":1.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.4971,0.2013,0.29839]}],"total_contact_groups":11},"final_pose_error":0.05165,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4964,0.00086,0.02463],"final_tcp_position":[0.49965,-0.0804,0.03496],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":117.73981,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.5166,0.06295,0.03827],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14392,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.18909,"phase_name":"align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":20.0,"raw_peak_contact_force":2.98455,"tcp_end":[0.49787,0.20278,0.29862],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.29613,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.50602,0.06303,0.03381],"object_pos_start":[0.5166,0.06295,0.03827],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14392,"object_z_max":0.03827,"peak_contact_force":0.55142,"phase_name":"approach_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":490.0,"raw_peak_contact_force":3.88411,"tcp_end":[0.49752,0.06814,0.11567],"tcp_start":[0.49787,0.20278,0.29862],"tcp_to_object_dist_end":0.08246,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":115.0,"n_steps_budget":600.0,"object_pos_end":[0.50601,0.063,0.03367],"object_pos_start":[0.50602,0.06303,0.03381],"object_to_goal_dist_end":0.14327,"object_to_goal_dist_start":0.14329,"object_z_max":0.03381,"peak_contact_force":77.41954,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":118.0,"raw_peak_contact_force":77.41954,"tcp_end":[0.49642,0.07603,0.05902],"tcp_start":[0.49752,0.06814,0.11567],"tcp_to_object_dist_end":0.03007,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50591,0.06302,0.03362],"object_pos_start":[0.50601,0.063,0.03367],"object_to_goal_dist_end":0.14328,"object_to_goal_dist_start":0.14327,"object_z_max":0.03367,"peak_contact_force":99.0935,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":99.0935,"subtask_id":"contact","tcp_end":[0.49625,0.07606,0.05867],"tcp_start":[0.49642,0.07603,0.05902],"tcp_to_object_dist_end":0.02985,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4964,0.00086,0.02463],"object_pos_start":[0.50591,0.06302,0.03362],"object_to_goal_dist_end":0.08238,"object_to_goal_dist_start":0.14328,"object_z_max":0.04007,"peak_contact_force":0.51939,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1915.0,"raw_peak_contact_force":117.73981,"tcp_end":[0.49965,-0.0804,0.03496],"tcp_start":[0.49625,0.07606,0.05867],"tcp_to_object_dist_end":0.08197,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.17284,"average_solve_count":81.0,"average_success_count":81.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_entry.arc_height":0.11822,"approach_entry.entry_speed":0.71691,"contact.contact_force":5.55085,"descend.descend_speed":0.06643,"push.push_depth":0.19957,"push.push_duration":2.59238,"push.push_speed":0.09388},"optimized_scores":{"best_composite_score":0.24065,"best_fitness_score":0.43065,"best_task_score":0.07132},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":996.0,"contact_point_centroid":[0.50602,0.016,0.00852],"force_p95":118.69013,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":123.57732,"mean_force":57.75805,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50013,6e-05,0.04958]},{"body_a":"attachment","body_b":"peg","contact_count":735.0,"contact_point_centroid":[0.50992,0.02405,0.05353],"force_p95":118.49234,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":122.45029,"mean_force":77.54904,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50061,0.02068,0.05335]},{"body_a":"peg","body_b":"channel_base_body","contact_count":114.0,"contact_point_centroid":[0.50645,0.05726,0.00937],"force_p95":0.62132,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":105.96322,"mean_force":3.59664,"phase_index":2.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.4965,0.06924,0.0863]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50829,0.07389,0.0583],"force_p95":104.74765,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":105.54062,"mean_force":87.02873,"phase_index":2.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49644,0.07444,0.05964]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51228,0.07347,0.00934],"force_p95":67.61977,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":67.61977,"mean_force":67.61977,"phase_index":3.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.4966,0.07472,0.05866]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50844,0.07389,0.05778],"force_p95":67.38301,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.38301,"mean_force":67.38301,"phase_index":3.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.4966,0.07472,0.05866]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":310.0,"contact_point_centroid":[0.52507,0.02573,0.05171],"force_p95":12.20673,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.39078,"mean_force":6.55745,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50215,0.01696,0.05415]},{"body_a":"peg","body_b":"channel_base_body","contact_count":519.0,"contact_point_centroid":[0.50584,0.05663,0.00935],"force_p95":0.60398,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.5772,"phase_index":1.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.49854,0.0821,0.24183]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.5365,0.05661,0.03623],"force_p95":1.44525,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.75988,"phase_index":0.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.49923,0.20034,0.29957]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":17.0,"contact_point_centroid":[0.52781,0.05661,0.01411],"force_p95":0.88065,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.04601,"mean_force":0.25192,"phase_index":1.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.49692,0.20036,0.29902]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47499,-0.03338,0.02421],"force_p95":0.40557,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41002,"mean_force":0.36674,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49864,-0.06203,0.03815]}],"total_contact_groups":11},"final_pose_error":0.06424,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4962,-0.00998,0.0242],"final_tcp_position":[0.49937,-0.07902,0.03611],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":123.57732,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.52027,0.05661,0.03869],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13812,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.14277,"phase_name":"align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":20.0,"raw_peak_contact_force":3.83578,"tcp_end":[0.49787,0.20278,0.29862],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.29905,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":528.0,"n_steps_budget":600.0,"object_pos_end":[0.50611,0.05667,0.03377],"object_pos_start":[0.52027,0.05661,0.03869],"object_to_goal_dist_end":0.13695,"object_to_goal_dist_start":0.13812,"object_z_max":0.03869,"peak_contact_force":0.54117,"phase_name":"approach_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":536.0,"raw_peak_contact_force":4.44541,"tcp_end":[0.49753,0.06422,0.11225],"tcp_start":[0.49787,0.20278,0.29862],"tcp_to_object_dist_end":0.07931,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":114.0,"n_steps_budget":720.0,"object_pos_end":[0.50619,0.05669,0.03374],"object_pos_start":[0.50611,0.05667,0.03377],"object_to_goal_dist_end":0.13697,"object_to_goal_dist_start":0.13695,"object_z_max":0.03378,"peak_contact_force":105.96322,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":118.0,"raw_peak_contact_force":105.96322,"tcp_end":[0.4966,0.07472,0.05866],"tcp_start":[0.49753,0.06422,0.11225],"tcp_to_object_dist_end":0.03221,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50608,0.05672,0.0337],"object_pos_start":[0.50619,0.05669,0.03374],"object_to_goal_dist_end":0.137,"object_to_goal_dist_start":0.13697,"object_z_max":0.03374,"peak_contact_force":67.61977,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":67.61977,"subtask_id":"contact","tcp_end":[0.49642,0.07477,0.05834],"tcp_start":[0.4966,0.07472,0.05866],"tcp_to_object_dist_end":0.03203,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4962,-0.00998,0.0242],"object_pos_start":[0.50608,0.05672,0.0337],"object_to_goal_dist_end":0.07188,"object_to_goal_dist_start":0.137,"object_z_max":0.04002,"peak_contact_force":0.55901,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2044.0,"raw_peak_contact_force":123.57732,"tcp_end":[0.49937,-0.07902,0.03611],"tcp_start":[0.49642,0.07477,0.05834],"tcp_to_object_dist_end":0.07013,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.20779,"average_solve_count":77.0,"average_success_count":77.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_entry.arc_height":0.07315,"approach_entry.entry_speed":0.33711,"contact.contact_force":8.80996,"descend.descend_speed":0.09457,"push.push_depth":0.18314,"push.push_duration":1.32155,"push.push_speed":0.09538},"optimized_scores":{"best_composite_score":0.1993,"best_fitness_score":0.3893,"best_task_score":0.09648},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":993.0,"contact_point_centroid":[0.49655,0.04788,0.00871],"force_p95":83.0587,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":86.69792,"mean_force":25.53833,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49343,0.00149,0.04589]},{"body_a":"attachment","body_b":"peg","contact_count":411.0,"contact_point_centroid":[0.50265,0.05516,0.05527],"force_p95":81.63979,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.40787,"mean_force":58.80012,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49674,0.04654,0.05495]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50826,0.07685,0.05811],"force_p95":79.74399,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.74399,"mean_force":79.74399,"phase_index":3.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.49639,0.07703,0.05933]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50907,0.07051,0.00934],"force_p95":79.14922,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":79.14922,"mean_force":79.14922,"phase_index":3.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.49639,0.07703,0.05933]},{"body_a":"peg","body_b":"channel_base_body","contact_count":117.0,"contact_point_centroid":[0.494,0.08004,0.00938],"force_p95":0.58324,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":78.41119,"mean_force":1.68377,"phase_index":2.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.4964,0.07422,0.08926]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.5082,0.07676,0.05848],"force_p95":76.89876,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":78.03033,"mean_force":66.71463,"phase_index":2.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49633,0.07696,0.06]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":397.0,"contact_point_centroid":[0.47495,0.07263,0.0161],"force_p95":7.90323,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.81371,"mean_force":4.73256,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49682,0.04508,0.05482]},{"body_a":"peg","body_b":"channel_base_body","contact_count":440.0,"contact_point_centroid":[0.49416,0.07994,0.00936],"force_p95":0.60603,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.5756,"phase_index":1.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.49794,0.10731,0.23165]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":20.0,"contact_point_centroid":[0.46621,0.07994,0.03877],"force_p95":1.38176,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.64457,"phase_index":0.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.49923,0.20034,0.29957]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":15.0,"contact_point_centroid":[0.47289,0.07995,0.02378],"force_p95":0.64934,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.74814,"mean_force":0.21246,"phase_index":1.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.4972,0.2012,0.298]}],"total_contact_groups":10},"final_pose_error":0.02776,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49648,0.03539,0.02413],"final_tcp_position":[0.49027,-0.07565,0.03283],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":86.69792,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.4833,0.07995,0.03833],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.16082,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.06788,"phase_name":"align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":20.0,"raw_peak_contact_force":2.95027,"tcp_end":[0.49787,0.20278,0.29862],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.28819,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":448.0,"n_steps_budget":600.0,"object_pos_end":[0.49383,0.07993,0.03378],"object_pos_start":[0.4833,0.07995,0.03833],"object_to_goal_dist_end":0.16017,"object_to_goal_dist_start":0.16082,"object_z_max":0.03833,"peak_contact_force":0.57952,"phase_name":"approach_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":455.0,"raw_peak_contact_force":3.77147,"tcp_end":[0.49749,0.07162,0.11787],"tcp_start":[0.49787,0.20278,0.29862],"tcp_to_object_dist_end":0.08458,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":117.0,"n_steps_budget":600.0,"object_pos_end":[0.49387,0.07994,0.03373],"object_pos_start":[0.49383,0.07993,0.03378],"object_to_goal_dist_end":0.16018,"object_to_goal_dist_start":0.16017,"object_z_max":0.03378,"peak_contact_force":78.41119,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":119.0,"raw_peak_contact_force":78.41119,"tcp_end":[0.49639,0.07703,0.05933],"tcp_start":[0.49749,0.07162,0.11787],"tcp_to_object_dist_end":0.02588,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49376,0.07996,0.03362],"object_pos_start":[0.49387,0.07994,0.03373],"object_to_goal_dist_end":0.16021,"object_to_goal_dist_start":0.16018,"object_z_max":0.03373,"peak_contact_force":79.74399,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":79.74399,"subtask_id":"contact","tcp_end":[0.49619,0.07704,0.05895],"tcp_start":[0.49639,0.07703,0.05933],"tcp_to_object_dist_end":0.02561,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49648,0.03539,0.02413],"object_pos_start":[0.49376,0.07996,0.03362],"object_to_goal_dist_end":0.11653,"object_to_goal_dist_start":0.16021,"object_z_max":0.04028,"peak_contact_force":0.68339,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1801.0,"raw_peak_contact_force":86.69792,"tcp_end":[0.49027,-0.07565,0.03283],"tcp_start":[0.49619,0.07704,0.05895],"tcp_to_object_dist_end":0.11155,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```