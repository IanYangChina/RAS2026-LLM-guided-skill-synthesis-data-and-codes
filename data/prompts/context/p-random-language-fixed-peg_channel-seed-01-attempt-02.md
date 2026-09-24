## Search State

- **Seed**: 1
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1153 | 0.34 | ❌ rejected |
| 1 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1706 | 0.42 | ✅ accepted |
| 0 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 2 | 0.1472 | 0.30 | ✅ accepted |

**Proposal policy**: task_score is 0.34 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.115) — your mutation base

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

- **Composite score**: 0.115
- **task_score** (E): 0.343
- **fitness_score**: 0.325  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| rotate_1 | 1.00 | 1.00 | 0.1730 |
| align_1 | 1.00 | 1.00 | 0.1462 |
| push_1 | 0.67 | 1.00 | 0.1361 |
| align_2 | 1.00 | 1.00 | 0.0056 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| rotate_1 | rotate | 1.00 / time_limit | (0.500, 0.200, 0.300)→(0.497, 0.075, 0.180) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.560 | 2.857 |
| align_1 | align | 1.00 / step_budget | (0.497, 0.075, 0.180)→(0.494, 0.118, 0.043) | (0.497, 0.080, 0.034)→(0.497, 0.084, 0.033) | 0.160→0.164 | 1.00 / 1.667 | 34.709 | 43.847 |
| push_1 | push | 0.67 / step_budget | (0.494, 0.118, 0.043)→(0.497, -0.018, 0.037) | (0.497, 0.084, 0.033)→(0.503, -0.035, 0.031) | 0.164→0.053 | 1.00 / 3.333 | 2138.487 | 189.492 |
| align_2 | align | 1.00 / step_budget | (0.497, -0.018, 0.037)→(0.499, -0.013, 0.037) | (0.503, -0.035, 0.031)→(0.497, -0.034, 0.031) | 0.053→0.052 | 1.00 / 3.667 | 109.715 | 198.998 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.771
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.290
- phase_score: 0.530
- phase_breakdown.push_score: 0.873
- phase_breakdown.contact_score: 0.000
- phase_breakdown.approach_score: 0.034

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.434
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.392
- **Median Q (composite search score)**: 0.135
- **K-run variance**: 0.0096
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.221


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.54464,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00649,"align_2.lateral_offset_x":0.00807,"push_1.push_distance":0.06452},"optimized_scores":{"best_composite_score":-0.01316,"best_fitness_score":0.19684,"best_task_score":0.39231},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":478.0,"contact_point_centroid":[0.50279,0.09987,0.00756],"force_p95":196.03982,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":200.46324,"mean_force":118.66969,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50387,0.12673,0.047]},{"body_a":"attachment","body_b":"peg","contact_count":502.0,"contact_point_centroid":[0.50727,0.1161,0.0474],"force_p95":195.46532,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":199.95474,"mean_force":124.43093,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5038,0.12479,0.04675]},{"body_a":"attachment","body_b":"peg","contact_count":109.0,"contact_point_centroid":[0.50657,0.13982,0.05102],"force_p95":119.53343,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.43451,"mean_force":83.80714,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49846,0.14657,0.05326]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":42.0,"contact_point_centroid":[0.52502,0.10079,0.05999],"force_p95":112.45132,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":121.40873,"mean_force":89.27815,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50675,0.10077,0.04781]},{"body_a":"peg","body_b":"channel_base_body","contact_count":563.0,"contact_point_centroid":[0.50214,0.1166,0.00925],"force_p95":94.17839,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.99062,"mean_force":15.43742,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49609,0.11288,0.10781]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":189.0,"contact_point_centroid":[0.47309,0.07158,0.03951],"force_p95":99.4154,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":104.89084,"mean_force":40.74243,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50412,0.09328,0.04443]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":105.0,"contact_point_centroid":[0.54191,0.07226,0.05993],"force_p95":91.56945,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":91.73939,"mean_force":85.64435,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49698,0.07281,0.03666]},{"body_a":"peg","body_b":"world","contact_count":139.0,"contact_point_centroid":[0.502,0.12548,-0.00017],"force_p95":18.82523,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.74864,"mean_force":13.94932,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50044,0.15422,0.04493]},{"body_a":"peg","body_b":"world","contact_count":28.0,"contact_point_centroid":[0.50222,0.12719,-0.0003],"force_p95":37.33342,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.90411,"mean_force":28.00895,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49992,0.15488,0.04587]},{"body_a":"peg","body_b":"channel_base_body","contact_count":112.0,"contact_point_centroid":[0.49138,0.02626,0.00998],"force_p95":0.74331,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.51779,"mean_force":0.48919,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49702,0.07279,0.03667]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50098,0.11602,0.0094],"force_p95":0.60736,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55146,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49749,0.13563,0.23636]},{"body_a":"attachment","body_b":"peg","contact_count":97.0,"contact_point_centroid":[0.49577,0.06089,0.03734],"force_p95":0.56365,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.64941,"mean_force":0.29117,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49703,0.0728,0.03668]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":33.0,"contact_point_centroid":[0.47498,0.04215,0.06],"force_p95":0.23745,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23825,"mean_force":0.08302,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49702,0.07275,0.03663]}],"total_contact_groups":13},"final_pose_error":0.01039,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49314,0.04383,0.03507],"final_tcp_position":[0.49645,0.07362,0.03673],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":200.46324,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,0.11601,0.03383],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.58045,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":984.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15182,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.50228,0.12805,0.02979],"object_pos_start":[0.50092,0.11601,0.03383],"object_to_goal_dist_end":0.20832,"object_to_goal_dist_start":0.19611,"object_z_max":0.0342,"peak_contact_force":103.03901,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":700.0,"raw_peak_contact_force":130.43451,"tcp_end":[0.50029,0.1577,0.04359],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":529.0,"n_steps_budget":600.0,"object_pos_end":[0.49317,0.04347,0.0363],"object_pos_start":[0.50228,0.12805,0.02979],"object_to_goal_dist_end":0.12371,"object_to_goal_dist_start":0.20832,"object_z_max":0.03645,"peak_contact_force":0.90274,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1350.0,"raw_peak_contact_force":200.46324,"tcp_end":[0.49795,0.07283,0.03714],"tcp_start":[0.50029,0.1577,0.04359],"tcp_to_object_dist_end":0.02976,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":113.0,"n_steps_budget":600.0,"object_pos_end":[0.49314,0.04383,0.03507],"object_pos_start":[0.49317,0.04347,0.0363],"object_to_goal_dist_end":0.12412,"object_to_goal_dist_start":0.12371,"object_z_max":0.0363,"peak_contact_force":0.98307,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":347.0,"raw_peak_contact_force":91.73939,"tcp_end":[0.49645,0.07362,0.03673],"tcp_start":[0.49795,0.07283,0.03714],"tcp_to_object_dist_end":0.03002,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.62698,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00066,"align_2.lateral_offset_x":0.00028,"push_1.push_distance":0.14385},"optimized_scores":{"best_composite_score":0.13467,"best_fitness_score":0.34467,"best_task_score":0.34659},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":181.0,"contact_point_centroid":[0.54456,-0.04378,0.05999],"force_p95":157.31654,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":197.95667,"mean_force":92.52556,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49997,-0.04801,0.03658]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":146.0,"contact_point_centroid":[0.52507,-0.04724,0.05997],"force_p95":178.37984,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":192.95565,"mean_force":146.45763,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50081,-0.04704,0.03654]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":327.0,"contact_point_centroid":[0.53787,-0.00712,0.06],"force_p95":113.33549,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":156.95298,"mean_force":69.75323,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49285,-0.00434,0.03745]},{"body_a":"attachment","body_b":"peg","contact_count":924.0,"contact_point_centroid":[0.49918,0.00521,0.03598],"force_p95":109.23448,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":148.12399,"mean_force":64.66315,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49182,0.0129,0.03761]},{"body_a":"peg","body_b":"channel_base_body","contact_count":970.0,"contact_point_centroid":[0.50789,-0.01322,0.00965],"force_p95":66.23914,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":100.23373,"mean_force":36.70102,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49171,0.01687,0.03774]},{"body_a":"peg","body_b":"channel_base_body","contact_count":137.0,"contact_point_centroid":[0.50918,-0.1008,0.05052],"force_p95":63.30351,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":74.92662,"mean_force":48.73122,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49592,-0.0445,0.03695]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":844.0,"contact_point_centroid":[0.52587,-0.0118,0.02748],"force_p95":68.27093,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":74.74661,"mean_force":45.21588,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49212,0.00682,0.03755]},{"body_a":"attachment","body_b":"peg","contact_count":32.0,"contact_point_centroid":[0.50292,-0.06017,0.03603],"force_p95":73.3121,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":74.25396,"mean_force":39.15562,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49748,-0.05091,0.03674]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":48.0,"contact_point_centroid":[0.52645,-0.07742,0.03485],"force_p95":46.95301,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":61.80501,"mean_force":19.92361,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49784,-0.05051,0.0367]},{"body_a":"peg","body_b":"channel_base_body","contact_count":126.0,"contact_point_centroid":[0.50621,-0.1003,0.03421],"force_p95":35.23978,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.12881,"mean_force":5.94677,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49994,-0.04823,0.03655]},{"body_a":"peg","body_b":"channel_base_body","contact_count":199.0,"contact_point_centroid":[0.50482,-0.07915,0.00957],"force_p95":14.48389,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.2715,"mean_force":2.17614,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50027,-0.04772,0.03656]},{"body_a":"peg","body_b":"link7","contact_count":299.0,"contact_point_centroid":[0.52005,0.01314,0.068],"force_p95":20.56289,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.22861,"mean_force":9.05042,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49017,0.03829,0.03781]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.49527,0.06395,0.00938],"force_p95":0.55699,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55424,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49748,0.13493,0.23568]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49942,0.19831,0.29814]},{"body_a":"peg","body_b":"channel_base_body","contact_count":447.0,"contact_point_centroid":[0.49494,0.06368,0.0094],"force_p95":0.55078,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55403,"mean_force":0.54515,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49304,0.08732,0.11116]}],"total_contact_groups":15},"final_pose_error":0.01428,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50526,-0.08193,0.03378],"final_tcp_position":[0.50066,-0.04691,0.03667],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":197.95667,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49482,0.06382,0.03401],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14404,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.55002,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":1001.0,"raw_peak_contact_force":2.44546,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14649,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":447.0,"n_steps_budget":930.0,"object_pos_end":[0.49519,0.06359,0.03403],"object_pos_start":[0.49482,0.06382,0.03401],"object_to_goal_dist_end":0.14379,"object_to_goal_dist_start":0.14404,"object_z_max":0.03403,"peak_contact_force":0.54085,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":447.0,"raw_peak_contact_force":0.55403,"tcp_end":[0.4911,0.10042,0.04259],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03803,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50974,-0.07621,0.0393],"object_pos_start":[0.49519,0.06359,0.03403],"object_to_goal_dist_end":0.01048,"object_to_goal_dist_start":0.14379,"object_z_max":0.04026,"peak_contact_force":124.41891,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3501.0,"raw_peak_contact_force":156.95298,"tcp_end":[0.49719,-0.051,0.03678],"tcp_start":[0.4911,0.10042,0.04259],"tcp_to_object_dist_end":0.02827,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":223.0,"n_steps_budget":600.0,"object_pos_end":[0.50526,-0.08193,0.03378],"object_pos_start":[0.50974,-0.07621,0.0393],"object_to_goal_dist_end":0.00837,"object_to_goal_dist_start":0.01048,"object_z_max":0.0393,"peak_contact_force":129.78657,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":732.0,"raw_peak_contact_force":197.95667,"tcp_end":[0.50066,-0.04691,0.03667],"tcp_start":[0.49719,-0.051,0.03678],"tcp_to_object_dist_end":0.03544,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75397,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.0088,"align_2.lateral_offset_x":0.00242,"push_1.push_distance":0.18666},"optimized_scores":{"best_composite_score":0.22428,"best_fitness_score":0.43428,"best_task_score":0.29017},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":368.0,"contact_point_centroid":[0.52505,-0.06769,0.05997],"force_p95":246.9539,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":307.29814,"mean_force":213.06789,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50078,-0.06752,0.03734]},{"body_a":"channel_base_body","body_b":"link7","contact_count":404.0,"contact_point_centroid":[0.54316,-0.10001,0.06495],"force_p95":265.65946,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":275.18801,"mean_force":205.48512,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50038,-0.0682,0.03743]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":316.0,"contact_point_centroid":[0.53439,-0.00769,0.05999],"force_p95":162.52179,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":211.06082,"mean_force":99.62535,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48903,-0.00318,0.03818]},{"body_a":"attachment","body_b":"peg","contact_count":885.0,"contact_point_centroid":[0.49795,-0.00099,0.03501],"force_p95":119.29778,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":135.14211,"mean_force":72.07101,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48947,0.00363,0.03811]},{"body_a":"peg","body_b":"channel_base_body","contact_count":460.0,"contact_point_centroid":[0.49552,-0.07702,0.00643],"force_p95":109.01688,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":126.44967,"mean_force":54.54474,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50031,-0.06843,0.03741]},{"body_a":"attachment","body_b":"peg","contact_count":443.0,"contact_point_centroid":[0.50217,-0.07444,0.03707],"force_p95":108.9793,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":125.4184,"mean_force":58.00005,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.5003,-0.06844,0.03741]},{"body_a":"peg","body_b":"channel_base_body","contact_count":970.0,"contact_point_centroid":[0.50777,-0.00976,0.00882],"force_p95":92.75892,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":123.89461,"mean_force":43.13647,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48937,0.01046,0.0382]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":39.0,"contact_point_centroid":[0.54582,-0.06361,0.05999],"force_p95":106.7136,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":123.87221,"mean_force":78.15873,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50037,-0.06691,0.03817]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":830.0,"contact_point_centroid":[0.52614,-0.00974,0.02411],"force_p95":98.20572,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":106.4616,"mean_force":57.13638,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48948,0.00063,0.03809]},{"body_a":"channel_base_body","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.53818,-0.1,0.065],"force_p95":78.97978,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":86.89518,"mean_force":32.96209,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4954,-0.07476,0.03847]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":12.0,"contact_point_centroid":[0.52502,-0.04711,0.01659],"force_p95":43.63254,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":52.89916,"mean_force":27.38526,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49626,-0.0748,0.03839]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":325.0,"contact_point_centroid":[0.47437,-0.05368,0.02273],"force_p95":38.07089,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.08547,"mean_force":23.79763,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50072,-0.06744,0.03741]},{"body_a":"peg","body_b":"world","contact_count":112.0,"contact_point_centroid":[0.50862,-0.06762,-0.00056],"force_p95":2.74676,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.41521,"mean_force":0.83395,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49285,-0.06415,0.038]},{"body_a":"peg","body_b":"link7","contact_count":244.0,"contact_point_centroid":[0.51785,0.00931,0.06875],"force_p95":19.75415,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.66911,"mean_force":9.08967,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.489,0.03549,0.03795]},{"body_a":"peg","body_b":"world","contact_count":96.0,"contact_point_centroid":[0.50546,-0.07556,-0.00099],"force_p95":4.94242,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.50088,"mean_force":0.71653,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49856,-0.07189,0.03764]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.49432,0.05896,0.00937],"force_p95":0.55417,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56118,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49747,0.13481,0.23556]}],"total_contact_groups":18},"final_pose_error":0.04125,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4914,-0.06444,0.02451],"final_tcp_position":[0.50034,-0.06686,0.0383],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":6290.13844,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49409,0.05914,0.03393],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.1394,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54973,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":1006.0,"raw_peak_contact_force":4.20518,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14702,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":443.0,"n_steps_budget":930.0,"object_pos_end":[0.49439,0.05889,0.034],"object_pos_start":[0.49409,0.05914,0.03393],"object_to_goal_dist_end":0.13914,"object_to_goal_dist_start":0.1394,"object_z_max":0.034,"peak_contact_force":0.54579,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":443.0,"raw_peak_contact_force":0.55295,"tcp_end":[0.49044,0.0962,0.04256],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03848,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50693,-0.07209,0.0171],"object_pos_start":[0.49439,0.05889,0.034],"object_to_goal_dist_end":0.02519,"object_to_goal_dist_start":0.13914,"object_z_max":0.03997,"peak_contact_force":6290.13844,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3360.0,"raw_peak_contact_force":211.06082,"tcp_end":[0.49551,-0.07509,0.03852],"tcp_start":[0.49044,0.0962,0.04256],"tcp_to_object_dist_end":0.02445,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":460.0,"n_steps_budget":600.0,"object_pos_end":[0.4914,-0.06444,0.02451],"object_pos_start":[0.50693,-0.07209,0.0171],"object_to_goal_dist_end":0.02358,"object_to_goal_dist_start":0.02519,"object_z_max":0.02448,"peak_contact_force":198.37442,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2147.0,"raw_peak_contact_force":307.29814,"tcp_end":[0.50034,-0.06686,0.0383],"tcp_start":[0.49551,-0.07509,0.03852],"tcp_to_object_dist_end":0.0166,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```