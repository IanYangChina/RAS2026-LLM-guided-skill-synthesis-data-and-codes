## Search State

- **Seed**: 1
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 6 | 0.4123 | 0.08 | ❌ rejected |
| 12 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 3 | 0.6820 | 0.46 | ❌ rejected |
| 11 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 3 | 0.6761 | 0.46 | ✅ accepted |
| 10 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.2247 | 0.00 | ❌ rejected |
| 9 | approach → approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | 6 | 0.2082 | 0.25 | ❌ rejected |

**Proposal policy**: task_score is 0.08 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`
- Frozen object start: [0.5009457299760205, 0.11603709570607482, 0.04]
- Frozen task target: [0.5009457299760205, -0.04396290429392519, 0.04]
- Goal object position: (0.5009457299760205, -0.04396290429392519, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5009457299760205, 0.11603709570607482, 0.04)
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
  frozen_object_start: [0.5009, 0.116, 0.04]
  frozen_task_target: [0.5009, -0.044, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5009457299760205, 0.11603709570607482, 0.04]}
  frozen_targets: {'channel_exit': [0.5009457299760205, -0.04396290429392519, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a

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

## Current Skill (Q=0.412) — your mutation base

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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
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
  subtask_id: contact
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - -0.08
    - 0.04
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_depth:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
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
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=world, offset=[0.5, -0.08, 0.04], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset.y (add)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.412
- **task_score** (E): 0.076
- **fitness_score**: 0.187  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.556
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2561 |
| contact_1 | 1.00 | 1.00 | 0.0100 |
| push_1 | 1.00 | 1.00 | 0.0109 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.483, 0.132, 0.055) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.667 | 295.214 | 302.346 |
| contact_1 | contact | 1.00 / force_exceeded | (0.483, 0.132, 0.055)→(0.483, 0.124, 0.050) | (0.497, 0.080, 0.034)→(0.497, 0.077, 0.034) | 0.160→0.157 | 1.00 / 2.000 | 38.370 | 38.992 |
| push_1 | push | 1.00 / force_exceeded | (0.483, 0.124, 0.050)→(0.482, 0.113, 0.049) | (0.497, 0.077, 0.034)→(0.499, 0.067, 0.035) | 0.157→0.147 | 1.00 / 2.000 | 1345.761 | 45.202 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.224
- phase_breakdown.approach_score: 0.615
- phase_breakdown.push_score: 0.018
- phase_breakdown.contact_score: 0.451

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.296
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.229
- **Median Q (composite search score)**: 0.467
- **K-run variance**: 0.0064
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.436


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a904e23429ae963dd2788b3e8d0575d9ce341e1daddfe013fbb1224c3e0c850e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `6bee39a4c127c6d39ee1365e3969a50bb09484f7e2580b1a3dc4d8c4ae20213b`; realized-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,0.11604,0.04]},{"name":"goal","value":[0.50095,-0.04396,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.11604,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50095,-0.04396,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67416,"average_solve_count":89.0,"average_success_count":89.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.09072,"approach_1.arc_height":0.03845,"contact_1.contact_force":10.70645,"push_1.push_depth":0.00121,"push_1.push_force_threshold":33.60102,"push_1.push_speed":0.09938},"optimized_scores":{"best_composite_score":0.29892,"best_fitness_score":0.29558,"best_task_score":0.22907},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":149.0,"contact_point_centroid":[0.50057,0.11027,0.04443],"force_p95":14.21443,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.72973,"mean_force":5.52348,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49399,0.12149,0.02722]},{"body_a":"peg","body_b":"channel_base_body","contact_count":138.0,"contact_point_centroid":[0.50594,0.07797,0.00991],"force_p95":10.25043,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.04873,"mean_force":4.88376,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49404,0.12228,0.02724]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":140.0,"contact_point_centroid":[0.52517,0.08958,0.03734],"force_p95":9.57684,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.01215,"mean_force":2.7496,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49347,0.11713,0.02674]},{"body_a":"peg","body_b":"channel_base_body","contact_count":414.0,"contact_point_centroid":[0.50149,0.10688,0.00964],"force_p95":3.84421,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44404,"mean_force":1.5982,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49572,0.14822,0.03515]},{"body_a":"attachment","body_b":"peg","contact_count":178.0,"contact_point_centroid":[0.49965,0.1297,0.04486],"force_p95":3.72406,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.12608,"mean_force":2.64141,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49621,0.14163,0.03186]},{"body_a":"peg","body_b":"channel_base_body","contact_count":810.0,"contact_point_centroid":[0.50088,0.11606,0.0094],"force_p95":0.61298,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55247,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49782,0.20345,0.16685]}],"total_contact_groups":6},"final_pose_error":0.1845,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50687,0.07766,0.03621],"final_tcp_position":[0.49336,0.10512,0.02695],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":3919.40707,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":826.0,"n_steps_budget":1000.0,"object_pos_end":[0.50094,0.11602,0.03389],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19612,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.50473,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":810.0,"raw_peak_contact_force":1.92055,"subtask_id":"approach","tcp_end":[0.49721,0.16326,0.04552],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04879,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":423.0,"n_steps_budget":600.0,"object_pos_end":[0.50285,0.10793,0.03545],"object_pos_start":[0.50094,0.11602,0.03389],"object_to_goal_dist_end":0.18801,"object_to_goal_dist_start":0.19612,"object_z_max":0.03544,"peak_contact_force":2.57625,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":592.0,"raw_peak_contact_force":4.44404,"subtask_id":"contact","tcp_end":[0.49679,0.13747,0.03008],"tcp_start":[0.49721,0.16326,0.04552],"tcp_to_object_dist_end":0.03063,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":206.0,"n_steps_budget":1000.0,"object_pos_end":[0.50687,0.07766,0.03621],"object_pos_start":[0.50285,0.10793,0.03545],"object_to_goal_dist_end":0.15786,"object_to_goal_dist_start":0.18801,"object_z_max":0.0364,"peak_contact_force":3919.40707,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":427.0,"raw_peak_contact_force":17.72973,"subtask_id":"push","tcp_end":[0.49336,0.10512,0.02695],"tcp_start":[0.49679,0.13747,0.03008],"tcp_to_object_dist_end":0.03198,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8416ac3bebb4dbec2abbf751596843a33db171fd8d70765023f3b940d846bd0c`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81633,"average_solve_count":49.0,"average_success_count":49.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.12206,"approach_1.arc_height":0.02006,"contact_1.contact_force":6.77937,"push_1.push_depth":0.01461,"push_1.push_force_threshold":34.51093,"push_1.push_speed":0.04805},"optimized_scores":{"best_composite_score":0.47112,"best_fitness_score":0.13445,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":81.0,"contact_point_centroid":[0.47497,0.10833,0.05979],"force_p95":446.63624,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":452.33029,"mean_force":414.22614,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48064,0.11879,0.05896]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47499,0.10887,0.05996],"force_p95":64.31467,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":64.31467,"mean_force":64.31467,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48172,0.11874,0.05922]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47499,0.10886,0.05996],"force_p95":55.40053,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":55.40053,"mean_force":55.40053,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48171,0.11873,0.05922]},{"body_a":"peg","body_b":"channel_base_body","contact_count":820.0,"contact_point_centroid":[0.49531,0.0638,0.00938],"force_p95":0.56258,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55591,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48753,0.16336,0.15967]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49946,0.19937,0.29689]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51278,0.06719,0.0094],"force_p95":0.54658,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54658,"mean_force":0.54658,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48171,0.11873,0.05922]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51131,0.07166,0.0094],"force_p95":0.54526,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54526,"mean_force":0.54526,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48172,0.11874,0.05922]}],"total_contact_groups":7},"final_pose_error":0.18603,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49529,0.06404,0.03399],"final_tcp_position":[0.48172,0.11874,0.05921],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":452.33029,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":847.0,"n_steps_budget":1000.0,"object_pos_end":[0.49535,0.06392,0.03399],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14412,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":444.57956,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":929.0,"raw_peak_contact_force":452.33029,"subtask_id":"approach","tcp_end":[0.48171,0.11873,0.05922],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06186,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49533,0.06399,0.03399],"object_pos_start":[0.49535,0.06392,0.03399],"object_to_goal_dist_end":0.14419,"object_to_goal_dist_start":0.14412,"object_z_max":0.03399,"peak_contact_force":55.40053,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":55.40053,"subtask_id":"contact","tcp_end":[0.48172,0.11874,0.05922],"tcp_start":[0.48171,0.11873,0.05922],"tcp_to_object_dist_end":0.0618,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49529,0.06404,0.03399],"object_pos_start":[0.49533,0.06399,0.03399],"object_to_goal_dist_end":0.14425,"object_to_goal_dist_start":0.14419,"object_z_max":0.03399,"peak_contact_force":64.31467,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":64.31467,"subtask_id":"push","tcp_end":[0.48172,0.11874,0.05921],"tcp_start":[0.48172,0.11874,0.05922],"tcp_to_object_dist_end":0.06174,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0188121de1b8142d5ff7a7406b62c43adf6da5520b986a997e46ef53b7d11bf9`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.84746,"average_solve_count":59.0,"average_success_count":59.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.1013,"approach_1.arc_height":0.02002,"contact_1.contact_force":4.16365,"push_1.push_depth":0.00861,"push_1.push_force_threshold":37.05698,"push_1.push_speed":0.01402},"optimized_scores":{"best_composite_score":0.46681,"best_fitness_score":0.13014,"best_task_score":0.00032},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":111.0,"contact_point_centroid":[0.47498,0.10511,0.05981],"force_p95":450.03234,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":452.78842,"mean_force":417.66551,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46874,0.11517,0.06047]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.475,0.1037,0.05996],"force_p95":57.13289,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":57.13289,"mean_force":57.13289,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47085,0.1149,0.0605]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.475,0.1037,0.05996],"force_p95":53.56216,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":53.56216,"mean_force":53.56216,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47086,0.11491,0.0605]},{"body_a":"peg","body_b":"channel_base_body","contact_count":863.0,"contact_point_centroid":[0.49424,0.059,0.00937],"force_p95":0.55479,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56311,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47986,0.15951,0.15663]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49906,0.19916,0.2956]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.48279,0.045,0.00939],"force_p95":0.54243,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54243,"mean_force":0.54243,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47085,0.1149,0.0605]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.48792,0.04207,0.00939],"force_p95":0.54176,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54176,"mean_force":0.54176,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47086,0.11491,0.0605]}],"total_contact_groups":7},"final_pose_error":0.18968,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49412,0.05879,0.03391],"final_tcp_position":[0.47087,0.11491,0.06049],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":452.78842,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":892.0,"n_steps_budget":1000.0,"object_pos_end":[0.49402,0.05882,0.03391],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13909,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":440.55644,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1009.0,"raw_peak_contact_force":452.78842,"subtask_id":"approach","tcp_end":[0.47085,0.1149,0.0605],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06625,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49407,0.0588,0.03391],"object_pos_start":[0.49402,0.05882,0.03391],"object_to_goal_dist_end":0.13906,"object_to_goal_dist_start":0.13909,"object_z_max":0.03391,"peak_contact_force":57.13289,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":57.13289,"subtask_id":"contact","tcp_end":[0.47086,0.11491,0.0605],"tcp_start":[0.47085,0.1149,0.0605],"tcp_to_object_dist_end":0.06628,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49412,0.05879,0.03391],"object_pos_start":[0.49407,0.0588,0.03391],"object_to_goal_dist_end":0.13905,"object_to_goal_dist_start":0.13906,"object_z_max":0.03391,"peak_contact_force":53.56216,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":53.56216,"subtask_id":"push","tcp_end":[0.47087,0.11491,0.06049],"tcp_start":[0.47086,0.11491,0.0605],"tcp_to_object_dist_end":0.06631,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```