## Search State

- **Seed**: 4
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.1553 | 0.14 | ❌ rejected |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 8 | -0.1583 | 0.22 | ❌ rejected |
| 1 | approach → contact → insert → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 7 | 0.0133 | 0.31 | ❌ rejected |
| 0 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3038 | 0.61 | ✅ accepted |

**Proposal policy**: task_score is 0.14 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.5354444884457894, -0.07909379577485107, 0.04]
- Frozen task target: [0.5, 0.2, 0.3]
- Goal object position: (0.5, 0.2, 0.3)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5354444884457894, -0.07909379577485107, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5354444884457894, 0.08090620422514894, 0.04)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5354444884457894, 0.08090620422514894, 0.04]
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
  frozen_object_starts: {'peg': [0.5354444884457894, -0.07909379577485107, 0.04]}
  frozen_targets: {'channel_exit': [0.5, 0.2, 0.3]}
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
| `object` | offset from object initial position (0.5354444884457894, -0.07909379577485107, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.2, 0.3) | final destination targets |
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

## Current Skill (Q=-0.155) — your mutation base

```yaml
skill: peg_channel
skill_type: arm_gripper
phases:
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
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
- id: release_1
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
- id: insert_1
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: force_exceeded
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.15
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0

```

## Design Metrics

- **Composite score**: -0.155
- **task_score** (E): 0.139
- **fitness_score**: 0.155  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.560

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.1789 |
| contact_peg | 1.00 | 1.00 | 0.0932 |
| push_through | 1.00 | 1.00 | 0.0560 |
| retract_after_push | 1.00 | 1.00 | 0.0904 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.097, 0.155) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.548 | 3.242 |
| contact_peg | contact | 1.00 / force_exceeded | (0.516, 0.097, 0.155)→(0.504, 0.087, 0.063) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.165 | 1.00 / 2.000 | 21.886 | 21.886 |
| push_through | push | 1.00 / step_budget | (0.504, 0.087, 0.063)→(0.506, 0.034, 0.046) | (0.505, 0.084, 0.034)→(0.499, 0.068, 0.038) | 0.165→0.148 | 1.00 / 3.667 | 211.266 | 279.841 |
| retract_after_push | retract | 1.00 / step_budget | (0.506, 0.034, 0.046)→(0.503, 0.034, 0.137) | (0.499, 0.068, 0.038)→(0.499, 0.045, 0.024) | 0.148→0.126 | 1.00 / 1.000 | 0.642 | 66.014 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.297
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.297
- phase_score: 0.178
- phase_breakdown.approach_contact_score: 0.215
- phase_breakdown.insertion_score: 0.163

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.226
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.297
- **Median Q (composite search score)**: -0.189
- **K-run variance**: 0.0025
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.334


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
{"anchors":[{"name":"object","value":[0.53544,-0.07909,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,-0.07909,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43972,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_height":0.09059,"approach_behind.approach_speed":0.09675,"contact_peg.contact_force_threshold":20.64822,"contact_peg.contact_speed":0.0465,"push_through.push_distance":0.06464,"push_through.push_retry_offset_x":-0.00839,"push_through.push_retry_offset_y":0.00416,"push_through.push_speed":0.05166,"retract_after_push.retract_height":0.13085,"retract_after_push.retract_speed":0.10434},"optimized_scores":{"best_composite_score":-0.18932,"best_fitness_score":0.12068,"best_task_score":0.0515},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":357.0,"contact_point_centroid":[0.52507,0.05254,0.05997],"force_p95":314.23232,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":335.43093,"mean_force":248.04826,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50883,0.05257,0.05281]},{"body_a":"attachment","body_b":"peg","contact_count":456.0,"contact_point_centroid":[0.51714,0.06295,0.053],"force_p95":145.03276,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":163.16707,"mean_force":128.52787,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50892,0.05653,0.054]},{"body_a":"peg","body_b":"channel_base_body","contact_count":456.0,"contact_point_centroid":[0.5086,0.06577,0.00837],"force_p95":141.15602,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":160.98901,"mean_force":125.64263,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50892,0.05653,0.054]},{"body_a":"attachment","body_b":"peg","contact_count":30.0,"contact_point_centroid":[0.50715,0.04641,0.0489],"force_p95":53.55038,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":87.35094,"mean_force":12.45608,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.50408,0.03565,0.04927]},{"body_a":"peg","body_b":"channel_base_body","contact_count":324.0,"contact_point_centroid":[0.49908,0.05858,0.0089],"force_p95":6.90364,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":85.81725,"mean_force":1.56259,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.50225,0.03602,0.10148]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.03631,0.06],"force_p95":70.93298,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":70.93298,"mean_force":70.93298,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.5051,0.03642,0.04576]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":223.0,"contact_point_centroid":[0.47432,0.07704,0.01845],"force_p95":53.01066,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":64.15027,"mean_force":42.27526,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50809,0.0485,0.05122]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":29.0,"contact_point_centroid":[0.47457,0.08389,0.02302],"force_p95":41.03073,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.26149,"mean_force":11.62894,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.50411,0.03566,0.04911]},{"body_a":"peg","body_b":"channel_base_body","contact_count":387.0,"contact_point_centroid":[0.50591,0.08091,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.70783,"mean_force":0.65892,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51797,0.08869,0.10283]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.52021,0.08416,0.05865],"force_p95":25.79485,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.23869,"mean_force":21.80023,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50917,0.0842,0.06321]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":55.0,"contact_point_centroid":[0.52504,0.07231,0.05737],"force_p95":15.98535,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.96229,"mean_force":10.73837,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50992,0.06917,0.05797]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52504,0.02525,0.02489],"force_p95":7.31618,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.37959,"mean_force":5.36206,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.50185,0.0361,0.10584]},{"body_a":"peg","body_b":"channel_base_body","contact_count":351.0,"contact_point_centroid":[0.5056,0.08086,0.00935],"force_p95":0.56712,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.59024,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.51445,0.14378,0.21628]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50047,0.19646,0.29449]}],"total_contact_groups":14},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50119,0.04532,0.02413],"final_tcp_position":[0.50222,0.03616,0.15684],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":335.43093,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":380.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54828,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":387.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach_contact","tcp_end":[0.5287,0.09356,0.14397],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11323,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":387.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03376],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":26.70783,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":389.0,"raw_peak_contact_force":26.70783,"subtask_id":"approach_contact","tcp_end":[0.50912,0.08416,0.06295],"tcp_start":[0.5287,0.09356,0.14397],"tcp_to_object_dist_end":0.02953,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":456.0,"n_steps_budget":900.0,"object_pos_end":[0.49682,0.06933,0.03806],"object_pos_start":[0.50597,0.0809,0.03376],"object_to_goal_dist_end":0.14938,"object_to_goal_dist_start":0.16113,"object_z_max":0.03803,"peak_contact_force":302.28236,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1547.0,"raw_peak_contact_force":335.43093,"subtask_id":"insertion","tcp_end":[0.5051,0.03642,0.04576],"tcp_start":[0.50912,0.08416,0.06295],"tcp_to_object_dist_end":0.0348,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":339.0,"n_steps_budget":810.0,"object_pos_end":[0.50119,0.04532,0.02413],"object_pos_start":[0.49682,0.06933,0.03806],"object_to_goal_dist_end":0.12633,"object_to_goal_dist_start":0.14938,"object_z_max":0.04092,"peak_contact_force":0.53272,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":392.0,"raw_peak_contact_force":87.35094,"subtask_id":"insertion","tcp_end":[0.50222,0.03616,0.15684],"tcp_start":[0.5051,0.03642,0.04576],"tcp_to_object_dist_end":0.13304,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `54762c1e743ba455eff3c9979c2b42f5642abe1893e28eae37dc231d7efcd4e4`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,-0.05536,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,-0.05536,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37879,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_height":0.12322,"approach_behind.approach_speed":0.08686,"contact_peg.contact_force_threshold":7.66011,"contact_peg.contact_speed":0.05501,"push_through.push_distance":0.06543,"push_through.push_retry_offset_x":0.00072,"push_through.push_retry_offset_y":0.00236,"push_through.push_speed":0.05703,"retract_after_push.retract_height":0.11466,"retract_after_push.retract_speed":0.19331},"optimized_scores":{"best_composite_score":-0.19257,"best_fitness_score":0.11743,"best_task_score":0.06943},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":225.0,"contact_point_centroid":[0.52506,0.06927,0.05997],"force_p95":321.84515,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":343.04239,"mean_force":254.79208,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50836,0.06926,0.05167]},{"body_a":"attachment","body_b":"peg","contact_count":359.0,"contact_point_centroid":[0.51558,0.08353,0.05298],"force_p95":154.37202,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":162.37522,"mean_force":124.55631,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.5078,0.07711,0.05392]},{"body_a":"peg","body_b":"channel_base_body","contact_count":359.0,"contact_point_centroid":[0.50821,0.08737,0.00842],"force_p95":153.25283,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":160.85615,"mean_force":122.7055,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.5078,0.07711,0.05392]},{"body_a":"attachment","body_b":"peg","contact_count":26.0,"contact_point_centroid":[0.50724,0.0692,0.0485],"force_p95":53.13671,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.1311,"mean_force":11.54302,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.50454,0.05828,0.04884]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":115.0,"contact_point_centroid":[0.47448,0.10272,0.02018],"force_p95":50.31457,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.82953,"mean_force":38.32062,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50741,0.06551,0.04971]},{"body_a":"peg","body_b":"channel_base_body","contact_count":268.0,"contact_point_centroid":[0.4963,0.08235,0.00887],"force_p95":2.60958,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.35646,"mean_force":1.2303,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.50274,0.05866,0.09395]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":25.0,"contact_point_centroid":[0.47464,0.10742,0.02362],"force_p95":41.77832,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.51049,"mean_force":11.09773,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.50457,0.05828,0.04868]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":150.0,"contact_point_centroid":[0.5251,0.09219,0.0568],"force_p95":22.34979,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.63778,"mean_force":10.01085,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50821,0.08229,0.05581]},{"body_a":"peg","body_b":"channel_base_body","contact_count":568.0,"contact_point_centroid":[0.50585,0.10455,0.00939],"force_p95":0.57562,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.87615,"mean_force":0.58035,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51063,0.11192,0.11899]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51619,0.10694,0.05885],"force_p95":19.44651,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.44651,"mean_force":19.44651,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50514,0.10696,0.06355]},{"body_a":"peg","body_b":"channel_base_body","contact_count":271.0,"contact_point_centroid":[0.50534,0.10477,0.00935],"force_p95":0.61177,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.5881,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50915,0.15619,0.23362]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50021,0.19705,0.29544]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52501,0.05909,0.05999],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.50545,0.05906,0.04604]}],"total_contact_groups":13},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49687,0.07036,0.02414],"final_tcp_position":[0.50261,0.05884,0.14112],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":343.04239,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":298.0,"n_steps_budget":1000.0,"object_pos_end":[0.506,0.10464,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54568,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":303.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach_contact","tcp_end":[0.51846,0.11747,0.17725],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14453,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":568.0,"n_steps_budget":1000.0,"object_pos_end":[0.50588,0.10472,0.03383],"object_pos_start":[0.506,0.10464,0.03383],"object_to_goal_dist_end":0.18491,"object_to_goal_dist_start":0.18484,"object_z_max":0.03384,"peak_contact_force":19.87615,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":569.0,"raw_peak_contact_force":19.87615,"subtask_id":"approach_contact","tcp_end":[0.50514,0.10694,0.06336],"tcp_start":[0.51846,0.11747,0.17725],"tcp_to_object_dist_end":0.02962,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":359.0,"n_steps_budget":810.0,"object_pos_end":[0.49697,0.09286,0.03846],"object_pos_start":[0.50588,0.10472,0.03383],"object_to_goal_dist_end":0.17289,"object_to_goal_dist_start":0.18491,"object_z_max":0.03845,"peak_contact_force":227.91168,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1208.0,"raw_peak_contact_force":343.04239,"subtask_id":"insertion","tcp_end":[0.5055,0.05922,0.04609],"tcp_start":[0.50514,0.10694,0.06336],"tcp_to_object_dist_end":0.03553,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":284.0,"n_steps_budget":600.0,"object_pos_end":[0.49687,0.07036,0.02414],"object_pos_start":[0.49697,0.09286,0.03846],"object_to_goal_dist_end":0.15123,"object_to_goal_dist_start":0.17289,"object_z_max":0.04093,"peak_contact_force":0.62378,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":322.0,"raw_peak_contact_force":59.1311,"subtask_id":"insertion","tcp_end":[0.50261,0.05884,0.14112],"tcp_start":[0.5055,0.05922,0.04609],"tcp_to_object_dist_end":0.11768,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b230a5798f38c3fb8968a6bc74f96ee85fe7026f3170cf8216fc868a1c5c570f`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,-0.09254,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,-0.09254,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44118,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_height":0.08989,"approach_behind.approach_speed":0.17423,"contact_peg.contact_force_threshold":10.84195,"contact_peg.contact_speed":0.03209,"push_through.push_distance":0.076,"push_through.push_retry_offset_x":0.00292,"push_through.push_retry_offset_y":0.00743,"push_through.push_speed":0.04704,"retract_after_push.retract_height":0.08471,"retract_after_push.retract_speed":0.17077},"optimized_scores":{"best_composite_score":-0.08405,"best_fitness_score":0.22595,"best_task_score":0.29721},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":211.0,"contact_point_centroid":[0.5124,0.04676,0.05445],"force_p95":156.81619,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":161.05102,"mean_force":123.43104,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50299,0.04271,0.05649]},{"body_a":"peg","body_b":"channel_base_body","contact_count":211.0,"contact_point_centroid":[0.50967,0.0435,0.00845],"force_p95":157.10588,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":160.54255,"mean_force":124.19886,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50299,0.04271,0.05649]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52501,0.00775,0.06],"force_p95":103.60465,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":103.60465,"mean_force":103.60465,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50624,0.00777,0.0476]},{"body_a":"attachment","body_b":"peg","contact_count":21.0,"contact_point_centroid":[0.50799,0.01705,0.04827],"force_p95":41.55668,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.56111,"mean_force":8.73114,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.50506,0.00613,0.04883]},{"body_a":"peg","body_b":"channel_base_body","contact_count":200.0,"contact_point_centroid":[0.49664,0.03662,0.00927],"force_p95":1.37423,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.47801,"mean_force":1.44845,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.50332,0.00684,0.07852]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":73.0,"contact_point_centroid":[0.5251,0.04403,0.05689],"force_p95":22.91369,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.87776,"mean_force":17.46282,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50562,0.03041,0.05438]},{"body_a":"peg","body_b":"channel_base_body","contact_count":463.0,"contact_point_centroid":[0.50315,0.0674,0.00938],"force_p95":0.5506,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.0744,"mean_force":0.58665,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49779,0.07603,0.10189]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50911,0.07147,0.05874],"force_p95":18.59477,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.59477,"mean_force":18.59477,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.4982,0.0713,0.06365]},{"body_a":"peg","body_b":"channel_base_body","contact_count":343.0,"contact_point_centroid":[0.503,0.06751,0.00931],"force_p95":0.62732,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.57174,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49947,0.13915,0.21837]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":15.0,"contact_point_centroid":[0.47485,0.02207,0.05675],"force_p95":0.35318,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40004,"mean_force":0.1582,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.50319,0.00681,0.06839]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52501,0.00719,0.06],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.5061,0.0072,0.04734]}],"total_contact_groups":11},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49934,0.01991,0.02398],"final_tcp_position":[0.50293,0.00723,0.11244],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":161.05102,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":359.0,"n_steps_budget":780.0,"object_pos_end":[0.50309,0.06748,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14765,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.55056,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":343.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach_contact","tcp_end":[0.50002,0.08129,0.14337],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11048,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":463.0,"n_steps_budget":1000.0,"object_pos_end":[0.50303,0.06742,0.0338],"object_pos_start":[0.50309,0.06748,0.0338],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14765,"object_z_max":0.0338,"peak_contact_force":19.0744,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":464.0,"raw_peak_contact_force":19.0744,"subtask_id":"approach_contact","tcp_end":[0.4982,0.07129,0.0635],"tcp_start":[0.50002,0.08129,0.14337],"tcp_to_object_dist_end":0.03035,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":211.0,"n_steps_budget":1000.0,"object_pos_end":[0.50222,0.0408,0.03851],"object_pos_start":[0.50303,0.06742,0.0338],"object_to_goal_dist_end":0.12083,"object_to_goal_dist_start":0.14758,"object_z_max":0.03846,"peak_contact_force":103.60465,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":496.0,"raw_peak_contact_force":161.05102,"subtask_id":"insertion","tcp_end":[0.50615,0.00737,0.0474],"tcp_start":[0.4982,0.07129,0.0635],"tcp_to_object_dist_end":0.03482,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":206.0,"n_steps_budget":600.0,"object_pos_end":[0.49934,0.01991,0.02398],"object_pos_start":[0.50222,0.0408,0.03851],"object_to_goal_dist_end":0.10119,"object_to_goal_dist_start":0.12083,"object_z_max":0.04042,"peak_contact_force":0.7701,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":238.0,"raw_peak_contact_force":51.56111,"subtask_id":"insertion","tcp_end":[0.50293,0.00723,0.11244],"tcp_start":[0.50615,0.00737,0.0474],"tcp_to_object_dist_end":0.08944,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```