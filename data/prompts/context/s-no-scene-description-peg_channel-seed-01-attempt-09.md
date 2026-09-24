## Search State

- **Seed**: 1
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → align → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 7 | -0.1096 | 0.00 | ❌ rejected |
| 8 | approach → rotate → contact → push | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | position_control | impedance_control | force_threshold_switch | admittance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 5 | 0.0551 | 0.00 | ❌ rejected |
| 7 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1659 | 0.40 | ❌ rejected |
| 6 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1659 | 0.40 | ❌ rejected |
| 5 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1614 | 0.09 | ❌ rejected |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

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
| `object` | offset from object initial position | approach/contact targets near object start |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose | approach/contact targets near fixture |

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

## Current Skill (Q=-0.110) — your mutation base

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

- **Composite score**: -0.110
- **task_score** (E): 0.001
- **fitness_score**: 0.050  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1958 |
| align_1 | 0.00 | 1.00 | 0.0435 |
| contact_1 | 1.00 | 1.00 | 0.0001 |
| push_1 | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.483, 0.095, 0.137) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.542 | 2.857 |
| align_1 | align | 0.00 / step_budget | (0.483, 0.095, 0.137)→(0.511, 0.069, 0.145) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 2.333 | 366.060 | 1042.377 |
| contact_1 | contact | 1.00 / force_exceeded | (0.511, 0.069, 0.145)→(0.511, 0.069, 0.145) | (0.497, 0.080, 0.034)→(0.497, 0.079, 0.034) | 0.160→0.160 | 1.00 / 2.333 | 92.354 | 92.354 |
| push_1 | push | 0.00 / guard_failure | (0.511, 0.069, 0.145)→(0.511, 0.069, 0.145) | (0.497, 0.079, 0.034)→(0.497, 0.079, 0.034) | 0.160→0.160 | 1.00 / 1.333 | 0.509 | 173.363 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.002
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.001
- phase_score: 0.090
- phase_breakdown.reach_peg_score: 0.300
- phase_breakdown.traverse_channel_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.055
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.001
- **Median Q (composite search score)**: -0.110
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.376


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a904e23429ae963dd2788b3e8d0575d9ce341e1daddfe013fbb1224c3e0c850e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `6bee39a4c127c6d39ee1365e3969a50bb09484f7e2580b1a3dc4d8c4ae20213b`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.07895,"average_solve_count":76.0,"average_success_count":76.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00852,"align_1.lateral_offset_y":0.00986,"approach_1.approach_speed":0.07941,"contact_1.contact_force":16.78798,"push_1.force_limit":36.86091,"push_1.push_distance":0.14964,"push_1.push_speed":0.14468},"optimized_scores":{"best_composite_score":-0.11003,"best_fitness_score":0.04997,"best_task_score":0.00062},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":484.0,"contact_point_centroid":[0.52549,0.04223,0.05982],"force_p95":571.23505,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1199.51995,"mean_force":464.62455,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50454,0.10698,0.13995]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":11.0,"contact_point_centroid":[0.47252,0.11807,0.05846],"force_p95":1014.77035,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1055.71811,"mean_force":335.84652,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46508,0.12476,0.06352]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.525,0.04165,0.05992],"force_p95":96.10058,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":98.33779,"mean_force":74.73498,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51285,0.10045,0.15138]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.525,0.0416,0.05986],"force_p95":18.56273,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":18.56273,"mean_force":18.56273,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51309,0.10037,0.15129]},{"body_a":"peg","body_b":"channel_base_body","contact_count":934.0,"contact_point_centroid":[0.50098,0.11602,0.00941],"force_p95":0.60698,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55077,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49791,0.15817,0.2076]},{"body_a":"peg","body_b":"channel_base_body","contact_count":542.0,"contact_point_centroid":[0.5009,0.11605,0.00941],"force_p95":0.60969,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65867,"mean_force":0.54354,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50265,0.10903,0.13601]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50118,0.10616,0.00941],"force_p95":0.62239,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62656,"mean_force":0.56907,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51285,0.10045,0.15138]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.48348,0.12,0.00942],"force_p95":0.51231,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51231,"mean_force":0.51231,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51309,0.10037,0.15129]}],"total_contact_groups":8},"final_pose_error":0.1758,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.501,0.11594,0.03385],"final_tcp_position":[0.51279,0.10053,0.15154],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":1199.51995,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":950.0,"n_steps_budget":1000.0,"object_pos_end":[0.50096,0.11605,0.03381],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19615,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.52566,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":934.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_peg","tcp_end":[0.49762,0.11872,0.12256],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08886,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.50091,0.11605,0.03386],"object_pos_start":[0.50096,0.11605,0.03381],"object_to_goal_dist_end":0.19615,"object_to_goal_dist_start":0.19615,"object_z_max":0.03395,"peak_contact_force":410.85188,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1037.0,"raw_peak_contact_force":1199.51995,"subtask_id":"reach_peg","tcp_end":[0.51309,0.10037,0.15129],"tcp_start":[0.49762,0.11872,0.12256],"tcp_to_object_dist_end":0.1191,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":750.0,"object_pos_end":[0.50093,0.11601,0.03386],"object_pos_start":[0.50091,0.11605,0.03386],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19615,"object_z_max":0.03386,"peak_contact_force":18.56273,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":18.56273,"tcp_end":[0.51294,0.10041,0.15131],"tcp_start":[0.51309,0.10037,0.15129],"tcp_to_object_dist_end":0.11909,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":780.0,"object_pos_end":[0.50096,0.11597,0.03385],"object_pos_start":[0.50093,0.11601,0.03386],"object_to_goal_dist_end":0.19607,"object_to_goal_dist_start":0.19611,"object_z_max":0.03386,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":98.33779,"subtask_id":"traverse_channel","tcp_end":[0.51279,0.10053,0.15154],"tcp_start":[0.51277,0.10049,0.15146],"tcp_to_object_dist_end":0.11928,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8416ac3bebb4dbec2abbf751596843a33db171fd8d70765023f3b940d846bd0c`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.03279,"average_solve_count":61.0,"average_success_count":61.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00669,"align_1.lateral_offset_y":0.00941,"approach_1.approach_speed":0.11751,"contact_1.contact_force":24.63767,"push_1.force_limit":31.58224,"push_1.push_distance":0.05573,"push_1.push_speed":0.11705},"optimized_scores":{"best_composite_score":-0.10543,"best_fitness_score":0.05457,"best_task_score":0.00121},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":456.0,"contact_point_centroid":[0.47495,-0.01266,0.05979],"force_p95":432.22166,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1002.50756,"mean_force":270.28539,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4981,0.05629,0.13314]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":227.0,"contact_point_centroid":[0.52508,-0.01541,0.05997],"force_p95":424.09185,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":463.67692,"mean_force":360.64328,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50833,0.05335,0.13919]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.47499,-0.0128,0.05999],"force_p95":259.9151,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":281.28319,"mean_force":138.64427,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51097,0.05113,0.14068]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.52505,-0.01498,0.05997],"force_p95":199.20281,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":220.18262,"mean_force":76.85572,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51097,0.05113,0.14068]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.47499,-0.01277,0.05997],"force_p95":123.82284,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":123.82284,"mean_force":123.82284,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51097,0.05118,0.14062]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.49527,0.06395,0.00938],"force_p95":0.55699,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55424,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48874,0.13697,0.2132]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49934,0.19861,0.29807]},{"body_a":"peg","body_b":"channel_base_body","contact_count":542.0,"contact_point_centroid":[0.49502,0.06385,0.00941],"force_p95":0.55079,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55403,"mean_force":0.54515,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49513,0.05816,0.13009]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.48963,0.04709,0.00941],"force_p95":0.54458,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54465,"mean_force":0.54345,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51097,0.05113,0.14068]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.48192,0.05163,0.00941],"force_p95":0.54304,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54304,"mean_force":0.54304,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51097,0.05118,0.14062]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.52511,-0.0149,0.05995],"force_p95":0.0,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51097,0.05118,0.14062]}],"total_contact_groups":11},"final_pose_error":0.11381,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49515,0.06357,0.03403],"final_tcp_position":[0.51105,0.0511,0.14071],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":1002.50756,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49482,0.06382,0.03401],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14404,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.55002,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1001.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_peg","tcp_end":[0.47996,0.07872,0.13594],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10408,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49488,0.06366,0.03403],"object_pos_start":[0.49482,0.06382,0.03401],"object_to_goal_dist_end":0.14388,"object_to_goal_dist_start":0.14404,"object_z_max":0.03403,"peak_contact_force":389.47169,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1225.0,"raw_peak_contact_force":1002.50756,"subtask_id":"reach_peg","tcp_end":[0.51097,0.05118,0.14062],"tcp_start":[0.47996,0.07872,0.13594],"tcp_to_object_dist_end":0.10851,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":690.0,"object_pos_end":[0.49493,0.06361,0.03403],"object_pos_start":[0.49488,0.06366,0.03403],"object_to_goal_dist_end":0.14383,"object_to_goal_dist_start":0.14388,"object_z_max":0.03403,"peak_contact_force":123.82284,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":123.82284,"tcp_end":[0.51093,0.05116,0.14066],"tcp_start":[0.51097,0.05118,0.14062],"tcp_to_object_dist_end":0.10854,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":630.0,"object_pos_end":[0.495,0.06358,0.03403],"object_pos_start":[0.49493,0.06361,0.03403],"object_to_goal_dist_end":0.14379,"object_to_goal_dist_start":0.14383,"object_z_max":0.03403,"peak_contact_force":0.9824,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":281.28319,"subtask_id":"traverse_channel","tcp_end":[0.51105,0.0511,0.14071],"tcp_start":[0.51101,0.05111,0.1407],"tcp_to_object_dist_end":0.10859,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0188121de1b8142d5ff7a7406b62c43adf6da5520b986a997e46ef53b7d11bf9`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67816,"average_solve_count":87.0,"average_success_count":87.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00996,"align_1.lateral_offset_y":0.00965,"approach_1.approach_speed":0.06434,"contact_1.contact_force":9.37997,"push_1.force_limit":48.88484,"push_1.push_distance":0.07734,"push_1.push_speed":0.08079},"optimized_scores":{"best_composite_score":-0.11332,"best_fitness_score":0.04668,"best_task_score":0.00056},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":526.0,"contact_point_centroid":[0.47448,-0.00337,0.05984],"force_p95":438.90191,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":925.10473,"mean_force":350.45541,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49022,0.06216,0.13891]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.47498,-0.00661,0.05994],"force_p95":138.01596,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":140.4674,"mean_force":115.95299,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50935,0.05557,0.14297]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.47496,-0.00662,0.0599],"force_p95":134.67765,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":134.67765,"mean_force":134.67765,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50927,0.05558,0.1429]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.49432,0.05896,0.00937],"force_p95":0.55417,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56118,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.484,0.14177,0.22229]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49912,0.19842,0.29766]},{"body_a":"peg","body_b":"channel_base_body","contact_count":602.0,"contact_point_centroid":[0.49399,0.05906,0.0094],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55392,"mean_force":0.54547,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48594,0.06339,0.13618]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.47848,0.05009,0.0094],"force_p95":0.54756,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54756,"mean_force":0.54756,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50927,0.05558,0.1429]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.48491,0.044,0.0094],"force_p95":0.54644,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54665,"mean_force":0.54503,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5094,0.05556,0.143]}],"total_contact_groups":8},"final_pose_error":0.12961,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49411,0.05867,0.03402],"final_tcp_position":[0.50954,0.05553,0.14306],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":925.10473,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49409,0.05914,0.03393],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.1394,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54973,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1006.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_peg","tcp_end":[0.47078,0.08779,0.15331],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12496,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":602.0,"n_steps_budget":660.0,"object_pos_end":[0.49388,0.05882,0.03402],"object_pos_start":[0.49409,0.05914,0.03393],"object_to_goal_dist_end":0.13908,"object_to_goal_dist_start":0.1394,"object_z_max":0.03402,"peak_contact_force":297.85672,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1128.0,"raw_peak_contact_force":925.10473,"subtask_id":"reach_peg","tcp_end":[0.50927,0.05558,0.1429],"tcp_start":[0.47078,0.08779,0.15331],"tcp_to_object_dist_end":0.11001,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":720.0,"object_pos_end":[0.49392,0.05876,0.03402],"object_pos_start":[0.49388,0.05882,0.03402],"object_to_goal_dist_end":0.13902,"object_to_goal_dist_start":0.13908,"object_z_max":0.03402,"peak_contact_force":134.67765,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":134.67765,"tcp_end":[0.50929,0.05557,0.14293],"tcp_start":[0.50927,0.05558,0.1429],"tcp_to_object_dist_end":0.11004,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49398,0.05871,0.03402],"object_pos_start":[0.49392,0.05876,0.03402],"object_to_goal_dist_end":0.13897,"object_to_goal_dist_start":0.13902,"object_z_max":0.03402,"peak_contact_force":0.54457,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":140.4674,"subtask_id":"traverse_channel","tcp_end":[0.50954,0.05553,0.14306],"tcp_start":[0.50951,0.05555,0.14307],"tcp_to_object_dist_end":0.1102,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```