## Search State

- **Seed**: 4
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3046 | 0.60 | ❌ rejected |
| 6 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3035 | 0.61 | ✅ accepted |
| 5 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | -0.2877 | 0.00 | ❌ rejected |
| 4 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2053 | 0.07 | ❌ rejected |
| 3 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3041 | 0.61 | ✅ accepted |

**Proposal policy**: task_score is 0.60 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- **task_score** (E): 0.604
- **fitness_score**: 0.331  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| push_1 | 1.00 | 1.00 | 0.1949 |
| align_1 | 1.00 | 1.00 | 0.1033 |
| release_1 | 1.00 | 1.00 | 0.1733 |
| insert_1 | 1.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| push_1 | push | 1.00 / time_limit | (0.500, 0.200, 0.300)→(0.497, 0.090, 0.139) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.544 | 3.242 |
| align_1 | align | 1.00 / step_budget | (0.497, 0.090, 0.139)→(0.502, 0.121, 0.042) | (0.505, 0.084, 0.034)→(0.505, 0.082, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.593 | 62.714 |
| release_1 | release | 1.00 / step_budget | (0.502, 0.121, 0.042)→(0.498, -0.052, 0.037) | (0.505, 0.082, 0.034)→(0.506, -0.081, 0.036) | 0.162→0.009 | 1.00 / 3.333 | 85.569 | 96.234 |
| insert_1 | insert | 1.00 / force_exceeded | (0.498, -0.052, 0.037)→(0.498, -0.052, 0.037) | (0.506, -0.081, 0.036)→(0.506, -0.081, 0.036) | 0.009→0.009 | 1.00 / 3.333 | 92.136 | 92.136 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.969
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.969
- phase_score: 0.189
- phase_breakdown.contact_score: 0.000
- phase_breakdown.push_score: 0.019
- phase_breakdown.approach_score: 0.890

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.501
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.969
- **Median Q (composite search score)**: 0.276
- **K-run variance**: 0.0165
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.350


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88785,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00384,"align_1.lateral_offset_y":-0.00209,"insert_1.insertion_depth":0.02382,"insert_1.insertion_force":9.43591,"push_1.push_distance":0.07374,"push_1.push_speed":0.09469},"optimized_scores":{"best_composite_score":0.16373,"best_fitness_score":0.1904,"best_task_score":0.30887},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":527.0,"contact_point_centroid":[0.54249,-0.00553,0.05999],"force_p95":79.48926,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":85.20883,"mean_force":58.21807,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49772,-0.00494,0.03684]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54263,-0.04915,0.05998],"force_p95":81.37865,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":81.37865,"mean_force":81.37865,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49799,-0.05315,0.03665]},{"body_a":"attachment","body_b":"peg","contact_count":878.0,"contact_point_centroid":[0.50376,0.00149,0.04468],"force_p95":16.21,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.10514,"mean_force":6.79821,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.4977,0.01312,0.03691]},{"body_a":"peg","body_b":"channel_base_body","contact_count":163.0,"contact_point_centroid":[0.50707,-0.10035,0.05873],"force_p95":16.43973,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.80272,"mean_force":12.66888,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49791,-0.0531,0.03665]},{"body_a":"peg","body_b":"channel_base_body","contact_count":622.0,"contact_point_centroid":[0.50564,-0.01442,0.00986],"force_p95":15.71944,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.9289,"mean_force":6.57942,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49776,0.0293,0.0371]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50709,-0.06497,0.05599],"force_p95":11.57885,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.57885,"mean_force":11.57885,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49799,-0.05315,0.03665]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50696,-0.10034,0.06121],"force_p95":11.49163,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.49163,"mean_force":11.49163,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49799,-0.05315,0.03665]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":378.0,"contact_point_centroid":[0.52506,-0.01998,0.02493],"force_p95":4.41451,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.56702,"mean_force":1.068,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49767,0.00744,0.03684]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.50581,0.08087,0.00937],"force_p95":0.55064,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.56248,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49735,0.14089,0.21678]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49934,0.19819,0.29721]},{"body_a":"peg","body_b":"channel_base_body","contact_count":360.0,"contact_point_centroid":[0.50598,0.08087,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54677,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49768,0.10099,0.09205]}],"total_contact_groups":11},"final_pose_error":0.02713,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50695,-0.08265,0.03623],"final_tcp_position":[0.49799,-0.05315,0.03665],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":85.20883,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54527,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1007.0,"raw_peak_contact_force":4.32595,"tcp_end":[0.49669,0.08705,0.14386],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11065,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":360.0,"n_steps_budget":750.0,"object_pos_end":[0.50597,0.08089,0.03378],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":0.54527,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":360.0,"raw_peak_contact_force":0.55006,"tcp_end":[0.50096,0.11622,0.04104],"tcp_start":[0.49669,0.08705,0.14386],"tcp_to_object_dist_end":0.03641,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50695,-0.08264,0.03624],"object_pos_start":[0.50597,0.08089,0.03378],"object_to_goal_dist_end":0.00833,"object_to_goal_dist_start":0.16113,"object_z_max":0.0372,"peak_contact_force":74.65875,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2568.0,"raw_peak_contact_force":85.20883,"tcp_end":[0.49799,-0.05315,0.03665],"tcp_start":[0.50096,0.11622,0.04104],"tcp_to_object_dist_end":0.03082,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50695,-0.08265,0.03623],"object_pos_start":[0.50695,-0.08264,0.03624],"object_to_goal_dist_end":0.00833,"object_to_goal_dist_start":0.00833,"object_z_max":0.03624,"peak_contact_force":81.37865,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":81.37865,"tcp_end":[0.49799,-0.05315,0.03665],"tcp_start":[0.49799,-0.05315,0.03665],"tcp_to_object_dist_end":0.03083,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88991,"average_solve_count":109.0,"average_success_count":109.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00571,"align_1.lateral_offset_y":-0.00474,"insert_1.insertion_depth":0.07561,"insert_1.insertion_force":1.43215,"push_1.push_distance":0.074,"push_1.push_speed":0.09717},"optimized_scores":{"best_composite_score":0.27583,"best_fitness_score":0.30249,"best_task_score":0.53541},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":105.0,"contact_point_centroid":[0.51229,0.12799,0.0546],"force_p95":159.91921,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":187.04045,"mean_force":112.24475,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50345,0.13369,0.05624]},{"body_a":"peg","body_b":"channel_base_body","contact_count":388.0,"contact_point_centroid":[0.50729,0.10844,0.00915],"force_p95":145.67286,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":177.189,"mean_force":30.87656,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49898,0.11665,0.08353]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54275,-0.04038,0.05998],"force_p95":78.93634,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.93634,"mean_force":78.93634,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49812,-0.04483,0.03668]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":294.0,"contact_point_centroid":[0.54286,-0.02761,0.05999],"force_p95":75.93866,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":76.24563,"mean_force":59.15381,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.4982,-0.02788,0.03679]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":91.0,"contact_point_centroid":[0.52514,0.11151,0.05207],"force_p95":31.6738,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.44195,"mean_force":13.01671,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5045,0.13576,0.05453]},{"body_a":"attachment","body_b":"peg","contact_count":860.0,"contact_point_centroid":[0.50364,0.01124,0.04167],"force_p95":13.49387,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.30901,"mean_force":3.72253,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49893,0.02291,0.03713]},{"body_a":"peg","body_b":"channel_base_body","contact_count":732.0,"contact_point_centroid":[0.50586,-0.01862,0.00988],"force_p95":14.05766,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.75315,"mean_force":4.70381,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.4992,0.02614,0.03738]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":433.0,"contact_point_centroid":[0.52506,-0.00628,0.02055],"force_p95":3.29403,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.56592,"mean_force":0.8075,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49904,0.02263,0.03727]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.50574,0.10468,0.00938],"force_p95":0.57571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.55797,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49732,0.14391,0.21057]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4994,0.19846,0.2975]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50631,-0.08942,0.00999],"force_p95":0.61285,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61285,"mean_force":0.61285,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49812,-0.04483,0.03668]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50367,-0.05662,0.0427],"force_p95":0.29587,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29587,"mean_force":0.29587,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49812,-0.04483,0.03668]}],"total_contact_groups":12},"final_pose_error":0.03537,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50691,-0.07383,0.03654],"final_tcp_position":[0.49813,-0.04483,0.03668],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":187.04045,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.10464,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54104,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1005.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.49659,0.09261,0.13146],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09881,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":388.0,"n_steps_budget":720.0,"object_pos_end":[0.50471,0.09846,0.03551],"object_pos_start":[0.50599,0.10464,0.03384],"object_to_goal_dist_end":0.17858,"object_to_goal_dist_start":0.18484,"object_z_max":0.03529,"peak_contact_force":0.68967,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":584.0,"raw_peak_contact_force":187.04045,"tcp_end":[0.50525,0.14206,0.04323],"tcp_start":[0.49659,0.09261,0.13146],"tcp_to_object_dist_end":0.04428,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5069,-0.07383,0.03654],"object_pos_start":[0.50471,0.09846,0.03551],"object_to_goal_dist_end":0.00989,"object_to_goal_dist_start":0.17858,"object_z_max":0.04004,"peak_contact_force":72.07615,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2319.0,"raw_peak_contact_force":76.24563,"tcp_end":[0.49812,-0.04483,0.03668],"tcp_start":[0.50525,0.14206,0.04323],"tcp_to_object_dist_end":0.0303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50691,-0.07383,0.03654],"object_pos_start":[0.5069,-0.07383,0.03654],"object_to_goal_dist_end":0.00989,"object_to_goal_dist_start":0.00989,"object_z_max":0.03654,"peak_contact_force":78.93634,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":78.93634,"tcp_end":[0.49813,-0.04483,0.03668],"tcp_start":[0.49812,-0.04483,0.03668],"tcp_to_object_dist_end":0.0303,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88991,"average_solve_count":109.0,"average_success_count":109.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00426,"align_1.lateral_offset_y":-0.00024,"insert_1.insertion_depth":0.09237,"insert_1.insertion_force":6.36736,"push_1.push_distance":0.05251,"push_1.push_speed":0.0859},"optimized_scores":{"best_composite_score":0.47431,"best_fitness_score":0.50097,"best_task_score":0.96851},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":514.0,"contact_point_centroid":[0.54205,-0.02309,0.05999],"force_p95":117.14575,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":127.2469,"mean_force":69.24589,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49729,-0.02312,0.03686]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54355,-0.05504,0.05998],"force_p95":116.09157,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":116.09157,"mean_force":116.09157,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49895,-0.05867,0.0365]},{"body_a":"attachment","body_b":"peg","contact_count":868.0,"contact_point_centroid":[0.50303,-0.01394,0.0447],"force_p95":81.17205,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":108.48874,"mean_force":21.48911,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49674,-0.00258,0.037]},{"body_a":"peg","body_b":"channel_base_body","contact_count":259.0,"contact_point_centroid":[0.50584,-0.10212,0.05521],"force_p95":82.88107,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":100.49104,"mean_force":59.30882,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49847,-0.0575,0.03658]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50505,-0.07017,0.04948],"force_p95":68.75439,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.75439,"mean_force":68.75439,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49895,-0.05867,0.0365]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50498,-0.10282,0.05994],"force_p95":68.17254,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":68.17254,"mean_force":68.17254,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49895,-0.05867,0.0365]},{"body_a":"peg","body_b":"channel_base_body","contact_count":647.0,"contact_point_centroid":[0.50638,-0.03015,0.00981],"force_p95":17.14635,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.22461,"mean_force":5.66308,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49651,0.01137,0.03726]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":367.0,"contact_point_centroid":[0.52511,-0.00351,0.02392],"force_p95":5.48114,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.63074,"mean_force":1.57147,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49597,0.02313,0.03715]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50307,0.06748,0.00936],"force_p95":0.55225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55539,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49737,0.14341,0.21708]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50456,-0.10526,0.00997],"force_p95":1.15415,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.15415,"mean_force":1.15415,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49895,-0.05867,0.0365]},{"body_a":"peg","body_b":"channel_base_body","contact_count":329.0,"contact_point_centroid":[0.50295,0.06733,0.00938],"force_p95":0.55057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55071,"mean_force":0.54664,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49644,0.09703,0.09194]}],"total_contact_groups":11},"final_pose_error":0.02164,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50496,-0.0875,0.03506],"final_tcp_position":[0.49895,-0.05867,0.0365],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":127.2469,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54571,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":984.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.49667,0.09042,0.14225],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11105,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":329.0,"n_steps_budget":690.0,"object_pos_end":[0.50303,0.0675,0.0338],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.54556,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":329.0,"raw_peak_contact_force":0.55071,"tcp_end":[0.49838,0.10458,0.04192],"tcp_start":[0.49667,0.09042,0.14225],"tcp_to_object_dist_end":0.03824,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50497,-0.08749,0.03505],"object_pos_start":[0.50303,0.0675,0.0338],"object_to_goal_dist_end":0.01027,"object_to_goal_dist_start":0.14766,"object_z_max":0.03835,"peak_contact_force":109.97146,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2655.0,"raw_peak_contact_force":127.2469,"tcp_end":[0.49895,-0.05867,0.0365],"tcp_start":[0.49838,0.10458,0.04192],"tcp_to_object_dist_end":0.02948,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50496,-0.0875,0.03506],"object_pos_start":[0.50497,-0.08749,0.03505],"object_to_goal_dist_end":0.01026,"object_to_goal_dist_start":0.01027,"object_z_max":0.03505,"peak_contact_force":116.09157,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":116.09157,"tcp_end":[0.49895,-0.05867,0.0365],"tcp_start":[0.49895,-0.05867,0.0365],"tcp_to_object_dist_end":0.02949,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```