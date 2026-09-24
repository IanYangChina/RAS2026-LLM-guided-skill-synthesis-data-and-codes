## Search State

- **Seed**: 7
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.2119 | 0.23 | ✅ accepted |

**Proposal policy**: task_score is 0.23 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.212) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: align_standoff
  anchor: object
  offset:
  - 0.0
  - 0.025
  - 0.05
  weight: 0.3
- id: push_goal
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
    entity: peg
    offset:
    - 0.0
    - 0.025
    - 0.05
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: align_standoff
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
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
      default: 3.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: align_standoff
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
    tolerance: 0.01
    orientation:
      mode: keep_current
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
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: push_goal
- id: retract_1
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
    - 0.05
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

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.025, 0.05], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.025, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=reduce_speed
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.212
- **task_score** (E): 0.233
- **fitness_score**: 0.322  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.67 | 1.00 | 0.1860 |
| contact_1 | 1.00 | 1.00 | 0.0724 |
| push_1 | 0.00 | 1.00 | 0.0001 |
| retract_1 | 0.33 | 1.00 | 0.1235 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.67 / step_budget | (0.500, 0.200, 0.300)→(0.502, 0.139, 0.126) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.533 | 2.732 |
| contact_1 | contact | 1.00 / force_exceeded | (0.502, 0.139, 0.126)→(0.497, 0.126, 0.055) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 | 1.00 / 2.000 | 12.741 | 12.741 |
| push_1 | push | 0.00 / guard_failure | (0.496, 0.075, 0.053)→(0.496, 0.075, 0.053) | (0.502, 0.098, 0.034)→(0.502, 0.048, 0.035) | 0.178→0.132 | 1.00 / 2.333 | 36.880 | 43.866 |
| retract_1 | retract | 0.33 / step_budget | (0.496, 0.075, 0.053)→(0.495, -0.040, 0.078) | (0.502, 0.048, 0.034)→(0.500, 0.027, 0.035) | 0.132→0.109 | 1.00 / 1.000 | 0.489 | 57.645 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.882
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.337
- phase_score: 0.791
- phase_breakdown.push_goal_score: 0.976
- phase_breakdown.align_standoff_score: 0.360

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.610
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.337
- **Median Q (composite search score)**: 0.069
- **K-run variance**: 0.0414
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.310


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.75,"average_solve_count":240.0,"average_success_count":240.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.01438,"contact_1.contact_force":8.77463,"contact_1.speed":0.02118,"push_1.push_distance":0.13501,"push_1.push_speed":0.04008,"retract_1.retract_speed":0.05552},"optimized_scores":{"best_composite_score":0.06863,"best_fitness_score":0.17863,"best_task_score":0.18558},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":22.0,"contact_point_centroid":[0.49849,0.10472,0.00942],"force_p95":42.10491,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.43496,"mean_force":31.83436,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50011,0.13807,0.05923]},{"body_a":"attachment","body_b":"peg","contact_count":22.0,"contact_point_centroid":[0.50728,0.12857,0.05855],"force_p95":41.74263,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.80311,"mean_force":31.43437,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50011,0.13807,0.05923]},{"body_a":"peg","body_b":"channel_base_body","contact_count":997.0,"contact_point_centroid":[0.50249,0.07306,0.00964],"force_p95":35.42294,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.26218,"mean_force":10.00514,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49704,0.05463,0.06703]},{"body_a":"attachment","body_b":"peg","contact_count":538.0,"contact_point_centroid":[0.50666,0.0955,0.0613],"force_p95":36.74824,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.83154,"mean_force":17.64384,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49762,0.09273,0.06237]},{"body_a":"peg","body_b":"channel_base_body","contact_count":343.0,"contact_point_centroid":[0.50367,0.11169,0.0094],"force_p95":0.58922,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.04852,"mean_force":0.58953,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50169,0.14236,0.08882]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.5074,0.12934,0.05892],"force_p95":15.60607,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.60607,"mean_force":15.60607,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50055,0.13913,0.05997]},{"body_a":"peg","body_b":"channel_base_body","contact_count":978.0,"contact_point_centroid":[0.50357,0.1117,0.00938],"force_p95":0.61271,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.5527,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50164,0.17194,0.2054]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49967,0.19945,0.29936]}],"total_contact_groups":8},"final_pose_error":0.05556,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50103,0.07556,0.03473],"final_tcp_position":[0.49638,-0.02595,0.07764],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":48.43496,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.11174,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.50216,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":994.0,"raw_peak_contact_force":2.06328,"subtask_id":"align_standoff","tcp_end":[0.50509,0.14601,0.11889],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09174,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":343.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.11172,0.03392],"object_pos_start":[0.50375,0.11174,0.0338],"object_to_goal_dist_end":0.19186,"object_to_goal_dist_start":0.19188,"object_z_max":0.03392,"peak_contact_force":16.04852,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":344.0,"raw_peak_contact_force":16.04852,"subtask_id":"align_standoff","tcp_end":[0.50056,0.13912,0.05982],"tcp_start":[0.50509,0.14601,0.11889],"tcp_to_object_dist_end":0.03783,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":22.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.11026,0.03397],"object_pos_start":[0.50373,0.11172,0.03392],"object_to_goal_dist_end":0.19038,"object_to_goal_dist_start":0.19186,"object_z_max":0.03398,"peak_contact_force":48.43496,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":44.0,"raw_peak_contact_force":48.43496,"subtask_id":"push_goal","tcp_end":[0.49983,0.13654,0.05888],"tcp_start":[0.49984,0.13663,0.05891],"tcp_to_object_dist_end":0.03636,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50103,0.07556,0.03473],"object_pos_start":[0.50312,0.11007,0.0339],"object_to_goal_dist_end":0.15565,"object_to_goal_dist_start":0.19019,"object_z_max":0.04058,"peak_contact_force":0.53745,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1535.0,"raw_peak_contact_force":43.26218,"tcp_end":[0.49638,-0.02595,0.07764],"tcp_start":[0.49983,0.13654,0.05888],"tcp_to_object_dist_end":0.11031,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.7004,"average_solve_count":247.0,"average_success_count":247.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.03829,"contact_1.contact_force":5.7708,"contact_1.speed":0.01729,"push_1.push_distance":0.15022,"push_1.push_speed":0.03295,"retract_1.retract_speed":0.05222},"optimized_scores":{"best_composite_score":0.06759,"best_fitness_score":0.17759,"best_task_score":0.17703},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":27.0,"contact_point_centroid":[0.48661,0.11012,0.00948],"force_p95":40.16243,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.09375,"mean_force":33.51546,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48716,0.14402,0.05952]},{"body_a":"attachment","body_b":"peg","contact_count":27.0,"contact_point_centroid":[0.49591,0.13598,0.05867],"force_p95":39.63877,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.72057,"mean_force":33.10908,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48716,0.14402,0.05952]},{"body_a":"peg","body_b":"channel_base_body","contact_count":997.0,"contact_point_centroid":[0.49624,0.08152,0.00961],"force_p95":33.44867,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.75534,"mean_force":9.76323,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4889,0.06026,0.06698]},{"body_a":"attachment","body_b":"peg","contact_count":526.0,"contact_point_centroid":[0.49641,0.10278,0.06133],"force_p95":35.55354,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.23873,"mean_force":17.57762,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48723,0.09911,0.06241]},{"body_a":"peg","body_b":"channel_base_body","contact_count":352.0,"contact_point_centroid":[0.496,0.11918,0.00944],"force_p95":0.59854,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.71981,"mean_force":0.57517,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48477,0.14687,0.0828]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49605,0.13694,0.05899],"force_p95":12.27137,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.27137,"mean_force":12.27137,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48757,0.14533,0.06021]},{"body_a":"peg","body_b":"channel_base_body","contact_count":975.0,"contact_point_centroid":[0.49616,0.11917,0.00944],"force_p95":0.61088,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.54781,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49109,0.17352,0.19999]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49947,0.1993,0.29858]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":11.0,"contact_point_centroid":[0.47486,0.08224,0.05904],"force_p95":0.282,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3317,"mean_force":0.09706,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49011,0.02733,0.07061]}],"total_contact_groups":9},"final_pose_error":0.06227,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49479,0.08501,0.03388],"final_tcp_position":[0.49289,-0.0195,0.07709],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":43.09375,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49606,0.1194,0.03391],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19953,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.54967,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":999.0,"raw_peak_contact_force":2.24822,"subtask_id":"align_standoff","tcp_end":[0.48441,0.1491,0.1082],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08086,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":352.0,"n_steps_budget":1000.0,"object_pos_end":[0.49606,0.11897,0.03403],"object_pos_start":[0.49606,0.1194,0.03391],"object_to_goal_dist_end":0.1991,"object_to_goal_dist_start":0.19953,"object_z_max":0.03404,"peak_contact_force":12.71981,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":353.0,"raw_peak_contact_force":12.71981,"subtask_id":"align_standoff","tcp_end":[0.48759,0.14532,0.06009],"tcp_start":[0.48441,0.1491,0.1082],"tcp_to_object_dist_end":0.03802,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":27.0,"n_steps_budget":1000.0,"object_pos_end":[0.49524,0.11693,0.03413],"object_pos_start":[0.49606,0.11897,0.03403],"object_to_goal_dist_end":0.19708,"object_to_goal_dist_start":0.1991,"object_z_max":0.03415,"peak_contact_force":40.53861,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":54.0,"raw_peak_contact_force":43.09375,"subtask_id":"push_goal","tcp_end":[0.48694,0.14209,0.0592],"tcp_start":[0.48695,0.14217,0.05924],"tcp_to_object_dist_end":0.03648,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49479,0.08501,0.03388],"object_pos_start":[0.49528,0.11676,0.03404],"object_to_goal_dist_end":0.16521,"object_to_goal_dist_start":0.1969,"object_z_max":0.04063,"peak_contact_force":0.54224,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1534.0,"raw_peak_contact_force":41.75534,"tcp_end":[0.49289,-0.0195,0.07709],"tcp_start":[0.48694,0.14209,0.0592],"tcp_to_object_dist_end":0.11311,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.68519,"average_solve_count":324.0,"average_success_count":324.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.02461,"contact_1.contact_force":5.53758,"contact_1.speed":0.01721,"push_1.push_distance":0.18095,"push_1.push_speed":0.01817,"retract_1.retract_speed":0.0742},"optimized_scores":{"best_composite_score":0.49959,"best_fitness_score":0.60959,"best_task_score":0.33681},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":432.0,"contact_point_centroid":[0.49987,-0.0693,0.05956],"force_p95":85.60519,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":87.91763,"mean_force":54.87554,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49473,-0.0595,0.05658]},{"body_a":"peg","body_b":"channel_base_body","contact_count":447.0,"contact_point_centroid":[0.50751,-0.10111,0.061],"force_p95":73.03244,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.72891,"mean_force":49.55407,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49472,-0.0598,0.05722]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":329.0,"contact_point_centroid":[0.52542,-0.08456,0.05943],"force_p95":45.28699,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":52.44212,"mean_force":23.86248,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49403,-0.06087,0.06043]},{"body_a":"attachment","body_b":"peg","contact_count":761.0,"contact_point_centroid":[0.50315,0.00093,0.04449],"force_p95":16.09892,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.06792,"mean_force":4.87948,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50014,0.01259,0.0418]},{"body_a":"peg","body_b":"channel_base_body","contact_count":43.0,"contact_point_centroid":[0.50697,-0.10047,0.06008],"force_p95":38.35451,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.65629,"mean_force":29.42203,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49991,-0.05393,0.04143]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":15.0,"contact_point_centroid":[0.47492,-0.08021,0.0301],"force_p95":16.16958,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.17301,"mean_force":6.54906,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49364,-0.06527,0.07317]},{"body_a":"peg","body_b":"channel_base_body","contact_count":471.0,"contact_point_centroid":[0.50684,-0.02792,0.00993],"force_p95":8.8964,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.20404,"mean_force":5.42624,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50023,0.01789,0.04191]},{"body_a":"peg","body_b":"channel_base_body","contact_count":609.0,"contact_point_centroid":[0.50591,0.06267,0.00938],"force_p95":0.55281,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.45496,"mean_force":0.57565,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50928,0.10726,0.09738]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.50558,0.08077,0.05718],"force_p95":8.56468,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.1998,"mean_force":3.17001,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50392,0.09277,0.04771]},{"body_a":"peg","body_b":"channel_base_body","contact_count":41.0,"contact_point_centroid":[0.50422,-0.07005,0.00932],"force_p95":4.70786,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.7183,"mean_force":1.17782,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49583,-0.06815,0.06959]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":514.0,"contact_point_centroid":[0.52504,-0.01682,0.02306],"force_p95":2.94627,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.81648,"mean_force":1.00778,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50008,0.01148,0.04173]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.50586,0.06296,0.00937],"force_p95":0.55508,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56049,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50796,0.15912,0.2203]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49958,0.1988,0.29774]}],"total_contact_groups":13},"final_pose_error":0.01156,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50537,-0.07816,0.03503],"final_tcp_position":[0.4957,-0.07478,0.08062],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":87.91763,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06297,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54709,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1006.0,"raw_peak_contact_force":3.88411,"subtask_id":"align_standoff","tcp_end":[0.51718,0.12215,0.15055],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13137,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":609.0,"n_steps_budget":1000.0,"object_pos_end":[0.506,0.06259,0.03417],"object_pos_start":[0.50593,0.06297,0.0338],"object_to_goal_dist_end":0.14284,"object_to_goal_dist_start":0.14323,"object_z_max":0.03409,"peak_contact_force":9.45496,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":615.0,"raw_peak_contact_force":9.45496,"subtask_id":"align_standoff","tcp_end":[0.50377,0.09234,0.04622],"tcp_start":[0.51718,0.12215,0.15055],"tcp_to_object_dist_end":0.03218,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":927.0,"n_steps_budget":1000.0,"object_pos_end":[0.50693,-0.08287,0.03545],"object_pos_start":[0.506,0.06259,0.03417],"object_to_goal_dist_end":0.00877,"object_to_goal_dist_start":0.14284,"object_z_max":0.0361,"peak_contact_force":21.66723,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1789.0,"raw_peak_contact_force":40.06792,"subtask_id":"push_goal","tcp_end":[0.49977,-0.0549,0.04118],"tcp_start":[0.49981,-0.05492,0.04123],"tcp_to_object_dist_end":0.02943,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.50537,-0.07816,0.03503],"object_pos_start":[0.50695,-0.08295,0.0354],"object_to_goal_dist_end":0.00754,"object_to_goal_dist_start":0.00884,"object_z_max":0.04608,"peak_contact_force":0.3869,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1264.0,"raw_peak_contact_force":87.91763,"tcp_end":[0.4957,-0.07478,0.08062],"tcp_start":[0.49977,-0.0549,0.04118],"tcp_to_object_dist_end":0.04673,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```