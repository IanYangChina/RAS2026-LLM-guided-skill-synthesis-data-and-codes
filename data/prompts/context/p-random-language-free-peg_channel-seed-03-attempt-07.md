## Search State

- **Seed**: 3
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 2 | 0.3966 | 0.31 | ✅ accepted |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 2 | 0.3725 | 0.31 | ✅ accepted |
| 5 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 3 | 0.5386 | 0.24 | ✅ accepted |
| 4 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 3 | 0.4977 | 0.22 | ✅ accepted |
| 3 | approach → descend → push → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.2072 | 0.11 | ❌ rejected |

**Proposal policy**: task_score is 0.31 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`
- Frozen object start: [0.46685193337148995, 0.058944840527687975, 0.04]
- Frozen task target: [0.46685193337148995, -0.10105515947231203, 0.04]
- Goal object position: (0.46685193337148995, -0.10105515947231203, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.46685193337148995, 0.058944840527687975, 0.04)
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
  frozen_object_start: [0.4669, 0.0589, 0.04]
  frozen_task_target: [0.4669, -0.1011, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.46685193337148995, 0.058944840527687975, 0.04]}
  frozen_targets: {'channel_exit': [0.46685193337148995, -0.10105515947231203, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834

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
| `object` | offset from object initial position (0.46685193337148995, 0.058944840527687975, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.46685193337148995, -0.10105515947231203, 0.04) | final destination targets |
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

## Current Skill (Q=0.397) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach_peg
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.15
  weight: 0.3
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_behind
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
    - 0.05
    - 0.15
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: approach_peg
- id: align_descend
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.03
    - 0.0
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.05
  subtask_id: approach_peg
- id: push_along_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.03
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.12
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  retries:
    max_attempts: 1
    strategy: repeat
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.15], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **align_descend** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.0], tolerance=0.01
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings: none
- **push_along_channel** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - retries: max_attempts=1, strategy=repeat

## Design Metrics

- **Composite score**: 0.397
- **task_score** (E): 0.310
- **fitness_score**: 0.527  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.130

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.1333 |
| align_descend | 1.00 | 1.00 | 0.1454 |
| push_along_channel | 1.00 | 1.00 | 0.1575 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.142, 0.184) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.547 | 3.954 |
| align_descend | descend | 1.00 / step_budget | (0.505, 0.142, 0.184)→(0.499, 0.113, 0.043) | (0.502, 0.081, 0.034)→(0.502, 0.082, 0.034) | 0.162→0.162 | 1.00 / 1.000 | 0.544 | 117.863 |
| push_along_channel | push | 1.00 / step_budget | (0.499, 0.113, 0.043)→(0.501, -0.044, 0.032) | (0.502, 0.082, 0.034)→(0.507, -0.073, 0.039) | 0.162→0.010 | 1.00 / 3.333 | 47.765 | 112.883 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.509
- phase_score: 0.664
- phase_breakdown.approach_peg_score: 0.050
- phase_breakdown.push_to_goal_score: 0.927

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.602
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.509
- **Median Q (composite search score)**: 0.397
- **K-run variance**: 0.0038
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 11.0
- **Final σ (mean)**: 0.341


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `cc7283febf3c95cef1fde4c5a16cbcb134186cb6faf3a169717a9aa53375931d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `178d67757a065da6e29d31070e25f6065dc7e42bdbf58dfbff0deec513214033`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9902,"average_solve_count":102.0,"average_success_count":102.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_height":0.12336,"push_along_channel.push_distance":0.16389},"optimized_scores":{"best_composite_score":0.32063,"best_fitness_score":0.45063,"best_task_score":0.13274},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":5.0,"contact_point_centroid":[0.47494,0.09487,0.0596],"force_p95":303.28679,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":352.45715,"mean_force":104.83996,"phase_index":1.0,"phase_name":"align_descend","phase_type":"descend","tcp_position_centroid":[0.48603,0.09418,0.05545]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":425.0,"contact_point_centroid":[0.555,-0.00283,0.05998],"force_p95":148.09686,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":166.19082,"mean_force":107.74458,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49199,-0.00565,0.03608]},{"body_a":"attachment","body_b":"peg","contact_count":593.0,"contact_point_centroid":[0.49895,-0.00934,0.03505],"force_p95":105.00735,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.30348,"mean_force":70.11029,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49173,-0.00162,0.03621]},{"body_a":"peg","body_b":"channel_base_body","contact_count":631.0,"contact_point_centroid":[0.50738,-0.028,0.00963],"force_p95":81.31024,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":96.49626,"mean_force":37.08038,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49149,0.00235,0.03632]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":585.0,"contact_point_centroid":[0.52592,-0.02204,0.02527],"force_p95":72.91147,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":77.36265,"mean_force":48.03293,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49182,-0.00363,0.03612]},{"body_a":"peg","body_b":"channel_base_body","contact_count":81.0,"contact_point_centroid":[0.50815,-0.10066,0.05101],"force_p95":58.32674,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":69.29323,"mean_force":40.17129,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49558,-0.04211,0.03531]},{"body_a":"peg","body_b":"link7","contact_count":204.0,"contact_point_centroid":[0.51745,-0.01934,0.06936],"force_p95":33.86414,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.69951,"mean_force":12.12472,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49062,0.00721,0.03637]},{"body_a":"peg","body_b":"channel_base_body","contact_count":254.0,"contact_point_centroid":[0.49458,0.05909,0.00931],"force_p95":0.67079,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.60375,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48313,0.15784,0.2336]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49827,0.19651,0.29445]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":5.0,"contact_point_centroid":[0.47494,0.04876,0.06],"force_p95":0.61699,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63788,"mean_force":0.45141,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48689,0.08039,0.03872]},{"body_a":"peg","body_b":"channel_base_body","contact_count":473.0,"contact_point_centroid":[0.49421,0.05879,0.00939],"force_p95":0.55027,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55326,"mean_force":0.5462,"phase_index":1.0,"phase_name":"align_descend","phase_type":"descend","tcp_position_centroid":[0.47793,0.10482,0.10831]}],"total_contact_groups":11},"final_pose_error":0.0291,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50856,-0.07418,0.03976],"final_tcp_position":[0.49632,-0.04586,0.03508],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":352.45715,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":283.0,"n_steps_budget":1000.0,"object_pos_end":[0.49407,0.05888,0.03384],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13915,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54846,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":289.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach_peg","tcp_end":[0.46935,0.12145,0.17855],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15958,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":473.0,"n_steps_budget":960.0,"object_pos_end":[0.49425,0.05904,0.03389],"object_pos_start":[0.49407,0.05888,0.03384],"object_to_goal_dist_end":0.13929,"object_to_goal_dist_start":0.13915,"object_z_max":0.03389,"peak_contact_force":0.54722,"phase_name":"align_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":478.0,"raw_peak_contact_force":352.45715,"subtask_id":"approach_peg","tcp_end":[0.48838,0.09105,0.04149],"tcp_start":[0.46935,0.12145,0.17855],"tcp_to_object_dist_end":0.03342,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":677.0,"n_steps_budget":1000.0,"object_pos_end":[0.50856,-0.07418,0.03976],"object_pos_start":[0.49425,0.05904,0.03389],"object_to_goal_dist_end":0.01036,"object_to_goal_dist_start":0.13929,"object_z_max":0.04102,"peak_contact_force":141.99478,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2524.0,"raw_peak_contact_force":166.19082,"subtask_id":"push_to_goal","tcp_end":[0.49632,-0.04586,0.03508],"tcp_start":[0.48838,0.09105,0.04149],"tcp_to_object_dist_end":0.0312,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1ee374347cb6f80436633ebcb956aaa73ea8a10685d65b21d5c3814cf0c53498`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9902,"average_solve_count":102.0,"average_success_count":102.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_height":0.1413,"push_along_channel.push_distance":0.1766},"optimized_scores":{"best_composite_score":0.397,"best_fitness_score":0.527,"best_task_score":0.28709},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.555,-0.04326,0.05999],"force_p95":82.02538,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":82.72033,"mean_force":73.78033,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50213,-0.04405,0.03016]},{"body_a":"attachment","body_b":"peg","contact_count":210.0,"contact_point_centroid":[0.5042,0.02428,0.0478],"force_p95":26.43229,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.87987,"mean_force":5.20936,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50165,0.03558,0.03495]},{"body_a":"peg","body_b":"channel_base_body","contact_count":16.0,"contact_point_centroid":[0.50506,-0.1004,0.05796],"force_p95":30.40426,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.94118,"mean_force":15.62401,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50219,-0.04375,0.03023]},{"body_a":"peg","body_b":"channel_base_body","contact_count":193.0,"contact_point_centroid":[0.50202,-0.01379,0.0095],"force_p95":24.80796,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.86677,"mean_force":5.3422,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50185,0.02611,0.03457]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":92.0,"contact_point_centroid":[0.52525,0.02548,0.03171],"force_p95":8.52575,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.44046,"mean_force":1.65147,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50174,0.05691,0.03654]},{"body_a":"peg","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.51698,-0.07003,0.06819],"force_p95":12.37704,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.82971,"mean_force":3.25785,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50211,-0.04047,0.03039]},{"body_a":"peg","body_b":"channel_base_body","contact_count":215.0,"contact_point_centroid":[0.50521,0.08085,0.00932],"force_p95":0.69672,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.61772,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.51415,0.16834,0.24228]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50101,0.19692,0.2943]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":22.0,"contact_point_centroid":[0.47471,-0.01439,0.02007],"force_p95":0.84287,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.94334,"mean_force":0.55925,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50156,0.01718,0.03358]},{"body_a":"peg","body_b":"channel_base_body","contact_count":454.0,"contact_point_centroid":[0.50605,0.08088,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55079,"mean_force":0.54677,"phase_index":1.0,"phase_name":"align_descend","phase_type":"descend","tcp_position_centroid":[0.51501,0.12619,0.11809]}],"total_contact_groups":10},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50566,-0.07772,0.03815],"final_tcp_position":[0.50235,-0.04646,0.03013],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":82.72033,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":244.0,"n_steps_budget":900.0,"object_pos_end":[0.50598,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54467,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":251.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach_peg","tcp_end":[0.5272,0.1418,0.19576],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.17435,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":454.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.50598,0.0809,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":0.54819,"phase_name":"align_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":454.0,"raw_peak_contact_force":0.55079,"subtask_id":"approach_peg","tcp_end":[0.50412,0.11288,0.04337],"tcp_start":[0.5272,0.1418,0.19576],"tcp_to_object_dist_end":0.03347,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":388.0,"n_steps_budget":1000.0,"object_pos_end":[0.50566,-0.07772,0.03815],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.00637,"object_to_goal_dist_start":0.1611,"object_z_max":0.04195,"peak_contact_force":0.0,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":546.0,"raw_peak_contact_force":82.72033,"subtask_id":"push_to_goal","tcp_end":[0.50235,-0.04646,0.03013],"tcp_start":[0.50412,0.11288,0.04337],"tcp_to_object_dist_end":0.03244,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e082b57d1be6744ae6d3993c25b90215f3fc56dc7131af62e0630c4f325e4b04`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9902,"average_solve_count":102.0,"average_success_count":102.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_height":0.12032,"push_along_channel.push_distance":0.19278},"optimized_scores":{"best_composite_score":0.47211,"best_fitness_score":0.60211,"best_task_score":0.50916},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":26.0,"contact_point_centroid":[0.555,-0.02504,0.06],"force_p95":84.75529,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":89.73759,"mean_force":71.47359,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50263,-0.02585,0.03123]},{"body_a":"peg","body_b":"channel_base_body","contact_count":226.0,"contact_point_centroid":[0.50084,0.00583,0.00928],"force_p95":19.73952,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.26149,"mean_force":3.66433,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50145,0.04483,0.03466]},{"body_a":"attachment","body_b":"peg","contact_count":188.0,"contact_point_centroid":[0.50432,0.03012,0.04368],"force_p95":20.81026,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.14758,"mean_force":4.59122,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50143,0.04158,0.03443]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":108.0,"contact_point_centroid":[0.5252,0.0099,0.04045],"force_p95":14.07307,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.29006,"mean_force":2.529,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50147,0.04141,0.03438]},{"body_a":"peg","body_b":"channel_base_body","contact_count":224.0,"contact_point_centroid":[0.50536,0.10453,0.00935],"force_p95":0.65943,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.59685,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50908,0.17909,0.23352]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50045,0.19822,0.29467]},{"body_a":"peg","body_b":"channel_base_body","contact_count":399.0,"contact_point_centroid":[0.50586,0.1048,0.00939],"force_p95":0.57546,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57958,"mean_force":0.54631,"phase_index":1.0,"phase_name":"align_descend","phase_type":"descend","tcp_position_centroid":[0.50968,0.1482,0.10867]}],"total_contact_groups":7},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5059,-0.06791,0.04049],"final_tcp_position":[0.50343,-0.03868,0.0311],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":89.73759,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":251.0,"n_steps_budget":930.0,"object_pos_end":[0.50584,0.1046,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18479,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54737,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":256.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach_peg","tcp_end":[0.518,0.16127,0.17791],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1553,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":399.0,"n_steps_budget":930.0,"object_pos_end":[0.50598,0.1046,0.03384],"object_pos_start":[0.50584,0.1046,0.03383],"object_to_goal_dist_end":0.1848,"object_to_goal_dist_start":0.18479,"object_z_max":0.03384,"peak_contact_force":0.53561,"phase_name":"align_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":399.0,"raw_peak_contact_force":0.57958,"subtask_id":"approach_peg","tcp_end":[0.50329,0.13629,0.04314],"tcp_start":[0.518,0.16127,0.17791],"tcp_to_object_dist_end":0.03314,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":430.0,"n_steps_budget":1000.0,"object_pos_end":[0.5059,-0.06791,0.04049],"object_pos_start":[0.50598,0.1046,0.03384],"object_to_goal_dist_end":0.01347,"object_to_goal_dist_start":0.1848,"object_z_max":0.04274,"peak_contact_force":1.29931,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":548.0,"raw_peak_contact_force":89.73759,"subtask_id":"push_to_goal","tcp_end":[0.50343,-0.03868,0.0311],"tcp_start":[0.50329,0.13629,0.04314],"tcp_to_object_dist_end":0.03079,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```