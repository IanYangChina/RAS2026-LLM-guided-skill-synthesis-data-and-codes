## Search State

- **Seed**: 1
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1494 | 0.30 | ✅ accepted |
| 2 | approach → descend → push → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 6 | -0.3041 | 0.00 | ❌ rejected |
| 1 | approach → approach → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0792 | 0.11 | ❌ rejected |
| 0 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1472 | 0.30 | ✅ accepted |

**Proposal policy**: task_score is 0.30 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`
- Frozen object start: [0.5009457299760205, 0.11603709570607482, 0.04]
- Frozen task target: [0.5009457299760205, -0.04396290429392519, 0.04]
- Goal object position: (0.5009457299760205, -0.04396290429392519, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5009457299760205, 0.11603709570607482, 0.04)
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
  frozen_object_start: [0.5009, 0.116, 0.04]
  frozen_task_target: [0.5009, -0.044, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5009457299760205, 0.11603709570607482, 0.04]}
  frozen_targets: {'channel_exit': [0.5009457299760205, -0.04396290429392519, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a

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
| `object` | offset from object initial position (0.5009457299760205, 0.11603709570607482, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5009457299760205, -0.04396290429392519, 0.04) | final destination targets |
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

## Current Skill (Q=0.149) — your mutation base

```yaml
skill: peg_channel
phases:
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
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
- id: align_2
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01

```

## Design Metrics

- **Composite score**: 0.149
- **task_score** (E): 0.303
- **fitness_score**: 0.359  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| rotate_1 | 1.00 | 1.00 | 0.1730 |
| align_1 | 1.00 | 1.00 | 0.1462 |
| push_1 | 0.00 | 1.00 | 0.1691 |
| align_2 | 1.00 | 1.00 | 0.0395 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| rotate_1 | rotate | 1.00 / time_limit | (0.500, 0.200, 0.300)→(0.497, 0.075, 0.180) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.667 | 34.709 | 43.847 |
| align_1 | align | 1.00 / step_budget | (0.497, 0.075, 0.180)→(0.494, 0.118, 0.043) | (0.497, 0.080, 0.034)→(0.497, 0.084, 0.033) | 0.160→0.164 | 1.00 / 3.000 | 40.632 | 209.865 |
| push_1 | push | 0.00 / step_budget | (0.494, 0.118, 0.043)→(0.495, -0.051, 0.038) | (0.497, 0.084, 0.033)→(0.503, -0.023, 0.022) | 0.164→0.069 | 1.00 / 4.000 | 169.613 | 335.661 |
| align_2 | align | 1.00 / step_budget | (0.495, -0.051, 0.038)→(0.500, -0.013, 0.038) | (0.503, -0.023, 0.022)→(0.492, -0.006, 0.028) | 0.069→0.081 | 1.00 / 1.000 | 0.560 | 2.857 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.844
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.617
- phase_score: 0.461
- phase_breakdown.push_score: 0.756
- phase_breakdown.contact_score: 0.000
- phase_breakdown.approach_score: 0.035

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.523
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.617
- **Median Q (composite search score)**: 0.223
- **K-run variance**: 0.0296
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.330


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a904e23429ae963dd2788b3e8d0575d9ce341e1daddfe013fbb1224c3e0c850e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `6bee39a4c127c6d39ee1365e3969a50bb09484f7e2580b1a3dc4d8c4ae20213b`; realized-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,0.11604,0.04]},{"name":"goal","value":[0.50095,-0.04396,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.11604,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50095,-0.04396,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91111,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00402,"align_2.lateral_offset_x":-0.00338,"push_1.push_distance":0.19974},"optimized_scores":{"best_composite_score":-0.08851,"best_fitness_score":0.12149,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":612.0,"contact_point_centroid":[0.54313,0.03297,0.05998],"force_p95":181.65148,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":221.82174,"mean_force":142.9968,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49828,0.03558,0.0368]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49881,0.08759,0.00785],"force_p95":186.25011,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":193.70876,"mean_force":88.94625,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50309,0.08093,0.04549]},{"body_a":"attachment","body_b":"peg","contact_count":704.0,"contact_point_centroid":[0.50842,0.1044,0.04972],"force_p95":188.72749,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":193.25437,"mean_force":134.93713,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50524,0.10804,0.04848]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":144.0,"contact_point_centroid":[0.52501,0.07324,0.06],"force_p95":151.88969,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":184.3155,"mean_force":81.08703,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50709,0.07322,0.04898]},{"body_a":"attachment","body_b":"peg","contact_count":109.0,"contact_point_centroid":[0.50657,0.13982,0.05102],"force_p95":119.53343,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.43451,"mean_force":83.80714,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49846,0.14657,0.05326]},{"body_a":"peg","body_b":"channel_base_body","contact_count":563.0,"contact_point_centroid":[0.50214,0.1166,0.00925],"force_p95":94.17839,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.99062,"mean_force":15.43742,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49609,0.11288,0.10781]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":503.0,"contact_point_centroid":[0.4737,0.07794,0.02683],"force_p95":78.05442,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":104.74472,"mean_force":37.5033,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50447,0.06075,0.04594]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":68.0,"contact_point_centroid":[0.54174,-0.00027,0.06],"force_p95":57.17842,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":62.96924,"mean_force":44.43147,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49684,0.004,0.03713]},{"body_a":"peg","body_b":"world","contact_count":121.0,"contact_point_centroid":[0.50193,0.12557,-0.00018],"force_p95":20.30006,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.74864,"mean_force":13.84534,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5003,0.15491,0.04486]},{"body_a":"attachment","body_b":"peg","contact_count":74.0,"contact_point_centroid":[0.4972,0.07697,0.0374],"force_p95":11.94898,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.68938,"mean_force":2.62698,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.4989,0.06534,0.03662]},{"body_a":"peg","body_b":"world","contact_count":28.0,"contact_point_centroid":[0.50222,0.12719,-0.0003],"force_p95":37.33342,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.90411,"mean_force":28.00895,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49992,0.15488,0.04587]},{"body_a":"peg","body_b":"channel_base_body","contact_count":681.0,"contact_point_centroid":[0.49389,0.08602,0.00943],"force_p95":1.24509,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.43752,"mean_force":0.79151,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49826,0.034,0.03682]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":230.0,"contact_point_centroid":[0.47493,0.0852,0.05153],"force_p95":0.49595,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.77719,"mean_force":0.17274,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49831,0.0362,0.03681]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50098,0.11602,0.0094],"force_p95":0.60736,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55146,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49749,0.13563,0.23636]}],"total_contact_groups":14},"final_pose_error":0.02342,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49354,0.12086,0.03519],"final_tcp_position":[0.49938,0.09157,0.03633],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":221.82174,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,0.11601,0.03383],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":103.03901,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":700.0,"raw_peak_contact_force":130.43451,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15182,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.50228,0.12805,0.02979],"object_pos_start":[0.50092,0.11601,0.03383],"object_to_goal_dist_end":0.20832,"object_to_goal_dist_start":0.19611,"object_z_max":0.0342,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2540.0,"raw_peak_contact_force":193.70876,"tcp_end":[0.50029,0.1577,0.04359],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49305,0.07397,0.03378],"object_pos_start":[0.50228,0.12805,0.02979],"object_to_goal_dist_end":0.15425,"object_to_goal_dist_start":0.20832,"object_z_max":0.03445,"peak_contact_force":1.26118,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1597.0,"raw_peak_contact_force":221.82174,"tcp_end":[0.49702,-0.00998,0.03707],"tcp_start":[0.50029,0.1577,0.04359],"tcp_to_object_dist_end":0.08411,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":722.0,"n_steps_budget":780.0,"object_pos_end":[0.49354,0.12086,0.03519],"object_pos_start":[0.49305,0.07397,0.03378],"object_to_goal_dist_end":0.20102,"object_to_goal_dist_start":0.15425,"object_z_max":0.0375,"peak_contact_force":0.58045,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":984.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.49938,0.09157,0.03633],"tcp_start":[0.49702,-0.00998,0.03707],"tcp_to_object_dist_end":0.02989,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8416ac3bebb4dbec2abbf751596843a33db171fd8d70765023f3b940d846bd0c`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75397,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":6e-05,"align_2.lateral_offset_x":0.00982,"push_1.push_distance":0.19983},"optimized_scores":{"best_composite_score":0.31332,"best_fitness_score":0.52332,"best_task_score":0.61729},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":315.0,"contact_point_centroid":[0.52507,-0.06336,0.05997],"force_p95":349.53584,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":413.07813,"mean_force":224.57372,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50051,-0.06315,0.03738]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":390.0,"contact_point_centroid":[0.54518,-0.06006,0.05993],"force_p95":299.24422,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":363.87883,"mean_force":244.31351,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50014,-0.06349,0.03723]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":320.0,"contact_point_centroid":[0.5345,-0.01039,0.05999],"force_p95":163.92289,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":231.35749,"mean_force":101.43498,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48915,-0.00587,0.0382]},{"body_a":"channel_base_body","body_b":"link7","contact_count":105.0,"contact_point_centroid":[0.53995,-0.10001,0.06496],"force_p95":179.30894,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":212.00164,"mean_force":113.99148,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49735,-0.06578,0.03688]},{"body_a":"attachment","body_b":"peg","contact_count":428.0,"contact_point_centroid":[0.50116,-0.07101,0.03747],"force_p95":102.00557,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":155.63084,"mean_force":60.49255,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.4996,-0.06391,0.03729]},{"body_a":"attachment","body_b":"peg","contact_count":914.0,"contact_point_centroid":[0.49773,0.00656,0.03581],"force_p95":119.75214,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":135.64184,"mean_force":70.49044,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48928,0.0118,0.03809]},{"body_a":"peg","body_b":"channel_base_body","contact_count":455.0,"contact_point_centroid":[0.49522,-0.06779,0.00671],"force_p95":104.7611,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":131.95849,"mean_force":50.1364,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49951,-0.06399,0.03725]},{"body_a":"peg","body_b":"channel_base_body","contact_count":974.0,"contact_point_centroid":[0.50841,-0.00557,0.0091],"force_p95":90.46195,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":125.68129,"mean_force":42.7604,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48928,0.01652,0.03819]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":861.0,"contact_point_centroid":[0.52617,-0.0053,0.02729],"force_p95":97.41828,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":103.62275,"mean_force":57.0482,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48933,0.00745,0.03807]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":41.0,"contact_point_centroid":[0.5252,-0.05989,0.01632],"force_p95":49.85018,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":52.58854,"mean_force":35.41516,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49471,-0.06771,0.03756]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":354.0,"contact_point_centroid":[0.47463,-0.08094,0.02323],"force_p95":31.70352,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.31126,"mean_force":24.78206,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50037,-0.06332,0.0373]},{"body_a":"peg","body_b":"link7","contact_count":368.0,"contact_point_centroid":[0.52011,0.01136,0.06772],"force_p95":25.39244,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.2712,"mean_force":12.48306,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48925,0.03609,0.03792]},{"body_a":"peg","body_b":"world","contact_count":54.0,"contact_point_centroid":[0.50938,-0.0647,-0.00078],"force_p95":1.89381,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.54032,"mean_force":0.83635,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49185,-0.06153,0.0379]},{"body_a":"peg","body_b":"world","contact_count":99.0,"contact_point_centroid":[0.50461,-0.0669,-0.00127],"force_p95":12.09503,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.75869,"mean_force":2.07914,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49645,-0.06636,0.03709]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.49527,0.06395,0.00938],"force_p95":0.55699,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55424,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49748,0.13493,0.23568]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49942,0.19831,0.29814]}],"total_contact_groups":17},"final_pose_error":0.03981,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4922,-0.07123,0.02448],"final_tcp_position":[0.50015,-0.06266,0.03861],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":413.07813,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49482,0.06382,0.03401],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14404,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54085,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":447.0,"raw_peak_contact_force":0.55403,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14649,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":447.0,"n_steps_budget":930.0,"object_pos_end":[0.49519,0.06359,0.03403],"object_pos_start":[0.49482,0.06382,0.03401],"object_to_goal_dist_end":0.14379,"object_to_goal_dist_start":0.14404,"object_z_max":0.03403,"peak_contact_force":95.85564,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3491.0,"raw_peak_contact_force":231.35749,"tcp_end":[0.4911,0.10042,0.04259],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03803,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50784,-0.07025,0.01681],"object_pos_start":[0.49519,0.06359,0.03403],"object_to_goal_dist_end":0.02635,"object_to_goal_dist_start":0.14379,"object_z_max":0.0399,"peak_contact_force":256.26262,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2187.0,"raw_peak_contact_force":413.07813,"tcp_end":[0.49336,-0.06787,0.03795],"tcp_start":[0.4911,0.10042,0.04259],"tcp_to_object_dist_end":0.02574,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.4922,-0.07123,0.02448],"object_pos_start":[0.50784,-0.07025,0.01681],"object_to_goal_dist_end":0.01946,"object_to_goal_dist_start":0.02635,"object_z_max":0.02446,"peak_contact_force":0.55002,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1001.0,"raw_peak_contact_force":2.44546,"tcp_end":[0.50015,-0.06266,0.03861],"tcp_start":[0.49336,-0.06787,0.03795],"tcp_to_object_dist_end":0.01835,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0188121de1b8142d5ff7a7406b62c43adf6da5520b986a997e46ef53b7d11bf9`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75397,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00792,"align_2.lateral_offset_x":0.0027,"push_1.push_distance":0.19093},"optimized_scores":{"best_composite_score":0.22333,"best_fitness_score":0.43333,"best_task_score":0.29168},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":365.0,"contact_point_centroid":[0.52506,-0.06893,0.05997],"force_p95":312.99034,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":372.08262,"mean_force":220.99034,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50089,-0.06878,0.03744]},{"body_a":"channel_base_body","body_b":"link7","contact_count":447.0,"contact_point_centroid":[0.54326,-0.10001,0.06494],"force_p95":279.59509,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":286.98941,"mean_force":224.31152,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50053,-0.0694,0.03747]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":306.0,"contact_point_centroid":[0.53435,-0.00837,0.05999],"force_p95":160.74736,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":204.5287,"mean_force":99.13652,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48899,-0.00386,0.03817]},{"body_a":"peg","body_b":"channel_base_body","contact_count":968.0,"contact_point_centroid":[0.50776,-0.01015,0.0088],"force_p95":89.92863,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":132.42793,"mean_force":43.3523,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48934,0.01039,0.0382]},{"body_a":"attachment","body_b":"peg","contact_count":883.0,"contact_point_centroid":[0.49793,-0.0011,0.03503],"force_p95":120.6848,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.82716,"mean_force":71.75743,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48944,0.00352,0.0381]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":827.0,"contact_point_centroid":[0.52614,-0.00784,0.02405],"force_p95":97.37745,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":108.048,"mean_force":56.59812,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48937,0.00203,0.03807]},{"body_a":"attachment","body_b":"peg","contact_count":431.0,"contact_point_centroid":[0.50107,-0.07378,0.03749],"force_p95":83.73605,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":105.26705,"mean_force":39.48636,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50041,-0.06954,0.0375]},{"body_a":"peg","body_b":"channel_base_body","contact_count":465.0,"contact_point_centroid":[0.4943,-0.07627,0.0065],"force_p95":79.03121,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.81346,"mean_force":37.88575,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50043,-0.06954,0.03748]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":362.0,"contact_point_centroid":[0.47426,-0.06195,0.02254],"force_p95":39.88978,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.05426,"mean_force":23.61174,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50089,-0.06877,0.03745]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":10.0,"contact_point_centroid":[0.52503,-0.04741,0.01618],"force_p95":34.51599,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.90594,"mean_force":26.8644,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49618,-0.07487,0.03838]},{"body_a":"peg","body_b":"world","contact_count":99.0,"contact_point_centroid":[0.50842,-0.07016,-0.00079],"force_p95":4.69933,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.07229,"mean_force":0.88604,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49316,-0.06552,0.03796]},{"body_a":"peg","body_b":"link7","contact_count":263.0,"contact_point_centroid":[0.51816,0.00819,0.0686],"force_p95":20.95147,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.27025,"mean_force":10.10048,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48898,0.03414,0.03796]},{"body_a":"peg","body_b":"world","contact_count":86.0,"contact_point_centroid":[0.50516,-0.07391,-0.00112],"force_p95":5.10491,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.61807,"mean_force":0.83964,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49839,-0.07263,0.03774]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.49432,0.05896,0.00937],"force_p95":0.55417,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56118,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49747,0.13481,0.23556]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49933,0.1979,0.29752]},{"body_a":"peg","body_b":"channel_base_body","contact_count":443.0,"contact_point_centroid":[0.49394,0.0588,0.0094],"force_p95":0.55052,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55295,"mean_force":0.54554,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49272,0.08527,0.11112]}],"total_contact_groups":16},"final_pose_error":0.04253,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49164,-0.06655,0.0232],"final_tcp_position":[0.50043,-0.06808,0.03841],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":372.08262,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49409,0.05914,0.03393],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.1394,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54579,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":443.0,"raw_peak_contact_force":0.55295,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14702,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":443.0,"n_steps_budget":930.0,"object_pos_end":[0.49439,0.05889,0.034],"object_pos_start":[0.49409,0.05914,0.03393],"object_to_goal_dist_end":0.13914,"object_to_goal_dist_start":0.1394,"object_z_max":0.034,"peak_contact_force":26.03927,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3346.0,"raw_peak_contact_force":204.5287,"tcp_end":[0.49044,0.0962,0.04256],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03848,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50681,-0.07224,0.01643],"object_pos_start":[0.49439,0.05889,0.034],"object_to_goal_dist_end":0.02573,"object_to_goal_dist_start":0.13914,"object_z_max":0.03998,"peak_contact_force":251.31656,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2166.0,"raw_peak_contact_force":372.08262,"tcp_end":[0.49552,-0.07479,0.03844],"tcp_start":[0.49044,0.0962,0.04256],"tcp_to_object_dist_end":0.02487,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":465.0,"n_steps_budget":600.0,"object_pos_end":[0.49164,-0.06655,0.0232],"object_pos_start":[0.50681,-0.07224,0.01643],"object_to_goal_dist_end":0.02309,"object_to_goal_dist_start":0.02573,"object_z_max":0.02375,"peak_contact_force":0.54973,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1006.0,"raw_peak_contact_force":4.20518,"tcp_end":[0.50043,-0.06808,0.03841],"tcp_start":[0.49552,-0.07479,0.03844],"tcp_to_object_dist_end":0.01764,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```