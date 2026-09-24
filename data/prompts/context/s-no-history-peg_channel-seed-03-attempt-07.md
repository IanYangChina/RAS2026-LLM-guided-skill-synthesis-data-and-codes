## Search State

- **Seed**: 3
- **Iteration**: 8 / 15

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

## Current Skill (Q=0.348) — your mutation base

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
  weight: 0.3
- id: push_to_goal
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_peg
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
    - 0.03
    - 0.1
    tolerance: 0.03
    orientation:
      mode: keep_current
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
  subtask_id: approach_pre_contact
- id: align_to_entrance
  type: align
  generator: arc_cartesian
  control: impedance_control
  termination: pose_tolerance
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
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: generator.arc_height
        mode: replace
    lateral_x:
      type: scalar
      range:
      - -0.04
      - 0.04
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
  subtask_id: approach_pre_contact
- id: push_through_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: channel_exit
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 45.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.0
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.1], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **align_to_entrance** (`align`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - lateral_x: status=consumed; consumers=target.offset.x (replace)
- **push_through_channel** (`push`)
  - target: source=yaml, anchor=task_goal, entity=channel_exit, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=45.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.348
- **task_score** (E): 0.404
- **fitness_score**: 0.578  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1574 |
| align_to_entrance | 1.00 | 1.00 | 0.1330 |
| push_through_channel | 0.00 | 1.00 | 0.0002 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.127, 0.164) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.548 | 3.954 |
| align_to_entrance | align | 1.00 / step_budget | (0.505, 0.127, 0.164)→(0.497, 0.121, 0.033) | (0.502, 0.081, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.162 | 1.00 / 1.000 | 0.546 | 0.561 |
| push_through_channel | push | 0.00 / guard_failure | (0.496, -0.055, 0.034)→(0.496, -0.055, 0.034) | (0.502, 0.081, 0.034)→(0.503, -0.082, 0.037) | 0.162→0.009 | 1.00 / 3.000 | 6.515 | 49.471 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.567
- phase_score: 0.699
- phase_breakdown.push_to_goal_score: 0.952
- phase_breakdown.approach_pre_contact_score: 0.108

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.646
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.567
- **Median Q (composite search score)**: 0.314
- **K-run variance**: 0.0023
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.196


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43182,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_entrance.arc_height":0.03936,"align_to_entrance.lateral_x":0.00824,"approach_peg.approach_height":0.0818,"push_through_channel.push_speed":0.05763},"optimized_scores":{"best_composite_score":0.31239,"best_fitness_score":0.54239,"best_task_score":0.32515},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":11.0,"contact_point_centroid":[0.49228,-0.1004,0.03644],"force_p95":43.98894,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.84446,"mean_force":20.29416,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49625,-0.05191,0.03451]},{"body_a":"attachment","body_b":"peg","contact_count":266.0,"contact_point_centroid":[0.49592,0.00491,0.03952],"force_p95":35.30585,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.54406,"mean_force":6.49322,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49545,0.01655,0.03234]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":110.0,"contact_point_centroid":[0.47457,-0.0336,0.04362],"force_p95":36.29049,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.18355,"mean_force":12.05281,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49586,-0.00452,0.03309]},{"body_a":"peg","body_b":"channel_base_body","contact_count":176.0,"contact_point_centroid":[0.49634,-0.0005,0.00962],"force_p95":6.33104,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.03278,"mean_force":2.14443,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49547,0.03763,0.03209]},{"body_a":"peg","body_b":"channel_base_body","contact_count":227.0,"contact_point_centroid":[0.49465,0.05911,0.00931],"force_p95":0.68694,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.61059,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48389,0.14936,0.21548]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49852,0.19574,0.29281]},{"body_a":"peg","body_b":"channel_base_body","contact_count":511.0,"contact_point_centroid":[0.49407,0.05893,0.00939],"force_p95":0.55028,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55326,"mean_force":0.5462,"phase_index":1.0,"phase_name":"align_to_entrance","phase_type":"align","tcp_position_centroid":[0.48282,0.12238,0.08735]}],"total_contact_groups":7},"final_pose_error":0.02604,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49193,-0.08305,0.03687],"final_tcp_position":[0.49628,-0.05481,0.03455],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":45.84446,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":256.0,"n_steps_budget":1000.0,"object_pos_end":[0.49407,0.05889,0.03383],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13915,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.5504,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":262.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach_pre_contact","tcp_end":[0.47046,0.10605,0.14558],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12357,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":511.0,"n_steps_budget":750.0,"object_pos_end":[0.4941,0.05881,0.03389],"object_pos_start":[0.49407,0.05889,0.03383],"object_to_goal_dist_end":0.13907,"object_to_goal_dist_start":0.13915,"object_z_max":0.03389,"peak_contact_force":0.54601,"phase_name":"align_to_entrance","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":511.0,"raw_peak_contact_force":0.55326,"subtask_id":"approach_pre_contact","tcp_end":[0.4972,0.09735,0.03335],"tcp_start":[0.47046,0.10605,0.14558],"tcp_to_object_dist_end":0.03867,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":402.0,"n_steps_budget":1000.0,"object_pos_end":[0.49186,-0.08245,0.03709],"object_pos_start":[0.4941,0.05881,0.03389],"object_to_goal_dist_end":0.00899,"object_to_goal_dist_start":0.13907,"object_z_max":0.03878,"peak_contact_force":13.39701,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":563.0,"raw_peak_contact_force":45.84446,"subtask_id":"push_to_goal","tcp_end":[0.49628,-0.05481,0.03455],"tcp_start":[0.49632,-0.05465,0.0346],"tcp_to_object_dist_end":0.02811,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29189,"average_solve_count":185.0,"average_success_count":185.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_entrance.arc_height":0.0557,"align_to_entrance.lateral_x":-0.00146,"approach_peg.approach_height":0.11974,"push_through_channel.push_speed":0.02411},"optimized_scores":{"best_composite_score":0.3144,"best_fitness_score":0.5444,"best_task_score":0.32022},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":335.0,"contact_point_centroid":[0.50248,0.01916,0.04563],"force_p95":16.56832,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.1802,"mean_force":4.46902,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49726,0.03066,0.03158]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.50773,-0.10022,0.0609],"force_p95":42.2811,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.23431,"mean_force":29.13378,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49645,-0.05391,0.03435]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":301.0,"contact_point_centroid":[0.52518,-0.01028,0.03039],"force_p95":15.63256,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.32329,"mean_force":2.46966,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49711,0.018,0.03196]},{"body_a":"peg","body_b":"channel_base_body","contact_count":168.0,"contact_point_centroid":[0.50695,-0.00035,0.00978],"force_p95":16.01763,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.80112,"mean_force":5.62516,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49778,0.04268,0.03171]},{"body_a":"peg","body_b":"channel_base_body","contact_count":174.0,"contact_point_centroid":[0.50503,0.08095,0.00931],"force_p95":0.85861,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.63446,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51441,0.16045,0.23426]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50148,0.19576,0.29278]},{"body_a":"peg","body_b":"channel_base_body","contact_count":606.0,"contact_point_centroid":[0.50598,0.08087,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55104,"mean_force":0.54677,"phase_index":1.0,"phase_name":"align_to_entrance","phase_type":"align","tcp_position_centroid":[0.51307,0.15361,0.10634]}],"total_contact_groups":7},"final_pose_error":0.02644,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50767,-0.08235,0.03647],"final_tcp_position":[0.49636,-0.05444,0.03428],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":48.1802,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":203.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.55004,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":210.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach_pre_contact","tcp_end":[0.52671,0.12808,0.18238],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15728,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":606.0,"n_steps_budget":960.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.55006,"phase_name":"align_to_entrance","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":606.0,"raw_peak_contact_force":0.55104,"subtask_id":"approach_pre_contact","tcp_end":[0.50123,0.12008,0.03265],"tcp_start":[0.52671,0.12808,0.18238],"tcp_to_object_dist_end":0.03949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":465.0,"n_steps_budget":1000.0,"object_pos_end":[0.50765,-0.08183,0.0365],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.00861,"object_to_goal_dist_start":0.16112,"object_z_max":0.03716,"peak_contact_force":5.62326,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":808.0,"raw_peak_contact_force":48.1802,"subtask_id":"push_to_goal","tcp_end":[0.49636,-0.05444,0.03428],"tcp_start":[0.4964,-0.05429,0.03433],"tcp_to_object_dist_end":0.02971,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32716,"average_solve_count":162.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_entrance.arc_height":0.04585,"align_to_entrance.lateral_x":-0.01163,"approach_peg.approach_height":0.09623,"push_through_channel.push_speed":0.0471},"optimized_scores":{"best_composite_score":0.41621,"best_fitness_score":0.64621,"best_task_score":0.56716},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":363.0,"contact_point_centroid":[0.49894,0.02348,0.04122],"force_p95":24.41303,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.38704,"mean_force":6.02716,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4922,0.03399,0.03271]},{"body_a":"peg","body_b":"channel_base_body","contact_count":7.0,"contact_point_centroid":[0.50803,-0.10039,0.06037],"force_p95":49.81986,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.29988,"mean_force":32.34846,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49502,-0.05444,0.0344]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":369.0,"contact_point_centroid":[0.52519,0.01051,0.03111],"force_p95":17.67177,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.88525,"mean_force":3.70337,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49208,0.03633,0.03263]},{"body_a":"peg","body_b":"channel_base_body","contact_count":210.0,"contact_point_centroid":[0.50681,0.0201,0.00978],"force_p95":17.50714,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.8808,"mean_force":5.43343,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49162,0.06067,0.0326]},{"body_a":"peg","body_b":"channel_base_body","contact_count":183.0,"contact_point_centroid":[0.50529,0.10472,0.00934],"force_p95":0.72388,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.60811,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50948,0.17096,0.22449]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50083,0.1974,0.29334]},{"body_a":"peg","body_b":"channel_base_body","contact_count":500.0,"contact_point_centroid":[0.50576,0.10458,0.00939],"force_p95":0.57533,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57958,"mean_force":0.54634,"phase_index":1.0,"phase_name":"align_to_entrance","phase_type":"align","tcp_position_centroid":[0.50413,0.16874,0.09894]}],"total_contact_groups":7},"final_pose_error":0.02583,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50806,-0.08201,0.0367],"final_tcp_position":[0.49495,-0.05532,0.03428],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":54.38704,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":210.0,"n_steps_budget":1000.0,"object_pos_end":[0.50592,0.10457,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18477,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54457,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":215.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach_pre_contact","tcp_end":[0.51795,0.14662,0.16276],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13614,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":500.0,"n_steps_budget":840.0,"object_pos_end":[0.50589,0.10472,0.03384],"object_pos_start":[0.50592,0.10457,0.03384],"object_to_goal_dist_end":0.18491,"object_to_goal_dist_start":0.18477,"object_z_max":0.03384,"peak_contact_force":0.54276,"phase_name":"align_to_entrance","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":500.0,"raw_peak_contact_force":0.57958,"subtask_id":"approach_pre_contact","tcp_end":[0.4915,0.14407,0.03431],"tcp_start":[0.51795,0.14662,0.16276],"tcp_to_object_dist_end":0.0419,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":528.0,"n_steps_budget":1000.0,"object_pos_end":[0.5081,-0.08162,0.03673],"object_pos_start":[0.50589,0.10472,0.03384],"object_to_goal_dist_end":0.00888,"object_to_goal_dist_start":0.18491,"object_z_max":0.03765,"peak_contact_force":0.52451,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":949.0,"raw_peak_contact_force":54.38704,"subtask_id":"push_to_goal","tcp_end":[0.49495,-0.05532,0.03428],"tcp_start":[0.49501,-0.05521,0.03434],"tcp_to_object_dist_end":0.02951,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```