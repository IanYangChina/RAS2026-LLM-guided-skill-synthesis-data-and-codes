## Search State

- **Seed**: 0
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2702 | 0.75 | ❌ rejected |
| 8 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.1932 | 0.72 | ❌ rejected |
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 6 | 0.0756 | 0.00 | ❌ rejected |
| 6 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2860 | 0.77 | ✅ accepted |
| 5 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 7 | -0.0598 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.75 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`
- Frozen object start: [0.5109569349857164, 0.061582937101109625, 0.04]
- Frozen task target: [0.5109569349857164, -0.09841706289889038, 0.04]
- Goal object position: (0.5109569349857164, -0.09841706289889038, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5109569349857164, 0.061582937101109625, 0.04)
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
  frozen_object_start: [0.511, 0.0616, 0.04]
  frozen_task_target: [0.511, -0.0984, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5109569349857164, 0.061582937101109625, 0.04]}
  frozen_targets: {'channel_exit': [0.5109569349857164, -0.09841706289889038, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.774, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.5109569349857164, 0.061582937101109625, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5109569349857164, -0.09841706289889038, 0.04) | final destination targets |
| `fixture` | offset from fixture pose (0.54, 0.0, 0.035) | approach/contact targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.270) — your mutation base

```yaml
skill: peg_channel
phases:
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: insert_2
  type: insert
  generator: impedance_motion
  control: admittance_control
  termination: force_exceeded

```

## Design Metrics

- **Composite score**: 0.270
- **task_score** (E): 0.751
- **fitness_score**: 0.585  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.056
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| insert_1 | 0.00 | 1.00 | 0.1730 |
| approach_1 | 1.00 | 1.00 | 0.1465 |
| push_1 | 0.67 | 1.00 | 0.1582 |
| retract_1 | 0.00 | 1.00 | 0.1081 |
| lift_1 | 0.00 | 1.00 | 0.1524 |
| insert_2 | 0.33 | 1.00 | 0.1144 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| insert_1 | insert | 0.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.075, 0.180) | (0.498, 0.080, 0.040)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.575 | 2.179 |
| approach_1 | approach | 1.00 / step_budget | (0.497, 0.075, 0.180)→(0.497, 0.119, 0.043) | (0.500, 0.080, 0.034)→(0.500, 0.084, 0.033) | 0.161→0.165 | 1.00 / 1.667 | 34.686 | 43.877 |
| push_1 | push | 0.67 / step_budget | (0.497, 0.119, 0.043)→(0.496, -0.039, 0.037) | (0.500, 0.084, 0.033)→(0.507, -0.060, 0.030) | 0.165→0.031 | 1.00 / 3.667 | 29.530 | 167.018 |
| retract_1 | retract | 0.00 / step_budget | (0.496, -0.039, 0.037)→(0.494, 0.002, 0.136) | (0.507, -0.060, 0.030)→(0.504, -0.056, 0.031) | 0.031→0.029 | 1.00 / 1.000 | 0.580 | 84.723 |
| lift_1 | lift | 0.00 / step_budget | (0.494, 0.002, 0.136)→(0.410, -0.044, 0.254) | (0.504, -0.056, 0.031)→(0.502, -0.056, 0.031) | 0.029→0.030 | 1.00 / 1.333 | 0.566 | 3.660 |
| insert_2 | insert | 0.33 / step_budget | (0.410, -0.044, 0.254)→(0.450, -0.062, 0.148) | (0.502, -0.056, 0.031)→(0.502, -0.057, 0.031) | 0.030→0.030 | 1.00 / 1.333 | 3.724 | 3.727 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.808
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.560
- phase_score: 0.607
- phase_breakdown.approach_score: 0.810
- phase_breakdown.push_score: 0.741
- phase_breakdown.contact_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.664
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.873
- **Median Q (composite search score)**: 0.294
- **K-run variance**: 0.0110
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.265


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d6915c31707ac435a9367b840736087e39a7a48adfeb36a4f94b6b3ae57cce94`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `19172182883d287409b73cab43749e937e65f1ca1d4501d52b4a913a881aad36`; realized-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51096,0.06158,0.04]},{"name":"goal","value":[0.51096,-0.09842,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51096,0.06158,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51096,-0.09842,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72414,"average_solve_count":232.0,"average_success_count":232.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.06429,"push_1.push_distance":0.13247,"push_1.push_speed":0.09701,"retract_1.retract_height":0.18361,"retract_1.speed":0.0651},"optimized_scores":{"best_composite_score":0.29383,"best_fitness_score":0.66383,"best_task_score":0.87295},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":330.0,"contact_point_centroid":[0.5417,-0.00801,0.06],"force_p95":72.24059,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":95.04103,"mean_force":51.17709,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49688,-0.00577,0.03699]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54279,-0.05202,0.05999],"force_p95":78.05217,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.8076,"mean_force":71.25333,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49816,-0.05587,0.03661]},{"body_a":"attachment","body_b":"peg","contact_count":694.0,"contact_point_centroid":[0.50268,-0.00042,0.04316],"force_p95":28.5307,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.52287,"mean_force":8.33009,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49665,0.01104,0.03709]},{"body_a":"peg","body_b":"channel_base_body","contact_count":66.0,"contact_point_centroid":[0.50637,-0.10055,0.05762],"force_p95":62.4611,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":64.04742,"mean_force":31.78938,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49779,-0.05349,0.03667]},{"body_a":"attachment","body_b":"peg","contact_count":64.0,"contact_point_centroid":[0.50428,-0.06404,0.0539],"force_p95":8.43001,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.70344,"mean_force":3.73852,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49631,-0.05229,0.03967]},{"body_a":"peg","body_b":"channel_base_body","contact_count":45.0,"contact_point_centroid":[0.50536,-0.1007,0.06078],"force_p95":8.32582,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.69063,"mean_force":5.09645,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49683,-0.05369,0.03831]},{"body_a":"peg","body_b":"channel_base_body","contact_count":574.0,"contact_point_centroid":[0.50596,-0.02145,0.00981],"force_p95":17.1625,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.7394,"mean_force":6.5145,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49665,0.02142,0.03732]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":306.0,"contact_point_centroid":[0.52506,-0.005,0.02182],"force_p95":7.83127,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.10827,"mean_force":2.03701,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49645,0.02134,0.0371]},{"body_a":"peg","body_b":"channel_base_body","contact_count":977.0,"contact_point_centroid":[0.50366,0.06159,0.00935],"force_p95":0.6416,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55484,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49748,0.13519,0.23593]},{"body_a":"peg","body_b":"channel_base_body","contact_count":952.0,"contact_point_centroid":[0.5061,-0.07865,0.00941],"force_p95":0.5537,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.93925,"mean_force":0.54586,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49488,-0.02599,0.08768]},{"body_a":"peg","body_b":"channel_base_body","contact_count":454.0,"contact_point_centroid":[0.50368,0.06157,0.00936],"force_p95":0.64141,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64379,"mean_force":0.54631,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49703,0.08639,0.11069]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49956,0.19884,0.29897]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50618,-0.07802,0.00939],"force_p95":0.55124,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55131,"mean_force":0.54638,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4495,-0.02864,0.1966]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50608,-0.07801,0.00939],"force_p95":0.55125,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55125,"mean_force":0.54638,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.43471,-0.06002,0.1837]}],"total_contact_groups":14},"final_pose_error":0.07666,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50607,-0.07809,0.03383],"final_tcp_position":[0.46591,-0.06998,0.10793],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":95.04103,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50384,0.06159,0.03376],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14178,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.59321,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":996.0,"raw_peak_contact_force":2.17216,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14707,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":454.0,"n_steps_budget":930.0,"object_pos_end":[0.5038,0.06158,0.03376],"object_pos_start":[0.50384,0.06159,0.03376],"object_to_goal_dist_end":0.14177,"object_to_goal_dist_start":0.14178,"object_z_max":0.03377,"peak_contact_force":0.47825,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":454.0,"raw_peak_contact_force":0.64379,"tcp_end":[0.49926,0.09848,0.04185],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03805,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":943.0,"n_steps_budget":1000.0,"object_pos_end":[0.50547,-0.08448,0.03607],"object_pos_start":[0.5038,0.06158,0.03376],"object_to_goal_dist_end":0.00809,"object_to_goal_dist_start":0.14177,"object_z_max":0.03811,"peak_contact_force":88.58851,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1970.0,"raw_peak_contact_force":95.04103,"tcp_end":[0.49815,-0.05584,0.03661],"tcp_start":[0.49926,0.09848,0.04185],"tcp_to_object_dist_end":0.02957,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5062,-0.07808,0.03383],"object_pos_start":[0.50547,-0.08448,0.03607],"object_to_goal_dist_end":0.00896,"object_to_goal_dist_start":0.00809,"object_z_max":0.03734,"peak_contact_force":0.54588,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1063.0,"raw_peak_contact_force":78.8076,"tcp_end":[0.49553,-0.00693,0.13691],"tcp_start":[0.49815,-0.05584,0.03661],"tcp_to_object_dist_end":0.1257,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50612,-0.07798,0.03383],"object_pos_start":[0.5062,-0.07808,0.03383],"object_to_goal_dist_end":0.00892,"object_to_goal_dist_start":0.00896,"object_z_max":0.03383,"peak_contact_force":0.54851,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55131,"tcp_end":[0.4062,-0.05047,0.26088],"tcp_start":[0.49553,-0.00693,0.13691],"tcp_to_object_dist_end":0.24958,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50607,-0.07809,0.03383],"object_pos_start":[0.50612,-0.07798,0.03383],"object_to_goal_dist_end":0.00887,"object_to_goal_dist_start":0.00892,"object_z_max":0.03383,"peak_contact_force":0.54684,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55125,"tcp_end":[0.46591,-0.06998,0.10793],"tcp_start":[0.4062,-0.05047,0.26088],"tcp_to_object_dist_end":0.08468,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `f24211f27d4adabdef509c8ed61621317fdbcaa86fc9ac888f85a717335bb714`; realized-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,0.11604,0.04]},{"name":"goal","value":[0.50095,-0.04396,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.11604,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50095,-0.04396,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58846,"average_solve_count":260.0,"average_success_count":260.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.04752,"push_1.push_distance":0.13792,"push_1.push_speed":0.07635,"retract_1.retract_height":0.1072,"retract_1.speed":0.06308},"optimized_scores":{"best_composite_score":0.13185,"best_fitness_score":0.50185,"best_task_score":0.81881},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":797.0,"contact_point_centroid":[0.50259,0.06317,0.00852],"force_p95":187.26986,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":190.35372,"mean_force":71.69451,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50084,0.09617,0.04326]},{"body_a":"attachment","body_b":"peg","contact_count":800.0,"contact_point_centroid":[0.50488,0.08623,0.04507],"force_p95":186.78661,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":189.82751,"mean_force":75.26732,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50088,0.09602,0.04329]},{"body_a":"attachment","body_b":"peg","contact_count":109.0,"contact_point_centroid":[0.50657,0.13982,0.05102],"force_p95":119.53343,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.43451,"mean_force":83.80714,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49846,0.14657,0.05326]},{"body_a":"peg","body_b":"channel_base_body","contact_count":563.0,"contact_point_centroid":[0.50214,0.1166,0.00925],"force_p95":94.17839,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.99062,"mean_force":15.43742,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49609,0.11288,0.10781]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":181.0,"contact_point_centroid":[0.47383,0.07061,0.03673],"force_p95":63.2384,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":69.64212,"mean_force":21.99025,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50178,0.09632,0.04296]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":160.0,"contact_point_centroid":[0.54194,0.02962,0.06],"force_p95":61.46822,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":67.24195,"mean_force":47.07276,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49696,0.03232,0.03708]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54238,0.00236,0.05999],"force_p95":55.95185,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":56.75142,"mean_force":48.75578,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4975,0.00648,0.03705]},{"body_a":"peg","body_b":"world","contact_count":133.0,"contact_point_centroid":[0.50197,0.12556,-0.00016],"force_p95":19.98008,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.74864,"mean_force":13.36728,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50043,0.15433,0.04503]},{"body_a":"peg","body_b":"world","contact_count":28.0,"contact_point_centroid":[0.50222,0.12719,-0.0003],"force_p95":37.33342,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.90411,"mean_force":28.00895,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49992,0.15488,0.04587]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":100.0,"contact_point_centroid":[0.52507,-9e-05,0.02506],"force_p95":6.01275,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.11854,"mean_force":1.79806,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49705,0.02713,0.03711]},{"body_a":"attachment","body_b":"peg","contact_count":30.0,"contact_point_centroid":[0.50492,-0.00345,0.05679],"force_p95":0.86314,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.12414,"mean_force":0.43499,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49564,0.00835,0.0405]},{"body_a":"peg","body_b":"channel_base_body","contact_count":999.0,"contact_point_centroid":[0.50668,-0.02116,0.00943],"force_p95":0.55183,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.99729,"mean_force":0.54792,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49452,0.02121,0.08885]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50098,0.11602,0.0094],"force_p95":0.60736,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55146,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49749,0.13563,0.23636]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":97.0,"contact_point_centroid":[0.52501,-0.02021,0.05694],"force_p95":0.07294,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.71603,"mean_force":0.03359,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49493,0.02441,0.1072]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.5067,-0.02036,0.00939],"force_p95":0.54893,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54926,"mean_force":0.5464,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45247,-0.00119,0.19541]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50671,-0.02023,0.00939],"force_p95":0.54891,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54893,"mean_force":0.54641,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.43951,-0.04766,0.17713]}],"total_contact_groups":18},"final_pose_error":0.07123,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50674,-0.02031,0.03385],"final_tcp_position":[0.46921,-0.06446,0.10232],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":190.35372,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,0.11601,0.03383],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.58045,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":984.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15182,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.50228,0.12805,0.02979],"object_pos_start":[0.50092,0.11601,0.03383],"object_to_goal_dist_end":0.20832,"object_to_goal_dist_start":0.19611,"object_z_max":0.0342,"peak_contact_force":103.03901,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":700.0,"raw_peak_contact_force":130.43451,"tcp_end":[0.50029,0.1577,0.04359],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50676,-0.02212,0.03672],"object_pos_start":[0.50228,0.12805,0.02979],"object_to_goal_dist_end":0.05837,"object_to_goal_dist_start":0.20832,"object_z_max":0.03715,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2171.0,"raw_peak_contact_force":190.35372,"tcp_end":[0.49751,0.00661,0.03707],"tcp_start":[0.50029,0.1577,0.04359],"tcp_to_object_dist_end":0.03018,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50674,-0.02011,0.03385],"object_pos_start":[0.50676,-0.02212,0.03672],"object_to_goal_dist_end":0.06058,"object_to_goal_dist_start":0.05837,"object_z_max":0.03676,"peak_contact_force":0.54907,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1128.0,"raw_peak_contact_force":56.75142,"tcp_end":[0.49524,0.029,0.14179],"tcp_start":[0.49751,0.00661,0.03707],"tcp_to_object_dist_end":0.11914,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50691,-0.02019,0.03385],"object_pos_start":[0.50674,-0.02011,0.03385],"object_to_goal_dist_end":0.06052,"object_to_goal_dist_start":0.06058,"object_z_max":0.03385,"peak_contact_force":0.54851,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1186.0,"raw_peak_contact_force":0.54926,"tcp_end":[0.41248,-0.03131,0.25354],"tcp_start":[0.49524,0.029,0.14179],"tcp_to_object_dist_end":0.23938,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50674,-0.02031,0.03385],"object_pos_start":[0.50691,-0.02019,0.03385],"object_to_goal_dist_end":0.06038,"object_to_goal_dist_start":0.06052,"object_z_max":0.03385,"peak_contact_force":0.54465,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1133.0,"raw_peak_contact_force":0.54893,"tcp_end":[0.46921,-0.06446,0.10232],"tcp_start":[0.41248,-0.03131,0.25354],"tcp_to_object_dist_end":0.0897,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d098a7862ff18c9bbe982af3446a89a0fa6bcfa8790d7d955f65b2375d67a881`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42601,"average_solve_count":223.0,"average_success_count":223.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.01584,"push_1.push_distance":0.19764,"push_1.push_speed":0.09999,"retract_1.retract_height":0.15934,"retract_1.speed":0.05506},"optimized_scores":{"best_composite_score":0.38489,"best_fitness_score":0.58823,"best_task_score":0.56047},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":323.0,"contact_point_centroid":[0.5347,-0.01197,0.05999],"force_p95":163.27058,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":215.66037,"mean_force":99.06075,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48937,-0.00762,0.03816]},{"body_a":"attachment","body_b":"peg","contact_count":922.0,"contact_point_centroid":[0.49778,0.00628,0.03602],"force_p95":123.8587,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":134.81535,"mean_force":70.86461,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48937,0.01176,0.03807]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.50853,-0.00672,0.00918],"force_p95":90.49579,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":132.9042,"mean_force":43.10028,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48936,0.01608,0.03817]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50364,-0.06913,0.008],"force_p95":36.05772,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":118.61147,"mean_force":5.43209,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49076,-0.03844,0.08337]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":845.0,"contact_point_centroid":[0.5262,-0.00745,0.02751],"force_p95":97.08482,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":109.12991,"mean_force":58.35121,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48945,0.00588,0.03805]},{"body_a":"channel_base_body","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.53505,-0.1,0.06499],"force_p95":91.51038,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":92.15353,"mean_force":85.14355,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49206,-0.0663,0.03775]},{"body_a":"attachment","body_b":"peg","contact_count":135.0,"contact_point_centroid":[0.50187,-0.06406,0.0395],"force_p95":64.85953,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":84.26375,"mean_force":29.86461,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49123,-0.06372,0.04451]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":124.0,"contact_point_centroid":[0.52518,-0.05991,0.02217],"force_p95":52.73423,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":64.09414,"mean_force":16.32131,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4913,-0.06404,0.04415]},{"body_a":"channel_base_body","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.53576,-0.1,0.065],"force_p95":39.96636,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":40.42584,"mean_force":35.83096,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49284,-0.06835,0.03793]},{"body_a":"peg","body_b":"link7","contact_count":368.0,"contact_point_centroid":[0.52008,0.0093,0.06777],"force_p95":24.83876,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.42224,"mean_force":12.17127,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48938,0.03416,0.03791]},{"body_a":"peg","body_b":"world","contact_count":34.0,"contact_point_centroid":[0.51015,-0.06935,-0.00066],"force_p95":17.95114,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.69091,"mean_force":2.04527,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49172,-0.06437,0.03785]},{"body_a":"peg","body_b":"channel_base_body","contact_count":74.0,"contact_point_centroid":[0.49339,-0.0713,0.00804],"force_p95":0.68339,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.0813,"mean_force":0.85667,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.41251,-0.05188,0.24129]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49516,-0.07119,0.00809],"force_p95":0.6845,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.88039,"mean_force":0.7513,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45037,-0.03381,0.18637]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.47499,-0.07129,0.02408],"force_p95":9.60909,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.62839,"mean_force":9.43538,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.41387,-0.05247,0.23512]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":37.0,"contact_point_centroid":[0.47498,-0.07474,0.02488],"force_p95":9.28785,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.45126,"mean_force":4.24016,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44542,-0.03597,0.19375]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.49527,0.06395,0.00938],"force_p95":0.55699,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55424,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49748,0.13493,0.23568]}],"total_contact_groups":19},"final_pose_error":0.21478,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49295,-0.07132,0.02416],"final_tcp_position":[0.41394,-0.0525,0.23485],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":215.66037,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49482,0.06382,0.03401],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14404,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.55002,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1001.0,"raw_peak_contact_force":2.44546,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14649,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":447.0,"n_steps_budget":930.0,"object_pos_end":[0.49519,0.06359,0.03403],"object_pos_start":[0.49482,0.06382,0.03401],"object_to_goal_dist_end":0.14379,"object_to_goal_dist_start":0.14404,"object_z_max":0.03403,"peak_contact_force":0.54085,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":447.0,"raw_peak_contact_force":0.55403,"tcp_end":[0.4911,0.10042,0.04259],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03803,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50917,-0.07329,0.01663],"object_pos_start":[0.49519,0.06359,0.03403],"object_to_goal_dist_end":0.02599,"object_to_goal_dist_start":0.14379,"object_z_max":0.0399,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3468.0,"raw_peak_contact_force":215.66037,"tcp_end":[0.49282,-0.06829,0.03792],"tcp_start":[0.4911,0.10042,0.04259],"tcp_to_object_dist_end":0.02731,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49918,-0.0712,0.02415],"object_pos_start":[0.50917,-0.07329,0.01663],"object_to_goal_dist_end":0.01814,"object_to_goal_dist_start":0.02599,"object_z_max":0.02914,"peak_contact_force":0.64358,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1285.0,"raw_peak_contact_force":118.61147,"tcp_end":[0.49209,-0.01648,0.12979],"tcp_start":[0.49282,-0.06829,0.03792],"tcp_to_object_dist_end":0.11918,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49365,-0.07129,0.02413],"object_pos_start":[0.49918,-0.0712,0.02415],"object_to_goal_dist_end":0.01918,"object_to_goal_dist_start":0.01814,"object_z_max":0.02567,"peak_contact_force":0.60162,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1037.0,"raw_peak_contact_force":9.88039,"tcp_end":[0.41146,-0.05128,0.24751],"tcp_start":[0.49209,-0.01648,0.12979],"tcp_to_object_dist_end":0.23886,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":74.0,"n_steps_budget":1000.0,"object_pos_end":[0.49295,-0.07132,0.02416],"object_pos_start":[0.49365,-0.07129,0.02413],"object_to_goal_dist_end":0.01939,"object_to_goal_dist_start":0.01918,"object_z_max":0.02414,"peak_contact_force":10.0813,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":76.0,"raw_peak_contact_force":10.0813,"tcp_end":[0.41394,-0.0525,0.23485],"tcp_start":[0.41146,-0.05128,0.24751],"tcp_to_object_dist_end":0.22581,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```