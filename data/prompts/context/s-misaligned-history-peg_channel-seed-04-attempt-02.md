## Search State

- **Seed**: 4
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 8  | -0.0963 | 0.00 | ❌ rejected |
| 1 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 5  | 0.3038 | 0.61 | ✅ accepted |
| 0 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6  | -0.1287 | 0.26 | ❌ rejected |

**Proposal policy**: task_score is 0.26 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.129) — your mutation base

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

- **Composite score**: -0.129
- **task_score** (E): 0.257
- **fitness_score**: 0.301  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1827 |
| lower_to_peg | 1.00 | 1.00 | 0.0986 |
| push_through_channel | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.097, 0.151) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.556 | 3.242 |
| lower_to_peg | descend | 1.00 / step_budget | (0.516, 0.097, 0.151)→(0.504, 0.091, 0.054) | (0.505, 0.084, 0.034)→(0.502, 0.039, 0.038) | 0.165→0.119 | 1.00 / 1.333 | 107.033 | 261.546 |
| push_through_channel | push | 0.00 / guard_failure | (0.503, 0.088, 0.052)→(0.503, 0.088, 0.052) | (0.502, 0.039, 0.038)→(0.503, 0.035, 0.038) | 0.119→0.115 | 1.00 / 2.000 | 37.759 | 78.297 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.681
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.681
- phase_score: 0.341
- phase_breakdown.approach_peg_score: 0.690
- phase_breakdown.contact_peg_score: 0.658
- phase_breakdown.push_through_score: 0.011

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.477
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.681
- **Median Q (composite search score)**: -0.197
- **K-run variance**: 0.0157
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.351


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.05594,"average_solve_count":143.0,"average_success_count":143.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.04968,"approach_peg.offset_z":0.1005,"lower_to_peg.lower_speed":0.05516,"push_through_channel.force_threshold":30.10012,"push_through_channel.push_speed":0.04188,"push_through_channel.retry_offset_x":0.00801,"push_through_channel.retry_offset_y":-0.00335,"push_through_channel.retry_offset_z":0.00324},"optimized_scores":{"best_composite_score":-0.2363,"best_fitness_score":0.1937,"best_task_score":0.0273},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.53313,0.11987,0.05999],"force_p95":103.00041,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":108.49981,"mean_force":57.3691,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50332,0.08087,0.05064]},{"body_a":"peg","body_b":"channel_base_body","contact_count":172.0,"contact_point_centroid":[0.50267,0.06659,0.00962],"force_p95":73.02291,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":97.58674,"mean_force":15.25838,"phase_index":1.0,"phase_name":"lower_to_peg","phase_type":"descend","tcp_position_centroid":[0.51068,0.09181,0.07913]},{"body_a":"attachment","body_b":"peg","contact_count":89.0,"contact_point_centroid":[0.50617,0.0901,0.05812],"force_p95":83.78847,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":97.31262,"mean_force":28.65419,"phase_index":1.0,"phase_name":"lower_to_peg","phase_type":"descend","tcp_position_centroid":[0.50068,0.08961,0.06306]},{"body_a":"peg","body_b":"channel_base_body","contact_count":14.0,"contact_point_centroid":[0.50012,0.04824,0.00969],"force_p95":10.3506,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.76587,"mean_force":2.91418,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50386,0.08217,0.05146]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.50185,0.08328,0.0606],"force_p95":9.5921,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.7483,"mean_force":6.20749,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50463,0.08326,0.05258]},{"body_a":"peg","body_b":"channel_base_body","contact_count":356.0,"contact_point_centroid":[0.5056,0.08091,0.00935],"force_p95":0.56686,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.58962,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51432,0.14431,0.22162]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50032,0.19687,0.29535]}],"total_contact_groups":7},"final_pose_error":0.16093,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50073,0.0616,0.0369],"final_tcp_position":[0.50328,0.08055,0.0505],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":108.49981,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":385.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.08086,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54604,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":392.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach_peg","tcp_end":[0.52865,0.09415,0.15366],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12273,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":176.0,"n_steps_budget":1000.0,"object_pos_end":[0.50145,0.06707,0.03555],"object_pos_start":[0.50598,0.08086,0.03378],"object_to_goal_dist_end":0.14714,"object_to_goal_dist_start":0.16109,"object_z_max":0.03758,"peak_contact_force":0.15009,"phase_name":"lower_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":261.0,"raw_peak_contact_force":97.58674,"subtask_id":"contact_peg","tcp_end":[0.50511,0.08362,0.05329],"tcp_start":[0.52865,0.09415,0.15366],"tcp_to_object_dist_end":0.02454,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":15.0,"n_steps_budget":1000.0,"object_pos_end":[0.50077,0.06216,0.03655],"object_pos_start":[0.50145,0.06707,0.03555],"object_to_goal_dist_end":0.14221,"object_to_goal_dist_start":0.14714,"object_z_max":0.03673,"peak_contact_force":53.50584,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":22.0,"raw_peak_contact_force":108.49981,"subtask_id":"push_through","tcp_end":[0.50328,0.08055,0.0505],"tcp_start":[0.50331,0.08066,0.05057],"tcp_to_object_dist_end":0.02321,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91667,"average_solve_count":96.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.07222,"approach_peg.offset_z":0.09211,"lower_to_peg.lower_speed":0.08704,"push_through_channel.force_threshold":15.17584,"push_through_channel.push_speed":0.0508,"push_through_channel.retry_offset_x":0.00746,"push_through_channel.retry_offset_y":-0.00242,"push_through_channel.retry_offset_z":0.00277},"optimized_scores":{"best_composite_score":-0.19659,"best_fitness_score":0.23341,"best_task_score":0.06165},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":161.0,"contact_point_centroid":[0.49969,0.09156,0.00955],"force_p95":103.39524,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":121.06178,"mean_force":19.73645,"phase_index":1.0,"phase_name":"lower_to_peg","phase_type":"descend","tcp_position_centroid":[0.50691,0.11526,0.07624]},{"body_a":"attachment","body_b":"peg","contact_count":83.0,"contact_point_centroid":[0.50416,0.11315,0.05786],"force_p95":112.83429,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":120.74667,"mean_force":37.41867,"phase_index":1.0,"phase_name":"lower_to_peg","phase_type":"descend","tcp_position_centroid":[0.49764,0.11378,0.06038]},{"body_a":"peg","body_b":"channel_base_body","contact_count":16.0,"contact_point_centroid":[0.50212,0.07282,0.00962],"force_p95":13.08199,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.85022,"mean_force":4.06231,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50091,0.10425,0.0504]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.50304,0.10505,0.05502],"force_p95":16.48037,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.84889,"mean_force":5.42603,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50148,0.10518,0.05124]},{"body_a":"peg","body_b":"channel_base_body","contact_count":321.0,"contact_point_centroid":[0.50534,0.10468,0.00936],"force_p95":0.60028,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.5816,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50909,0.15567,0.21864]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50019,0.19746,0.29535]}],"total_contact_groups":6},"final_pose_error":0.18159,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50492,0.08428,0.03778],"final_tcp_position":[0.5004,0.10134,0.04951],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":121.06178,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":348.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.10471,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18491,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.57499,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":353.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach_peg","tcp_end":[0.51871,0.11569,0.14753],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11493,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":162.0,"n_steps_budget":840.0,"object_pos_end":[0.50204,0.09104,0.03655],"object_pos_start":[0.50597,0.10471,0.03384],"object_to_goal_dist_end":0.17109,"object_to_goal_dist_start":0.18491,"object_z_max":0.03776,"peak_contact_force":0.777,"phase_name":"lower_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":244.0,"raw_peak_contact_force":121.06178,"subtask_id":"contact_peg","tcp_end":[0.50251,0.10714,0.05293],"tcp_start":[0.51871,0.11569,0.14753],"tcp_to_object_dist_end":0.02297,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.50462,0.08471,0.03731],"object_pos_start":[0.50204,0.09104,0.03655],"object_to_goal_dist_end":0.1648,"object_to_goal_dist_start":0.17109,"object_z_max":0.03755,"peak_contact_force":0.35946,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":26.0,"raw_peak_contact_force":23.85022,"subtask_id":"push_through","tcp_end":[0.5004,0.10134,0.04951],"tcp_start":[0.50046,0.10156,0.04959],"tcp_to_object_dist_end":0.02105,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.02548,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.05237,"approach_peg.offset_z":0.09837,"lower_to_peg.lower_speed":0.03327,"push_through_channel.force_threshold":5.14188,"push_through_channel.push_speed":0.08839,"push_through_channel.retry_offset_x":-0.00512,"push_through_channel.retry_offset_y":0.00923,"push_through_channel.retry_offset_z":-0.0099},"optimized_scores":{"best_composite_score":0.04677,"best_fitness_score":0.47677,"best_task_score":0.68077},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":90.0,"contact_point_centroid":[0.50385,0.14161,-0.00025],"force_p95":555.95537,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":565.98812,"mean_force":349.33201,"phase_index":1.0,"phase_name":"lower_to_peg","phase_type":"descend","tcp_position_centroid":[0.50431,0.08059,0.05495]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":20.0,"contact_point_centroid":[0.47466,0.10273,0.05943],"force_p95":385.68072,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":422.02691,"mean_force":289.55146,"phase_index":1.0,"phase_name":"lower_to_peg","phase_type":"descend","tcp_position_centroid":[0.47931,0.09417,0.0655]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":36.0,"contact_point_centroid":[0.47498,0.11994,0.05161],"force_p95":367.39642,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":369.53263,"mean_force":265.09433,"phase_index":1.0,"phase_name":"lower_to_peg","phase_type":"descend","tcp_position_centroid":[0.49996,0.07804,0.06448]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":193.0,"contact_point_centroid":[0.52501,0.11994,0.05065],"force_p95":323.91322,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":352.2449,"mean_force":216.4221,"phase_index":1.0,"phase_name":"lower_to_peg","phase_type":"descend","tcp_position_centroid":[0.50139,0.07998,0.07149]},{"body_a":"attachment","body_b":"peg","contact_count":90.0,"contact_point_centroid":[0.50355,0.08509,0.05475],"force_p95":138.60166,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":147.71862,"mean_force":113.93109,"phase_index":1.0,"phase_name":"lower_to_peg","phase_type":"descend","tcp_position_centroid":[0.50355,0.08026,0.06491]},{"body_a":"peg","body_b":"channel_base_body","contact_count":444.0,"contact_point_centroid":[0.50342,0.05675,0.00915],"force_p95":126.95125,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":147.60807,"mean_force":23.63789,"phase_index":1.0,"phase_name":"lower_to_peg","phase_type":"descend","tcp_position_centroid":[0.49786,0.0818,0.07433]},{"body_a":"world","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.5042,0.1415,-8e-05],"force_p95":100.47984,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":102.54216,"mean_force":81.29127,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50412,0.08103,0.0559]},{"body_a":"peg","body_b":"channel_base_body","contact_count":379.0,"contact_point_centroid":[0.503,0.06751,0.00932],"force_p95":0.61734,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56935,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49941,0.13985,0.22305]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.50241,-0.03659,0.00998],"force_p95":0.38438,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38444,"mean_force":0.38392,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.5041,0.08104,0.05591]}],"total_contact_groups":9},"final_pose_error":0.16186,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50232,-0.04146,0.04043],"final_tcp_position":[0.50418,0.08102,0.0559],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":565.98812,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":395.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.06748,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54779,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":379.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach_peg","tcp_end":[0.50011,0.08169,0.1515],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1186,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":481.0,"n_steps_budget":1000.0,"object_pos_end":[0.50235,-0.04018,0.04054],"object_pos_start":[0.50309,0.06748,0.0338],"object_to_goal_dist_end":0.0399,"object_to_goal_dist_start":0.14764,"object_z_max":0.04355,"peak_contact_force":320.17181,"phase_name":"lower_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":873.0,"raw_peak_contact_force":565.98812,"subtask_id":"contact_peg","tcp_end":[0.50409,0.08104,0.0559],"tcp_start":[0.50011,0.08169,0.1515],"tcp_to_object_dist_end":0.1222,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50234,-0.0406,0.04052],"object_pos_start":[0.50235,-0.04018,0.04054],"object_to_goal_dist_end":0.03947,"object_to_goal_dist_start":0.0399,"object_z_max":0.04054,"peak_contact_force":59.41262,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":102.54216,"subtask_id":"push_through","tcp_end":[0.50418,0.08102,0.0559],"tcp_start":[0.50415,0.08103,0.0559],"tcp_to_object_dist_end":0.12261,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```