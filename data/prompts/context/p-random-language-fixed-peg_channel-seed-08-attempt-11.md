## Search State

- **Seed**: 8
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | -0.2605 | 0.17 | ✅ accepted |
| 10 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | -0.4837 | 0.00 | ❌ rejected |
| 9 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | -0.2560 | 0.14 | ❌ rejected |
| 8 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | -0.2627 | 0.16 | ✅ accepted |
| 7 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | -0.2676 | 0.15 | ✅ accepted |

**Proposal policy**: task_score is 0.17 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.260) — your mutation base

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
- id: approach_peg
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
    - 0.05
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
- id: descend_to_object
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.04
    - 0.025
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
- id: align_and_contact
  type: align
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.01
    - 0.025
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: push_along_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.025
    offset_along_axis:
      distance: 0.18
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
  parameters:
    push_force_limit:
      type: scalar
      range:
      - 10.0
      - 40.0
      default: 30.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    push_lateral_offset:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.005
      binds_to:
      - path: retry.offset.x
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    push_stroke:
      type: scalar
      range:
      - 0.12
      - 0.24
      default: 0.18
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.0
  subtask_id: push
- id: retract_from_channel
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.15
  parameters:
    retract_speed:
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
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.04, 0.05]
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_object** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.04, 0.025]
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **align_and_contact** (`align`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.01, 0.025]
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
- **push_along_channel** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.025], offset_along_axis={axis=channel_axis, distance=0.18, mode=replace_offset_projection, sign=positive}
  - parameter_bindings:
    - push_force_limit: status=consumed; consumers=termination.force_threshold (replace)
    - push_lateral_offset: status=consumed; consumers=retry.offset.x (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_stroke: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.0, 0.0]
- **retract_from_channel** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15]
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.260
- **task_score** (E): 0.168
- **fitness_score**: 0.230  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.2194 |
| descend_to_object | 1.00 | 1.00 | 0.0340 |
| align_and_contact | 1.00 | 1.00 | 0.0236 |
| push_along_channel | 0.00 | 1.00 | 0.0775 |
| retract_from_channel | 0.67 | 1.00 | 0.1201 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.123, 0.097) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.536 | 3.526 |
| descend_to_object | descend | 1.00 / step_budget | (0.513, 0.123, 0.097)→(0.503, 0.120, 0.067) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.536 | 0.583 |
| align_and_contact | align | 1.00 / step_budget | (0.503, 0.120, 0.067)→(0.500, 0.099, 0.058) | (0.503, 0.080, 0.034)→(0.503, 0.071, 0.036) | 0.160→0.151 | 1.00 / 1.333 | 14.395 | 41.977 |
| push_along_channel | push | 0.00 / step_budget | (0.500, 0.099, 0.058)→(0.497, 0.022, 0.054) | (0.503, 0.071, 0.036)→(0.500, 0.023, 0.024) | 0.151→0.105 | 1.00 / 1.000 | 0.595 | 14.743 |
| retract_from_channel | retract | 0.67 / step_budget | (0.497, 0.022, 0.054)→(0.494, 0.022, 0.174) | (0.500, 0.023, 0.024)→(0.502, 0.023, 0.024) | 0.105→0.105 | 1.00 / 1.000 | 0.612 | 0.675 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.318
- alignment_error: None
- force_efficiency: 0.407
- terminal_score: 0.267
- phase_score: 0.234
- phase_breakdown.push_score: 0.051
- phase_breakdown.approach_score: 0.305
- phase_breakdown.contact_score: 0.713

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.247
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.267
- **Median Q (composite search score)**: -0.266
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at upper bound**: push_along_channel.push_speed
- **Final σ (mean)**: 0.361


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.14356,"average_solve_count":202.0,"average_success_count":202.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_and_contact.align_speed":0.02262,"approach_peg.approach_speed":0.06403,"descend_to_object.descend_speed":0.02998,"push_along_channel.push_force_limit":26.97958,"push_along_channel.push_lateral_offset":0.00704,"push_along_channel.push_speed":0.03712,"push_along_channel.push_stroke":0.21468,"retract_from_channel.retract_speed":0.0767},"optimized_scores":{"best_composite_score":-0.24256,"best_fitness_score":0.24744,"best_task_score":0.26717},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":121.0,"contact_point_centroid":[0.49855,0.11161,0.00946],"force_p95":13.34774,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.66179,"mean_force":2.21676,"phase_index":2.0,"phase_name":"align_and_contact","phase_type":"align","tcp_position_centroid":[0.48885,0.1487,0.06023]},{"body_a":"attachment","body_b":"peg","contact_count":19.0,"contact_point_centroid":[0.4933,0.13415,0.05803],"force_p95":28.24366,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.27697,"mean_force":10.98328,"phase_index":2.0,"phase_name":"align_and_contact","phase_type":"align","tcp_position_centroid":[0.48908,0.14524,0.05871]},{"body_a":"peg","body_b":"channel_base_body","contact_count":998.0,"contact_point_centroid":[0.49625,0.08301,0.00907],"force_p95":6.78122,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.45744,"mean_force":2.67511,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48773,0.10134,0.05288]},{"body_a":"attachment","body_b":"peg","contact_count":524.0,"contact_point_centroid":[0.49329,0.10722,0.05014],"force_p95":7.36587,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.09791,"mean_force":4.08326,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48751,0.11713,0.05267]},{"body_a":"peg","body_b":"channel_base_body","contact_count":623.0,"contact_point_centroid":[0.49616,0.11919,0.00943],"force_p95":0.61231,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55268,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49091,0.17956,0.19603]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49946,0.19925,0.29783]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49532,0.06817,0.00801],"force_p95":0.72551,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72551,"mean_force":0.6058,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.48513,0.06716,0.11525]},{"body_a":"peg","body_b":"channel_base_body","contact_count":132.0,"contact_point_centroid":[0.49643,0.11949,0.00942],"force_p95":0.59926,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64214,"mean_force":0.54241,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.48545,0.15958,0.08257]}],"total_contact_groups":8},"final_pose_error":0.02585,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49463,0.06813,0.0241],"final_tcp_position":[0.48546,0.06722,0.17787],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":29.66179,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":648.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11961,0.03387],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19974,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.51891,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":647.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48372,0.16068,0.09927],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0782,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":132.0,"n_steps_budget":900.0,"object_pos_end":[0.49601,0.11993,0.03385],"object_pos_start":[0.49602,0.11961,0.03387],"object_to_goal_dist_end":0.20006,"object_to_goal_dist_start":0.19974,"object_z_max":0.03396,"peak_contact_force":0.51648,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":132.0,"raw_peak_contact_force":0.64214,"tcp_end":[0.48901,0.15888,0.06581],"tcp_start":[0.48372,0.16068,0.09927],"tcp_to_object_dist_end":0.05087,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":121.0,"n_steps_budget":870.0,"object_pos_end":[0.49736,0.11227,0.03837],"object_pos_start":[0.49601,0.11993,0.03385],"object_to_goal_dist_end":0.19229,"object_to_goal_dist_start":0.20006,"object_z_max":0.03833,"peak_contact_force":0.46071,"phase_name":"align_and_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":140.0,"raw_peak_contact_force":29.66179,"subtask_id":"contact","tcp_end":[0.49037,0.13777,0.05634],"tcp_start":[0.48901,0.15888,0.06581],"tcp_to_object_dist_end":0.03197,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49591,0.0681,0.0241],"object_pos_start":[0.49736,0.11227,0.03837],"object_to_goal_dist_end":0.14901,"object_to_goal_dist_start":0.19229,"object_z_max":0.04058,"peak_contact_force":0.63682,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1522.0,"raw_peak_contact_force":9.45744,"subtask_id":"push","tcp_end":[0.48839,0.06764,0.05355],"tcp_start":[0.49037,0.13777,0.05634],"tcp_to_object_dist_end":0.0304,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49463,0.06813,0.0241],"object_pos_start":[0.49591,0.0681,0.0241],"object_to_goal_dist_end":0.14908,"object_to_goal_dist_start":0.14901,"object_z_max":0.0241,"peak_contact_force":0.63682,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.72551,"tcp_end":[0.48546,0.06722,0.17787],"tcp_start":[0.48839,0.06764,0.05355],"tcp_to_object_dist_end":0.15405,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.60563,"average_solve_count":284.0,"average_success_count":284.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_and_contact.align_speed":0.00688,"approach_peg.approach_speed":0.05082,"descend_to_object.descend_speed":0.0408,"push_along_channel.push_force_limit":16.9161,"push_along_channel.push_lateral_offset":-0.00221,"push_along_channel.push_speed":0.04621,"push_along_channel.push_stroke":0.17891,"retract_from_channel.retract_speed":0.0862},"optimized_scores":{"best_composite_score":-0.2658,"best_fitness_score":0.2242,"best_task_score":0.14097},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":148.0,"contact_point_centroid":[0.50562,0.05572,0.00937],"force_p95":43.51362,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.70474,"mean_force":15.47597,"phase_index":2.0,"phase_name":"align_and_contact","phase_type":"align","tcp_position_centroid":[0.50575,0.09407,0.06184]},{"body_a":"attachment","body_b":"peg","contact_count":61.0,"contact_point_centroid":[0.50856,0.07693,0.05827],"force_p95":43.7774,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.27789,"mean_force":36.35503,"phase_index":2.0,"phase_name":"align_and_contact","phase_type":"align","tcp_position_centroid":[0.50468,0.08776,0.05941]},{"body_a":"peg","body_b":"channel_base_body","contact_count":996.0,"contact_point_centroid":[0.50604,0.02059,0.00914],"force_p95":5.21755,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.00993,"mean_force":2.29679,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50092,0.04262,0.05397]},{"body_a":"attachment","body_b":"peg","contact_count":486.0,"contact_point_centroid":[0.50494,0.04661,0.05199],"force_p95":5.60374,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.73467,"mean_force":3.68519,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50083,0.05758,0.05382]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":21.0,"contact_point_centroid":[0.52515,0.0438,0.05999],"force_p95":4.14249,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.16178,"mean_force":1.66762,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50131,0.07513,0.05433]},{"body_a":"peg","body_b":"channel_base_body","contact_count":751.0,"contact_point_centroid":[0.50584,0.06297,0.00936],"force_p95":0.5567,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56458,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51156,0.15237,0.19392]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49977,0.19845,0.29669]},{"body_a":"peg","body_b":"channel_base_body","contact_count":991.0,"contact_point_centroid":[0.50363,0.00447,0.00807],"force_p95":0.65658,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65658,"mean_force":0.60595,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49762,0.00418,0.1228]},{"body_a":"peg","body_b":"channel_base_body","contact_count":100.0,"contact_point_centroid":[0.50599,0.06298,0.00938],"force_p95":0.55118,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55396,"mean_force":0.54655,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.51704,0.10587,0.08298]}],"total_contact_groups":9},"final_pose_error":0.01096,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50557,0.00447,0.02416],"final_tcp_position":[0.49804,0.00421,0.19344],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":44.70474,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":779.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,0.06295,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54608,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":785.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach","tcp_end":[0.5243,0.10785,0.09681],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07951,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":100.0,"n_steps_budget":660.0,"object_pos_end":[0.50595,0.06295,0.0338],"object_pos_start":[0.50595,0.06295,0.0338],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14321,"object_z_max":0.03381,"peak_contact_force":0.54493,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":100.0,"raw_peak_contact_force":0.55396,"tcp_end":[0.50935,0.10402,0.06805],"tcp_start":[0.5243,0.10785,0.09681],"tcp_to_object_dist_end":0.05358,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":148.0,"n_steps_budget":1000.0,"object_pos_end":[0.50578,0.0527,0.03531],"object_pos_start":[0.50595,0.06295,0.0338],"object_to_goal_dist_end":0.13291,"object_to_goal_dist_start":0.14321,"object_z_max":0.03506,"peak_contact_force":0.46043,"phase_name":"align_and_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":209.0,"raw_peak_contact_force":44.70474,"subtask_id":"contact","tcp_end":[0.50444,0.08271,0.0582],"tcp_start":[0.50935,0.10402,0.06805],"tcp_to_object_dist_end":0.03777,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50405,0.00446,0.02415],"object_pos_start":[0.50578,0.0527,0.03531],"object_to_goal_dist_end":0.08603,"object_to_goal_dist_start":0.13291,"object_z_max":0.04059,"peak_contact_force":0.57919,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1503.0,"raw_peak_contact_force":10.00993,"subtask_id":"push","tcp_end":[0.50086,0.00428,0.05403],"tcp_start":[0.50444,0.08271,0.0582],"tcp_to_object_dist_end":0.03005,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":991.0,"n_steps_budget":1000.0,"object_pos_end":[0.50557,0.00447,0.02416],"object_pos_start":[0.50405,0.00446,0.02415],"object_to_goal_dist_end":0.08612,"object_to_goal_dist_start":0.08603,"object_z_max":0.02416,"peak_contact_force":0.63239,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":991.0,"raw_peak_contact_force":0.65658,"tcp_end":[0.49804,0.00421,0.19344],"tcp_start":[0.50086,0.00428,0.05403],"tcp_to_object_dist_end":0.16945,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.94619,"average_solve_count":223.0,"average_success_count":223.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_and_contact.align_speed":0.04113,"approach_peg.approach_speed":0.05063,"descend_to_object.descend_speed":0.03104,"push_along_channel.push_force_limit":27.95281,"push_along_channel.push_lateral_offset":0.00797,"push_along_channel.push_speed":0.05,"push_along_channel.push_stroke":0.16192,"retract_from_channel.retract_speed":0.05573},"optimized_scores":{"best_composite_score":-0.27308,"best_fitness_score":0.21692,"best_task_score":0.09648},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":122.0,"contact_point_centroid":[0.50531,0.04904,0.00937],"force_p95":47.50628,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.56507,"mean_force":20.73008,"phase_index":2.0,"phase_name":"align_and_contact","phase_type":"align","tcp_position_centroid":[0.50722,0.08674,0.06122]},{"body_a":"attachment","body_b":"peg","contact_count":60.0,"contact_point_centroid":[0.50966,0.07007,0.05817],"force_p95":48.60752,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.07991,"mean_force":41.19252,"phase_index":2.0,"phase_name":"align_and_contact","phase_type":"align","tcp_position_centroid":[0.5059,0.08096,0.05916]},{"body_a":"peg","body_b":"channel_base_body","contact_count":995.0,"contact_point_centroid":[0.5036,0.01301,0.00907],"force_p95":5.44893,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.76187,"mean_force":2.26547,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50164,0.03422,0.05377]},{"body_a":"attachment","body_b":"peg","contact_count":450.0,"contact_point_centroid":[0.50476,0.04001,0.05251],"force_p95":5.61,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.8569,"mean_force":3.83738,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50176,0.05142,0.05383]},{"body_a":"peg","body_b":"channel_base_body","contact_count":773.0,"contact_point_centroid":[0.50597,0.05663,0.00936],"force_p95":0.60058,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56713,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.5149,0.14917,0.19353]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49986,0.19824,0.29633]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50208,-0.00228,0.00807],"force_p95":0.64359,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64364,"mean_force":0.60592,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49772,-0.00696,0.10126]},{"body_a":"peg","body_b":"channel_base_body","contact_count":108.0,"contact_point_centroid":[0.50586,0.05635,0.00938],"force_p95":0.55243,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55251,"mean_force":0.54667,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.5215,0.09965,0.08226]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52505,0.03991,0.06],"force_p95":0.29672,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.31921,"mean_force":0.12011,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50428,0.07417,0.05677]}],"total_contact_groups":9},"final_pose_error":0.05357,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50468,-0.00233,0.02415],"final_tcp_position":[0.49791,-0.00693,0.14994],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":51.56507,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":802.0,"n_steps_budget":1000.0,"object_pos_end":[0.50614,0.05659,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.54277,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":810.0,"raw_peak_contact_force":4.44541,"subtask_id":"approach","tcp_end":[0.53079,0.10174,0.09634],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08099,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":108.0,"n_steps_budget":930.0,"object_pos_end":[0.50612,0.05663,0.03378],"object_pos_start":[0.50614,0.05659,0.03378],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.13687,"object_z_max":0.03378,"peak_contact_force":0.54604,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":108.0,"raw_peak_contact_force":0.55251,"tcp_end":[0.51134,0.09769,0.06711],"tcp_start":[0.53079,0.10174,0.09634],"tcp_to_object_dist_end":0.05313,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":122.0,"n_steps_budget":600.0,"object_pos_end":[0.50487,0.04813,0.03332],"object_pos_start":[0.50612,0.05663,0.03378],"object_to_goal_dist_end":0.1284,"object_to_goal_dist_start":0.13691,"object_z_max":0.03388,"peak_contact_force":42.2642,"phase_name":"align_and_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":182.0,"raw_peak_contact_force":51.56507,"subtask_id":"contact","tcp_end":[0.50556,0.07655,0.05842],"tcp_start":[0.51134,0.09769,0.06711],"tcp_to_object_dist_end":0.03792,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50084,-0.00224,0.02415],"object_pos_start":[0.50487,0.04813,0.03332],"object_to_goal_dist_end":0.07936,"object_to_goal_dist_start":0.1284,"object_z_max":0.04057,"peak_contact_force":0.56826,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1453.0,"raw_peak_contact_force":24.76187,"subtask_id":"push","tcp_end":[0.50117,-0.00691,0.05341],"tcp_start":[0.50556,0.07655,0.05842],"tcp_to_object_dist_end":0.02963,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50468,-0.00233,0.02415],"object_pos_start":[0.50084,-0.00224,0.02415],"object_to_goal_dist_end":0.0794,"object_to_goal_dist_start":0.07936,"object_z_max":0.02415,"peak_contact_force":0.56826,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.64364,"tcp_end":[0.49791,-0.00693,0.14994],"tcp_start":[0.50117,-0.00691,0.05341],"tcp_to_object_dist_end":0.12606,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```