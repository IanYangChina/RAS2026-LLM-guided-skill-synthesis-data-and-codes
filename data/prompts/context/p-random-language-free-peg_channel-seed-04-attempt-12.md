## Search State

- **Seed**: 4
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 8 | -0.0953 | 0.23 | ❌ rejected |
| 11 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 8 | -0.2488 | 0.17 | ❌ rejected |
| 10 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.1835 | 0.00 | ❌ rejected |
| 9 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3033 | 0.61 | ❌ rejected |
| 8 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3046 | 0.61 | ✅ accepted |

**Proposal policy**: task_score is 0.23 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.095) — your mutation base

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

- **Composite score**: -0.095
- **task_score** (E): 0.230
- **fitness_score**: 0.335  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.1822 |
| align | 0.00 | 1.00 | 0.1066 |
| push | 0.67 | 1.00 | 0.0469 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.097, 0.152) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.547 | 3.242 |
| align | align | 0.00 / step_budget | (0.516, 0.097, 0.152)→(0.515, 0.099, 0.046) | (0.505, 0.084, 0.034)→(0.497, 0.074, 0.034) | 0.165→0.154 | 1.00 / 2.667 | 268.117 | 539.816 |
| push | push | 0.67 / time_limit | (0.515, 0.099, 0.046)→(0.509, 0.052, 0.042) | (0.497, 0.074, 0.034)→(0.500, 0.025, 0.035) | 0.154→0.106 | 1.00 / 2.333 | 22.632 | 29.412 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.639
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.525
- phase_score: 0.638
- phase_breakdown.push_through_channel_score: 0.648
- phase_breakdown.approach_peg_score: 0.599

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.593
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.525
- **Median Q (composite search score)**: -0.109
- **K-run variance**: 0.0422
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.300


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95918,"average_solve_count":196.0,"average_success_count":196.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align.align_speed":0.03962,"align.align_y_offset":0.02865,"align.align_z_offset":-0.09497,"approach.approach_height":0.08739,"approach.approach_speed":0.03739,"push.guard_force_threshold":29.32492,"push.push_distance":0.17833,"push.push_speed":0.03421},"optimized_scores":{"best_composite_score":-0.33946,"best_fitness_score":0.09054,"best_task_score":7e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":837.0,"contact_point_centroid":[0.53713,0.10049,0.0599],"force_p95":421.6099,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":568.38475,"mean_force":410.50995,"phase_index":1.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.52527,0.10013,0.06156]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.54459,0.10252,0.05993],"force_p95":49.27332,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":49.27332,"mean_force":49.27332,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.53275,0.10163,0.0616]},{"body_a":"peg","body_b":"channel_base_body","contact_count":380.0,"contact_point_centroid":[0.50563,0.08091,0.00935],"force_p95":0.56185,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.58692,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51429,0.14422,0.21544]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.5002,0.19723,0.29559]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50595,0.08087,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5501,"mean_force":0.54677,"phase_index":1.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.52486,0.09936,0.06826]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52106,0.09068,0.00938],"force_p95":0.54458,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54458,"mean_force":0.54458,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.53275,0.10163,0.0616]}],"total_contact_groups":6},"final_pose_error":0.20278,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50599,0.08087,0.03378],"final_tcp_position":[0.53277,0.10163,0.0616],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":568.38475,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":409.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.08086,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54605,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":416.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach_peg","tcp_end":[0.52879,0.09334,0.14092],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11025,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.50598,0.08086,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16109,"object_z_max":0.03378,"peak_contact_force":403.29034,"phase_name":"align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1837.0,"raw_peak_contact_force":568.38475,"tcp_end":[0.53275,0.10163,0.0616],"tcp_start":[0.52879,0.09334,0.14092],"tcp_to_object_dist_end":0.04383,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":49.27332,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":49.27332,"subtask_id":"push_through_channel","tcp_end":[0.53277,0.10163,0.0616],"tcp_start":[0.53275,0.10163,0.0616],"tcp_to_object_dist_end":0.04385,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24516,"average_solve_count":155.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align.align_speed":0.05592,"align.align_y_offset":0.01214,"align.align_z_offset":-0.07969,"approach.approach_height":0.09809,"approach.approach_speed":0.08608,"push.guard_force_threshold":29.80523,"push.push_distance":0.16955,"push.push_speed":0.03385},"optimized_scores":{"best_composite_score":-0.10941,"best_fitness_score":0.32059,"best_task_score":0.16495},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":790.0,"contact_point_centroid":[0.52507,0.11842,0.05999],"force_p95":453.3217,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":489.31512,"mean_force":384.72285,"phase_index":1.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.50955,0.11795,0.04621]},{"body_a":"attachment","body_b":"peg","contact_count":572.0,"contact_point_centroid":[0.51185,0.1082,0.05079],"force_p95":143.51203,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":168.87713,"mean_force":91.24331,"phase_index":1.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.51047,0.11745,0.04899]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50304,0.09925,0.00894],"force_p95":141.30267,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":157.56929,"mean_force":50.43654,"phase_index":1.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.51039,0.11742,0.0579]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":454.0,"contact_point_centroid":[0.47455,0.09497,0.03141],"force_p95":51.70724,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":72.71322,"mean_force":9.3912,"phase_index":1.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.50836,0.11849,0.04303]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":408.0,"contact_point_centroid":[0.53984,0.09235,0.06],"force_p95":18.33412,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":21.96058,"mean_force":14.01096,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49903,0.08325,0.03156]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":28.0,"contact_point_centroid":[0.52523,0.10548,0.05709],"force_p95":20.51725,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.77125,"mean_force":5.8061,"phase_index":1.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.51242,0.11658,0.05386]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52501,0.12,0.06],"force_p95":8.69377,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":8.94144,"mean_force":5.88754,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50498,0.11881,0.03635]},{"body_a":"attachment","body_b":"peg","contact_count":756.0,"contact_point_centroid":[0.49805,0.07582,0.03281],"force_p95":1.51945,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.92678,"mean_force":0.66662,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49939,0.0876,0.0317]},{"body_a":"peg","body_b":"channel_base_body","contact_count":980.0,"contact_point_centroid":[0.49463,0.05092,0.00987],"force_p95":1.77765,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.13111,"mean_force":0.84771,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49942,0.08756,0.03174]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":94.0,"contact_point_centroid":[0.47488,0.08155,0.03048],"force_p95":3.14285,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.72225,"mean_force":0.72849,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.5021,0.1098,0.03344]},{"body_a":"peg","body_b":"channel_base_body","contact_count":309.0,"contact_point_centroid":[0.50535,0.10472,0.00936],"force_p95":0.60088,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.58299,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50934,0.15557,0.22121]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50032,0.19731,0.29522]}],"total_contact_groups":12},"final_pose_error":0.13849,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49871,0.03038,0.03473],"final_tcp_position":[0.49772,0.0603,0.03154],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":489.31512,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":336.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.10469,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18489,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.55104,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":341.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach_peg","tcp_end":[0.51867,0.11585,0.15302],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12037,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49296,0.09147,0.03449],"object_pos_start":[0.50599,0.10469,0.03384],"object_to_goal_dist_end":0.1717,"object_to_goal_dist_start":0.18489,"object_z_max":0.03474,"peak_contact_force":401.05947,"phase_name":"align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2844.0,"raw_peak_contact_force":489.31512,"tcp_end":[0.50499,0.11881,0.03639],"tcp_start":[0.51867,0.11585,0.15302],"tcp_to_object_dist_end":0.02993,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49871,0.03038,0.03473],"object_pos_start":[0.49296,0.09147,0.03449],"object_to_goal_dist_end":0.11051,"object_to_goal_dist_start":0.1717,"object_z_max":0.03543,"peak_contact_force":17.7079,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2241.0,"raw_peak_contact_force":21.96058,"subtask_id":"push_through_channel","tcp_end":[0.49772,0.0603,0.03154],"tcp_start":[0.50499,0.11881,0.03639],"tcp_to_object_dist_end":0.03011,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.96954,"average_solve_count":197.0,"average_success_count":197.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align.align_speed":0.04091,"align.align_y_offset":0.00143,"align.align_z_offset":-0.0744,"approach.approach_height":0.10823,"approach.approach_speed":0.05998,"push.guard_force_threshold":33.67922,"push.push_distance":0.15761,"push.push_speed":0.04816},"optimized_scores":{"best_composite_score":0.16312,"best_fitness_score":0.59312,"best_task_score":0.52537},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":712.0,"contact_point_centroid":[0.52509,0.07567,0.05999],"force_p95":521.843,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":561.74895,"mean_force":358.32179,"phase_index":1.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.51053,0.07569,0.0429]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50702,0.06549,0.0077],"force_p95":261.93809,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":262.40637,"mean_force":154.58027,"phase_index":1.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.50755,0.07627,0.05795]},{"body_a":"attachment","body_b":"peg","contact_count":755.0,"contact_point_centroid":[0.51454,0.06887,0.04742],"force_p95":261.52105,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":261.91589,"mean_force":210.04372,"phase_index":1.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.50996,0.07565,0.04382]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":392.0,"contact_point_centroid":[0.47375,0.06191,0.02589],"force_p95":95.7811,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":111.88867,"mean_force":33.33962,"phase_index":1.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.50976,0.07565,0.04224]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":58.0,"contact_point_centroid":[0.52553,0.06771,0.05083],"force_p95":53.51956,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":62.17752,"mean_force":16.90061,"phase_index":1.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.51116,0.07555,0.04474]},{"body_a":"attachment","body_b":"peg","contact_count":758.0,"contact_point_centroid":[0.49852,0.0211,0.03397],"force_p95":2.5116,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.00156,"mean_force":0.93374,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50052,0.03276,0.03332]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":287.0,"contact_point_centroid":[0.47489,0.0334,0.03196],"force_p95":2.56445,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.29126,"mean_force":0.69345,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50353,0.06122,0.03454]},{"body_a":"peg","body_b":"channel_base_body","contact_count":889.0,"contact_point_centroid":[0.49436,-0.00482,0.00994],"force_p95":2.37515,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.55649,"mean_force":1.06748,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50058,0.03312,0.03336]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52502,0.07587,0.05999],"force_p95":11.22871,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":11.33645,"mean_force":5.48865,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50799,0.0755,0.03874]},{"body_a":"peg","body_b":"channel_base_body","contact_count":363.0,"contact_point_centroid":[0.50309,0.06753,0.00932],"force_p95":0.62015,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.57033,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49945,0.13994,0.22759]}],"total_contact_groups":10},"final_pose_error":0.10277,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49414,-0.03478,0.035],"final_tcp_position":[0.49712,-0.00495,0.03239],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":561.74895,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":379.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54537,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":363.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach_peg","tcp_end":[0.50016,0.08217,0.16079],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12788,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49235,0.05003,0.03483],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.13036,"object_to_goal_dist_start":0.14759,"object_z_max":0.03499,"peak_contact_force":0.0,"phase_name":"align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2917.0,"raw_peak_contact_force":561.74895,"tcp_end":[0.50802,0.07551,0.03881],"tcp_start":[0.50016,0.08217,0.16079],"tcp_to_object_dist_end":0.03018,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49414,-0.03478,0.035],"object_pos_start":[0.49235,0.05003,0.03483],"object_to_goal_dist_end":0.04587,"object_to_goal_dist_start":0.13036,"object_z_max":0.03526,"peak_contact_force":0.91604,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1938.0,"raw_peak_contact_force":17.00156,"subtask_id":"push_through_channel","tcp_end":[0.49712,-0.00495,0.03239],"tcp_start":[0.50802,0.07551,0.03881],"tcp_to_object_dist_end":0.03009,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```