## Search State

- **Seed**: 8
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | -0.2669 | 0.17 | ❌ rejected |
| 12 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | -0.2614 | 0.11 | ❌ rejected |
| 11 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | -0.2605 | 0.17 | ✅ accepted |
| 10 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | -0.4837 | 0.00 | ❌ rejected |
| 9 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | -0.2560 | 0.14 | ❌ rejected |

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

## Current Skill (Q=-0.267) — your mutation base

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

- **Composite score**: -0.267
- **task_score** (E): 0.166
- **fitness_score**: 0.223  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.2195 |
| descend_to_object | 1.00 | 1.00 | 0.0341 |
| align_and_contact | 1.00 | 1.00 | 0.0244 |
| push_along_channel | 0.00 | 1.00 | 0.0756 |
| retract_from_channel | 0.67 | 1.00 | 0.1183 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.123, 0.097) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.544 | 3.526 |
| descend_to_object | descend | 1.00 / step_budget | (0.513, 0.123, 0.097)→(0.503, 0.120, 0.067) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.543 | 0.600 |
| align_and_contact | align | 1.00 / step_budget | (0.503, 0.120, 0.067)→(0.499, 0.099, 0.057) | (0.503, 0.080, 0.034)→(0.503, 0.070, 0.039) | 0.160→0.150 | 1.00 / 1.333 | 2.972 | 30.366 |
| push_along_channel | push | 0.00 / step_budget | (0.499, 0.099, 0.057)→(0.496, 0.023, 0.054) | (0.503, 0.070, 0.039)→(0.501, 0.028, 0.024) | 0.150→0.109 | 1.00 / 1.000 | 0.646 | 10.555 |
| retract_from_channel | retract | 0.67 / step_budget | (0.496, 0.023, 0.054)→(0.493, 0.023, 0.172) | (0.501, 0.028, 0.024)→(0.503, 0.028, 0.024) | 0.109→0.109 | 1.00 / 1.000 | 0.622 | 6.750 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.315
- alignment_error: None
- force_efficiency: 0.753
- terminal_score: 0.268
- phase_score: 0.241
- phase_breakdown.push_score: 0.064
- phase_breakdown.approach_score: 0.305
- phase_breakdown.contact_score: 0.711

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.252
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.268
- **Median Q (composite search score)**: -0.278
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.382


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.94554,"average_solve_count":202.0,"average_success_count":202.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_and_contact.align_speed":0.03188,"approach_peg.approach_speed":0.05471,"descend_to_object.descend_speed":0.04225,"push_along_channel.push_force_limit":26.51413,"push_along_channel.push_lateral_offset":-0.00833,"push_along_channel.push_speed":0.04686,"push_along_channel.push_stroke":0.21346,"retract_from_channel.retract_speed":0.05503},"optimized_scores":{"best_composite_score":-0.23802,"best_fitness_score":0.25198,"best_task_score":0.26783},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":117.0,"contact_point_centroid":[0.49843,0.11094,0.00956],"force_p95":6.76415,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.33052,"mean_force":1.24527,"phase_index":2.0,"phase_name":"align_and_contact","phase_type":"align","tcp_position_centroid":[0.48894,0.14791,0.06016]},{"body_a":"attachment","body_b":"peg","contact_count":16.0,"contact_point_centroid":[0.49282,0.13234,0.05785],"force_p95":10.00538,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.66972,"mean_force":5.56307,"phase_index":2.0,"phase_name":"align_and_contact","phase_type":"align","tcp_position_centroid":[0.48925,0.14374,0.05844]},{"body_a":"peg","body_b":"channel_base_body","contact_count":998.0,"contact_point_centroid":[0.49571,0.08159,0.0089],"force_p95":7.24387,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.78453,"mean_force":2.60383,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48785,0.09561,0.05309]},{"body_a":"attachment","body_b":"peg","contact_count":441.0,"contact_point_centroid":[0.49339,0.10719,0.05027],"force_p95":7.59137,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.44523,"mean_force":4.66226,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48761,0.11709,0.05279]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49409,0.0689,0.00802],"force_p95":0.72551,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.53437,"mean_force":0.63112,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.48521,0.05613,0.10362]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.475,0.04434,0.02431],"force_p95":8.90935,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.05195,"mean_force":3.52285,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.48494,0.0561,0.09319]},{"body_a":"peg","body_b":"channel_base_body","contact_count":640.0,"contact_point_centroid":[0.49615,0.1191,0.00945],"force_p95":0.60863,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55064,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49089,0.17955,0.19597]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49946,0.19927,0.29791]},{"body_a":"peg","body_b":"channel_base_body","contact_count":129.0,"contact_point_centroid":[0.49643,0.11952,0.00949],"force_p95":0.55974,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64184,"mean_force":0.53529,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.48553,0.15942,0.08241]}],"total_contact_groups":9},"final_pose_error":0.05006,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49442,0.06853,0.0241],"final_tcp_position":[0.48541,0.05617,0.15404],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":12.33052,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":665.0,"n_steps_budget":1000.0,"object_pos_end":[0.49604,0.11909,0.03382],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19923,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.52366,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":664.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48372,0.16069,0.0993],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07855,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":129.0,"n_steps_budget":660.0,"object_pos_end":[0.49601,0.11904,0.034],"object_pos_start":[0.49604,0.11909,0.03382],"object_to_goal_dist_end":0.19917,"object_to_goal_dist_start":0.19923,"object_z_max":0.03404,"peak_contact_force":0.52489,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":129.0,"raw_peak_contact_force":0.64184,"tcp_end":[0.48906,0.15852,0.06571],"tcp_start":[0.48372,0.16069,0.0993],"tcp_to_object_dist_end":0.05112,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":117.0,"n_steps_budget":630.0,"object_pos_end":[0.49688,0.11159,0.0387],"object_pos_start":[0.49601,0.11904,0.034],"object_to_goal_dist_end":0.19162,"object_to_goal_dist_start":0.19917,"object_z_max":0.03867,"peak_contact_force":8.05029,"phase_name":"align_and_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":133.0,"raw_peak_contact_force":12.33052,"subtask_id":"contact","tcp_end":[0.49044,0.13676,0.05634],"tcp_start":[0.48906,0.15852,0.06571],"tcp_to_object_dist_end":0.0314,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4947,0.06917,0.02409],"object_pos_start":[0.49688,0.11159,0.0387],"object_to_goal_dist_end":0.15011,"object_to_goal_dist_start":0.19162,"object_z_max":0.04054,"peak_contact_force":0.72551,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1439.0,"raw_peak_contact_force":10.78453,"subtask_id":"push","tcp_end":[0.48859,0.05656,0.054],"tcp_start":[0.49044,0.13676,0.05634],"tcp_to_object_dist_end":0.03303,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49442,0.06853,0.0241],"object_pos_start":[0.4947,0.06917,0.02409],"object_to_goal_dist_end":0.14948,"object_to_goal_dist_start":0.15011,"object_z_max":0.02456,"peak_contact_force":0.63682,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1008.0,"raw_peak_contact_force":9.53437,"tcp_end":[0.48541,0.05617,0.15404],"tcp_start":[0.48859,0.05656,0.054],"tcp_to_object_dist_end":0.13084,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.46302,"average_solve_count":311.0,"average_success_count":311.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_and_contact.align_speed":0.005,"approach_peg.approach_speed":0.08686,"descend_to_object.descend_speed":0.01355,"push_along_channel.push_force_limit":37.72865,"push_along_channel.push_lateral_offset":-0.00232,"push_along_channel.push_speed":0.01284,"push_along_channel.push_stroke":0.20673,"retract_from_channel.retract_speed":0.09312},"optimized_scores":{"best_composite_score":-0.27844,"best_fitness_score":0.21156,"best_task_score":0.1363},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":150.0,"contact_point_centroid":[0.50599,0.05549,0.00946],"force_p95":40.40791,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.8873,"mean_force":9.9251,"phase_index":2.0,"phase_name":"align_and_contact","phase_type":"align","tcp_position_centroid":[0.50569,0.09479,0.06183]},{"body_a":"attachment","body_b":"peg","contact_count":43.0,"contact_point_centroid":[0.50789,0.07822,0.05857],"force_p95":40.72001,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.46678,"mean_force":32.92164,"phase_index":2.0,"phase_name":"align_and_contact","phase_type":"align","tcp_position_centroid":[0.50461,0.08925,0.05954]},{"body_a":"peg","body_b":"channel_base_body","contact_count":933.0,"contact_point_centroid":[0.5064,0.00936,0.00808],"force_p95":0.72551,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.07313,"mean_force":0.76359,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49708,0.01322,0.1229]},{"body_a":"peg","body_b":"channel_base_body","contact_count":994.0,"contact_point_centroid":[0.50604,0.02413,0.00918],"force_p95":5.31719,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.63402,"mean_force":2.35405,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50035,0.04673,0.0538]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":40.0,"contact_point_centroid":[0.52501,0.00747,0.0244],"force_p95":9.42435,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.57097,"mean_force":4.03155,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.497,0.01323,0.13486]},{"body_a":"attachment","body_b":"peg","contact_count":495.0,"contact_point_centroid":[0.50451,0.04916,0.05158],"force_p95":5.13622,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.27746,"mean_force":3.31568,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50027,0.06007,0.05347]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":42.0,"contact_point_centroid":[0.52501,0.01712,0.02473],"force_p95":8.64012,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.92572,"mean_force":4.4763,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50024,0.02274,0.05409]},{"body_a":"peg","body_b":"channel_base_body","contact_count":696.0,"contact_point_centroid":[0.50575,0.063,0.00936],"force_p95":0.55977,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.566,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51163,0.15227,0.1937]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49984,0.1983,0.29635]},{"body_a":"peg","body_b":"channel_base_body","contact_count":109.0,"contact_point_centroid":[0.50597,0.06283,0.00938],"force_p95":0.55273,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55422,"mean_force":0.54653,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.51724,0.1059,0.08336]}],"total_contact_groups":10},"final_pose_error":0.01129,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50694,0.01016,0.02471],"final_tcp_position":[0.4975,0.01326,0.19341],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":42.8873,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":724.0,"n_steps_budget":1000.0,"object_pos_end":[0.50602,0.06303,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54974,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":730.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach","tcp_end":[0.52432,0.10779,0.09668],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07932,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":109.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.06304,0.0338],"object_pos_start":[0.50602,0.06303,0.0338],"object_to_goal_dist_end":0.1433,"object_to_goal_dist_start":0.14329,"object_z_max":0.03381,"peak_contact_force":0.54336,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":109.0,"raw_peak_contact_force":0.55422,"tcp_end":[0.5093,0.10403,0.06789],"tcp_start":[0.52432,0.10779,0.09668],"tcp_to_object_dist_end":0.05342,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":150.0,"n_steps_budget":1000.0,"object_pos_end":[0.50567,0.05109,0.03863],"object_pos_start":[0.50599,0.06304,0.0338],"object_to_goal_dist_end":0.13122,"object_to_goal_dist_start":0.1433,"object_z_max":0.03852,"peak_contact_force":0.40632,"phase_name":"align_and_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":193.0,"raw_peak_contact_force":42.8873,"subtask_id":"contact","tcp_end":[0.50386,0.08263,0.05752],"tcp_start":[0.5093,0.10403,0.06789],"tcp_to_object_dist_end":0.0368,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50636,0.00899,0.02415],"object_pos_start":[0.50567,0.05109,0.03863],"object_to_goal_dist_end":0.09061,"object_to_goal_dist_start":0.13122,"object_z_max":0.0406,"peak_contact_force":0.56795,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1531.0,"raw_peak_contact_force":9.63402,"subtask_id":"push","tcp_end":[0.50031,0.01338,0.05434],"tcp_start":[0.50386,0.08263,0.05752],"tcp_to_object_dist_end":0.0311,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":933.0,"n_steps_budget":1000.0,"object_pos_end":[0.50694,0.01016,0.02471],"object_pos_start":[0.50636,0.00899,0.02415],"object_to_goal_dist_end":0.09171,"object_to_goal_dist_start":0.09061,"object_z_max":0.02505,"peak_contact_force":0.58466,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":973.0,"raw_peak_contact_force":10.07313,"tcp_end":[0.4975,0.01326,0.19341],"tcp_start":[0.50031,0.01338,0.05434],"tcp_to_object_dist_end":0.16899,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.47305,"average_solve_count":334.0,"average_success_count":334.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_and_contact.align_speed":0.00582,"approach_peg.approach_speed":0.04512,"descend_to_object.descend_speed":0.02347,"push_along_channel.push_force_limit":28.23544,"push_along_channel.push_lateral_offset":-0.00722,"push_along_channel.push_speed":0.02441,"push_along_channel.push_stroke":0.23998,"retract_from_channel.retract_speed":0.07092},"optimized_scores":{"best_composite_score":-0.28419,"best_fitness_score":0.20581,"best_task_score":0.09264},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":141.0,"contact_point_centroid":[0.50606,0.04919,0.00952],"force_p95":33.14702,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.87891,"mean_force":3.66246,"phase_index":2.0,"phase_name":"align_and_contact","phase_type":"align","tcp_position_centroid":[0.50705,0.08868,0.06112]},{"body_a":"attachment","body_b":"peg","contact_count":18.0,"contact_point_centroid":[0.50757,0.07332,0.0588],"force_p95":35.26938,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.51305,"mean_force":24.82077,"phase_index":2.0,"phase_name":"align_and_contact","phase_type":"align","tcp_position_centroid":[0.50583,0.0848,0.05933]},{"body_a":"peg","body_b":"channel_base_body","contact_count":997.0,"contact_point_centroid":[0.50533,0.01845,0.00901],"force_p95":6.31342,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.24701,"mean_force":2.4783,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50063,0.03666,0.05314]},{"body_a":"attachment","body_b":"peg","contact_count":454.0,"contact_point_centroid":[0.50512,0.04453,0.0509],"force_p95":7.59163,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.92356,"mean_force":4.28056,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50069,0.05531,0.05286]},{"body_a":"peg","body_b":"channel_base_body","contact_count":775.0,"contact_point_centroid":[0.50595,0.05662,0.00936],"force_p95":0.60152,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56701,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51488,0.14921,0.19361]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49984,0.19828,0.29641]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":15.0,"contact_point_centroid":[0.52507,0.03931,0.06],"force_p95":2.24082,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.25531,"mean_force":0.99718,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50199,0.07192,0.05411]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50402,0.00469,0.00807],"force_p95":0.64358,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64364,"mean_force":0.60592,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49722,-0.00106,0.11151]},{"body_a":"peg","body_b":"channel_base_body","contact_count":112.0,"contact_point_centroid":[0.50612,0.0566,0.00937],"force_p95":0.60176,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60305,"mean_force":0.54676,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.5215,0.09968,0.08229]}],"total_contact_groups":9},"final_pose_error":0.03441,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5064,0.00466,0.02415],"final_tcp_position":[0.49754,-0.00103,0.16953],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":35.87891,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":804.0,"n_steps_budget":1000.0,"object_pos_end":[0.50616,0.05662,0.03376],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.55964,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":812.0,"raw_peak_contact_force":4.44541,"subtask_id":"approach","tcp_end":[0.53079,0.10176,0.09638],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08102,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":112.0,"n_steps_budget":1000.0,"object_pos_end":[0.50617,0.05662,0.03376],"object_pos_start":[0.50616,0.05662,0.03376],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.13691,"object_z_max":0.03376,"peak_contact_force":0.56065,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":112.0,"raw_peak_contact_force":0.60305,"tcp_end":[0.51124,0.0977,0.06696],"tcp_start":[0.53079,0.10176,0.09638],"tcp_to_object_dist_end":0.05306,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":141.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0477,0.03888],"object_pos_start":[0.50617,0.05662,0.03376],"object_to_goal_dist_end":0.12784,"object_to_goal_dist_start":0.1369,"object_z_max":0.03889,"peak_contact_force":0.45937,"phase_name":"align_and_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":159.0,"raw_peak_contact_force":35.87891,"subtask_id":"contact","tcp_end":[0.50412,0.07611,0.05669],"tcp_start":[0.51124,0.0977,0.06696],"tcp_to_object_dist_end":0.03358,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5032,0.00472,0.02415],"object_pos_start":[0.50597,0.0477,0.03888],"object_to_goal_dist_end":0.08625,"object_to_goal_dist_start":0.12784,"object_z_max":0.04056,"peak_contact_force":0.64358,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1466.0,"raw_peak_contact_force":11.24701,"subtask_id":"push","tcp_end":[0.50057,-0.00098,0.0538],"tcp_start":[0.50412,0.07611,0.05669],"tcp_to_object_dist_end":0.0303,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5064,0.00466,0.02415],"object_pos_start":[0.5032,0.00472,0.02415],"object_to_goal_dist_end":0.08637,"object_to_goal_dist_start":0.08625,"object_z_max":0.02415,"peak_contact_force":0.64358,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.64364,"tcp_end":[0.49754,-0.00103,0.16953],"tcp_start":[0.50057,-0.00098,0.0538],"tcp_to_object_dist_end":0.14576,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```