## Search State

- **Seed**: 3
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → rotate → descend → push | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.2623 | 0.46 | ✅ accepted |
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.4187 | 0.00 | ❌ rejected |
| 10 | approach → rotate → descend → push | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | 7 | -0.1611 | 0.13 | ❌ rejected |
| 9 | approach → rotate → descend → push | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | -0.0292 | 0.25 | ❌ rejected |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.2411 | 0.26 | ❌ rejected |

**Proposal policy**: task_score is 0.46 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.262) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach_pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.1
  weight: 0.2
- id: push_insertion
  target_entity: object
  metric: goal_progress
  weight: 0.8
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.03
    - 0.03
    - 0.1
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    lateral_x_offset:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.x
        mode: replace
  subtask_id: approach_pre_contact
- id: rotate_1
  type: rotate
  generator: joint_interpolation
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.03
    - 0.03
    - 0.1
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
    lateral_x_offset:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.x
        mode: replace
  subtask_id: approach_pre_contact
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.03
    - 0.03
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_force_threshold:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    lateral_x_offset:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.x
        mode: replace
  subtask_id: approach_pre_contact
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.03
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lateral_x_offset:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.x
        mode: replace
    push_retry_x_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.01
      binds_to:
      - path: retry.offset.x
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_retry
    when: during_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push_insertion

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.03, 0.03, 0.1], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - lateral_x_offset: status=consumed; consumers=target.offset.x (replace)
- **rotate_1** (`rotate`)
  - target: source=yaml, anchor=task_object, offset=[0.03, 0.03, 0.1], tolerance=0.02
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - lateral_x_offset: status=consumed; consumers=target.offset.x (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.03, 0.03, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - lateral_x_offset: status=consumed; consumers=target.offset.x (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.03, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lateral_x_offset: status=consumed; consumers=target.offset.x (replace)
    - push_retry_x_offset: status=consumed; consumers=retry.offset.x (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_retry, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.262
- **task_score** (E): 0.457
- **fitness_score**: 0.639  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.083
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1656 |
| rotate_1 | 1.00 | 1.00 | 0.0174 |
| descend_1 | 0.33 | 1.00 | 0.1181 |
| push_1 | 1.00 | 1.00 | 0.1702 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.509, 0.122, 0.156) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.547 | 3.954 |
| rotate_1 | rotate | 1.00 / step_budget | (0.509, 0.122, 0.156)→(0.502, 0.137, 0.151) | (0.502, 0.081, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.162 | 1.00 / 1.000 | 0.540 | 0.560 |
| descend_1 | descend | 0.33 / step_budget | (0.502, 0.137, 0.151)→(0.497, 0.112, 0.036) | (0.502, 0.081, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.162 | 1.00 / 1.333 | 16.301 | 16.314 |
| push_1 | push | 1.00 / step_budget | (0.497, 0.112, 0.036)→(0.492, -0.058, 0.036) | (0.502, 0.081, 0.034)→(0.508, -0.075, 0.036) | 0.162→0.013 | 1.00 / 4.667 | 146.514 | 187.883 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.893
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.247
- phase_score: 0.787
- phase_breakdown.push_insertion_score: 0.956
- phase_breakdown.approach_pre_contact_score: 0.112

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.740
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.720
- **Median Q (composite search score)**: 0.280
- **K-run variance**: 0.0079
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.208


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56667,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_x_offset":0.02389,"descend_1.descend_force_threshold":17.36709,"descend_1.descend_speed":0.05761,"descend_1.lateral_x_offset":0.0077,"push_1.lateral_x_offset":0.00485,"push_1.push_retry_x_offset":-0.00243,"push_1.push_speed":0.10027,"rotate_1.lateral_x_offset":-0.01872},"optimized_scores":{"best_composite_score":0.36115,"best_fitness_score":0.57115,"best_task_score":0.24707},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":74.0,"contact_point_centroid":[0.55943,-0.1,0.06497],"force_p95":177.54527,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":237.44785,"mean_force":117.36362,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50166,-0.05198,0.03592]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":61.0,"contact_point_centroid":[0.52502,-0.05204,0.05999],"force_p95":163.45898,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":193.03267,"mean_force":99.73717,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50179,-0.05305,0.03605]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":180.0,"contact_point_centroid":[0.54218,0.04304,0.05999],"force_p95":117.99429,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":139.80207,"mean_force":95.90831,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49846,0.03936,0.03483]},{"body_a":"attachment","body_b":"peg","contact_count":230.0,"contact_point_centroid":[0.5006,-0.02007,0.03916],"force_p95":42.68441,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.35914,"mean_force":10.57697,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50007,-0.00858,0.0353]},{"body_a":"peg","body_b":"channel_base_body","contact_count":93.0,"contact_point_centroid":[0.49831,-0.10059,0.05104],"force_p95":51.6471,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":62.68011,"mean_force":19.20543,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5016,-0.05138,0.03586]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54049,0.09284,0.05995],"force_p95":47.81326,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":47.81326,"mean_force":47.81326,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4968,0.08946,0.03467]},{"body_a":"peg","body_b":"channel_base_body","contact_count":289.0,"contact_point_centroid":[0.4978,-0.01429,0.00946],"force_p95":18.90094,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.45965,"mean_force":3.29726,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49901,0.02234,0.03496]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":108.0,"contact_point_centroid":[0.4748,0.00218,0.0344],"force_p95":2.21854,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.52601,"mean_force":0.9313,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49864,0.03344,0.03487]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":56.0,"contact_point_centroid":[0.52527,-0.02804,0.02857],"force_p95":4.58367,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.35794,"mean_force":1.29617,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49964,0.00153,0.03498]},{"body_a":"peg","body_b":"channel_base_body","contact_count":312.0,"contact_point_centroid":[0.49445,0.05894,0.00933],"force_p95":0.62145,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.59307,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49375,0.14789,0.22154]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49917,0.19645,0.29451]},{"body_a":"peg","body_b":"channel_base_body","contact_count":848.0,"contact_point_centroid":[0.49412,0.05903,0.00939],"force_p95":0.55034,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54594,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48883,0.10224,0.08847]},{"body_a":"peg","body_b":"channel_base_body","contact_count":87.0,"contact_point_centroid":[0.4941,0.05889,0.00939],"force_p95":0.55033,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55101,"mean_force":0.54627,"phase_index":1.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.48582,0.10795,0.1515]}],"total_contact_groups":13},"final_pose_error":0.0256,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49755,-0.0839,0.03599],"final_tcp_position":[0.50189,-0.05483,0.03639],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":237.44785,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":341.0,"n_steps_budget":1000.0,"object_pos_end":[0.49416,0.05887,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13913,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54693,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":347.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach_pre_contact","tcp_end":[0.48926,0.10182,0.1546],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12826,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":87.0,"n_steps_budget":600.0,"object_pos_end":[0.49418,0.05886,0.03386],"object_pos_start":[0.49416,0.05887,0.03385],"object_to_goal_dist_end":0.13912,"object_to_goal_dist_start":0.13913,"object_z_max":0.03386,"peak_contact_force":0.5416,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":87.0,"raw_peak_contact_force":0.55101,"subtask_id":"approach_pre_contact","tcp_end":[0.48302,0.11652,0.15034],"tcp_start":[0.48926,0.10182,0.1546],"tcp_to_object_dist_end":0.13045,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":848.0,"n_steps_budget":1000.0,"object_pos_end":[0.49397,0.05878,0.03397],"object_pos_start":[0.49418,0.05886,0.03386],"object_to_goal_dist_end":0.13904,"object_to_goal_dist_start":0.13912,"object_z_max":0.03397,"peak_contact_force":47.81326,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":849.0,"raw_peak_contact_force":47.81326,"subtask_id":"approach_pre_contact","tcp_end":[0.49682,0.08944,0.03458],"tcp_start":[0.48302,0.11652,0.15034],"tcp_to_object_dist_end":0.0308,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":499.0,"n_steps_budget":1000.0,"object_pos_end":[0.49755,-0.0839,0.03599],"object_pos_start":[0.49397,0.05878,0.03397],"object_to_goal_dist_end":0.00611,"object_to_goal_dist_start":0.13904,"object_z_max":0.04001,"peak_contact_force":153.70588,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1091.0,"raw_peak_contact_force":237.44785,"subtask_id":"push_insertion","tcp_end":[0.50189,-0.05483,0.03639],"tcp_start":[0.49682,0.08944,0.03458],"tcp_to_object_dist_end":0.02939,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50714,"average_solve_count":140.0,"average_success_count":140.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_x_offset":-0.01275,"descend_1.descend_force_threshold":24.29243,"descend_1.descend_speed":0.0613,"descend_1.lateral_x_offset":-0.00597,"push_1.lateral_x_offset":-0.00916,"push_1.push_retry_x_offset":0.00499,"push_1.push_speed":0.06402,"rotate_1.lateral_x_offset":0.01476},"optimized_scores":{"best_composite_score":0.14575,"best_fitness_score":0.60575,"best_task_score":0.40278},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_left_wall","contact_count":548.0,"contact_point_centroid":[0.52589,-0.01042,0.02803],"force_p95":114.27594,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":139.5596,"mean_force":46.3406,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48904,0.00548,0.0346]},{"body_a":"attachment","body_b":"peg","contact_count":524.0,"contact_point_centroid":[0.49736,-0.00373,0.03539],"force_p95":126.33142,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":135.48567,"mean_force":70.76181,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48893,0.00284,0.03465]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":68.0,"contact_point_centroid":[0.47499,-0.0526,0.03905],"force_p95":114.55969,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":124.73745,"mean_force":89.79263,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48628,-0.05266,0.03501]},{"body_a":"peg","body_b":"channel_base_body","contact_count":511.0,"contact_point_centroid":[0.50846,-0.02149,0.00951],"force_p95":83.24744,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":88.34596,"mean_force":46.81632,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48904,0.00423,0.03473]},{"body_a":"peg","body_b":"channel_base_body","contact_count":52.0,"contact_point_centroid":[0.51278,-0.10055,0.03076],"force_p95":60.8642,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":62.41627,"mean_force":38.93129,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48629,-0.05728,0.03494]},{"body_a":"peg","body_b":"link7","contact_count":286.0,"contact_point_centroid":[0.51893,-0.03364,0.0673],"force_p95":36.1707,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.15351,"mean_force":26.92924,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48803,-0.01314,0.03483]},{"body_a":"peg","body_b":"channel_base_body","contact_count":293.0,"contact_point_centroid":[0.50542,0.08086,0.00934],"force_p95":0.58945,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.59884,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50846,0.15836,0.22195]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50024,0.19688,0.29406]},{"body_a":"peg","body_b":"channel_base_body","contact_count":87.0,"contact_point_centroid":[0.50635,0.08109,0.00938],"force_p95":0.55012,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55023,"mean_force":0.54677,"phase_index":1.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.51335,0.12827,0.15199]},{"body_a":"peg","body_b":"channel_base_body","contact_count":585.0,"contact_point_centroid":[0.50592,0.08084,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5501,"mean_force":0.54677,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50228,0.12463,0.09322]}],"total_contact_groups":10},"final_pose_error":0.01991,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.51325,-0.07137,0.03582],"final_tcp_position":[0.48628,-0.06129,0.03494],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":139.5596,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":322.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54522,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":329.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach_pre_contact","tcp_end":[0.5171,0.1218,0.15551],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1289,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":87.0,"n_steps_budget":600.0,"object_pos_end":[0.50598,0.08086,0.03378],"object_pos_start":[0.50598,0.0809,0.03378],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":0.54605,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":87.0,"raw_peak_contact_force":0.55023,"subtask_id":"approach_pre_contact","tcp_end":[0.51016,0.13731,0.15074],"tcp_start":[0.5171,0.1218,0.15551],"tcp_to_object_dist_end":0.12994,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":585.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.50598,0.08086,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16109,"object_z_max":0.03378,"peak_contact_force":0.54527,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":585.0,"raw_peak_contact_force":0.5501,"subtask_id":"approach_pre_contact","tcp_end":[0.49673,0.11188,0.03728],"tcp_start":[0.51016,0.13731,0.15074],"tcp_to_object_dist_end":0.03252,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":604.0,"n_steps_budget":1000.0,"object_pos_end":[0.51325,-0.07137,0.03582],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.01635,"object_to_goal_dist_start":0.16113,"object_z_max":0.03936,"peak_contact_force":126.93142,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1989.0,"raw_peak_contact_force":139.5596,"subtask_id":"push_insertion","tcp_end":[0.48628,-0.06129,0.03494],"tcp_start":[0.49673,0.11188,0.03728],"tcp_to_object_dist_end":0.0288,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.16384,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_x_offset":0.00239,"descend_1.descend_force_threshold":14.90473,"descend_1.descend_speed":0.03906,"descend_1.lateral_x_offset":-0.00472,"push_1.lateral_x_offset":-0.0153,"push_1.push_retry_x_offset":0.00118,"push_1.push_speed":0.05705,"rotate_1.lateral_x_offset":-0.0206},"optimized_scores":{"best_composite_score":0.27995,"best_fitness_score":0.73995,"best_task_score":0.72},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":358.0,"contact_point_centroid":[0.47498,-0.03606,0.04106],"force_p95":173.58966,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":186.64214,"mean_force":122.33931,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48636,-0.0361,0.03735]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":673.0,"contact_point_centroid":[0.52598,-0.01536,0.02857],"force_p95":94.88053,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":116.49456,"mean_force":43.78412,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48774,-0.00024,0.03624]},{"body_a":"attachment","body_b":"peg","contact_count":669.0,"contact_point_centroid":[0.49653,-0.0078,0.03642],"force_p95":102.61969,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":109.1869,"mean_force":54.65153,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48765,-0.00174,0.03627]},{"body_a":"peg","body_b":"channel_base_body","contact_count":617.0,"contact_point_centroid":[0.50889,-0.02739,0.00972],"force_p95":50.22566,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":67.72773,"mean_force":28.10378,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48762,-0.00455,0.03645]},{"body_a":"peg","body_b":"channel_base_body","contact_count":143.0,"contact_point_centroid":[0.51106,-0.10051,0.03461],"force_p95":43.95791,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":52.06844,"mean_force":27.57383,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48634,-0.05154,0.03788]},{"body_a":"peg","body_b":"link7","contact_count":241.0,"contact_point_centroid":[0.51888,-0.03168,0.06824],"force_p95":28.77184,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.74592,"mean_force":14.34119,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48644,-0.01284,0.03625]},{"body_a":"peg","body_b":"channel_base_body","contact_count":275.0,"contact_point_centroid":[0.5055,0.10461,0.00936],"force_p95":0.61051,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.58744,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51022,0.16966,0.22303]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50036,0.19789,0.29481]},{"body_a":"peg","body_b":"channel_base_body","contact_count":88.0,"contact_point_centroid":[0.5056,0.10515,0.00939],"force_p95":0.57445,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57941,"mean_force":0.54639,"phase_index":1.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.51636,0.14949,0.15309]},{"body_a":"peg","body_b":"channel_base_body","contact_count":591.0,"contact_point_centroid":[0.50587,0.10452,0.00939],"force_p95":0.57565,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57865,"mean_force":0.54634,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50433,0.14694,0.09405]}],"total_contact_groups":10},"final_pose_error":0.02324,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.51283,-0.07032,0.03683],"final_tcp_position":[0.48637,-0.05692,0.0379],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":186.64214,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":302.0,"n_steps_budget":1000.0,"object_pos_end":[0.50587,0.10458,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18477,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54778,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":307.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach_pre_contact","tcp_end":[0.52047,0.14294,0.15684],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12967,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":88.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.10461,0.03384],"object_pos_start":[0.50587,0.10458,0.03383],"object_to_goal_dist_end":0.18481,"object_to_goal_dist_start":0.18477,"object_z_max":0.03384,"peak_contact_force":0.53281,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":88.0,"raw_peak_contact_force":0.57941,"subtask_id":"approach_pre_contact","tcp_end":[0.51283,0.15856,0.15189],"tcp_start":[0.52047,0.14294,0.15684],"tcp_to_object_dist_end":0.12997,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":591.0,"n_steps_budget":1000.0,"object_pos_end":[0.50583,0.10466,0.03384],"object_pos_start":[0.50599,0.10461,0.03384],"object_to_goal_dist_end":0.18486,"object_to_goal_dist_start":0.18481,"object_z_max":0.03384,"peak_contact_force":0.54523,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":591.0,"raw_peak_contact_force":0.57865,"subtask_id":"approach_pre_contact","tcp_end":[0.49813,0.13534,0.03761],"tcp_start":[0.51283,0.15856,0.15189],"tcp_to_object_dist_end":0.03186,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":790.0,"n_steps_budget":1000.0,"object_pos_end":[0.51283,-0.07032,0.03683],"object_pos_start":[0.50583,0.10466,0.03384],"object_to_goal_dist_end":0.01638,"object_to_goal_dist_start":0.18486,"object_z_max":0.04042,"peak_contact_force":158.90547,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2701.0,"raw_peak_contact_force":186.64214,"subtask_id":"push_insertion","tcp_end":[0.48637,-0.05692,0.0379],"tcp_start":[0.49813,0.13534,0.03761],"tcp_to_object_dist_end":0.02968,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```