## Search State

- **Seed**: 0
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 5 | 0.5483 | 0.00 | ✅ accepted |

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

## Current Skill (Q=0.548) — your mutation base

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
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
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
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - -0.08
    - 0.04
    orientation:
      mode: keep_current
  parameters:
    push_force:
      type: scalar
      range:
      - 1.0
      - 40.0
      default: 30.0
      binds_to:
      - path: termination.force_threshold
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
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.0]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=world, offset=[0.5, -0.08, 0.04]
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_force: status=consumed; consumers=termination.force_threshold (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.548
- **task_score** (E): 0.000
- **fitness_score**: 0.162  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.667
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2580 |
| contact_1 | 1.00 | 1.00 | 0.0001 |
| push_1 | 1.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.124, 0.055) | (0.498, 0.080, 0.040)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 2.333 | 370.903 | 398.655 |
| contact_1 | contact | 1.00 / force_exceeded | (0.497, 0.124, 0.055)→(0.497, 0.124, 0.055) | (0.500, 0.080, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 2.333 | 175.402 | 175.402 |
| push_1 | push | 1.00 / force_exceeded | (0.497, 0.124, 0.055)→(0.497, 0.124, 0.055) | (0.500, 0.080, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 2.333 | 241.008 | 241.008 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.001
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.001
- phase_score: 0.280
- phase_breakdown.push_score: 0.024
- phase_breakdown.contact_score: 0.588
- phase_breakdown.approach_score: 0.742

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.168
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.001
- **Median Q (composite search score)**: 0.547
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.356


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.01639,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04681,"contact_1.contact_force":10.40256,"contact_1.speed":0.03426,"push_1.push_force":17.65949,"push_1.push_speed":0.03476},"optimized_scores":{"best_composite_score":0.54318,"best_fitness_score":0.15651,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":49.0,"contact_point_centroid":[0.50939,0.16898,-0.00036],"force_p95":289.69233,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":304.06415,"mean_force":247.05997,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50717,0.10758,0.05426]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50969,0.16894,-0.00011],"force_p95":92.2382,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":92.2382,"mean_force":92.2382,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50699,0.10845,0.05575]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50972,0.16895,-0.0001],"force_p95":78.30952,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.30952,"mean_force":78.30952,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50701,0.10848,0.05577]},{"body_a":"peg","body_b":"channel_base_body","contact_count":977.0,"contact_point_centroid":[0.50367,0.06156,0.00936],"force_p95":0.58149,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55485,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50058,0.15688,0.17289]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50431,0.20792,0.29852]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50271,0.07946,0.00938],"force_p95":0.55412,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55412,"mean_force":0.55412,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50701,0.10848,0.05577]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.48835,0.07083,0.00938],"force_p95":0.54355,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54355,"mean_force":0.54355,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50699,0.10845,0.05575]}],"total_contact_groups":7},"final_pose_error":0.1893,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50378,0.06161,0.03379],"final_tcp_position":[0.50705,0.10851,0.05577],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":304.06415,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.0616,0.03379],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14178,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":255.96105,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1045.0,"raw_peak_contact_force":304.06415,"subtask_id":"approach","tcp_end":[0.50699,0.10845,0.05575],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05185,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":660.0,"object_pos_end":[0.50375,0.06161,0.03379],"object_pos_start":[0.50373,0.0616,0.03379],"object_to_goal_dist_end":0.1418,"object_to_goal_dist_start":0.14178,"object_z_max":0.03379,"peak_contact_force":92.2382,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":92.2382,"subtask_id":"contact","tcp_end":[0.50701,0.10848,0.05577],"tcp_start":[0.50699,0.10845,0.05575],"tcp_to_object_dist_end":0.05187,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50378,0.06161,0.03379],"object_pos_start":[0.50375,0.06161,0.03379],"object_to_goal_dist_end":0.14179,"object_to_goal_dist_start":0.1418,"object_z_max":0.03379,"peak_contact_force":78.30952,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":78.30952,"subtask_id":"push","tcp_end":[0.50705,0.10851,0.05577],"tcp_start":[0.50701,0.10848,0.05577],"tcp_to_object_dist_end":0.0519,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.98305,"average_solve_count":59.0,"average_success_count":59.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09505,"contact_1.contact_force":5.75817,"contact_1.speed":0.03746,"push_1.push_force":10.53279,"push_1.push_speed":0.0789},"optimized_scores":{"best_composite_score":0.54665,"best_fitness_score":0.15999,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":30.0,"contact_point_centroid":[0.49976,0.21918,-0.00048],"force_p95":247.03862,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":250.98039,"mean_force":231.82733,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49757,0.15774,0.05399]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5,0.21921,-0.00031],"force_p95":119.677,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":119.677,"mean_force":119.677,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49734,0.15851,0.05512]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50002,0.21924,-0.00028],"force_p95":88.20807,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":88.20807,"mean_force":88.20807,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49736,0.15855,0.05519]},{"body_a":"peg","body_b":"channel_base_body","contact_count":796.0,"contact_point_centroid":[0.50096,0.11601,0.00939],"force_p95":0.6115,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55354,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49571,0.18165,0.16961]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.5183,0.12,0.00941],"force_p95":0.52674,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52674,"mean_force":0.52674,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49734,0.15851,0.05512]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51794,0.12,0.00942],"force_p95":0.50296,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50296,"mean_force":0.50296,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49736,0.15855,0.05519]}],"total_contact_groups":6},"final_pose_error":0.2391,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50093,0.11608,0.03386],"final_tcp_position":[0.49739,0.1586,0.05523],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":250.98039,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":812.0,"n_steps_budget":1000.0,"object_pos_end":[0.50098,0.11609,0.03386],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19619,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":221.00217,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":826.0,"raw_peak_contact_force":250.98039,"subtask_id":"approach","tcp_end":[0.49734,0.15851,0.05512],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04759,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50097,0.11608,0.03386],"object_pos_start":[0.50098,0.11609,0.03386],"object_to_goal_dist_end":0.19618,"object_to_goal_dist_start":0.19619,"object_z_max":0.03386,"peak_contact_force":119.677,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":119.677,"subtask_id":"contact","tcp_end":[0.49736,0.15855,0.05519],"tcp_start":[0.49734,0.15851,0.05512],"tcp_to_object_dist_end":0.04766,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50093,0.11608,0.03386],"object_pos_start":[0.50097,0.11608,0.03386],"object_to_goal_dist_end":0.19617,"object_to_goal_dist_start":0.19618,"object_z_max":0.03386,"peak_contact_force":88.20807,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":88.20807,"subtask_id":"push","tcp_end":[0.49739,0.1586,0.05523],"tcp_start":[0.49736,0.15855,0.05519],"tcp_to_object_dist_end":0.04772,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.98333,"average_solve_count":60.0,"average_success_count":60.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09851,"contact_1.contact_force":18.96065,"contact_1.speed":0.03459,"push_1.push_force":2.59789,"push_1.push_speed":0.04583},"optimized_scores":{"best_composite_score":0.5551,"best_fitness_score":0.16843,"best_task_score":0.00081},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.48191,0.16717,-0.00043],"force_p95":639.81751,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":640.91926,"mean_force":458.87334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4868,0.10599,0.05419]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.48947,0.16738,-0.00066],"force_p95":556.50734,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":556.50734,"mean_force":556.50734,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48691,0.10591,0.05357]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47491,0.12,0.05333],"force_p95":491.78115,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":491.78115,"mean_force":491.78115,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48691,0.10591,0.05357]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":130.0,"contact_point_centroid":[0.47491,0.12,0.05913],"force_p95":220.49587,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":401.46819,"mean_force":158.38475,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4841,0.11134,0.06554]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.48191,0.16722,-0.00066],"force_p95":314.29156,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":314.29156,"mean_force":314.29156,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48683,0.1059,0.05358]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47487,0.12,0.05333],"force_p95":259.13145,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":259.13145,"mean_force":259.13145,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48683,0.1059,0.05358]},{"body_a":"peg","body_b":"channel_base_body","contact_count":902.0,"contact_point_centroid":[0.49528,0.06396,0.00938],"force_p95":0.55872,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55494,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48683,0.154,0.16301]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50429,0.21551,0.29313]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.4779,0.05862,0.0094],"force_p95":0.55239,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55239,"mean_force":0.55239,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48683,0.1059,0.05358]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.47968,0.05461,0.0094],"force_p95":0.54846,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54846,"mean_force":0.54846,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48691,0.10591,0.05357]}],"total_contact_groups":10},"final_pose_error":0.18688,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4949,0.06368,0.034],"final_tcp_position":[0.48698,0.10593,0.05358],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":640.91926,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":929.0,"n_steps_budget":1000.0,"object_pos_end":[0.49483,0.0638,0.034],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14402,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":635.74677,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1071.0,"raw_peak_contact_force":640.91926,"subtask_id":"approach","tcp_end":[0.48683,0.1059,0.05358],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04712,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49486,0.06373,0.034],"object_pos_start":[0.49483,0.0638,0.034],"object_to_goal_dist_end":0.14395,"object_to_goal_dist_start":0.14402,"object_z_max":0.034,"peak_contact_force":314.29156,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":314.29156,"subtask_id":"contact","tcp_end":[0.48691,0.10591,0.05357],"tcp_start":[0.48683,0.1059,0.05358],"tcp_to_object_dist_end":0.04717,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.4949,0.06368,0.034],"object_pos_start":[0.49486,0.06373,0.034],"object_to_goal_dist_end":0.14389,"object_to_goal_dist_start":0.14395,"object_z_max":0.034,"peak_contact_force":556.50734,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":556.50734,"subtask_id":"push","tcp_end":[0.48698,0.10593,0.05358],"tcp_start":[0.48691,0.10591,0.05357],"tcp_to_object_dist_end":0.04723,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```