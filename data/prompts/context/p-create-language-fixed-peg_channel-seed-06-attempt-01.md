## Search State

- **Seed**: 6
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | contact_lost | 4 | -0.1745 | 0.04 | ❌ rejected |
| 0 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.3693 | 0.23 | ✅ accepted |

**Proposal policy**: task_score is 0.04 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`
- Frozen object start: [0.5030531481177555, 0.06746166958506708, 0.04]
- Frozen task target: [0.5030531481177555, -0.09253833041493292, 0.04]
- Goal object position: (0.5030531481177555, -0.09253833041493292, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5030531481177555, 0.06746166958506708, 0.04)
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
  frozen_object_start: [0.5031, 0.0675, 0.04]
  frozen_task_target: [0.5031, -0.0925, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5030531481177555, 0.06746166958506708, 0.04]}
  frozen_targets: {'channel_exit': [0.5030531481177555, -0.09253833041493292, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de

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

## Current Skill (Q=-0.175) — your mutation base

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
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    approach_speed:
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
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.12
      axis: channel_axis
      mode: add_to_offset
      sign: positive
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
    probe_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
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
    tolerance: 0.02
    orientation:
      mode: keep_current
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
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.0], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.12, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - probe_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=world, offset=[0.5, -0.08, 0.04], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.175
- **task_score** (E): 0.042
- **fitness_score**: 0.055  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.1941 |
| descend_to_peg | 1.00 | 1.00 | 0.0360 |
| push_along_channel | 0.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.498, 0.136, 0.118) | (0.500, 0.099, 0.040)→(0.501, 0.100, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.557 | 2.127 |
| descend_to_peg | descend | 1.00 / step_budget | (0.498, 0.136, 0.118)→(0.497, 0.130, 0.083) | (0.501, 0.100, 0.034)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.545 | 0.609 |
| push_along_channel | push | 0.00 / guard_failure | (0.494, 0.080, 0.078)→(0.494, 0.080, 0.078) | (0.501, 0.099, 0.034)→(0.501, 0.091, 0.036) | 0.180→0.171 | 1.00 / 3.000 | 49.474 | 51.796 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.096
- alignment_error: None
- force_efficiency: 0.125
- terminal_score: 0.074
- phase_score: 0.063
- phase_breakdown.push_score: 0.037
- phase_breakdown.approach_score: 0.205
- phase_breakdown.contact_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.068
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.074
- **Median Q (composite search score)**: -0.170
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.314


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `080f370e6b427cbdf66706e7036a0e474f3967ccfc94f129756881a980a10a27`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `1f3f20d8b9dd2cb87de5d9f0723b4addbc88cdcf096cd2177633d23c0fa32881`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46392,"average_solve_count":97.0,"average_success_count":97.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.09253,"descend_to_peg.descend_speed":0.03175,"push_along_channel.push_distance":0.1868,"push_along_channel.push_speed":0.02353},"optimized_scores":{"best_composite_score":-0.19063,"best_fitness_score":0.03937,"best_task_score":0.00027},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":42.0,"contact_point_centroid":[0.475,0.11993,0.05596],"force_p95":33.62466,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":42.13813,"mean_force":27.88958,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.4966,0.07997,0.07811]},{"body_a":"peg","body_b":"channel_base_body","contact_count":417.0,"contact_point_centroid":[0.50309,0.06752,0.00933],"force_p95":0.57454,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56727,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49422,0.16406,0.20231]},{"body_a":"peg","body_b":"channel_base_body","contact_count":117.0,"contact_point_centroid":[0.50306,0.06745,0.00938],"force_p95":0.55051,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55115,"mean_force":0.54665,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.4995,0.10301,0.09998]},{"body_a":"peg","body_b":"channel_base_body","contact_count":307.0,"contact_point_centroid":[0.50309,0.06741,0.00938],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55092,"mean_force":0.54665,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.497,0.08697,0.07875]}],"total_contact_groups":4},"final_pose_error":0.16782,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50305,0.06742,0.0338],"final_tcp_position":[0.49662,0.08008,0.07803],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":42.13813,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":433.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54555,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":417.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.50047,0.10725,0.11667],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09198,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":117.0,"n_steps_budget":870.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.54609,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":117.0,"raw_peak_contact_force":0.55115,"tcp_end":[0.49961,0.09916,0.0829],"tcp_start":[0.50047,0.10725,0.11667],"tcp_to_object_dist_end":0.05857,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":307.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":35.24004,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":349.0,"raw_peak_contact_force":42.13813,"tcp_end":[0.49662,0.08008,0.07803],"tcp_start":[0.49663,0.08006,0.07806],"tcp_to_object_dist_end":0.04646,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `625c03a21403c0f6267b643060335ee3d751a26340ace08db5429afcee4c5ccf`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.98276,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.03515,"descend_to_peg.descend_speed":0.03991,"push_along_channel.push_distance":0.20095,"push_along_channel.push_speed":0.04996},"optimized_scores":{"best_composite_score":-0.1704,"best_fitness_score":0.0596,"best_task_score":0.05298},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.47493,0.11988,0.05996],"force_p95":52.15744,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.51097,"mean_force":36.18485,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49917,0.07953,0.0789]},{"body_a":"peg","body_b":"channel_base_body","contact_count":736.0,"contact_point_centroid":[0.5037,0.10776,0.0095],"force_p95":4.72167,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.91943,"mean_force":1.21969,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49925,0.10886,0.07884]},{"body_a":"peg","body_b":"link7","contact_count":142.0,"contact_point_centroid":[0.50369,0.12426,0.04811],"force_p95":6.50466,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.58576,"mean_force":3.67968,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49913,0.0845,0.07881]},{"body_a":"peg","body_b":"channel_base_body","contact_count":437.0,"contact_point_centroid":[0.50354,0.11167,0.00936],"force_p95":0.61786,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56251,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49715,0.18299,0.20953]},{"body_a":"peg","body_b":"channel_base_body","contact_count":113.0,"contact_point_centroid":[0.50383,0.11177,0.00939],"force_p95":0.58533,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61446,"mean_force":0.54511,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50395,0.14429,0.10113]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50376,0.20565,0.29957]}],"total_contact_groups":6},"final_pose_error":0.13852,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50378,0.10277,0.03744],"final_tcp_position":[0.49918,0.07941,0.07892],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":69.51097,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":459.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.11177,0.03382],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.58303,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":453.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.50657,0.14723,0.11846],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09181,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":113.0,"n_steps_budget":720.0,"object_pos_end":[0.50374,0.11178,0.03389],"object_pos_start":[0.50375,0.11177,0.03382],"object_to_goal_dist_end":0.19192,"object_to_goal_dist_start":0.1919,"object_z_max":0.03389,"peak_contact_force":0.53284,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":113.0,"raw_peak_contact_force":0.61446,"tcp_end":[0.50208,0.14194,0.08352],"tcp_start":[0.50657,0.14723,0.11846],"tcp_to_object_dist_end":0.0581,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":736.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.10278,0.03743],"object_pos_start":[0.50374,0.11178,0.03389],"object_to_goal_dist_end":0.18284,"object_to_goal_dist_start":0.19192,"object_z_max":0.03744,"peak_contact_force":69.51097,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":891.0,"raw_peak_contact_force":69.51097,"tcp_end":[0.49918,0.07941,0.07892],"tcp_start":[0.49917,0.0794,0.07893],"tcp_to_object_dist_end":0.04784,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `abe38b4b57ac37a91047e57d04e408cb1fd05583a47670bcb186dc9505a3f021`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.68391,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.0516,"descend_to_peg.descend_speed":0.01798,"push_along_channel.push_distance":0.17642,"push_along_channel.push_speed":0.04132},"optimized_scores":{"best_composite_score":-0.16249,"best_fitness_score":0.06751,"best_task_score":0.07395},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":17.0,"contact_point_centroid":[0.475,0.11987,0.05009],"force_p95":43.68395,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":43.73989,"mean_force":26.43218,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.4876,0.07996,0.07757]},{"body_a":"peg","body_b":"channel_base_body","contact_count":970.0,"contact_point_centroid":[0.49611,0.11272,0.0096],"force_p95":6.36416,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.12653,"mean_force":1.68085,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48758,0.11183,0.07732]},{"body_a":"attachment","body_b":"peg","contact_count":109.0,"contact_point_centroid":[0.48861,0.11783,0.06511],"force_p95":4.78211,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.8251,"mean_force":3.54369,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48756,0.08274,0.07748]},{"body_a":"peg","body_b":"link7","contact_count":273.0,"contact_point_centroid":[0.49524,0.12798,0.04746],"force_p95":5.33,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.99477,"mean_force":3.45585,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48751,0.08817,0.07737]},{"body_a":"peg","body_b":"channel_base_body","contact_count":405.0,"contact_point_centroid":[0.49635,0.1191,0.00943],"force_p95":0.63181,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55783,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48776,0.1851,0.20591]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50452,0.21206,0.29574]},{"body_a":"peg","body_b":"channel_base_body","contact_count":143.0,"contact_point_centroid":[0.49603,0.11914,0.00942],"force_p95":0.6171,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66128,"mean_force":0.5423,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48709,0.15091,0.10065]}],"total_contact_groups":7},"final_pose_error":0.10758,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49639,0.10361,0.03776],"final_tcp_position":[0.48759,0.07994,0.07756],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":43.73989,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":430.0,"n_steps_budget":1000.0,"object_pos_end":[0.49605,0.11937,0.03387],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19951,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.5423,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":429.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.48566,0.15363,0.11907],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09242,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":143.0,"n_steps_budget":1000.0,"object_pos_end":[0.49599,0.11913,0.03389],"object_pos_start":[0.49605,0.11937,0.03387],"object_to_goal_dist_end":0.19926,"object_to_goal_dist_start":0.19951,"object_z_max":0.03398,"peak_contact_force":0.55568,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":143.0,"raw_peak_contact_force":0.66128,"tcp_end":[0.49041,0.1489,0.08188],"tcp_start":[0.48566,0.15363,0.11907],"tcp_to_object_dist_end":0.05674,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":970.0,"n_steps_budget":1000.0,"object_pos_end":[0.49638,0.1036,0.03779],"object_pos_start":[0.49599,0.11913,0.03389],"object_to_goal_dist_end":0.18365,"object_to_goal_dist_start":0.19926,"object_z_max":0.03781,"peak_contact_force":43.66996,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1369.0,"raw_peak_contact_force":43.73989,"tcp_end":[0.48759,0.07994,0.07756],"tcp_start":[0.48759,0.0799,0.07758],"tcp_to_object_dist_end":0.0471,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```