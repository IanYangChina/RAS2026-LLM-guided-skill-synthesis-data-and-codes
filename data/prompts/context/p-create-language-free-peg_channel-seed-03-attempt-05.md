## Search State

- **Seed**: 3
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → contact → align → push → retract | linear_cartesian | linear_cartesian | joint_interpolation | impedance_motion | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 7 | -0.1447 | 0.03 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.4195 | 0.12 | ✅ accepted |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 6 | -0.0583 | 0.00 | ❌ rejected |
| 2 | approach → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.0214 | 0.02 | ❌ rejected |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.4166 | 0.12 | ✅ accepted |

**Proposal policy**: task_score is 0.03 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.145) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.025
  - 0.1
  weight: 0.3
- id: goal_push
  offset:
  - 0.0
  - 0.025
  - 0.0
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
    offset:
    - 0.0
    - 0.025
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_contact
- id: descend_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.025
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
- id: push_1
  type: push
  generator: impedance_motion
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
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.14
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: goal_push
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.025, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.025, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.145
- **task_score** (E): 0.034
- **fitness_score**: 0.095  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1415 |
| descend_1 | 1.00 | 1.00 | 0.1332 |
| align_1 | 1.00 | 1.00 | 0.0223 |
| push_1 | 0.33 | 1.00 | 0.0435 |
| retract_1 | 1.00 | 1.00 | 0.0804 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.506, 0.120, 0.191) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.545 | 3.954 |
| descend_1 | contact | 1.00 / force_exceeded | (0.506, 0.120, 0.191)→(0.500, 0.108, 0.060) | (0.502, 0.081, 0.034)→(0.502, 0.082, 0.034) | 0.162→0.162 | 1.00 / 2.000 | 32.476 | 32.476 |
| align_1 | align | 1.00 / step_budget | (0.500, 0.108, 0.060)→(0.492, 0.129, 0.056) | (0.502, 0.082, 0.034)→(0.499, 0.084, 0.037) | 0.162→0.165 | 1.00 / 1.667 | 25.933 | 52.775 |
| push_1 | push | 0.33 / guard_failure | (0.492, 0.128, 0.056)→(0.491, 0.085, 0.054) | (0.499, 0.084, 0.037)→(0.500, 0.066, 0.033) | 0.165→0.146 | 1.00 / 1.667 | 26.136 | 56.334 |
| retract_1 | retract | 1.00 / step_budget | (0.491, 0.085, 0.054)→(0.488, 0.084, 0.135) | (0.500, 0.066, 0.033)→(0.500, 0.061, 0.031) | 0.146→0.142 | 1.00 / 1.000 | 0.582 | 35.199 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.353
- alignment_error: None
- force_efficiency: 0.052
- terminal_score: 0.094
- phase_score: 0.288
- phase_breakdown.pre_contact_score: 0.180
- phase_breakdown.goal_insertion_score: 0.335

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.211
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.094
- **Median Q (composite search score)**: -0.202
- **K-run variance**: 0.0066
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.358


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.91758,"average_solve_count":182.0,"average_success_count":182.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18404,"approach_1.approach_speed":0.01837,"descend_1.contact_force":1.8142,"push_1.force_limit":38.0871,"push_1.push_distance":0.18151,"push_1.push_speed":0.04778,"push_1.retry_offset_x":0.01431},"optimized_scores":{"best_composite_score":-0.20272,"best_fitness_score":0.03728,"best_task_score":0.00415},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":189.0,"contact_point_centroid":[0.475,0.09836,0.05999],"force_p95":76.71703,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":79.64127,"mean_force":59.34548,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48416,0.09687,0.05863]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.475,0.1087,0.05997],"force_p95":77.308,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":77.51955,"mean_force":75.82961,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48352,0.10042,0.05871]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.475,0.10873,0.05997],"force_p95":74.9263,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":75.99598,"mean_force":65.15918,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4835,0.10043,0.05871]},{"body_a":"peg","body_b":"channel_base_body","contact_count":946.0,"contact_point_centroid":[0.49414,0.05894,0.00939],"force_p95":0.5503,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":58.15386,"mean_force":0.60691,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.47761,0.09376,0.14291]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49455,0.07707,0.05889],"force_p95":57.56575,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.56575,"mean_force":57.56575,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.48679,0.08615,0.06005]},{"body_a":"peg","body_b":"channel_base_body","contact_count":268.0,"contact_point_centroid":[0.49235,0.07508,0.00973],"force_p95":34.11288,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.57129,"mean_force":13.39928,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48452,0.09512,0.0587]},{"body_a":"attachment","body_b":"peg","contact_count":227.0,"contact_point_centroid":[0.49134,0.08454,0.05804],"force_p95":33.72575,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.15064,"mean_force":15.08711,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48467,0.09431,0.0587]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":138.0,"contact_point_centroid":[0.47498,0.06797,0.06],"force_p95":8.43381,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.5634,"mean_force":1.86295,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48436,0.09576,0.05861]},{"body_a":"peg","body_b":"channel_base_body","contact_count":246.0,"contact_point_centroid":[0.49472,0.05881,0.00931],"force_p95":0.6755,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.6056,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48376,0.14831,0.26242]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49855,0.19699,0.29734]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49977,0.0397,0.00959],"force_p95":1.42477,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.43382,"mean_force":1.32906,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48352,0.10042,0.05871]},{"body_a":"peg","body_b":"channel_base_body","contact_count":240.0,"contact_point_centroid":[0.49433,0.05493,0.00943],"force_p95":0.73585,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.07604,"mean_force":0.54646,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48104,0.09989,0.09817]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":16.0,"contact_point_centroid":[0.47494,0.05398,0.05937],"force_p95":0.2192,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29155,"mean_force":0.0851,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48165,0.1,0.07558]}],"total_contact_groups":13},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4943,0.05691,0.03414],"final_tcp_position":[0.48074,0.09984,0.13907],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":79.64127,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":275.0,"n_steps_budget":1000.0,"object_pos_end":[0.49421,0.05899,0.03384],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13925,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.5454,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":281.0,"raw_peak_contact_force":4.20518,"subtask_id":"pre_contact","tcp_end":[0.47024,0.10206,0.23176],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.20396,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":946.0,"n_steps_budget":1000.0,"object_pos_end":[0.49438,0.05909,0.03399],"object_pos_start":[0.49421,0.05899,0.03384],"object_to_goal_dist_end":0.13933,"object_to_goal_dist_start":0.13925,"object_z_max":0.03396,"peak_contact_force":58.15386,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":947.0,"raw_peak_contact_force":58.15386,"subtask_id":"pre_contact","tcp_end":[0.48687,0.08616,0.05992],"tcp_start":[0.47024,0.10206,0.23176],"tcp_to_object_dist_end":0.03823,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":269.0,"n_steps_budget":600.0,"object_pos_end":[0.49439,0.05611,0.03484],"object_pos_start":[0.49438,0.05909,0.03399],"object_to_goal_dist_end":0.13633,"object_to_goal_dist_start":0.13933,"object_z_max":0.03892,"peak_contact_force":76.08009,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":822.0,"raw_peak_contact_force":79.64127,"tcp_end":[0.48352,0.1004,0.05872],"tcp_start":[0.48687,0.08616,0.05992],"tcp_to_object_dist_end":0.05147,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49434,0.05575,0.03469],"object_pos_start":[0.49439,0.05611,0.03484],"object_to_goal_dist_end":0.13597,"object_to_goal_dist_start":0.13633,"object_z_max":0.03484,"peak_contact_force":75.40398,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":77.51955,"subtask_id":"goal_insertion","tcp_end":[0.48351,0.10043,0.05871],"tcp_start":[0.48351,0.10043,0.05871],"tcp_to_object_dist_end":0.05187,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":240.0,"n_steps_budget":630.0,"object_pos_end":[0.4943,0.05691,0.03414],"object_pos_start":[0.49421,0.05514,0.03454],"object_to_goal_dist_end":0.13715,"object_to_goal_dist_start":0.13538,"object_z_max":0.03578,"peak_contact_force":0.54134,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":259.0,"raw_peak_contact_force":75.99598,"tcp_end":[0.48074,0.09984,0.13907],"tcp_start":[0.48351,0.10043,0.05871],"tcp_to_object_dist_end":0.11418,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.92481,"average_solve_count":266.0,"average_success_count":266.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1408,"approach_1.approach_speed":0.03323,"descend_1.contact_force":6.79628,"push_1.force_limit":47.44107,"push_1.push_distance":0.14931,"push_1.push_speed":0.02146,"push_1.retry_offset_x":0.00311},"optimized_scores":{"best_composite_score":-0.02933,"best_fitness_score":0.21067,"best_task_score":0.09401},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":140.0,"contact_point_centroid":[0.50031,0.06421,0.05041],"force_p95":44.0424,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.41195,"mean_force":24.29805,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49409,0.074,0.05093]},{"body_a":"peg","body_b":"channel_base_body","contact_count":336.0,"contact_point_centroid":[0.50174,0.09574,0.00976],"force_p95":37.88179,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.71674,"mean_force":13.88455,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50066,0.12314,0.05639]},{"body_a":"attachment","body_b":"peg","contact_count":260.0,"contact_point_centroid":[0.50689,0.1104,0.05646],"force_p95":37.71111,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.24403,"mean_force":17.33577,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50164,0.12103,0.05688]},{"body_a":"peg","body_b":"channel_base_body","contact_count":351.0,"contact_point_centroid":[0.50597,0.04764,0.00915],"force_p95":32.3164,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.46614,"mean_force":8.99611,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49418,0.06812,0.051]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":39.0,"contact_point_centroid":[0.52501,0.03256,0.05689],"force_p95":21.53137,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.88917,"mean_force":18.00937,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49413,0.07079,0.05104]},{"body_a":"peg","body_b":"channel_base_body","contact_count":583.0,"contact_point_centroid":[0.50595,0.08086,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.22258,"mean_force":0.5788,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.51618,0.11316,0.12512]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.5128,0.09748,0.05873],"force_p95":18.81109,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.81109,"mean_force":18.81109,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.50655,0.10767,0.05964]},{"body_a":"peg","body_b":"channel_base_body","contact_count":267.0,"contact_point_centroid":[0.50548,0.08086,0.00933],"force_p95":0.60575,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.60391,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.514,0.15722,0.24204]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50039,0.19722,0.29599]},{"body_a":"peg","body_b":"channel_base_body","contact_count":242.0,"contact_point_centroid":[0.5047,0.02435,0.00804],"force_p95":0.68345,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68354,"mean_force":0.6059,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49082,0.0008,0.0892]}],"total_contact_groups":10},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50396,0.02438,0.02413],"final_tcp_position":[0.4906,0.00103,0.13032],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":47.41195,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":296.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54804,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":303.0,"raw_peak_contact_force":4.32595,"subtask_id":"pre_contact","tcp_end":[0.52784,0.11917,0.193],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16522,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":583.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,0.08088,0.03377],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.16111,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":19.22258,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":584.0,"raw_peak_contact_force":19.22258,"subtask_id":"pre_contact","tcp_end":[0.50652,0.10766,0.05943],"tcp_start":[0.52784,0.11917,0.193],"tcp_to_object_dist_end":0.03709,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":339.0,"n_steps_budget":600.0,"object_pos_end":[0.5028,0.07881,0.0366],"object_pos_start":[0.50595,0.08088,0.03377],"object_to_goal_dist_end":0.15888,"object_to_goal_dist_start":0.16111,"object_z_max":0.04059,"peak_contact_force":0.38038,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":596.0,"raw_peak_contact_force":38.71674,"tcp_end":[0.49697,0.13124,0.05459],"tcp_start":[0.50652,0.10766,0.05943],"tcp_to_object_dist_end":0.05573,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":354.0,"n_steps_budget":1000.0,"object_pos_end":[0.50558,0.02435,0.02414],"object_pos_start":[0.5028,0.07881,0.0366],"object_to_goal_dist_end":0.10569,"object_to_goal_dist_start":0.15888,"object_z_max":0.04023,"peak_contact_force":0.60102,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":530.0,"raw_peak_contact_force":47.41195,"subtask_id":"goal_insertion","tcp_end":[0.49353,0.0011,0.05009],"tcp_start":[0.49697,0.13124,0.05459],"tcp_to_object_dist_end":0.03687,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":242.0,"n_steps_budget":630.0,"object_pos_end":[0.50396,0.02438,0.02413],"object_pos_start":[0.50558,0.02435,0.02414],"object_to_goal_dist_end":0.10565,"object_to_goal_dist_start":0.10569,"object_z_max":0.02414,"peak_contact_force":0.68339,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":242.0,"raw_peak_contact_force":0.68354,"tcp_end":[0.4906,0.00103,0.13032],"tcp_start":[0.49353,0.0011,0.05009],"tcp_to_object_dist_end":0.10954,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.15084,"average_solve_count":179.0,"average_success_count":179.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09193,"approach_1.approach_speed":0.03054,"descend_1.contact_force":8.98579,"push_1.force_limit":42.73985,"push_1.push_distance":0.18512,"push_1.push_speed":0.02928,"push_1.retry_offset_x":0.00907},"optimized_scores":{"best_composite_score":-0.20192,"best_fitness_score":0.03808,"best_task_score":0.00478},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":16.0,"contact_point_centroid":[0.49137,0.11994,0.00986],"force_p95":43.75354,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.07036,"mean_force":24.96753,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49487,0.15397,0.05462]},{"body_a":"attachment","body_b":"peg","contact_count":16.0,"contact_point_centroid":[0.49896,0.1428,0.05422],"force_p95":43.43434,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.70629,"mean_force":24.6122,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49487,0.15397,0.05462]},{"body_a":"peg","body_b":"channel_base_body","contact_count":339.0,"contact_point_centroid":[0.49456,0.1198,0.00975],"force_p95":33.29225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.96576,"mean_force":13.96284,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49918,0.14643,0.05664]},{"body_a":"attachment","body_b":"peg","contact_count":339.0,"contact_point_centroid":[0.50426,0.13577,0.0562],"force_p95":32.81468,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.49145,"mean_force":13.50817,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49918,0.14643,0.05664]},{"body_a":"peg","body_b":"channel_base_body","contact_count":251.0,"contact_point_centroid":[0.4995,0.10741,0.00965],"force_p95":0.87854,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.9174,"mean_force":0.75683,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4919,0.15184,0.09345]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.49851,0.14146,0.0543],"force_p95":22.51885,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.19118,"mean_force":5.2708,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49405,0.1524,0.05462]},{"body_a":"peg","body_b":"channel_base_body","contact_count":394.0,"contact_point_centroid":[0.50579,0.10452,0.00939],"force_p95":0.57553,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.05215,"mean_force":0.59589,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.51106,0.13425,0.10336]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51266,0.12123,0.05885],"force_p95":19.64273,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.64273,"mean_force":19.64273,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.50573,0.13097,0.05989]},{"body_a":"peg","body_b":"channel_base_body","contact_count":313.0,"contact_point_centroid":[0.50555,0.10468,0.00936],"force_p95":0.60068,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.58243,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50897,0.16769,0.22013]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49998,0.19841,0.29633]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52501,0.10569,0.05867],"force_p95":0.14047,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14285,"mean_force":0.11904,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49155,0.15178,0.10578]}],"total_contact_groups":11},"final_pose_error":0.01973,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50057,0.10268,0.03531],"final_tcp_position":[0.49168,0.15181,0.13478],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":44.07036,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":340.0,"n_steps_budget":1000.0,"object_pos_end":[0.50592,0.10457,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18477,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54154,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":345.0,"raw_peak_contact_force":3.33087,"subtask_id":"pre_contact","tcp_end":[0.51856,0.13816,0.1489],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12053,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":394.0,"n_steps_budget":750.0,"object_pos_end":[0.50582,0.10466,0.03383],"object_pos_start":[0.50592,0.10457,0.03384],"object_to_goal_dist_end":0.18485,"object_to_goal_dist_start":0.18477,"object_z_max":0.03384,"peak_contact_force":20.05215,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":395.0,"raw_peak_contact_force":20.05215,"subtask_id":"pre_contact","tcp_end":[0.50571,0.13096,0.05967],"tcp_start":[0.51856,0.13816,0.1489],"tcp_to_object_dist_end":0.03687,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":339.0,"n_steps_budget":600.0,"object_pos_end":[0.5003,0.1183,0.03938],"object_pos_start":[0.50582,0.10466,0.03383],"object_to_goal_dist_end":0.19831,"object_to_goal_dist_start":0.18485,"object_z_max":0.03938,"peak_contact_force":1.33782,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":678.0,"raw_peak_contact_force":39.96576,"tcp_end":[0.49518,0.15445,0.05493],"tcp_start":[0.50571,0.13096,0.05967],"tcp_to_object_dist_end":0.03968,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":16.0,"n_steps_budget":1000.0,"object_pos_end":[0.49987,0.11755,0.03898],"object_pos_start":[0.5003,0.1183,0.03938],"object_to_goal_dist_end":0.19756,"object_to_goal_dist_start":0.19831,"object_z_max":0.03938,"peak_contact_force":2.40218,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":32.0,"raw_peak_contact_force":44.07036,"subtask_id":"goal_insertion","tcp_end":[0.49457,0.15273,0.05428],"tcp_start":[0.49456,0.15283,0.05433],"tcp_to_object_dist_end":0.03873,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":251.0,"n_steps_budget":660.0,"object_pos_end":[0.50057,0.10268,0.03531],"object_pos_start":[0.49996,0.11734,0.03884],"object_to_goal_dist_end":0.18274,"object_to_goal_dist_start":0.19734,"object_z_max":0.03934,"peak_contact_force":0.52157,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":264.0,"raw_peak_contact_force":28.9174,"tcp_end":[0.49168,0.15181,0.13478],"tcp_start":[0.49457,0.15273,0.05428],"tcp_to_object_dist_end":0.1113,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```