## Search State

- **Seed**: 2
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → align → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.1348 | 0.16 | ❌ rejected |
| 4 | approach → align → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | 0.2429 | 0.22 | ❌ rejected |
| 3 | approach → align → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | 0.2510 | 0.24 | ✅ accepted |
| 2 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 4 | 0.1662 | 0.18 | ✅ accepted |
| 1 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1703 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.16 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`
- Frozen object start: [0.48092897073994534, 0.06387929147312987, 0.04]
- Frozen task target: [0.48092897073994534, -0.09612070852687013, 0.04]
- Goal object position: (0.48092897073994534, -0.09612070852687013, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48092897073994534, 0.06387929147312987, 0.04)
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
  frozen_object_start: [0.4809, 0.0639, 0.04]
  frozen_task_target: [0.4809, -0.0961, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48092897073994534, 0.06387929147312987, 0.04]}
  frozen_targets: {'channel_exit': [0.48092897073994534, -0.09612070852687013, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7

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
| `object` | offset from object initial position (0.48092897073994534, 0.06387929147312987, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.48092897073994534, -0.09612070852687013, 0.04) | final destination targets |
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

## Current Skill (Q=-0.135) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: pre_push
  anchor: object
  offset:
  - 0.0
  - 0.04
  - 0.0
  weight: 0.3
- id: final_push
  weight: 0.7
phases:
- id: approach_high
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.15
    - 0.1
  parameters:
    approach_y_offset:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.y
        mode: replace
    approach_z_offset:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: pre_push
- id: lateral_align
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.04
    - 0.1
  parameters:
    lateral_y_offset:
      type: scalar
      range:
      - 0.0
      - 0.08
      default: 0.04
      binds_to:
      - path: target.offset.y
        mode: replace
  subtask_id: pre_push
- id: vertical_descend
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.04
    - 0.0
  subtask_id: pre_push
- id: push_through_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    entity: channel_exit
    offset:
    - 0.0
    - 0.0
    - 0.02
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.07
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: final_push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_high** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.15, 0.1]
  - parameter_bindings:
    - approach_y_offset: status=consumed; consumers=target.offset.y (replace)
    - approach_z_offset: status=consumed; consumers=target.offset.z (replace)
- **lateral_align** (`align`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.1]
  - parameter_bindings:
    - lateral_y_offset: status=consumed; consumers=target.offset.y (replace)
- **vertical_descend** (`align`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.0]
  - parameter_bindings: none
- **push_through_channel** (`push`)
  - target: source=yaml, anchor=task_goal, entity=channel_exit, offset=[0.0, 0.0, 0.02]
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.135
- **task_score** (E): 0.164
- **fitness_score**: 0.175  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_high | 1.00 | 0.1221 |
| lateral_align | 1.00 | 0.0841 |
| vertical_descend | 1.00 | 0.0973 |
| push_through_channel | 1.00 | 0.0660 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.496, 0.194, 0.182) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 |
| lateral_align | align | 1.00 / step_budget | (0.496, 0.194, 0.182)→(0.495, 0.121, 0.142) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 |
| vertical_descend | align | 1.00 / step_budget | (0.495, 0.121, 0.142)→(0.499, 0.087, 0.052) | (0.498, 0.068, 0.034)→(0.499, 0.062, 0.030) | 0.148→0.143 |
| push_through_channel | push | 1.00 / time_limit | (0.499, 0.087, 0.052)→(0.495, 0.152, 0.046) | (0.499, 0.062, 0.030)→(0.499, -0.009, 0.024) | 0.143→0.075 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.315
- alignment_error: None
- terminal_score: 0.204
- phase_score: 0.206
- phase_breakdown.pre_push_score: 0.662
- phase_breakdown.final_push_score: 0.011

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.205
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.210
- **Median Q (composite search score)**: -0.121
- **K-run variance**: 0.0010
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.517


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `6269840a353345700ffa70ea476a3ad730b138bf2ec3c52304c054f0e194e023`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a2936262b79fcd5a49fda15d77b54223f43c58bfee2e71dc505f8a2f79369706`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58475,"average_solve_count":118.0,"average_success_count":118.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_y_offset":0.08976,"approach_high.approach_z_offset":0.09879,"lateral_align.lateral_y_offset":0.02938,"push_through_channel.push_distance":0.16319,"push_through_channel.push_speed":0.03813},"optimized_scores":{"best_composite_score":-0.10466,"best_fitness_score":0.20534,"best_task_score":0.20421},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":216.0,"contact_point_centroid":[0.4968,0.06485,0.00919],"force_p95":197.21837,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":204.35558,"mean_force":29.77477,"phase_index":2.0,"phase_name":"vertical_descend","phase_type":"align","tcp_position_centroid":[0.49012,0.0999,0.09669]},{"body_a":"attachment","body_b":"peg","contact_count":40.0,"contact_point_centroid":[0.50196,0.07876,0.05463],"force_p95":203.24936,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":203.90844,"mean_force":157.97432,"phase_index":2.0,"phase_name":"vertical_descend","phase_type":"align","tcp_position_centroid":[0.49259,0.08462,0.05687]},{"body_a":"peg","body_b":"channel_base_body","contact_count":989.0,"contact_point_centroid":[0.49538,0.01646,0.00812],"force_p95":0.77007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":128.44976,"mean_force":1.3531,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49181,0.11506,0.04649]},{"body_a":"attachment","body_b":"peg","contact_count":18.0,"contact_point_centroid":[0.49787,0.07339,0.05193],"force_p95":127.07175,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":127.58829,"mean_force":41.55328,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49513,0.08272,0.05129]},{"body_a":"peg","body_b":"channel_base_body","contact_count":86.0,"contact_point_centroid":[0.49696,0.06357,0.00925],"force_p95":1.26088,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.64305,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49257,0.1815,0.23332]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49908,0.19785,0.29265]},{"body_a":"peg","body_b":"channel_base_body","contact_count":91.0,"contact_point_centroid":[0.49568,0.06465,0.00939],"force_p95":0.55905,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56397,"mean_force":0.54573,"phase_index":1.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.48727,0.1451,0.16506]}],"total_contact_groups":7},"final_pose_error":0.07636,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49459,0.01351,0.02405],"final_tcp_position":[0.49171,0.14618,0.04564],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"phases":[{"n_steps":113.0,"n_steps_budget":1000.0,"object_pos_end":[0.49524,0.06385,0.03387],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14406,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_push","tcp_end":[0.48696,0.16809,0.18605],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.18465,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":91.0,"n_steps_budget":600.0,"object_pos_end":[0.49498,0.06397,0.03389],"object_pos_start":[0.49524,0.06385,0.03387],"object_to_goal_dist_end":0.14418,"object_to_goal_dist_start":0.14406,"object_z_max":0.03389,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"pre_push","tcp_end":[0.49003,0.11929,0.14722],"tcp_start":[0.48696,0.16809,0.18605],"tcp_to_object_dist_end":0.12621,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":216.0,"n_steps_budget":780.0,"object_pos_end":[0.49596,0.05913,0.0296],"object_pos_start":[0.49498,0.06397,0.03389],"object_to_goal_dist_end":0.13958,"object_to_goal_dist_start":0.14418,"object_z_max":0.03392,"phase_name":"vertical_descend","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"pre_push","tcp_end":[0.49554,0.08251,0.05175],"tcp_start":[0.49003,0.11929,0.14722],"tcp_to_object_dist_end":0.03221,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49459,0.01351,0.02405],"object_pos_start":[0.49596,0.05913,0.0296],"object_to_goal_dist_end":0.09501,"object_to_goal_dist_start":0.13958,"object_z_max":0.0408,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"final_push","tcp_end":[0.49171,0.14618,0.04564],"tcp_start":[0.49554,0.08251,0.05175],"tcp_to_object_dist_end":0.13445,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `78f29ebb38dd2df9149fb0cd7c7c33d55e802bb94eee599b284bb0b197a04fb7`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.544,"average_solve_count":125.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_y_offset":0.14134,"approach_high.approach_z_offset":0.08314,"lateral_align.lateral_y_offset":0.02948,"push_through_channel.push_distance":0.17457,"push_through_channel.push_speed":0.02998},"optimized_scores":{"best_composite_score":-0.12072,"best_fitness_score":0.18928,"best_task_score":0.21004},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":201.0,"contact_point_centroid":[0.49527,0.05931,0.00917],"force_p95":147.02479,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":197.09836,"mean_force":22.51039,"phase_index":2.0,"phase_name":"vertical_descend","phase_type":"align","tcp_position_centroid":[0.48812,0.09694,0.09308]},{"body_a":"attachment","body_b":"peg","contact_count":37.0,"contact_point_centroid":[0.49813,0.07347,0.05483],"force_p95":185.71058,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":196.59196,"mean_force":119.35433,"phase_index":2.0,"phase_name":"vertical_descend","phase_type":"align","tcp_position_centroid":[0.49081,0.08125,0.0566]},{"body_a":"peg","body_b":"channel_base_body","contact_count":955.0,"contact_point_centroid":[0.49898,-0.06745,0.00818],"force_p95":0.74089,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.62772,"mean_force":0.65607,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48956,0.1044,0.04617]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52513,-0.04548,0.0313],"force_p95":6.05764,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.1832,"mean_force":1.89414,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4894,0.08497,0.04642]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":14.0,"contact_point_centroid":[0.47496,-0.08808,0.03045],"force_p95":5.26422,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.4223,"mean_force":2.45922,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48925,0.08913,0.04616]},{"body_a":"peg","body_b":"channel_base_body","contact_count":11.0,"contact_point_centroid":[0.51371,-0.10025,0.02803],"force_p95":2.52881,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.45981,"mean_force":0.57201,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48924,0.08562,0.04622]},{"body_a":"peg","body_b":"channel_base_body","contact_count":94.0,"contact_point_centroid":[0.49545,0.05881,0.0092],"force_p95":1.54807,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.70136,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.4867,0.19971,0.22504]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49809,0.19978,0.28904]},{"body_a":"peg","body_b":"channel_base_body","contact_count":139.0,"contact_point_centroid":[0.49432,0.05883,0.00938],"force_p95":0.55338,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55647,"mean_force":0.54643,"phase_index":1.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.48014,0.15998,0.15243]}],"total_contact_groups":9},"final_pose_error":0.09729,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49897,-0.07146,0.02413],"final_tcp_position":[0.48996,0.12812,0.04606],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"phases":[{"n_steps":123.0,"n_steps_budget":1000.0,"object_pos_end":[0.49416,0.05893,0.0338],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13919,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_push","tcp_end":[0.47673,0.19969,0.17198],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.19802,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":139.0,"n_steps_budget":750.0,"object_pos_end":[0.4942,0.05901,0.03383],"object_pos_start":[0.49416,0.05893,0.0338],"object_to_goal_dist_end":0.13926,"object_to_goal_dist_start":0.13919,"object_z_max":0.03383,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"pre_push","tcp_end":[0.48722,0.11673,0.1385],"tcp_start":[0.47673,0.19969,0.17198],"tcp_to_object_dist_end":0.11973,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":201.0,"n_steps_budget":750.0,"object_pos_end":[0.49589,0.05051,0.03147],"object_pos_start":[0.4942,0.05901,0.03383],"object_to_goal_dist_end":0.13085,"object_to_goal_dist_start":0.13926,"object_z_max":0.03386,"phase_name":"vertical_descend","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"pre_push","tcp_end":[0.49299,0.07891,0.05087],"tcp_start":[0.48722,0.11673,0.1385],"tcp_to_object_dist_end":0.03452,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49897,-0.07146,0.02413],"object_pos_start":[0.49589,0.05051,0.03147],"object_to_goal_dist_end":0.01805,"object_to_goal_dist_start":0.13085,"object_z_max":0.04455,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"final_push","tcp_end":[0.48996,0.12812,0.04606],"tcp_start":[0.49299,0.07891,0.05087],"tcp_to_object_dist_end":0.20098,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ecba62e37d233197bb248f7fe6e722b45204af5e83240a6f27138a89bcccfe42`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.60976,"average_solve_count":123.0,"average_success_count":123.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_y_offset":0.14078,"approach_high.approach_z_offset":0.10008,"lateral_align.lateral_y_offset":0.01765,"push_through_channel.push_distance":0.14011,"push_through_channel.push_speed":0.05123},"optimized_scores":{"best_composite_score":-0.17898,"best_fitness_score":0.13102,"best_task_score":0.07852},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":198.0,"contact_point_centroid":[0.50849,0.0828,0.0092],"force_p95":196.2687,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":202.39874,"mean_force":34.09737,"phase_index":2.0,"phase_name":"vertical_descend","phase_type":"align","tcp_position_centroid":[0.5055,0.11163,0.09383]},{"body_a":"attachment","body_b":"peg","contact_count":40.0,"contact_point_centroid":[0.5155,0.09487,0.05482],"force_p95":200.87943,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":201.7075,"mean_force":166.66411,"phase_index":2.0,"phase_name":"vertical_descend","phase_type":"align","tcp_position_centroid":[0.50548,0.09989,0.05689]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":22.0,"contact_point_centroid":[0.52505,0.09944,0.05998],"force_p95":151.75027,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":151.77324,"mean_force":80.96862,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50906,0.09941,0.05291]},{"body_a":"peg","body_b":"channel_base_body","contact_count":988.0,"contact_point_centroid":[0.50031,0.03515,0.00818],"force_p95":1.00009,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":133.80578,"mean_force":4.02727,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50397,0.14057,0.04663]},{"body_a":"attachment","body_b":"peg","contact_count":36.0,"contact_point_centroid":[0.51369,0.09002,0.05307],"force_p95":131.88057,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":133.44166,"mean_force":93.30752,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50887,0.09918,0.0527]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":10.0,"contact_point_centroid":[0.52505,0.07933,0.05623],"force_p95":10.85092,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.17878,"mean_force":6.74547,"phase_index":2.0,"phase_name":"vertical_descend","phase_type":"align","tcp_position_centroid":[0.50637,0.09933,0.05482]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":15.0,"contact_point_centroid":[0.52512,0.05263,0.02418],"force_p95":6.61111,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.98174,"mean_force":1.94536,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50421,0.11252,0.04705]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.47497,0.01892,0.03587],"force_p95":6.1286,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.42062,"mean_force":1.86275,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50439,0.12347,0.04722]},{"body_a":"peg","body_b":"channel_base_body","contact_count":84.0,"contact_point_centroid":[0.50398,0.08101,0.00923],"force_p95":1.95267,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.72857,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.51451,0.20851,0.23299]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.50271,0.20144,0.28875]},{"body_a":"peg","body_b":"channel_base_body","contact_count":142.0,"contact_point_centroid":[0.50611,0.0807,0.00938],"force_p95":0.55147,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55543,"mean_force":0.54667,"phase_index":1.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.51506,0.17252,0.16092]}],"total_contact_groups":11},"final_pose_error":0.03593,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5028,0.03085,0.02414],"final_tcp_position":[0.50305,0.18222,0.0453],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"phases":[{"n_steps":113.0,"n_steps_budget":1000.0,"object_pos_end":[0.506,0.08089,0.03377],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_push","tcp_end":[0.52414,0.21445,0.18717],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.2042,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":142.0,"n_steps_budget":810.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.506,0.08089,0.03377],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"pre_push","tcp_end":[0.50826,0.1272,0.1415],"tcp_start":[0.52414,0.21445,0.18717],"tcp_to_object_dist_end":0.11728,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":198.0,"n_steps_budget":720.0,"object_pos_end":[0.5066,0.07752,0.03024],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.15796,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"phase_name":"vertical_descend","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"pre_push","tcp_end":[0.50825,0.09835,0.05216],"tcp_start":[0.50826,0.1272,0.1415],"tcp_to_object_dist_end":0.03028,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5028,0.03085,0.02414],"object_pos_start":[0.5066,0.07752,0.03024],"object_to_goal_dist_end":0.11201,"object_to_goal_dist_start":0.15796,"object_z_max":0.0408,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"final_push","tcp_end":[0.50305,0.18222,0.0453],"tcp_start":[0.50825,0.09835,0.05216],"tcp_to_object_dist_end":0.15285,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```