## Search State

- **Seed**: 8
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.0772 | 0.02 | ❌ rejected |
| 0 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | -0.1933 | 0.18 | ✅ accepted |

**Proposal policy**: task_score is 0.02 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
| `object` | offset from object initial position (0.48615778212844485, 0.11898214746703403, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.48615778212844485, -0.04101785253296597, 0.04) | final destination targets |
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

## Current Skill (Q=0.077) — your mutation base

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
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
- id: contact_1
  type: contact
  generator: impedance_motion
  control: force_threshold_switch
  termination: contact_detected
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
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
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
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: 0.077
- **task_score** (E): 0.024
- **fitness_score**: 0.137  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2166 |
| descend_1 | 1.00 | 1.00 | 0.0386 |
| push_1 | 0.00 | 1.00 | 0.0408 |
| retract_1 | 0.00 | 1.00 | 0.0063 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.109, 0.106) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.532 | 3.526 |
| descend_1 | descend | 1.00 / force_exceeded | (0.513, 0.109, 0.106)→(0.506, 0.098, 0.070) | (0.503, 0.080, 0.034)→(0.503, 0.084, 0.033) | 0.160→0.164 | 1.00 / 2.000 | 347.520 | 346.645 |
| push_1 | push | 0.00 / step_budget | (0.506, 0.098, 0.070)→(0.522, 0.076, 0.083) | (0.503, 0.084, 0.033)→(0.505, 0.073, 0.034) | 0.164→0.153 | 1.00 / 2.667 | 283.054 | 611.884 |
| retract_1 | retract | 0.00 / step_budget | (0.522, 0.076, 0.083)→(0.524, 0.073, 0.079) | (0.505, 0.073, 0.034)→(0.505, 0.073, 0.032) | 0.153→0.153 | 1.00 / 2.333 | 237.019 | 240.794 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.114
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.065
- phase_score: 0.245
- phase_breakdown.reach_goal_score: 0.037
- phase_breakdown.reach_pre_contact_score: 0.730

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.173
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.065
- **Median Q (composite search score)**: 0.061
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.341


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30857,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.07209,"descend_1.contact_force":2.32394,"descend_1.descend_speed":0.0161,"push_1.push_speed":0.01405,"retract_1.retract_speed":0.04989},"optimized_scores":{"best_composite_score":0.11319,"best_fitness_score":0.17319,"best_task_score":0.06544},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":471.0,"contact_point_centroid":[0.45405,0.11993,0.06],"force_p95":275.55065,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":323.11776,"mean_force":224.7402,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48463,0.08101,0.06828]},{"body_a":"peg","body_b":"channel_base_body","contact_count":943.0,"contact_point_centroid":[0.50034,0.09953,0.00923],"force_p95":222.54765,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":242.73203,"mean_force":83.73155,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48262,0.08986,0.07073]},{"body_a":"peg","body_b":"link7","contact_count":939.0,"contact_point_centroid":[0.49409,0.13675,0.04193],"force_p95":226.50577,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":240.50722,"mean_force":94.11476,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48239,0.0905,0.07086]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":999.0,"contact_point_centroid":[0.45577,0.11995,0.05999],"force_p95":193.45207,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":197.54347,"mean_force":178.17393,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48798,0.08183,0.06463]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":473.0,"contact_point_centroid":[0.47499,0.11922,0.05999],"force_p95":125.36627,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":152.44381,"mean_force":106.83227,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4846,0.08117,0.0683]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":580.0,"contact_point_centroid":[0.52545,0.10212,0.02124],"force_p95":69.77448,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":104.31119,"mean_force":31.65628,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48227,0.09091,0.07124]},{"body_a":"peg","body_b":"world","contact_count":270.0,"contact_point_centroid":[0.50372,0.12793,-0.00044],"force_p95":57.0886,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.61368,"mean_force":29.32986,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47749,0.10915,0.07578]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":5.0,"contact_point_centroid":[0.475,0.12,0.06],"force_p95":47.6159,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":48.83528,"mean_force":40.31852,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48667,0.08195,0.06748]},{"body_a":"attachment","body_b":"peg","contact_count":156.0,"contact_point_centroid":[0.48812,0.11643,0.05996],"force_p95":28.79622,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.81807,"mean_force":12.07353,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48288,0.08178,0.06914]},{"body_a":"peg","body_b":"link7","contact_count":969.0,"contact_point_centroid":[0.50625,0.12557,0.04765],"force_p95":0.31178,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.04119,"mean_force":0.27415,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.488,0.08183,0.06459]},{"body_a":"peg","body_b":"channel_base_body","contact_count":990.0,"contact_point_centroid":[0.50681,0.07804,0.00998],"force_p95":0.59251,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.7465,"mean_force":0.50171,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48799,0.08183,0.0646]},{"body_a":"peg","body_b":"channel_base_body","contact_count":360.0,"contact_point_centroid":[0.49629,0.11932,0.00944],"force_p95":0.62506,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55923,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49155,0.17117,0.19936]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49945,0.19885,0.2968]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":55.0,"contact_point_centroid":[0.525,0.0801,0.02822],"force_p95":0.22044,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.754,"mean_force":0.12519,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48862,0.08203,0.06407]},{"body_a":"peg","body_b":"channel_base_body","contact_count":136.0,"contact_point_centroid":[0.49637,0.11992,0.00945],"force_p95":0.57715,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58345,"mean_force":0.52786,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46875,0.14008,0.07127]}],"total_contact_groups":15},"final_pose_error":0.16483,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50221,0.10079,0.02881],"final_tcp_position":[0.48954,0.08235,0.06351],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":323.11776,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":385.0,"n_steps_budget":1000.0,"object_pos_end":[0.49605,0.12009,0.03393],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.20022,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.51253,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":384.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_pre_contact","tcp_end":[0.48479,0.1449,0.10857],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07946,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":136.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.13248,0.03075],"object_pos_start":[0.49605,0.12009,0.03393],"object_to_goal_dist_end":0.21271,"object_to_goal_dist_start":0.20022,"object_z_max":0.03393,"peak_contact_force":3.20764,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":136.0,"raw_peak_contact_force":0.58345,"subtask_id":"reach_pre_contact","tcp_end":[0.47223,0.13687,0.08305],"tcp_start":[0.48479,0.1449,0.10857],"tcp_to_object_dist_end":0.05762,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50246,0.1006,0.03411],"object_pos_start":[0.49602,0.13248,0.03075],"object_to_goal_dist_end":0.18072,"object_to_goal_dist_start":0.21271,"object_z_max":0.03616,"peak_contact_force":323.11776,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3832.0,"raw_peak_contact_force":323.11776,"subtask_id":"reach_goal","tcp_end":[0.48665,0.08196,0.06749],"tcp_start":[0.47223,0.13687,0.08305],"tcp_to_object_dist_end":0.04137,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50221,0.10079,0.02881],"object_pos_start":[0.50246,0.1006,0.03411],"object_to_goal_dist_end":0.18115,"object_to_goal_dist_start":0.18072,"object_z_max":0.03412,"peak_contact_force":195.69783,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3018.0,"raw_peak_contact_force":197.54347,"tcp_end":[0.48954,0.08235,0.06351],"tcp_start":[0.48665,0.08196,0.06749],"tcp_to_object_dist_end":0.04128,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.22941,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06706,"descend_1.contact_force":7.67168,"descend_1.descend_speed":0.01987,"push_1.push_speed":0.03276,"retract_1.retract_speed":0.05119},"optimized_scores":{"best_composite_score":0.06107,"best_fitness_score":0.12107,"best_task_score":0.00525},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":15.0,"contact_point_centroid":[0.52654,0.08582,0.05915],"force_p95":676.11905,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":746.21839,"mean_force":397.01066,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51632,0.08327,0.06249]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":967.0,"contact_point_centroid":[0.53095,0.11993,0.05992],"force_p95":304.85034,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":729.51601,"mean_force":275.60873,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5315,0.07572,0.08762]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.53051,0.08697,0.05998],"force_p95":512.70746,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":512.70746,"mean_force":512.70746,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52112,0.08208,0.06562]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":998.0,"contact_point_centroid":[0.52616,0.11996,0.05996],"force_p95":244.5769,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":256.31424,"mean_force":194.70103,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53499,0.07302,0.08624]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50516,0.06043,0.00937],"force_p95":0.55701,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":200.35071,"mean_force":1.27832,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53095,0.07591,0.08686]},{"body_a":"attachment","body_b":"peg","contact_count":17.0,"contact_point_centroid":[0.51338,0.07651,0.05733],"force_p95":194.1838,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":200.20844,"mean_force":43.19771,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50786,0.07883,0.05696]},{"body_a":"peg","body_b":"channel_base_body","contact_count":422.0,"contact_point_centroid":[0.5057,0.06293,0.00935],"force_p95":0.58052,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.57861,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51155,0.14466,0.19731]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5001,0.19737,0.29505]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50519,0.06079,0.00939],"force_p95":0.55109,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55487,"mean_force":0.54626,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53499,0.07303,0.08625]},{"body_a":"peg","body_b":"channel_base_body","contact_count":28.0,"contact_point_centroid":[0.5064,0.06424,0.00938],"force_p95":0.55058,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55118,"mean_force":0.5467,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52739,0.08484,0.08856]}],"total_contact_groups":10},"final_pose_error":0.15651,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50536,0.06075,0.03387],"final_tcp_position":[0.53643,0.07214,0.08537],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":746.21839,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":450.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,0.06298,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14324,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54913,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":456.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_pre_contact","tcp_end":[0.52354,0.09395,0.1055],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08006,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":28.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.06294,0.03381],"object_pos_start":[0.50594,0.06298,0.03381],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14324,"object_z_max":0.03381,"peak_contact_force":512.70746,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":29.0,"raw_peak_contact_force":512.70746,"subtask_id":"reach_pre_contact","tcp_end":[0.52017,0.08233,0.06435],"tcp_start":[0.52354,0.09395,0.1055],"tcp_to_object_dist_end":0.03886,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50518,0.06064,0.03387],"object_pos_start":[0.50599,0.06294,0.03381],"object_to_goal_dist_end":0.14086,"object_to_goal_dist_start":0.1432,"object_z_max":0.0339,"peak_contact_force":263.4131,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1999.0,"raw_peak_contact_force":746.21839,"subtask_id":"reach_goal","tcp_end":[0.53439,0.07651,0.08818],"tcp_start":[0.52017,0.08233,0.06435],"tcp_to_object_dist_end":0.06368,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50536,0.06075,0.03387],"object_pos_start":[0.50518,0.06064,0.03387],"object_to_goal_dist_end":0.14098,"object_to_goal_dist_start":0.14086,"object_z_max":0.03387,"peak_contact_force":246.83465,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1998.0,"raw_peak_contact_force":256.31424,"tcp_end":[0.53643,0.07214,0.08537],"tcp_start":[0.53439,0.07651,0.08818],"tcp_to_object_dist_end":0.06122,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.01878,"average_solve_count":213.0,"average_success_count":213.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.0126,"descend_1.contact_force":6.05294,"descend_1.descend_speed":0.01195,"push_1.push_speed":0.04315,"retract_1.retract_speed":0.04495},"optimized_scores":{"best_composite_score":0.05747,"best_fitness_score":0.11747,"best_task_score":8e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":40.0,"contact_point_centroid":[0.52897,0.07802,0.05905],"force_p95":593.1134,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":766.31465,"mean_force":354.61136,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52402,0.07163,0.06643]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.53677,0.07959,0.05965],"force_p95":526.64559,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":526.64559,"mean_force":526.64559,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52736,0.07464,0.06486]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":946.0,"contact_point_centroid":[0.53633,0.11995,0.05995],"force_p95":291.15422,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":452.60343,"mean_force":266.07684,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54107,0.06939,0.09381]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":998.0,"contact_point_centroid":[0.52707,0.11996,0.05996],"force_p95":267.45676,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":268.52369,"mean_force":204.7962,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54403,0.0662,0.09093]},{"body_a":"peg","body_b":"channel_base_body","contact_count":444.0,"contact_point_centroid":[0.50585,0.05662,0.00935],"force_p95":0.6014,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.58239,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51469,0.14174,0.1973]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50015,0.19733,0.29511]},{"body_a":"peg","body_b":"channel_base_body","contact_count":28.0,"contact_point_centroid":[0.50614,0.05687,0.00938],"force_p95":0.57407,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57608,"mean_force":0.54631,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53363,0.07814,0.088]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50612,0.05664,0.00938],"force_p95":0.55441,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57045,"mean_force":0.5466,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54018,0.06949,0.09242]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50615,0.05655,0.00939],"force_p95":0.55316,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55517,"mean_force":0.54647,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54403,0.0662,0.09094]}],"total_contact_groups":9},"final_pose_error":0.15195,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50607,0.05657,0.03383],"final_tcp_position":[0.546,0.06481,0.088],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":766.31465,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":473.0,"n_steps_budget":1000.0,"object_pos_end":[0.50614,0.0566,0.03377],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.53374,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":481.0,"raw_peak_contact_force":4.44541,"subtask_id":"reach_pre_contact","tcp_end":[0.52977,0.08797,0.10489],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08124,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":28.0,"n_steps_budget":1000.0,"object_pos_end":[0.50614,0.0566,0.03378],"object_pos_start":[0.50614,0.0566,0.03377],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.13688,"object_z_max":0.03378,"peak_contact_force":526.64559,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":29.0,"raw_peak_contact_force":526.64559,"subtask_id":"reach_pre_contact","tcp_end":[0.52641,0.07486,0.06358],"tcp_start":[0.52977,0.08797,0.10489],"tcp_to_object_dist_end":0.0404,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50619,0.05658,0.03382],"object_pos_start":[0.50614,0.0566,0.03378],"object_to_goal_dist_end":0.13686,"object_to_goal_dist_start":0.13688,"object_z_max":0.03382,"peak_contact_force":262.63178,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1986.0,"raw_peak_contact_force":766.31465,"subtask_id":"reach_goal","tcp_end":[0.54379,0.07038,0.09387],"tcp_start":[0.52641,0.07486,0.06358],"tcp_to_object_dist_end":0.07218,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50607,0.05657,0.03383],"object_pos_start":[0.50619,0.05658,0.03382],"object_to_goal_dist_end":0.13684,"object_to_goal_dist_start":0.13686,"object_z_max":0.03383,"peak_contact_force":268.52369,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1998.0,"raw_peak_contact_force":268.52369,"tcp_end":[0.546,0.06481,0.088],"tcp_start":[0.54379,0.07038,0.09387],"tcp_to_object_dist_end":0.0678,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```