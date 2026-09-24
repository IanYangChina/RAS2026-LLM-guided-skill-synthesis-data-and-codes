## Search State

- **Seed**: 3
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → contact → push → push → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | time_limit | pose_tolerance | 8 | -0.0206 | 0.10 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.4176 | 0.11 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.4164 | 0.11 | ❌ rejected |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.3943 | 0.10 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.4153 | 0.12 | ❌ rejected |

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

## Current Skill (Q=-0.021) — your mutation base

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

- **Composite score**: -0.021
- **task_score** (E): 0.097
- **fitness_score**: 0.219  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1818 |
| descend_1 | 1.00 | 1.00 | 0.0838 |
| lateral_align | 1.00 | 1.00 | 0.0107 |
| push_1 | 1.00 | 1.00 | 0.0677 |
| retract_1 | 1.00 | 1.00 | 0.0804 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.117, 0.141) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.549 | 3.954 |
| descend_1 | contact | 1.00 / force_exceeded | (0.505, 0.117, 0.141)→(0.499, 0.109, 0.059) | (0.502, 0.081, 0.034)→(0.502, 0.082, 0.034) | 0.162→0.162 | 1.00 / 2.000 | 26.306 | 26.306 |
| lateral_align | push | 1.00 / step_budget | (0.499, 0.109, 0.059)→(0.488, 0.109, 0.059) | (0.502, 0.082, 0.034)→(0.497, 0.081, 0.036) | 0.162→0.161 | 1.00 / 2.333 | 63.540 | 65.436 |
| push_1 | push | 1.00 / time_limit | (0.488, 0.109, 0.059)→(0.488, 0.041, 0.059) | (0.497, 0.081, 0.036)→(0.501, 0.040, 0.033) | 0.161→0.120 | 1.00 / 2.667 | 67.435 | 144.759 |
| retract_1 | retract | 1.00 / step_budget | (0.488, 0.041, 0.059)→(0.485, 0.041, 0.139) | (0.501, 0.040, 0.033)→(0.501, 0.031, 0.027) | 0.120→0.112 | 1.00 / 1.000 | 0.555 | 73.750 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.304
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.065
- phase_score: 0.339
- phase_breakdown.pre_contact_score: 0.773
- phase_breakdown.goal_push_score: 0.153

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.230
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.171
- **Median Q (composite search score)**: -0.016
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.256


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.03518,"average_solve_count":199.0,"average_success_count":199.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08085,"approach_1.approach_speed":0.04271,"descend_1.contact_force":4.43282,"lateral_align.lateral_distance":-0.0101,"lateral_align.lateral_speed":0.02918,"push_1.push_distance":0.19579,"push_1.push_speed":0.04968,"push_1.push_time":8.81346},"optimized_scores":{"best_composite_score":-0.0104,"best_fitness_score":0.2296,"best_task_score":0.06534},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":872.0,"contact_point_centroid":[0.475,0.04127,0.05999],"force_p95":96.38869,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":316.22325,"mean_force":87.10981,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48145,0.05129,0.05912]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.475,0.00053,0.05999],"force_p95":77.96338,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":79.28805,"mean_force":66.04136,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48206,0.01012,0.05904]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":12.0,"contact_point_centroid":[0.47499,0.07697,0.05991],"force_p95":72.86843,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":74.52128,"mean_force":53.28223,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"push","tcp_position_centroid":[0.48183,0.08666,0.05886]},{"body_a":"attachment","body_b":"peg","contact_count":477.0,"contact_point_centroid":[0.49053,0.05067,0.05803],"force_p95":26.89137,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.17163,"mean_force":7.16486,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48132,0.05759,0.05915]},{"body_a":"peg","body_b":"channel_base_body","contact_count":993.0,"contact_point_centroid":[0.50206,0.03472,0.00941],"force_p95":14.69998,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.31316,"mean_force":2.23644,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48145,0.05117,0.05912]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.48652,0.05077,0.00946],"force_p95":1.67103,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.56238,"mean_force":1.56263,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"push","tcp_position_centroid":[0.48218,0.08672,0.05904]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.48732,0.07582,0.05889],"force_p95":16.65323,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.78273,"mean_force":4.21847,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"push","tcp_position_centroid":[0.4828,0.08685,0.05941]},{"body_a":"peg","body_b":"channel_base_body","contact_count":469.0,"contact_point_centroid":[0.49425,0.05911,0.00939],"force_p95":0.55045,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.654,"mean_force":0.5826,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.47418,0.09129,0.09652]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.48864,0.07643,0.05878],"force_p95":17.12023,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.12023,"mean_force":17.12023,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.48287,0.08691,0.05969]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":301.0,"contact_point_centroid":[0.52503,0.03097,0.05788],"force_p95":12.65436,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.3054,"mean_force":7.08928,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48136,0.05067,0.05915]},{"body_a":"peg","body_b":"channel_base_body","contact_count":237.0,"contact_point_centroid":[0.50224,0.01195,0.00803],"force_p95":0.77016,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.60853,"mean_force":0.78413,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.47957,0.01003,0.09829]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":10.0,"contact_point_centroid":[0.47495,0.03253,0.02421],"force_p95":6.2604,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.40412,"mean_force":1.55035,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48187,0.02485,0.05908]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":13.0,"contact_point_centroid":[0.52501,-0.01033,0.02418],"force_p95":6.11489,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.40238,"mean_force":3.76789,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.47919,0.01006,0.10926]},{"body_a":"peg","body_b":"channel_base_body","contact_count":371.0,"contact_point_centroid":[0.49443,0.05887,0.00934],"force_p95":0.60191,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.58563,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48274,0.14565,0.21292]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49875,0.19723,0.29545]}],"total_contact_groups":15},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50261,0.01028,0.02423],"final_tcp_position":[0.47929,0.01006,0.13926],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":316.22325,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":400.0,"n_steps_budget":1000.0,"object_pos_end":[0.49422,0.05892,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13918,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54871,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":406.0,"raw_peak_contact_force":4.20518,"subtask_id":"pre_contact","tcp_end":[0.46802,0.09619,0.13629],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11211,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":469.0,"n_steps_budget":690.0,"object_pos_end":[0.494,0.05907,0.03391],"object_pos_start":[0.49422,0.05892,0.03385],"object_to_goal_dist_end":0.13933,"object_to_goal_dist_start":0.13918,"object_z_max":0.03391,"peak_contact_force":17.654,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":470.0,"raw_peak_contact_force":17.654,"tcp_end":[0.48291,0.0869,0.05956],"tcp_start":[0.46802,0.09619,0.13629],"tcp_to_object_dist_end":0.03944,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.49438,0.05905,0.03422],"object_pos_start":[0.494,0.05907,0.03391],"object_to_goal_dist_end":0.13929,"object_to_goal_dist_start":0.13933,"object_z_max":0.03433,"peak_contact_force":74.52128,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":37.0,"raw_peak_contact_force":74.52128,"tcp_end":[0.48141,0.08659,0.05903],"tcp_start":[0.48291,0.0869,0.05956],"tcp_to_object_dist_end":0.03927,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5007,0.01158,0.02406],"object_pos_start":[0.49438,0.05905,0.03422],"object_to_goal_dist_end":0.09296,"object_to_goal_dist_start":0.13929,"object_z_max":0.04056,"peak_contact_force":91.55361,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2653.0,"raw_peak_contact_force":316.22325,"subtask_id":"goal_push","tcp_end":[0.48206,0.01015,0.05904],"tcp_start":[0.48141,0.08659,0.05903],"tcp_to_object_dist_end":0.03967,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":237.0,"n_steps_budget":630.0,"object_pos_end":[0.50261,0.01028,0.02423],"object_pos_start":[0.5007,0.01158,0.02406],"object_to_goal_dist_end":0.09169,"object_to_goal_dist_start":0.09296,"object_z_max":0.02433,"peak_contact_force":0.55435,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":252.0,"raw_peak_contact_force":79.28805,"tcp_end":[0.47929,0.01006,0.13926],"tcp_start":[0.48206,0.01015,0.05904],"tcp_to_object_dist_end":0.11737,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10823,"average_solve_count":231.0,"average_success_count":231.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08465,"approach_1.approach_speed":0.02817,"descend_1.contact_force":6.54501,"lateral_align.lateral_distance":-0.02897,"lateral_align.lateral_speed":0.03911,"push_1.push_distance":0.171,"push_1.push_speed":0.03264,"push_1.push_time":7.35722},"optimized_scores":{"best_composite_score":-0.0359,"best_fitness_score":0.2041,"best_task_score":0.05299},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":33.0,"contact_point_centroid":[0.48833,0.08439,0.00939],"force_p95":61.75075,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":62.30783,"mean_force":50.686,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"push","tcp_position_centroid":[0.50515,0.10818,0.05879]},{"body_a":"attachment","body_b":"peg","contact_count":33.0,"contact_point_centroid":[0.50962,0.09726,0.05888],"force_p95":61.31367,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":61.86756,"mean_force":50.25659,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"push","tcp_position_centroid":[0.50515,0.10818,0.05879]},{"body_a":"peg","body_b":"channel_base_body","contact_count":243.0,"contact_point_centroid":[0.49521,0.03297,0.0094],"force_p95":0.6501,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.44759,"mean_force":1.06695,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49693,0.03216,0.09784]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.51078,0.03165,0.05842],"force_p95":36.42597,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.89748,"mean_force":9.14211,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49893,0.03221,0.05946]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50719,0.05503,0.00912],"force_p95":51.96568,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":52.43706,"mean_force":45.09963,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49907,0.07074,0.05807]},{"body_a":"attachment","body_b":"peg","contact_count":1000.0,"contact_point_centroid":[0.50921,0.06608,0.05741],"force_p95":51.47731,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.97325,"mean_force":44.62593,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49907,0.07074,0.05807]},{"body_a":"peg","body_b":"channel_base_body","contact_count":344.0,"contact_point_centroid":[0.50603,0.08095,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.36893,"mean_force":0.63638,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.51776,0.11205,0.09912]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51361,0.0972,0.0587],"force_p95":30.86801,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.86801,"mean_force":30.86801,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.50879,0.10815,0.05942]},{"body_a":"peg","body_b":"channel_base_body","contact_count":353.0,"contact_point_centroid":[0.50551,0.08086,0.00935],"force_p95":0.56701,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.58999,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51413,0.15626,0.21518]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50023,0.19772,0.29553]}],"total_contact_groups":10},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49592,0.03326,0.03388],"final_tcp_position":[0.49667,0.03218,0.13889],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":62.30783,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":382.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54528,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":389.0,"raw_peak_contact_force":4.32595,"subtask_id":"pre_contact","tcp_end":[0.52848,0.11642,0.14016],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1144,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":344.0,"n_steps_budget":690.0,"object_pos_end":[0.506,0.08088,0.03378],"object_pos_start":[0.50598,0.0809,0.03378],"object_to_goal_dist_end":0.16111,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":31.36893,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":345.0,"raw_peak_contact_force":31.36893,"tcp_end":[0.50874,0.10813,0.0592],"tcp_start":[0.52848,0.11642,0.14016],"tcp_to_object_dist_end":0.03737,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":33.0,"n_steps_budget":600.0,"object_pos_end":[0.50016,0.08046,0.03568],"object_pos_start":[0.506,0.08088,0.03378],"object_to_goal_dist_end":0.16052,"object_to_goal_dist_start":0.16111,"object_z_max":0.03563,"peak_contact_force":61.4953,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":66.0,"raw_peak_contact_force":62.30783,"tcp_end":[0.49968,0.10862,0.0592],"tcp_start":[0.50874,0.10813,0.0592],"tcp_to_object_dist_end":0.0367,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49612,0.03329,0.03374],"object_pos_start":[0.50016,0.08046,0.03568],"object_to_goal_dist_end":0.11353,"object_to_goal_dist_start":0.16052,"object_z_max":0.03568,"peak_contact_force":49.94181,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2000.0,"raw_peak_contact_force":52.43706,"subtask_id":"goal_push","tcp_end":[0.49954,0.0324,0.05848],"tcp_start":[0.49968,0.10862,0.0592],"tcp_to_object_dist_end":0.02499,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":243.0,"n_steps_budget":630.0,"object_pos_end":[0.49592,0.03326,0.03388],"object_pos_start":[0.49612,0.03329,0.03374],"object_to_goal_dist_end":0.1135,"object_to_goal_dist_start":0.11353,"object_z_max":0.03447,"peak_contact_force":0.54817,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":257.0,"raw_peak_contact_force":53.44759,"tcp_end":[0.49667,0.03218,0.13889],"tcp_start":[0.49954,0.0324,0.05848],"tcp_to_object_dist_end":0.10502,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.92653,"average_solve_count":245.0,"average_success_count":245.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09015,"approach_1.approach_speed":0.02556,"descend_1.contact_force":2.82095,"lateral_align.lateral_distance":-0.04129,"lateral_align.lateral_speed":0.01897,"push_1.push_distance":0.166,"push_1.push_speed":0.03109,"push_1.push_time":5.72714},"optimized_scores":{"best_composite_score":-0.01557,"best_fitness_score":0.22443,"best_task_score":0.17149},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.475,0.07283,0.06],"force_p95":86.66256,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":88.51305,"mean_force":70.00816,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48278,0.08183,0.05892]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":829.0,"contact_point_centroid":[0.475,0.09677,0.05999],"force_p95":64.14089,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":65.61606,"mean_force":56.80276,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48279,0.10576,0.0589]},{"body_a":"peg","body_b":"channel_base_body","contact_count":75.0,"contact_point_centroid":[0.48727,0.10894,0.00938],"force_p95":59.26179,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.48027,"mean_force":49.94239,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"push","tcp_position_centroid":[0.49664,0.13143,0.05941]},{"body_a":"attachment","body_b":"peg","contact_count":75.0,"contact_point_centroid":[0.50379,0.12209,0.05913],"force_p95":58.80508,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.0211,"mean_force":51.10771,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"push","tcp_position_centroid":[0.49664,0.13143,0.05941]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50674,0.08401,0.00986],"force_p95":33.24019,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.96917,"mean_force":4.08136,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48285,0.10709,0.05894]},{"body_a":"attachment","body_b":"peg","contact_count":788.0,"contact_point_centroid":[0.49205,0.09623,0.05801],"force_p95":36.31036,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.55125,"mean_force":7.82508,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48282,0.10338,0.05896]},{"body_a":"peg","body_b":"channel_base_body","contact_count":384.0,"contact_point_centroid":[0.50584,0.10482,0.00939],"force_p95":0.57555,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.89653,"mean_force":0.62278,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.51106,0.13425,0.10253]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51279,0.12141,0.05877],"force_p95":29.37285,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.37285,"mean_force":29.37285,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.50569,0.13102,0.05984]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":17.0,"contact_point_centroid":[0.47449,0.10566,0.058],"force_p95":26.606,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.80829,"mean_force":24.73789,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"push","tcp_position_centroid":[0.48726,0.1321,0.05999]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.47469,0.10574,0.0583],"force_p95":9.63398,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.57997,"mean_force":3.38146,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.484,0.1323,0.05997]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":529.0,"contact_point_centroid":[0.52503,0.07718,0.05999],"force_p95":8.14141,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.02922,"mean_force":5.3307,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48272,0.0968,0.05893]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.49278,0.07575,0.05755],"force_p95":4.67193,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.22924,"mean_force":1.03821,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48267,0.08175,0.05904]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.525,0.06027,0.06],"force_p95":4.11407,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32799,"mean_force":2.18876,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48278,0.08183,0.05892]},{"body_a":"peg","body_b":"channel_base_body","contact_count":316.0,"contact_point_centroid":[0.50548,0.10454,0.00936],"force_p95":0.60053,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.58215,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50897,0.16767,0.21928]},{"body_a":"peg","body_b":"channel_base_body","contact_count":230.0,"contact_point_centroid":[0.50583,0.0608,0.00892],"force_p95":0.99386,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.8037,"mean_force":0.59083,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48031,0.08139,0.0984]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49998,0.19841,0.29632]}],"total_contact_groups":16},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50514,0.04866,0.02411],"final_tcp_position":[0.48002,0.08137,0.13919],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":88.51305,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":343.0,"n_steps_budget":1000.0,"object_pos_end":[0.50583,0.10463,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18483,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.55165,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":348.0,"raw_peak_contact_force":3.33087,"subtask_id":"pre_contact","tcp_end":[0.51856,0.13811,0.14722],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11891,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":384.0,"n_steps_budget":720.0,"object_pos_end":[0.506,0.10466,0.03384],"object_pos_start":[0.50583,0.10463,0.03384],"object_to_goal_dist_end":0.18486,"object_to_goal_dist_start":0.18483,"object_z_max":0.03384,"peak_contact_force":29.89653,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":385.0,"raw_peak_contact_force":29.89653,"tcp_end":[0.50566,0.13101,0.05963],"tcp_start":[0.51856,0.13811,0.14722],"tcp_to_object_dist_end":0.03687,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":75.0,"n_steps_budget":1000.0,"object_pos_end":[0.49596,0.10369,0.03681],"object_pos_start":[0.506,0.10466,0.03384],"object_to_goal_dist_end":0.18376,"object_to_goal_dist_start":0.18486,"object_z_max":0.03681,"peak_contact_force":54.60415,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":167.0,"raw_peak_contact_force":59.48027,"tcp_end":[0.48429,0.13221,0.06016],"tcp_start":[0.50566,0.13101,0.05963],"tcp_to_object_dist_end":0.03866,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50675,0.07466,0.04072],"object_pos_start":[0.49596,0.10369,0.03681],"object_to_goal_dist_end":0.1548,"object_to_goal_dist_start":0.18376,"object_z_max":0.04072,"peak_contact_force":60.8084,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3155.0,"raw_peak_contact_force":65.61606,"subtask_id":"goal_push","tcp_end":[0.48278,0.08185,0.05892],"tcp_start":[0.48429,0.13221,0.06016],"tcp_to_object_dist_end":0.03094,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":239.0,"n_steps_budget":630.0,"object_pos_end":[0.50514,0.04866,0.02411],"object_pos_start":[0.50675,0.07466,0.04072],"object_to_goal_dist_end":0.12974,"object_to_goal_dist_start":0.1548,"object_z_max":0.04074,"peak_contact_force":0.56215,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":240.0,"raw_peak_contact_force":88.51305,"tcp_end":[0.48002,0.08137,0.13919],"tcp_start":[0.48278,0.08185,0.05892],"tcp_to_object_dist_end":0.12225,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```