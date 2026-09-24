## Search State

- **Seed**: 0
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | -0.2073 | 0.01 | ❌ rejected |
| 4 | approach → approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | -0.1645 | 0.08 | ❌ rejected |
| 3 | approach → approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.4813 | 0.84 | ✅ accepted |
| 2 | approach → approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.0344 | 0.00 | ❌ rejected |
| 1 | approach → approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.1077 | 0.17 | ✅ accepted |

**Proposal policy**: task_score is 0.01 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.207) — your mutation base

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

- **Composite score**: -0.207
- **task_score** (E): 0.005
- **fitness_score**: 0.203  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 1.00 | 1.00 | 0.1819 |
| approach_final | 1.00 | 1.00 | 0.0933 |
| contact_peg | 1.00 | 1.00 | 0.0109 |
| push_through | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.125, 0.135) | (0.498, 0.080, 0.040)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.534 | 2.179 |
| approach_final | approach | 1.00 / step_budget | (0.495, 0.125, 0.135)→(0.495, 0.120, 0.042) | (0.500, 0.080, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.555 | 39.320 |
| contact_peg | contact | 1.00 / step_budget | (0.495, 0.120, 0.042)→(0.496, 0.112, 0.036) | (0.500, 0.080, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.160 | 1.00 / 2.333 | 162.145 | 197.464 |
| push_through | push | 0.00 / guard_failure | (0.496, 0.112, 0.036)→(0.496, 0.112, 0.036) | (0.500, 0.080, 0.034)→(0.500, 0.080, 0.034) | 0.160→0.160 | 1.00 / 2.000 | 284.096 | 472.309 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.014
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.014
- phase_score: 0.347
- phase_breakdown.push_score: 0.011
- phase_breakdown.contact_score: 0.795
- phase_breakdown.approach_score: 0.904

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.214
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.014
- **Median Q (composite search score)**: -0.211
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.303


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.12903,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_final.speed":0.06738,"approach_high.clearance_height":0.07532,"approach_high.speed":0.09111,"contact_peg.speed":0.00998,"push_through.push_force_limit":41.05555,"push_through.push_speed":0.08508,"push_through.push_tolerance":0.01965},"optimized_scores":{"best_composite_score":-0.21458,"best_fitness_score":0.19542,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54559,0.09448,0.05997],"force_p95":546.5138,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":548.92387,"mean_force":524.82317,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50103,0.09297,0.03609]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52503,0.09313,0.05998],"force_p95":419.17713,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":420.54216,"mean_force":406.8919,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50103,0.09297,0.03609]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":226.0,"contact_point_centroid":[0.54463,0.0947,0.05995],"force_p95":213.04027,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":215.54319,"mean_force":186.78946,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50001,0.09333,0.03614]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":17.0,"contact_point_centroid":[0.52502,0.09314,0.05999],"force_p95":123.75615,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":125.1038,"mean_force":103.92083,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.501,0.09296,0.03607]},{"body_a":"peg","body_b":"channel_base_body","contact_count":615.0,"contact_point_centroid":[0.50359,0.06158,0.00935],"force_p95":0.58219,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55971,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.50269,0.15234,0.20742]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49969,0.199,0.29853]},{"body_a":"peg","body_b":"channel_base_body","contact_count":258.0,"contact_point_centroid":[0.50381,0.06167,0.00938],"force_p95":0.55602,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56109,"mean_force":0.54664,"phase_index":1.0,"phase_name":"approach_final","phase_type":"approach","tcp_position_centroid":[0.50273,0.10438,0.08277]},{"body_a":"peg","body_b":"channel_base_body","contact_count":278.0,"contact_point_centroid":[0.50373,0.06147,0.00938],"force_p95":0.55532,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55587,"mean_force":0.54657,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49981,0.09441,0.03679]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.50843,0.07783,0.00938],"force_p95":0.55369,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55403,"mean_force":0.55061,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50103,0.09297,0.03609]}],"total_contact_groups":9},"final_pose_error":0.1731,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50379,0.06159,0.03379],"final_tcp_position":[0.50093,0.09305,0.03618],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":548.92387,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":638.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.06161,0.03379],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.1418,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.54132,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":634.0,"raw_peak_contact_force":2.17216,"tcp_end":[0.50692,0.10735,0.12236],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09973,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":258.0,"n_steps_budget":840.0,"object_pos_end":[0.50379,0.06159,0.03379],"object_pos_start":[0.50377,0.06161,0.03379],"object_to_goal_dist_end":0.14178,"object_to_goal_dist_start":0.1418,"object_z_max":0.03379,"peak_contact_force":0.54663,"phase_name":"approach_final","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":258.0,"raw_peak_contact_force":0.56109,"subtask_id":"approach","tcp_end":[0.50033,0.10175,0.04291],"tcp_start":[0.50692,0.10735,0.12236],"tcp_to_object_dist_end":0.04133,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":278.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.06161,0.03379],"object_pos_start":[0.50379,0.06159,0.03379],"object_to_goal_dist_end":0.1418,"object_to_goal_dist_start":0.14178,"object_z_max":0.03379,"peak_contact_force":125.1038,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":521.0,"raw_peak_contact_force":215.54319,"subtask_id":"contact","tcp_end":[0.50104,0.09295,0.03607],"tcp_start":[0.50033,0.10175,0.04291],"tcp_to_object_dist_end":0.03154,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.50378,0.06161,0.03379],"object_pos_start":[0.50375,0.06161,0.03379],"object_to_goal_dist_end":0.14179,"object_to_goal_dist_start":0.1418,"object_z_max":0.03379,"peak_contact_force":500.72247,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":548.92387,"subtask_id":"push","tcp_end":[0.50093,0.09305,0.03618],"tcp_start":[0.50102,0.09299,0.03611],"tcp_to_object_dist_end":0.03166,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.96774,"average_solve_count":155.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_final.speed":0.04478,"approach_high.clearance_height":0.12844,"approach_high.speed":0.04195,"contact_peg.speed":0.03003,"push_through.push_force_limit":43.82895,"push_through.push_speed":0.04459,"push_through.push_tolerance":0.04133},"optimized_scores":{"best_composite_score":-0.1964,"best_fitness_score":0.2136,"best_task_score":0.01416},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54806,0.11999,0.05983],"force_p95":354.74805,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":354.91559,"mean_force":353.24015,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49595,0.14454,0.03415]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.54806,0.12,0.05992],"force_p95":94.00049,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":95.30077,"mean_force":80.95756,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49587,0.14483,0.03431]},{"body_a":"peg","body_b":"channel_base_body","contact_count":64.0,"contact_point_centroid":[0.5012,0.11368,0.00941],"force_p95":3.47599,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.92522,"mean_force":1.03148,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49576,0.15042,0.03807]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.50054,0.13371,0.04483],"force_p95":9.47069,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.49108,"mean_force":6.59285,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49577,0.14558,0.03475]},{"body_a":"peg","body_b":"channel_base_body","contact_count":413.0,"contact_point_centroid":[0.501,0.11607,0.00936],"force_p95":0.62268,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.56334,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49824,0.17947,0.23672]},{"body_a":"peg","body_b":"channel_base_body","contact_count":455.0,"contact_point_centroid":[0.50087,0.11594,0.00943],"force_p95":0.59594,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6189,"mean_force":0.54246,"phase_index":1.0,"phase_name":"approach_final","phase_type":"approach","tcp_position_centroid":[0.49631,0.1572,0.10977]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.50141,0.09628,0.00992],"force_p95":0.4136,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41479,"mean_force":0.40286,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49595,0.14454,0.03415]}],"total_contact_groups":7},"final_pose_error":0.22469,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5013,0.11377,0.03521],"final_tcp_position":[0.496,0.14458,0.0342],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":354.91559,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":429.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,0.11606,0.03387],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19616,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.51571,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":413.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.49806,0.15974,0.17707],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14975,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":455.0,"n_steps_budget":1000.0,"object_pos_end":[0.501,0.11601,0.03383],"object_pos_start":[0.50092,0.11606,0.03387],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19616,"object_z_max":0.03398,"peak_contact_force":0.57596,"phase_name":"approach_final","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":455.0,"raw_peak_contact_force":0.6189,"subtask_id":"approach","tcp_end":[0.49676,0.15529,0.04267],"tcp_start":[0.49806,0.15974,0.17707],"tcp_to_object_dist_end":0.04048,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":64.0,"n_steps_budget":600.0,"object_pos_end":[0.50123,0.11412,0.03495],"object_pos_start":[0.501,0.11601,0.03383],"object_to_goal_dist_end":0.19419,"object_to_goal_dist_start":0.19611,"object_z_max":0.03479,"peak_contact_force":95.30077,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":73.0,"raw_peak_contact_force":95.30077,"subtask_id":"contact","tcp_end":[0.49594,0.14455,0.03415],"tcp_start":[0.49676,0.15529,0.04267],"tcp_to_object_dist_end":0.0309,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.50127,0.11394,0.03509],"object_pos_start":[0.50123,0.11412,0.03495],"object_to_goal_dist_end":0.194,"object_to_goal_dist_start":0.19419,"object_z_max":0.03509,"peak_contact_force":351.5647,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":354.91559,"subtask_id":"push","tcp_end":[0.496,0.14458,0.0342],"tcp_start":[0.49597,0.14453,0.03415],"tcp_to_object_dist_end":0.0311,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34483,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_final.speed":0.09702,"approach_high.clearance_height":0.05778,"approach_high.speed":0.06208,"contact_peg.speed":0.03826,"push_through.push_force_limit":48.367,"push_through.push_speed":0.05749,"push_through.push_tolerance":0.0203},"optimized_scores":{"best_composite_score":-0.2108,"best_fitness_score":0.1992,"best_task_score":0.00109},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.53576,0.09966,0.05998],"force_p95":508.6864,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":513.08812,"mean_force":469.07093,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49059,0.09752,0.03734]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":187.0,"contact_point_centroid":[0.53449,0.09985,0.05993],"force_p95":276.77649,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":281.54883,"mean_force":244.55734,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48928,0.09796,0.0373]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47496,0.10559,0.05973],"force_p95":105.29279,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":116.7799,"mean_force":54.06842,"phase_index":1.0,"phase_name":"approach_final","phase_type":"approach","tcp_position_centroid":[0.48567,0.10489,0.05455]},{"body_a":"peg","body_b":"channel_base_body","contact_count":675.0,"contact_point_centroid":[0.4953,0.06395,0.00937],"force_p95":0.56637,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55817,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.48832,0.1532,0.19885]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49929,0.19866,0.29742]},{"body_a":"peg","body_b":"channel_base_body","contact_count":218.0,"contact_point_centroid":[0.49503,0.06377,0.0094],"force_p95":0.55112,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55289,"mean_force":0.54519,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48907,0.09855,0.0376]},{"body_a":"peg","body_b":"channel_base_body","contact_count":230.0,"contact_point_centroid":[0.49504,0.06384,0.0094],"force_p95":0.55037,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55239,"mean_force":0.54537,"phase_index":1.0,"phase_name":"approach_final","phase_type":"approach","tcp_position_centroid":[0.48245,0.10635,0.07332]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.49371,0.04608,0.00941],"force_p95":0.54106,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54106,"mean_force":0.54101,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49059,0.09752,0.03734]}],"total_contact_groups":8},"final_pose_error":0.17798,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49519,0.0636,0.03402],"final_tcp_position":[0.49056,0.09771,0.03751],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":513.08812,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":702.0,"n_steps_budget":1000.0,"object_pos_end":[0.49494,0.06369,0.03397],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14391,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54607,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":703.0,"raw_peak_contact_force":2.44546,"tcp_end":[0.47878,0.10921,0.1059],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08664,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":230.0,"n_steps_budget":600.0,"object_pos_end":[0.49496,0.06363,0.034],"object_pos_start":[0.49494,0.06369,0.03397],"object_to_goal_dist_end":0.14385,"object_to_goal_dist_start":0.14391,"object_z_max":0.034,"peak_contact_force":0.54374,"phase_name":"approach_final","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":234.0,"raw_peak_contact_force":116.7799,"subtask_id":"approach","tcp_end":[0.48846,0.10385,0.04147],"tcp_start":[0.47878,0.10921,0.1059],"tcp_to_object_dist_end":0.04142,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":218.0,"n_steps_budget":600.0,"object_pos_end":[0.49504,0.06359,0.03402],"object_pos_start":[0.49496,0.06363,0.034],"object_to_goal_dist_end":0.1438,"object_to_goal_dist_start":0.14385,"object_z_max":0.03402,"peak_contact_force":266.03104,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":405.0,"raw_peak_contact_force":281.54883,"subtask_id":"contact","tcp_end":[0.49059,0.09747,0.0373],"tcp_start":[0.48846,0.10385,0.04147],"tcp_to_object_dist_end":0.03433,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.49511,0.06359,0.03402],"object_pos_start":[0.49504,0.06359,0.03402],"object_to_goal_dist_end":0.14379,"object_to_goal_dist_start":0.1438,"object_z_max":0.03402,"peak_contact_force":0.0,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":513.08812,"subtask_id":"push","tcp_end":[0.49056,0.09771,0.03751],"tcp_start":[0.49058,0.09756,0.03738],"tcp_to_object_dist_end":0.0346,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```