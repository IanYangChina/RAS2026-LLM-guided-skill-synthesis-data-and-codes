## Search State

- **Seed**: 8
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | -0.2650 | 0.17 | ✅ accepted |
| 13 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | -0.2669 | 0.17 | ❌ rejected |
| 12 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | -0.2614 | 0.11 | ❌ rejected |
| 11 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | -0.2605 | 0.17 | ✅ accepted |
| 10 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | -0.4837 | 0.00 | ❌ rejected |

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

## Current Skill (Q=-0.265) — your mutation base

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

- **Composite score**: -0.265
- **task_score** (E): 0.170
- **fitness_score**: 0.225  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.2196 |
| descend_to_object | 1.00 | 1.00 | 0.0339 |
| align_and_contact | 1.00 | 1.00 | 0.0239 |
| push_along_channel | 0.00 | 1.00 | 0.0721 |
| retract_from_channel | 0.00 | 1.00 | 0.0902 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.123, 0.097) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.531 | 3.526 |
| descend_to_object | descend | 1.00 / step_budget | (0.513, 0.123, 0.097)→(0.503, 0.120, 0.067) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.556 | 0.602 |
| align_and_contact | align | 1.00 / step_budget | (0.503, 0.120, 0.067)→(0.500, 0.099, 0.057) | (0.503, 0.080, 0.034)→(0.503, 0.070, 0.038) | 0.160→0.150 | 1.00 / 1.333 | 0.768 | 38.619 |
| push_along_channel | push | 0.00 / step_budget | (0.500, 0.099, 0.057)→(0.497, 0.027, 0.054) | (0.503, 0.070, 0.038)→(0.501, 0.025, 0.024) | 0.150→0.107 | 1.00 / 1.000 | 0.675 | 10.514 |
| retract_from_channel | retract | 0.00 / step_budget | (0.497, 0.027, 0.054)→(0.493, 0.027, 0.144) | (0.501, 0.025, 0.024)→(0.502, 0.025, 0.024) | 0.107→0.107 | 1.00 / 1.000 | 0.630 | 3.502 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.320
- alignment_error: None
- force_efficiency: 0.413
- terminal_score: 0.275
- phase_score: 0.231
- phase_breakdown.push_score: 0.045
- phase_breakdown.approach_score: 0.305
- phase_breakdown.contact_score: 0.713

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.249
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.275
- **Median Q (composite search score)**: -0.268
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.355


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.82041,"average_solve_count":245.0,"average_success_count":245.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_and_contact.align_speed":0.02065,"approach_peg.approach_speed":0.0634,"descend_to_object.descend_speed":0.03184,"push_along_channel.push_force_limit":24.03399,"push_along_channel.push_lateral_offset":-0.00221,"push_along_channel.push_speed":0.01841,"push_along_channel.push_stroke":0.18897,"retract_from_channel.retract_speed":0.01063},"optimized_scores":{"best_composite_score":-0.24148,"best_fitness_score":0.24852,"best_task_score":0.27526},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":124.0,"contact_point_centroid":[0.49924,0.11161,0.00949],"force_p95":20.27509,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.35471,"mean_force":2.50524,"phase_index":2.0,"phase_name":"align_and_contact","phase_type":"align","tcp_position_centroid":[0.48884,0.14865,0.06025]},{"body_a":"attachment","body_b":"peg","contact_count":19.0,"contact_point_centroid":[0.49305,0.13524,0.05798],"force_p95":28.4845,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.98039,"mean_force":13.1541,"phase_index":2.0,"phase_name":"align_and_contact","phase_type":"align","tcp_position_centroid":[0.48889,0.14625,0.05906]},{"body_a":"peg","body_b":"channel_base_body","contact_count":997.0,"contact_point_centroid":[0.49585,0.08415,0.00912],"force_p95":6.38723,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.7935,"mean_force":2.51571,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48761,0.10421,0.05287]},{"body_a":"attachment","body_b":"peg","contact_count":536.0,"contact_point_centroid":[0.49311,0.10753,0.05013],"force_p95":6.96807,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.4951,"mean_force":3.69472,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48743,0.11754,0.05262]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49474,0.06864,0.00806],"force_p95":0.6834,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.0833,"mean_force":0.64463,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.48471,0.07344,0.09741]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":11.0,"contact_point_centroid":[0.475,0.04415,0.02441],"force_p95":8.55398,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.63022,"mean_force":3.95578,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.48467,0.07344,0.11634]},{"body_a":"peg","body_b":"channel_base_body","contact_count":623.0,"contact_point_centroid":[0.49616,0.11919,0.00943],"force_p95":0.61231,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55268,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49091,0.17956,0.19603]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49946,0.19925,0.29783]},{"body_a":"peg","body_b":"channel_base_body","contact_count":129.0,"contact_point_centroid":[0.49604,0.11947,0.00942],"force_p95":0.59935,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64214,"mean_force":0.54267,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.48547,0.15959,0.08263]}],"total_contact_groups":9},"final_pose_error":0.06124,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49416,0.0678,0.02415],"final_tcp_position":[0.48489,0.07348,0.14242],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":29.35471,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":648.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11961,0.03387],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19974,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.51891,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":647.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48372,0.16068,0.09927],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0782,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":129.0,"n_steps_budget":840.0,"object_pos_end":[0.49607,0.11992,0.03385],"object_pos_start":[0.49602,0.11961,0.03387],"object_to_goal_dist_end":0.20006,"object_to_goal_dist_start":0.19974,"object_z_max":0.03396,"peak_contact_force":0.5929,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":129.0,"raw_peak_contact_force":0.64214,"tcp_end":[0.48901,0.15889,0.06592],"tcp_start":[0.48372,0.16068,0.09927],"tcp_to_object_dist_end":0.05096,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":124.0,"n_steps_budget":930.0,"object_pos_end":[0.4963,0.112,0.03844],"object_pos_start":[0.49607,0.11992,0.03385],"object_to_goal_dist_end":0.19204,"object_to_goal_dist_start":0.20006,"object_z_max":0.03842,"peak_contact_force":1.41373,"phase_name":"align_and_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":143.0,"raw_peak_contact_force":29.35471,"subtask_id":"contact","tcp_end":[0.49039,0.13766,0.0563],"tcp_start":[0.48901,0.15889,0.06592],"tcp_to_object_dist_end":0.03181,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49566,0.06879,0.02413],"object_pos_start":[0.4963,0.112,0.03844],"object_to_goal_dist_end":0.1497,"object_to_goal_dist_start":0.19204,"object_z_max":0.04059,"peak_contact_force":0.6834,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1533.0,"raw_peak_contact_force":10.7935,"subtask_id":"push","tcp_end":[0.48813,0.07398,0.05357],"tcp_start":[0.49039,0.13766,0.0563],"tcp_to_object_dist_end":0.03083,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49416,0.0678,0.02415],"object_pos_start":[0.49566,0.06879,0.02413],"object_to_goal_dist_end":0.14876,"object_to_goal_dist_start":0.1497,"object_z_max":0.02461,"peak_contact_force":0.64359,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1011.0,"raw_peak_contact_force":9.0833,"tcp_end":[0.48489,0.07348,0.14242],"tcp_start":[0.48813,0.07398,0.05357],"tcp_to_object_dist_end":0.11876,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.87549,"average_solve_count":257.0,"average_success_count":257.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_and_contact.align_speed":0.0142,"approach_peg.approach_speed":0.07107,"descend_to_object.descend_speed":0.03078,"push_along_channel.push_force_limit":29.44249,"push_along_channel.push_lateral_offset":-0.00182,"push_along_channel.push_speed":0.03369,"push_along_channel.push_stroke":0.23236,"retract_from_channel.retract_speed":0.02406},"optimized_scores":{"best_composite_score":-0.26825,"best_fitness_score":0.22175,"best_task_score":0.14251},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":133.0,"contact_point_centroid":[0.50556,0.0547,0.00939],"force_p95":43.44931,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.31666,"mean_force":15.66184,"phase_index":2.0,"phase_name":"align_and_contact","phase_type":"align","tcp_position_centroid":[0.5058,0.09343,0.06169]},{"body_a":"attachment","body_b":"peg","contact_count":56.0,"contact_point_centroid":[0.50849,0.077,0.05842],"force_p95":43.57577,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.88495,"mean_force":36.035,"phase_index":2.0,"phase_name":"align_and_contact","phase_type":"align","tcp_position_centroid":[0.5048,0.08788,0.05949]},{"body_a":"peg","body_b":"channel_base_body","contact_count":996.0,"contact_point_centroid":[0.50601,0.02146,0.00915],"force_p95":5.14064,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.58907,"mean_force":2.32378,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50081,0.04375,0.05382]},{"body_a":"attachment","body_b":"peg","contact_count":503.0,"contact_point_centroid":[0.5049,0.04685,0.05185],"force_p95":5.46315,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.26548,"mean_force":3.60305,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50075,0.05779,0.05369]},{"body_a":"peg","body_b":"channel_base_body","contact_count":709.0,"contact_point_centroid":[0.50582,0.06302,0.00936],"force_p95":0.55944,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56564,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51163,0.15223,0.19361]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":17.0,"contact_point_centroid":[0.52511,0.04376,0.06],"force_p95":3.58504,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.60685,"mean_force":1.52578,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.5013,0.07526,0.05426]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49982,0.19834,0.29644]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50423,0.00494,0.00805],"force_p95":0.69709,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6971,"mean_force":0.6058,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49719,0.00676,0.09628]},{"body_a":"peg","body_b":"channel_base_body","contact_count":101.0,"contact_point_centroid":[0.50612,0.0628,0.00938],"force_p95":0.55274,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55422,"mean_force":0.54659,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.51708,0.10581,0.08289]}],"total_contact_groups":9},"final_pose_error":0.06411,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50598,0.00504,0.02414],"final_tcp_position":[0.49736,0.00678,0.13983],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":44.31666,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":737.0,"n_steps_budget":1000.0,"object_pos_end":[0.50602,0.06295,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54588,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":743.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach","tcp_end":[0.52432,0.10778,0.09666],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07934,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":101.0,"n_steps_budget":870.0,"object_pos_end":[0.50598,0.06294,0.0338],"object_pos_start":[0.50602,0.06295,0.03381],"object_to_goal_dist_end":0.14319,"object_to_goal_dist_start":0.14321,"object_z_max":0.03381,"peak_contact_force":0.54513,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":101.0,"raw_peak_contact_force":0.55422,"tcp_end":[0.50935,0.10398,0.06789],"tcp_start":[0.52432,0.10778,0.09666],"tcp_to_object_dist_end":0.05345,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":133.0,"n_steps_budget":1000.0,"object_pos_end":[0.50569,0.05239,0.03558],"object_pos_start":[0.50598,0.06294,0.0338],"object_to_goal_dist_end":0.13259,"object_to_goal_dist_start":0.14319,"object_z_max":0.03535,"peak_contact_force":0.47302,"phase_name":"align_and_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":189.0,"raw_peak_contact_force":44.31666,"subtask_id":"contact","tcp_end":[0.50439,0.08266,0.05808],"tcp_start":[0.50935,0.10398,0.06789],"tcp_to_object_dist_end":0.03774,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50434,0.00499,0.02414],"object_pos_start":[0.50569,0.05239,0.03558],"object_to_goal_dist_end":0.08657,"object_to_goal_dist_start":0.13259,"object_z_max":0.04059,"peak_contact_force":0.61748,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1516.0,"raw_peak_contact_force":9.58907,"subtask_id":"push","tcp_end":[0.50069,0.00689,0.05385],"tcp_start":[0.50439,0.08266,0.05808],"tcp_to_object_dist_end":0.02999,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.00504,0.02414],"object_pos_start":[0.50434,0.00499,0.02414],"object_to_goal_dist_end":0.08671,"object_to_goal_dist_start":0.08657,"object_z_max":0.02414,"peak_contact_force":0.52114,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.6971,"tcp_end":[0.49736,0.00678,0.13983],"tcp_start":[0.50069,0.00689,0.05385],"tcp_to_object_dist_end":0.11602,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.84388,"average_solve_count":237.0,"average_success_count":237.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_and_contact.align_speed":0.02108,"approach_peg.approach_speed":0.0611,"descend_to_object.descend_speed":0.02217,"push_along_channel.push_force_limit":22.85492,"push_along_channel.push_lateral_offset":-0.00312,"push_along_channel.push_speed":0.02882,"push_along_channel.push_stroke":0.23402,"retract_from_channel.retract_speed":0.04641},"optimized_scores":{"best_composite_score":-0.28539,"best_fitness_score":0.20461,"best_task_score":0.09255},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":123.0,"contact_point_centroid":[0.50589,0.04779,0.00948],"force_p95":40.87548,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.1853,"mean_force":10.10508,"phase_index":2.0,"phase_name":"align_and_contact","phase_type":"align","tcp_position_centroid":[0.50713,0.08738,0.06115]},{"body_a":"attachment","body_b":"peg","contact_count":36.0,"contact_point_centroid":[0.50862,0.07192,0.05861],"force_p95":41.38628,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.79426,"mean_force":32.88495,"phase_index":2.0,"phase_name":"align_and_contact","phase_type":"align","tcp_position_centroid":[0.50593,0.0831,0.05935]},{"body_a":"peg","body_b":"channel_base_body","contact_count":997.0,"contact_point_centroid":[0.50549,0.01713,0.00903],"force_p95":5.28954,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.15807,"mean_force":2.21739,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50094,0.03714,0.05358]},{"body_a":"attachment","body_b":"peg","contact_count":450.0,"contact_point_centroid":[0.50514,0.04291,0.05139],"force_p95":5.63668,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.81412,"mean_force":3.73152,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50096,0.05383,0.05325]},{"body_a":"peg","body_b":"channel_base_body","contact_count":756.0,"contact_point_centroid":[0.50594,0.05664,0.00936],"force_p95":0.60154,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56756,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51494,0.14908,0.19333]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49988,0.19819,0.29622]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50421,0.00261,0.00801],"force_p95":0.72551,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72551,"mean_force":0.6058,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49733,-9e-05,0.10155]},{"body_a":"peg","body_b":"channel_base_body","contact_count":112.0,"contact_point_centroid":[0.5061,0.05659,0.00938],"force_p95":0.6032,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60841,"mean_force":0.54578,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.52154,0.09963,0.08224]}],"total_contact_groups":8},"final_pose_error":0.0544,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50558,0.00254,0.02409],"final_tcp_position":[0.49752,-7e-05,0.14983],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":42.1853,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":785.0,"n_steps_budget":1000.0,"object_pos_end":[0.50613,0.05662,0.03377],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.52923,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":793.0,"raw_peak_contact_force":4.44541,"subtask_id":"approach","tcp_end":[0.5308,0.10167,0.0962],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08084,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":112.0,"n_steps_budget":1000.0,"object_pos_end":[0.50613,0.05662,0.03378],"object_pos_start":[0.50613,0.05662,0.03377],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.1369,"object_z_max":0.03382,"peak_contact_force":0.53091,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":112.0,"raw_peak_contact_force":0.60841,"tcp_end":[0.51128,0.09768,0.06699],"tcp_start":[0.5308,0.10167,0.0962],"tcp_to_object_dist_end":0.05306,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":123.0,"n_steps_budget":960.0,"object_pos_end":[0.50554,0.04546,0.03856],"object_pos_start":[0.50613,0.05662,0.03378],"object_to_goal_dist_end":0.12559,"object_to_goal_dist_start":0.1369,"object_z_max":0.03847,"peak_contact_force":0.41822,"phase_name":"align_and_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":159.0,"raw_peak_contact_force":42.1853,"subtask_id":"contact","tcp_end":[0.50458,0.07629,0.05728],"tcp_start":[0.51128,0.09768,0.06699],"tcp_to_object_dist_end":0.03608,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50406,0.00255,0.02409],"object_pos_start":[0.50554,0.04546,0.03856],"object_to_goal_dist_end":0.08417,"object_to_goal_dist_start":0.12559,"object_z_max":0.04058,"peak_contact_force":0.72551,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1447.0,"raw_peak_contact_force":11.15807,"subtask_id":"push","tcp_end":[0.50078,-0.0,0.05413],"tcp_start":[0.50458,0.07629,0.05728],"tcp_to_object_dist_end":0.03032,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50558,0.00254,0.02409],"object_pos_start":[0.50406,0.00255,0.02409],"object_to_goal_dist_end":0.08425,"object_to_goal_dist_start":0.08417,"object_z_max":0.0241,"peak_contact_force":0.72551,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.72551,"tcp_end":[0.49752,-7e-05,0.14983],"tcp_start":[0.50078,-0.0,0.05413],"tcp_to_object_dist_end":0.12602,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```