## Search State

- **Seed**: 2
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → align → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | 0.2133 | 0.41 | ❌ rejected |
| 12 | approach → align → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.1805 | 0.07 | ❌ rejected |
| 11 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 6 | -0.1989 | 0.01 | ❌ rejected |
| 10 | approach → align → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | 0.2138 | 0.42 | ✅ accepted |
| 9 | approach → align → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0068 | 0.40 | ❌ rejected |

**Proposal policy**: task_score is 0.41 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.213) — your mutation base

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

- **Composite score**: 0.213
- **task_score** (E): 0.411
- **fitness_score**: 0.473  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_high | 1.00 | 0.1590 |
| lateral_align | 1.00 | 0.1070 |
| vertical_descend | 1.00 | 0.0879 |
| push_through_channel | 1.00 | 0.1709 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.492, 0.215, 0.146) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 |
| lateral_align | align | 1.00 / step_budget | (0.492, 0.215, 0.146)→(0.495, 0.112, 0.130) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 |
| vertical_descend | align | 1.00 / step_budget | (0.495, 0.112, 0.130)→(0.494, 0.108, 0.043) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 |
| push_through_channel | push | 1.00 / time_limit | (0.494, 0.108, 0.043)→(0.499, -0.063, 0.038) | (0.498, 0.068, 0.034)→(0.497, -0.078, 0.028) | 0.148→0.016 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.852
- alignment_error: None
- terminal_score: 0.619
- phase_score: 0.538
- phase_breakdown.pre_push_score: 0.050
- phase_breakdown.final_push_score: 0.747

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.570
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.619
- **Median Q (composite search score)**: 0.184
- **K-run variance**: 0.0050
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.343


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.96581,"average_solve_count":117.0,"average_success_count":117.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_y_offset":0.1793,"approach_high.approach_z_offset":0.09853,"lateral_align.lateral_y_offset":0.01853,"push_through_channel.push_speed":0.13688},"optimized_scores":{"best_composite_score":0.31045,"best_fitness_score":0.57045,"best_task_score":0.61877},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":345.0,"contact_point_centroid":[0.555,0.04181,0.05997],"force_p95":375.57999,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":749.32099,"mean_force":107.5537,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49158,0.047,0.04017]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.47494,0.09983,0.04319],"force_p95":231.55232,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":242.08497,"mean_force":150.69097,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48566,0.09981,0.03793]},{"body_a":"channel_base_body","body_b":"link7","contact_count":18.0,"contact_point_centroid":[0.56834,-0.10043,0.06481],"force_p95":184.10574,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":185.96149,"mean_force":143.03123,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49912,-0.06528,0.03881]},{"body_a":"attachment","body_b":"peg","contact_count":649.0,"contact_point_centroid":[0.50141,0.00872,0.04082],"force_p95":153.45893,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":164.68517,"mean_force":66.81444,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49385,0.01595,0.04027]},{"body_a":"peg","body_b":"channel_base_body","contact_count":776.0,"contact_point_centroid":[0.50498,-0.00217,0.00895],"force_p95":132.70469,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":142.99608,"mean_force":45.07679,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49327,0.0224,0.04017]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":556.0,"contact_point_centroid":[0.52562,0.00284,0.03156],"force_p95":71.50713,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":80.10123,"mean_force":35.84034,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49334,0.02386,0.04035]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":56.0,"contact_point_centroid":[0.4745,-0.08335,0.02344],"force_p95":35.64817,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.57127,"mean_force":21.16889,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49874,-0.06166,0.03885]},{"body_a":"peg","body_b":"channel_base_body","contact_count":463.0,"contact_point_centroid":[0.4955,0.06402,0.00937],"force_p95":0.59674,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56388,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.48878,0.21912,0.2193]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.4993,0.20019,0.29691]},{"body_a":"peg","body_b":"channel_base_body","contact_count":288.0,"contact_point_centroid":[0.49549,0.06387,0.00941],"force_p95":0.55067,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55403,"mean_force":0.54512,"phase_index":2.0,"phase_name":"vertical_descend","phase_type":"align","tcp_position_centroid":[0.48965,0.09521,0.08614]},{"body_a":"peg","body_b":"channel_base_body","contact_count":683.0,"contact_point_centroid":[0.495,0.06384,0.0094],"force_p95":0.5507,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55289,"mean_force":0.54541,"phase_index":1.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.48398,0.16276,0.1359]}],"total_contact_groups":11},"final_pose_error":0.01456,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49234,-0.07252,0.02417],"final_tcp_position":[0.49919,-0.0655,0.03896],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"phases":[{"n_steps":490.0,"n_steps_budget":1000.0,"object_pos_end":[0.4949,0.06387,0.03394],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14409,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_push","tcp_end":[0.47966,0.23817,0.1468],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.2082,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":683.0,"n_steps_budget":990.0,"object_pos_end":[0.49495,0.06362,0.03402],"object_pos_start":[0.4949,0.06387,0.03394],"object_to_goal_dist_end":0.14384,"object_to_goal_dist_start":0.14409,"object_z_max":0.03402,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"pre_push","tcp_end":[0.49077,0.09037,0.12975],"tcp_start":[0.47966,0.23817,0.1468],"tcp_to_object_dist_end":0.09948,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":288.0,"n_steps_budget":630.0,"object_pos_end":[0.4949,0.06409,0.03403],"object_pos_start":[0.49495,0.06362,0.03402],"object_to_goal_dist_end":0.1443,"object_to_goal_dist_start":0.14384,"object_z_max":0.03403,"phase_name":"vertical_descend","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"pre_push","tcp_end":[0.49047,0.10101,0.04241],"tcp_start":[0.49077,0.09037,0.12975],"tcp_to_object_dist_end":0.03812,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":811.0,"n_steps_budget":840.0,"object_pos_end":[0.49234,-0.07252,0.02417],"object_pos_start":[0.4949,0.06409,0.03403],"object_to_goal_dist_end":0.01912,"object_to_goal_dist_start":0.1443,"object_z_max":0.04032,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"final_push","tcp_end":[0.49919,-0.0655,0.03896],"tcp_start":[0.49047,0.10101,0.04241],"tcp_to_object_dist_end":0.01775,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.07547,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_y_offset":0.15289,"approach_high.approach_z_offset":0.10344,"lateral_align.lateral_y_offset":0.0394,"push_through_channel.push_speed":0.14642},"optimized_scores":{"best_composite_score":0.1838,"best_fitness_score":0.4438,"best_task_score":0.30563},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":338.0,"contact_point_centroid":[0.555,0.04053,0.05998],"force_p95":351.99276,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":723.91198,"mean_force":108.81764,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49119,0.04521,0.04039]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":10.0,"contact_point_centroid":[0.47496,0.09944,0.0435],"force_p95":356.59099,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":374.55556,"mean_force":161.49793,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4857,0.09943,0.03824]},{"body_a":"attachment","body_b":"peg","contact_count":554.0,"contact_point_centroid":[0.50134,0.006,0.04039],"force_p95":156.45119,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":167.09861,"mean_force":69.44464,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49363,0.01322,0.04043]},{"body_a":"channel_base_body","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.56779,-0.1003,0.06487],"force_p95":162.00489,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":164.28699,"mean_force":127.28063,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49894,-0.06494,0.0389]},{"body_a":"peg","body_b":"channel_base_body","contact_count":702.0,"contact_point_centroid":[0.50477,-0.0047,0.00895],"force_p95":134.4915,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":144.68076,"mean_force":44.22885,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4929,0.02135,0.04034]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":472.0,"contact_point_centroid":[0.52566,-0.00793,0.03034],"force_p95":74.51429,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.83002,"mean_force":38.31597,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49363,0.01296,0.04039]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":22.0,"contact_point_centroid":[0.47445,-0.0832,0.02311],"force_p95":28.74957,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.9517,"mean_force":18.88504,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49883,-0.06437,0.0389]},{"body_a":"peg","body_b":"channel_base_body","contact_count":420.0,"contact_point_centroid":[0.49456,0.05893,0.00934],"force_p95":0.59568,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.58105,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.48228,0.20443,0.2222]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49874,0.19975,0.29574]},{"body_a":"peg","body_b":"channel_base_body","contact_count":495.0,"contact_point_centroid":[0.49412,0.05905,0.00939],"force_p95":0.55036,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54606,"phase_index":1.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.47687,0.15682,0.13957]},{"body_a":"peg","body_b":"channel_base_body","contact_count":284.0,"contact_point_centroid":[0.49411,0.05899,0.0094],"force_p95":0.55026,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55169,"mean_force":0.54572,"phase_index":2.0,"phase_name":"vertical_descend","phase_type":"align","tcp_position_centroid":[0.48812,0.10259,0.08659]}],"total_contact_groups":11},"final_pose_error":0.01481,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49188,-0.07418,0.02391],"final_tcp_position":[0.49906,-0.06525,0.03897],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"phases":[{"n_steps":449.0,"n_steps_budget":1000.0,"object_pos_end":[0.49414,0.05907,0.03386],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13933,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_push","tcp_end":[0.4671,0.20951,0.15298],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.19379,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":495.0,"n_steps_budget":750.0,"object_pos_end":[0.49398,0.05907,0.03392],"object_pos_start":[0.49414,0.05907,0.03386],"object_to_goal_dist_end":0.13933,"object_to_goal_dist_start":0.13933,"object_z_max":0.03392,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"pre_push","tcp_end":[0.48882,0.10619,0.13041],"tcp_start":[0.4671,0.20951,0.15298],"tcp_to_object_dist_end":0.10751,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":284.0,"n_steps_budget":630.0,"object_pos_end":[0.49393,0.05907,0.03396],"object_pos_start":[0.49398,0.05907,0.03392],"object_to_goal_dist_end":0.13933,"object_to_goal_dist_start":0.13933,"object_z_max":0.03396,"phase_name":"vertical_descend","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"pre_push","tcp_end":[0.48936,0.09929,0.04253],"tcp_start":[0.48882,0.10619,0.13041],"tcp_to_object_dist_end":0.04138,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":751.0,"n_steps_budget":780.0,"object_pos_end":[0.49188,-0.07418,0.02391],"object_pos_start":[0.49393,0.05907,0.03396],"object_to_goal_dist_end":0.01893,"object_to_goal_dist_start":0.13933,"object_z_max":0.04026,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"final_push","tcp_end":[0.49906,-0.06525,0.03897],"tcp_start":[0.48936,0.09929,0.04253],"tcp_to_object_dist_end":0.01892,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.95495,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_y_offset":0.11744,"approach_high.approach_z_offset":0.08918,"lateral_align.lateral_y_offset":0.04894,"push_through_channel.push_speed":0.12437},"optimized_scores":{"best_composite_score":0.14553,"best_fitness_score":0.40553,"best_task_score":0.30949},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":406.0,"contact_point_centroid":[0.555,0.01188,0.05999],"force_p95":77.87944,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":482.39363,"mean_force":55.90955,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4984,0.01197,0.03782]},{"body_a":"attachment","body_b":"peg","contact_count":642.0,"contact_point_centroid":[0.50354,0.00761,0.0441],"force_p95":68.85933,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":103.88091,"mean_force":11.73626,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49838,0.01916,0.03787]},{"body_a":"peg","body_b":"channel_base_body","contact_count":80.0,"contact_point_centroid":[0.50679,-0.10118,0.05756],"force_p95":83.46119,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":103.37275,"mean_force":52.45932,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49901,-0.05555,0.03756]},{"body_a":"peg","body_b":"channel_base_body","contact_count":599.0,"contact_point_centroid":[0.50674,-0.00446,0.00978],"force_p95":17.87203,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.94645,"mean_force":6.17902,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49835,0.03878,0.03798]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":376.0,"contact_point_centroid":[0.5251,0.00791,0.02423],"force_p95":7.41268,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.57271,"mean_force":1.76295,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49832,0.03542,0.03793]},{"body_a":"peg","body_b":"channel_base_body","contact_count":493.0,"contact_point_centroid":[0.50568,0.08092,0.00936],"force_p95":0.56028,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57772,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.51444,0.19816,0.21382]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.50024,0.19954,0.29558]},{"body_a":"peg","body_b":"channel_base_body","contact_count":267.0,"contact_point_centroid":[0.50598,0.08074,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55008,"mean_force":0.54677,"phase_index":1.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.51675,0.16777,0.13083]},{"body_a":"peg","body_b":"channel_base_body","contact_count":271.0,"contact_point_centroid":[0.50592,0.0809,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54676,"phase_index":2.0,"phase_name":"vertical_descend","phase_type":"align","tcp_position_centroid":[0.50318,0.13048,0.08611]}],"total_contact_groups":9},"final_pose_error":0.0216,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50699,-0.08598,0.0351],"final_tcp_position":[0.49937,-0.05856,0.03747],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"phases":[{"n_steps":522.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_push","tcp_end":[0.52949,0.19731,0.13688],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15729,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":267.0,"n_steps_budget":600.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"pre_push","tcp_end":[0.50605,0.13835,0.12886],"tcp_start":[0.52949,0.19731,0.13688],"tcp_to_object_dist_end":0.1111,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":271.0,"n_steps_budget":630.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"phase_name":"vertical_descend","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"pre_push","tcp_end":[0.50205,0.12255,0.04275],"tcp_start":[0.50605,0.13835,0.12886],"tcp_to_object_dist_end":0.04279,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":991.0,"n_steps_budget":1000.0,"object_pos_end":[0.50699,-0.08598,0.0351],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.01042,"object_to_goal_dist_start":0.16113,"object_z_max":0.03729,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"final_push","tcp_end":[0.49937,-0.05856,0.03747],"tcp_start":[0.50205,0.12255,0.04275],"tcp_to_object_dist_end":0.02856,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```