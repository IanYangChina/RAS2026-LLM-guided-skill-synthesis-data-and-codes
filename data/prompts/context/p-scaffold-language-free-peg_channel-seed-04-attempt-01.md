## Search State

- **Seed**: 4
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | -0.0888 | 0.41 | ❌ rejected |
| 0 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.2470 | 0.45 | ✅ accepted |

**Proposal policy**: task_score is 0.41 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`
- Frozen object start: [0.5354444884457894, 0.08090620422514894, 0.04]
- Frozen task target: [0.5354444884457894, -0.07909379577485107, 0.04]
- Goal object position: (0.5354444884457894, -0.07909379577485107, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5354444884457894, 0.08090620422514894, 0.04)
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
  frozen_object_start: [0.5354, 0.0809, 0.04]
  frozen_task_target: [0.5354, -0.0791, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5354444884457894, 0.08090620422514894, 0.04]}
  frozen_targets: {'channel_exit': [0.5354444884457894, -0.07909379577485107, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c

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
| `object` | offset from object initial position (0.5354444884457894, 0.08090620422514894, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5354444884457894, -0.07909379577485107, 0.04) | final destination targets |
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

## Current Skill (Q=-0.089) — your mutation base

```yaml
skill: peg_channel
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  parameters:
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

```

## Design Metrics

- **Composite score**: -0.089
- **task_score** (E): 0.414
- **fitness_score**: 0.551  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.640

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_behind | 1.00 | 1.00 | 0.0936 |
| descend_to_peg | 1.00 | 0.67 | 0.1908 |
| contact_peg | 0.00 | 1.00 | 0.0279 |
| push_through_channel | 1.00 | 1.00 | 0.0375 |
| retract_up | 0.00 | 1.00 | 0.1469 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_behind | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.141, 0.232) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.546 | 3.242 |
| descend_to_peg | descend | 1.00 / step_budget | (0.516, 0.141, 0.232)→(0.503, 0.121, 0.043) | (0.505, 0.084, 0.034)→(0.504, 0.075, 0.036) | 0.165→0.155 | 0.67 / 0.667 | 0.365 | 49.517 |
| contact_peg | contact | 0.00 / step_budget | (0.503, 0.121, 0.043)→(0.500, 0.096, 0.032) | (0.504, 0.075, 0.036)→(0.505, 0.063, 0.032) | 0.155→0.143 | 1.00 / 2.000 | 1.286 | 3.253 |
| push_through_channel | push | 1.00 / time_limit | (0.500, 0.096, 0.032)→(0.517, 0.087, 0.062) | (0.505, 0.063, 0.032)→(0.500, -0.044, 0.031) | 0.143→0.039 | 1.00 / 3.000 | 420.019 | 3255.221 |
| retract_up | retract | 0.00 / step_budget | (0.517, 0.087, 0.062)→(0.510, 0.040, 0.200) | (0.500, -0.044, 0.031)→(0.498, -0.044, 0.031) | 0.039→0.038 | 1.00 / 1.000 | 0.586 | 421.203 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.868
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.868
- phase_score: 0.773
- phase_breakdown.pre_insert_alignment_score: 0.162
- phase_breakdown.channel_insertion_score: 0.925

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.811
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.868
- **Median Q (composite search score)**: -0.121
- **K-run variance**: 0.0400
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.264


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `424e8a040c59c1e1e42822c1022320b6050001458f7b9b4937cb9238911ce80b`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `72d2436204c0f1ee3bbdbdfe3e5489661153a48f95d8f0dc3b73e6ce1e1e081b`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17647,"average_solve_count":255.0,"average_success_count":255.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.align_y_offset":0.01762,"align_behind.approach_height":0.10517,"align_behind.speed":0.18531,"contact_peg.contact_force_threshold":9.42629,"contact_peg.speed":0.02301,"descend_to_peg.descend_y_offset":0.00111,"descend_to_peg.speed":0.02342,"push_through_channel.push_distance":0.20126,"push_through_channel.push_speed":0.05891,"retract_up.retract_height":0.12694,"retract_up.speed":0.07159},"optimized_scores":{"best_composite_score":-0.12142,"best_fitness_score":0.51858,"best_task_score":0.15908},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":951.0,"contact_point_centroid":[0.52571,0.11918,0.05994],"force_p95":392.71145,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2233.83231,"mean_force":368.82452,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.5176,0.06902,0.0912]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":30.0,"contact_point_centroid":[0.52681,0.05818,0.0596],"force_p95":1814.55839,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2188.52985,"mean_force":799.13056,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51012,0.05118,0.03339]},{"body_a":"attachment","body_b":"peg","contact_count":62.0,"contact_point_centroid":[0.51492,0.09602,0.05575],"force_p95":142.79081,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":147.41662,"mean_force":102.31826,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50792,0.10502,0.05532]},{"body_a":"peg","body_b":"channel_base_body","contact_count":629.0,"contact_point_centroid":[0.50694,0.08148,0.00931],"force_p95":113.43761,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":142.44525,"mean_force":10.5489,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51596,0.11428,0.13241]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.52501,0.11996,0.05996],"force_p95":89.26061,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":91.89753,"mean_force":65.36537,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.52544,0.07091,0.08747]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50226,0.05716,0.03377],"force_p95":55.61733,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.46593,"mean_force":31.18305,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50381,0.06863,0.03329]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":27.0,"contact_point_centroid":[0.52608,-0.03654,0.05302],"force_p95":5.57401,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.44917,"mean_force":2.49769,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50566,0.04904,0.05575]},{"body_a":"peg","body_b":"channel_base_body","contact_count":963.0,"contact_point_centroid":[0.49476,-0.07147,0.00948],"force_p95":0.78287,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.14834,"mean_force":0.64949,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51746,0.0691,0.09089]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":23.0,"contact_point_centroid":[0.52503,0.08043,0.05711],"force_p95":8.17781,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.97907,"mean_force":4.29309,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50901,0.10504,0.05361]},{"body_a":"peg","body_b":"channel_base_body","contact_count":15.0,"contact_point_centroid":[0.49259,-0.10029,0.05798],"force_p95":7.10853,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.13688,"mean_force":3.88011,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51473,0.07122,0.09937]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":64.0,"contact_point_centroid":[0.47471,-0.06291,0.05445],"force_p95":5.96514,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.82023,"mean_force":1.37082,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51245,0.06487,0.08569]},{"body_a":"peg","body_b":"channel_base_body","contact_count":351.0,"contact_point_centroid":[0.5056,0.08086,0.00935],"force_p95":0.56712,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.59024,"phase_index":0.0,"phase_name":"align_behind","phase_type":"approach","tcp_position_centroid":[0.51482,0.16055,0.25963]},{"body_a":"peg","body_b":"channel_base_body","contact_count":667.0,"contact_point_centroid":[0.50179,0.03356,0.00796],"force_p95":0.72566,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.99047,"mean_force":0.63075,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50099,0.08621,0.03694]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"align_behind","phase_type":"approach","tcp_position_centroid":[0.50047,0.19725,0.29686]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49416,-0.07504,0.0094],"force_p95":0.55245,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55389,"mean_force":0.54567,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51919,0.04392,0.15964]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.05577,0.02419],"force_p95":0.4157,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4157,"mean_force":0.4157,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49951,0.07417,0.03547]}],"total_contact_groups":16},"final_pose_error":0.12009,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49415,-0.07533,0.03395],"final_tcp_position":[0.51292,0.00513,0.23323],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":2233.83231,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":380.0,"n_steps_budget":600.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54828,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":387.0,"raw_peak_contact_force":4.32595,"subtask_id":"pre_insert_alignment","tcp_end":[0.52941,0.12614,0.22726],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.20009,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":640.0,"n_steps_budget":1000.0,"object_pos_end":[0.50314,0.05198,0.0399],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.13202,"object_to_goal_dist_start":0.1611,"object_z_max":0.041,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":714.0,"raw_peak_contact_force":147.41662,"subtask_id":"pre_insert_alignment","tcp_end":[0.50659,0.10362,0.04338],"tcp_start":[0.52941,0.12614,0.22726],"tcp_to_object_dist_end":0.05187,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":686.0,"n_steps_budget":870.0,"object_pos_end":[0.50344,0.0336,0.02419],"object_pos_start":[0.50314,0.05198,0.0399],"object_to_goal_dist_end":0.11475,"object_to_goal_dist_start":0.13202,"object_z_max":0.0399,"peak_contact_force":0.62973,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":668.0,"raw_peak_contact_force":3.99047,"subtask_id":"pre_insert_alignment","tcp_end":[0.49944,0.07349,0.03539],"tcp_start":[0.50659,0.10362,0.04338],"tcp_to_object_dist_end":0.04162,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49389,-0.07502,0.03395],"object_pos_start":[0.50344,0.0336,0.02419],"object_to_goal_dist_end":0.00993,"object_to_goal_dist_start":0.11475,"object_z_max":0.04088,"peak_contact_force":362.21409,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2054.0,"raw_peak_contact_force":2233.83231,"subtask_id":"channel_insertion","tcp_end":[0.52544,0.07089,0.0874],"tcp_start":[0.49944,0.07349,0.03539],"tcp_to_object_dist_end":0.15856,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49415,-0.07533,0.03395],"object_pos_start":[0.49389,-0.07502,0.03395],"object_to_goal_dist_end":0.00962,"object_to_goal_dist_start":0.00993,"object_z_max":0.03396,"peak_contact_force":0.54038,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1005.0,"raw_peak_contact_force":91.89753,"tcp_end":[0.51292,0.00513,0.23323],"tcp_start":[0.52544,0.07089,0.0874],"tcp_to_object_dist_end":0.21572,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `54762c1e743ba455eff3c9979c2b42f5642abe1893e28eae37dc231d7efcd4e4`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.05639,"average_solve_count":266.0,"average_success_count":266.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.align_y_offset":0.03907,"align_behind.approach_height":0.10342,"align_behind.speed":0.06559,"contact_peg.contact_force_threshold":8.99764,"contact_peg.speed":0.01855,"descend_to_peg.descend_y_offset":0.0246,"descend_to_peg.speed":0.03325,"push_through_channel.push_distance":0.18255,"push_through_channel.push_speed":0.05789,"retract_up.retract_height":0.16106,"retract_up.speed":0.03412},"optimized_scores":{"best_composite_score":-0.31586,"best_fitness_score":0.32414,"best_task_score":0.21534},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":270.0,"contact_point_centroid":[0.52523,0.11145,0.05053],"force_p95":486.8765,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3572.21003,"mean_force":249.4827,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51298,0.10958,0.0476]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.54386,0.11997,0.05991],"force_p95":3345.8321,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3408.73377,"mean_force":1835.40549,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50536,0.11189,0.0262]},{"body_a":"world","body_b":"link7","contact_count":909.0,"contact_point_centroid":[0.50718,0.17484,-7e-05],"force_p95":355.22033,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":652.5423,"mean_force":284.46439,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51066,0.11312,0.04879]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":16.0,"contact_point_centroid":[0.49651,0.11512,0.00914],"force_p95":507.79791,"geom_a":"pusher_tip","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":507.91959,"mean_force":394.06173,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49487,0.10911,0.01852]},{"body_a":"world","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.50551,0.16832,-1e-05],"force_p95":145.49651,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":146.42256,"mean_force":137.16199,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51316,0.10736,0.04965]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52501,0.10913,0.04978],"force_p95":114.55043,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":120.57941,"mean_force":60.2897,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51316,0.10736,0.04965]},{"body_a":"peg","body_b":"channel_base_body","contact_count":966.0,"contact_point_centroid":[0.50518,0.01647,0.00814],"force_p95":0.72033,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":79.28846,"mean_force":0.75013,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51015,0.11304,0.04768]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.5059,0.11221,0.03765],"force_p95":65.37413,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":73.65009,"mean_force":30.29596,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50359,0.12406,0.02872]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.5257,0.07535,0.04012],"force_p95":19.38779,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.07575,"mean_force":4.08491,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50849,0.11466,0.02801]},{"body_a":"peg","body_b":"channel_base_body","contact_count":247.0,"contact_point_centroid":[0.50541,0.10476,0.00935],"force_p95":0.63571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.5921,"phase_index":0.0,"phase_name":"align_behind","phase_type":"approach","tcp_position_centroid":[0.50896,0.18294,0.26117]},{"body_a":"peg","body_b":"channel_base_body","contact_count":637.0,"contact_point_centroid":[0.50628,0.09427,0.00965],"force_p95":2.46994,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.26201,"mean_force":1.28332,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50095,0.13539,0.03364]},{"body_a":"attachment","body_b":"peg","contact_count":309.0,"contact_point_centroid":[0.50453,0.11815,0.04323],"force_p95":2.45918,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.95456,"mean_force":1.75526,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50126,0.13006,0.03133]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"align_behind","phase_type":"approach","tcp_position_centroid":[0.50026,0.19851,0.29688]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":47.0,"contact_point_centroid":[0.52502,0.09741,0.03166],"force_p95":1.09775,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.19983,"mean_force":0.63459,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50159,0.12702,0.03018]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50208,0.01423,0.00804],"force_p95":0.68339,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6834,"mean_force":0.60596,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50989,0.08789,0.1149]},{"body_a":"peg","body_b":"channel_base_body","contact_count":613.0,"contact_point_centroid":[0.50592,0.10459,0.00939],"force_p95":0.57562,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57941,"mean_force":0.54634,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50993,0.15878,0.1362]}],"total_contact_groups":16},"final_pose_error":0.22003,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50013,0.01435,0.02413],"final_tcp_position":[0.50833,0.06192,0.18313],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":3572.21003,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":274.0,"n_steps_budget":840.0,"object_pos_end":[0.50596,0.10458,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18478,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54433,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":279.0,"raw_peak_contact_force":3.33087,"subtask_id":"pre_insert_alignment","tcp_end":[0.51832,0.16834,0.22952],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.20618,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":613.0,"n_steps_budget":1000.0,"object_pos_end":[0.50587,0.10457,0.03384],"object_pos_start":[0.50596,0.10458,0.03384],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.18478,"object_z_max":0.03384,"peak_contact_force":0.55155,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":613.0,"raw_peak_contact_force":0.57941,"subtask_id":"pre_insert_alignment","tcp_end":[0.50319,0.14953,0.04327],"tcp_start":[0.51832,0.16834,0.22952],"tcp_to_object_dist_end":0.04602,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":648.0,"n_steps_budget":900.0,"object_pos_end":[0.50701,0.09603,0.03525],"object_pos_start":[0.50587,0.10457,0.03384],"object_to_goal_dist_end":0.17623,"object_to_goal_dist_start":0.18476,"object_z_max":0.03538,"peak_contact_force":1.82541,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":993.0,"raw_peak_contact_force":3.26201,"subtask_id":"pre_insert_alignment","tcp_end":[0.50172,0.1257,0.02967],"tcp_start":[0.50319,0.14953,0.04327],"tcp_to_object_dist_end":0.03065,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50427,0.01421,0.02413],"object_pos_start":[0.50701,0.09603,0.03525],"object_to_goal_dist_end":0.09563,"object_to_goal_dist_start":0.17623,"object_z_max":0.04069,"peak_contact_force":257.385,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2210.0,"raw_peak_contact_force":3572.21003,"subtask_id":"channel_insertion","tcp_end":[0.51318,0.10739,0.04962],"tcp_start":[0.50172,0.1257,0.02967],"tcp_to_object_dist_end":0.09702,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50013,0.01435,0.02413],"object_pos_start":[0.50427,0.01421,0.02413],"object_to_goal_dist_end":0.09568,"object_to_goal_dist_start":0.09563,"object_z_max":0.02413,"peak_contact_force":0.68339,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1004.0,"raw_peak_contact_force":146.42256,"tcp_end":[0.50833,0.06192,0.18313],"tcp_start":[0.51318,0.10739,0.04962],"tcp_to_object_dist_end":0.16616,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b230a5798f38c3fb8968a6bc74f96ee85fe7026f3170cf8216fc868a1c5c570f`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.15444,"average_solve_count":259.0,"average_success_count":259.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.align_y_offset":0.03185,"align_behind.approach_height":0.11725,"align_behind.speed":0.20178,"contact_peg.contact_force_threshold":9.26724,"contact_peg.speed":0.01386,"descend_to_peg.descend_y_offset":0.02037,"descend_to_peg.speed":0.02921,"push_through_channel.push_distance":0.19123,"push_through_channel.push_speed":0.08792,"retract_up.retract_height":0.18667,"retract_up.speed":0.0631},"optimized_scores":{"best_composite_score":0.17093,"best_fitness_score":0.81093,"best_task_score":0.86845},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":587.0,"contact_point_centroid":[0.5252,0.08359,0.0502],"force_p95":447.65862,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3959.62047,"mean_force":414.21966,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51312,0.08138,0.04847]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":105.0,"contact_point_centroid":[0.54031,0.11473,0.0598],"force_p95":3108.59838,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3856.40294,"mean_force":723.16609,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50811,0.08096,0.0442]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":143.0,"contact_point_centroid":[0.47498,0.11997,0.05997],"force_p95":551.96726,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1025.28948,"mean_force":108.67419,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51175,0.0841,0.05868]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":532.0,"contact_point_centroid":[0.47493,0.11988,0.05457],"force_p95":633.82847,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":673.76407,"mean_force":554.22442,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51325,0.08168,0.04942]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":18.0,"contact_point_centroid":[0.52508,0.08525,0.04992],"force_p95":506.38415,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":669.70071,"mean_force":322.4898,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51329,0.08348,0.04979]},{"body_a":"world","body_b":"link7","contact_count":835.0,"contact_point_centroid":[0.50723,0.14353,-6e-05],"force_p95":346.07858,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":507.9053,"mean_force":227.74322,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51271,0.0821,0.04909]},{"body_a":"world","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.50318,0.14419,-4e-05],"force_p95":326.5627,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":333.84788,"mean_force":260.76873,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51333,0.08333,0.04959]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.50519,0.07415,0.04815],"force_p95":139.29814,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":186.2144,"mean_force":35.24876,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.5015,0.08577,0.0285]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":15.0,"contact_point_centroid":[0.52616,0.04252,0.01876],"force_p95":58.41059,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":177.87741,"mean_force":13.26793,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51179,0.07492,0.02471]},{"body_a":"peg","body_b":"channel_base_body","contact_count":950.0,"contact_point_centroid":[0.49969,-0.07027,0.00953],"force_p95":0.69531,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.80712,"mean_force":0.65395,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.5121,0.08225,0.04908]},{"body_a":"peg","body_b":"channel_base_body","contact_count":705.0,"contact_point_centroid":[0.50484,0.05387,0.00974],"force_p95":2.06241,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.50714,"mean_force":1.25271,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.4977,0.09598,0.03334]},{"body_a":"peg","body_b":"channel_base_body","contact_count":304.0,"contact_point_centroid":[0.503,0.06739,0.0093],"force_p95":0.6829,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.57494,"phase_index":0.0,"phase_name":"align_behind","phase_type":"approach","tcp_position_centroid":[0.49949,0.16307,0.26745]},{"body_a":"attachment","body_b":"peg","contact_count":439.0,"contact_point_centroid":[0.50165,0.08082,0.04478],"force_p95":1.79184,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.01987,"mean_force":1.3387,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49807,0.09275,0.03166]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.47491,-0.01652,0.04473],"force_p95":1.65907,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.8188,"mean_force":0.96402,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50517,0.08013,0.04537]},{"body_a":"peg","body_b":"channel_base_body","contact_count":15.0,"contact_point_centroid":[0.49813,-0.10035,0.0575],"force_p95":0.81718,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.94008,"mean_force":0.22686,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50759,0.08353,0.04347]},{"body_a":"peg","body_b":"channel_base_body","contact_count":679.0,"contact_point_centroid":[0.50308,0.06753,0.00938],"force_p95":0.55067,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5555,"mean_force":0.54665,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49881,0.11835,0.14118]}],"total_contact_groups":17},"final_pose_error":0.23315,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50114,-0.07149,0.03503],"final_tcp_position":[0.50927,0.05228,0.1849],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":3959.62047,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":320.0,"n_steps_budget":600.0,"object_pos_end":[0.50303,0.0675,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.5457,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":304.0,"raw_peak_contact_force":2.06903,"subtask_id":"pre_insert_alignment","tcp_end":[0.50039,0.12842,0.23978],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.21482,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":679.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50303,0.0675,0.0338],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"peak_contact_force":0.54362,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":679.0,"raw_peak_contact_force":0.5555,"subtask_id":"pre_insert_alignment","tcp_end":[0.49918,0.10847,0.04299],"tcp_start":[0.50039,0.12842,0.23978],"tcp_to_object_dist_end":0.04222,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":711.0,"n_steps_budget":1000.0,"object_pos_end":[0.50473,0.05866,0.0354],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.13882,"object_to_goal_dist_start":0.14762,"object_z_max":0.03543,"peak_contact_force":1.40262,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1144.0,"raw_peak_contact_force":2.50714,"subtask_id":"pre_insert_alignment","tcp_end":[0.49889,0.08827,0.02968],"tcp_start":[0.49918,0.10847,0.04299],"tcp_to_object_dist_end":0.03071,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50103,-0.07076,0.03536],"object_pos_start":[0.50473,0.05866,0.0354],"object_to_goal_dist_end":0.01039,"object_to_goal_dist_start":0.13882,"object_z_max":0.04262,"peak_contact_force":640.45765,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3056.0,"raw_peak_contact_force":3959.62047,"subtask_id":"channel_insertion","tcp_end":[0.51334,0.08336,0.04951],"tcp_start":[0.49889,0.08827,0.02968],"tcp_to_object_dist_end":0.15526,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50114,-0.07149,0.03503],"object_pos_start":[0.50103,-0.07076,0.03536],"object_to_goal_dist_end":0.00992,"object_to_goal_dist_start":0.01039,"object_z_max":0.03536,"peak_contact_force":0.53418,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1165.0,"raw_peak_contact_force":1025.28948,"tcp_end":[0.50927,0.05228,0.1849],"tcp_start":[0.51334,0.08336,0.04951],"tcp_to_object_dist_end":0.19455,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```