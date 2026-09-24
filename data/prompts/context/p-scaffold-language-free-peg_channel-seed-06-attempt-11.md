## Search State

- **Seed**: 6
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | -0.4006 | 0.00 | ❌ rejected |
| 10 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | -0.0499 | 0.44 | ❌ rejected |
| 9 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.1430 | 0.32 | ❌ rejected |
| 8 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 12 | -0.4106 | 0.13 | ❌ rejected |
| 7 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.2771 | 0.00 | ❌ rejected |

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
| `object` | offset from object initial position (0.5030531481177555, 0.06746166958506708, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5030531481177555, -0.09253833041493292, 0.04) | final destination targets |
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

## Current Skill (Q=-0.401) — your mutation base

```yaml
skill: peg_channel
phases:
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
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_depth:
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

- **Composite score**: -0.401
- **task_score** (E): 0.000
- **fitness_score**: 0.039  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.690

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.1319 |
| approach_1 | 1.00 | 1.00 | 0.1316 |
| contact_1 | 1.00 | 1.00 | 0.0075 |
| push_1 | 0.00 | 1.00 | 0.0003 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.498, 0.114, 0.202) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.547 | 2.127 |
| approach_1 | approach | 1.00 / step_budget | (0.498, 0.114, 0.202)→(0.497, 0.104, 0.071) | (0.501, 0.099, 0.034)→(0.501, 0.100, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.556 | 0.627 |
| contact_1 | contact | 1.00 / force_exceeded | (0.497, 0.104, 0.071)→(0.495, 0.103, 0.064) | (0.501, 0.100, 0.034)→(0.501, 0.102, 0.034) | 0.180→0.182 | 1.00 / 2.000 | 23.027 | 23.027 |
| push_1 | push | 0.00 / guard_failure | (0.495, 0.103, 0.064)→(0.495, 0.103, 0.064) | (0.501, 0.102, 0.034)→(0.501, 0.102, 0.034) | 0.182→0.182 | 1.00 / 2.000 | 22.586 | 22.586 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.325
- terminal_score: 0.000
- phase_score: 0.068
- phase_breakdown.reach_object_score: 0.226
- phase_breakdown.push_channel_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.041
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.401
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.325


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69663,"average_solve_count":89.0,"average_success_count":89.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.0018,"align_1.lateral_offset_y":-0.00298,"align_1.tolerance":0.02682,"approach_1.arc_height":0.02936,"approach_1.speed":0.06411,"contact_1.force_threshold":14.43131,"contact_1.speed":0.0289,"push_1.max_time":2.87006,"push_1.push_depth":0.22406,"push_1.speed":0.05618,"retract_1.retract_height":0.15447,"retract_1.speed":0.05446},"optimized_scores":{"best_composite_score":-0.40082,"best_fitness_score":0.03918,"best_task_score":0.00044},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":46.0,"contact_point_centroid":[0.50344,0.0674,0.00938],"force_p95":0.5506,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.23395,"mean_force":1.10507,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49816,0.07018,0.06799]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50828,0.06991,0.05879],"force_p95":25.77315,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.77315,"mean_force":25.77315,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49738,0.06983,0.06379]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.50393,0.05645,0.00937],"force_p95":16.68063,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.50815,"mean_force":9.23289,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4973,0.06981,0.06356]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.5082,0.06996,0.05867],"force_p95":16.05211,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.84918,"mean_force":8.87848,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4973,0.06981,0.06356]},{"body_a":"peg","body_b":"channel_base_body","contact_count":298.0,"contact_point_centroid":[0.50302,0.06755,0.0093],"force_p95":0.68972,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.57552,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49876,0.13933,0.24694]},{"body_a":"peg","body_b":"channel_base_body","contact_count":856.0,"contact_point_centroid":[0.50306,0.06745,0.00938],"force_p95":0.55065,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5555,"mean_force":0.54664,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49778,0.09228,0.13109]}],"total_contact_groups":6},"final_pose_error":0.22401,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50295,0.06739,0.03374],"final_tcp_position":[0.49717,0.06977,0.06339],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":26.23395,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":314.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.06746,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.5427,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":298.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_object","tcp_end":[0.49878,0.08184,0.19952],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1664,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":856.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50309,0.06746,0.0338],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14762,"object_z_max":0.0338,"peak_contact_force":0.54355,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":856.0,"raw_peak_contact_force":0.5555,"subtask_id":"reach_object","tcp_end":[0.49908,0.07067,0.07177],"tcp_start":[0.49878,0.08184,0.19952],"tcp_to_object_dist_end":0.03832,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":46.0,"n_steps_budget":840.0,"object_pos_end":[0.50308,0.06743,0.03379],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.1476,"object_to_goal_dist_start":0.14762,"object_z_max":0.0338,"peak_contact_force":26.23395,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":47.0,"raw_peak_contact_force":26.23395,"subtask_id":"reach_object","tcp_end":[0.49736,0.06982,0.06362],"tcp_start":[0.49908,0.07067,0.07177],"tcp_to_object_dist_end":0.03047,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.50295,0.06739,0.03374],"object_pos_start":[0.50308,0.06743,0.03379],"object_to_goal_dist_end":0.14755,"object_to_goal_dist_start":0.1476,"object_z_max":0.03379,"peak_contact_force":17.50815,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":17.50815,"subtask_id":"push_channel","tcp_end":[0.49717,0.06977,0.06339],"tcp_start":[0.49736,0.06982,0.06362],"tcp_to_object_dist_end":0.03031,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73684,"average_solve_count":76.0,"average_success_count":76.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00918,"align_1.lateral_offset_y":0.00066,"align_1.tolerance":0.01501,"approach_1.arc_height":0.0542,"approach_1.speed":0.07405,"contact_1.force_threshold":13.76849,"contact_1.speed":0.04708,"push_1.max_time":4.2504,"push_1.push_depth":0.1613,"push_1.speed":0.04592,"retract_1.retract_height":0.11744,"retract_1.speed":0.04184},"optimized_scores":{"best_composite_score":-0.40154,"best_fitness_score":0.03846,"best_task_score":0.00047},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":36.0,"contact_point_centroid":[0.50319,0.11169,0.00942],"force_p95":0.58803,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.1967,"mean_force":1.17186,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49934,0.11677,0.06709]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50962,0.11642,0.05884],"force_p95":22.73865,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.73865,"mean_force":22.73865,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49863,0.11626,0.06365]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.50476,0.10639,0.0094],"force_p95":15.71784,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.50244,"mean_force":8.65644,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49855,0.11621,0.0634]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50954,0.11641,0.0587],"force_p95":15.10049,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.84622,"mean_force":8.38892,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49855,0.11621,0.0634]},{"body_a":"peg","body_b":"channel_base_body","contact_count":222.0,"contact_point_centroid":[0.50347,0.11162,0.00932],"force_p95":0.77745,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.58055,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50667,0.16109,0.24762]},{"body_a":"peg","body_b":"channel_base_body","contact_count":969.0,"contact_point_centroid":[0.50368,0.11167,0.00941],"force_p95":0.59884,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66596,"mean_force":0.54351,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50569,0.15172,0.13466]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49992,0.19873,0.29863]}],"total_contact_groups":7},"final_pose_error":0.16121,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50362,0.1117,0.03377],"final_tcp_position":[0.49842,0.11615,0.06321],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":23.1967,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":244.0,"n_steps_budget":900.0,"object_pos_end":[0.50373,0.11179,0.03383],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19193,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.56248,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":238.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_object","tcp_end":[0.51373,0.12641,0.20314],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.17023,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":969.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.11173,0.03383],"object_pos_start":[0.50373,0.11179,0.03383],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19193,"object_z_max":0.03395,"peak_contact_force":0.5527,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":969.0,"raw_peak_contact_force":0.66596,"subtask_id":"reach_object","tcp_end":[0.49998,0.11747,0.06999],"tcp_start":[0.51373,0.12641,0.20314],"tcp_to_object_dist_end":0.03681,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":36.0,"n_steps_budget":600.0,"object_pos_end":[0.50373,0.11173,0.03384],"object_pos_start":[0.50373,0.11173,0.03383],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19187,"object_z_max":0.03387,"peak_contact_force":23.1967,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":37.0,"raw_peak_contact_force":23.1967,"subtask_id":"reach_object","tcp_end":[0.49861,0.11623,0.06347],"tcp_start":[0.49998,0.11747,0.06999],"tcp_to_object_dist_end":0.0304,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.50362,0.1117,0.03377],"object_pos_start":[0.50373,0.11173,0.03384],"object_to_goal_dist_end":0.19183,"object_to_goal_dist_start":0.19187,"object_z_max":0.03384,"peak_contact_force":16.50244,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":16.50244,"subtask_id":"push_channel","tcp_end":[0.49842,0.11615,0.06321],"tcp_start":[0.49861,0.11623,0.06347],"tcp_to_object_dist_end":0.03022,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67568,"average_solve_count":74.0,"average_success_count":74.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00548,"align_1.lateral_offset_y":2e-05,"align_1.tolerance":0.02541,"approach_1.arc_height":0.02837,"approach_1.speed":0.07819,"contact_1.force_threshold":12.95542,"contact_1.speed":0.02894,"push_1.max_time":2.42549,"push_1.push_depth":0.21822,"push_1.speed":0.02059,"retract_1.retract_height":0.11504,"retract_1.speed":0.05654},"optimized_scores":{"best_composite_score":-0.3994,"best_fitness_score":0.0406,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.47806,0.11985,0.00947],"force_p95":33.7469,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.7469,"mean_force":33.7469,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49031,0.12172,0.06571]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49954,0.1153,0.06184],"force_p95":32.97859,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.97859,"mean_force":32.97859,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49031,0.12172,0.06571]},{"body_a":"peg","body_b":"channel_base_body","contact_count":40.0,"contact_point_centroid":[0.49605,0.11991,0.00944],"force_p95":0.5741,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.64988,"mean_force":1.01112,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49105,0.12197,0.0695]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49965,0.11543,0.06184],"force_p95":19.06989,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.06989,"mean_force":19.06989,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49033,0.12173,0.06588]},{"body_a":"peg","body_b":"channel_base_body","contact_count":204.0,"contact_point_centroid":[0.49661,0.11907,0.00935],"force_p95":0.7111,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.58076,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48987,0.16381,0.24766]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49907,0.19774,0.29692]},{"body_a":"peg","body_b":"channel_base_body","contact_count":865.0,"contact_point_centroid":[0.49601,0.11927,0.00943],"force_p95":0.60012,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66092,"mean_force":0.54176,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48574,0.14333,0.13622]}],"total_contact_groups":7},"final_pose_error":0.21818,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49595,0.12572,0.03327],"final_tcp_position":[0.49022,0.12169,0.0656],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":33.7469,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":229.0,"n_steps_budget":870.0,"object_pos_end":[0.49609,0.11907,0.03386],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19921,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.5356,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":228.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_object","tcp_end":[0.48193,0.13251,0.20449],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.17174,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":865.0,"n_steps_budget":1000.0,"object_pos_end":[0.49606,0.12149,0.03383],"object_pos_start":[0.49609,0.11907,0.03386],"object_to_goal_dist_end":0.20162,"object_to_goal_dist_start":0.19921,"object_z_max":0.03416,"peak_contact_force":0.572,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":865.0,"raw_peak_contact_force":0.66092,"subtask_id":"reach_object","tcp_end":[0.49184,0.12242,0.07272],"tcp_start":[0.48193,0.13251,0.20449],"tcp_to_object_dist_end":0.03913,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":40.0,"n_steps_budget":870.0,"object_pos_end":[0.49601,0.12562,0.03325],"object_pos_start":[0.49606,0.12149,0.03383],"object_to_goal_dist_end":0.20577,"object_to_goal_dist_start":0.20162,"object_z_max":0.03383,"peak_contact_force":19.64988,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":41.0,"raw_peak_contact_force":19.64988,"subtask_id":"reach_object","tcp_end":[0.49031,0.12172,0.06571],"tcp_start":[0.49184,0.12242,0.07272],"tcp_to_object_dist_end":0.03319,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49595,0.12572,0.03327],"object_pos_start":[0.49601,0.12562,0.03325],"object_to_goal_dist_end":0.20587,"object_to_goal_dist_start":0.20577,"object_z_max":0.03325,"peak_contact_force":33.7469,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":33.7469,"subtask_id":"push_channel","tcp_end":[0.49022,0.12169,0.0656],"tcp_start":[0.49031,0.12172,0.06571],"tcp_to_object_dist_end":0.03309,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```