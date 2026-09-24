## Search State

- **Seed**: 2
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → align → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0068 | 0.40 | ❌ rejected |
| 8 | approach → align → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | 0.2132 | 0.41 | ✅ accepted |
| 7 | approach → align → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | 0.2504 | 0.24 | ✅ accepted |
| 6 | approach → align → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | -0.0319 | 0.03 | ❌ rejected |
| 5 | approach → align → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.1348 | 0.16 | ❌ rejected |

**Proposal policy**: task_score is 0.40 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.007) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: pre_push
  anchor: object
  offset:
  - 0.0
  - 0.15
  - 0.1
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
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.15
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.1
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
  - target: source=yaml, anchor=task_goal, entity=channel_exit, offset=[0.0, 0.0, 0.0]
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.15
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.007
- **task_score** (E): 0.397
- **fitness_score**: 0.467  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_high | 0.67 | 0.1110 |
| lateral_align | 1.00 | 0.1042 |
| vertical_descend | 1.00 | 0.1017 |
| push_through_channel | 1.00 | 0.1740 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_high | approach | 0.67 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.222, 0.195) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 |
| lateral_align | align | 1.00 / step_budget | (0.497, 0.222, 0.195)→(0.496, 0.133, 0.145) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 |
| vertical_descend | align | 1.00 / step_budget | (0.496, 0.133, 0.145)→(0.494, 0.111, 0.046) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 |
| push_through_channel | push | 1.00 / time_limit | (0.494, 0.111, 0.046)→(0.499, -0.063, 0.039) | (0.498, 0.068, 0.034)→(0.498, -0.076, 0.027) | 0.148→0.017 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.829
- alignment_error: None
- terminal_score: 0.614
- phase_score: 0.532
- phase_breakdown.pre_push_score: 0.055
- phase_breakdown.final_push_score: 0.736

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.565
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.614
- **Median Q (composite search score)**: -0.030
- **K-run variance**: 0.0049
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.313


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.96491,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_tol":0.05167,"approach_high.approach_y_offset":0.15363,"approach_high.approach_z_offset":0.12297,"lateral_align.lateral_tol":0.03052,"lateral_align.lateral_y_offset":0.03949,"push_through_channel.push_speed":0.12214,"push_through_channel.push_time_limit":1.92719,"vertical_descend.descend_tol":0.011},"optimized_scores":{"best_composite_score":0.10463,"best_fitness_score":0.56463,"best_task_score":0.61416},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":361.0,"contact_point_centroid":[0.555,0.04755,0.05998],"force_p95":287.65974,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":684.44676,"mean_force":83.45926,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49152,0.05016,0.04028]},{"body_a":"channel_base_body","body_b":"link7","contact_count":34.0,"contact_point_centroid":[0.56768,-0.10017,0.06492],"force_p95":179.31613,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":180.82141,"mean_force":153.27675,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49872,-0.06473,0.03882]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":5.0,"contact_point_centroid":[0.47497,0.10394,0.04458],"force_p95":164.59319,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":170.95278,"mean_force":106.72606,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48574,0.10392,0.03934]},{"body_a":"attachment","body_b":"peg","contact_count":727.0,"contact_point_centroid":[0.50094,0.00591,0.0385],"force_p95":155.23219,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":166.53953,"mean_force":66.1309,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49396,0.0117,0.04023]},{"body_a":"peg","body_b":"channel_base_body","contact_count":880.0,"contact_point_centroid":[0.50358,-0.00055,0.0088],"force_p95":132.58868,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":142.95641,"mean_force":44.4905,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4932,0.02259,0.04026]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":513.0,"contact_point_centroid":[0.52582,-0.00461,0.02604],"force_p95":77.17572,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.55643,"mean_force":43.0603,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49363,0.01475,0.04029]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":57.0,"contact_point_centroid":[0.47471,-0.08226,0.02255],"force_p95":24.18693,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.16273,"mean_force":15.50373,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49858,-0.06363,0.0388]},{"body_a":"peg","body_b":"channel_base_body","contact_count":58.0,"contact_point_centroid":[0.49868,0.06402,0.00918],"force_p95":1.54361,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.69131,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49327,0.2062,0.24625]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49911,0.2007,0.29245]},{"body_a":"peg","body_b":"channel_base_body","contact_count":147.0,"contact_point_centroid":[0.49484,0.06355,0.00939],"force_p95":0.56467,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59693,"mean_force":0.5453,"phase_index":1.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.48875,0.17161,0.17848]},{"body_a":"peg","body_b":"channel_base_body","contact_count":316.0,"contact_point_centroid":[0.49526,0.06414,0.00939],"force_p95":0.5502,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55295,"mean_force":0.54582,"phase_index":2.0,"phase_name":"vertical_descend","phase_type":"align","tcp_position_centroid":[0.49009,0.11777,0.0955]}],"total_contact_groups":11},"final_pose_error":0.01534,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49194,-0.06883,0.02369],"final_tcp_position":[0.49881,-0.06474,0.03897],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"phases":[{"n_steps":85.0,"n_steps_budget":870.0,"object_pos_end":[0.49508,0.06406,0.03385],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14427,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_push","tcp_end":[0.48862,0.21029,0.21242],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.23089,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":147.0,"n_steps_budget":840.0,"object_pos_end":[0.49525,0.06388,0.03389],"object_pos_start":[0.49508,0.06406,0.03385],"object_to_goal_dist_end":0.14409,"object_to_goal_dist_start":0.14427,"object_z_max":0.03389,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"pre_push","tcp_end":[0.4913,0.12955,0.14825],"tcp_start":[0.48862,0.21029,0.21242],"tcp_to_object_dist_end":0.13193,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":316.0,"n_steps_budget":750.0,"object_pos_end":[0.49495,0.06401,0.03394],"object_pos_start":[0.49525,0.06388,0.03389],"object_to_goal_dist_end":0.14423,"object_to_goal_dist_start":0.14409,"object_z_max":0.03394,"phase_name":"vertical_descend","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"pre_push","tcp_end":[0.49089,0.10631,0.04343],"tcp_start":[0.4913,0.12955,0.14825],"tcp_to_object_dist_end":0.04354,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":931.0,"n_steps_budget":960.0,"object_pos_end":[0.49194,-0.06883,0.02369],"object_pos_start":[0.49495,0.06401,0.03394],"object_to_goal_dist_end":0.02135,"object_to_goal_dist_start":0.14423,"object_z_max":0.04021,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"final_push","tcp_end":[0.49881,-0.06474,0.03897],"tcp_start":[0.49089,0.10631,0.04343],"tcp_to_object_dist_end":0.01724,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.96667,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_tol":0.03495,"approach_high.approach_y_offset":0.15238,"approach_high.approach_z_offset":0.12743,"lateral_align.lateral_tol":0.04497,"lateral_align.lateral_y_offset":0.01742,"push_through_channel.push_speed":0.10858,"push_through_channel.push_time_limit":1.73906,"vertical_descend.descend_tol":0.01927},"optimized_scores":{"best_composite_score":-0.03011,"best_fitness_score":0.42989,"best_task_score":0.26998},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.56983,-0.10013,0.06494],"force_p95":147.24125,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":150.60938,"mean_force":112.72206,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49921,-0.06478,0.03945]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":21.0,"contact_point_centroid":[0.47498,0.10089,0.05221],"force_p95":116.5593,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":118.57163,"mean_force":70.99625,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48578,0.10087,0.04703]},{"body_a":"attachment","body_b":"peg","contact_count":850.0,"contact_point_centroid":[0.49887,0.00255,0.04163],"force_p95":87.9183,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":97.65237,"mean_force":42.90615,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49292,0.01182,0.04362]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49927,-0.0048,0.00902],"force_p95":85.72194,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":91.04981,"mean_force":36.10124,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49215,0.02144,0.04399]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":149.0,"contact_point_centroid":[0.47488,-0.04741,0.02266],"force_p95":28.31193,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.36357,"mean_force":17.23987,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49775,-0.05426,0.0397]},{"body_a":"peg","body_b":"channel_base_body","contact_count":48.0,"contact_point_centroid":[0.47818,-0.10015,0.02321],"force_p95":29.32928,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.33499,"mean_force":20.48137,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49876,-0.06229,0.03942]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":147.0,"contact_point_centroid":[0.52501,-0.05609,0.04529],"force_p95":15.65245,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.85193,"mean_force":11.44956,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49462,-0.00198,0.04375]},{"body_a":"peg","body_b":"channel_base_body","contact_count":100.0,"contact_point_centroid":[0.49552,0.05927,0.00921],"force_p95":1.35752,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.69198,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.48561,0.20401,0.24183]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49775,0.20032,0.29111]},{"body_a":"peg","body_b":"channel_base_body","contact_count":113.0,"contact_point_centroid":[0.49409,0.05903,0.00938],"force_p95":0.55333,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55479,"mean_force":0.5465,"phase_index":1.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.47989,0.16574,0.17525]},{"body_a":"peg","body_b":"channel_base_body","contact_count":198.0,"contact_point_centroid":[0.49401,0.05894,0.00939],"force_p95":0.55021,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55206,"mean_force":0.54634,"phase_index":2.0,"phase_name":"vertical_descend","phase_type":"align","tcp_position_centroid":[0.4876,0.1088,0.10147]}],"total_contact_groups":11},"final_pose_error":0.01501,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49438,-0.07428,0.02359],"final_tcp_position":[0.49929,-0.06501,0.03948],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"phases":[{"n_steps":129.0,"n_steps_budget":870.0,"object_pos_end":[0.49408,0.05895,0.0338],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13921,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_push","tcp_end":[0.47526,0.20731,0.20091],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.22426,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":113.0,"n_steps_budget":930.0,"object_pos_end":[0.49405,0.05893,0.03383],"object_pos_start":[0.49408,0.05895,0.0338],"object_to_goal_dist_end":0.13919,"object_to_goal_dist_start":0.13921,"object_z_max":0.03383,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"pre_push","tcp_end":[0.48707,0.11688,0.14984],"tcp_start":[0.47526,0.20731,0.20091],"tcp_to_object_dist_end":0.12986,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":198.0,"n_steps_budget":750.0,"object_pos_end":[0.49405,0.05887,0.03386],"object_pos_start":[0.49405,0.05893,0.03383],"object_to_goal_dist_end":0.13914,"object_to_goal_dist_start":0.13919,"object_z_max":0.03386,"phase_name":"vertical_descend","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"pre_push","tcp_end":[0.48933,0.10175,0.05199],"tcp_start":[0.48707,0.11688,0.14984],"tcp_to_object_dist_end":0.0468,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49438,-0.07428,0.02359],"object_pos_start":[0.49405,0.05887,0.03386],"object_to_goal_dist_end":0.01826,"object_to_goal_dist_start":0.13914,"object_z_max":0.04029,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"final_push","tcp_end":[0.49929,-0.06501,0.03948],"tcp_start":[0.48933,0.10175,0.05199],"tcp_to_object_dist_end":0.01904,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.96639,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_tol":0.02941,"approach_high.approach_y_offset":0.18205,"approach_high.approach_z_offset":0.10697,"lateral_align.lateral_tol":0.03338,"lateral_align.lateral_y_offset":0.03824,"push_through_channel.push_speed":0.13379,"push_through_channel.push_time_limit":2.48793,"vertical_descend.descend_tol":0.01096},"optimized_scores":{"best_composite_score":-0.05402,"best_fitness_score":0.40598,"best_task_score":0.30833},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":284.0,"contact_point_centroid":[0.555,-0.00233,0.05999],"force_p95":79.42879,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":414.60357,"mean_force":54.98478,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49839,-0.0025,0.03772]},{"body_a":"attachment","body_b":"peg","contact_count":596.0,"contact_point_centroid":[0.5035,0.00969,0.0439],"force_p95":61.29332,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":104.9759,"mean_force":12.08022,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49834,0.02122,0.03784]},{"body_a":"peg","body_b":"channel_base_body","contact_count":75.0,"contact_point_centroid":[0.50661,-0.10113,0.0571],"force_p95":91.25274,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":95.15818,"mean_force":51.12394,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49889,-0.0555,0.03749]},{"body_a":"peg","body_b":"channel_base_body","contact_count":582.0,"contact_point_centroid":[0.50643,-0.0086,0.00976],"force_p95":18.86512,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.14404,"mean_force":6.36734,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4984,0.03469,0.03795]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":379.0,"contact_point_centroid":[0.52507,0.00387,0.02529],"force_p95":6.21119,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.61523,"mean_force":1.51745,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49826,0.03156,0.03788]},{"body_a":"peg","body_b":"channel_base_body","contact_count":178.0,"contact_point_centroid":[0.50514,0.0808,0.00931],"force_p95":0.85642,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.63248,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.51448,0.22692,0.22827]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.50165,0.20261,0.29217]},{"body_a":"peg","body_b":"channel_base_body","contact_count":143.0,"contact_point_centroid":[0.50609,0.08094,0.00938],"force_p95":0.55017,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55104,"mean_force":0.54677,"phase_index":1.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.51736,0.2034,0.15282]},{"body_a":"peg","body_b":"channel_base_body","contact_count":282.0,"contact_point_centroid":[0.50598,0.08087,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55023,"mean_force":0.54677,"phase_index":2.0,"phase_name":"vertical_descend","phase_type":"align","tcp_position_centroid":[0.50511,0.13807,0.09067]}],"total_contact_groups":9},"final_pose_error":0.02149,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50691,-0.08608,0.03496],"final_tcp_position":[0.49929,-0.05868,0.0374],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"phases":[{"n_steps":207.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_push","tcp_end":[0.52677,0.24968,0.17129],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.21871,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":143.0,"n_steps_budget":870.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"pre_push","tcp_end":[0.50924,0.15194,0.13781],"tcp_start":[0.52677,0.24968,0.17129],"tcp_to_object_dist_end":0.12603,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":282.0,"n_steps_budget":690.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"phase_name":"vertical_descend","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"pre_push","tcp_end":[0.50253,0.1243,0.04328],"tcp_start":[0.50924,0.15194,0.13781],"tcp_to_object_dist_end":0.0446,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":931.0,"n_steps_budget":960.0,"object_pos_end":[0.50691,-0.08608,0.03496],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.01049,"object_to_goal_dist_start":0.1611,"object_z_max":0.03724,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"final_push","tcp_end":[0.49929,-0.05868,0.0374],"tcp_start":[0.50253,0.1243,0.04328],"tcp_to_object_dist_end":0.02855,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```