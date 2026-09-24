## Search State

- **Seed**: 4
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.1363 | 0.27 | ❌ rejected |
| 9 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3033 | 0.61 | ❌ rejected |
| 8 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 4 | 0.4253 | 0.01 | ❌ rejected |
| 7 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3046 | 0.60 | ❌ rejected |
| 6 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3035 | 0.61 | ✅ accepted |

**Proposal policy**: task_score is 0.27 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.136) — your mutation base

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

- **Composite score**: 0.136
- **task_score** (E): 0.266
- **fitness_score**: 0.305  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.111
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.2617 |
| push_forward | 0.67 | 1.00 | 0.0361 |
| retract_tcp | 1.00 | 1.00 | 0.0408 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.119, 0.053) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.333 | 136.174 | 168.437 |
| push_forward | push | 0.67 / guard_failure | (0.516, 0.119, 0.053)→(0.515, 0.084, 0.046) | (0.505, 0.084, 0.034)→(0.506, 0.051, 0.036) | 0.165→0.131 | 1.00 / 2.333 | 28.755 | 32.501 |
| retract_tcp | retract | 1.00 / step_budget | (0.515, 0.084, 0.046)→(0.511, 0.084, 0.087) | (0.506, 0.051, 0.036)→(0.503, 0.041, 0.031) | 0.131→0.123 | 1.00 / 1.000 | 0.577 | 38.378 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.788
- alignment_error: None
- force_efficiency: 0.501
- terminal_score: 0.788
- phase_score: 0.691
- phase_breakdown.reach_peg_score: 0.823
- phase_breakdown.push_channel_score: 0.658

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.730
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.788
- **Median Q (composite search score)**: 0.164
- **K-run variance**: 0.0718
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.348


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.10714,"average_solve_count":56.0,"average_success_count":56.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.16437,"push_forward.force_threshold":22.48408,"push_forward.push_distance":0.14532,"push_forward.push_speed":0.03608,"retract_tcp.retract_speed":0.08181},"optimized_scores":{"best_composite_score":-0.20502,"best_fitness_score":0.07498,"best_task_score":9e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":56.0,"contact_point_centroid":[0.54162,0.11831,0.05965],"force_p95":491.35081,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":499.91019,"mean_force":416.3706,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.52975,0.11889,0.06096]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.5424,0.11839,0.05995],"force_p95":60.76422,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":60.92012,"mean_force":57.68102,"phase_index":2.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.53054,0.11883,0.0617]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.54227,0.11838,0.05992],"force_p95":41.75732,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":41.75732,"mean_force":41.75732,"phase_index":1.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.53041,0.11882,0.06164]},{"body_a":"peg","body_b":"channel_base_body","contact_count":750.0,"contact_point_centroid":[0.50576,0.08089,0.00936],"force_p95":0.5521,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.56711,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51492,0.15503,0.1666]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50005,0.19828,0.29526]},{"body_a":"peg","body_b":"channel_base_body","contact_count":457.0,"contact_point_centroid":[0.50601,0.08085,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54677,"phase_index":2.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.52725,0.11808,0.08216]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52106,0.09068,0.00938],"force_p95":0.54458,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54458,"mean_force":0.54458,"phase_index":1.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.53041,0.11882,0.06164]}],"total_contact_groups":7},"final_pose_error":0.01005,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50597,0.08086,0.03378],"final_tcp_position":[0.52697,0.11803,0.10227],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":499.91019,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":779.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":407.42641,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":842.0,"raw_peak_contact_force":499.91019,"subtask_id":"reach_peg","tcp_end":[0.53041,0.11882,0.06164],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":41.75732,"phase_name":"push_forward","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":41.75732,"subtask_id":"push_channel","tcp_end":[0.53048,0.11883,0.06166],"tcp_start":[0.53041,0.11882,0.06164],"tcp_to_object_dist_end":0.05308,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":457.0,"n_steps_budget":600.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":0.54612,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":461.0,"raw_peak_contact_force":60.92012,"tcp_end":[0.52697,0.11803,0.10227],"tcp_start":[0.53048,0.11883,0.06166],"tcp_to_object_dist_end":0.08071,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8209,"average_solve_count":67.0,"average_success_count":67.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.15037,"push_forward.force_threshold":27.91785,"push_forward.push_distance":0.11211,"push_forward.push_speed":0.02769,"retract_tcp.retract_speed":0.11189},"optimized_scores":{"best_composite_score":0.16409,"best_fitness_score":0.11076,"best_task_score":0.00937},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.12,0.06],"force_p95":46.66389,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":46.66389,"mean_force":46.66389,"phase_index":2.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.51505,0.12955,0.04286]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52502,0.11998,0.06],"force_p95":25.86701,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":30.81663,"mean_force":23.81072,"phase_index":1.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.51528,0.12965,0.04295]},{"body_a":"peg","body_b":"channel_base_body","contact_count":114.0,"contact_point_centroid":[0.50183,0.09861,0.00964],"force_p95":3.9121,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.578,"mean_force":0.98764,"phase_index":1.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.51644,0.13208,0.04426]},{"body_a":"attachment","body_b":"peg","contact_count":49.0,"contact_point_centroid":[0.51128,0.11937,0.04398],"force_p95":4.07751,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.07171,"mean_force":1.27085,"phase_index":1.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.51568,0.13045,0.04333]},{"body_a":"peg","body_b":"channel_base_body","contact_count":720.0,"contact_point_centroid":[0.50569,0.10459,0.00937],"force_p95":0.57579,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56205,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50923,0.16718,0.1686]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49989,0.19879,0.29604]},{"body_a":"peg","body_b":"channel_base_body","contact_count":452.0,"contact_point_centroid":[0.5007,0.0944,0.00966],"force_p95":0.59945,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.95011,"mean_force":0.49295,"phase_index":2.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.51171,0.12872,0.06316]},{"body_a":"attachment","body_b":"peg","contact_count":133.0,"contact_point_centroid":[0.50854,0.11738,0.05239],"force_p95":0.41446,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.74976,"mean_force":0.24038,"phase_index":2.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.51206,0.12882,0.05185]}],"total_contact_groups":8},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50347,0.10131,0.03382],"final_tcp_position":[0.51149,0.12865,0.08359],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":46.66389,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":747.0,"n_steps_budget":1000.0,"object_pos_end":[0.50583,0.10467,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18486,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54535,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":752.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_peg","tcp_end":[0.5194,0.13696,0.04806],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.03781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":114.0,"n_steps_budget":1000.0,"object_pos_end":[0.50364,0.10155,0.0348],"object_pos_start":[0.50583,0.10467,0.03384],"object_to_goal_dist_end":0.18166,"object_to_goal_dist_start":0.18486,"object_z_max":0.03494,"peak_contact_force":30.81663,"phase_name":"push_forward","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":195.0,"raw_peak_contact_force":30.81663,"subtask_id":"push_channel","tcp_end":[0.51505,0.12955,0.04286],"tcp_start":[0.5194,0.13696,0.04806],"tcp_to_object_dist_end":0.03129,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":452.0,"n_steps_budget":600.0,"object_pos_end":[0.50347,0.10131,0.03382],"object_pos_start":[0.50364,0.10155,0.0348],"object_to_goal_dist_end":0.18145,"object_to_goal_dist_start":0.18166,"object_z_max":0.03563,"peak_contact_force":0.54251,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":586.0,"raw_peak_contact_force":46.66389,"tcp_end":[0.51149,0.12865,0.08359],"tcp_start":[0.51505,0.12955,0.04286],"tcp_to_object_dist_end":0.05735,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71277,"average_solve_count":94.0,"average_success_count":94.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.155,"push_forward.force_threshold":34.99628,"push_forward.push_distance":0.1223,"push_forward.push_speed":0.05944,"retract_tcp.retract_speed":0.10139},"optimized_scores":{"best_composite_score":0.44974,"best_fitness_score":0.72974,"best_task_score":0.78812},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":926.0,"contact_point_centroid":[0.50155,0.03881,0.03903],"force_p95":21.96132,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.92789,"mean_force":14.23291,"phase_index":1.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.49694,0.0496,0.03898]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.5071,0.01439,0.00989],"force_p95":16.39889,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.36536,"mean_force":10.68512,"phase_index":1.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.49699,0.05205,0.03932]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":857.0,"contact_point_centroid":[0.52516,0.02234,0.02541],"force_p95":11.88742,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.31361,"mean_force":7.52762,"phase_index":1.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.49699,0.04619,0.03864]},{"body_a":"peg","body_b":"channel_base_body","contact_count":389.0,"contact_point_centroid":[0.50101,-0.04684,0.00902],"force_p95":0.95975,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.54925,"mean_force":0.64905,"phase_index":2.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49473,0.00441,0.05516]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.50201,-0.00653,0.03461],"force_p95":4.26925,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.18334,"mean_force":1.11473,"phase_index":2.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49753,0.00438,0.03498]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.52509,-0.03563,0.02326],"force_p95":5.50824,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.72405,"mean_force":1.80628,"phase_index":2.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49483,0.00444,0.05505]},{"body_a":"peg","body_b":"channel_base_body","contact_count":756.0,"contact_point_centroid":[0.50302,0.06746,0.00935],"force_p95":0.55434,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55803,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49888,0.14985,0.17053]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":29.0,"contact_point_centroid":[0.47486,-0.04926,0.05495],"force_p95":0.5317,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.6723,"mean_force":0.19858,"phase_index":2.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49474,0.0044,0.04479]}],"total_contact_groups":8},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50096,-0.05864,0.02416],"final_tcp_position":[0.49444,0.00444,0.07554],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":24.92789,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":772.0,"n_steps_budget":1000.0,"object_pos_end":[0.50306,0.0675,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.55073,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":756.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_peg","tcp_end":[0.49932,0.10171,0.04797],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.03721,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50704,-0.02998,0.0406],"object_pos_start":[0.50306,0.0675,0.0338],"object_to_goal_dist_end":0.05052,"object_to_goal_dist_start":0.14766,"object_z_max":0.04061,"peak_contact_force":13.69215,"phase_name":"push_forward","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2754.0,"raw_peak_contact_force":24.92789,"subtask_id":"push_channel","tcp_end":[0.498,0.00455,0.03481],"tcp_start":[0.49932,0.10171,0.04797],"tcp_to_object_dist_end":0.03616,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":398.0,"n_steps_budget":600.0,"object_pos_end":[0.50096,-0.05864,0.02416],"object_pos_start":[0.50704,-0.02998,0.0406],"object_to_goal_dist_end":0.02661,"object_to_goal_dist_start":0.05052,"object_z_max":0.04078,"peak_contact_force":0.64361,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":446.0,"raw_peak_contact_force":7.54925,"tcp_end":[0.49444,0.00444,0.07554],"tcp_start":[0.498,0.00455,0.03481],"tcp_to_object_dist_end":0.08162,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```