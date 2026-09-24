## Search State

- **Seed**: 5
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.1849 | 0.40 | ❌ rejected |
| 6 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.5812 | 0.90 | ❌ rejected |
| 5 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.6025 | 0.95 | ❌ rejected |
| 4 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.6042 | 0.99 | ✅ accepted |
| 3 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.2993 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.40 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.185) — your mutation base

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

- **Composite score**: 0.185
- **task_score** (E): 0.397
- **fitness_score**: 0.354  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.111
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2499 |
| contact | 1.00 | 1.00 | 0.0166 |
| push | 1.00 | 1.00 | 0.0430 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.140, 0.059) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.530 | 2.488 |
| contact | contact | 1.00 / step_budget | (0.508, 0.140, 0.059)→(0.505, 0.130, 0.046) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.542 | 0.585 |
| push | push | 1.00 / force_exceeded | (0.505, 0.130, 0.046)→(0.500, 0.088, 0.041) | (0.504, 0.095, 0.034)→(0.502, 0.058, 0.037) | 0.175→0.139 | 1.00 / 3.000 | 190.077 | 9.100 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.215
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.058
- phase_score: 0.286
- phase_breakdown.contact_score: 0.668
- phase_breakdown.push_score: 0.029
- phase_breakdown.approach_score: 0.673

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.455
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.574
- **Median Q (composite search score)**: 0.175
- **K-run variance**: 0.0023
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.359


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48454,"average_solve_count":97.0,"average_success_count":97.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.speed":0.09988,"contact.speed":0.06336,"push.force_threshold":30.69622,"push.push_depth":0.04073,"push.speed":0.03176},"optimized_scores":{"best_composite_score":0.24779,"best_fitness_score":0.19446,"best_task_score":0.05766},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":474.0,"contact_point_centroid":[0.50127,0.07652,0.00986],"force_p95":3.41819,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.13629,"mean_force":1.42088,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50734,0.11738,0.04084]},{"body_a":"attachment","body_b":"peg","contact_count":365.0,"contact_point_centroid":[0.505,0.10395,0.04086],"force_p95":3.27194,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.6971,"mean_force":1.33261,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50707,0.11565,0.04057]},{"body_a":"peg","body_b":"channel_base_body","contact_count":444.0,"contact_point_centroid":[0.50565,0.10463,0.00937],"force_p95":0.5793,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.5718,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50925,0.17308,0.17325]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50023,0.19864,0.29447]},{"body_a":"peg","body_b":"channel_base_body","contact_count":38.0,"contact_point_centroid":[0.50593,0.10515,0.00939],"force_p95":0.5751,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57678,"mean_force":0.54616,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.51557,0.14491,0.05255]}],"total_contact_groups":5},"final_pose_error":0.21807,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49312,0.0703,0.03459],"final_tcp_position":[0.50607,0.09726,0.04005],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":190.07714,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":471.0,"n_steps_budget":1000.0,"object_pos_end":[0.50587,0.10457,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18477,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.55047,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":476.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.5189,0.14872,0.05854],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05224,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":38.0,"n_steps_budget":600.0,"object_pos_end":[0.50591,0.10457,0.03384],"object_pos_start":[0.50587,0.10457,0.03384],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.18477,"object_z_max":0.03384,"peak_contact_force":0.54321,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":38.0,"raw_peak_contact_force":0.57678,"tcp_end":[0.51186,0.13927,0.04588],"tcp_start":[0.5189,0.14872,0.05854],"tcp_to_object_dist_end":0.03721,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":535.0,"n_steps_budget":1000.0,"object_pos_end":[0.49312,0.0703,0.03459],"object_pos_start":[0.50591,0.10457,0.03384],"object_to_goal_dist_end":0.15056,"object_to_goal_dist_start":0.18476,"object_z_max":0.03525,"peak_contact_force":190.07714,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":839.0,"raw_peak_contact_force":7.13629,"tcp_end":[0.50607,0.09726,0.04005],"tcp_start":[0.51186,0.13927,0.04588],"tcp_to_object_dist_end":0.0304,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95139,"average_solve_count":144.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.speed":0.04833,"contact.speed":0.06105,"push.force_threshold":39.18684,"push.push_depth":0.06284,"push.speed":0.05786},"optimized_scores":{"best_composite_score":0.17498,"best_fitness_score":0.45498,"best_task_score":0.57389},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":127.0,"contact_point_centroid":[0.50557,0.05591,0.0096],"force_p95":6.21283,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.71718,"mean_force":1.72833,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49615,0.09572,0.0415]},{"body_a":"attachment","body_b":"peg","contact_count":55.0,"contact_point_centroid":[0.50037,0.08104,0.05264],"force_p95":6.43941,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.49359,"mean_force":2.86884,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49548,0.0926,0.04067]},{"body_a":"peg","body_b":"channel_base_body","contact_count":500.0,"contact_point_centroid":[0.5031,0.06744,0.00934],"force_p95":0.55956,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56386,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49915,0.15669,0.17621]},{"body_a":"peg","body_b":"channel_base_body","contact_count":42.0,"contact_point_centroid":[0.50236,0.06826,0.00938],"force_p95":0.55058,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55098,"mean_force":0.5466,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.49868,0.11015,0.05182]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52501,0.05987,0.06],"force_p95":0.10103,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.10146,"mean_force":0.06936,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49519,0.08882,0.04027]}],"total_contact_groups":5},"final_pose_error":0.23106,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50693,0.06079,0.03574],"final_tcp_position":[0.49518,0.08817,0.04023],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":190.07714,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":516.0,"n_steps_budget":1000.0,"object_pos_end":[0.50303,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54836,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":500.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.49962,0.1148,0.05801],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05331,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":42.0,"n_steps_budget":600.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50303,0.06743,0.0338],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.54347,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":42.0,"raw_peak_contact_force":0.55098,"tcp_end":[0.49875,0.10344,0.04496],"tcp_start":[0.49962,0.1148,0.05801],"tcp_to_object_dist_end":0.03792,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":143.0,"n_steps_budget":1000.0,"object_pos_end":[0.50693,0.06079,0.03574],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.14103,"object_to_goal_dist_start":0.14762,"object_z_max":0.03606,"peak_contact_force":190.07714,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":186.0,"raw_peak_contact_force":7.71718,"tcp_end":[0.49518,0.08817,0.04023],"tcp_start":[0.49875,0.10344,0.04496],"tcp_to_object_dist_end":0.03013,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95858,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.speed":0.03945,"contact.speed":0.0815,"push.force_threshold":39.67635,"push.push_depth":0.0959,"push.speed":0.04108},"optimized_scores":{"best_composite_score":0.1319,"best_fitness_score":0.4119,"best_task_score":0.55976},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":756.0,"contact_point_centroid":[0.50449,0.07296,0.00991],"force_p95":10.8565,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.44678,"mean_force":6.928,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49925,0.1109,0.04191]},{"body_a":"attachment","body_b":"peg","contact_count":717.0,"contact_point_centroid":[0.50196,0.09764,0.04145],"force_p95":10.51151,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.08924,"mean_force":6.89963,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49913,0.10911,0.04176]},{"body_a":"peg","body_b":"channel_base_body","contact_count":469.0,"contact_point_centroid":[0.50361,0.11172,0.00937],"force_p95":0.61578,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56076,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50237,0.17681,0.17561]},{"body_a":"peg","body_b":"channel_base_body","contact_count":36.0,"contact_point_centroid":[0.50255,0.11071,0.00945],"force_p95":0.6013,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62687,"mean_force":0.53614,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.50418,0.15186,0.05343]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.4998,0.19946,0.29892]}],"total_contact_groups":5},"final_pose_error":0.25306,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50653,0.04435,0.04052],"final_tcp_position":[0.49892,0.07716,0.0413],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":190.07714,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":491.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.11175,0.03383],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.49212,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":485.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.50591,0.15526,0.05915],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05038,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":36.0,"n_steps_budget":600.0,"object_pos_end":[0.50372,0.11181,0.03405],"object_pos_start":[0.50371,0.11175,0.03383],"object_to_goal_dist_end":0.19194,"object_to_goal_dist_start":0.19188,"object_z_max":0.03406,"peak_contact_force":0.54075,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":36.0,"raw_peak_contact_force":0.62687,"tcp_end":[0.503,0.14656,0.04689],"tcp_start":[0.50591,0.15526,0.05915],"tcp_to_object_dist_end":0.03706,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":760.0,"n_steps_budget":1000.0,"object_pos_end":[0.50653,0.04435,0.04052],"object_pos_start":[0.50372,0.11181,0.03405],"object_to_goal_dist_end":0.12452,"object_to_goal_dist_start":0.19194,"object_z_max":0.04057,"peak_contact_force":190.07714,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1473.0,"raw_peak_contact_force":12.44678,"tcp_end":[0.49892,0.07716,0.0413],"tcp_start":[0.503,0.14656,0.04689],"tcp_to_object_dist_end":0.03369,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```