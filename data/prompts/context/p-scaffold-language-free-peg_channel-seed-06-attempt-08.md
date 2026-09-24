## Search State

- **Seed**: 6
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 12 | -0.4106 | 0.13 | ❌ rejected |
| 7 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.2771 | 0.00 | ❌ rejected |
| 6 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3569 | 0.72 | ❌ rejected |
| 5 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | time_limit | 9 | -0.0271 | 0.37 | ❌ rejected |
| 4 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3579 | 0.72 | ❌ rejected |

**Proposal policy**: task_score is 0.13 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.411) — your mutation base

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

- **Composite score**: -0.411
- **task_score** (E): 0.127
- **fitness_score**: 0.079  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.690

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.1801 |
| approach_1 | 1.00 | 1.00 | 0.0919 |
| contact_1 | 1.00 | 1.00 | 0.0001 |
| push_1 | 0.00 | 1.00 | 0.0001 |
| retract_1 | 1.00 | 1.00 | 0.0810 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.500, 0.103, 0.151) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.555 | 2.127 |
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.103, 0.151)→(0.502, 0.107, 0.060) | (0.501, 0.099, 0.034)→(0.501, 0.091, 0.033) | 0.180→0.171 | 1.00 / 2.333 | 86.430 | 133.833 |
| contact_1 | contact | 1.00 / force_exceeded | (0.502, 0.107, 0.060)→(0.502, 0.107, 0.060) | (0.501, 0.091, 0.033)→(0.501, 0.091, 0.033) | 0.171→0.171 | 1.00 / 2.333 | 64.087 | 64.087 |
| push_1 | push | 0.00 / guard_failure | (0.502, 0.107, 0.060)→(0.502, 0.107, 0.060) | (0.501, 0.091, 0.033)→(0.501, 0.090, 0.033) | 0.171→0.171 | 1.00 / 2.333 | 64.140 | 78.071 |
| retract_1 | retract | 1.00 / step_budget | (0.502, 0.107, 0.060)→(0.498, 0.097, 0.140) | (0.501, 0.090, 0.034)→(0.501, 0.078, 0.031) | 0.170→0.159 | 1.00 / 1.000 | 0.565 | 90.607 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.288
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.288
- phase_score: 0.052
- phase_breakdown.reach_object_score: 0.203
- phase_breakdown.push_through_channel_score: 0.006

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.146
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.288
- **Median Q (composite search score)**: -0.441
- **K-run variance**: 0.0022
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.270


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20988,"average_solve_count":162.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00834,"align_1.lateral_offset_y":-0.01955,"approach_1.arc_height":0.01798,"approach_1.speed":0.03398,"contact_1.force_threshold":23.7975,"contact_1.speed":0.02847,"push_1.force_guard_threshold":12.65265,"push_1.push_distance":0.08523,"push_1.speed":0.03649,"retract_1.arc_height":0.03572,"retract_1.retract_height":0.11519,"retract_1.speed":0.03735},"optimized_scores":{"best_composite_score":-0.34373,"best_fitness_score":0.14627,"best_task_score":0.28819},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":834.0,"contact_point_centroid":[0.50397,0.07224,0.00913],"force_p95":116.02502,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":145.93707,"mean_force":29.327,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50344,0.0827,0.10172]},{"body_a":"attachment","body_b":"peg","contact_count":278.0,"contact_point_centroid":[0.50429,0.08341,0.05552],"force_p95":129.97702,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":145.42229,"mean_force":86.39578,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50438,0.07987,0.06585]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":61.0,"contact_point_centroid":[0.525,0.11996,0.05893],"force_p95":107.05423,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":134.63028,"mean_force":57.6011,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50574,0.07956,0.06395]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":258.0,"contact_point_centroid":[0.47499,0.11998,0.05767],"force_p95":98.60039,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":108.37056,"mean_force":71.92766,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50428,0.07987,0.066]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.47497,0.11996,0.05999],"force_p95":82.08896,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":84.92494,"mean_force":62.26326,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50677,0.07964,0.06117]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.47497,0.11996,0.05999],"force_p95":55.30693,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":55.30693,"mean_force":55.30693,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50689,0.07952,0.06142]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.47497,0.11995,0.05999],"force_p95":41.58016,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":41.61576,"mean_force":33.20527,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50685,0.07954,0.06131]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.525,0.11999,0.06],"force_p95":24.4693,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":26.14685,"mean_force":11.83938,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50685,0.07954,0.06131]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.50445,0.02147,0.00801],"force_p95":0.77008,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.8815,"mean_force":0.6142,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50318,0.09432,0.10285]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50307,0.06748,0.00936],"force_p95":0.55225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55539,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50044,0.14279,0.22774]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.525,0.11999,0.06],"force_p95":1.35902,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1.35902,"mean_force":1.35902,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50689,0.07952,0.06142]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.04542,0.02418],"force_p95":0.39374,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39374,"mean_force":0.39374,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50305,0.10296,0.10329]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50489,0.04878,0.00803],"force_p95":0.2323,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2323,"mean_force":0.2323,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50689,0.07952,0.06142]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50484,0.04898,0.0083],"force_p95":0.15337,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15883,"mean_force":0.10989,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50685,0.07954,0.06131]}],"total_contact_groups":14},"final_pose_error":0.01176,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50364,0.02135,0.02417],"final_tcp_position":[0.50262,0.06729,0.14492],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":145.93707,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54571,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":984.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_object","tcp_end":[0.50682,0.0762,0.1661],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13264,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":834.0,"n_steps_budget":1000.0,"object_pos_end":[0.5052,0.06149,0.03411],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.14171,"object_to_goal_dist_start":0.14759,"object_z_max":0.03399,"peak_contact_force":92.36787,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1431.0,"raw_peak_contact_force":145.93707,"subtask_id":"reach_object","tcp_end":[0.50689,0.07952,0.06142],"tcp_start":[0.50682,0.0762,0.1661],"tcp_to_object_dist_end":0.03277,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":750.0,"object_pos_end":[0.50517,0.06064,0.03479],"object_pos_start":[0.5052,0.06149,0.03411],"object_to_goal_dist_end":0.14084,"object_to_goal_dist_start":0.14171,"object_z_max":0.03411,"peak_contact_force":55.30693,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":55.30693,"subtask_id":"reach_object","tcp_end":[0.50689,0.07953,0.06136],"tcp_start":[0.50689,0.07952,0.06142],"tcp_to_object_dist_end":0.03264,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50513,0.0598,0.03545],"object_pos_start":[0.50517,0.06064,0.03479],"object_to_goal_dist_end":0.13997,"object_to_goal_dist_start":0.14084,"object_z_max":0.03607,"peak_contact_force":0.99119,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":41.61576,"subtask_id":"push_through_channel","tcp_end":[0.50679,0.07957,0.06123],"tcp_start":[0.50681,0.07955,0.06127],"tcp_to_object_dist_end":0.03253,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50364,0.02135,0.02417],"object_pos_start":[0.50506,0.0581,0.03666],"object_to_goal_dist_end":0.10265,"object_to_goal_dist_start":0.13824,"object_z_max":0.04101,"peak_contact_force":0.60595,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":978.0,"raw_peak_contact_force":84.92494,"tcp_end":[0.50262,0.06729,0.14492],"tcp_start":[0.50679,0.07957,0.06123],"tcp_to_object_dist_end":0.1292,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.27972,"average_solve_count":143.0,"average_success_count":143.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00889,"align_1.lateral_offset_y":-0.00586,"approach_1.arc_height":0.02457,"approach_1.speed":0.03293,"contact_1.force_threshold":20.23798,"contact_1.speed":0.01637,"push_1.force_guard_threshold":18.99049,"push_1.push_distance":0.11323,"push_1.speed":0.028,"retract_1.arc_height":0.079,"retract_1.retract_height":0.12546,"retract_1.speed":0.04387},"optimized_scores":{"best_composite_score":-0.4407,"best_fitness_score":0.0493,"best_task_score":0.04803},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":824.0,"contact_point_centroid":[0.5038,0.11382,0.00898],"force_p95":115.11077,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":122.22127,"mean_force":27.37449,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50842,0.12235,0.10006]},{"body_a":"attachment","body_b":"peg","contact_count":236.0,"contact_point_centroid":[0.50476,0.1248,0.05408],"force_p95":118.29257,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":121.62567,"mean_force":93.68559,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50476,0.11993,0.0644]},{"body_a":"peg","body_b":"channel_base_body","contact_count":945.0,"contact_point_centroid":[0.50305,0.10505,0.00937],"force_p95":29.92521,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":87.8773,"mean_force":3.74948,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50141,0.1252,0.105]},{"body_a":"attachment","body_b":"peg","contact_count":92.0,"contact_point_centroid":[0.50376,0.11704,0.05743],"force_p95":67.48844,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":87.22963,"mean_force":32.96866,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50375,0.11567,0.06847]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50008,0.12,0.00774],"force_p95":87.13384,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":87.13384,"mean_force":87.13384,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50428,0.11141,0.06369]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50439,0.1205,0.05339],"force_p95":86.44782,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":86.44782,"mean_force":86.44782,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50428,0.11141,0.06369]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49697,0.11691,0.00772],"force_p95":85.54924,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":85.66605,"mean_force":84.0052,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50425,0.1113,0.06375]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50436,0.12045,0.05341],"force_p95":84.81345,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":84.92159,"mean_force":83.37465,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50425,0.1113,0.06375]},{"body_a":"peg","body_b":"channel_base_body","contact_count":873.0,"contact_point_centroid":[0.50364,0.11165,0.00939],"force_p95":0.60421,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55268,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50441,0.15767,0.21414]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50375,0.20562,0.29956]}],"total_contact_groups":10},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50325,0.10339,0.03386],"final_tcp_position":[0.5011,0.10691,0.14744],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":122.22127,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":895.0,"n_steps_budget":1000.0,"object_pos_end":[0.50367,0.11173,0.03383],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19186,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.58612,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":889.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_object","tcp_end":[0.51548,0.10884,0.14207],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10892,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":824.0,"n_steps_budget":1000.0,"object_pos_end":[0.50367,0.10257,0.0305],"object_pos_start":[0.50367,0.11173,0.03383],"object_to_goal_dist_end":0.18285,"object_to_goal_dist_start":0.19186,"object_z_max":0.03385,"peak_contact_force":74.33359,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1060.0,"raw_peak_contact_force":122.22127,"subtask_id":"reach_object","tcp_end":[0.50428,0.11141,0.06369],"tcp_start":[0.51548,0.10884,0.14207],"tcp_to_object_dist_end":0.03435,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50368,0.10253,0.03051],"object_pos_start":[0.50367,0.10257,0.0305],"object_to_goal_dist_end":0.18281,"object_to_goal_dist_start":0.18285,"object_z_max":0.0305,"peak_contact_force":87.13384,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":87.13384,"subtask_id":"reach_object","tcp_end":[0.50428,0.11136,0.06369],"tcp_start":[0.50428,0.11141,0.06369],"tcp_to_object_dist_end":0.03434,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.5036,0.10248,0.03052],"object_pos_start":[0.50368,0.10253,0.03051],"object_to_goal_dist_end":0.18276,"object_to_goal_dist_start":0.18281,"object_z_max":0.03053,"peak_contact_force":84.49799,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":85.66605,"subtask_id":"push_through_channel","tcp_end":[0.50421,0.1112,0.06387],"tcp_start":[0.50422,0.11124,0.06381],"tcp_to_object_dist_end":0.03448,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":945.0,"n_steps_budget":1000.0,"object_pos_end":[0.50325,0.10339,0.03386],"object_pos_start":[0.5035,0.10241,0.03056],"object_to_goal_dist_end":0.18352,"object_to_goal_dist_start":0.18268,"object_z_max":0.03689,"peak_contact_force":0.54321,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1037.0,"raw_peak_contact_force":87.8773,"tcp_end":[0.5011,0.10691,0.14744],"tcp_start":[0.50421,0.1112,0.06387],"tcp_to_object_dist_end":0.11366,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86598,"average_solve_count":97.0,"average_success_count":97.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00695,"align_1.lateral_offset_y":0.00293,"approach_1.arc_height":0.04424,"approach_1.speed":0.06215,"contact_1.force_threshold":9.21405,"contact_1.speed":0.01763,"push_1.force_guard_threshold":14.34152,"push_1.push_distance":0.15463,"push_1.speed":0.01774,"retract_1.arc_height":0.04504,"retract_1.retract_height":0.09795,"retract_1.speed":0.07107},"optimized_scores":{"best_composite_score":-0.44747,"best_fitness_score":0.04253,"best_task_score":0.04559},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":98.0,"contact_point_centroid":[0.49418,0.19856,-5e-05],"force_p95":110.38821,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":133.33989,"mean_force":94.1197,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49302,0.13642,0.05408]},{"body_a":"world","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.49553,0.19374,-1e-05],"force_p95":106.6551,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":106.9309,"mean_force":104.22401,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4944,0.13133,0.05386]},{"body_a":"world","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.49551,0.19354,-1e-05],"force_p95":92.607,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":99.01961,"mean_force":54.97621,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49437,0.13116,0.05389]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.49554,0.19395,-1e-05],"force_p95":49.82016,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":49.82016,"mean_force":49.82016,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49443,0.13151,0.05381]},{"body_a":"peg","body_b":"channel_base_body","contact_count":819.0,"contact_point_centroid":[0.49612,0.11844,0.00944],"force_p95":0.60586,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.45772,"mean_force":0.61861,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48402,0.14912,0.09677]},{"body_a":"attachment","body_b":"peg","contact_count":31.0,"contact_point_centroid":[0.49661,0.1356,0.05235],"force_p95":11.88805,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.40266,"mean_force":2.21374,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49362,0.13545,0.05397]},{"body_a":"peg","body_b":"channel_base_body","contact_count":777.0,"contact_point_centroid":[0.49618,0.11922,0.00946],"force_p95":0.6,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.54802,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48616,0.16679,0.2167]},{"body_a":"peg","body_b":"channel_base_body","contact_count":632.0,"contact_point_centroid":[0.49462,0.10994,0.00941],"force_p95":0.61587,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.06846,"mean_force":0.54377,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49152,0.14378,0.09191]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.48713,0.09402,0.00928],"force_p95":0.89316,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.89316,"mean_force":0.89316,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49443,0.13151,0.05381]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.48485,0.09535,0.0092],"force_p95":0.8684,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.87413,"mean_force":0.81327,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4944,0.13133,0.05386]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50461,0.21211,0.29589]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47496,0.10758,0.05871],"force_p95":0.48639,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48639,"mean_force":0.48639,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49439,0.13127,0.05387]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":12.0,"contact_point_centroid":[0.47477,0.10759,0.05883],"force_p95":0.30254,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36144,"mean_force":0.08811,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49425,0.13131,0.05394]}],"total_contact_groups":13},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49495,0.11017,0.03379],"final_tcp_position":[0.49132,0.11676,0.12699],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":133.33989,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":802.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11897,0.03389],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.1991,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.53442,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":801.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_object","tcp_end":[0.47795,0.12462,0.14385],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11158,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":827.0,"n_steps_budget":930.0,"object_pos_end":[0.49444,0.10913,0.03438],"object_pos_start":[0.49602,0.11897,0.03389],"object_to_goal_dist_end":0.1893,"object_to_goal_dist_start":0.1991,"object_z_max":0.03604,"peak_contact_force":92.58883,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":948.0,"raw_peak_contact_force":133.33989,"subtask_id":"reach_object","tcp_end":[0.49443,0.13151,0.05381],"tcp_start":[0.47795,0.12462,0.14385],"tcp_to_object_dist_end":0.02963,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49425,0.10902,0.0344],"object_pos_start":[0.49444,0.10913,0.03438],"object_to_goal_dist_end":0.18919,"object_to_goal_dist_start":0.1893,"object_z_max":0.03438,"peak_contact_force":49.82016,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":49.82016,"subtask_id":"reach_object","tcp_end":[0.49441,0.13141,0.05384],"tcp_start":[0.49443,0.13151,0.05381],"tcp_to_object_dist_end":0.02965,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49408,0.10894,0.03444],"object_pos_start":[0.49425,0.10902,0.0344],"object_to_goal_dist_end":0.18911,"object_to_goal_dist_start":0.18919,"object_z_max":0.03449,"peak_contact_force":106.9309,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":7.0,"raw_peak_contact_force":106.9309,"subtask_id":"push_through_channel","tcp_end":[0.49438,0.13122,0.05388],"tcp_start":[0.49439,0.13127,0.05387],"tcp_to_object_dist_end":0.02957,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":632.0,"n_steps_budget":750.0,"object_pos_end":[0.49495,0.11017,0.03379],"object_pos_start":[0.49381,0.10883,0.03455],"object_to_goal_dist_end":0.19033,"object_to_goal_dist_start":0.18901,"object_z_max":0.03489,"peak_contact_force":0.54508,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":648.0,"raw_peak_contact_force":99.01961,"tcp_end":[0.49132,0.11676,0.12699],"tcp_start":[0.49438,0.13122,0.05388],"tcp_to_object_dist_end":0.0935,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```