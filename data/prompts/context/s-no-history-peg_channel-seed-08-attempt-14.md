## Search State

- **Seed**: 8
- **Iteration**: 15 / 15

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
- Frozen realised-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`
- Frozen object start: [0.48615778212844485, 0.11898214746703403, 0.04]
- Frozen task target: [0.48615778212844485, -0.04101785253296597, 0.04]
- Goal object position: (0.48615778212844485, -0.04101785253296597, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48615778212844485, 0.11898214746703403, 0.04)
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
  frozen_object_start: [0.4862, 0.119, 0.04]
  frozen_task_target: [0.4862, -0.041, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48615778212844485, 0.11898214746703403, 0.04]}
  frozen_targets: {'channel_exit': [0.48615778212844485, -0.04101785253296597, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e

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
| `object` | offset from object initial position (0.48615778212844485, 0.11898214746703403, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.48615778212844485, -0.04101785253296597, 0.04) | final destination targets |
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

## Current Skill (Q=-0.394) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach_peg
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.0
  weight: 0.3
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.05
    - 0.12
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_arc_height:
      type: scalar
      range:
      - 0.04
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.arc_height
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_peg
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
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
      mode: keep_current
  parameters:
    descend_force_threshold:
      type: scalar
      range:
      - 3.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_peg
- id: push_1
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
    - 0.0
    - 0.026
    offset_along_axis:
      distance: 0.18
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.03
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.16
      - 0.22
      default: 0.18
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.005
      - 0.015
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.02
      - 0.05
      default: 0.03
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.12], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_arc_height: status=consumed; consumers=generator.arc_height (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.026], offset_along_axis={axis=channel_axis, distance=0.18, mode=add_to_offset, sign=positive}, tolerance=0.03
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]

## Design Metrics

- **Composite score**: -0.394
- **task_score** (E): 0.020
- **fitness_score**: 0.036  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1608 |
| descend_1 | 1.00 | 1.00 | 0.1303 |
| push_1 | 0.00 | 1.00 | 0.0021 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.515, 0.197, 0.144) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.530 | 3.526 |
| descend_1 | descend | 1.00 / step_budget | (0.515, 0.197, 0.144)→(0.501, 0.111, 0.047) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.564 | 0.603 |
| push_1 | push | 0.00 / guard_failure | (0.508, 0.103, 0.042)→(0.509, 0.101, 0.041) | (0.503, 0.080, 0.034)→(0.503, 0.076, 0.035) | 0.160→0.156 | 1.00 / 2.000 | 540.042 | 1095.891 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.067
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.025
- phase_score: 0.055
- phase_breakdown.push_to_goal_score: 0.037
- phase_breakdown.reach_entrance_score: 0.095

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.043
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.025
- **Median Q (composite search score)**: -0.394
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.269


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a8ce855c7f52ba2d198de8387bdd2f3b869655c206850d620daaec6ac6f298cd`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `79b30dd7102e96fb2fa0880d3932c959e04a6f943c7e87b878f77a0e54f87a94`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.9125,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_arc_height":0.04316,"approach_1.approach_speed":0.10549,"descend_1.descend_speed":0.0131,"descend_1.descend_tolerance":0.02561,"push_1.guard_force_threshold":23.60898,"push_1.push_distance":0.20241,"push_1.push_speed":0.00916,"push_1.push_tolerance":0.03563},"optimized_scores":{"best_composite_score":-0.39424,"best_fitness_score":0.03576,"best_task_score":0.02533},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.49618,0.134,0.05036],"force_p95":240.62052,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":248.18075,"mean_force":130.61791,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49517,0.14577,0.04555]},{"body_a":"peg","body_b":"channel_base_body","contact_count":8.0,"contact_point_centroid":[0.49434,0.10641,0.0092],"force_p95":234.10923,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":247.15163,"mean_force":81.4529,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49428,0.14653,0.04608]},{"body_a":"peg","body_b":"channel_base_body","contact_count":291.0,"contact_point_centroid":[0.49637,0.11913,0.00939],"force_p95":0.64564,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56807,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49261,0.23664,0.22876]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49976,0.20228,0.29771]},{"body_a":"peg","body_b":"channel_base_body","contact_count":364.0,"contact_point_centroid":[0.49608,0.1191,0.00944],"force_p95":0.61498,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64541,"mean_force":0.54015,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48726,0.19147,0.10153]}],"total_contact_groups":5},"final_pose_error":0.2246,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49818,0.11322,0.03573],"final_tcp_position":[0.50176,0.14111,0.04248],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":248.18075,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":316.0,"n_steps_budget":960.0,"object_pos_end":[0.49604,0.11912,0.03385],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19925,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.5406,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":315.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_entrance","tcp_end":[0.48552,0.23164,0.1551],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16575,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":364.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11915,0.03412],"object_pos_start":[0.49604,0.11912,0.03385],"object_to_goal_dist_end":0.19927,"object_to_goal_dist_start":0.19925,"object_z_max":0.03413,"peak_contact_force":0.59468,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":364.0,"raw_peak_contact_force":0.64541,"subtask_id":"reach_entrance","tcp_end":[0.4913,0.14946,0.04829],"tcp_start":[0.48552,0.23164,0.1551],"tcp_to_object_dist_end":0.03379,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":8.0,"n_steps_budget":1000.0,"object_pos_end":[0.49638,0.11554,0.03497],"object_pos_start":[0.49602,0.11915,0.03412],"object_to_goal_dist_end":0.19564,"object_to_goal_dist_start":0.19927,"object_z_max":0.03529,"peak_contact_force":248.18075,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":13.0,"raw_peak_contact_force":248.18075,"subtask_id":"push_to_goal","tcp_end":[0.50176,0.14111,0.04248],"tcp_start":[0.49932,0.14247,0.0433],"tcp_to_object_dist_end":0.02719,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0a7722137b05abd45e72adac5a0a8f18d70c24ddc36cf4c70c52ed7e5618005d`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.07595,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_arc_height":0.06782,"approach_1.approach_speed":0.12359,"descend_1.descend_speed":0.0222,"descend_1.descend_tolerance":0.01538,"push_1.guard_force_threshold":31.51764,"push_1.push_distance":0.20212,"push_1.push_speed":0.01021,"push_1.push_tolerance":0.04373},"optimized_scores":{"best_composite_score":-0.38726,"best_fitness_score":0.04274,"best_task_score":0.02499},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.526,0.08672,0.05985],"force_p95":1587.8539,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1599.21748,"mean_force":1485.58163,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51221,0.08592,0.04174]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50774,0.07898,0.04433],"force_p95":101.1037,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":109.00315,"mean_force":54.92416,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50857,0.0902,0.04397]},{"body_a":"peg","body_b":"channel_base_body","contact_count":9.0,"contact_point_centroid":[0.50791,0.04936,0.00922],"force_p95":67.12683,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":95.44305,"mean_force":16.83114,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50804,0.09104,0.04454]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52508,0.05891,0.03536],"force_p95":14.25952,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.85269,"mean_force":8.92104,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51136,0.08683,0.04222]},{"body_a":"peg","body_b":"channel_base_body","contact_count":357.0,"contact_point_centroid":[0.50556,0.06304,0.00934],"force_p95":0.59524,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.58446,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51373,0.22619,0.21045]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50052,0.20443,0.29585]},{"body_a":"peg","body_b":"channel_base_body","contact_count":341.0,"contact_point_centroid":[0.50604,0.06301,0.00938],"force_p95":0.55136,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55501,"mean_force":0.54657,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51469,0.14005,0.09336]}],"total_contact_groups":7},"final_pose_error":0.22294,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50479,0.05217,0.03691],"final_tcp_position":[0.51351,0.08356,0.04067],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":1599.21748,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":385.0,"n_steps_budget":870.0,"object_pos_end":[0.50603,0.06301,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14327,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54972,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":391.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_entrance","tcp_end":[0.52563,0.1823,0.14003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16093,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":341.0,"n_steps_budget":1000.0,"object_pos_end":[0.50603,0.06297,0.0338],"object_pos_start":[0.50603,0.06301,0.03381],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14327,"object_z_max":0.03381,"peak_contact_force":0.54555,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":341.0,"raw_peak_contact_force":0.55501,"subtask_id":"reach_entrance","tcp_end":[0.50501,0.09523,0.04705],"tcp_start":[0.52563,0.1823,0.14003],"tcp_to_object_dist_end":0.03488,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":9.0,"n_steps_budget":1000.0,"object_pos_end":[0.50579,0.05768,0.03472],"object_pos_start":[0.50603,0.06297,0.0338],"object_to_goal_dist_end":0.13791,"object_to_goal_dist_start":0.14323,"object_z_max":0.03576,"peak_contact_force":1371.94577,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":16.0,"raw_peak_contact_force":1599.21748,"subtask_id":"push_to_goal","tcp_end":[0.51351,0.08356,0.04067],"tcp_start":[0.51278,0.08508,0.04133],"tcp_to_object_dist_end":0.02765,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `bf9c239495ea25cc1b534d0795871edaef0fee72244885088104a44eb548c1a2`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,0.05661,0.04]},{"name":"goal","value":[0.53648,-0.10339,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53648,-0.10339,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13021,"average_solve_count":192.0,"average_success_count":192.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_arc_height":0.09105,"approach_1.approach_speed":0.05095,"descend_1.descend_speed":0.0246,"descend_1.descend_tolerance":0.02358,"push_1.guard_force_threshold":29.4918,"push_1.push_distance":0.19289,"push_1.push_speed":0.00972,"push_1.push_tolerance":0.03173},"optimized_scores":{"best_composite_score":-0.40072,"best_fitness_score":0.02928,"best_task_score":0.01077},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52556,0.08215,0.05992],"force_p95":1432.75942,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1440.27377,"mean_force":1365.13027,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51138,0.08157,0.04232]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50845,0.07171,0.04366],"force_p95":76.14066,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":82.99536,"mean_force":45.01928,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51013,0.08315,0.04314]},{"body_a":"peg","body_b":"channel_base_body","contact_count":8.0,"contact_point_centroid":[0.50734,0.05193,0.00943],"force_p95":66.56144,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.6181,"mean_force":21.89099,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50838,0.08557,0.04451]},{"body_a":"peg","body_b":"channel_base_body","contact_count":445.0,"contact_point_centroid":[0.50573,0.05661,0.00935],"force_p95":0.60291,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.58222,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51803,0.22943,0.20603]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50031,0.20435,0.29661]},{"body_a":"peg","body_b":"channel_base_body","contact_count":334.0,"contact_point_centroid":[0.50628,0.05662,0.00938],"force_p95":0.59828,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60958,"mean_force":0.54671,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51914,0.1337,0.09086]}],"total_contact_groups":6},"final_pose_error":0.21588,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50452,0.04998,0.03615],"final_tcp_position":[0.51241,0.07937,0.04129],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":1440.27377,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":474.0,"n_steps_budget":1000.0,"object_pos_end":[0.50615,0.05662,0.03376],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.50099,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":482.0,"raw_peak_contact_force":4.44541,"subtask_id":"reach_entrance","tcp_end":[0.5331,0.1756,0.13546],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15882,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":334.0,"n_steps_budget":1000.0,"object_pos_end":[0.50611,0.0566,0.03378],"object_pos_start":[0.50615,0.05662,0.03376],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.1369,"object_z_max":0.03378,"peak_contact_force":0.55231,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":334.0,"raw_peak_contact_force":0.60958,"subtask_id":"reach_entrance","tcp_end":[0.50614,0.08902,0.04657],"tcp_start":[0.5331,0.1756,0.13546],"tcp_to_object_dist_end":0.03485,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":8.0,"n_steps_budget":1000.0,"object_pos_end":[0.50571,0.05391,0.03457],"object_pos_start":[0.50611,0.0566,0.03378],"object_to_goal_dist_end":0.13415,"object_to_goal_dist_start":0.13688,"object_z_max":0.03533,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":14.0,"raw_peak_contact_force":1440.27377,"subtask_id":"push_to_goal","tcp_end":[0.51241,0.07937,0.04129],"tcp_start":[0.51186,0.08081,0.04195],"tcp_to_object_dist_end":0.02717,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```