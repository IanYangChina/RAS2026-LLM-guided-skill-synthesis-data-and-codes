## Search State

- **Seed**: 2
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → align → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | 0.2504 | 0.24 | ✅ accepted |
| 6 | approach → align → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | -0.0319 | 0.03 | ❌ rejected |
| 5 | approach → align → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.1348 | 0.16 | ❌ rejected |
| 4 | approach → align → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | 0.2429 | 0.22 | ❌ rejected |
| 3 | approach → align → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | 0.2510 | 0.24 | ✅ accepted |

**Proposal policy**: task_score is 0.24 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.250) — your mutation base

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

- **Composite score**: 0.250
- **task_score** (E): 0.237
- **fitness_score**: 0.510  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_high | 1.00 | 0.1475 |
| lateral_align | 1.00 | 0.1093 |
| vertical_descend | 1.00 | 0.0884 |
| push_through_channel | 1.00 | 0.1796 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.492, 0.215, 0.160) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 |
| lateral_align | align | 1.00 / step_budget | (0.492, 0.215, 0.160)→(0.494, 0.112, 0.131) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 |
| vertical_descend | align | 1.00 / step_budget | (0.494, 0.112, 0.131)→(0.494, 0.108, 0.043) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 |
| push_through_channel | push | 1.00 / time_limit | (0.494, 0.108, 0.043)→(0.496, -0.072, 0.054) | (0.498, 0.068, 0.034)→(0.496, -0.023, 0.024) | 0.148→0.059 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.530
- alignment_error: None
- terminal_score: 0.369
- phase_score: 0.746
- phase_breakdown.pre_push_score: 0.821
- phase_breakdown.final_push_score: 0.713

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.595
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.369
- **Median Q (composite search score)**: 0.229
- **K-run variance**: 0.0039
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.290


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88991,"average_solve_count":109.0,"average_success_count":109.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_y_offset":0.12138,"approach_high.approach_z_offset":0.09847,"lateral_align.lateral_y_offset":0.0368,"push_through_channel.push_speed":0.11194},"optimized_scores":{"best_composite_score":0.33485,"best_fitness_score":0.59485,"best_task_score":0.36876},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":487.0,"contact_point_centroid":[0.49655,0.03941,0.04152],"force_p95":35.15855,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.23079,"mean_force":16.85876,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4899,0.04783,0.04391]},{"body_a":"peg","body_b":"channel_base_body","contact_count":942.0,"contact_point_centroid":[0.50037,0.00538,0.00902],"force_p95":33.32656,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.44471,"mean_force":9.08918,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49149,0.01568,0.04678]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":110.0,"contact_point_centroid":[0.52516,0.00893,0.02652],"force_p95":16.43496,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.8621,"mean_force":12.82827,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49232,0.01262,0.04803]},{"body_a":"peg","body_b":"channel_base_body","contact_count":428.0,"contact_point_centroid":[0.49538,0.06392,0.00936],"force_p95":0.60146,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56538,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.48886,0.19211,0.22021]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49924,0.19933,0.29681]},{"body_a":"peg","body_b":"channel_base_body","contact_count":283.0,"contact_point_centroid":[0.49515,0.06394,0.0094],"force_p95":0.55088,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55289,"mean_force":0.54526,"phase_index":2.0,"phase_name":"vertical_descend","phase_type":"align","tcp_position_centroid":[0.48938,0.10577,0.08672]},{"body_a":"peg","body_b":"channel_base_body","contact_count":361.0,"contact_point_centroid":[0.49509,0.06393,0.0094],"force_p95":0.55044,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5516,"mean_force":0.5456,"phase_index":1.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.48389,0.14635,0.13748]}],"total_contact_groups":7},"final_pose_error":0.01053,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4932,-0.02098,0.02413],"final_tcp_position":[0.49562,-0.07226,0.05436],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"phases":[{"n_steps":455.0,"n_steps_budget":1000.0,"object_pos_end":[0.49509,0.06368,0.03394],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14389,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_push","tcp_end":[0.47978,0.18552,0.1484],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16787,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":361.0,"n_steps_budget":600.0,"object_pos_end":[0.49499,0.06363,0.03399],"object_pos_start":[0.49509,0.06368,0.03394],"object_to_goal_dist_end":0.14385,"object_to_goal_dist_start":0.14389,"object_z_max":0.03399,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"pre_push","tcp_end":[0.49026,0.10843,0.13048],"tcp_start":[0.47978,0.18552,0.1484],"tcp_to_object_dist_end":0.10648,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":283.0,"n_steps_budget":630.0,"object_pos_end":[0.49489,0.06367,0.03402],"object_pos_start":[0.49499,0.06363,0.03399],"object_to_goal_dist_end":0.14389,"object_to_goal_dist_start":0.14385,"object_z_max":0.03402,"phase_name":"vertical_descend","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"pre_push","tcp_end":[0.49043,0.10351,0.04263],"tcp_start":[0.49026,0.10843,0.13048],"tcp_to_object_dist_end":0.041,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":976.0,"n_steps_budget":1000.0,"object_pos_end":[0.4932,-0.02098,0.02413],"object_pos_start":[0.49489,0.06367,0.03402],"object_to_goal_dist_end":0.0615,"object_to_goal_dist_start":0.14389,"object_z_max":0.04056,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"final_push","tcp_end":[0.49562,-0.07226,0.05436],"tcp_start":[0.49043,0.10351,0.04263],"tcp_to_object_dist_end":0.05958,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89091,"average_solve_count":110.0,"average_success_count":110.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_y_offset":0.14554,"approach_high.approach_z_offset":0.11945,"lateral_align.lateral_y_offset":0.03956,"push_through_channel.push_speed":0.10813},"optimized_scores":{"best_composite_score":0.22883,"best_fitness_score":0.48883,"best_task_score":0.18592},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":968.0,"contact_point_centroid":[0.50004,0.00083,0.00906],"force_p95":29.24212,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.86029,"mean_force":8.66469,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49105,0.01303,0.04682]},{"body_a":"attachment","body_b":"peg","contact_count":500.0,"contact_point_centroid":[0.4961,0.03333,0.04157],"force_p95":29.73485,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.49216,"mean_force":15.87319,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48947,0.04172,0.04422]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":74.0,"contact_point_centroid":[0.52509,9e-05,0.02687],"force_p95":12.43452,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.0657,"mean_force":9.37208,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49234,0.00368,0.04867]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.47499,-0.00181,0.02411],"force_p95":8.88576,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.32943,"mean_force":4.89282,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49558,-0.07243,0.05437]},{"body_a":"peg","body_b":"channel_base_body","contact_count":369.0,"contact_point_centroid":[0.49439,0.05895,0.00934],"force_p95":0.60294,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.58585,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.48249,0.20102,0.23031]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49864,0.1996,0.2957]},{"body_a":"peg","body_b":"channel_base_body","contact_count":449.0,"contact_point_centroid":[0.49432,0.05891,0.00939],"force_p95":0.55042,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54614,"phase_index":1.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.47705,0.15402,0.14845]},{"body_a":"peg","body_b":"channel_base_body","contact_count":289.0,"contact_point_centroid":[0.49399,0.05883,0.00939],"force_p95":0.54995,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5514,"mean_force":0.54579,"phase_index":2.0,"phase_name":"vertical_descend","phase_type":"align","tcp_position_centroid":[0.48811,0.10275,0.08735]}],"total_contact_groups":8},"final_pose_error":0.01026,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49301,-0.02674,0.02416],"final_tcp_position":[0.49559,-0.07263,0.05439],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"phases":[{"n_steps":398.0,"n_steps_budget":900.0,"object_pos_end":[0.49416,0.05886,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13912,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_push","tcp_end":[0.46759,0.20287,0.16908],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.19933,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":449.0,"n_steps_budget":720.0,"object_pos_end":[0.49417,0.05912,0.0339],"object_pos_start":[0.49416,0.05886,0.03385],"object_to_goal_dist_end":0.13937,"object_to_goal_dist_start":0.13912,"object_z_max":0.0339,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"pre_push","tcp_end":[0.48868,0.10645,0.13191],"tcp_start":[0.46759,0.20287,0.16908],"tcp_to_object_dist_end":0.10898,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":289.0,"n_steps_budget":630.0,"object_pos_end":[0.49433,0.05902,0.03394],"object_pos_start":[0.49417,0.05912,0.0339],"object_to_goal_dist_end":0.13927,"object_to_goal_dist_start":0.13937,"object_z_max":0.03395,"phase_name":"vertical_descend","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"pre_push","tcp_end":[0.48952,0.09936,0.04262],"tcp_start":[0.48868,0.10645,0.13191],"tcp_to_object_dist_end":0.04154,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49301,-0.02674,0.02416],"object_pos_start":[0.49433,0.05902,0.03394],"object_to_goal_dist_end":0.056,"object_to_goal_dist_start":0.13927,"object_z_max":0.04054,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"final_push","tcp_end":[0.49559,-0.07263,0.05439],"tcp_start":[0.48952,0.09936,0.04262],"tcp_to_object_dist_end":0.05501,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90164,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_y_offset":0.18238,"approach_high.approach_z_offset":0.1162,"lateral_align.lateral_y_offset":0.02999,"push_through_channel.push_speed":0.11917},"optimized_scores":{"best_composite_score":0.18748,"best_fitness_score":0.44748,"best_task_score":0.15579},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":518.0,"contact_point_centroid":[0.50325,0.04444,0.04311],"force_p95":40.27437,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.46194,"mean_force":17.82541,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49772,0.05423,0.04434]},{"body_a":"peg","body_b":"channel_base_body","contact_count":892.0,"contact_point_centroid":[0.50574,0.00814,0.00905],"force_p95":36.30268,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.15448,"mean_force":10.08626,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49742,0.02116,0.0471]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":363.0,"contact_point_centroid":[0.52508,0.03023,0.02626],"force_p95":14.00767,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.72985,"mean_force":7.18693,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4976,0.05423,0.04427]},{"body_a":"peg","body_b":"channel_base_body","contact_count":492.0,"contact_point_centroid":[0.50565,0.0809,0.00936],"force_p95":0.56028,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57778,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.51471,0.22912,0.2259]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.50033,0.20092,0.29595]},{"body_a":"peg","body_b":"channel_base_body","contact_count":575.0,"contact_point_centroid":[0.50598,0.08084,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55008,"mean_force":0.54676,"phase_index":1.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.51584,0.18807,0.1432]},{"body_a":"peg","body_b":"channel_base_body","contact_count":275.0,"contact_point_centroid":[0.50603,0.08084,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54677,"phase_index":2.0,"phase_name":"vertical_descend","phase_type":"align","tcp_position_centroid":[0.50218,0.11966,0.08681]}],"total_contact_groups":7},"final_pose_error":0.01236,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50211,-0.0219,0.02409],"final_tcp_position":[0.49612,-0.0698,0.0542],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"phases":[{"n_steps":521.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_push","tcp_end":[0.52978,0.25693,0.16125],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.21865,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":575.0,"n_steps_budget":960.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"pre_push","tcp_end":[0.50438,0.1201,0.13041],"tcp_start":[0.52978,0.25693,0.16125],"tcp_to_object_dist_end":0.10429,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":275.0,"n_steps_budget":630.0,"object_pos_end":[0.50595,0.08088,0.03378],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.16111,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"phase_name":"vertical_descend","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"pre_push","tcp_end":[0.50182,0.11987,0.04278],"tcp_start":[0.50438,0.1201,0.13041],"tcp_to_object_dist_end":0.04023,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50211,-0.0219,0.02409],"object_pos_start":[0.50595,0.08088,0.03378],"object_to_goal_dist_end":0.06028,"object_to_goal_dist_start":0.16111,"object_z_max":0.04023,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"final_push","tcp_end":[0.49612,-0.0698,0.0542],"tcp_start":[0.50182,0.11987,0.04278],"tcp_to_object_dist_end":0.05689,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```