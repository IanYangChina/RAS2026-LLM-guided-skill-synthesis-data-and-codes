## Search State

- **Seed**: 1
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 3 | 0.6761 | 0.46 | ✅ accepted |
| 10 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.2247 | 0.00 | ❌ rejected |
| 9 | approach → approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | 6 | 0.2082 | 0.25 | ❌ rejected |
| 8 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | 4 | 0.2939 | 0.23 | ❌ rejected |
| 7 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 3 | 0.3672 | 0.44 | ❌ rejected |

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
- **task_score** (E): 0.463
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
| push_1 | 1.00 | 1.00 | 0.1928 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.483, 0.125, 0.056) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.667 | 299.925 | 317.270 |
| contact_1 | contact | 1.00 / force_exceeded | (0.483, 0.125, 0.056)→(0.483, 0.119, 0.050) | (0.497, 0.080, 0.034)→(0.497, 0.077, 0.034) | 0.160→0.157 | 1.00 / 2.000 | 34.152 | 34.883 |
| push_1 | push | 1.00 / step_budget | (0.483, 0.119, 0.050)→(0.495, -0.072, 0.036) | (0.497, 0.077, 0.034)→(0.501, -0.041, 0.033) | 0.157→0.045 | 1.00 / 2.000 | 41.302 | 182.152 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.500
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.250
- phase_score: 0.753
- phase_breakdown.approach_score: 0.662
- phase_breakdown.push_score: 0.865
- phase_breakdown.contact_score: 0.510

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.840
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.664
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.268


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.23567,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":11.23939,"push_1.push_depth":-0.00246,"push_1.push_speed":0.05403},"optimized_scores":{"best_composite_score":0.65951,"best_fitness_score":0.83951,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":502.0,"contact_point_centroid":[0.50118,0.01215,0.04681],"force_p95":118.83897,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":122.91555,"mean_force":21.86468,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49502,0.0231,0.03114]},{"body_a":"peg","body_b":"channel_base_body","contact_count":93.0,"contact_point_centroid":[0.50661,-0.10156,0.06039],"force_p95":115.37509,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":116.04904,"mean_force":94.33255,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.496,-0.05884,0.03406]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":350.0,"contact_point_centroid":[0.52526,0.00164,0.03418],"force_p95":24.10444,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.53837,"mean_force":4.89256,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49475,0.0286,0.03071]},{"body_a":"peg","body_b":"channel_base_body","contact_count":235.0,"contact_point_centroid":[0.51113,-0.02474,0.00985],"force_p95":17.20503,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.84108,"mean_force":7.6371,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49515,0.01487,0.03145]},{"body_a":"peg","body_b":"channel_base_body","contact_count":370.0,"contact_point_centroid":[0.5027,0.10303,0.00973],"force_p95":3.98906,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.53579,"mean_force":2.03534,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49585,0.14519,0.03669]},{"body_a":"attachment","body_b":"peg","contact_count":218.0,"contact_point_centroid":[0.49955,0.12938,0.04658],"force_p95":3.84443,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.21665,"mean_force":2.72381,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49608,0.14131,0.03345]},{"body_a":"peg","body_b":"channel_base_body","contact_count":757.0,"contact_point_centroid":[0.50092,0.11598,0.0094],"force_p95":0.61519,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.5534,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49783,0.17796,0.17136]}],"total_contact_groups":7},"final_pose_error":0.02184,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50578,-0.08559,0.0361],"final_tcp_position":[0.49577,-0.06196,0.03375],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":122.91555,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":773.0,"n_steps_budget":1000.0,"object_pos_end":[0.50094,0.11601,0.03384],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.53532,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":757.0,"raw_peak_contact_force":1.92055,"subtask_id":"approach","tcp_end":[0.49732,0.15727,0.04901],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04411,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":375.0,"n_steps_budget":600.0,"object_pos_end":[0.50256,0.10768,0.03535],"object_pos_start":[0.50094,0.11601,0.03384],"object_to_goal_dist_end":0.18776,"object_to_goal_dist_start":0.19611,"object_z_max":0.03542,"peak_contact_force":2.34402,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":588.0,"raw_peak_contact_force":4.53579,"subtask_id":"contact","tcp_end":[0.49673,0.13728,0.03053],"tcp_start":[0.49732,0.15727,0.04901],"tcp_to_object_dist_end":0.03055,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":594.0,"n_steps_budget":1000.0,"object_pos_end":[0.50578,-0.08559,0.0361],"object_pos_start":[0.50256,0.10768,0.03535],"object_to_goal_dist_end":0.00894,"object_to_goal_dist_start":0.18776,"object_z_max":0.03724,"peak_contact_force":122.91555,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1180.0,"raw_peak_contact_force":122.91555,"subtask_id":"push","tcp_end":[0.49577,-0.06196,0.03375],"tcp_start":[0.49673,0.13728,0.03053],"tcp_to_object_dist_end":0.02577,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.27528,"average_solve_count":178.0,"average_success_count":178.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":12.48808,"push_1.push_depth":-0.01443,"push_1.push_speed":0.02291},"optimized_scores":{"best_composite_score":0.7051,"best_fitness_score":0.55177,"best_task_score":0.24962},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":80.0,"contact_point_centroid":[0.47497,0.10117,0.05979],"force_p95":444.27811,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":462.40253,"mean_force":410.68659,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48066,0.11161,0.05891]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":182.0,"contact_point_centroid":[0.475,0.0848,0.05899],"force_p95":164.24872,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":170.5452,"mean_force":120.16359,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4851,0.08962,0.0578]},{"body_a":"attachment","body_b":"peg","contact_count":194.0,"contact_point_centroid":[0.49673,0.02487,0.04862],"force_p95":59.10818,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":61.46396,"mean_force":31.48927,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48843,0.02682,0.04926]},{"body_a":"peg","body_b":"channel_base_body","contact_count":581.0,"contact_point_centroid":[0.4996,0.0287,0.00941],"force_p95":48.52149,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":55.38884,"mean_force":9.71602,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48811,0.03142,0.05]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47499,0.10174,0.05995],"force_p95":48.19016,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":48.19016,"mean_force":48.19016,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48168,0.11162,0.05913]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":77.0,"contact_point_centroid":[0.52514,0.0256,0.05247],"force_p95":29.19486,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.82829,"mean_force":16.82316,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48691,0.05853,0.05327]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.47494,0.03931,0.02433],"force_p95":5.83743,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.95943,"mean_force":1.5824,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48825,0.00339,0.045]},{"body_a":"peg","body_b":"channel_base_body","contact_count":837.0,"contact_point_centroid":[0.49523,0.06389,0.00938],"force_p95":0.56101,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55569,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48778,0.15029,0.16359]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4994,0.19869,0.29695]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49602,0.04591,0.0094],"force_p95":0.5415,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5415,"mean_force":0.5415,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48168,0.11162,0.05913]}],"total_contact_groups":10},"final_pose_error":0.01973,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49981,-0.01609,0.03935],"final_tcp_position":[0.49499,-0.07555,0.03721],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":462.40253,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":864.0,"n_steps_budget":1000.0,"object_pos_end":[0.49511,0.06361,0.034],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14382,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":428.13355,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":945.0,"raw_peak_contact_force":462.40253,"subtask_id":"approach","tcp_end":[0.48168,0.11162,0.05913],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05583,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49518,0.06363,0.034],"object_pos_start":[0.49511,0.06361,0.034],"object_to_goal_dist_end":0.14384,"object_to_goal_dist_start":0.14382,"object_z_max":0.034,"peak_contact_force":48.19016,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":48.19016,"subtask_id":"contact","tcp_end":[0.48171,0.11162,0.05913],"tcp_start":[0.48168,0.11162,0.05913],"tcp_to_object_dist_end":0.05582,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":588.0,"n_steps_budget":1000.0,"object_pos_end":[0.49981,-0.01609,0.03935],"object_pos_start":[0.49518,0.06363,0.034],"object_to_goal_dist_end":0.06392,"object_to_goal_dist_start":0.14384,"object_z_max":0.04079,"peak_contact_force":0.53986,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1043.0,"raw_peak_contact_force":170.5452,"subtask_id":"push","tcp_end":[0.49499,-0.07555,0.03721],"tcp_start":[0.48171,0.11162,0.05913],"tcp_to_object_dist_end":0.0597,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91743,"average_solve_count":109.0,"average_success_count":109.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":6.03064,"push_1.push_depth":-0.01855,"push_1.push_speed":0.08679},"optimized_scores":{"best_composite_score":0.66367,"best_fitness_score":0.51034,"best_task_score":0.13814},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":85.0,"contact_point_centroid":[0.47497,0.09764,0.05978],"force_p95":473.10539,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":487.48578,"mean_force":446.49663,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46842,0.10758,0.06044]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":350.0,"contact_point_centroid":[0.475,0.06033,0.05996],"force_p95":225.02732,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":252.9938,"mean_force":180.6631,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47953,0.06981,0.05966]},{"body_a":"peg","body_b":"channel_base_body","contact_count":736.0,"contact_point_centroid":[0.49898,0.02497,0.00912],"force_p95":131.09778,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":137.28315,"mean_force":42.15068,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48423,0.03459,0.05564]},{"body_a":"attachment","body_b":"peg","contact_count":524.0,"contact_point_centroid":[0.49567,0.03645,0.05684],"force_p95":131.92649,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":136.85213,"mean_force":58.51464,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48561,0.03471,0.05676]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.475,0.09686,0.05996],"force_p95":51.92172,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":51.92172,"mean_force":51.92172,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46968,0.10754,0.06062]},{"body_a":"peg","body_b":"channel_base_body","contact_count":843.0,"contact_point_centroid":[0.49427,0.05902,0.00937],"force_p95":0.55513,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56351,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48067,0.14771,0.16347]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49906,0.19829,0.29586]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.47799,0.05101,0.00939],"force_p95":0.54853,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54853,"mean_force":0.54853,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46968,0.10754,0.06062]}],"total_contact_groups":8},"final_pose_error":0.01975,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49731,-0.01998,0.02368],"final_tcp_position":[0.49443,-0.07972,0.03784],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":487.48578,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":872.0,"n_steps_budget":1000.0,"object_pos_end":[0.49397,0.05889,0.03391],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13915,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":471.1054,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":963.0,"raw_peak_contact_force":487.48578,"subtask_id":"approach","tcp_end":[0.46968,0.10754,0.06062],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06058,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49401,0.05884,0.03391],"object_pos_start":[0.49397,0.05889,0.03391],"object_to_goal_dist_end":0.1391,"object_to_goal_dist_start":0.13915,"object_z_max":0.03391,"peak_contact_force":51.92172,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":51.92172,"subtask_id":"contact","tcp_end":[0.46969,0.10753,0.06061],"tcp_start":[0.46968,0.10754,0.06062],"tcp_to_object_dist_end":0.06062,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":744.0,"n_steps_budget":1000.0,"object_pos_end":[0.49731,-0.01998,0.02368],"object_pos_start":[0.49401,0.05884,0.03391],"object_to_goal_dist_end":0.06226,"object_to_goal_dist_start":0.1391,"object_z_max":0.03952,"peak_contact_force":0.45185,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1610.0,"raw_peak_contact_force":252.9938,"subtask_id":"push","tcp_end":[0.49443,-0.07972,0.03784],"tcp_start":[0.46969,0.10753,0.06061],"tcp_to_object_dist_end":0.06147,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```