## Search State

- **Seed**: 4
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | -0.4374 | 0.00 | ❌ rejected |
| 2 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | -0.4455 | 0.20 | ❌ rejected |
| 1 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | -0.0888 | 0.41 | ❌ rejected |
| 0 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.2470 | 0.45 | ✅ accepted |

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

## Current Skill (Q=-0.437) — your mutation base

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

- **Composite score**: -0.437
- **task_score** (E): 0.002
- **fitness_score**: 0.036  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.067
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1427 |
| descend_1 | 1.00 | 1.00 | 0.1087 |
| contact_1 | 0.33 | 1.00 | 0.0333 |
| push_1 | 0.00 | 1.00 | 0.0009 |
| retract_1 | 1.00 | 1.00 | 0.1048 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.100, 0.200) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.545 | 3.242 |
| descend_1 | descend | 1.00 / step_budget | (0.516, 0.100, 0.200)→(0.504, 0.089, 0.093) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.165 | 1.00 / 1.000 | 0.545 | 0.562 |
| contact_1 | contact | 0.33 / guard_failure | (0.504, 0.089, 0.093)→(0.501, 0.085, 0.061) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.164 | 1.00 / 2.000 | 12.627 | 12.346 |
| push_1 | push | 0.00 / guard_failure | (0.501, 0.085, 0.061)→(0.501, 0.084, 0.060) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.164→0.164 | 1.00 / 2.000 | 31.530 | 31.530 |
| retract_1 | retract | 1.00 / step_budget | (0.501, 0.084, 0.060)→(0.501, 0.088, 0.165) | (0.505, 0.084, 0.034)→(0.504, 0.084, 0.034) | 0.164→0.164 | 1.00 / 1.000 | 0.542 | 32.444 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.003
- alignment_error: None
- force_efficiency: 0.336
- terminal_score: 0.001
- phase_score: 0.055
- phase_breakdown.pre_insert_alignment_score: 0.180
- phase_breakdown.channel_insertion_score: 0.001

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.039
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.003
- **Median Q (composite search score)**: -0.501
- **K-run variance**: 0.0085
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.307


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.19565,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.16693,"contact_1.contact_speed":0.01569,"contact_1.force_threshold":1.34546,"descend_1.descend_speed":0.06695,"descend_1.y_offset":-0.00044,"push_1.max_time":6.11598,"push_1.push_distance":0.14816,"push_1.push_speed":0.07596,"retract_1.retract_speed":0.09918},"optimized_scores":{"best_composite_score":-0.30665,"best_fitness_score":0.03335,"best_task_score":0.00097},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":7.0,"contact_point_centroid":[0.49436,0.07306,0.00931],"force_p95":32.22234,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.21006,"mean_force":18.03047,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50249,0.08076,0.06037]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.51433,0.08057,0.05863],"force_p95":31.75428,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.75557,"mean_force":17.52151,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50249,0.08076,0.06037]},{"body_a":"peg","body_b":"channel_base_body","contact_count":326.0,"contact_point_centroid":[0.50518,0.0806,0.00942],"force_p95":0.57513,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.7319,"mean_force":0.73745,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50104,0.08821,0.11106]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.51363,0.08072,0.05882],"force_p95":22.6091,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.27753,"mean_force":5.83056,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5018,0.08036,0.06044]},{"body_a":"peg","body_b":"channel_base_body","contact_count":253.0,"contact_point_centroid":[0.50539,0.08096,0.00933],"force_p95":0.62146,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.60707,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51479,0.14409,0.24433]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50094,0.19513,0.29484]},{"body_a":"peg","body_b":"channel_base_body","contact_count":210.0,"contact_point_centroid":[0.50598,0.08087,0.00938],"force_p95":0.5501,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55048,"mean_force":0.54677,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51788,0.08976,0.14765]},{"body_a":"peg","body_b":"channel_base_body","contact_count":186.0,"contact_point_centroid":[0.50598,0.08087,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55008,"mean_force":0.54677,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50397,0.08179,0.07626]}],"total_contact_groups":8},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5055,0.08036,0.03411],"final_tcp_position":[0.50248,0.08445,0.16458],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":33.21006,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":282.0,"n_steps_budget":630.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.5443,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":289.0,"raw_peak_contact_force":4.32595,"subtask_id":"pre_insert_alignment","tcp_end":[0.52838,0.0965,0.19952],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16797,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":210.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":0.54455,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":210.0,"raw_peak_contact_force":0.55048,"subtask_id":"pre_insert_alignment","tcp_end":[0.50734,0.08301,0.0933],"tcp_start":[0.52838,0.0965,0.19952],"tcp_to_object_dist_end":0.05958,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":186.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":1.39306,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":186.0,"raw_peak_contact_force":0.55008,"subtask_id":"pre_insert_alignment","tcp_end":[0.50271,0.0809,0.06066],"tcp_start":[0.50734,0.08301,0.0933],"tcp_to_object_dist_end":0.02709,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.50562,0.08065,0.03379],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.16086,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":33.21006,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":14.0,"raw_peak_contact_force":33.21006,"subtask_id":"channel_insertion","tcp_end":[0.50228,0.08043,0.06009],"tcp_start":[0.50271,0.0809,0.06066],"tcp_to_object_dist_end":0.02652,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":326.0,"n_steps_budget":780.0,"object_pos_end":[0.5055,0.08036,0.03411],"object_pos_start":[0.50562,0.08065,0.03379],"object_to_goal_dist_end":0.16057,"object_to_goal_dist_start":0.16086,"object_z_max":0.03449,"peak_contact_force":0.53856,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":337.0,"raw_peak_contact_force":28.7319,"tcp_end":[0.50248,0.08445,0.16458],"tcp_start":[0.50228,0.08043,0.06009],"tcp_to_object_dist_end":0.13057,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.91908,"average_solve_count":173.0,"average_success_count":173.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.20859,"contact_1.contact_speed":0.01099,"contact_1.force_threshold":4.24321,"descend_1.descend_speed":0.05269,"descend_1.y_offset":-0.00108,"push_1.max_time":5.52138,"push_1.push_distance":0.0983,"push_1.push_speed":0.03367,"retract_1.retract_speed":0.08889},"optimized_scores":{"best_composite_score":-0.50418,"best_fitness_score":0.03582,"best_task_score":0.00164},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":335.0,"contact_point_centroid":[0.50492,0.10427,0.00942],"force_p95":0.60597,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.19738,"mean_force":0.77824,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50056,0.11158,0.11091]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.51304,0.10393,0.0588],"force_p95":31.20537,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.75959,"mean_force":7.18958,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50121,0.10363,0.06029]},{"body_a":"peg","body_b":"channel_base_body","contact_count":10.0,"contact_point_centroid":[0.49096,0.0963,0.00938],"force_p95":29.83244,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.08087,"mean_force":23.34266,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50182,0.10412,0.06024]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.51366,0.10407,0.05866],"force_p95":29.37084,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.63045,"mean_force":22.87097,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50182,0.10412,0.06024]},{"body_a":"peg","body_b":"channel_base_body","contact_count":192.0,"contact_point_centroid":[0.50611,0.10479,0.00939],"force_p95":0.57562,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.9507,"mean_force":0.64212,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5026,0.1049,0.07628]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51388,0.10445,0.05883],"force_p95":18.43149,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.43149,"mean_force":18.43149,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50203,0.1043,0.06071]},{"body_a":"peg","body_b":"channel_base_body","contact_count":215.0,"contact_point_centroid":[0.50506,0.10457,0.00935],"force_p95":0.67266,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.59899,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50948,0.15631,0.24591]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50053,0.19622,0.29519]},{"body_a":"peg","body_b":"channel_base_body","contact_count":219.0,"contact_point_centroid":[0.50603,0.10455,0.00939],"force_p95":0.575,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57958,"mean_force":0.54632,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51166,0.11258,0.14914]}],"total_contact_groups":9},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50534,0.1041,0.03403],"final_tcp_position":[0.50222,0.10793,0.16483],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":33.19738,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":242.0,"n_steps_budget":600.0,"object_pos_end":[0.50589,0.10473,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18493,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54214,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":247.0,"raw_peak_contact_force":3.33087,"subtask_id":"pre_insert_alignment","tcp_end":[0.51843,0.11922,0.20229],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16954,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":219.0,"n_steps_budget":1000.0,"object_pos_end":[0.50583,0.10467,0.03384],"object_pos_start":[0.50589,0.10473,0.03383],"object_to_goal_dist_end":0.18486,"object_to_goal_dist_start":0.18493,"object_z_max":0.03384,"peak_contact_force":0.54522,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":219.0,"raw_peak_contact_force":0.57958,"subtask_id":"pre_insert_alignment","tcp_end":[0.50539,0.10597,0.09347],"tcp_start":[0.51843,0.11922,0.20229],"tcp_to_object_dist_end":0.05965,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":192.0,"n_steps_budget":1000.0,"object_pos_end":[0.50589,0.10456,0.03383],"object_pos_start":[0.50583,0.10467,0.03384],"object_to_goal_dist_end":0.18475,"object_to_goal_dist_start":0.18486,"object_z_max":0.03384,"peak_contact_force":18.9507,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":193.0,"raw_peak_contact_force":18.9507,"subtask_id":"pre_insert_alignment","tcp_end":[0.50204,0.1043,0.06056],"tcp_start":[0.50539,0.10597,0.09347],"tcp_to_object_dist_end":0.02701,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":10.0,"n_steps_budget":1000.0,"object_pos_end":[0.50544,0.10431,0.03401],"object_pos_start":[0.50589,0.10456,0.03383],"object_to_goal_dist_end":0.18448,"object_to_goal_dist_start":0.18475,"object_z_max":0.03399,"peak_contact_force":30.08087,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":20.0,"raw_peak_contact_force":30.08087,"subtask_id":"channel_insertion","tcp_end":[0.50162,0.1037,0.05996],"tcp_start":[0.50204,0.1043,0.06056],"tcp_to_object_dist_end":0.02624,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":335.0,"n_steps_budget":870.0,"object_pos_end":[0.50534,0.1041,0.03403],"object_pos_start":[0.50544,0.10431,0.03401],"object_to_goal_dist_end":0.18428,"object_to_goal_dist_start":0.18448,"object_z_max":0.03444,"peak_contact_force":0.53579,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":346.0,"raw_peak_contact_force":33.19738,"tcp_end":[0.50222,0.10793,0.16483],"tcp_start":[0.50162,0.1037,0.05996],"tcp_to_object_dist_end":0.1309,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.99495,"average_solve_count":198.0,"average_success_count":198.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.15715,"contact_1.contact_speed":0.01509,"contact_1.force_threshold":2.74471,"descend_1.descend_speed":0.06909,"descend_1.y_offset":0.00853,"push_1.max_time":8.91845,"push_1.push_distance":0.08911,"push_1.push_speed":0.03092,"retract_1.retract_speed":0.03088},"optimized_scores":{"best_composite_score":-0.50129,"best_fitness_score":0.03871,"best_task_score":0.00327},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":362.0,"contact_point_centroid":[0.50132,0.06683,0.00941],"force_p95":0.69554,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.40187,"mean_force":1.0868,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49734,0.07606,0.11036]},{"body_a":"attachment","body_b":"peg","contact_count":20.0,"contact_point_centroid":[0.50931,0.06872,0.05896],"force_p95":31.89733,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.97507,"mean_force":9.87139,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49749,0.06917,0.06041]},{"body_a":"peg","body_b":"channel_base_body","contact_count":11.0,"contact_point_centroid":[0.48766,0.06057,0.00939],"force_p95":30.64542,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.30048,"mean_force":24.47849,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49817,0.06947,0.06013]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.51002,0.06925,0.05859],"force_p95":30.19579,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.85774,"mean_force":24.02432,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49817,0.06947,0.06013]},{"body_a":"peg","body_b":"channel_base_body","contact_count":218.0,"contact_point_centroid":[0.50311,0.06731,0.00938],"force_p95":0.55067,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.53674,"mean_force":0.62458,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49777,0.07335,0.0757]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51022,0.06946,0.05876],"force_p95":17.0242,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.0242,"mean_force":17.0242,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49837,0.06973,0.06061]},{"body_a":"peg","body_b":"channel_base_body","contact_count":275.0,"contact_point_centroid":[0.50308,0.06737,0.0093],"force_p95":0.718,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.57792,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49971,0.14044,0.24678]},{"body_a":"peg","body_b":"channel_base_body","contact_count":214.0,"contact_point_centroid":[0.50308,0.06769,0.00938],"force_p95":0.55136,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5555,"mean_force":0.54665,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4995,0.08071,0.14761]}],"total_contact_groups":8},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5022,0.06694,0.03379],"final_tcp_position":[0.49931,0.07147,0.16477],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":35.40187,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":291.0,"n_steps_budget":690.0,"object_pos_end":[0.50301,0.06746,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54707,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":275.0,"raw_peak_contact_force":2.06903,"subtask_id":"pre_insert_alignment","tcp_end":[0.50046,0.08451,0.19962],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16671,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":214.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50301,0.06746,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14762,"object_z_max":0.0338,"peak_contact_force":0.54595,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":214.0,"raw_peak_contact_force":0.5555,"subtask_id":"pre_insert_alignment","tcp_end":[0.4996,0.07714,0.09333],"tcp_start":[0.50046,0.08451,0.19962],"tcp_to_object_dist_end":0.06042,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":218.0,"n_steps_budget":1000.0,"object_pos_end":[0.50304,0.06741,0.0338],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":17.53674,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":219.0,"raw_peak_contact_force":17.53674,"subtask_id":"pre_insert_alignment","tcp_end":[0.49839,0.0697,0.06049],"tcp_start":[0.4996,0.07714,0.09333],"tcp_to_object_dist_end":0.02719,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":11.0,"n_steps_budget":1000.0,"object_pos_end":[0.50258,0.06714,0.03399],"object_pos_start":[0.50304,0.06741,0.0338],"object_to_goal_dist_end":0.14728,"object_to_goal_dist_start":0.14758,"object_z_max":0.03398,"peak_contact_force":31.30048,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":22.0,"raw_peak_contact_force":31.30048,"subtask_id":"channel_insertion","tcp_end":[0.49799,0.06902,0.05985],"tcp_start":[0.49839,0.0697,0.06049],"tcp_to_object_dist_end":0.02632,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":362.0,"n_steps_budget":1000.0,"object_pos_end":[0.5022,0.06694,0.03379],"object_pos_start":[0.50258,0.06714,0.03399],"object_to_goal_dist_end":0.14709,"object_to_goal_dist_start":0.14728,"object_z_max":0.03497,"peak_contact_force":0.55161,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":382.0,"raw_peak_contact_force":35.40187,"tcp_end":[0.49931,0.07147,0.16477],"tcp_start":[0.49799,0.06902,0.05985],"tcp_to_object_dist_end":0.13109,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```