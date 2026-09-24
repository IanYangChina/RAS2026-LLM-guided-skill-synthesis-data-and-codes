## Search State

- **Seed**: 3
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → rotate → descend → push | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.2919 | 0.56 | ✅ accepted |
| 12 | approach → rotate → descend → push | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.2623 | 0.46 | ✅ accepted |
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.4187 | 0.00 | ❌ rejected |
| 10 | approach → rotate → descend → push | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | 7 | -0.1611 | 0.13 | ❌ rejected |
| 9 | approach → rotate → descend → push | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | -0.0292 | 0.25 | ❌ rejected |

**Proposal policy**: task_score is 0.56 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.292) — your mutation base

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

- **Composite score**: 0.292
- **task_score** (E): 0.560
- **fitness_score**: 0.669  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.083
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1665 |
| rotate_1 | 1.00 | 1.00 | 0.0177 |
| descend_1 | 0.33 | 1.00 | 0.1179 |
| push_1 | 1.00 | 1.00 | 0.1686 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.519, 0.122, 0.155) | (0.509, 0.081, 0.040)→(0.502, 0.082, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.548 | 3.954 |
| rotate_1 | rotate | 1.00 / step_budget | (0.519, 0.122, 0.155)→(0.512, 0.138, 0.150) | (0.502, 0.082, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.162 | 1.00 / 1.000 | 0.549 | 0.560 |
| descend_1 | descend | 0.33 / step_budget | (0.512, 0.138, 0.150)→(0.495, 0.113, 0.038) | (0.502, 0.081, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.162 | 1.00 / 1.333 | 20.601 | 20.618 |
| push_1 | push | 1.00 / step_budget | (0.495, 0.113, 0.038)→(0.498, -0.056, 0.035) | (0.502, 0.081, 0.034)→(0.510, -0.075, 0.035) | 0.162→0.017 | 1.00 / 4.000 | 98.276 | 207.911 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.898
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.307
- phase_score: 0.768
- phase_breakdown.push_insertion_score: 0.932
- phase_breakdown.approach_pre_contact_score: 0.111

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.819
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.359
- **K-run variance**: 0.0111
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.223


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57143,"average_solve_count":133.0,"average_success_count":133.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_x_offset":0.04211,"descend_1.descend_force_threshold":9.59165,"descend_1.descend_speed":0.05073,"descend_1.lateral_x_offset":0.01372,"push_1.lateral_x_offset":0.00702,"push_1.push_retry_x_offset":-0.00259,"push_1.push_speed":0.08147,"rotate_1.lateral_x_offset":0.00516},"optimized_scores":{"best_composite_score":0.37358,"best_fitness_score":0.58358,"best_task_score":0.30745},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":69.0,"contact_point_centroid":[0.55813,-0.1,0.06497],"force_p95":188.94203,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":253.02362,"mean_force":119.6285,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50227,-0.05355,0.03492]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":117.0,"contact_point_centroid":[0.52502,-0.04288,0.05999],"force_p95":156.454,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":220.46629,"mean_force":97.68021,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5022,-0.04355,0.03469]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":34.0,"contact_point_centroid":[0.54458,0.05141,0.06],"force_p95":81.52037,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":88.29168,"mean_force":71.46323,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50152,0.04847,0.03365]},{"body_a":"attachment","body_b":"peg","contact_count":174.0,"contact_point_centroid":[0.49904,-0.01155,0.03579],"force_p95":27.6118,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":71.80051,"mean_force":9.84528,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50195,-0.00028,0.03433]},{"body_a":"peg","body_b":"channel_base_body","contact_count":74.0,"contact_point_centroid":[0.49386,-0.10075,0.04299],"force_p95":35.65603,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":68.88376,"mean_force":16.17863,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50231,-0.05433,0.03502]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.09071,0.06],"force_p95":60.72579,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":60.72579,"mean_force":60.72579,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50325,0.09005,0.03635]},{"body_a":"peg","body_b":"channel_base_body","contact_count":294.0,"contact_point_centroid":[0.49634,-0.03001,0.00931],"force_p95":13.23353,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.88937,"mean_force":2.77483,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50191,0.00429,0.03417]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":209.0,"contact_point_centroid":[0.47477,-0.00847,0.03893],"force_p95":3.51864,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.87181,"mean_force":0.97639,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5017,0.02173,0.03382]},{"body_a":"peg","body_b":"channel_base_body","contact_count":315.0,"contact_point_centroid":[0.49457,0.05884,0.00933],"force_p95":0.61835,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.59263,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50215,0.1479,0.22144]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49973,0.19649,0.29454]},{"body_a":"peg","body_b":"channel_base_body","contact_count":718.0,"contact_point_centroid":[0.49405,0.05906,0.00939],"force_p95":0.5503,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54598,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49975,0.10315,0.09064]},{"body_a":"peg","body_b":"channel_base_body","contact_count":87.0,"contact_point_centroid":[0.49415,0.05893,0.00939],"force_p95":0.55033,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55101,"mean_force":0.54631,"phase_index":1.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.50175,0.10813,0.15109]}],"total_contact_groups":12},"final_pose_error":0.02394,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49329,-0.08473,0.03527],"final_tcp_position":[0.50255,-0.05694,0.03535],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":253.02362,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":344.0,"n_steps_budget":1000.0,"object_pos_end":[0.49422,0.05898,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13924,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54922,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":350.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach_pre_contact","tcp_end":[0.50521,0.10183,0.15436],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12838,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":87.0,"n_steps_budget":600.0,"object_pos_end":[0.49423,0.05898,0.03386],"object_pos_start":[0.49422,0.05898,0.03385],"object_to_goal_dist_end":0.13924,"object_to_goal_dist_start":0.13924,"object_z_max":0.03386,"peak_contact_force":0.54735,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":87.0,"raw_peak_contact_force":0.55101,"subtask_id":"approach_pre_contact","tcp_end":[0.49894,0.11695,0.14986],"tcp_start":[0.50521,0.10183,0.15436],"tcp_to_object_dist_end":0.12977,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":718.0,"n_steps_budget":1000.0,"object_pos_end":[0.49403,0.05877,0.03395],"object_pos_start":[0.49423,0.05898,0.03386],"object_to_goal_dist_end":0.13903,"object_to_goal_dist_start":0.13924,"object_z_max":0.03395,"peak_contact_force":60.72579,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":719.0,"raw_peak_contact_force":60.72579,"subtask_id":"approach_pre_contact","tcp_end":[0.50326,0.09001,0.03622],"tcp_start":[0.49894,0.11695,0.14986],"tcp_to_object_dist_end":0.03266,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":460.0,"n_steps_budget":1000.0,"object_pos_end":[0.49329,-0.08473,0.03527],"object_pos_start":[0.49403,0.05877,0.03395],"object_to_goal_dist_end":0.00947,"object_to_goal_dist_start":0.13903,"object_z_max":0.04028,"peak_contact_force":151.44144,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":971.0,"raw_peak_contact_force":253.02362,"subtask_id":"push_insertion","tcp_end":[0.50255,-0.05694,0.03535],"tcp_start":[0.50326,0.09001,0.03622],"tcp_to_object_dist_end":0.02929,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.9372,"average_solve_count":207.0,"average_success_count":207.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_x_offset":-0.00216,"descend_1.descend_force_threshold":13.42696,"descend_1.descend_speed":0.02741,"descend_1.lateral_x_offset":-0.01554,"push_1.lateral_x_offset":0.00734,"push_1.push_retry_x_offset":-0.00203,"push_1.push_speed":0.04751,"rotate_1.lateral_x_offset":-0.00576},"optimized_scores":{"best_composite_score":0.14343,"best_fitness_score":0.60343,"best_task_score":0.37189},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":138.0,"contact_point_centroid":[0.55328,-0.10001,0.06498],"force_p95":120.46969,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":165.69221,"mean_force":79.4554,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49189,-0.03607,0.03444]},{"body_a":"attachment","body_b":"peg","contact_count":973.0,"contact_point_centroid":[0.49869,0.00588,0.03319],"force_p95":140.85871,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":148.96962,"mean_force":108.08383,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49057,0.0115,0.03428]},{"body_a":"peg","body_b":"channel_base_body","contact_count":995.0,"contact_point_centroid":[0.51075,-0.01116,0.00917],"force_p95":106.15002,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":113.94998,"mean_force":75.11725,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49051,0.0137,0.03434]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":975.0,"contact_point_centroid":[0.5269,-0.00433,0.03121],"force_p95":103.89442,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":108.22331,"mean_force":78.8714,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49056,0.01168,0.03428]},{"body_a":"peg","body_b":"link7","contact_count":927.0,"contact_point_centroid":[0.52138,-0.01197,0.06688],"force_p95":61.46186,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.67464,"mean_force":41.70118,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49071,0.00728,0.03422]},{"body_a":"peg","body_b":"channel_base_body","contact_count":21.0,"contact_point_centroid":[0.51136,-0.10038,0.05308],"force_p95":45.16893,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.09808,"mean_force":35.698,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49607,-0.0477,0.03414]},{"body_a":"peg","body_b":"channel_base_body","contact_count":299.0,"contact_point_centroid":[0.50543,0.08086,0.00934],"force_p95":0.58247,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.59779,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51333,0.1583,0.22175]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50058,0.19694,0.29415]},{"body_a":"peg","body_b":"channel_base_body","contact_count":87.0,"contact_point_centroid":[0.50635,0.08109,0.00938],"force_p95":0.55012,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55023,"mean_force":0.54677,"phase_index":1.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.52261,0.12821,0.15141]},{"body_a":"peg","body_b":"channel_base_body","contact_count":582.0,"contact_point_centroid":[0.50598,0.08087,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5501,"mean_force":0.54677,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50325,0.12491,0.09382]}],"total_contact_groups":10},"final_pose_error":0.03385,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5113,-0.07406,0.03922],"final_tcp_position":[0.49659,-0.04846,0.03403],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":165.69221,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":328.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54542,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":335.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach_pre_contact","tcp_end":[0.52636,0.12161,0.15502],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12952,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":87.0,"n_steps_budget":600.0,"object_pos_end":[0.50598,0.08086,0.03378],"object_pos_start":[0.50598,0.0809,0.03378],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":0.54612,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":87.0,"raw_peak_contact_force":0.55023,"subtask_id":"approach_pre_contact","tcp_end":[0.5194,0.13742,0.15012],"tcp_start":[0.52636,0.12161,0.15502],"tcp_to_object_dist_end":0.13006,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":582.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.50598,0.08086,0.03378],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16109,"object_z_max":0.03378,"peak_contact_force":0.54612,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":582.0,"raw_peak_contact_force":0.5501,"subtask_id":"approach_pre_contact","tcp_end":[0.4888,0.11209,0.03821],"tcp_start":[0.5194,0.13742,0.15012],"tcp_to_object_dist_end":0.03591,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5113,-0.07406,0.03922],"object_pos_start":[0.50597,0.08086,0.03378],"object_to_goal_dist_end":0.01279,"object_to_goal_dist_start":0.16109,"object_z_max":0.03926,"peak_contact_force":110.54628,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4029.0,"raw_peak_contact_force":165.69221,"subtask_id":"push_insertion","tcp_end":[0.49659,-0.04846,0.03403],"tcp_start":[0.4888,0.11209,0.03821],"tcp_to_object_dist_end":0.02997,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51572,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_x_offset":0.00669,"descend_1.descend_force_threshold":19.42569,"descend_1.descend_speed":0.03696,"descend_1.lateral_x_offset":-0.01116,"push_1.lateral_x_offset":0.00127,"push_1.push_retry_x_offset":-0.00822,"push_1.push_speed":0.08092,"rotate_1.lateral_x_offset":-0.01506},"optimized_scores":{"best_composite_score":0.35875,"best_fitness_score":0.81875,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":55.0,"contact_point_centroid":[0.54953,-0.10001,0.06495],"force_p95":192.15169,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":205.01606,"mean_force":134.26811,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49071,-0.04266,0.03343]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":39.0,"contact_point_centroid":[0.52883,-0.01448,0.05999],"force_p95":140.64976,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":184.67656,"mean_force":93.25917,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48633,-0.01893,0.03294]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":779.0,"contact_point_centroid":[0.52733,0.01435,0.02847],"force_p95":115.32628,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":159.23197,"mean_force":69.40869,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48974,0.02556,0.03412]},{"body_a":"attachment","body_b":"peg","contact_count":760.0,"contact_point_centroid":[0.49872,0.02134,0.03384],"force_p95":135.27059,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":141.67612,"mean_force":90.40036,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48972,0.02601,0.03413]},{"body_a":"peg","body_b":"channel_base_body","contact_count":711.0,"contact_point_centroid":[0.51073,0.01158,0.00943],"force_p95":95.077,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":106.36841,"mean_force":57.22633,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48974,0.03365,0.03426]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":19.0,"contact_point_centroid":[0.47499,-0.01414,0.03726],"force_p95":67.29058,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":67.85075,"mean_force":43.72981,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48624,-0.01414,0.03309]},{"body_a":"peg","body_b":"link7","contact_count":471.0,"contact_point_centroid":[0.51943,0.01704,0.06756],"force_p95":45.91074,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.11659,"mean_force":29.28243,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48994,0.03821,0.03437]},{"body_a":"peg","body_b":"channel_base_body","contact_count":278.0,"contact_point_centroid":[0.50535,0.10451,0.00936],"force_p95":0.60957,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.58705,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5122,0.16957,0.22277]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50049,0.1979,0.29482]},{"body_a":"peg","body_b":"channel_base_body","contact_count":88.0,"contact_point_centroid":[0.50639,0.10499,0.00939],"force_p95":0.57445,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57941,"mean_force":0.54619,"phase_index":1.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.52013,0.14938,0.1526]},{"body_a":"peg","body_b":"channel_base_body","contact_count":565.0,"contact_point_centroid":[0.50575,0.10465,0.00939],"force_p95":0.57565,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57865,"mean_force":0.54631,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5036,0.14703,0.0944]}],"total_contact_groups":11},"final_pose_error":0.01969,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.52393,-0.06694,0.0299],"final_tcp_position":[0.49377,-0.06274,0.03422],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":205.01606,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":305.0,"n_steps_budget":1000.0,"object_pos_end":[0.50583,0.10468,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18487,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54917,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":310.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach_pre_contact","tcp_end":[0.52423,0.14277,0.15636],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12963,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":88.0,"n_steps_budget":600.0,"object_pos_end":[0.50588,0.10457,0.03383],"object_pos_start":[0.50583,0.10468,0.03383],"object_to_goal_dist_end":0.18477,"object_to_goal_dist_start":0.18487,"object_z_max":0.03384,"peak_contact_force":0.55405,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":88.0,"raw_peak_contact_force":0.57941,"subtask_id":"approach_pre_contact","tcp_end":[0.51659,0.15851,0.15136],"tcp_start":[0.52423,0.14277,0.15636],"tcp_to_object_dist_end":0.12976,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":565.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.10472,0.03383],"object_pos_start":[0.50588,0.10457,0.03383],"object_to_goal_dist_end":0.18492,"object_to_goal_dist_start":0.18477,"object_z_max":0.03384,"peak_contact_force":0.52971,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":565.0,"raw_peak_contact_force":0.57865,"subtask_id":"approach_pre_contact","tcp_end":[0.4925,0.13542,0.03818],"tcp_start":[0.51659,0.15851,0.15136],"tcp_to_object_dist_end":0.03379,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":813.0,"n_steps_budget":1000.0,"object_pos_end":[0.52393,-0.06694,0.0299],"object_pos_start":[0.50593,0.10472,0.03383],"object_to_goal_dist_end":0.02907,"object_to_goal_dist_start":0.18492,"object_z_max":0.03949,"peak_contact_force":32.84044,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2834.0,"raw_peak_contact_force":205.01606,"subtask_id":"push_insertion","tcp_end":[0.49377,-0.06274,0.03422],"tcp_start":[0.4925,0.13542,0.03818],"tcp_to_object_dist_end":0.03076,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```