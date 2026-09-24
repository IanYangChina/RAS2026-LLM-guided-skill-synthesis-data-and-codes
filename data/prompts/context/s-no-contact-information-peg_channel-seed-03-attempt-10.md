## Search State

- **Seed**: 3
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | impedance_control | pose_tolerance | contact_detected | pose_tolerance | 6 | -0.1294 | 0.10 | ❌ rejected |
| 9 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | impedance_control | pose_tolerance | contact_detected | pose_tolerance | 4 | 0.2959 | 0.33 | ❌ rejected |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 7 | 0.4871 | 0.21 | ❌ rejected |
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | impedance_control | pose_tolerance | contact_detected | pose_tolerance | 5 | 0.0691 | 0.24 | ❌ rejected |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.1085 | 0.18 | ❌ rejected |

**Proposal policy**: task_score is 0.10 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.129) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_above
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.1
  weight: 0.3
- id: reach_goal
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_1
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
    - 0.1
    tolerance: 0.02
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_above
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.02
    - 0.0
    tolerance: 0.01
  parameters:
    contact_offset:
      type: scalar
      range:
      - 0.01
      - 0.03
      default: 0.02
      binds_to:
      - path: target.offset.y
        mode: replace
  guards:
  - id: contact_check
    when: after_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.01
    - 0.0
  subtask_id: reach_above
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.03
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
    push_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.1], tolerance=0.02
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], tolerance=0.01
  - parameter_bindings:
    - contact_offset: status=consumed; consumers=target.offset.y (replace)
  - guards:
    - id=contact_check, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.01, 0.0]
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=replace_offset_projection, sign=positive}, tolerance=0.03
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: -0.129
- **task_score** (E): 0.100
- **fitness_score**: 0.201  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1886 |
| descend_1 | 1.00 | 0.1070 |
| push_1 | 1.00 | 0.1043 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.507, 0.079, 0.159) | (0.509, 0.081, 0.040)→(0.502, 0.082, 0.034) | 0.165→0.162 |
| descend_1 | descend | 1.00 / step_budget | (0.507, 0.079, 0.159)→(0.503, 0.082, 0.055) | (0.502, 0.082, 0.034)→(0.503, 0.082, 0.030) | 0.162→0.163 |
| push_1 | push | 1.00 / step_budget | (0.503, 0.082, 0.055)→(0.501, -0.023, 0.051) | (0.503, 0.082, 0.030)→(0.498, 0.032, 0.025) | 0.163→0.113 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.319
- alignment_error: None
- terminal_score: 0.109
- phase_score: 0.301
- phase_breakdown.reach_above_score: 0.167
- phase_breakdown.reach_goal_score: 0.359

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.224
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.123
- **Median Q (composite search score)**: -0.137
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at lower bound**: approach_1.arc_height
- **Final σ (mean)**: 0.380


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.63873,"average_solve_count":346.0,"average_success_count":346.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.01935,"approach_1.arc_height":0.05,"descend_1.descend_speed":0.01652,"push_1.push_distance":0.1669,"push_1.push_speed":0.00612,"push_1.push_tolerance":0.02354},"optimized_scores":{"best_composite_score":-0.10569,"best_fitness_score":0.22431,"best_task_score":0.10896},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":252.0,"contact_point_centroid":[0.49873,0.02618,0.00821],"force_p95":144.92744,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":147.99435,"mean_force":55.56403,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49161,-0.00257,0.05372]},{"body_a":"attachment","body_b":"peg","contact_count":139.0,"contact_point_centroid":[0.50213,0.03678,0.05415],"force_p95":145.47637,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":147.53408,"mean_force":99.59879,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49361,0.03181,0.05621]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49506,0.05895,0.00917],"force_p95":91.65245,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":141.61245,"mean_force":12.28679,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47462,0.05879,0.10022]},{"body_a":"attachment","body_b":"peg","contact_count":155.0,"contact_point_centroid":[0.49716,0.05912,0.05468],"force_p95":123.08585,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":141.04949,"mean_force":75.75105,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48639,0.05893,0.05875]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47499,-0.01667,0.0239],"force_p95":10.05828,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.22371,"mean_force":2.78814,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48839,-0.05644,0.04983]},{"body_a":"peg","body_b":"channel_base_body","contact_count":447.0,"contact_point_centroid":[0.49442,0.05887,0.00935],"force_p95":0.59176,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.57894,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47721,0.11014,0.24666]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49819,0.19538,0.29873]}],"total_contact_groups":7},"final_pose_error":0.02945,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49336,0.00785,0.02463],"final_tcp_position":[0.48793,-0.07879,0.04932],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"phases":[{"n_steps":476.0,"n_steps_budget":1000.0,"object_pos_end":[0.49424,0.05896,0.03386],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13922,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_above","tcp_end":[0.46459,0.05931,0.15984],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12941,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4984,0.05889,0.02774],"object_pos_start":[0.49424,0.05896,0.03386],"object_to_goal_dist_end":0.13944,"object_to_goal_dist_start":0.13922,"object_z_max":0.03398,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_above","tcp_end":[0.49088,0.05917,0.05388],"tcp_start":[0.46459,0.05931,0.15984],"tcp_to_object_dist_end":0.0272,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":260.0,"n_steps_budget":1000.0,"object_pos_end":[0.49336,0.00785,0.02463],"object_pos_start":[0.4984,0.05889,0.02774],"object_to_goal_dist_end":0.08943,"object_to_goal_dist_start":0.13944,"object_z_max":0.03927,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"reach_goal","tcp_end":[0.48793,-0.07879,0.04932],"tcp_start":[0.49088,0.05917,0.05388],"tcp_to_object_dist_end":0.09025,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.37423,"average_solve_count":326.0,"average_success_count":326.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.04644,"approach_1.arc_height":0.05085,"descend_1.descend_speed":0.01138,"push_1.push_distance":0.11771,"push_1.push_speed":0.01104,"push_1.push_tolerance":0.03538},"optimized_scores":{"best_composite_score":-0.14525,"best_fitness_score":0.18475,"best_task_score":0.06809},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":459.0,"contact_point_centroid":[0.52505,0.08064,0.05998],"force_p95":268.25422,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":298.36637,"mean_force":207.61894,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51067,0.08065,0.05698]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":93.0,"contact_point_centroid":[0.52501,0.06502,0.06],"force_p95":150.1443,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":158.23539,"mean_force":106.23093,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51056,0.06502,0.05725]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.51375,0.08078,0.00884],"force_p95":137.55138,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":143.31857,"mean_force":56.59301,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51535,0.07973,0.08283]},{"body_a":"attachment","body_b":"peg","contact_count":520.0,"contact_point_centroid":[0.52162,0.08049,0.05463],"force_p95":138.96376,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":142.8249,"mean_force":107.84746,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51063,0.08056,0.0574]},{"body_a":"attachment","body_b":"peg","contact_count":172.0,"contact_point_centroid":[0.51869,0.06374,0.05514],"force_p95":121.34833,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":126.8058,"mean_force":85.98544,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51043,0.0582,0.05706]},{"body_a":"peg","body_b":"channel_base_body","contact_count":212.0,"contact_point_centroid":[0.50878,0.06078,0.00879],"force_p95":120.85553,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":126.10379,"mean_force":69.92541,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50995,0.0485,0.05624]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":56.0,"contact_point_centroid":[0.52503,0.06585,0.05768],"force_p95":48.32438,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.83761,"mean_force":12.7348,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51085,0.05697,0.05794]},{"body_a":"peg","body_b":"channel_base_body","contact_count":425.0,"contact_point_centroid":[0.50559,0.08086,0.00935],"force_p95":0.56059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.58266,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52184,0.11969,0.24608]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50063,0.19518,0.29863]}],"total_contact_groups":9},"final_pose_error":0.02986,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50045,0.03208,0.02462],"final_tcp_position":[0.50725,-0.00728,0.05166],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"phases":[{"n_steps":454.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_above","tcp_end":[0.53335,0.07849,0.15925],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12845,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50496,0.08169,0.03076],"object_pos_start":[0.50598,0.0809,0.03378],"object_to_goal_dist_end":0.16203,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_above","tcp_end":[0.50984,0.08092,0.05546],"tcp_start":[0.53335,0.07849,0.15925],"tcp_to_object_dist_end":0.02518,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":220.0,"n_steps_budget":1000.0,"object_pos_end":[0.50045,0.03208,0.02462],"object_pos_start":[0.50496,0.08169,0.03076],"object_to_goal_dist_end":0.11313,"object_to_goal_dist_start":0.16203,"object_z_max":0.0398,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"reach_goal","tcp_end":[0.50725,-0.00728,0.05166],"tcp_start":[0.50984,0.08092,0.05546],"tcp_to_object_dist_end":0.04824,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.39776,"average_solve_count":357.0,"average_success_count":357.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.02225,"approach_1.arc_height":0.17699,"descend_1.descend_speed":0.01029,"push_1.push_distance":0.11567,"push_1.push_speed":0.01626,"push_1.push_tolerance":0.01107},"optimized_scores":{"best_composite_score":-0.13723,"best_fitness_score":0.19277,"best_task_score":0.12254},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":382.0,"contact_point_centroid":[0.52505,0.10438,0.05998],"force_p95":264.14092,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":297.38249,"mean_force":194.67501,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51011,0.10438,0.05544]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":88.0,"contact_point_centroid":[0.52501,0.08817,0.06],"force_p95":149.46728,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":163.96703,"mean_force":103.39634,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51038,0.08815,0.05664]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.51302,0.10446,0.00871],"force_p95":146.10319,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":154.71296,"mean_force":59.66415,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51175,0.10219,0.08332]},{"body_a":"attachment","body_b":"peg","contact_count":496.0,"contact_point_centroid":[0.52079,0.104,0.0538],"force_p95":150.3203,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":154.21389,"mean_force":119.24013,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50975,0.1041,0.05625]},{"body_a":"peg","body_b":"channel_base_body","contact_count":208.0,"contact_point_centroid":[0.5095,0.08519,0.00874],"force_p95":126.26319,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":136.05767,"mean_force":75.74301,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50986,0.07333,0.05576]},{"body_a":"attachment","body_b":"peg","contact_count":174.0,"contact_point_centroid":[0.51868,0.08686,0.05469],"force_p95":126.83078,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":135.52953,"mean_force":90.40443,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51027,0.08155,0.05648]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":60.0,"contact_point_centroid":[0.52504,0.09182,0.05766],"force_p95":45.63509,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.37635,"mean_force":17.20956,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51075,0.08303,0.0575]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":48.0,"contact_point_centroid":[0.52504,0.10533,0.05134],"force_p95":12.04514,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.83313,"mean_force":3.6159,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51,0.10378,0.05676]},{"body_a":"peg","body_b":"channel_base_body","contact_count":395.0,"contact_point_centroid":[0.50551,0.10455,0.00937],"force_p95":0.58074,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57498,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51614,0.12902,0.24321]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50018,0.19638,0.29866]}],"total_contact_groups":10},"final_pose_error":0.0295,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50108,0.05563,0.02511],"final_tcp_position":[0.50708,0.01818,0.05095],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"phases":[{"n_steps":422.0,"n_steps_budget":1000.0,"object_pos_end":[0.50583,0.10467,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18487,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_above","tcp_end":[0.52309,0.0989,0.15887],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12636,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5055,0.10574,0.03023],"object_pos_start":[0.50583,0.10467,0.03384],"object_to_goal_dist_end":0.18608,"object_to_goal_dist_start":0.18487,"object_z_max":0.03384,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_above","tcp_end":[0.50955,0.10467,0.05449],"tcp_start":[0.52309,0.0989,0.15887],"tcp_to_object_dist_end":0.02462,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":217.0,"n_steps_budget":1000.0,"object_pos_end":[0.50108,0.05563,0.02511],"object_pos_start":[0.5055,0.10574,0.03023],"object_to_goal_dist_end":0.13645,"object_to_goal_dist_start":0.18608,"object_z_max":0.03978,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"reach_goal","tcp_end":[0.50708,0.01818,0.05095],"tcp_start":[0.50955,0.10467,0.05449],"tcp_to_object_dist_end":0.04589,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```