## Search State

- **Seed**: 4
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → align → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 14 | -0.5188 | 0.04 | ❌ rejected |
| 4 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 13 | -0.5048 | 0.00 | ❌ rejected |
| 3 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | -0.4374 | 0.00 | ❌ rejected |
| 2 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | -0.4455 | 0.20 | ❌ rejected |
| 1 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | -0.0888 | 0.41 | ❌ rejected |

**Proposal policy**: task_score is 0.04 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.519) — your mutation base

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

- **Composite score**: -0.519
- **task_score** (E): 0.041
- **fitness_score**: 0.101  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.820

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2077 |
| descend_1 | 1.00 | 1.00 | 0.0512 |
| align_1 | 1.00 | 1.00 | 0.0173 |
| contact_1 | 1.00 | 1.00 | 0.0000 |
| push_1 | 0.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.123, 0.109) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.164 | 1.00 / 1.000 | 0.546 | 3.242 |
| descend_1 | descend | 1.00 / step_budget | (0.516, 0.123, 0.109)→(0.507, 0.116, 0.059) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.164→0.165 | 1.00 / 1.333 | 108.289 | 113.300 |
| align_1 | align | 1.00 / step_budget | (0.507, 0.116, 0.059)→(0.508, 0.107, 0.046) | (0.505, 0.084, 0.034)→(0.507, 0.076, 0.034) | 0.165→0.156 | 1.00 / 3.000 | 239.963 | 289.059 |
| contact_1 | contact | 1.00 / force_exceeded | (0.508, 0.107, 0.046)→(0.508, 0.107, 0.046) | (0.507, 0.076, 0.034)→(0.507, 0.076, 0.034) | 0.156→0.156 | 1.00 / 3.000 | 74.587 | 74.587 |
| push_1 | push | 0.00 / guard_failure | (0.508, 0.107, 0.046)→(0.508, 0.107, 0.046) | (0.507, 0.076, 0.034)→(0.507, 0.076, 0.034) | 0.156→0.156 | 1.00 / 3.000 | 87.783 | 87.783 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.194
- phase_breakdown.pre_insert_alignment_score: 0.646
- phase_breakdown.channel_insertion_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.116
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.080
- **Median Q (composite search score)**: -0.515
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.323


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34146,"average_solve_count":82.0,"average_success_count":82.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00297,"align_1.lateral_offset_y":0.01806,"approach_1.approach_height":0.03142,"approach_1.approach_speed":0.12999,"contact_1.contact_force_threshold":9.36034,"contact_1.contact_speed":0.02671,"descend_1.descend_speed":0.06671,"descend_1.descend_z_offset":0.00722,"push_1.force_limit_threshold":35.36666,"push_1.push_distance":0.14642,"push_1.push_max_time":8.20361,"push_1.push_speed":0.05548,"retract_1.retract_height":0.05869,"retract_1.retract_speed":0.09819},"optimized_scores":{"best_composite_score":-0.50375,"best_fitness_score":0.11625,"best_task_score":4e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":177.0,"contact_point_centroid":[0.52774,0.11468,0.05983],"force_p95":324.78986,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":338.76977,"mean_force":315.9627,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51657,0.11473,0.06406]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":513.0,"contact_point_centroid":[0.53007,0.11467,0.05992],"force_p95":332.05276,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":334.37708,"mean_force":305.32115,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51889,0.11476,0.0642]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.53197,0.11423,0.05992],"force_p95":70.37231,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":70.37231,"mean_force":70.37231,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52077,0.1144,0.06415]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.53196,0.11423,0.05992],"force_p95":68.79375,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":68.79375,"mean_force":68.79375,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52076,0.1144,0.06415]},{"body_a":"peg","body_b":"channel_base_body","contact_count":405.0,"contact_point_centroid":[0.50565,0.08086,0.00935],"force_p95":0.56136,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.58444,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5144,0.15734,0.18783]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50046,0.1975,0.29341]},{"body_a":"peg","body_b":"channel_base_body","contact_count":256.0,"contact_point_centroid":[0.50592,0.08098,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5501,"mean_force":0.54677,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51841,0.1153,0.06783]},{"body_a":"peg","body_b":"channel_base_body","contact_count":513.0,"contact_point_centroid":[0.50598,0.0808,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55007,"mean_force":0.54677,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51889,0.11476,0.0642]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.507,0.09875,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.55006,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52077,0.1144,0.06415]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49001,0.08914,0.00938],"force_p95":0.54527,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54527,"mean_force":0.54527,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52076,0.1144,0.06415]}],"total_contact_groups":10},"final_pose_error":0.18307,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50599,0.08089,0.03378],"final_tcp_position":[0.52078,0.1144,0.06415],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":338.76977,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":434.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54815,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":441.0,"raw_peak_contact_force":4.32595,"subtask_id":"pre_insert_alignment","tcp_end":[0.52878,0.11886,0.08829],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07026,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":256.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":323.74724,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":433.0,"raw_peak_contact_force":338.76977,"subtask_id":"pre_insert_alignment","tcp_end":[0.51721,0.11484,0.06421],"tcp_start":[0.52878,0.11886,0.08829],"tcp_to_object_dist_end":0.04697,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.50595,0.08088,0.03378],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":332.07497,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1026.0,"raw_peak_contact_force":334.37708,"subtask_id":"pre_insert_alignment","tcp_end":[0.52076,0.1144,0.06415],"tcp_start":[0.51721,0.11484,0.06421],"tcp_to_object_dist_end":0.0476,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.50595,0.08088,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":68.79375,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":68.79375,"subtask_id":"pre_insert_alignment","tcp_end":[0.52077,0.1144,0.06415],"tcp_start":[0.52076,0.1144,0.06415],"tcp_to_object_dist_end":0.04759,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":70.37231,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":70.37231,"subtask_id":"channel_insertion","tcp_end":[0.52078,0.1144,0.06415],"tcp_start":[0.52077,0.1144,0.06415],"tcp_to_object_dist_end":0.04759,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26882,"average_solve_count":93.0,"average_success_count":93.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00211,"align_1.lateral_offset_y":0.01004,"approach_1.approach_height":0.08442,"approach_1.approach_speed":0.10702,"contact_1.contact_force_threshold":9.5471,"contact_1.contact_speed":0.01225,"descend_1.descend_speed":0.0584,"descend_1.descend_z_offset":0.01385,"push_1.force_limit_threshold":18.63847,"push_1.push_distance":0.12248,"push_1.push_max_time":8.41456,"push_1.push_speed":0.0555,"retract_1.retract_height":0.0943,"retract_1.retract_speed":0.0416},"optimized_scores":{"best_composite_score":-0.53705,"best_fitness_score":0.08295,"best_task_score":0.04218},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":173.0,"contact_point_centroid":[0.52505,0.11999,0.05998],"force_p95":249.72134,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":274.6845,"mean_force":193.3053,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50224,0.12203,0.03757]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52504,0.11999,0.05998],"force_p95":72.52629,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":72.52629,"mean_force":72.52629,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50177,0.1221,0.03708]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52505,0.11999,0.05998],"force_p95":71.28554,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":71.28554,"mean_force":71.28554,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50179,0.1221,0.03709]},{"body_a":"attachment","body_b":"peg","contact_count":232.0,"contact_point_centroid":[0.50545,0.11296,0.04609],"force_p95":9.90886,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.5188,"mean_force":3.84498,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50228,0.12481,0.04149]},{"body_a":"peg","body_b":"channel_base_body","contact_count":363.0,"contact_point_centroid":[0.50617,0.0849,0.00975],"force_p95":9.30083,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.87647,"mean_force":2.82856,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50228,0.12502,0.04178]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":103.0,"contact_point_centroid":[0.52503,0.0941,0.03708],"force_p95":2.15102,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.49991,"mean_force":0.71459,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50222,0.12378,0.04]},{"body_a":"peg","body_b":"channel_base_body","contact_count":300.0,"contact_point_centroid":[0.50553,0.10469,0.00936],"force_p95":0.60165,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.58401,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50915,0.1694,0.21534]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50026,0.19799,0.29466]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.5228,0.10061,0.00937],"force_p95":0.60012,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60012,"mean_force":0.60012,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50179,0.1221,0.03709]},{"body_a":"peg","body_b":"channel_base_body","contact_count":268.0,"contact_point_centroid":[0.50563,0.10465,0.00939],"force_p95":0.57527,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57941,"mean_force":0.54641,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51054,0.13828,0.09933]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.5229,0.10043,0.00937],"force_p95":0.55992,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55992,"mean_force":0.55992,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50177,0.1221,0.03708]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.09209,0.05875],"force_p95":0.0,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50179,0.1221,0.03709]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52502,0.09211,0.05874],"force_p95":0.0,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50177,0.1221,0.03708]}],"total_contact_groups":13},"final_pose_error":0.15264,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.507,0.09209,0.03377],"final_tcp_position":[0.50175,0.12212,0.03707],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":274.6845,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":327.0,"n_steps_budget":1000.0,"object_pos_end":[0.50592,0.10457,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54457,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":332.0,"raw_peak_contact_force":3.33087,"subtask_id":"pre_insert_alignment","tcp_end":[0.51853,0.14226,0.14169],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11494,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":268.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.10471,0.03384],"object_pos_start":[0.50592,0.10457,0.03384],"object_to_goal_dist_end":0.18491,"object_to_goal_dist_start":0.18476,"object_z_max":0.03384,"peak_contact_force":0.57578,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":268.0,"raw_peak_contact_force":0.57941,"subtask_id":"pre_insert_alignment","tcp_end":[0.50411,0.1348,0.05733],"tcp_start":[0.51853,0.14226,0.14169],"tcp_to_object_dist_end":0.03823,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":377.0,"n_steps_budget":600.0,"object_pos_end":[0.50699,0.09208,0.03377],"object_pos_start":[0.50597,0.10471,0.03384],"object_to_goal_dist_end":0.17234,"object_to_goal_dist_start":0.18491,"object_z_max":0.0365,"peak_contact_force":183.40576,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":871.0,"raw_peak_contact_force":274.6845,"subtask_id":"pre_insert_alignment","tcp_end":[0.50179,0.1221,0.03709],"tcp_start":[0.50411,0.1348,0.05733],"tcp_to_object_dist_end":0.03064,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.507,0.09209,0.03377],"object_pos_start":[0.50699,0.09208,0.03377],"object_to_goal_dist_end":0.17234,"object_to_goal_dist_start":0.17234,"object_z_max":0.03377,"peak_contact_force":71.28554,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":71.28554,"subtask_id":"pre_insert_alignment","tcp_end":[0.50177,0.1221,0.03708],"tcp_start":[0.50179,0.1221,0.03709],"tcp_to_object_dist_end":0.03065,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.507,0.09209,0.03377],"object_pos_start":[0.507,0.09209,0.03377],"object_to_goal_dist_end":0.17234,"object_to_goal_dist_start":0.17234,"object_z_max":0.03377,"peak_contact_force":72.52629,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":72.52629,"subtask_id":"channel_insertion","tcp_end":[0.50175,0.12212,0.03707],"tcp_start":[0.50177,0.1221,0.03708],"tcp_to_object_dist_end":0.03066,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.60563,"average_solve_count":71.0,"average_success_count":71.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00452,"align_1.lateral_offset_y":0.0102,"approach_1.approach_height":0.03853,"approach_1.approach_speed":0.18773,"contact_1.contact_force_threshold":8.93028,"contact_1.contact_speed":0.02016,"descend_1.descend_speed":0.05187,"descend_1.descend_z_offset":0.01353,"push_1.force_limit_threshold":24.85807,"push_1.push_distance":0.14527,"push_1.push_max_time":6.3072,"push_1.push_speed":0.06478,"retract_1.retract_height":0.19105,"retract_1.retract_speed":0.08258},"optimized_scores":{"best_composite_score":-0.51547,"best_fitness_score":0.10453,"best_task_score":0.0797},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":147.0,"contact_point_centroid":[0.5456,0.08453,0.05995],"force_p95":237.23382,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":258.11499,"mean_force":149.97244,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50085,0.0845,0.03634]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":119.0,"contact_point_centroid":[0.52502,0.08464,0.05999],"force_p95":144.66128,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":154.35925,"mean_force":124.14116,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5009,0.08449,0.03637]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54574,0.0845,0.05994],"force_p95":120.44975,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":120.44975,"mean_force":120.44975,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50086,0.08445,0.03659]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52503,0.08461,0.05998],"force_p95":83.68162,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":83.68162,"mean_force":83.68162,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50083,0.08444,0.0366]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52504,0.08462,0.05998],"force_p95":77.59134,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":77.59134,"mean_force":77.59134,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50086,0.08445,0.03659]},{"body_a":"peg","body_b":"channel_base_body","contact_count":429.0,"contact_point_centroid":[0.50809,0.04372,0.00989],"force_p95":6.16344,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.81324,"mean_force":2.56437,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49923,0.08877,0.04111]},{"body_a":"attachment","body_b":"peg","contact_count":374.0,"contact_point_centroid":[0.50396,0.07572,0.04648],"force_p95":5.92776,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.52206,"mean_force":2.54667,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49948,0.08757,0.03958]},{"body_a":"peg","body_b":"channel_base_body","contact_count":383.0,"contact_point_centroid":[0.50312,0.06744,0.00932],"force_p95":0.61376,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.5691,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49932,0.15237,0.19433]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50882,0.03713,0.00999],"force_p95":1.39942,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.39942,"mean_force":1.39942,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50083,0.08444,0.0366]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.506,0.07254,0.04644],"force_p95":1.06594,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.06594,"mean_force":1.06594,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50083,0.08444,0.0366]},{"body_a":"peg","body_b":"channel_base_body","contact_count":137.0,"contact_point_centroid":[0.50284,0.06734,0.00938],"force_p95":0.55056,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55159,"mean_force":0.54665,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49825,0.10301,0.07553]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50883,0.03713,0.00999],"force_p95":0.38998,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38998,"mean_force":0.38998,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50086,0.08445,0.03659]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50601,0.07254,0.04642],"force_p95":0.2301,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2301,"mean_force":0.2301,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50086,0.08445,0.03659]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54572,0.0845,0.05994],"force_p95":0.12029,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.12029,"mean_force":0.12029,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50083,0.08444,0.0366]}],"total_contact_groups":14},"final_pose_error":0.17511,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50668,0.05471,0.03518],"final_tcp_position":[0.50086,0.08445,0.0366],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":258.11499,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":399.0,"n_steps_budget":840.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54552,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":383.0,"raw_peak_contact_force":2.06903,"subtask_id":"pre_insert_alignment","tcp_end":[0.49973,0.10698,0.09562],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07346,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":137.0,"n_steps_budget":630.0,"object_pos_end":[0.50302,0.06748,0.0338],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.54544,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":137.0,"raw_peak_contact_force":0.55159,"subtask_id":"pre_insert_alignment","tcp_end":[0.49846,0.09931,0.05581],"tcp_start":[0.49973,0.10698,0.09562],"tcp_to_object_dist_end":0.03897,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":441.0,"n_steps_budget":600.0,"object_pos_end":[0.50668,0.05471,0.03518],"object_pos_start":[0.50302,0.06748,0.0338],"object_to_goal_dist_end":0.13496,"object_to_goal_dist_start":0.14764,"object_z_max":0.03616,"peak_contact_force":204.40749,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1069.0,"raw_peak_contact_force":258.11499,"subtask_id":"pre_insert_alignment","tcp_end":[0.50083,0.08444,0.0366],"tcp_start":[0.49846,0.09931,0.05581],"tcp_to_object_dist_end":0.03034,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":960.0,"object_pos_end":[0.50668,0.05471,0.03518],"object_pos_start":[0.50668,0.05471,0.03518],"object_to_goal_dist_end":0.13496,"object_to_goal_dist_start":0.13496,"object_z_max":0.03518,"peak_contact_force":83.68162,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":83.68162,"subtask_id":"pre_insert_alignment","tcp_end":[0.50086,0.08445,0.03659],"tcp_start":[0.50083,0.08444,0.0366],"tcp_to_object_dist_end":0.03033,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50668,0.05471,0.03518],"object_pos_start":[0.50668,0.05471,0.03518],"object_to_goal_dist_end":0.13496,"object_to_goal_dist_start":0.13496,"object_z_max":0.03518,"peak_contact_force":120.44975,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":120.44975,"subtask_id":"channel_insertion","tcp_end":[0.50086,0.08445,0.0366],"tcp_start":[0.50086,0.08445,0.03659],"tcp_to_object_dist_end":0.03033,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```