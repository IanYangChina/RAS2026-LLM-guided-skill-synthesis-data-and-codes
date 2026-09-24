## Search State

- **Seed**: 8
- **Iteration**: 13 / 15

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

## Current Skill (Q=0.203) — your mutation base

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

- **Composite score**: 0.203
- **task_score** (E): 0.339
- **fitness_score**: 0.583  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1572 |
| descend_1 | 0.00 | 1.00 | 0.1370 |
| push_1 | 0.00 | 1.00 | 0.0571 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.518, 0.128, 0.170) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.544 | 3.526 |
| descend_1 | descend | 0.00 / step_budget | (0.518, 0.128, 0.170)→(0.500, 0.110, 0.038) | (0.503, 0.080, 0.034)→(0.503, 0.079, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.417 | 1.979 |
| push_1 | push | 0.00 / step_budget | (0.500, 0.110, 0.038)→(0.519, 0.082, 0.075) | (0.503, 0.079, 0.034)→(0.499, -0.048, 0.024) | 0.160→0.037 | 1.00 / 2.000 | 292.017 | 1349.054 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.836
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.624
- phase_score: 0.725
- phase_breakdown.approach_peg_score: 0.872
- phase_breakdown.push_to_goal_score: 0.662

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.685
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.624
- **Median Q (composite search score)**: 0.171
- **K-run variance**: 0.0054
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.268


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.8565,"average_solve_count":223.0,"average_success_count":223.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_arc_height":0.08317,"approach_1.approach_speed":0.06295,"descend_1.descend_force_threshold":3.31118,"descend_1.descend_speed":0.02093,"push_1.push_distance":0.18033,"push_1.push_speed":0.00979,"push_1.push_tolerance":0.0323},"optimized_scores":{"best_composite_score":0.30464,"best_fitness_score":0.68464,"best_task_score":0.62371},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.54216,0.11967,0.05897],"force_p95":1271.27785,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1275.70685,"mean_force":829.92691,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5168,0.13214,0.01766]},{"body_a":"attachment","body_b":"world","contact_count":28.0,"contact_point_centroid":[0.51694,0.15236,-0.00126],"force_p95":794.25095,"geom_a":"pusher_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":826.79449,"mean_force":364.12226,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51559,0.14364,0.00545]},{"body_a":"world","body_b":"link7","contact_count":892.0,"contact_point_centroid":[0.49924,0.17927,-5e-05],"force_p95":300.80277,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":562.01648,"mean_force":265.62619,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50127,0.11799,0.04923]},{"body_a":"peg","body_b":"channel_base_body","contact_count":945.0,"contact_point_centroid":[0.49562,-0.01231,0.00817],"force_p95":0.80456,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.39667,"mean_force":0.77921,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50168,0.11891,0.04792]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.49592,0.13565,0.03768],"force_p95":38.84199,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.70294,"mean_force":22.55949,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49518,0.14744,0.03384]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47498,0.00875,0.0244],"force_p95":8.9226,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.87918,"mean_force":3.4507,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50082,0.1232,0.05071]},{"body_a":"peg","body_b":"channel_base_body","contact_count":333.0,"contact_point_centroid":[0.49636,0.11918,0.00942],"force_p95":0.64455,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56179,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49104,0.22545,0.22299]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.52548,0.06231,0.04665],"force_p95":1.78674,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.14729,"mean_force":0.78701,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52077,0.13587,0.01709]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4997,0.20214,0.29806]},{"body_a":"peg","body_b":"channel_base_body","contact_count":839.0,"contact_point_centroid":[0.49601,0.11912,0.00946],"force_p95":0.59691,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64118,"mean_force":0.53931,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48663,0.16886,0.09566]}],"total_contact_groups":10},"final_pose_error":0.15832,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49701,-0.01473,0.02413],"final_tcp_position":[0.49844,0.09682,0.05161],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":1275.70685,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":358.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11941,0.03408],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19954,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.53248,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":357.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach_peg","tcp_end":[0.48411,0.18857,0.16019],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14432,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":839.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11906,0.03385],"object_pos_start":[0.49602,0.11941,0.03408],"object_to_goal_dist_end":0.19919,"object_to_goal_dist_start":0.19954,"object_z_max":0.03414,"peak_contact_force":0.54295,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":839.0,"raw_peak_contact_force":0.64118,"subtask_id":"approach_peg","tcp_end":[0.49157,0.1504,0.03603],"tcp_start":[0.48411,0.18857,0.16019],"tcp_to_object_dist_end":0.03173,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49701,-0.01473,0.02413],"object_pos_start":[0.49602,0.11906,0.03385],"object_to_goal_dist_end":0.06724,"object_to_goal_dist_start":0.19919,"object_z_max":0.04144,"peak_contact_force":275.26668,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1924.0,"raw_peak_contact_force":1275.70685,"subtask_id":"push_to_goal","tcp_end":[0.49844,0.09682,0.05161],"tcp_start":[0.49157,0.1504,0.03603],"tcp_to_object_dist_end":0.11489,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.92308,"average_solve_count":221.0,"average_success_count":221.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_arc_height":0.08299,"approach_1.approach_speed":0.08458,"descend_1.descend_force_threshold":5.28743,"descend_1.descend_speed":0.0209,"push_1.push_distance":0.19799,"push_1.push_speed":0.01066,"push_1.push_tolerance":0.02649},"optimized_scores":{"best_composite_score":0.17134,"best_fitness_score":0.55134,"best_task_score":0.22783},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":25.0,"contact_point_centroid":[0.52712,0.0823,0.05957],"force_p95":1307.916,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1353.5165,"mean_force":681.8696,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51158,0.07672,0.03437]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":946.0,"contact_point_centroid":[0.52534,0.11986,0.05994],"force_p95":390.29055,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1236.64379,"mean_force":333.99865,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52479,0.07343,0.08556]},{"body_a":"peg","body_b":"channel_base_body","contact_count":934.0,"contact_point_centroid":[0.49746,-0.05958,0.00826],"force_p95":0.7094,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.15007,"mean_force":0.76268,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52503,0.07357,0.08598]},{"body_a":"attachment","body_b":"peg","contact_count":15.0,"contact_point_centroid":[0.51249,0.07363,0.05305],"force_p95":37.73668,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.02911,"mean_force":8.67482,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51183,0.08288,0.03351]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47482,-0.03922,0.04313],"force_p95":8.84581,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.04076,"mean_force":1.42061,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51232,0.07101,0.06574]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.52576,-0.01015,0.05845],"force_p95":1.58208,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.56172,"mean_force":0.56573,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51429,0.07328,0.05697]},{"body_a":"peg","body_b":"channel_base_body","contact_count":690.0,"contact_point_centroid":[0.50603,0.06231,0.00938],"force_p95":0.55747,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.54206,"mean_force":0.56852,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51674,0.09537,0.10432]},{"body_a":"attachment","body_b":"peg","contact_count":17.0,"contact_point_centroid":[0.50645,0.08087,0.05603],"force_p95":3.77845,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.24745,"mean_force":1.11643,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5049,0.0929,0.0437]},{"body_a":"peg","body_b":"channel_base_body","contact_count":445.0,"contact_point_centroid":[0.50562,0.06296,0.00935],"force_p95":0.58022,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.57696,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52635,0.11746,0.26488]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50086,0.19482,0.30115]}],"total_contact_groups":10},"final_pose_error":0.2134,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49973,-0.06356,0.02413],"final_tcp_position":[0.5288,0.07534,0.08626],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":1353.5165,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":473.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.06304,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1433,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.5432,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":479.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach_peg","tcp_end":[0.5319,0.09835,0.17294],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14587,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":690.0,"n_steps_budget":1000.0,"object_pos_end":[0.50625,0.06275,0.03414],"object_pos_start":[0.50598,0.06304,0.0338],"object_to_goal_dist_end":0.143,"object_to_goal_dist_start":0.1433,"object_z_max":0.03423,"peak_contact_force":0.02537,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":707.0,"raw_peak_contact_force":4.54206,"subtask_id":"approach_peg","tcp_end":[0.50383,0.0927,0.03816],"tcp_start":[0.5319,0.09835,0.17294],"tcp_to_object_dist_end":0.03032,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49973,-0.06356,0.02413],"object_pos_start":[0.50625,0.06275,0.03414],"object_to_goal_dist_end":0.02285,"object_to_goal_dist_start":0.143,"object_z_max":0.05339,"peak_contact_force":300.18145,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1985.0,"raw_peak_contact_force":1353.5165,"subtask_id":"push_to_goal","tcp_end":[0.5288,0.07534,0.08626],"tcp_start":[0.50383,0.0927,0.03816],"tcp_to_object_dist_end":0.15492,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.96618,"average_solve_count":207.0,"average_success_count":207.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_arc_height":0.06581,"approach_1.approach_speed":0.11071,"descend_1.descend_force_threshold":4.13408,"descend_1.descend_speed":0.02586,"push_1.push_distance":0.20268,"push_1.push_speed":0.00982,"push_1.push_tolerance":0.03674},"optimized_scores":{"best_composite_score":0.13389,"best_fitness_score":0.51389,"best_task_score":0.16581},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":18.0,"contact_point_centroid":[0.5259,0.07799,0.05983],"force_p95":1306.6291,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1417.93894,"mean_force":733.12028,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50957,0.07416,0.03366]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":948.0,"contact_point_centroid":[0.52545,0.1198,0.05994],"force_p95":401.93364,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":701.46866,"mean_force":336.5234,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5262,0.07082,0.08748]},{"body_a":"peg","body_b":"channel_base_body","contact_count":953.0,"contact_point_centroid":[0.49824,-0.05775,0.00834],"force_p95":0.81193,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.66018,"mean_force":0.81314,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52607,0.07085,0.08727]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.5098,0.06991,0.05311],"force_p95":42.45048,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.21317,"mean_force":10.57861,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50902,0.08038,0.03484]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47499,-0.08653,0.02417],"force_p95":8.29785,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.11403,"mean_force":3.7409,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52423,0.07003,0.09184]},{"body_a":"peg","body_b":"channel_base_body","contact_count":376.0,"contact_point_centroid":[0.50574,0.05661,0.00934],"force_p95":0.60234,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.5887,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52779,0.12433,0.2602]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50147,0.19402,0.30012]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52536,-0.00103,0.04685],"force_p95":1.33489,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.87311,"mean_force":0.50738,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51306,0.07054,0.05369]},{"body_a":"peg","body_b":"channel_base_body","contact_count":698.0,"contact_point_centroid":[0.50608,0.05658,0.00938],"force_p95":0.55729,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.75354,"mean_force":0.54703,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51982,0.09188,0.10632]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50679,0.07462,0.05813],"force_p95":0.45155,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.47956,"mean_force":0.28064,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50445,0.0867,0.03895]}],"total_contact_groups":10},"final_pose_error":0.22219,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50102,-0.06507,0.02414],"final_tcp_position":[0.53046,0.07285,0.08851],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":1417.93894,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":405.0,"n_steps_budget":990.0,"object_pos_end":[0.50612,0.05663,0.0338],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.55715,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":413.0,"raw_peak_contact_force":4.44541,"subtask_id":"approach_peg","tcp_end":[0.53756,0.09735,0.17717],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15233,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":698.0,"n_steps_budget":1000.0,"object_pos_end":[0.50619,0.05654,0.03377],"object_pos_start":[0.50612,0.05663,0.0338],"object_to_goal_dist_end":0.13682,"object_to_goal_dist_start":0.13691,"object_z_max":0.03383,"peak_contact_force":0.68128,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":701.0,"raw_peak_contact_force":0.75354,"subtask_id":"approach_peg","tcp_end":[0.50431,0.08666,0.03839],"tcp_start":[0.53756,0.09735,0.17717],"tcp_to_object_dist_end":0.03053,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50102,-0.06507,0.02414],"object_pos_start":[0.50619,0.05654,0.03377],"object_to_goal_dist_end":0.02181,"object_to_goal_dist_start":0.13682,"object_z_max":0.04375,"peak_contact_force":300.60199,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1990.0,"raw_peak_contact_force":1417.93894,"subtask_id":"push_to_goal","tcp_end":[0.53046,0.07285,0.08851],"tcp_start":[0.50431,0.08666,0.03839],"tcp_to_object_dist_end":0.15502,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```