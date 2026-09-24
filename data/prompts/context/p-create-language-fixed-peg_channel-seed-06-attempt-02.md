## Search State

- **Seed**: 6
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.3490 | 0.28 | ✅ accepted |
| 1 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | contact_lost | 4 | -0.1745 | 0.04 | ❌ rejected |
| 0 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.3693 | 0.23 | ✅ accepted |

**Proposal policy**: task_score is 0.28 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.349) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: approach_behind_peg
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
      mode: keep_current
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
- id: engage_peg
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
      distance: 0.06
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
      - 15.0
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
- id: push_through_channel
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind_peg** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **engage_peg** (`contact`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.06, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - probe_speed: status=consumed; consumers=generator.speed (replace)
- **push_through_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.349
- **task_score** (E): 0.279
- **fitness_score**: 0.518  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.111
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind_peg | 1.00 | 1.00 | 0.2490 |
| engage_peg | 0.33 | 1.00 | 0.0284 |
| push_through_channel | 0.67 | 1.00 | 0.1886 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.144, 0.059) | (0.500, 0.099, 0.040)→(0.501, 0.105, 0.033) | 0.180→0.185 | 1.00 / 1.000 | 0.559 | 2.127 |
| engage_peg | contact | 0.33 / step_budget | (0.497, 0.144, 0.059)→(0.494, 0.117, 0.055) | (0.501, 0.105, 0.033)→(0.501, 0.092, 0.035) | 0.185→0.173 | 1.00 / 1.667 | 1300.651 | 2.497 |
| push_through_channel | push | 0.67 / step_budget | (0.494, 0.117, 0.055)→(0.494, -0.072, 0.051) | (0.501, 0.092, 0.035)→(0.505, 0.048, 0.024) | 0.173→0.129 | 1.00 / 1.667 | 120.290 | 138.877 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.287
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.155
- phase_score: 0.529
- phase_breakdown.push_score: 0.465
- phase_breakdown.approach_score: 0.677
- phase_breakdown.contact_score: 0.577

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.608
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.353
- **Median Q (composite search score)**: 0.328
- **K-run variance**: 0.0038
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.274


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.03465,"average_solve_count":202.0,"average_success_count":202.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_peg.approach_speed":0.0985,"engage_peg.contact_force":3.77488,"engage_peg.probe_speed":0.01147,"push_through_channel.push_distance":0.24679,"push_through_channel.push_speed":0.04974},"optimized_scores":{"best_composite_score":0.32782,"best_fitness_score":0.60782,"best_task_score":0.3534},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":518.0,"contact_point_centroid":[0.49834,-0.10015,0.065],"force_p95":222.4423,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":229.69371,"mean_force":212.40676,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49531,-0.0878,0.0472]},{"body_a":"attachment","body_b":"peg","contact_count":150.0,"contact_point_centroid":[0.50023,0.05252,0.04981],"force_p95":47.42932,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.9905,"mean_force":25.03078,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49393,0.06218,0.05063]},{"body_a":"peg","body_b":"channel_base_body","contact_count":998.0,"contact_point_centroid":[0.5063,0.01617,0.00836],"force_p95":28.93879,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.90018,"mean_force":4.1253,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49426,-0.04455,0.04826]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":64.0,"contact_point_centroid":[0.52501,0.0105,0.04088],"force_p95":20.56988,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.08101,"mean_force":11.40707,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49315,-0.01149,0.04945]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50382,0.06204,0.00954],"force_p95":1.40485,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.5622,"mean_force":0.74451,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"contact","tcp_position_centroid":[0.49608,0.10099,0.05322]},{"body_a":"attachment","body_b":"peg","contact_count":277.0,"contact_point_centroid":[0.4993,0.08234,0.05697],"force_p95":1.38288,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.16739,"mean_force":0.87569,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"contact","tcp_position_centroid":[0.49596,0.09403,0.05313]},{"body_a":"peg","body_b":"channel_base_body","contact_count":473.0,"contact_point_centroid":[0.50311,0.06744,0.00933],"force_p95":0.56216,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56483,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.49927,0.1565,0.17566]}],"total_contact_groups":7},"final_pose_error":0.06866,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50595,0.01092,0.02411],"final_tcp_position":[0.49814,-0.08711,0.04616],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":229.69371,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":489.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.5465,"phase_name":"approach_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":473.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach","tcp_end":[0.49971,0.11474,0.05781],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05316,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50341,0.0635,0.03616],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.1436,"object_to_goal_dist_start":0.14759,"object_z_max":0.03616,"peak_contact_force":1.05663,"phase_name":"engage_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1277.0,"raw_peak_contact_force":2.5622,"tcp_end":[0.49597,0.0914,0.05315],"tcp_start":[0.49971,0.11474,0.05781],"tcp_to_object_dist_end":0.0335,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,0.01092,0.02411],"object_pos_start":[0.50341,0.0635,0.03616],"object_to_goal_dist_end":0.09249,"object_to_goal_dist_start":0.1436,"object_z_max":0.04019,"peak_contact_force":217.90204,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1730.0,"raw_peak_contact_force":229.69371,"subtask_id":"push","tcp_end":[0.49814,-0.08711,0.04616],"tcp_start":[0.49597,0.0914,0.05315],"tcp_to_object_dist_end":0.10078,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34807,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_peg.approach_speed":0.0763,"engage_peg.contact_force":10.64157,"engage_peg.probe_speed":0.04144,"push_through_channel.push_distance":0.19591,"push_through_channel.push_speed":0.04964},"optimized_scores":{"best_composite_score":0.28635,"best_fitness_score":0.56635,"best_task_score":0.32738},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":454.0,"contact_point_centroid":[0.50535,0.06162,0.00818],"force_p95":0.78019,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.94432,"mean_force":0.70823,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49905,0.00839,0.04989]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":12.0,"contact_point_centroid":[0.52501,0.03501,0.02428],"force_p95":9.31727,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.45922,"mean_force":4.05963,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4987,-0.05814,0.0494]},{"body_a":"peg","body_b":"channel_base_body","contact_count":813.0,"contact_point_centroid":[0.50411,0.09361,0.00981],"force_p95":4.09342,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.36909,"mean_force":2.42438,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"contact","tcp_position_centroid":[0.50237,0.12565,0.05422]},{"body_a":"attachment","body_b":"peg","contact_count":597.0,"contact_point_centroid":[0.50352,0.10758,0.05394],"force_p95":3.71966,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.96104,"mean_force":2.66856,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"contact","tcp_position_centroid":[0.50225,0.11948,0.05412]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.50356,0.11173,0.00936],"force_p95":0.61856,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56259,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.50246,0.17672,0.17504]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.49995,0.19944,0.29855]}],"total_contact_groups":6},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50692,0.0594,0.02438],"final_tcp_position":[0.4987,-0.07939,0.04935],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":9.94432,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":472.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.11175,0.03385],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.53168,"phase_name":"approach_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":466.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach","tcp_end":[0.5059,0.15519,0.05886],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05018,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":813.0,"n_steps_budget":900.0,"object_pos_end":[0.50412,0.07399,0.03826],"object_pos_start":[0.50372,0.11175,0.03385],"object_to_goal_dist_end":0.15406,"object_to_goal_dist_start":0.19188,"object_z_max":0.04062,"peak_contact_force":0.43683,"phase_name":"engage_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1410.0,"raw_peak_contact_force":4.36909,"tcp_end":[0.50218,0.09762,0.05409],"tcp_start":[0.5059,0.15519,0.05886],"tcp_to_object_dist_end":0.02851,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":459.0,"n_steps_budget":1000.0,"object_pos_end":[0.50692,0.0594,0.02438],"object_pos_start":[0.50412,0.07399,0.03826],"object_to_goal_dist_end":0.14044,"object_to_goal_dist_start":0.15406,"object_z_max":0.03826,"peak_contact_force":0.52874,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":466.0,"raw_peak_contact_force":9.94432,"subtask_id":"push","tcp_end":[0.4987,-0.07939,0.04935],"tcp_start":[0.50218,0.09762,0.05409],"tcp_to_object_dist_end":0.14126,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18857,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_peg.approach_speed":0.06454,"engage_peg.contact_force":7.11977,"engage_peg.probe_speed":0.02949,"push_through_channel.push_distance":0.22939,"push_through_channel.push_speed":0.05391},"optimized_scores":{"best_composite_score":0.43295,"best_fitness_score":0.37962,"best_task_score":0.15492},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":593.0,"contact_point_centroid":[0.47499,0.01612,0.05997],"force_p95":154.81307,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":176.99292,"mean_force":133.99032,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48527,0.02201,0.05862]},{"body_a":"peg","body_b":"channel_base_body","contact_count":909.0,"contact_point_centroid":[0.49937,0.08662,0.00865],"force_p95":81.83528,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":87.73872,"mean_force":18.06618,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48502,0.04149,0.0585]},{"body_a":"attachment","body_b":"peg","contact_count":322.0,"contact_point_centroid":[0.49092,0.11311,0.05817],"force_p95":84.04948,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":87.26801,"mean_force":51.29024,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48414,0.11144,0.05814]},{"body_a":"peg","body_b":"world","contact_count":46.0,"contact_point_centroid":[0.49706,0.13357,-0.00029],"force_p95":43.90142,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.2616,"mean_force":17.70499,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48215,0.15474,0.05622]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":12.0,"contact_point_centroid":[0.52501,0.09469,0.02422],"force_p95":6.50899,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.81283,"mean_force":2.38243,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48561,-0.00655,0.0586]},{"body_a":"peg","body_b":"channel_base_body","contact_count":449.0,"contact_point_centroid":[0.4961,0.11944,0.00943],"force_p95":0.60526,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.54526,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.49138,0.17995,0.17477]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47496,0.06538,0.04683],"force_p95":1.73436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.01843,"mean_force":0.40315,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48472,0.05769,0.05876]},{"body_a":"peg","body_b":"world","contact_count":7.0,"contact_point_centroid":[0.49597,0.13378,-0.00021],"force_p95":1.00831,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.04134,"mean_force":0.7878,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.4845,0.16204,0.06129]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.49962,0.19921,0.29688]},{"body_a":"peg","body_b":"world","contact_count":10.0,"contact_point_centroid":[0.49587,0.1335,-0.00023],"force_p95":0.54556,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55997,"mean_force":0.46352,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"contact","tcp_position_centroid":[0.48347,0.16122,0.05775]}],"total_contact_groups":10},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50352,0.07299,0.0241],"final_tcp_position":[0.48631,-0.04936,0.05851],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":3900.4596,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":475.0,"n_steps_budget":1000.0,"object_pos_end":[0.49591,0.1354,0.03017],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.21566,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.59819,"phase_name":"approach_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":480.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48436,0.16171,0.05926],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04089,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":10.0,"n_steps_budget":1000.0,"object_pos_end":[0.49574,0.13966,0.02991],"object_pos_start":[0.49591,0.1354,0.03017],"object_to_goal_dist_end":0.21994,"object_to_goal_dist_start":0.21566,"object_z_max":0.03017,"peak_contact_force":3900.4596,"phase_name":"engage_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":10.0,"raw_peak_contact_force":0.55997,"tcp_end":[0.48268,0.16058,0.05673],"tcp_start":[0.48436,0.16171,0.05926],"tcp_to_object_dist_end":0.03643,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":931.0,"n_steps_budget":1000.0,"object_pos_end":[0.50352,0.07299,0.0241],"object_pos_start":[0.49574,0.13966,0.02991],"object_to_goal_dist_end":0.15386,"object_to_goal_dist_start":0.21994,"object_z_max":0.04063,"peak_contact_force":142.43953,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1890.0,"raw_peak_contact_force":176.99292,"subtask_id":"push","tcp_end":[0.48631,-0.04936,0.05851],"tcp_start":[0.48268,0.16058,0.05673],"tcp_to_object_dist_end":0.12826,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```