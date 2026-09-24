## Search State

- **Seed**: 6
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.1430 | 0.32 | ❌ rejected |
| 8 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 12 | -0.4106 | 0.13 | ❌ rejected |
| 7 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.2771 | 0.00 | ❌ rejected |
| 6 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3569 | 0.72 | ❌ rejected |
| 5 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | time_limit | 9 | -0.0271 | 0.37 | ❌ rejected |

**Proposal policy**: task_score is 0.32 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.143) — your mutation base

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

- **Composite score**: -0.143
- **task_score** (E): 0.318
- **fitness_score**: 0.330  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.067
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.1660 |
| approach_1 | 1.00 | 1.00 | 0.0770 |
| contact_1 | 0.67 | 1.00 | 0.0266 |
| push_1 | 0.33 | 1.00 | 0.0413 |
| retract_1 | 1.00 | 1.00 | 0.0832 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.498, 0.151, 0.143) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.544 | 2.127 |
| approach_1 | approach | 1.00 / step_budget | (0.498, 0.151, 0.143)→(0.497, 0.134, 0.069) | (0.501, 0.099, 0.034)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.522 | 0.616 |
| contact_1 | contact | 0.67 / step_budget | (0.497, 0.134, 0.069)→(0.495, 0.116, 0.049) | (0.501, 0.099, 0.034)→(0.502, 0.090, 0.035) | 0.180→0.170 | 1.00 / 2.000 | 8.954 | 10.045 |
| push_1 | push | 0.33 / guard_failure | (0.494, 0.112, 0.048)→(0.493, 0.070, 0.046) | (0.502, 0.090, 0.035)→(0.503, 0.045, 0.037) | 0.170→0.126 | 1.00 / 2.667 | 64.484 | 73.548 |
| retract_1 | retract | 1.00 / step_budget | (0.493, 0.070, 0.046)→(0.499, 0.058, 0.128) | (0.503, 0.045, 0.037)→(0.503, 0.048, 0.034) | 0.126→0.129 | 1.00 / 1.000 | 0.544 | 56.289 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.783
- alignment_error: None
- force_efficiency: 0.307
- terminal_score: 0.783
- phase_score: 0.606
- phase_breakdown.reach_object_score: 0.470
- phase_breakdown.push_channel_score: 0.664

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.677
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.783
- **Median Q (composite search score)**: -0.209
- **K-run variance**: 0.0428
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.260


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.608,"average_solve_count":250.0,"average_success_count":250.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00182,"approach_1.arc_height":0.0488,"approach_1.speed":0.01568,"contact_1.force_threshold":8.47456,"contact_1.speed":0.01315,"push_1.push_depth":0.11104,"push_1.speed":0.02283,"retract_1.arc_height":0.06315,"retract_1.speed":0.04858},"optimized_scores":{"best_composite_score":-0.35707,"best_fitness_score":0.18293,"best_task_score":0.16492},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54051,0.06482,0.05998],"force_p95":143.12577,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":143.77275,"mean_force":117.285,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49542,0.06566,0.03706]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.54044,0.06372,0.05995],"force_p95":119.06282,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":132.36187,"mean_force":71.52232,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49535,0.06462,0.03704]},{"body_a":"peg","body_b":"channel_base_body","contact_count":33.0,"contact_point_centroid":[0.50352,0.03034,0.00992],"force_p95":19.75006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.94843,"mean_force":10.59066,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49652,0.07398,0.03843]},{"body_a":"attachment","body_b":"peg","contact_count":36.0,"contact_point_centroid":[0.50162,0.0625,0.04246],"force_p95":19.39548,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.5999,"mean_force":9.36123,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49652,0.07407,0.03845]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50709,0.04419,0.00991],"force_p95":3.0972,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.60005,"mean_force":1.91955,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49703,0.08639,0.04845]},{"body_a":"attachment","body_b":"peg","contact_count":866.0,"contact_point_centroid":[0.50067,0.07316,0.04698],"force_p95":2.83053,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.28159,"mean_force":1.7712,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49702,0.08469,0.04656]},{"body_a":"peg","body_b":"channel_base_body","contact_count":832.0,"contact_point_centroid":[0.50309,0.06747,0.00935],"force_p95":0.5532,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55699,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49982,0.15899,0.21747]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50601,0.04016,0.00943],"force_p95":0.55264,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.8548,"mean_force":0.54518,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49713,0.08411,0.08059]},{"body_a":"attachment","body_b":"peg","contact_count":22.0,"contact_point_centroid":[0.50294,0.05671,0.05081],"force_p95":1.04561,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.12714,"mean_force":0.23576,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49422,0.068,0.03778]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52505,0.04389,0.01364],"force_p95":0.95133,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.97084,"mean_force":0.75358,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49571,0.06893,0.03746]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50305,0.06744,0.00938],"force_p95":0.55056,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55077,"mean_force":0.54665,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49898,0.1194,0.09097]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":10.0,"contact_point_centroid":[0.52506,0.03176,0.06],"force_p95":0.19796,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24906,"mean_force":0.10124,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49518,0.06461,0.0372]}],"total_contact_groups":12},"final_pose_error":0.02933,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50648,0.04107,0.03413],"final_tcp_position":[0.50235,0.06388,0.12681],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":143.77275,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":848.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54783,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":832.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_object","tcp_end":[0.50139,0.12036,0.14204],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12051,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14758,"object_z_max":0.0338,"peak_contact_force":0.54744,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55077,"subtask_id":"reach_object","tcp_end":[0.49914,0.10279,0.06891],"tcp_start":[0.50139,0.12036,0.14204],"tcp_to_object_dist_end":0.04999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50573,0.04919,0.03635],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.12937,"object_to_goal_dist_start":0.14759,"object_z_max":0.03692,"peak_contact_force":2.13968,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1866.0,"raw_peak_contact_force":4.60005,"subtask_id":"reach_object","tcp_end":[0.49769,0.07795,0.03979],"tcp_start":[0.49914,0.10279,0.06891],"tcp_to_object_dist_end":0.03006,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":48.0,"n_steps_budget":1000.0,"object_pos_end":[0.50627,0.03724,0.03723],"object_pos_start":[0.50573,0.04919,0.03635],"object_to_goal_dist_end":0.11744,"object_to_goal_dist_start":0.12937,"object_z_max":0.03768,"peak_contact_force":137.30292,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":76.0,"raw_peak_contact_force":143.77275,"subtask_id":"push_channel","tcp_end":[0.49539,0.0651,0.03703],"tcp_start":[0.49541,0.06534,0.03704],"tcp_to_object_dist_end":0.02991,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50648,0.04107,0.03413],"object_pos_start":[0.50636,0.03677,0.03723],"object_to_goal_dist_end":0.12139,"object_to_goal_dist_start":0.11697,"object_z_max":0.0375,"peak_contact_force":0.549,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1040.0,"raw_peak_contact_force":132.36187,"tcp_end":[0.50235,0.06388,0.12681],"tcp_start":[0.49539,0.0651,0.03703],"tcp_to_object_dist_end":0.09554,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.67508,"average_solve_count":317.0,"average_success_count":317.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00054,"approach_1.arc_height":0.03596,"approach_1.speed":0.01649,"contact_1.force_threshold":4.26627,"contact_1.speed":0.01148,"push_1.push_depth":0.14241,"push_1.speed":0.0257,"retract_1.arc_height":0.0813,"retract_1.speed":0.0565},"optimized_scores":{"best_composite_score":0.13684,"best_fitness_score":0.67684,"best_task_score":0.7832},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":245.0,"contact_point_centroid":[0.49984,0.05949,0.03983],"force_p95":31.63418,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.63659,"mean_force":12.06405,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49475,0.07017,0.04028]},{"body_a":"peg","body_b":"channel_base_body","contact_count":190.0,"contact_point_centroid":[0.50528,0.02932,0.00988],"force_p95":26.9143,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.43377,"mean_force":14.06716,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49481,0.06975,0.04035]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":169.0,"contact_point_centroid":[0.52508,0.0364,0.02547],"force_p95":14.27219,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.70481,"mean_force":5.58912,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49446,0.06112,0.0399]},{"body_a":"attachment","body_b":"peg","contact_count":35.0,"contact_point_centroid":[0.50254,0.0006,0.05491],"force_p95":0.69124,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.32301,"mean_force":0.45399,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49281,0.01169,0.04244]},{"body_a":"peg","body_b":"channel_base_body","contact_count":986.0,"contact_point_centroid":[0.50679,-0.01495,0.00944],"force_p95":0.56398,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.58995,"mean_force":0.54626,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49752,0.01643,0.08782]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.52506,-0.01836,0.05734],"force_p95":0.34782,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.83269,"mean_force":0.22025,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4929,0.01186,0.04289]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50507,0.09677,0.00979],"force_p95":1.98914,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.25301,"mean_force":1.24356,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49747,0.13922,0.05083]},{"body_a":"peg","body_b":"channel_base_body","contact_count":714.0,"contact_point_centroid":[0.50361,0.11169,0.00938],"force_p95":0.6133,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.5556,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50205,0.18057,0.21804]},{"body_a":"attachment","body_b":"peg","contact_count":660.0,"contact_point_centroid":[0.50191,0.12414,0.05421],"force_p95":1.67997,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.90219,"mean_force":1.22735,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49753,0.13596,0.04811]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50371,0.11161,0.00942],"force_p95":0.59304,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64041,"mean_force":0.54256,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50141,0.17084,0.1043]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49972,0.19943,0.29907]}],"total_contact_groups":11},"final_pose_error":0.00991,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50688,-0.01353,0.03377],"final_tcp_position":[0.50324,-0.01309,0.13146],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":34.63659,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":736.0,"n_steps_budget":1000.0,"object_pos_end":[0.50376,0.11173,0.03379],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.56349,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":730.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_object","tcp_end":[0.50576,0.16278,0.14313],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12069,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.11171,0.03396],"object_pos_start":[0.50376,0.11173,0.03379],"object_to_goal_dist_end":0.19184,"object_to_goal_dist_start":0.19187,"object_z_max":0.03402,"peak_contact_force":0.50766,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.64041,"subtask_id":"reach_object","tcp_end":[0.49989,0.1562,0.068],"tcp_start":[0.50576,0.16278,0.14313],"tcp_to_object_dist_end":0.05615,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5044,0.10209,0.03603],"object_pos_start":[0.50371,0.11171,0.03396],"object_to_goal_dist_end":0.18218,"object_to_goal_dist_start":0.19184,"object_z_max":0.03603,"peak_contact_force":1.44012,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1660.0,"raw_peak_contact_force":2.25301,"subtask_id":"reach_object","tcp_end":[0.49793,0.13094,0.04424],"tcp_start":[0.49989,0.1562,0.068],"tcp_to_object_dist_end":0.03069,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":342.0,"n_steps_budget":1000.0,"object_pos_end":[0.50686,-0.01923,0.03834],"object_pos_start":[0.5044,0.10209,0.03603],"object_to_goal_dist_end":0.06118,"object_to_goal_dist_start":0.18218,"object_z_max":0.03986,"peak_contact_force":33.99252,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":604.0,"raw_peak_contact_force":34.63659,"subtask_id":"push_channel","tcp_end":[0.49439,0.00742,0.03979],"tcp_start":[0.49793,0.13094,0.04424],"tcp_to_object_dist_end":0.02946,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":987.0,"n_steps_budget":1000.0,"object_pos_end":[0.50688,-0.01353,0.03377],"object_pos_start":[0.50686,-0.01923,0.03834],"object_to_goal_dist_end":0.06711,"object_to_goal_dist_start":0.06118,"object_z_max":0.03864,"peak_contact_force":0.54659,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1057.0,"raw_peak_contact_force":8.32301,"tcp_end":[0.50324,-0.01309,0.13146],"tcp_start":[0.49439,0.00742,0.03979],"tcp_to_object_dist_end":0.09775,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.92086,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00209,"approach_1.arc_height":0.05981,"approach_1.speed":0.04926,"contact_1.force_threshold":10.41663,"contact_1.speed":0.00842,"push_1.push_depth":0.13949,"push_1.speed":0.01531,"retract_1.arc_height":0.08236,"retract_1.speed":0.04837},"optimized_scores":{"best_composite_score":-0.20886,"best_fitness_score":0.13114,"best_task_score":0.00557},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":14.0,"contact_point_centroid":[0.48151,0.11459,0.00951],"force_p95":40.24526,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.23462,"mean_force":30.55522,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49008,0.13927,0.06289]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.50063,0.13599,0.05867],"force_p95":39.89813,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.89711,"mean_force":30.15499,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49008,0.13927,0.06289]},{"body_a":"peg","body_b":"channel_base_body","contact_count":740.0,"contact_point_centroid":[0.49455,0.11833,0.00944],"force_p95":0.6265,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.18289,"mean_force":0.65276,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48934,0.13992,0.09435]},{"body_a":"attachment","body_b":"peg","contact_count":28.0,"contact_point_centroid":[0.49974,0.13598,0.05873],"force_p95":14.78711,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.72486,"mean_force":2.99149,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48913,0.13895,0.06303]},{"body_a":"peg","body_b":"channel_base_body","contact_count":43.0,"contact_point_centroid":[0.49634,0.11913,0.00948],"force_p95":0.60626,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.2816,"mean_force":1.0653,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4912,0.14124,0.06669]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.5009,0.1364,0.05888],"force_p95":22.83378,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.83378,"mean_force":22.83378,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49037,0.13979,0.06349]},{"body_a":"peg","body_b":"channel_base_body","contact_count":660.0,"contact_point_centroid":[0.49622,0.11909,0.00944],"force_p95":0.60458,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55108,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49192,0.18412,0.2187]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49944,0.19929,0.29812]},{"body_a":"peg","body_b":"channel_base_body","contact_count":733.0,"contact_point_centroid":[0.49606,0.1191,0.00945],"force_p95":0.60515,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65754,"mean_force":0.54027,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48855,0.16763,0.09761]}],"total_contact_groups":9},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49512,0.1179,0.03384],"final_tcp_position":[0.4918,0.12257,0.12589],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":42.23462,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":685.0,"n_steps_budget":1000.0,"object_pos_end":[0.49604,0.11901,0.03382],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19914,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.52044,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":684.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_object","tcp_end":[0.48581,0.16973,0.14425],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12195,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":733.0,"n_steps_budget":990.0,"object_pos_end":[0.49602,0.11908,0.03401],"object_pos_start":[0.49604,0.11901,0.03382],"object_to_goal_dist_end":0.19921,"object_to_goal_dist_start":0.19914,"object_z_max":0.03418,"peak_contact_force":0.50981,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":733.0,"raw_peak_contact_force":0.65754,"subtask_id":"reach_object","tcp_end":[0.49212,0.14235,0.06929],"tcp_start":[0.48581,0.16973,0.14425],"tcp_to_object_dist_end":0.04244,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":43.0,"n_steps_budget":1000.0,"object_pos_end":[0.49603,0.11902,0.03396],"object_pos_start":[0.49602,0.11908,0.03401],"object_to_goal_dist_end":0.19915,"object_to_goal_dist_start":0.19921,"object_z_max":0.03405,"peak_contact_force":23.2816,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":44.0,"raw_peak_contact_force":23.2816,"subtask_id":"reach_object","tcp_end":[0.49035,0.13971,0.06335],"tcp_start":[0.49212,0.14235,0.06929],"tcp_to_object_dist_end":0.03639,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":14.0,"n_steps_budget":1000.0,"object_pos_end":[0.4954,0.11841,0.03416],"object_pos_start":[0.49603,0.11902,0.03396],"object_to_goal_dist_end":0.19855,"object_to_goal_dist_start":0.19915,"object_z_max":0.03416,"peak_contact_force":22.15652,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":28.0,"raw_peak_contact_force":42.23462,"subtask_id":"push_channel","tcp_end":[0.48987,0.13858,0.06258],"tcp_start":[0.48989,0.13865,0.06263],"tcp_to_object_dist_end":0.03529,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":740.0,"n_steps_budget":960.0,"object_pos_end":[0.49512,0.1179,0.03384],"object_pos_start":[0.49538,0.11829,0.03413],"object_to_goal_dist_end":0.19805,"object_to_goal_dist_start":0.19843,"object_z_max":0.03493,"peak_contact_force":0.53515,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":768.0,"raw_peak_contact_force":28.18289,"tcp_end":[0.4918,0.12257,0.12589],"tcp_start":[0.48987,0.13858,0.06258],"tcp_to_object_dist_end":0.09223,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```