## Search State

- **Seed**: 3
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | impedance_control | pose_tolerance | contact_detected | pose_tolerance | 4 | 0.3196 | 0.35 | ✅ accepted |
| 11 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | -0.1406 | 0.00 | ❌ rejected |
| 10 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | impedance_control | pose_tolerance | contact_detected | pose_tolerance | 6 | -0.1294 | 0.10 | ❌ rejected |
| 9 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | impedance_control | pose_tolerance | contact_detected | pose_tolerance | 4 | 0.2959 | 0.33 | ❌ rejected |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 7 | 0.4871 | 0.21 | ❌ rejected |

**Proposal policy**: task_score is 0.35 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.320) — your mutation base

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

- **Composite score**: 0.320
- **task_score** (E): 0.347
- **fitness_score**: 0.550  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1503 |
| descend_1 | 1.00 | 0.1310 |
| push_1 | 1.00 | 0.1548 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.141, 0.165) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 |
| descend_1 | descend | 1.00 / step_budget | (0.505, 0.141, 0.165)→(0.500, 0.105, 0.041) | (0.502, 0.081, 0.034)→(0.502, 0.061, 0.031) | 0.162→0.142 |
| push_1 | push | 1.00 / step_budget | (0.500, 0.105, 0.041)→(0.499, -0.050, 0.037) | (0.502, 0.061, 0.031)→(0.504, -0.080, 0.034) | 0.142→0.010 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- terminal_score: 0.494
- phase_score: 0.661
- phase_breakdown.reach_above_score: 0.124
- phase_breakdown.reach_goal_score: 0.890

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.594
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.494
- **Median Q (composite search score)**: 0.319
- **K-run variance**: 0.0013
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.391


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91346,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11117,"descend_1.contact_offset":0.01517,"push_1.push_distance":0.17685,"push_1.push_tolerance":0.0334},"optimized_scores":{"best_composite_score":0.27613,"best_fitness_score":0.50613,"best_task_score":0.23427},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.53441,0.07665,0.05974],"force_p95":281.18372,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":286.85965,"mean_force":199.03814,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48911,0.07673,0.037]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":323.0,"contact_point_centroid":[0.53714,-0.01215,0.05997],"force_p95":195.52122,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":221.51447,"mean_force":168.78149,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49214,-0.01238,0.03726]},{"body_a":"attachment","body_b":"peg","contact_count":278.0,"contact_point_centroid":[0.49849,-0.03201,0.04089],"force_p95":105.89605,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":120.94078,"mean_force":43.38142,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49246,-0.02165,0.0372]},{"body_a":"peg","body_b":"channel_base_body","contact_count":186.0,"contact_point_centroid":[0.49888,-0.10094,0.05563],"force_p95":79.24003,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":107.95656,"mean_force":46.36834,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49325,-0.04979,0.03704]},{"body_a":"peg","body_b":"channel_base_body","contact_count":277.0,"contact_point_centroid":[0.50114,-0.04543,0.00968],"force_p95":51.1881,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.82935,"mean_force":12.9191,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4919,-0.00882,0.03731]},{"body_a":"peg","body_b":"channel_base_body","contact_count":815.0,"contact_point_centroid":[0.49502,0.05515,0.00946],"force_p95":9.50105,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":52.43802,"mean_force":2.05792,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47763,0.09813,0.09972]},{"body_a":"attachment","body_b":"peg","contact_count":94.0,"contact_point_centroid":[0.49267,0.06899,0.05001],"force_p95":44.61798,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.03951,"mean_force":13.33485,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48715,0.08,0.04685]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":176.0,"contact_point_centroid":[0.5253,-0.04057,0.02556],"force_p95":28.18409,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.64897,"mean_force":12.98833,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49209,-0.01695,0.03733]},{"body_a":"peg","body_b":"channel_base_body","contact_count":272.0,"contact_point_centroid":[0.49457,0.05884,0.00932],"force_p95":0.65511,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.59994,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48302,0.15765,0.22776]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49835,0.19668,0.29433]},{"body_a":"peg","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.51202,-0.0613,0.07298],"force_p95":0.54218,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.5746,"mean_force":0.27137,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.492,-0.02772,0.03738]}],"total_contact_groups":11},"final_pose_error":0.04139,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49914,-0.08774,0.03712],"final_tcp_position":[0.495,-0.05913,0.03673],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"phases":[{"n_steps":301.0,"n_steps_budget":1000.0,"object_pos_end":[0.49421,0.05893,0.03384],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13919,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_above","tcp_end":[0.46903,0.12081,0.1671],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14907,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":826.0,"n_steps_budget":900.0,"object_pos_end":[0.49794,0.0475,0.03558],"object_pos_start":[0.49421,0.05893,0.03384],"object_to_goal_dist_end":0.12759,"object_to_goal_dist_start":0.13919,"object_z_max":0.03778,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_above","tcp_end":[0.48951,0.0767,0.03683],"tcp_start":[0.46903,0.12081,0.1671],"tcp_to_object_dist_end":0.03042,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":469.0,"n_steps_budget":1000.0,"object_pos_end":[0.49914,-0.08774,0.03712],"object_pos_start":[0.49794,0.0475,0.03558],"object_to_goal_dist_end":0.00831,"object_to_goal_dist_start":0.12759,"object_z_max":0.04334,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"reach_goal","tcp_end":[0.495,-0.05913,0.03673],"tcp_start":[0.48951,0.0767,0.03683],"tcp_to_object_dist_end":0.02892,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91429,"average_solve_count":105.0,"average_success_count":105.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07968,"descend_1.contact_offset":0.02953,"push_1.push_distance":0.19631,"push_1.push_tolerance":0.04738},"optimized_scores":{"best_composite_score":0.31902,"best_fitness_score":0.54902,"best_task_score":0.31318},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":51.0,"contact_point_centroid":[0.52513,0.11391,0.05994],"force_p95":361.47702,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":390.16686,"mean_force":291.4981,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50518,0.11385,0.04395]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":81.0,"contact_point_centroid":[0.52501,-0.01701,0.06],"force_p95":134.05877,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":144.45121,"mean_force":102.50424,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50175,-0.01693,0.03939]},{"body_a":"attachment","body_b":"peg","contact_count":227.0,"contact_point_centroid":[0.505,-0.01313,0.04022],"force_p95":135.21696,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":141.97316,"mean_force":53.73901,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50171,-0.00251,0.03937]},{"body_a":"peg","body_b":"channel_base_body","contact_count":73.0,"contact_point_centroid":[0.50641,-0.10126,0.05366],"force_p95":98.57304,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":101.03717,"mean_force":76.89384,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50145,-0.04626,0.03882]},{"body_a":"peg","body_b":"channel_base_body","contact_count":261.0,"contact_point_centroid":[0.50518,-0.03484,0.00957],"force_p95":64.32142,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":76.13501,"mean_force":32.20825,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50174,0.00194,0.03941]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":81.0,"contact_point_centroid":[0.52514,-0.00099,0.03011],"force_p95":26.07891,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.87493,"mean_force":6.49505,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50191,0.02548,0.03961]},{"body_a":"peg","body_b":"channel_base_body","contact_count":315.0,"contact_point_centroid":[0.50555,0.08086,0.00934],"force_p95":0.57738,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.59521,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5143,0.16739,0.21224]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50063,0.19767,0.29382]},{"body_a":"peg","body_b":"channel_base_body","contact_count":446.0,"contact_point_centroid":[0.50591,0.08087,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55023,"mean_force":0.54677,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5147,0.12491,0.08467]}],"total_contact_groups":9},"final_pose_error":0.02986,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50723,-0.07975,0.03828],"final_tcp_position":[0.50087,-0.05347,0.03771],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"phases":[{"n_steps":344.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_above","tcp_end":[0.52827,0.13866,0.13645],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11992,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":446.0,"n_steps_budget":690.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_above","tcp_end":[0.50468,0.11382,0.04362],"tcp_start":[0.52827,0.13866,0.13645],"tcp_to_object_dist_end":0.03439,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":351.0,"n_steps_budget":1000.0,"object_pos_end":[0.50723,-0.07975,0.03828],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.00743,"object_to_goal_dist_start":0.16113,"object_z_max":0.04039,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"reach_goal","tcp_end":[0.50087,-0.05347,0.03771],"tcp_start":[0.50468,0.11382,0.04362],"tcp_to_object_dist_end":0.02704,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91176,"average_solve_count":102.0,"average_success_count":102.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13482,"descend_1.contact_offset":0.01363,"push_1.push_distance":0.18961,"push_1.push_tolerance":0.02848},"optimized_scores":{"best_composite_score":0.36373,"best_fitness_score":0.59373,"best_task_score":0.49355},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":39.0,"contact_point_centroid":[0.52504,0.11999,0.05998],"force_p95":353.95846,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":375.72992,"mean_force":254.62568,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50549,0.12278,0.04388]},{"body_a":"peg","body_b":"channel_base_body","contact_count":727.0,"contact_point_centroid":[0.50673,0.10315,0.00924],"force_p95":100.59082,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":152.35975,"mean_force":12.50791,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50934,0.14051,0.11197]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":78.0,"contact_point_centroid":[0.525,0.03537,0.06],"force_p95":120.6788,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":151.62506,"mean_force":97.89526,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50129,0.03556,0.03778]},{"body_a":"attachment","body_b":"peg","contact_count":94.0,"contact_point_centroid":[0.51463,0.11819,0.05571],"force_p95":139.89802,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":151.57962,"mean_force":92.56912,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5067,0.12575,0.05757]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54543,-9e-05,0.06],"force_p95":148.76915,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":149.78577,"mean_force":139.61961,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50061,0.00417,0.03699]},{"body_a":"attachment","body_b":"peg","contact_count":109.0,"contact_point_centroid":[0.5026,0.01517,0.04163],"force_p95":13.30457,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.50582,"mean_force":3.42288,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50097,0.02676,0.03737]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":31.0,"contact_point_centroid":[0.52519,0.04341,0.02572],"force_p95":11.91894,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.05275,"mean_force":2.9928,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50278,0.09055,0.03994]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.4747,0.02586,0.0276],"force_p95":19.3331,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.88544,"mean_force":7.39796,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50174,0.08372,0.03825]},{"body_a":"peg","body_b":"channel_base_body","contact_count":214.0,"contact_point_centroid":[0.50302,0.00648,0.0091],"force_p95":7.50314,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.13875,"mean_force":2.04173,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50155,0.05109,0.03815]},{"body_a":"peg","body_b":"channel_base_body","contact_count":199.0,"contact_point_centroid":[0.50521,0.10448,0.00934],"force_p95":0.70038,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.6032,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50902,0.17938,0.24075]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.47497,0.03799,0.03208],"force_p95":2.53638,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.56593,"mean_force":2.27044,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50538,0.12274,0.04366]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50051,0.19809,0.2948]}],"total_contact_groups":12},"final_pose_error":0.02977,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50528,-0.07391,0.02744],"final_tcp_position":[0.50062,-0.0372,0.0368],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"phases":[{"n_steps":226.0,"n_steps_budget":870.0,"object_pos_end":[0.50583,0.10465,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_above","tcp_end":[0.51772,0.16206,0.19214],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16881,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":747.0,"n_steps_budget":1000.0,"object_pos_end":[0.50101,0.05516,0.02445],"object_pos_start":[0.50583,0.10465,0.03383],"object_to_goal_dist_end":0.13605,"object_to_goal_dist_start":0.18484,"object_z_max":0.0407,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_above","tcp_end":[0.50509,0.12351,0.04241],"tcp_start":[0.51772,0.16206,0.19214],"tcp_to_object_dist_end":0.07079,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":293.0,"n_steps_budget":1000.0,"object_pos_end":[0.50528,-0.07391,0.02744],"object_pos_start":[0.50101,0.05516,0.02445],"object_to_goal_dist_end":0.01492,"object_to_goal_dist_start":0.13605,"object_z_max":0.03205,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"reach_goal","tcp_end":[0.50062,-0.0372,0.0368],"tcp_start":[0.50509,0.12351,0.04241],"tcp_to_object_dist_end":0.03816,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```