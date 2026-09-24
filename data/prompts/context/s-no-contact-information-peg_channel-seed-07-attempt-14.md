## Search State

- **Seed**: 7
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.2910 | 0.00 | ❌ rejected |
| 13 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.3505 | 0.66 | ❌ rejected |
| 12 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.3630 | 0.73 | ✅ accepted |
| 11 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.1581 | 0.13 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.0846 | 0.00 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`
- Frozen object start: [0.5100076373283734, 0.11177710407756605, 0.04]
- Frozen task target: [0.5100076373283734, -0.04822289592243395, 0.04]
- Goal object position: (0.5100076373283734, -0.04822289592243395, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5100076373283734, 0.11177710407756605, 0.04)
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
  frozen_object_start: [0.51, 0.1118, 0.04]
  frozen_task_target: [0.51, -0.0482, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5100076373283734, 0.11177710407756605, 0.04]}
  frozen_targets: {'channel_exit': [0.5100076373283734, -0.04822289592243395, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415

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
| `object` | offset from object initial position (0.5100076373283734, 0.11177710407756605, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5100076373283734, -0.04822289592243395, 0.04) | final destination targets |
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

## Current Skill (Q=-0.291) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_approach
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.1
  weight: 0.3
- id: reach_contact
  anchor: object
  offset:
  - 0.0
  - 0.04
  - 0.0
  weight: 0.3
- id: push_complete
  metric: goal_progress
  weight: 0.4
phases:
- id: approach_peg
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.05
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_approach
- id: contact_peg
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.04
    - 0.0
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 3.0
      - 15.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - -0.003
    - 0.0
    - 0.0
  subtask_id: reach_contact
- id: push_channel
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    retry_lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.003
      binds_to:
      - path: retry.offset.x
        mode: replace
  guards:
  - id: push_force_limit
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.003
    - 0.0
    - 0.0
  subtask_id: push_complete
- id: retract_away
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **contact_peg** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.04, 0.0], tolerance=0.01
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[-0.003, 0.0, 0.0]
- **push_channel** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - retry_lateral_offset_x: status=consumed; consumers=retry.offset.x (replace)
  - guards:
    - id=push_force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.003, 0.0, 0.0]
- **retract_away** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: -0.291
- **task_score** (E): 0.000
- **fitness_score**: 0.219  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_peg | 1.00 | 0.1620 |
| contact_peg | 0.00 | 0.1151 |
| push_channel | 0.67 | 0.0728 |
| retract_away | 1.00 | 0.1090 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.151, 0.148) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 |
| contact_peg | contact | 0.00 / step_budget | (0.505, 0.151, 0.148)→(0.499, 0.066, 0.071) | (0.502, 0.098, 0.034)→(0.512, 0.112, 0.027) | 0.178→0.193 |
| push_channel | push | 0.67 / step_budget | (0.506, 0.053, 0.057)→(0.504, -0.016, 0.034) | (0.512, 0.112, 0.027)→(0.516, 0.112, 0.027) | 0.193→0.193 |
| retract_away | retract | 1.00 / step_budget | (0.504, -0.016, 0.034)→(0.498, -0.068, 0.123) | (0.516, 0.112, 0.027)→(0.551, 0.112, 0.027) | 0.193→0.205 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- terminal_score: 0.000
- phase_score: 0.368
- phase_breakdown.push_complete_score: 0.000
- phase_breakdown.reach_approach_score: 0.820

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.221
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.001
- **Median Q (composite search score)**: -0.290
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.423


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `474e87cb3f7f98c9c8d99c8760356b7c026b70b97898f68d5a6c39ba94bca956`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a79e5fd8fc80d9ecadd30a274b12d8d7e7d0841df5ca68ae512c46dc86b114e6`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.79279,"average_solve_count":333.0,"average_success_count":333.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.02897,"contact_peg.contact_force_threshold":2.75759,"contact_peg.contact_push_distance":0.08002,"contact_peg.contact_speed":0.02389,"push_channel.push_distance":0.15757,"push_channel.push_retry_lateral_x":-0.00489,"push_channel.push_retry_lateral_z":0.00022,"push_channel.push_speed":0.04451,"retract_away.retract_speed":0.03099},"optimized_scores":{"best_composite_score":-0.29039,"best_fitness_score":0.21961,"best_task_score":0.00062},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":509.0,"contact_point_centroid":[0.50359,0.11165,0.00937],"force_p95":0.61193,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55971,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50229,0.1814,0.22151]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50363,0.1116,0.00941],"force_p95":0.60486,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65746,"mean_force":0.54357,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49665,-0.05174,0.08069]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50367,0.11168,0.0094],"force_p95":0.59409,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65067,"mean_force":0.54426,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50212,0.11827,0.10487]},{"body_a":"peg","body_b":"channel_base_body","contact_count":268.0,"contact_point_centroid":[0.50378,0.11158,0.0094],"force_p95":0.60022,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64695,"mean_force":0.54408,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49939,0.02647,0.0507]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49972,0.19946,0.29926]}],"total_contact_groups":5},"final_pose_error":0.01339,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50376,0.11167,0.03382],"final_tcp_position":[0.49684,-0.07558,0.12776],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"phases":[{"n_steps":531.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.11175,0.03386],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_approach","tcp_end":[0.50619,0.16413,0.14874],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12628,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.11173,0.0338],"object_pos_start":[0.50372,0.11175,0.03386],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19188,"object_z_max":0.03403,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"reach_contact","tcp_end":[0.50099,0.07672,0.0687],"tcp_start":[0.50619,0.16413,0.14874],"tcp_to_object_dist_end":0.04951,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":268.0,"n_steps_budget":1000.0,"object_pos_end":[0.50379,0.11171,0.03383],"object_pos_start":[0.50377,0.11173,0.0338],"object_to_goal_dist_end":0.19185,"object_to_goal_dist_start":0.19187,"object_z_max":0.03393,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_complete","tcp_end":[0.49991,-0.02658,0.0347],"tcp_start":[0.50099,0.07672,0.0687],"tcp_to_object_dist_end":0.13835,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50376,0.11167,0.03382],"object_pos_start":[0.50379,0.11171,0.03383],"object_to_goal_dist_end":0.19181,"object_to_goal_dist_start":0.19185,"object_z_max":0.03406,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.49684,-0.07558,0.12776],"tcp_start":[0.49991,-0.02658,0.0347],"tcp_to_object_dist_end":0.20961,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3ca2e925d364d2c0fe81fb71ee31d40f947a20e349a0720e1c44a2dd2bc628da`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95708,"average_solve_count":233.0,"average_success_count":233.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.06811,"contact_peg.contact_force_threshold":7.58705,"contact_peg.contact_push_distance":0.08006,"contact_peg.contact_speed":0.01167,"push_channel.push_distance":0.1328,"push_channel.push_retry_lateral_x":0.00576,"push_channel.push_retry_lateral_z":0.00489,"push_channel.push_speed":0.03169,"retract_away.retract_speed":0.05641},"optimized_scores":{"best_composite_score":-0.28943,"best_fitness_score":0.22057,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52504,0.05112,0.05999],"force_p95":190.01495,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":223.547,"mean_force":55.88675,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50854,0.05114,0.03273]},{"body_a":"peg","body_b":"world","contact_count":862.0,"contact_point_centroid":[0.50584,0.15902,-0.0019],"force_p95":0.72587,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.92467,"mean_force":0.61099,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48533,0.12458,0.10505]},{"body_a":"peg","body_b":"channel_base_body","contact_count":457.0,"contact_point_centroid":[0.49621,0.11924,0.00939],"force_p95":0.61908,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55968,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49135,0.18463,0.22123]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.4995,0.19924,0.29775]},{"body_a":"peg","body_b":"world","contact_count":1000.0,"contact_point_centroid":[0.58802,0.16025,-0.00199],"force_p95":0.7259,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72624,"mean_force":0.60602,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50164,-0.00018,0.06988]},{"body_a":"peg","body_b":"world","contact_count":157.0,"contact_point_centroid":[0.53213,0.15966,-0.00199],"force_p95":0.72584,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72585,"mean_force":0.60534,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49724,0.07215,0.05421]},{"body_a":"peg","body_b":"channel_base_body","contact_count":135.0,"contact_point_centroid":[0.49693,0.11991,0.00945],"force_p95":0.59564,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60078,"mean_force":0.50292,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48224,0.16699,0.14209]}],"total_contact_groups":7},"final_pose_error":0.04406,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.64232,0.16038,0.01409],"final_tcp_position":[0.49869,-0.04819,0.10954],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"phases":[{"n_steps":482.0,"n_steps_budget":1000.0,"object_pos_end":[0.49606,0.11961,0.03387],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19975,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_approach","tcp_end":[0.48459,0.17079,0.14964],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1271,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52632,0.16014,0.01409],"object_pos_start":[0.49606,0.11961,0.03387],"object_to_goal_dist_end":0.24296,"object_to_goal_dist_start":0.19975,"object_z_max":0.0339,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"reach_contact","tcp_end":[0.48804,0.0911,0.07541],"tcp_start":[0.48459,0.17079,0.14964],"tcp_to_object_dist_end":0.09996,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":157.0,"n_steps_budget":1000.0,"object_pos_end":[0.53813,0.16009,0.01409],"object_pos_start":[0.52632,0.16014,0.01409],"object_to_goal_dist_end":0.24447,"object_to_goal_dist_start":0.24296,"object_z_max":0.01409,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_complete","tcp_end":[0.50828,0.05071,0.03224],"tcp_start":[0.5084,0.05084,0.0324],"tcp_to_object_dist_end":0.11483,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.64232,0.16038,0.01409],"object_pos_start":[0.53838,0.16019,0.01408],"object_to_goal_dist_end":0.28055,"object_to_goal_dist_start":0.24461,"object_z_max":0.0141,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.49869,-0.04819,0.10954],"tcp_start":[0.50828,0.05071,0.03224],"tcp_to_object_dist_end":0.27063,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f85f1938a541e3d507519c8f918b8ca98f1f9baf6ab2f6f3ba2c32478e079e47`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.1441,"average_solve_count":229.0,"average_success_count":229.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.06585,"contact_peg.contact_force_threshold":6.50171,"contact_peg.contact_push_distance":0.08034,"contact_peg.contact_speed":0.02096,"push_channel.push_distance":0.15539,"push_channel.push_retry_lateral_x":-0.00134,"push_channel.push_retry_lateral_z":0.00498,"push_channel.push_speed":0.04271,"retract_away.retract_speed":0.07977},"optimized_scores":{"best_composite_score":-0.29325,"best_fitness_score":0.21675,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":572.0,"contact_point_centroid":[0.50578,0.06294,0.00936],"force_p95":0.56465,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.57021,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51168,0.15763,0.21883]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49994,0.1982,0.29659]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50595,0.06304,0.00938],"force_p95":0.55213,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54656,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51485,0.07229,0.10355]},{"body_a":"peg","body_b":"channel_base_body","contact_count":744.0,"contact_point_centroid":[0.50597,0.06307,0.00939],"force_p95":0.55079,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55442,"mean_force":0.54631,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49825,-0.07592,0.08183]},{"body_a":"peg","body_b":"channel_base_body","contact_count":272.0,"contact_point_centroid":[0.50599,0.06274,0.00939],"force_p95":0.55157,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55425,"mean_force":0.54637,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50492,-0.01955,0.05081]}],"total_contact_groups":5},"final_pose_error":0.01028,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50608,0.06304,0.03386],"final_tcp_position":[0.49701,-0.07912,0.1302],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"phases":[{"n_steps":600.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06298,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14324,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_approach","tcp_end":[0.52439,0.11848,0.14619],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12669,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50605,0.06301,0.03383],"object_pos_start":[0.50593,0.06298,0.03381],"object_to_goal_dist_end":0.14327,"object_to_goal_dist_start":0.14324,"object_z_max":0.03383,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"reach_contact","tcp_end":[0.50885,0.03079,0.06909],"tcp_start":[0.52439,0.11848,0.14619],"tcp_to_object_dist_end":0.04784,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":272.0,"n_steps_budget":1000.0,"object_pos_end":[0.50591,0.06304,0.03384],"object_pos_start":[0.50605,0.06301,0.03383],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14327,"object_z_max":0.03384,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_complete","tcp_end":[0.50301,-0.0729,0.03457],"tcp_start":[0.50885,0.03079,0.06909],"tcp_to_object_dist_end":0.13597,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":744.0,"n_steps_budget":840.0,"object_pos_end":[0.50608,0.06304,0.03386],"object_pos_start":[0.50591,0.06304,0.03384],"object_to_goal_dist_end":0.1433,"object_to_goal_dist_start":0.14329,"object_z_max":0.03386,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.49701,-0.07912,0.1302],"tcp_start":[0.50301,-0.0729,0.03457],"tcp_to_object_dist_end":0.17197,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```