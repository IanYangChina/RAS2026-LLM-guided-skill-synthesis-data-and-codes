## Search State

- **Seed**: 1
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 3 | 0.6759 | 0.46 | ✅ accepted |

**Proposal policy**: task_score is 0.46 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.676) — your mutation base

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

- **Composite score**: 0.676
- **task_score** (E): 0.457
- **fitness_score**: 0.634  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.222
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.180

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2569 |
| contact_1 | 1.00 | 1.00 | 0.0091 |
| push_1 | 1.00 | 1.00 | 0.1939 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.483, 0.125, 0.056) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.667 | 299.925 | 317.270 |
| contact_1 | contact | 1.00 / force_exceeded | (0.483, 0.125, 0.056)→(0.483, 0.119, 0.050) | (0.497, 0.080, 0.034)→(0.497, 0.077, 0.034) | 0.160→0.157 | 1.00 / 2.000 | 34.152 | 34.883 |
| push_1 | push | 1.00 / step_budget | (0.483, 0.119, 0.050)→(0.495, -0.074, 0.036) | (0.497, 0.077, 0.034)→(0.501, -0.040, 0.034) | 0.157→0.046 | 1.00 / 2.000 | 42.173 | 191.509 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.486
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.248
- phase_score: 0.764
- phase_breakdown.approach_score: 0.662
- phase_breakdown.push_score: 0.883
- phase_breakdown.contact_score: 0.510

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.840
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.660
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.225


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24026,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":15.49293,"push_1.push_depth":-0.00295,"push_1.push_speed":0.05642},"optimized_scores":{"best_composite_score":0.65995,"best_fitness_score":0.83995,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":476.0,"contact_point_centroid":[0.50124,0.01215,0.04677],"force_p95":121.90256,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":125.37196,"mean_force":25.0889,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49496,0.02309,0.03108]},{"body_a":"peg","body_b":"channel_base_body","contact_count":96.0,"contact_point_centroid":[0.50722,-0.10151,0.0614],"force_p95":116.29985,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.10512,"mean_force":94.78447,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49581,-0.05899,0.0339]},{"body_a":"peg","body_b":"channel_base_body","contact_count":234.0,"contact_point_centroid":[0.50958,-0.02503,0.00989],"force_p95":18.29279,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.38379,"mean_force":7.91482,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49509,0.01408,0.03142]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":431.0,"contact_point_centroid":[0.52523,-0.00693,0.03776],"force_p95":24.63797,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.1582,"mean_force":6.24335,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49482,0.02022,0.03098]},{"body_a":"peg","body_b":"channel_base_body","contact_count":370.0,"contact_point_centroid":[0.5027,0.10303,0.00973],"force_p95":3.98906,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.53579,"mean_force":2.03534,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49585,0.14519,0.03669]},{"body_a":"attachment","body_b":"peg","contact_count":218.0,"contact_point_centroid":[0.49955,0.12938,0.04658],"force_p95":3.84443,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.21665,"mean_force":2.72381,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49608,0.14131,0.03345]},{"body_a":"peg","body_b":"channel_base_body","contact_count":757.0,"contact_point_centroid":[0.50092,0.11598,0.0094],"force_p95":0.61519,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.5534,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49783,0.17796,0.17136]}],"total_contact_groups":7},"final_pose_error":0.02219,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5047,-0.086,0.03685],"final_tcp_position":[0.49543,-0.06223,0.03349],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":125.37196,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":773.0,"n_steps_budget":1000.0,"object_pos_end":[0.50094,0.11601,0.03384],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.53532,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":757.0,"raw_peak_contact_force":1.92055,"subtask_id":"approach","tcp_end":[0.49732,0.15727,0.04901],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04411,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":375.0,"n_steps_budget":600.0,"object_pos_end":[0.50256,0.10768,0.03535],"object_pos_start":[0.50094,0.11601,0.03384],"object_to_goal_dist_end":0.18776,"object_to_goal_dist_start":0.19611,"object_z_max":0.03542,"peak_contact_force":2.34402,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":588.0,"raw_peak_contact_force":4.53579,"subtask_id":"contact","tcp_end":[0.49673,0.13728,0.03053],"tcp_start":[0.49732,0.15727,0.04901],"tcp_to_object_dist_end":0.03055,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":599.0,"n_steps_budget":1000.0,"object_pos_end":[0.5047,-0.086,0.03685],"object_pos_start":[0.50256,0.10768,0.03535],"object_to_goal_dist_end":0.00825,"object_to_goal_dist_start":0.18776,"object_z_max":0.03702,"peak_contact_force":125.37196,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1237.0,"raw_peak_contact_force":125.37196,"subtask_id":"push","tcp_end":[0.49543,-0.06223,0.03349],"tcp_start":[0.49673,0.13728,0.03053],"tcp_to_object_dist_end":0.02574,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38168,"average_solve_count":131.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":13.53612,"push_1.push_depth":-0.01654,"push_1.push_speed":0.05888},"optimized_scores":{"best_composite_score":0.71065,"best_fitness_score":0.55732,"best_task_score":0.24755},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":80.0,"contact_point_centroid":[0.47497,0.10117,0.05979],"force_p95":444.27811,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":462.40253,"mean_force":410.68659,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48066,0.11161,0.05891]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":204.0,"contact_point_centroid":[0.475,0.08018,0.05835],"force_p95":169.61086,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":177.301,"mean_force":113.35441,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48541,0.08424,0.0571]},{"body_a":"attachment","body_b":"peg","contact_count":258.0,"contact_point_centroid":[0.49603,0.03154,0.04993],"force_p95":70.38757,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":73.13398,"mean_force":40.75047,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48806,0.03485,0.0505]},{"body_a":"peg","body_b":"channel_base_body","contact_count":605.0,"contact_point_centroid":[0.50091,0.02811,0.00938],"force_p95":56.22605,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":60.58894,"mean_force":14.06337,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4881,0.03115,0.05009]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47499,0.10174,0.05995],"force_p95":48.19016,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":48.19016,"mean_force":48.19016,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48168,0.11162,0.05913]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":147.0,"contact_point_centroid":[0.52507,0.02803,0.05432],"force_p95":35.73669,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.72711,"mean_force":23.86769,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48691,0.05732,0.05325]},{"body_a":"peg","body_b":"channel_base_body","contact_count":837.0,"contact_point_centroid":[0.49523,0.06389,0.00938],"force_p95":0.56101,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55569,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48778,0.15029,0.16359]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4994,0.19869,0.29695]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49602,0.04591,0.0094],"force_p95":0.5415,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5415,"mean_force":0.5415,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48168,0.11162,0.05913]}],"total_contact_groups":9},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4994,-0.01382,0.04047],"final_tcp_position":[0.49502,-0.07743,0.03724],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":462.40253,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":864.0,"n_steps_budget":1000.0,"object_pos_end":[0.49511,0.06361,0.034],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14382,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":428.13355,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":945.0,"raw_peak_contact_force":462.40253,"subtask_id":"approach","tcp_end":[0.48168,0.11162,0.05913],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05583,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49518,0.06363,0.034],"object_pos_start":[0.49511,0.06361,0.034],"object_to_goal_dist_end":0.14384,"object_to_goal_dist_start":0.14382,"object_z_max":0.034,"peak_contact_force":48.19016,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":48.19016,"subtask_id":"contact","tcp_end":[0.48171,0.11162,0.05913],"tcp_start":[0.48168,0.11162,0.05913],"tcp_to_object_dist_end":0.05582,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":607.0,"n_steps_budget":1000.0,"object_pos_end":[0.4994,-0.01382,0.04047],"object_pos_start":[0.49518,0.06363,0.034],"object_to_goal_dist_end":0.06619,"object_to_goal_dist_start":0.14384,"object_z_max":0.04079,"peak_contact_force":0.47925,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1214.0,"raw_peak_contact_force":177.301,"subtask_id":"push","tcp_end":[0.49502,-0.07743,0.03724],"tcp_start":[0.48171,0.11162,0.05913],"tcp_to_object_dist_end":0.06385,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91262,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":19.99317,"push_1.push_depth":-0.01993,"push_1.push_speed":0.09849},"optimized_scores":{"best_composite_score":0.6571,"best_fitness_score":0.50376,"best_task_score":0.12377},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":85.0,"contact_point_centroid":[0.47497,0.09764,0.05978],"force_p95":473.10539,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":487.48578,"mean_force":446.49663,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46842,0.10758,0.06044]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":321.0,"contact_point_centroid":[0.475,0.06122,0.05996],"force_p95":231.73317,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":271.85432,"mean_force":182.03942,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47921,0.07091,0.05969]},{"body_a":"peg","body_b":"channel_base_body","contact_count":707.0,"contact_point_centroid":[0.49909,0.02436,0.00913],"force_p95":130.13405,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":137.01468,"mean_force":42.2748,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48424,0.03315,0.05543]},{"body_a":"attachment","body_b":"peg","contact_count":490.0,"contact_point_centroid":[0.4956,0.03588,0.05679],"force_p95":130.96686,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":136.59768,"mean_force":60.28663,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48564,0.03374,0.05667]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.475,0.09686,0.05996],"force_p95":51.92172,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":51.92172,"mean_force":51.92172,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46968,0.10754,0.06062]},{"body_a":"peg","body_b":"channel_base_body","contact_count":843.0,"contact_point_centroid":[0.49427,0.05902,0.00937],"force_p95":0.55513,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56351,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48067,0.14771,0.16347]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49906,0.19829,0.29586]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.47799,0.05101,0.00939],"force_p95":0.54853,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54853,"mean_force":0.54853,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46968,0.10754,0.06062]}],"total_contact_groups":8},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49932,-0.01926,0.02396],"final_tcp_position":[0.49438,-0.08088,0.03778],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":487.48578,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":872.0,"n_steps_budget":1000.0,"object_pos_end":[0.49397,0.05889,0.03391],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13915,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":471.1054,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":963.0,"raw_peak_contact_force":487.48578,"subtask_id":"approach","tcp_end":[0.46968,0.10754,0.06062],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06058,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49401,0.05884,0.03391],"object_pos_start":[0.49397,0.05889,0.03391],"object_to_goal_dist_end":0.1391,"object_to_goal_dist_start":0.13915,"object_z_max":0.03391,"peak_contact_force":51.92172,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":51.92172,"subtask_id":"contact","tcp_end":[0.46969,0.10753,0.06061],"tcp_start":[0.46968,0.10754,0.06062],"tcp_to_object_dist_end":0.06062,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":714.0,"n_steps_budget":1000.0,"object_pos_end":[0.49932,-0.01926,0.02396],"object_pos_start":[0.49401,0.05884,0.03391],"object_to_goal_dist_end":0.06283,"object_to_goal_dist_start":0.1391,"object_z_max":0.03952,"peak_contact_force":0.66814,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1518.0,"raw_peak_contact_force":271.85432,"subtask_id":"push","tcp_end":[0.49438,-0.08088,0.03778],"tcp_start":[0.46969,0.10753,0.06061],"tcp_to_object_dist_end":0.06335,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```