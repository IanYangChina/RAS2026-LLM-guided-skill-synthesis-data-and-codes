## Search State

- **Seed**: 0
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 11 | -0.1634 | 0.00 | ❌ rejected |
| 9 | approach → descend → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 10 | 0.1128 | 0.48 | ❌ rejected |
| 8 | approach → approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | -0.0107 | 0.35 | ❌ rejected |
| 7 | approach → approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | -0.0635 | 0.00 | ❌ rejected |
| 6 | approach → approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.4735 | 0.82 | ❌ rejected |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`
- Frozen object start: [0.5109569349857164, 0.061582937101109625, 0.04]
- Frozen task target: [0.5109569349857164, -0.09841706289889038, 0.04]
- Goal object position: (0.5109569349857164, -0.09841706289889038, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5109569349857164, 0.061582937101109625, 0.04)
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
  frozen_object_start: [0.511, 0.0616, 0.04]
  frozen_task_target: [0.511, -0.0984, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5109569349857164, 0.061582937101109625, 0.04]}
  frozen_targets: {'channel_exit': [0.5109569349857164, -0.09841706289889038, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454

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

## Current Skill (Q=-0.163) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
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
    - 0.04
    - 0.08
    orientation:
      mode: none
  parameters:
    clearance_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: approach_final
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
    orientation:
      mode: none
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: contact_peg
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
    - 0.02
    - 0.0
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
- id: push_through
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
      distance: 0.18
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.16
      - 0.25
      default: 0.18
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
    push_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_high** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.08]
  - orientation: mode=none
  - parameter_bindings:
    - clearance_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **approach_final** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.0]
  - orientation: mode=none
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_peg** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_through** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.18, mode=replace_offset_projection, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: -0.163
- **task_score** (E): 0.000
- **fitness_score**: 0.197  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.610

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 1.00 | 1.00 | 0.1835 |
| approach_final | 1.00 | 1.00 | 0.0911 |
| contact_peg | 1.00 | 1.00 | 0.0091 |
| push_through | 0.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.125, 0.133) | (0.498, 0.080, 0.040)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.565 | 2.179 |
| approach_final | approach | 1.00 / step_budget | (0.495, 0.125, 0.133)→(0.495, 0.120, 0.042) | (0.500, 0.080, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.532 | 0.614 |
| contact_peg | contact | 1.00 / force_exceeded | (0.495, 0.120, 0.042)→(0.493, 0.114, 0.036) | (0.500, 0.080, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 2.000 | 19.144 | 19.144 |
| push_through | push | 0.00 / guard_failure | (0.493, 0.114, 0.036)→(0.493, 0.114, 0.036) | (0.500, 0.080, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 2.000 | 69.864 | 72.959 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.340
- phase_breakdown.push_score: 0.011
- phase_breakdown.contact_score: 0.765
- phase_breakdown.approach_score: 0.903

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.204
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.001
- **Median Q (composite search score)**: -0.163
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.306


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d6915c31707ac435a9367b840736087e39a7a48adfeb36a4f94b6b3ae57cce94`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `19172182883d287409b73cab43749e937e65f1ca1d4501d52b4a913a881aad36`; realized-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51096,0.06158,0.04]},{"name":"goal","value":[0.51096,-0.09842,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51096,0.06158,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51096,-0.09842,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.86508,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_final.speed":0.05925,"approach_high.clearance_height":0.05003,"approach_high.speed":0.05167,"contact_peg.contact_force":12.04822,"contact_peg.speed":0.03722,"push_through.force_limit_guard":38.99983,"push_through.lateral_offset":0.01195,"push_through.push_distance":0.22155,"push_through.push_speed":0.03435,"push_through.push_tolerance":0.03456,"push_through.retry_lateral_shift":0.01299},"optimized_scores":{"best_composite_score":-0.17135,"best_fitness_score":0.18865,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54279,0.09673,0.05996],"force_p95":54.41643,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":54.73212,"mean_force":51.94788,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49805,0.09578,0.03636]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5428,0.09681,0.05999],"force_p95":18.04237,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":18.04237,"mean_force":18.04237,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49806,0.09586,0.03643]},{"body_a":"peg","body_b":"channel_base_body","contact_count":737.0,"contact_point_centroid":[0.50363,0.06159,0.00934],"force_p95":0.64162,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55752,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.50257,0.15211,0.19494]},{"body_a":"peg","body_b":"channel_base_body","contact_count":181.0,"contact_point_centroid":[0.50386,0.06161,0.00936],"force_p95":0.64135,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64277,"mean_force":0.54664,"phase_index":1.0,"phase_name":"approach_final","phase_type":"approach","tcp_position_centroid":[0.50298,0.10419,0.07051]},{"body_a":"peg","body_b":"channel_base_body","contact_count":75.0,"contact_point_centroid":[0.50445,0.06142,0.00936],"force_p95":0.64131,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64235,"mean_force":0.54467,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49882,0.09878,0.03903]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.48592,0.0638,0.00935],"force_p95":0.63394,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63856,"mean_force":0.59477,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49805,0.09578,0.03636]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49967,0.19915,0.29871]}],"total_contact_groups":7},"final_pose_error":0.25632,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50367,0.0616,0.03377],"final_tcp_position":[0.49805,0.09574,0.03632],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":54.73212,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":760.0,"n_steps_budget":1000.0,"object_pos_end":[0.50385,0.06159,0.03376],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14178,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.59497,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":756.0,"raw_peak_contact_force":2.17216,"tcp_end":[0.50677,0.10669,0.09739],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07806,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":181.0,"n_steps_budget":690.0,"object_pos_end":[0.50384,0.06159,0.03377],"object_pos_start":[0.50385,0.06159,0.03376],"object_to_goal_dist_end":0.14178,"object_to_goal_dist_start":0.14178,"object_z_max":0.03377,"peak_contact_force":0.55409,"phase_name":"approach_final","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":181.0,"raw_peak_contact_force":0.64277,"subtask_id":"approach","tcp_end":[0.50064,0.10195,0.04304],"tcp_start":[0.50677,0.10669,0.09739],"tcp_to_object_dist_end":0.04153,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":75.0,"n_steps_budget":600.0,"object_pos_end":[0.50371,0.06158,0.03376],"object_pos_start":[0.50384,0.06159,0.03377],"object_to_goal_dist_end":0.14177,"object_to_goal_dist_start":0.14178,"object_z_max":0.03377,"peak_contact_force":18.04237,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":76.0,"raw_peak_contact_force":18.04237,"subtask_id":"contact","tcp_end":[0.49806,0.09581,0.03639],"tcp_start":[0.50064,0.10195,0.04304],"tcp_to_object_dist_end":0.03479,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50368,0.06159,0.03376],"object_pos_start":[0.50371,0.06158,0.03376],"object_to_goal_dist_end":0.14178,"object_to_goal_dist_start":0.14177,"object_z_max":0.03376,"peak_contact_force":54.73212,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":54.73212,"subtask_id":"push","tcp_end":[0.49805,0.09574,0.03632],"tcp_start":[0.49805,0.09575,0.03634],"tcp_to_object_dist_end":0.0347,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `f24211f27d4adabdef509c8ed61621317fdbcaa86fc9ac888f85a717335bb714`; realized-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,0.11604,0.04]},{"name":"goal","value":[0.50095,-0.04396,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.11604,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50095,-0.04396,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.03774,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_final.speed":0.03034,"approach_high.clearance_height":0.14306,"approach_high.speed":0.06993,"contact_peg.contact_force":12.02853,"contact_peg.speed":0.02604,"push_through.force_limit_guard":49.95256,"push_through.lateral_offset":0.00928,"push_through.push_distance":0.21645,"push_through.push_speed":0.07039,"push_through.push_tolerance":0.02401,"push_through.retry_lateral_shift":-0.01746},"optimized_scores":{"best_composite_score":-0.15586,"best_fitness_score":0.20414,"best_task_score":0.00018},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.54727,0.12,0.05996],"force_p95":85.50468,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":87.32966,"mean_force":62.90978,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49461,0.14636,0.03441]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54729,0.12,0.06],"force_p95":12.73856,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":12.73856,"mean_force":12.73856,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.4946,0.14648,0.03447]},{"body_a":"peg","body_b":"channel_base_body","contact_count":352.0,"contact_point_centroid":[0.50102,0.11608,0.00935],"force_p95":0.64351,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.56714,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49833,0.17972,0.2439]},{"body_a":"peg","body_b":"channel_base_body","contact_count":124.0,"contact_point_centroid":[0.50072,0.11582,0.00942],"force_p95":0.60872,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64644,"mean_force":0.54294,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49495,0.15028,0.03742]},{"body_a":"peg","body_b":"channel_base_body","contact_count":507.0,"contact_point_centroid":[0.50085,0.116,0.00943],"force_p95":0.60712,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64535,"mean_force":0.54216,"phase_index":1.0,"phase_name":"approach_final","phase_type":"approach","tcp_position_centroid":[0.49642,0.15747,0.11722]},{"body_a":"peg","body_b":"channel_base_body","contact_count":6.0,"contact_point_centroid":[0.51254,0.11889,0.00938],"force_p95":0.62715,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63755,"mean_force":0.54862,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49461,0.14636,0.03441]}],"total_contact_groups":6},"final_pose_error":0.24719,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50087,0.11601,0.03379],"final_tcp_position":[0.49462,0.14627,0.03439],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":87.32966,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":368.0,"n_steps_budget":1000.0,"object_pos_end":[0.50096,0.11601,0.03391],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.1961,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.55062,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":352.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.49818,0.1603,0.19156],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16378,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":507.0,"n_steps_budget":1000.0,"object_pos_end":[0.50093,0.11609,0.03396],"object_pos_start":[0.50096,0.11601,0.03391],"object_to_goal_dist_end":0.19618,"object_to_goal_dist_start":0.1961,"object_z_max":0.034,"peak_contact_force":0.49563,"phase_name":"approach_final","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":507.0,"raw_peak_contact_force":0.64535,"subtask_id":"approach","tcp_end":[0.49683,0.15526,0.04291],"tcp_start":[0.49818,0.1603,0.19156],"tcp_to_object_dist_end":0.04039,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":124.0,"n_steps_budget":600.0,"object_pos_end":[0.50101,0.11603,0.0338],"object_pos_start":[0.50093,0.11609,0.03396],"object_to_goal_dist_end":0.19613,"object_to_goal_dist_start":0.19618,"object_z_max":0.03396,"peak_contact_force":12.73856,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":125.0,"raw_peak_contact_force":12.73856,"subtask_id":"contact","tcp_end":[0.4946,0.14644,0.03445],"tcp_start":[0.49683,0.15526,0.04291],"tcp_to_object_dist_end":0.03109,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.50096,0.11603,0.0338],"object_pos_start":[0.50101,0.11603,0.0338],"object_to_goal_dist_end":0.19613,"object_to_goal_dist_start":0.19613,"object_z_max":0.0338,"peak_contact_force":80.02974,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":12.0,"raw_peak_contact_force":87.32966,"subtask_id":"push","tcp_end":[0.49462,0.14627,0.03439],"tcp_start":[0.49461,0.14628,0.03439],"tcp_to_object_dist_end":0.03091,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d098a7862ff18c9bbe982af3446a89a0fa6bcfa8790d7d955f65b2375d67a881`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.87603,"average_solve_count":121.0,"average_success_count":121.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_final.speed":0.05874,"approach_high.clearance_height":0.06239,"approach_high.speed":0.05618,"contact_peg.contact_force":7.34766,"contact_peg.speed":0.03027,"push_through.force_limit_guard":44.447,"push_through.lateral_offset":0.00682,"push_through.push_distance":0.19767,"push_through.push_speed":0.06202,"push_through.push_tolerance":0.03738,"push_through.retry_lateral_shift":-0.00094},"optimized_scores":{"best_composite_score":-0.16287,"best_fitness_score":0.19713,"best_task_score":0.00066},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.53212,0.10174,0.0599],"force_p95":76.31919,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":76.81538,"mean_force":53.82989,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48685,0.10033,0.03733]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53214,0.10191,0.05998],"force_p95":26.64972,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":26.64972,"mean_force":26.64972,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48687,0.10049,0.03747]},{"body_a":"peg","body_b":"channel_base_body","contact_count":674.0,"contact_point_centroid":[0.49532,0.06397,0.00937],"force_p95":0.56638,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55819,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.48833,0.1532,0.20105]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49929,0.19867,0.29748]},{"body_a":"peg","body_b":"channel_base_body","contact_count":260.0,"contact_point_centroid":[0.495,0.06347,0.0094],"force_p95":0.55038,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55289,"mean_force":0.54531,"phase_index":1.0,"phase_name":"approach_final","phase_type":"approach","tcp_position_centroid":[0.48235,0.10636,0.0756]},{"body_a":"peg","body_b":"channel_base_body","contact_count":42.0,"contact_point_centroid":[0.49512,0.06608,0.0094],"force_p95":0.55199,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55238,"mean_force":0.54566,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48739,0.10221,0.0392]},{"body_a":"peg","body_b":"channel_base_body","contact_count":6.0,"contact_point_centroid":[0.49512,0.04757,0.0094],"force_p95":0.54669,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54796,"mean_force":0.5411,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48685,0.10033,0.03733]}],"total_contact_groups":7},"final_pose_error":0.23471,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49532,0.06371,0.03401],"final_tcp_position":[0.48684,0.10019,0.03725],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":76.81538,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":701.0,"n_steps_budget":1000.0,"object_pos_end":[0.49489,0.06374,0.03397],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14396,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.55032,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":702.0,"raw_peak_contact_force":2.44546,"tcp_end":[0.47882,0.10926,0.1103],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09032,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":260.0,"n_steps_budget":840.0,"object_pos_end":[0.49531,0.0637,0.03401],"object_pos_start":[0.49489,0.06374,0.03397],"object_to_goal_dist_end":0.1439,"object_to_goal_dist_start":0.14396,"object_z_max":0.03401,"peak_contact_force":0.54721,"phase_name":"approach_final","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":260.0,"raw_peak_contact_force":0.55289,"subtask_id":"approach","tcp_end":[0.48839,0.10384,0.04151],"tcp_start":[0.47882,0.10926,0.1103],"tcp_to_object_dist_end":0.04142,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":42.0,"n_steps_budget":600.0,"object_pos_end":[0.49493,0.06364,0.03401],"object_pos_start":[0.49531,0.0637,0.03401],"object_to_goal_dist_end":0.14386,"object_to_goal_dist_start":0.1439,"object_z_max":0.03401,"peak_contact_force":26.64972,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":43.0,"raw_peak_contact_force":26.64972,"subtask_id":"contact","tcp_end":[0.48686,0.10043,0.03742],"tcp_start":[0.48839,0.10384,0.04151],"tcp_to_object_dist_end":0.03782,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.49521,0.06362,0.03401],"object_pos_start":[0.49493,0.06364,0.03401],"object_to_goal_dist_end":0.14382,"object_to_goal_dist_start":0.14386,"object_z_max":0.03401,"peak_contact_force":74.8306,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":12.0,"raw_peak_contact_force":76.81538,"subtask_id":"push","tcp_end":[0.48684,0.10019,0.03725],"tcp_start":[0.48684,0.10022,0.03726],"tcp_to_object_dist_end":0.03765,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```