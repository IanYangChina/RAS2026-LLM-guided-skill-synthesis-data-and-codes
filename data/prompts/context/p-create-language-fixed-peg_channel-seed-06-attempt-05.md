## Search State

- **Seed**: 6
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.3201 | 0.68 | ❌ rejected |
| 4 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.3254 | 0.70 | ✅ accepted |
| 3 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.0151 | 0.08 | ❌ rejected |
| 2 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.3490 | 0.28 | ✅ accepted |
| 1 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | contact_lost | 4 | -0.1745 | 0.04 | ❌ rejected |

**Proposal policy**: task_score is 0.68 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.320) — your mutation base

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
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: engage_peg
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.02
    - 0.0
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
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
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
  parameters:
    lateral_jitter:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: retry.offset.x
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.12
      - 0.25
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 3
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind_peg** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.0], tolerance=0.02
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **engage_peg** (`align`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], tolerance=0.01
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
- **push_through_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis
  - parameter_bindings:
    - lateral_jitter: status=consumed; consumers=retry.offset.x (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=3, strategy=offset_target, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.320
- **task_score** (E): 0.677
- **fitness_score**: 0.600  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind_peg | 1.00 | 1.00 | 0.2489 |
| engage_peg | 1.00 | 1.00 | 0.0274 |
| push_through_channel | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.144, 0.059) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.537 | 2.127 |
| engage_peg | align | 1.00 / step_budget | (0.497, 0.144, 0.059)→(0.496, 0.127, 0.038) | (0.501, 0.099, 0.034)→(0.501, 0.097, 0.035) | 0.180→0.177 | 1.00 / 1.333 | 1.864 | 14.925 |
| push_through_channel | push | 0.00 / guard_failure | (0.493, 0.003, 0.033)→(0.493, 0.003, 0.033) | (0.501, 0.097, 0.035)→(0.505, -0.024, 0.037) | 0.177→0.064 | 1.00 / 3.000 | 24.430 | 52.401 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 1.000
- phase_score: 0.665
- phase_breakdown.push_score: 0.621
- phase_breakdown.approach_score: 0.677
- phase_breakdown.contact_score: 0.787

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.799
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.495
- **K-run variance**: 0.0699
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.285


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29121,"average_solve_count":182.0,"average_success_count":182.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_peg.approach_speed":0.09248,"engage_peg.align_speed":0.031,"push_through_channel.lateral_jitter":0.00509,"push_through_channel.push_distance":0.21956,"push_through_channel.push_speed":0.03732},"optimized_scores":{"best_composite_score":0.49505,"best_fitness_score":0.77505,"best_task_score":0.94041},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":192.0,"contact_point_centroid":[0.49762,0.00997,0.04018],"force_p95":29.56789,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.3938,"mean_force":4.97237,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49535,0.02123,0.03301]},{"body_a":"peg","body_b":"channel_base_body","contact_count":19.0,"contact_point_centroid":[0.5071,-0.10037,0.05823],"force_p95":46.36432,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.22639,"mean_force":12.8306,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49489,-0.05204,0.03243]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":59.0,"contact_point_centroid":[0.5253,-0.06643,0.04615],"force_p95":29.97635,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.76493,"mean_force":7.92366,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4949,-0.03644,0.03246]},{"body_a":"peg","body_b":"channel_base_body","contact_count":210.0,"contact_point_centroid":[0.49917,-0.02316,0.00937],"force_p95":11.13207,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.39533,"mean_force":2.48526,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49535,0.01648,0.033]},{"body_a":"peg","body_b":"channel_base_body","contact_count":110.0,"contact_point_centroid":[0.50338,0.06607,0.00939],"force_p95":3.23003,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.97344,"mean_force":1.05021,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"align","tcp_position_centroid":[0.49819,0.10551,0.04681]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.50134,0.08452,0.04965],"force_p95":14.51392,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.95824,"mean_force":8.17124,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"align","tcp_position_centroid":[0.49845,0.09638,0.03784]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":52.0,"contact_point_centroid":[0.47469,0.01646,0.04423],"force_p95":3.6617,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.84167,"mean_force":1.01184,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49532,0.04743,0.03292]},{"body_a":"peg","body_b":"channel_base_body","contact_count":487.0,"contact_point_centroid":[0.50301,0.06749,0.00933],"force_p95":0.55988,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56432,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.49878,0.15837,0.17757]}],"total_contact_groups":8},"final_pose_error":0.06725,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50744,-0.083,0.03612],"final_tcp_position":[0.49465,-0.05703,0.03218],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":49.3938,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":503.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.06748,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54717,"phase_name":"approach_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":487.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach","tcp_end":[0.49963,0.11475,0.05789],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05316,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":110.0,"n_steps_budget":750.0,"object_pos_end":[0.5026,0.06583,0.0351],"object_pos_start":[0.50309,0.06748,0.0338],"object_to_goal_dist_end":0.14594,"object_to_goal_dist_start":0.14764,"object_z_max":0.0349,"peak_contact_force":4.85102,"phase_name":"engage_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":117.0,"raw_peak_contact_force":15.97344,"subtask_id":"contact","tcp_end":[0.49853,0.09556,0.03707],"tcp_start":[0.49963,0.11475,0.05789],"tcp_to_object_dist_end":0.03007,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":404.0,"n_steps_budget":1000.0,"object_pos_end":[0.50738,-0.08223,0.03622],"object_pos_start":[0.5026,0.06583,0.0351],"object_to_goal_dist_end":0.00858,"object_to_goal_dist_start":0.14594,"object_z_max":0.04045,"peak_contact_force":9.70102,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":532.0,"raw_peak_contact_force":49.3938,"subtask_id":"push","tcp_end":[0.49465,-0.05703,0.03218],"tcp_start":[0.49471,-0.05694,0.03225],"tcp_to_object_dist_end":0.02852,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20118,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_peg.approach_speed":0.09853,"engage_peg.align_speed":0.02444,"push_through_channel.lateral_jitter":0.00101,"push_through_channel.push_distance":0.22078,"push_through_channel.push_speed":0.05396},"optimized_scores":{"best_composite_score":0.51896,"best_fitness_score":0.79896,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.50532,-0.10126,0.04683],"force_p95":54.11192,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":55.3461,"mean_force":16.05073,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49761,-0.05383,0.0343]},{"body_a":"attachment","body_b":"peg","contact_count":248.0,"contact_point_centroid":[0.499,0.02789,0.04729],"force_p95":35.42352,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.33976,"mean_force":7.32831,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49828,0.03923,0.03504]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":157.0,"contact_point_centroid":[0.47468,0.01729,0.043],"force_p95":35.89743,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.28793,"mean_force":7.58533,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49816,0.04716,0.03479]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":23.0,"contact_point_centroid":[0.5254,-0.08064,0.04814],"force_p95":20.78411,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.587,"mean_force":6.33109,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49769,-0.04987,0.03438]},{"body_a":"peg","body_b":"channel_base_body","contact_count":91.0,"contact_point_centroid":[0.50371,0.11124,0.00946],"force_p95":0.79227,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.23515,"mean_force":1.11634,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"align","tcp_position_centroid":[0.50293,0.14809,0.04852]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.50304,0.12921,0.04836],"force_p95":16.94311,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.76953,"mean_force":7.86408,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"align","tcp_position_centroid":[0.50143,0.14112,0.04039]},{"body_a":"peg","body_b":"channel_base_body","contact_count":240.0,"contact_point_centroid":[0.49987,0.00339,0.00929],"force_p95":11.52278,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.12179,"mean_force":2.3198,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4982,0.04339,0.03497]},{"body_a":"peg","body_b":"channel_base_body","contact_count":446.0,"contact_point_centroid":[0.50356,0.11163,0.00937],"force_p95":0.61829,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56118,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.50223,0.17739,0.17514]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.49977,0.19977,0.29834]}],"total_contact_groups":9},"final_pose_error":0.02462,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50724,-0.0851,0.03514],"final_tcp_position":[0.49748,-0.057,0.03415],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":55.3461,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":468.0,"n_steps_budget":1000.0,"object_pos_end":[0.5037,0.11174,0.03396],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.54419,"phase_name":"approach_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":462.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach","tcp_end":[0.50595,0.15518,0.0588],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05009,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":91.0,"n_steps_budget":900.0,"object_pos_end":[0.50341,0.10963,0.03475],"object_pos_start":[0.5037,0.11174,0.03396],"object_to_goal_dist_end":0.18973,"object_to_goal_dist_start":0.19187,"object_z_max":0.0347,"peak_contact_force":0.66625,"phase_name":"engage_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":98.0,"raw_peak_contact_force":18.23515,"subtask_id":"contact","tcp_end":[0.50126,0.13994,0.03904],"tcp_start":[0.50595,0.15518,0.0588],"tcp_to_object_dist_end":0.03069,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":511.0,"n_steps_budget":1000.0,"object_pos_end":[0.50702,-0.08524,0.03554],"object_pos_start":[0.50341,0.10963,0.03475],"object_to_goal_dist_end":0.00983,"object_to_goal_dist_start":0.18973,"object_z_max":0.04042,"peak_contact_force":27.27352,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":688.0,"raw_peak_contact_force":55.3461,"subtask_id":"push","tcp_end":[0.49748,-0.057,0.03415],"tcp_start":[0.49753,-0.0569,0.03421],"tcp_to_object_dist_end":0.02983,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95902,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_peg.approach_speed":0.11117,"engage_peg.align_speed":0.0203,"push_through_channel.lateral_jitter":0.00504,"push_through_channel.push_distance":0.15198,"push_through_channel.push_speed":0.02635},"optimized_scores":{"best_composite_score":-0.0536,"best_fitness_score":0.2264,"best_task_score":0.08944},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.4749,0.11998,0.03563],"force_p95":50.04034,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":52.4624,"mean_force":25.03682,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48637,0.12247,0.03373]},{"body_a":"peg","body_b":"channel_base_body","contact_count":43.0,"contact_point_centroid":[0.49892,0.09825,0.00959],"force_p95":7.95319,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.35832,"mean_force":2.29637,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48741,0.13552,0.03516]},{"body_a":"attachment","body_b":"peg","contact_count":33.0,"contact_point_centroid":[0.49326,0.12565,0.05609],"force_p95":7.47783,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.03062,"mean_force":2.06025,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4874,0.13693,0.03521]},{"body_a":"peg","body_b":"channel_base_body","contact_count":117.0,"contact_point_centroid":[0.49609,0.11686,0.00943],"force_p95":1.22667,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.56533,"mean_force":0.90765,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"align","tcp_position_centroid":[0.48539,0.15421,0.04832]},{"body_a":"attachment","body_b":"peg","contact_count":15.0,"contact_point_centroid":[0.493,0.13493,0.0548],"force_p95":9.93609,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.21527,"mean_force":3.03792,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"align","tcp_position_centroid":[0.48837,0.1465,0.03896]},{"body_a":"peg","body_b":"channel_base_body","contact_count":431.0,"contact_point_centroid":[0.49629,0.11904,0.00939],"force_p95":0.62155,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56012,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.49135,0.18015,0.17419]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":22.0,"contact_point_centroid":[0.52532,0.09976,0.01997],"force_p95":1.058,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.07699,"mean_force":0.65495,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48652,0.12603,0.03399]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.49937,0.19964,0.29637]}],"total_contact_groups":8},"final_pose_error":0.12891,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50217,0.09416,0.03963],"final_tcp_position":[0.48637,0.12189,0.03361],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":52.4624,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":456.0,"n_steps_budget":1000.0,"object_pos_end":[0.49604,0.11896,0.03387],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.1991,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.5182,"phase_name":"approach_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":455.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48454,0.1618,0.05966],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05131,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":124.0,"n_steps_budget":1000.0,"object_pos_end":[0.49725,0.11596,0.03558],"object_pos_start":[0.49604,0.11896,0.03387],"object_to_goal_dist_end":0.19603,"object_to_goal_dist_start":0.1991,"object_z_max":0.03578,"peak_contact_force":0.0758,"phase_name":"engage_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":132.0,"raw_peak_contact_force":10.56533,"subtask_id":"contact","tcp_end":[0.48905,0.14504,0.03724],"tcp_start":[0.48454,0.1618,0.05966],"tcp_to_object_dist_end":0.03026,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":69.0,"n_steps_budget":1000.0,"object_pos_end":[0.50198,0.09477,0.0394],"object_pos_start":[0.49725,0.11596,0.03558],"object_to_goal_dist_end":0.17478,"object_to_goal_dist_start":0.19603,"object_z_max":0.04008,"peak_contact_force":36.31536,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":102.0,"raw_peak_contact_force":52.4624,"subtask_id":"push","tcp_end":[0.48637,0.12189,0.03361],"tcp_start":[0.48638,0.12207,0.03366],"tcp_to_object_dist_end":0.03183,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```