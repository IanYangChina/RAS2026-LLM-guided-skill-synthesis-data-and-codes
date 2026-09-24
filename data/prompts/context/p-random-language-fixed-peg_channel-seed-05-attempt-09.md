## Search State

- **Seed**: 5
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4556 | 0.65 | ❌ rejected |
| 8 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.6199 | 0.92 | ❌ rejected |
| 7 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.1849 | 0.40 | ❌ rejected |
| 6 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.5812 | 0.90 | ❌ rejected |
| 5 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.6025 | 0.95 | ❌ rejected |

**Proposal policy**: task_score is 0.65 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`
- Frozen object start: [0.5244002338996304, 0.1046352631789195, 0.04]
- Frozen task target: [0.5244002338996304, -0.05536473682108051, 0.04]
- Goal object position: (0.5244002338996304, -0.05536473682108051, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5244002338996304, 0.1046352631789195, 0.04)
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
  frozen_object_start: [0.5244, 0.1046, 0.04]
  frozen_task_target: [0.5244, -0.0554, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5244002338996304, 0.1046352631789195, 0.04]}
  frozen_targets: {'channel_exit': [0.5244002338996304, -0.05536473682108051, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e

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

## Current Skill (Q=0.456) — your mutation base

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
    offset:
    - 0.0
    - 0.04
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
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
- id: contact
  type: contact
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.02
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
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
      distance: 0.05
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
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
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

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.04, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.02, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **push** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.05, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.456
- **task_score** (E): 0.646
- **fitness_score**: 0.686  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2398 |
| contact | 1.00 | 1.00 | 0.0220 |
| push | 1.00 | 1.00 | 0.2074 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.142, 0.068) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.540 | 2.488 |
| contact | contact | 1.00 / step_budget | (0.508, 0.142, 0.068)→(0.504, 0.131, 0.050) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.533 | 0.583 |
| push | push | 1.00 / step_budget | (0.504, 0.131, 0.050)→(0.504, -0.076, 0.032) | (0.504, 0.095, 0.034)→(0.502, -0.041, 0.035) | 0.175→0.047 | 1.00 / 2.000 | 72.382 | 125.565 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 1.000
- phase_score: 0.666
- phase_breakdown.contact_score: 0.734
- phase_breakdown.push_score: 0.682
- phase_breakdown.approach_score: 0.552

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.800
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.506
- **K-run variance**: 0.0142
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.304


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9b36d26f861d7a613dfb3d8c86d70470e42095a430c2befa4bd6e530468a8a7e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2af86d8f59685db6584febc0596b9044223ae39cea3120c112c665a54a1c4732`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.79322,"average_solve_count":295.0,"average_success_count":295.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.speed":0.01366,"contact.speed":0.01681,"push.push_depth":0.20183,"push.speed":0.01962},"optimized_scores":{"best_composite_score":0.29103,"best_fitness_score":0.52103,"best_task_score":0.21185},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":393.0,"contact_point_centroid":[0.50276,0.04635,0.04423],"force_p95":69.42348,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":70.59338,"mean_force":47.25856,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.5087,0.04966,0.04275]},{"body_a":"peg","body_b":"channel_base_body","contact_count":563.0,"contact_point_centroid":[0.49864,0.03385,0.00935],"force_p95":65.58401,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":68.97156,"mean_force":31.13325,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50778,0.03634,0.04117]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":155.0,"contact_point_centroid":[0.47481,0.00438,0.02554],"force_p95":31.11499,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.50679,"mean_force":16.63252,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.5089,-0.0027,0.04005]},{"body_a":"peg","body_b":"channel_base_body","contact_count":320.0,"contact_point_centroid":[0.50531,0.10464,0.00936],"force_p95":0.60033,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.58162,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50934,0.17421,0.17819]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50018,0.19872,0.29482]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":28.0,"contact_point_centroid":[0.52517,0.01391,0.05387],"force_p95":0.96157,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16156,"mean_force":0.3285,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50533,-0.04606,0.03434]},{"body_a":"peg","body_b":"channel_base_body","contact_count":55.0,"contact_point_centroid":[0.50653,0.10531,0.00939],"force_p95":0.57492,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57865,"mean_force":0.54687,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.51458,0.14683,0.05973]}],"total_contact_groups":7},"final_pose_error":0.01966,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50016,0.01594,0.03544],"final_tcp_position":[0.50304,-0.07802,0.03061],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":70.59338,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":347.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.10472,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18492,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.52962,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":352.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.51872,0.1509,0.0682],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05896,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":55.0,"n_steps_budget":1000.0,"object_pos_end":[0.506,0.10465,0.03384],"object_pos_start":[0.50593,0.10472,0.03384],"object_to_goal_dist_end":0.18485,"object_to_goal_dist_start":0.18492,"object_z_max":0.03384,"peak_contact_force":0.53977,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":55.0,"raw_peak_contact_force":0.57865,"tcp_end":[0.51096,0.14038,0.05061],"tcp_start":[0.51872,0.1509,0.0682],"tcp_to_object_dist_end":0.03978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":592.0,"n_steps_budget":1000.0,"object_pos_end":[0.50016,0.01594,0.03544],"object_pos_start":[0.506,0.10465,0.03384],"object_to_goal_dist_end":0.09605,"object_to_goal_dist_start":0.18485,"object_z_max":0.04163,"peak_contact_force":0.40822,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1139.0,"raw_peak_contact_force":70.59338,"tcp_end":[0.50304,-0.07802,0.03061],"tcp_start":[0.51096,0.14038,0.05061],"tcp_to_object_dist_end":0.09413,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `314cefd2153cfe84bc0d0d2dfbeb7f4daf8feaf5f2c7ce7d396802b52a157f39`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.97321,"average_solve_count":224.0,"average_success_count":224.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.speed":0.05493,"contact.speed":0.05352,"push.push_depth":0.1705,"push.speed":0.04232},"optimized_scores":{"best_composite_score":0.50614,"best_fitness_score":0.73614,"best_task_score":0.72535},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":533.0,"contact_point_centroid":[0.50261,0.00541,0.00791],"force_p95":105.53696,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":108.30881,"mean_force":40.12051,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.4994,0.01307,0.04225]},{"body_a":"attachment","body_b":"peg","contact_count":409.0,"contact_point_centroid":[0.50231,0.00529,0.04217],"force_p95":105.86402,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":107.84034,"mean_force":53.84803,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49976,0.00646,0.04181]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":146.0,"contact_point_centroid":[0.52521,0.02895,0.03857],"force_p95":34.88019,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.64796,"mean_force":23.63677,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49816,0.05295,0.0459]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":12.0,"contact_point_centroid":[0.47495,-0.04411,0.01903],"force_p95":26.06133,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.33263,"mean_force":14.94276,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49878,-0.02975,0.03671]},{"body_a":"peg","body_b":"channel_base_body","contact_count":341.0,"contact_point_centroid":[0.50299,0.06741,0.00931],"force_p95":0.62808,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.57186,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49975,0.15851,0.18114]},{"body_a":"peg","body_b":"channel_base_body","contact_count":31.0,"contact_point_centroid":[0.50422,0.06877,0.00938],"force_p95":0.55171,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55314,"mean_force":0.54676,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.49895,0.11466,0.06127]},{"body_a":"peg","body_b":"world","contact_count":8.0,"contact_point_centroid":[0.49873,-0.02513,-4e-05],"force_p95":0.0,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49918,-0.03454,0.03652]}],"total_contact_groups":7},"final_pose_error":0.01975,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49897,-0.0486,0.03393],"final_tcp_position":[0.50621,-0.08394,0.03756],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":108.30881,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":357.0,"n_steps_budget":1000.0,"object_pos_end":[0.50304,0.0675,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54409,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":341.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.50019,0.11837,0.06779],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06125,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":31.0,"n_steps_budget":600.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50304,0.0675,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"peak_contact_force":0.54395,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":31.0,"raw_peak_contact_force":0.55314,"tcp_end":[0.49908,0.10871,0.05384],"tcp_start":[0.50019,0.11837,0.06779],"tcp_to_object_dist_end":0.04606,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":536.0,"n_steps_budget":1000.0,"object_pos_end":[0.49897,-0.0486,0.03393],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.032,"object_to_goal_dist_start":0.14759,"object_z_max":0.04003,"peak_contact_force":55.21978,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1108.0,"raw_peak_contact_force":108.30881,"tcp_end":[0.50621,-0.08394,0.03756],"tcp_start":[0.49908,0.10871,0.05384],"tcp_to_object_dist_end":0.03627,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7acce370299b32aeef0e4239da3e97eae076cb9602edead185a6cf774ee0bc4e`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.74615,"average_solve_count":260.0,"average_success_count":260.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.speed":0.06013,"contact.speed":0.01019,"push.push_depth":0.21713,"push.speed":0.06133},"optimized_scores":{"best_composite_score":0.5697,"best_fitness_score":0.7997,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":311.0,"contact_point_centroid":[0.50666,-0.10324,0.05875],"force_p95":181.71819,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":197.79279,"mean_force":136.8891,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50066,-0.0631,0.02919]},{"body_a":"attachment","body_b":"peg","contact_count":629.0,"contact_point_centroid":[0.50442,-0.01534,0.05217],"force_p95":171.20065,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":189.24134,"mean_force":72.55673,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49973,-0.00465,0.03321]},{"body_a":"channel_base_body","body_b":"link7","contact_count":53.0,"contact_point_centroid":[0.5501,-0.1,0.06496],"force_p95":101.49906,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":109.22109,"mean_force":58.80552,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50146,-0.06626,0.028]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":455.0,"contact_point_centroid":[0.52531,-0.00624,0.04216],"force_p95":29.6773,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.31404,"mean_force":9.02123,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49943,0.02145,0.03477]},{"body_a":"peg","body_b":"channel_base_body","contact_count":350.0,"contact_point_centroid":[0.5106,-0.04133,0.00983],"force_p95":25.86831,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.05472,"mean_force":8.49118,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49966,-0.00176,0.03375]},{"body_a":"peg","body_b":"channel_base_body","contact_count":317.0,"contact_point_centroid":[0.5035,0.11176,0.00933],"force_p95":0.64985,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.57066,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50284,0.17765,0.17958]},{"body_a":"peg","body_b":"channel_base_body","contact_count":87.0,"contact_point_centroid":[0.50388,0.1114,0.00944],"force_p95":0.58135,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61848,"mean_force":0.53994,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.50289,0.15167,0.05806]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49992,0.19945,0.29864]}],"total_contact_groups":8},"final_pose_error":0.04057,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50681,-0.0894,0.03574],"final_tcp_position":[0.5029,-0.06517,0.0282],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":197.79279,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":339.0,"n_steps_budget":1000.0,"object_pos_end":[0.50374,0.11178,0.03381],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19192,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.54506,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":333.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.50623,0.15719,0.06895],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05748,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":87.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.1118,0.03396],"object_pos_start":[0.50374,0.11178,0.03381],"object_to_goal_dist_end":0.19193,"object_to_goal_dist_start":0.19192,"object_z_max":0.03395,"peak_contact_force":0.51427,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":87.0,"raw_peak_contact_force":0.61848,"tcp_end":[0.50164,0.14328,0.04605],"tcp_start":[0.50623,0.15719,0.06895],"tcp_to_object_dist_end":0.03378,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":815.0,"n_steps_budget":1000.0,"object_pos_end":[0.50681,-0.0894,0.03574],"object_pos_start":[0.50371,0.1118,0.03396],"object_to_goal_dist_end":0.01236,"object_to_goal_dist_start":0.19193,"object_z_max":0.03856,"peak_contact_force":161.51732,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1798.0,"raw_peak_contact_force":197.79279,"tcp_end":[0.5029,-0.06517,0.0282],"tcp_start":[0.50164,0.14328,0.04605],"tcp_to_object_dist_end":0.02567,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```