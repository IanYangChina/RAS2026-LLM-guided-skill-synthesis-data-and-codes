## Search State

- **Seed**: 5
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.3506 | 0.20 | ✅ accepted |

**Proposal policy**: task_score is 0.20 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.351) — your mutation base

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
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
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
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - -0.08
    - 0.04
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
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
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=world, offset=[0.5, -0.08, 0.04]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.351
- **task_score** (E): 0.202
- **fitness_score**: 0.247  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2530 |
| contact_1 | 1.00 | 1.00 | 0.0002 |
| push_1 | 0.00 | 1.00 | 0.0566 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.139, 0.056) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 2.000 | 235.458 | 312.479 |
| contact_1 | contact | 1.00 / force_exceeded | (0.508, 0.139, 0.056)→(0.508, 0.139, 0.056) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 2.000 | 140.025 | 140.025 |
| push_1 | push | 0.00 / step_budget | (0.508, 0.139, 0.056)→(0.509, 0.083, 0.052) | (0.504, 0.095, 0.034)→(0.505, 0.045, 0.031) | 0.175→0.126 | 1.00 / 3.000 | 175.872 | 601.143 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.322
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.314
- phase_score: 0.283
- phase_breakdown.push_score: 0.039
- phase_breakdown.approach_score: 0.725
- phase_breakdown.contact_score: 0.572

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.296
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.314
- **Median Q (composite search score)**: 0.366
- **K-run variance**: 0.0022
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.408


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.95536,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07487,"contact_1.contact_force":8.48501,"contact_1.speed":0.0341,"push_1.push_speed":0.07019},"optimized_scores":{"best_composite_score":0.3661,"best_fitness_score":0.26277,"best_task_score":0.24314},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":143.0,"contact_point_centroid":[0.47493,0.11989,0.05327],"force_p95":574.78063,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":641.57753,"mean_force":342.85093,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51305,0.07886,0.05236]},{"body_a":"world","body_b":"link7","contact_count":310.0,"contact_point_centroid":[0.51438,0.18546,-2e-05],"force_p95":339.85554,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":520.73604,"mean_force":130.52021,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51565,0.12313,0.05363]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":101.0,"contact_point_centroid":[0.52501,0.11983,0.06],"force_p95":452.44188,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":476.95777,"mean_force":171.52527,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51303,0.07872,0.0524]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":629.0,"contact_point_centroid":[0.52501,0.11256,0.05728],"force_p95":253.33833,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":458.46643,"mean_force":184.30202,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51416,0.11171,0.05309]},{"body_a":"world","body_b":"link7","contact_count":54.0,"contact_point_centroid":[0.52196,0.20897,-0.00036],"force_p95":254.60039,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":308.69844,"mean_force":222.55013,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51955,0.1478,0.0545]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.52238,0.20907,-0.00011],"force_p95":142.45687,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":142.45687,"mean_force":142.45687,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51928,0.14896,0.05613]},{"body_a":"attachment","body_b":"peg","contact_count":542.0,"contact_point_centroid":[0.50485,0.11812,0.04618],"force_p95":1.90801,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":94.41601,"mean_force":1.19538,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51435,0.1187,0.05324]},{"body_a":"peg","body_b":"channel_base_body","contact_count":970.0,"contact_point_centroid":[0.50259,0.0814,0.00971],"force_p95":1.48325,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":87.18667,"mean_force":1.07728,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51478,0.11633,0.05331]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":38.0,"contact_point_centroid":[0.5252,0.06284,0.04017],"force_p95":11.61842,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.82293,"mean_force":2.62819,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51268,0.0928,0.05261]},{"body_a":"peg","body_b":"channel_base_body","contact_count":872.0,"contact_point_centroid":[0.50577,0.10466,0.00938],"force_p95":0.57571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.55929,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50662,0.1756,0.16899]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50394,0.2189,0.29027]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":5.0,"contact_point_centroid":[0.47494,0.0068,0.04432],"force_p95":1.39608,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.44451,"mean_force":0.98184,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51312,0.07895,0.05237]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50572,0.08666,0.00939],"force_p95":0.55166,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55166,"mean_force":0.55166,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51928,0.14896,0.05613]}],"total_contact_groups":13},"final_pose_error":0.16037,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5028,0.01542,0.02456],"final_tcp_position":[0.51317,0.07935,0.05225],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":641.57753,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":899.0,"n_steps_budget":1000.0,"object_pos_end":[0.50591,0.10456,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":224.51936,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":958.0,"raw_peak_contact_force":308.69844,"subtask_id":"approach","tcp_end":[0.51928,0.14896,0.05613],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05145,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":660.0,"object_pos_end":[0.50587,0.10457,0.03384],"object_pos_start":[0.50591,0.10456,0.03384],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.18476,"object_z_max":0.03384,"peak_contact_force":142.45687,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":142.45687,"subtask_id":"contact","tcp_end":[0.5192,0.1489,0.05622],"tcp_start":[0.51928,0.14896,0.05613],"tcp_to_object_dist_end":0.05142,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5028,0.01542,0.02456],"object_pos_start":[0.50587,0.10457,0.03384],"object_to_goal_dist_end":0.0967,"object_to_goal_dist_start":0.18476,"object_z_max":0.04074,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2738.0,"raw_peak_contact_force":641.57753,"subtask_id":"push","tcp_end":[0.51317,0.07935,0.05225],"tcp_start":[0.5192,0.1489,0.05622],"tcp_to_object_dist_end":0.07044,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.03,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09175,"contact_1.contact_force":14.47256,"contact_1.speed":0.02539,"push_1.push_speed":0.09514},"optimized_scores":{"best_composite_score":0.28669,"best_fitness_score":0.18336,"best_task_score":0.05012},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":733.0,"contact_point_centroid":[0.46851,0.11989,0.05917],"force_p95":328.55887,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":575.34609,"mean_force":256.83105,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5032,0.08412,0.05248]},{"body_a":"world","body_b":"link7","contact_count":459.0,"contact_point_centroid":[0.49517,0.15371,-3e-05],"force_p95":293.95319,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":442.02793,"mean_force":159.46651,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50207,0.09168,0.05297]},{"body_a":"world","body_b":"link7","contact_count":35.0,"contact_point_centroid":[0.50185,0.17427,-0.00046],"force_p95":312.64557,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":338.35029,"mean_force":257.8297,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49971,0.11276,0.05394]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50213,0.17424,-0.00024],"force_p95":142.25744,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":142.25744,"mean_force":142.25744,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49956,0.11353,0.05525]},{"body_a":"peg","body_b":"channel_base_body","contact_count":986.0,"contact_point_centroid":[0.5052,0.06066,0.00942],"force_p95":0.60739,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.83162,"mean_force":0.61797,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50226,0.0878,0.0528]},{"body_a":"attachment","body_b":"peg","contact_count":36.0,"contact_point_centroid":[0.5036,0.08294,0.04712],"force_p95":6.85686,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.74497,"mean_force":2.1916,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50045,0.08269,0.05302]},{"body_a":"peg","body_b":"channel_base_body","contact_count":858.0,"contact_point_centroid":[0.50307,0.06748,0.00936],"force_p95":0.55311,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55667,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49678,0.15936,0.17016]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":51.0,"contact_point_centroid":[0.52517,0.0598,0.02638],"force_p95":0.65592,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.83671,"mean_force":0.28404,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50097,0.08045,0.05266]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51449,0.05357,0.00938],"force_p95":0.54773,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54773,"mean_force":0.54773,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49956,0.11353,0.05525]}],"total_contact_groups":9},"final_pose_error":0.16902,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50662,0.05944,0.03378],"final_tcp_position":[0.50646,0.08846,0.05216],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":575.34609,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":874.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":257.68589,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":893.0,"raw_peak_contact_force":338.35029,"subtask_id":"approach","tcp_end":[0.49956,0.11353,0.05525],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05097,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":840.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":142.25744,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":142.25744,"subtask_id":"contact","tcp_end":[0.49948,0.11349,0.05538],"tcp_start":[0.49956,0.11353,0.05525],"tcp_to_object_dist_end":0.051,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50662,0.05944,0.03378],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.13974,"object_to_goal_dist_start":0.14758,"object_z_max":0.0363,"peak_contact_force":281.97899,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2265.0,"raw_peak_contact_force":575.34609,"subtask_id":"push","tcp_end":[0.50646,0.08846,0.05216],"tcp_start":[0.49948,0.11349,0.05538],"tcp_to_object_dist_end":0.03435,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64583,"average_solve_count":96.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09527,"contact_1.contact_force":2.75201,"contact_1.speed":0.02813,"push_1.push_speed":0.05715},"optimized_scores":{"best_composite_score":0.39886,"best_fitness_score":0.29553,"best_task_score":0.31419},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":102.0,"contact_point_centroid":[0.47498,0.11987,0.05707],"force_p95":473.59656,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":586.50507,"mean_force":269.6643,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50612,0.08055,0.05234]},{"body_a":"world","body_b":"link7","contact_count":839.0,"contact_point_centroid":[0.50637,0.17804,-2e-05],"force_p95":171.9921,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":451.81318,"mean_force":127.28389,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50493,0.11509,0.05313]},{"body_a":"world","body_b":"link7","contact_count":32.0,"contact_point_centroid":[0.50821,0.21538,-0.00045],"force_p95":276.41692,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":290.38816,"mean_force":231.46498,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50602,0.15394,0.05403]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50849,0.21544,-0.00028],"force_p95":135.36112,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":135.36112,"mean_force":135.36112,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5058,0.15477,0.05522]},{"body_a":"peg","body_b":"channel_base_body","contact_count":904.0,"contact_point_centroid":[0.50427,0.08589,0.00952],"force_p95":3.11731,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.88567,"mean_force":1.15065,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50499,0.11455,0.05312]},{"body_a":"attachment","body_b":"peg","contact_count":293.0,"contact_point_centroid":[0.50477,0.10624,0.04826],"force_p95":6.55399,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.7323,"mean_force":2.08025,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50502,0.10601,0.0529]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":65.0,"contact_point_centroid":[0.52521,0.08108,0.04391],"force_p95":4.33454,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.68463,"mean_force":0.6464,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50518,0.10009,0.05282]},{"body_a":"peg","body_b":"channel_base_body","contact_count":798.0,"contact_point_centroid":[0.5036,0.11167,0.00938],"force_p95":0.61168,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55399,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4998,0.17937,0.16873]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50378,0.20566,0.29959]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52006,0.10443,0.0094],"force_p95":0.52771,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52771,"mean_force":0.52771,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5058,0.15477,0.05522]}],"total_contact_groups":10},"final_pose_error":0.16158,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50449,0.06019,0.03409],"final_tcp_position":[0.50646,0.081,0.05207],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":586.50507,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":820.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.11174,0.03382],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":224.16953,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":846.0,"raw_peak_contact_force":290.38816,"subtask_id":"approach","tcp_end":[0.5058,0.15477,0.05522],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0481,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":720.0,"object_pos_end":[0.50374,0.11174,0.03383],"object_pos_start":[0.50375,0.11174,0.03382],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19188,"object_z_max":0.03382,"peak_contact_force":135.36112,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":135.36112,"subtask_id":"contact","tcp_end":[0.50572,0.15472,0.05535],"tcp_start":[0.5058,0.15477,0.05522],"tcp_to_object_dist_end":0.04811,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50449,0.06019,0.03409],"object_pos_start":[0.50374,0.11174,0.03383],"object_to_goal_dist_end":0.14039,"object_to_goal_dist_start":0.19188,"object_z_max":0.03627,"peak_contact_force":245.6356,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2203.0,"raw_peak_contact_force":586.50507,"subtask_id":"push","tcp_end":[0.50646,0.081,0.05207],"tcp_start":[0.50572,0.15472,0.05535],"tcp_to_object_dist_end":0.02756,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```