## Search State

- **Seed**: 8
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.0086 | 0.15 | ❌ rejected |
| 6 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.0230 | 0.29 | ✅ accepted |
| 5 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | -0.1685 | 0.23 | ✅ accepted |
| 4 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0360 | 0.00 | ❌ rejected |
| 3 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | -0.1885 | 0.19 | ✅ accepted |

**Proposal policy**: task_score is 0.15 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`
- Frozen object start: [0.48615778212844485, 0.11898214746703403, 0.04]
- Frozen task target: [0.48615778212844485, -0.04101785253296597, 0.04]
- Goal object position: (0.48615778212844485, -0.04101785253296597, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48615778212844485, 0.11898214746703403, 0.04)
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
  frozen_object_start: [0.4862, 0.119, 0.04]
  frozen_task_target: [0.4862, -0.041, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48615778212844485, 0.11898214746703403, 0.04]}
  frozen_targets: {'channel_exit': [0.48615778212844485, -0.04101785253296597, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e

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

## Current Skill (Q=-0.009) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach
  anchor: object
  offset:
  - 0.0
  - 0.04
  - 0.0
- id: contact
  anchor: object
  offset:
  - 0.0
  - 0.02
  - 0.0
- id: push
  anchor: world
  offset:
  - 0.5
  - -0.08
  - 0.04
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.04
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    lateral_offset_x:
      type: scalar
      range:
      - -0.015
      - 0.015
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
  subtask_id: approach
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.02
    - 0.02
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
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
    offset:
    - 0.0
    - 0.005
    - 0.02
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 2.0
      - 20.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
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
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.02
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 1.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.03
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: push_force_guard
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
  retries:
    max_attempts: 2
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.005
  subtask_id: push
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **align_1** (`align`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.04, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.02, 0.02], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.005, 0.02], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 1.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=push_force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
  - retries: max_attempts=2, strategy=reduce_speed, offset=[0.0, 0.0, 0.005]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.009
- **task_score** (E): 0.148
- **fitness_score**: 0.331  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.150
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.667
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| lateral_align | 1.00 | 1.00 | 0.2271 |
| vertical_approach | 1.00 | 1.00 | 0.0693 |
| contact_1 | 1.00 | 1.00 | 0.0233 |
| push_1 | 0.67 | 1.00 | 0.0986 |
| retract_1 | 1.00 | 1.00 | 0.1375 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| lateral_align | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.496, 0.180, 0.074) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.535 | 3.526 |
| vertical_approach | approach | 1.00 / step_budget | (0.496, 0.180, 0.074)→(0.497, 0.112, 0.059) | (0.503, 0.080, 0.034)→(0.503, 0.076, 0.034) | 0.160→0.156 | 1.00 / 1.333 | 15.173 | 15.396 |
| contact_1 | contact | 1.00 / force_exceeded | (0.497, 0.112, 0.059)→(0.497, 0.094, 0.045) | (0.503, 0.076, 0.034)→(0.504, 0.072, 0.035) | 0.156→0.152 | 1.00 / 2.333 | 19.091 | 19.724 |
| push_1 | push | 0.67 / step_budget | (0.497, 0.094, 0.045)→(0.501, -0.004, 0.054) | (0.504, 0.072, 0.035)→(0.500, -0.009, 0.027) | 0.152→0.077 | 1.00 / 1.333 | 18.183 | 41.026 |
| retract_1 | retract | 1.00 / step_budget | (0.503, -0.065, 0.051)→(0.500, -0.062, 0.188) | (0.502, -0.067, 0.024)→(0.500, -0.066, 0.024) | 0.022→0.023 | 1.00 / 1.000 | 0.588 | 9.524 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.713
- alignment_error: None
- force_efficiency: 0.250
- terminal_score: 0.160
- phase_score: 0.559
- phase_breakdown.approach_score: 0.439
- phase_breakdown.contact_score: 0.503
- phase_breakdown.push_score: 0.617

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.458
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.226
- **Median Q (composite search score)**: -0.032
- **K-run variance**: 0.0078
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.234


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a8ce855c7f52ba2d198de8387bdd2f3b869655c206850d620daaec6ac6f298cd`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `79b30dd7102e96fb2fa0880d3932c959e04a6f943c7e87b878f77a0e54f87a94`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48649,"average_solve_count":74.0,"average_success_count":74.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force_threshold":7.59651,"contact_1.contact_speed":0.03527,"lateral_align.align_speed":0.13545,"push_1.push_distance":0.15964,"push_1.push_speed":0.05632,"push_1.push_tolerance":0.01496,"retract_1.retract_speed":0.0892,"vertical_approach.approach_speed":0.03997},"optimized_scores":{"best_composite_score":-0.10275,"best_fitness_score":0.13725,"best_task_score":0.0573},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50752,0.12,0.00923],"force_p95":53.18697,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.18697,"mean_force":53.18697,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49772,0.11633,0.06081]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.5091,0.11613,0.05774],"force_p95":52.66033,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.66033,"mean_force":52.66033,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49772,0.11633,0.06081]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51327,0.09989,0.00924],"force_p95":46.10593,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.10593,"mean_force":46.10593,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49772,0.11636,0.06083]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.5091,0.11619,0.05775],"force_p95":45.58317,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.58317,"mean_force":45.58317,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49772,0.11636,0.06083]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50037,0.11646,0.00945],"force_p95":36.97632,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.06956,"mean_force":9.35342,"phase_index":1.0,"phase_name":"vertical_approach","phase_type":"approach","tcp_position_centroid":[0.49398,0.14838,0.06362]},{"body_a":"attachment","body_b":"peg","contact_count":353.0,"contact_point_centroid":[0.50757,0.12648,0.05859],"force_p95":40.04749,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.58301,"mean_force":25.03723,"phase_index":1.0,"phase_name":"vertical_approach","phase_type":"approach","tcp_position_centroid":[0.49633,0.12784,0.06191]},{"body_a":"peg","body_b":"channel_base_body","contact_count":637.0,"contact_point_centroid":[0.4962,0.11906,0.00943],"force_p95":0.61726,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55249,"phase_index":0.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.49737,0.18932,0.18285]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.49962,0.19943,0.29752]}],"total_contact_groups":8},"final_pose_error":0.16934,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49693,0.10675,0.03347],"final_tcp_position":[0.49773,0.1163,0.0608],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":53.18697,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":662.0,"n_steps_budget":1000.0,"object_pos_end":[0.49603,0.11907,0.03393],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.1992,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.52932,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":661.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.49636,0.17996,0.07415],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07298,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49692,0.10677,0.03348],"object_pos_start":[0.49603,0.11907,0.03393],"object_to_goal_dist_end":0.18691,"object_to_goal_dist_start":0.1992,"object_z_max":0.03448,"peak_contact_force":44.42969,"phase_name":"vertical_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1353.0,"raw_peak_contact_force":45.06956,"tcp_end":[0.49772,0.11636,0.06083],"tcp_start":[0.49636,0.17996,0.07415],"tcp_to_object_dist_end":0.02899,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":750.0,"object_pos_end":[0.49692,0.10676,0.03347],"object_pos_start":[0.49692,0.10677,0.03348],"object_to_goal_dist_end":0.1869,"object_to_goal_dist_start":0.18691,"object_z_max":0.03348,"peak_contact_force":46.10593,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":46.10593,"tcp_end":[0.49772,0.11633,0.06081],"tcp_start":[0.49772,0.11636,0.06083],"tcp_to_object_dist_end":0.02898,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49693,0.10675,0.03347],"object_pos_start":[0.49692,0.10676,0.03347],"object_to_goal_dist_end":0.18689,"object_to_goal_dist_start":0.1869,"object_z_max":0.03347,"peak_contact_force":53.18697,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":53.18697,"subtask_id":"push","tcp_end":[0.49773,0.1163,0.0608],"tcp_start":[0.49772,0.11633,0.06081],"tcp_to_object_dist_end":0.02896,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0a7722137b05abd45e72adac5a0a8f18d70c24ddc36cf4c70c52ed7e5618005d`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.33333,"average_solve_count":204.0,"average_success_count":204.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force_threshold":7.47828,"contact_1.contact_speed":0.02561,"lateral_align.align_speed":0.14638,"push_1.push_distance":0.12755,"push_1.push_speed":0.04004,"push_1.push_tolerance":0.02248,"retract_1.retract_speed":0.15404,"vertical_approach.approach_speed":0.03912},"optimized_scores":{"best_composite_score":0.10937,"best_fitness_score":0.39937,"best_task_score":0.16036},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":787.0,"contact_point_centroid":[0.50311,0.01062,0.04099],"force_p95":31.72548,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.39412,"mean_force":15.73959,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49749,0.02083,0.04186]},{"body_a":"peg","body_b":"channel_base_body","contact_count":883.0,"contact_point_centroid":[0.50649,-0.02277,0.00949],"force_p95":29.04123,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.29331,"mean_force":12.36426,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49864,0.00378,0.04381]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":660.0,"contact_point_centroid":[0.52516,-0.00447,0.03092],"force_p95":14.71199,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.88407,"mean_force":7.60222,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49726,0.02217,0.04158]},{"body_a":"peg","body_b":"channel_base_body","contact_count":572.0,"contact_point_centroid":[0.49524,-0.05989,0.00822],"force_p95":8.1741,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.84009,"mean_force":1.61524,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50018,-0.05114,0.11664]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":108.0,"contact_point_centroid":[0.47488,-0.05531,0.02556],"force_p95":9.12625,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.39306,"mean_force":5.63093,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50001,-0.04692,0.12935]},{"body_a":"attachment","body_b":"peg","contact_count":223.0,"contact_point_centroid":[0.5029,0.07557,0.05205],"force_p95":4.22261,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.06683,"mean_force":2.6894,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49565,0.08721,0.03967]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":83.0,"contact_point_centroid":[0.52502,0.05661,0.04213],"force_p95":2.52642,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.12214,"mean_force":1.55106,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49589,0.08502,0.03851]},{"body_a":"peg","body_b":"channel_base_body","contact_count":716.0,"contact_point_centroid":[0.50704,0.05587,0.00958],"force_p95":3.48191,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.85448,"mean_force":1.22473,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49483,0.0969,0.04496]},{"body_a":"peg","body_b":"channel_base_body","contact_count":619.0,"contact_point_centroid":[0.50579,0.06302,0.00936],"force_p95":0.56122,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56841,"phase_index":0.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.49738,0.18927,0.18226]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.4995,0.19926,0.29566]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50594,0.06294,0.00938],"force_p95":0.5519,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54656,"phase_index":1.0,"phase_name":"vertical_approach","phase_type":"approach","tcp_position_centroid":[0.49364,0.14876,0.06325]}],"total_contact_groups":11},"final_pose_error":0.01363,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4937,-0.05907,0.02414],"final_tcp_position":[0.50049,-0.05804,0.18788],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":34.39412,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":647.0,"n_steps_budget":1000.0,"object_pos_end":[0.50602,0.06295,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54345,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":653.0,"raw_peak_contact_force":3.88411,"tcp_end":[0.49639,0.17996,0.07407],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12411,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,0.06306,0.03383],"object_pos_start":[0.50602,0.06295,0.03381],"object_to_goal_dist_end":0.14332,"object_to_goal_dist_start":0.14321,"object_z_max":0.03383,"peak_contact_force":0.54338,"phase_name":"vertical_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55532,"tcp_end":[0.49587,0.11692,0.05887],"tcp_start":[0.49639,0.17996,0.07407],"tcp_to_object_dist_end":0.06024,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":718.0,"n_steps_budget":1000.0,"object_pos_end":[0.50706,0.05518,0.03661],"object_pos_start":[0.50595,0.06306,0.03383],"object_to_goal_dist_end":0.13541,"object_to_goal_dist_start":0.14332,"object_z_max":0.03661,"peak_contact_force":9.06683,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1022.0,"raw_peak_contact_force":9.06683,"tcp_end":[0.49608,0.08309,0.03748],"tcp_start":[0.49587,0.11692,0.05887],"tcp_to_object_dist_end":0.03,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50137,-0.06001,0.02413],"object_pos_start":[0.50706,0.05518,0.03661],"object_to_goal_dist_end":0.02556,"object_to_goal_dist_start":0.13541,"object_z_max":0.0404,"peak_contact_force":0.70984,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2330.0,"raw_peak_contact_force":34.39412,"subtask_id":"push","tcp_end":[0.50283,-0.06121,0.05093],"tcp_start":[0.49608,0.08309,0.03748],"tcp_to_object_dist_end":0.02686,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":572.0,"n_steps_budget":630.0,"object_pos_end":[0.4937,-0.05907,0.02414],"object_pos_start":[0.50137,-0.06001,0.02413],"object_to_goal_dist_end":0.027,"object_to_goal_dist_start":0.02556,"object_z_max":0.02607,"peak_contact_force":0.61914,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":680.0,"raw_peak_contact_force":9.84009,"tcp_end":[0.50049,-0.05804,0.18788],"tcp_start":[0.50283,-0.06121,0.05093],"tcp_to_object_dist_end":0.16389,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `bf9c239495ea25cc1b534d0795871edaef0fee72244885088104a44eb548c1a2`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,0.05661,0.04]},{"name":"goal","value":[0.53648,-0.10339,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53648,-0.10339,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42442,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force_threshold":10.27022,"contact_1.contact_speed":0.02237,"lateral_align.align_speed":0.11845,"push_1.push_distance":0.13969,"push_1.push_speed":0.06194,"push_1.push_tolerance":0.01289,"retract_1.retract_speed":0.12634,"vertical_approach.approach_speed":0.06851},"optimized_scores":{"best_composite_score":-0.03237,"best_fitness_score":0.45763,"best_task_score":0.22575},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":873.0,"contact_point_centroid":[0.50352,-0.00526,0.04181],"force_p95":32.06129,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.49622,"mean_force":15.86158,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49803,0.00514,0.04243]},{"body_a":"peg","body_b":"channel_base_body","contact_count":816.0,"contact_point_centroid":[0.50685,-0.03197,0.00973],"force_p95":28.83229,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.61061,"mean_force":12.86452,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49869,-0.00492,0.04359]},{"body_a":"peg","body_b":"channel_base_body","contact_count":120.0,"contact_point_centroid":[0.50679,-0.10035,0.0198],"force_p95":28.21011,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.77065,"mean_force":21.83038,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50224,-0.0495,0.04927]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":654.0,"contact_point_centroid":[0.52513,-0.01847,0.03056],"force_p95":13.59669,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.07393,"mean_force":6.62018,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49758,0.00852,0.04184]},{"body_a":"peg","body_b":"channel_base_body","contact_count":688.0,"contact_point_centroid":[0.50021,-0.07305,0.00807],"force_p95":0.73726,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.20835,"mean_force":0.65184,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49967,-0.05834,0.11656]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52502,-0.04889,0.02429],"force_p95":8.67569,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.77744,"mean_force":3.1249,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49985,-0.06108,0.17396]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.47496,-0.09714,0.02446],"force_p95":8.56288,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.73658,"mean_force":2.16863,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49929,-0.05829,0.07854]},{"body_a":"peg","body_b":"channel_base_body","contact_count":643.0,"contact_point_centroid":[0.50589,0.05665,0.00936],"force_p95":0.6011,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.57132,"phase_index":0.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.49736,0.18927,0.18225]},{"body_a":"peg","body_b":"channel_base_body","contact_count":420.0,"contact_point_centroid":[0.50716,0.05026,0.00955],"force_p95":2.68183,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.99946,"mean_force":0.98523,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49535,0.09037,0.04374]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.49945,0.19923,0.29541]},{"body_a":"attachment","body_b":"peg","contact_count":105.0,"contact_point_centroid":[0.50381,0.07153,0.05493],"force_p95":2.87912,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.65699,"mean_force":1.96723,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49593,0.08336,0.03838]},{"body_a":"peg","body_b":"channel_base_body","contact_count":692.0,"contact_point_centroid":[0.50611,0.05657,0.00938],"force_p95":0.55332,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56181,"mean_force":0.5465,"phase_index":1.0,"phase_name":"vertical_approach","phase_type":"approach","tcp_position_centroid":[0.49356,0.14269,0.06173]}],"total_contact_groups":12},"final_pose_error":0.01255,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50592,-0.07301,0.02411],"final_tcp_position":[0.49996,-0.0656,0.18813],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":35.49622,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":672.0,"n_steps_budget":1000.0,"object_pos_end":[0.50615,0.05663,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.53275,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":680.0,"raw_peak_contact_force":4.44541,"tcp_end":[0.4964,0.17997,0.07414],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13015,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":692.0,"n_steps_budget":750.0,"object_pos_end":[0.50613,0.05669,0.03382],"object_pos_start":[0.50615,0.05663,0.03378],"object_to_goal_dist_end":0.13696,"object_to_goal_dist_start":0.13691,"object_z_max":0.03383,"peak_contact_force":0.54683,"phase_name":"vertical_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":692.0,"raw_peak_contact_force":0.56181,"tcp_end":[0.49645,0.10407,0.05661],"tcp_start":[0.4964,0.17997,0.07414],"tcp_to_object_dist_end":0.05346,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":420.0,"n_steps_budget":840.0,"object_pos_end":[0.50662,0.05309,0.03613],"object_pos_start":[0.50613,0.05669,0.03382],"object_to_goal_dist_end":0.13332,"object_to_goal_dist_start":0.13696,"object_z_max":0.03613,"peak_contact_force":2.10019,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":525.0,"raw_peak_contact_force":3.99946,"tcp_end":[0.49621,0.08155,0.03709],"tcp_start":[0.49645,0.10407,0.05661],"tcp_to_object_dist_end":0.03031,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50251,-0.073,0.02416],"object_pos_start":[0.50662,0.05309,0.03613],"object_to_goal_dist_end":0.0175,"object_to_goal_dist_start":0.13332,"object_z_max":0.04032,"peak_contact_force":0.65124,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2463.0,"raw_peak_contact_force":35.49622,"subtask_id":"push","tcp_end":[0.50235,-0.06855,0.05009],"tcp_start":[0.49621,0.08155,0.03709],"tcp_to_object_dist_end":0.02631,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":688.0,"n_steps_budget":750.0,"object_pos_end":[0.50592,-0.07301,0.02411],"object_pos_start":[0.50251,-0.073,0.02416],"object_to_goal_dist_end":0.01834,"object_to_goal_dist_start":0.0175,"object_z_max":0.02486,"peak_contact_force":0.55739,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":703.0,"raw_peak_contact_force":9.20835,"tcp_end":[0.49996,-0.0656,0.18813],"tcp_start":[0.50235,-0.06855,0.05009],"tcp_to_object_dist_end":0.1643,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```