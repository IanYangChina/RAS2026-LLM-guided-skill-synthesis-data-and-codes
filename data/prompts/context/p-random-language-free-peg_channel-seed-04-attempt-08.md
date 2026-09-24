## Search State

- **Seed**: 4
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3046 | 0.61 | ✅ accepted |
| 7 | approach → push | linear_cartesian | impedance_motion | position_control | impedance_control | pose_tolerance | force_exceeded | 4 | 0.1948 | 0.10 | ❌ rejected |
| 6 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 6 | -0.3300 | 0.00 | ❌ rejected |
| 5 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3030 | 0.61 | ✅ accepted |
| 4 | approach → descend → align → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.1542 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.61 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.305) — your mutation base

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

- **Composite score**: 0.305
- **task_score** (E): 0.606
- **fitness_score**: 0.331  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| push_1 | 1.00 | 1.00 | 0.1916 |
| align_1 | 1.00 | 1.00 | 0.1072 |
| release_1 | 1.00 | 1.00 | 0.1728 |
| insert_1 | 1.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| push_1 | push | 1.00 / time_limit | (0.500, 0.200, 0.300)→(0.497, 0.090, 0.143) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.546 | 3.242 |
| align_1 | align | 1.00 / step_budget | (0.497, 0.090, 0.143)→(0.501, 0.121, 0.042) | (0.505, 0.084, 0.034)→(0.505, 0.082, 0.035) | 0.165→0.162 | 1.00 / 1.000 | 0.510 | 58.092 |
| release_1 | release | 1.00 / step_budget | (0.501, 0.121, 0.042)→(0.498, -0.052, 0.037) | (0.505, 0.082, 0.035)→(0.506, -0.081, 0.036) | 0.162→0.010 | 1.00 / 4.000 | 86.098 | 98.325 |
| insert_1 | insert | 1.00 / force_exceeded | (0.498, -0.052, 0.037)→(0.498, -0.052, 0.037) | (0.506, -0.081, 0.036)→(0.506, -0.081, 0.036) | 0.010→0.010 | 1.00 / 4.000 | 92.712 | 92.712 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.971
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.971
- phase_score: 0.190
- phase_breakdown.contact_score: 0.000
- phase_breakdown.push_score: 0.019
- phase_breakdown.approach_score: 0.890

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.502
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.971
- **Median Q (composite search score)**: 0.275
- **K-run variance**: 0.0167
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.296


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89076,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00206,"align_1.lateral_offset_y":-0.0011,"insert_1.insertion_depth":0.05536,"insert_1.insertion_force":9.3989,"push_1.push_distance":0.0861,"push_1.push_speed":0.0729},"optimized_scores":{"best_composite_score":0.16321,"best_fitness_score":0.18987,"best_task_score":0.30953},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":524.0,"contact_point_centroid":[0.54251,-0.00658,0.05999],"force_p95":77.15966,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":86.55825,"mean_force":57.33939,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49774,-0.006,0.03684]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5427,-0.04927,0.05998],"force_p95":81.78861,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":81.78861,"mean_force":81.78861,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49806,-0.05327,0.03664]},{"body_a":"attachment","body_b":"peg","contact_count":852.0,"contact_point_centroid":[0.50384,-0.00163,0.04486],"force_p95":17.80065,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.6871,"mean_force":7.28544,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49769,0.00996,0.03689]},{"body_a":"peg","body_b":"channel_base_body","contact_count":166.0,"contact_point_centroid":[0.50701,-0.1004,0.05811],"force_p95":19.21127,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.53521,"mean_force":15.09356,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49797,-0.05319,0.03665]},{"body_a":"peg","body_b":"channel_base_body","contact_count":629.0,"contact_point_centroid":[0.50582,-0.01347,0.00982],"force_p95":16.13436,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.11716,"mean_force":6.08305,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49774,0.03022,0.03709]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50716,-0.06506,0.05604],"force_p95":13.38455,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.38455,"mean_force":13.38455,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49806,-0.05327,0.03664]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50697,-0.10037,0.06066],"force_p95":13.27224,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.27224,"mean_force":13.27224,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49806,-0.05327,0.03664]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":441.0,"contact_point_centroid":[0.52506,-0.00558,0.02857],"force_p95":5.72078,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.90116,"mean_force":1.42474,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49761,0.02233,0.03685]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.50581,0.08087,0.00937],"force_p95":0.55064,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.56248,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49739,0.1417,0.22254]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49933,0.1983,0.29747]},{"body_a":"peg","body_b":"channel_base_body","contact_count":390.0,"contact_point_centroid":[0.50598,0.08087,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54677,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49777,0.10206,0.09766]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,-0.08271,0.01068],"force_p95":0.0409,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0409,"mean_force":0.0409,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49806,-0.05327,0.03664]}],"total_contact_groups":12},"final_pose_error":0.02701,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50699,-0.08272,0.03567],"final_tcp_position":[0.49806,-0.05327,0.03664],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":86.55825,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.55006,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1007.0,"raw_peak_contact_force":4.32595,"tcp_end":[0.49675,0.08861,0.15497],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12179,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":390.0,"n_steps_budget":810.0,"object_pos_end":[0.50597,0.08089,0.03378],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":0.54527,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":390.0,"raw_peak_contact_force":0.55006,"tcp_end":[0.50105,0.11669,0.04114],"tcp_start":[0.49675,0.08861,0.15497],"tcp_to_object_dist_end":0.03688,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50699,-0.08272,0.03567],"object_pos_start":[0.50597,0.08089,0.03378],"object_to_goal_dist_end":0.00866,"object_to_goal_dist_start":0.16113,"object_z_max":0.03828,"peak_contact_force":73.4976,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2612.0,"raw_peak_contact_force":86.55825,"tcp_end":[0.49806,-0.05327,0.03664],"tcp_start":[0.50105,0.11669,0.04114],"tcp_to_object_dist_end":0.03079,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50699,-0.08272,0.03567],"object_pos_start":[0.50699,-0.08272,0.03567],"object_to_goal_dist_end":0.00866,"object_to_goal_dist_start":0.00866,"object_z_max":0.03567,"peak_contact_force":81.78861,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":81.78861,"tcp_end":[0.49806,-0.05327,0.03664],"tcp_start":[0.49806,-0.05327,0.03664],"tcp_to_object_dist_end":0.03079,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89286,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00026,"align_1.lateral_offset_y":0.00292,"insert_1.insertion_depth":0.14955,"insert_1.insertion_force":8.36594,"push_1.push_distance":0.09995,"push_1.push_speed":0.0954},"optimized_scores":{"best_composite_score":0.27531,"best_fitness_score":0.30198,"best_task_score":0.53827},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":90.0,"contact_point_centroid":[0.51187,0.12669,0.05523],"force_p95":144.83409,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":173.17445,"mean_force":104.75663,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50325,0.13279,0.05693]},{"body_a":"peg","body_b":"channel_base_body","contact_count":431.0,"contact_point_centroid":[0.50682,0.10718,0.00921],"force_p95":142.01269,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":161.0506,"mean_force":22.36463,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49874,0.11296,0.09062]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":318.0,"contact_point_centroid":[0.54284,-0.02265,0.05999],"force_p95":76.36811,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":80.34264,"mean_force":58.24495,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49816,-0.0226,0.03681]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5427,-0.03913,0.05998],"force_p95":78.75244,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.75244,"mean_force":78.75244,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49808,-0.04365,0.03669]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":75.0,"contact_point_centroid":[0.52512,0.11004,0.05175],"force_p95":26.64887,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.68304,"mean_force":10.61195,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50419,0.13463,0.05523]},{"body_a":"peg","body_b":"channel_base_body","contact_count":741.0,"contact_point_centroid":[0.50627,-0.02017,0.00991],"force_p95":13.39184,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.87035,"mean_force":5.15308,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49888,0.02477,0.03724]},{"body_a":"attachment","body_b":"peg","contact_count":899.0,"contact_point_centroid":[0.5036,0.01451,0.04187],"force_p95":13.25227,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.73964,"mean_force":4.08661,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49873,0.02616,0.03706]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":546.0,"contact_point_centroid":[0.52503,-0.00355,0.02592],"force_p95":3.70504,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.85364,"mean_force":0.89161,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49877,0.02497,0.03711]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.50574,0.10468,0.00938],"force_p95":0.57571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.55797,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49736,0.14061,0.21742]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49939,0.19838,0.29762]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.507,-0.08771,0.00999],"force_p95":0.56975,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56975,"mean_force":0.56975,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49808,-0.04365,0.03669]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50319,-0.05532,0.04077],"force_p95":0.51618,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.51618,"mean_force":0.51618,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49808,-0.04365,0.03669]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52501,-0.07094,0.02212],"force_p95":0.41236,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41236,"mean_force":0.41236,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49808,-0.04365,0.03669]}],"total_contact_groups":13},"final_pose_error":0.03655,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50701,-0.07257,0.03681],"final_tcp_position":[0.49808,-0.04365,0.03669],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":173.17445,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.10464,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54104,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1005.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.49672,0.08648,0.14501],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11302,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":431.0,"n_steps_budget":810.0,"object_pos_end":[0.50662,0.0973,0.03638],"object_pos_start":[0.50599,0.10464,0.03384],"object_to_goal_dist_end":0.17746,"object_to_goal_dist_start":0.18484,"object_z_max":0.03618,"peak_contact_force":0.43929,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":596.0,"raw_peak_contact_force":173.17445,"tcp_end":[0.50449,0.14066,0.04281],"tcp_start":[0.49672,0.08648,0.14501],"tcp_to_object_dist_end":0.04388,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50701,-0.07257,0.03681],"object_pos_start":[0.50662,0.0973,0.03638],"object_to_goal_dist_end":0.0107,"object_to_goal_dist_start":0.17746,"object_z_max":0.03866,"peak_contact_force":72.09793,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2504.0,"raw_peak_contact_force":80.34264,"tcp_end":[0.49808,-0.04365,0.03669],"tcp_start":[0.50449,0.14066,0.04281],"tcp_to_object_dist_end":0.03027,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50701,-0.07257,0.03681],"object_pos_start":[0.50701,-0.07257,0.03681],"object_to_goal_dist_end":0.0107,"object_to_goal_dist_start":0.0107,"object_z_max":0.03681,"peak_contact_force":78.75244,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":78.75244,"tcp_end":[0.49808,-0.04365,0.03669],"tcp_start":[0.49808,-0.04365,0.03669],"tcp_to_object_dist_end":0.03027,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88679,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00775,"align_1.lateral_offset_y":0.00778,"insert_1.insertion_depth":0.12912,"insert_1.insertion_force":14.7393,"push_1.push_distance":0.03107,"push_1.push_speed":0.09208},"optimized_scores":{"best_composite_score":0.47536,"best_fitness_score":0.50203,"best_task_score":0.97057},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":490.0,"contact_point_centroid":[0.54207,-0.02558,0.05999],"force_p95":119.51259,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":128.07518,"mean_force":70.88509,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.4973,-0.0258,0.03686]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54357,-0.05521,0.05998],"force_p95":117.59503,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":117.59503,"mean_force":117.59503,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49897,-0.05883,0.0365]},{"body_a":"attachment","body_b":"peg","contact_count":877.0,"contact_point_centroid":[0.50302,-0.01574,0.04458],"force_p95":82.45648,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":102.57498,"mean_force":22.21601,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49669,-0.0044,0.03702]},{"body_a":"peg","body_b":"channel_base_body","contact_count":260.0,"contact_point_centroid":[0.5057,-0.10221,0.05505],"force_p95":84.44689,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":99.00219,"mean_force":60.45193,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49848,-0.05759,0.03658]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50441,-0.07043,0.04781],"force_p95":67.80957,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.80957,"mean_force":67.80957,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49897,-0.05883,0.0365]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50444,-0.10302,0.05991],"force_p95":67.46814,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":67.46814,"mean_force":67.46814,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49897,-0.05883,0.0365]},{"body_a":"peg","body_b":"channel_base_body","contact_count":687.0,"contact_point_centroid":[0.50585,-0.03358,0.00985],"force_p95":16.6443,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.65444,"mean_force":5.83366,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49653,0.00857,0.03727]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":380.0,"contact_point_centroid":[0.52509,-0.00178,0.0229],"force_p95":7.86185,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.14219,"mean_force":1.93279,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49585,0.02453,0.03721]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50307,0.06748,0.00936],"force_p95":0.55225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55539,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49734,0.14591,0.21081]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49978,-0.10495,0.00995],"force_p95":0.63952,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63952,"mean_force":0.63952,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49897,-0.05883,0.0365]},{"body_a":"peg","body_b":"channel_base_body","contact_count":288.0,"contact_point_centroid":[0.50306,0.06745,0.00938],"force_p95":0.55057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55071,"mean_force":0.54665,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49638,0.0997,0.08598]}],"total_contact_groups":11},"final_pose_error":0.02149,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50449,-0.08783,0.03507],"final_tcp_position":[0.49897,-0.05883,0.0365],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":128.07518,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54571,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":984.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.49662,0.09532,0.13],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10037,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":288.0,"n_steps_budget":630.0,"object_pos_end":[0.50307,0.06743,0.0338],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.54572,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":288.0,"raw_peak_contact_force":0.55071,"tcp_end":[0.49824,0.10495,0.04211],"tcp_start":[0.49662,0.09532,0.13],"tcp_to_object_dist_end":0.03874,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50451,-0.08783,0.03506],"object_pos_start":[0.50307,0.06743,0.0338],"object_to_goal_dist_end":0.0103,"object_to_goal_dist_start":0.14759,"object_z_max":0.03822,"peak_contact_force":112.69979,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2694.0,"raw_peak_contact_force":128.07518,"tcp_end":[0.49897,-0.05883,0.0365],"tcp_start":[0.49824,0.10495,0.04211],"tcp_to_object_dist_end":0.02956,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50449,-0.08783,0.03507],"object_pos_start":[0.50451,-0.08783,0.03506],"object_to_goal_dist_end":0.01029,"object_to_goal_dist_start":0.0103,"object_z_max":0.03506,"peak_contact_force":117.59503,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":117.59503,"tcp_end":[0.49897,-0.05883,0.0365],"tcp_start":[0.49897,-0.05883,0.0365],"tcp_to_object_dist_end":0.02956,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```