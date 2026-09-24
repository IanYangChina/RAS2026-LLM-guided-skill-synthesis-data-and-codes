## Search State

- **Seed**: 3
- **Iteration**: 4 / 15

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

## Current Skill (Q=0.431) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: align_at_entrance
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.12
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
    - 0.0
    - 0.12
    tolerance: 0.01
    orientation:
      mode: keep_current
  subtask_id: align_at_entrance
- id: align_to_entrance
  type: align
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
    - 0.0
    offset_along_axis:
      distance: 0.0
      axis: world_x
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    lateral_offset:
      type: scalar
      range:
      - -0.04
      - 0.04
      default: 0.0
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: align_at_entrance
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
      mode: none
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
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
    max_attempts: 1
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **align_to_entrance** (`align`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.0], offset_along_axis={axis=world_x, distance=0.0, mode=replace_offset_projection, sign=positive}, tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - lateral_offset: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **push_through_channel** (`push`)
  - target: source=yaml, anchor=task_goal, entity=channel_exit, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=1, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.431
- **task_score** (E): 0.383
- **fitness_score**: 0.561  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.130

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1777 |
| align_to_entrance | 1.00 | 1.00 | 0.1272 |
| push_through_channel | 0.00 | 1.00 | 0.0003 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.089, 0.165) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.545 | 3.954 |
| align_to_entrance | align | 1.00 / step_budget | (0.505, 0.089, 0.165)→(0.504, 0.110, 0.043) | (0.502, 0.081, 0.034)→(0.502, 0.075, 0.037) | 0.162→0.155 | 1.00 / 1.333 | 145.541 | 296.291 |
| push_through_channel | push | 0.00 / guard_failure | (0.497, -0.049, 0.036)→(0.497, -0.049, 0.036) | (0.502, 0.075, 0.037)→(0.502, -0.080, 0.034) | 0.155→0.010 | 1.00 / 3.000 | 8.062 | 41.982 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.549
- phase_score: 0.694
- phase_breakdown.push_to_goal_score: 0.952
- phase_breakdown.align_at_entrance_score: 0.092

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.636
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.549
- **Median Q (composite search score)**: 0.405
- **K-run variance**: 0.0029
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 11.0
- **Final σ (mean)**: 0.139


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.35227,"average_solve_count":176.0,"average_success_count":176.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_entrance.lateral_offset":0.03128,"push_through_channel.push_speed":0.03274},"optimized_scores":{"best_composite_score":0.40482,"best_fitness_score":0.53482,"best_task_score":0.31494},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":85.0,"contact_point_centroid":[0.52511,0.08696,0.05998],"force_p95":521.22547,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":590.43756,"mean_force":432.33648,"phase_index":1.0,"phase_name":"align_to_entrance","phase_type":"align","tcp_position_centroid":[0.5104,0.08743,0.04697]},{"body_a":"peg","body_b":"channel_base_body","contact_count":561.0,"contact_point_centroid":[0.49475,0.05875,0.00939],"force_p95":0.61549,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":95.44641,"mean_force":1.73101,"phase_index":1.0,"phase_name":"align_to_entrance","phase_type":"align","tcp_position_centroid":[0.49125,0.0777,0.09772]},{"body_a":"attachment","body_b":"peg","contact_count":19.0,"contact_point_centroid":[0.50653,0.07281,0.05781],"force_p95":67.44236,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":94.41463,"mean_force":35.08406,"phase_index":1.0,"phase_name":"align_to_entrance","phase_type":"align","tcp_position_centroid":[0.50961,0.0839,0.05736]},{"body_a":"attachment","body_b":"peg","contact_count":213.0,"contact_point_centroid":[0.49877,0.00576,0.04061],"force_p95":29.58306,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.3184,"mean_force":7.85273,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50186,0.01688,0.03738]},{"body_a":"peg","body_b":"channel_base_body","contact_count":8.0,"contact_point_centroid":[0.49307,-0.10036,0.03392],"force_p95":38.69722,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.18571,"mean_force":15.53744,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4984,-0.05123,0.03607]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":274.0,"contact_point_centroid":[0.47472,-0.01132,0.03656],"force_p95":24.82196,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.3315,"mean_force":3.79152,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50183,0.01675,0.03737]},{"body_a":"peg","body_b":"channel_base_body","contact_count":179.0,"contact_point_centroid":[0.49544,-0.01164,0.00965],"force_p95":19.94622,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.46682,"mean_force":5.55178,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50243,0.02392,0.03784]},{"body_a":"peg","body_b":"channel_base_body","contact_count":603.0,"contact_point_centroid":[0.49428,0.05897,0.00936],"force_p95":0.56357,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.57047,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48177,0.13116,0.22803]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52502,0.08897,0.06],"force_p95":3.63975,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4.04416,"mean_force":1.34805,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50872,0.08952,0.04269]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49884,0.19714,0.29666]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":10.0,"contact_point_centroid":[0.47485,0.05805,0.05871],"force_p95":0.16759,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19018,"mean_force":0.05353,"phase_index":1.0,"phase_name":"align_to_entrance","phase_type":"align","tcp_position_centroid":[0.51172,0.08502,0.05217]}],"total_contact_groups":11},"final_pose_error":0.02572,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49261,-0.08334,0.037],"final_tcp_position":[0.4983,-0.05464,0.03605],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":590.43756,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":632.0,"n_steps_budget":1000.0,"object_pos_end":[0.49414,0.05883,0.03388],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13908,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54311,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":638.0,"raw_peak_contact_force":4.20518,"subtask_id":"align_at_entrance","tcp_end":[0.46629,0.06766,0.16484],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13418,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":561.0,"n_steps_budget":930.0,"object_pos_end":[0.49412,0.05833,0.03411],"object_pos_start":[0.49414,0.05883,0.03388],"object_to_goal_dist_end":0.13858,"object_to_goal_dist_start":0.13908,"object_z_max":0.03433,"peak_contact_force":435.85167,"phase_name":"align_to_entrance","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":675.0,"raw_peak_contact_force":590.43756,"subtask_id":"align_at_entrance","tcp_end":[0.50876,0.08951,0.04274],"tcp_start":[0.46629,0.06766,0.16484],"tcp_to_object_dist_end":0.03552,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":382.0,"n_steps_budget":1000.0,"object_pos_end":[0.49244,-0.08297,0.03716],"object_pos_start":[0.49412,0.05833,0.03411],"object_to_goal_dist_end":0.0086,"object_to_goal_dist_start":0.13858,"object_z_max":0.03963,"peak_contact_force":12.15042,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":677.0,"raw_peak_contact_force":43.3184,"subtask_id":"push_to_goal","tcp_end":[0.4983,-0.05464,0.03605],"tcp_start":[0.49836,-0.05439,0.03609],"tcp_to_object_dist_end":0.02894,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38776,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_entrance.lateral_offset":-0.00292,"push_through_channel.push_speed":0.04288},"optimized_scores":{"best_composite_score":0.38128,"best_fitness_score":0.51128,"best_task_score":0.28662},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":392.0,"contact_point_centroid":[0.50686,0.08077,0.00932],"force_p95":106.85226,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":126.5286,"mean_force":9.92352,"phase_index":1.0,"phase_name":"align_to_entrance","phase_type":"align","tcp_position_centroid":[0.51543,0.09786,0.10163]},{"body_a":"attachment","body_b":"peg","contact_count":42.0,"contact_point_centroid":[0.51301,0.09698,0.05645],"force_p95":125.51052,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":126.04382,"mean_force":87.70064,"phase_index":1.0,"phase_name":"align_to_entrance","phase_type":"align","tcp_position_centroid":[0.5067,0.10606,0.05703]},{"body_a":"attachment","body_b":"peg","contact_count":200.0,"contact_point_centroid":[0.50113,0.00217,0.04416],"force_p95":16.9295,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.46805,"mean_force":3.16797,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49817,0.0139,0.03686]},{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.4895,-0.10056,0.02808],"force_p95":36.7262,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.06289,"mean_force":28.76983,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49706,-0.03845,0.03589]},{"body_a":"peg","body_b":"channel_base_body","contact_count":266.0,"contact_point_centroid":[0.50448,0.00016,0.00953],"force_p95":7.82423,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.25925,"mean_force":1.97484,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49909,0.04129,0.03785]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":40.0,"contact_point_centroid":[0.52511,-0.04794,0.02807],"force_p95":12.09061,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.0668,"mean_force":4.50287,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49813,0.01232,0.03682]},{"body_a":"peg","body_b":"channel_base_body","contact_count":582.0,"contact_point_centroid":[0.5057,0.0809,0.00936],"force_p95":0.55708,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57299,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51481,0.14157,0.22731]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50013,0.19736,0.29642]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52501,0.06234,0.06],"force_p95":0.63974,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6458,"mean_force":0.58513,"phase_index":1.0,"phase_name":"align_to_entrance","phase_type":"align","tcp_position_centroid":[0.50536,0.10795,0.04826]}],"total_contact_groups":9},"final_pose_error":0.04096,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5059,-0.07554,0.02858],"final_tcp_position":[0.49707,-0.03935,0.03588],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":126.5286,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":611.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.55007,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":618.0,"raw_peak_contact_force":4.32595,"subtask_id":"align_at_entrance","tcp_end":[0.53006,0.08827,0.16393],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13256,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":392.0,"n_steps_budget":840.0,"object_pos_end":[0.506,0.06535,0.04066],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.14547,"object_to_goal_dist_start":0.16112,"object_z_max":0.04061,"peak_contact_force":0.39798,"phase_name":"align_to_entrance","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":436.0,"raw_peak_contact_force":126.5286,"subtask_id":"align_at_entrance","tcp_end":[0.50372,0.10847,0.04323],"tcp_start":[0.53006,0.08827,0.16393],"tcp_to_object_dist_end":0.04326,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":384.0,"n_steps_budget":1000.0,"object_pos_end":[0.50586,-0.07541,0.02858],"object_pos_start":[0.506,0.06535,0.04066],"object_to_goal_dist_end":0.01363,"object_to_goal_dist_start":0.14547,"object_z_max":0.04079,"peak_contact_force":11.48204,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":511.0,"raw_peak_contact_force":40.46805,"subtask_id":"push_to_goal","tcp_end":[0.49707,-0.03935,0.03588],"tcp_start":[0.49708,-0.03911,0.0359],"tcp_to_object_dist_end":0.03783,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65909,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_entrance.lateral_offset":-0.0071,"push_through_channel.push_speed":0.0637},"optimized_scores":{"best_composite_score":0.50592,"best_fitness_score":0.63592,"best_task_score":0.54854},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":408.0,"contact_point_centroid":[0.50671,0.1056,0.00924],"force_p95":129.49687,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":171.90744,"mean_force":14.40782,"phase_index":1.0,"phase_name":"align_to_entrance","phase_type":"align","tcp_position_centroid":[0.50781,0.12145,0.1015]},{"body_a":"attachment","body_b":"peg","contact_count":59.0,"contact_point_centroid":[0.50987,0.12319,0.05599],"force_p95":138.5887,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":171.22272,"mean_force":95.98502,"phase_index":1.0,"phase_name":"align_to_entrance","phase_type":"align","tcp_position_centroid":[0.50164,0.13063,0.05619]},{"body_a":"peg","body_b":"channel_base_body","contact_count":6.0,"contact_point_centroid":[0.50778,-0.10035,0.06108],"force_p95":40.43318,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.1585,"mean_force":13.60173,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49634,-0.05328,0.03572]},{"body_a":"attachment","body_b":"peg","contact_count":282.0,"contact_point_centroid":[0.50173,0.0303,0.04251],"force_p95":26.44364,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.76036,"mean_force":6.85845,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49642,0.04145,0.03766]},{"body_a":"peg","body_b":"channel_base_body","contact_count":196.0,"contact_point_centroid":[0.50515,0.00055,0.00978],"force_p95":25.10301,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.7695,"mean_force":8.50092,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49653,0.04417,0.03786]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":355.0,"contact_point_centroid":[0.52522,0.01127,0.02936],"force_p95":10.72048,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.27474,"mean_force":2.17638,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49638,0.03873,0.03756]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52505,0.10125,0.05744],"force_p95":6.79351,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.27982,"mean_force":2.13394,"phase_index":1.0,"phase_name":"align_to_entrance","phase_type":"align","tcp_position_centroid":[0.50191,0.13288,0.05]},{"body_a":"peg","body_b":"channel_base_body","contact_count":505.0,"contact_point_centroid":[0.5056,0.10471,0.00937],"force_p95":0.57748,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56875,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50937,0.15373,0.22847]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49996,0.19792,0.29673]}],"total_contact_groups":9},"final_pose_error":0.02617,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50739,-0.08276,0.0363],"final_tcp_position":[0.49629,-0.05447,0.03566],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":171.90744,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":532.0,"n_steps_budget":1000.0,"object_pos_end":[0.506,0.10464,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.5424,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":537.0,"raw_peak_contact_force":3.33087,"subtask_id":"align_at_entrance","tcp_end":[0.51968,0.11123,0.16543],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13247,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":408.0,"n_steps_budget":870.0,"object_pos_end":[0.50611,0.10177,0.03483],"object_pos_start":[0.506,0.10464,0.03384],"object_to_goal_dist_end":0.18195,"object_to_goal_dist_start":0.18484,"object_z_max":0.03479,"peak_contact_force":0.3736,"phase_name":"align_to_entrance","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":472.0,"raw_peak_contact_force":171.90744,"subtask_id":"align_at_entrance","tcp_end":[0.4997,0.13303,0.04353],"tcp_start":[0.51968,0.11123,0.16543],"tcp_to_object_dist_end":0.03307,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":478.0,"n_steps_budget":1000.0,"object_pos_end":[0.50753,-0.08255,0.03642],"object_pos_start":[0.50611,0.10177,0.03483],"object_to_goal_dist_end":0.00872,"object_to_goal_dist_start":0.18195,"object_z_max":0.03844,"peak_contact_force":0.55269,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":839.0,"raw_peak_contact_force":42.1585,"subtask_id":"push_to_goal","tcp_end":[0.49629,-0.05447,0.03566],"tcp_start":[0.49633,-0.05421,0.03569],"tcp_to_object_dist_end":0.03026,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```