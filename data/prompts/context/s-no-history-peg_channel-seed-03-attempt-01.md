## Search State

- **Seed**: 3
- **Iteration**: 2 / 15

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

## Current Skill (Q=0.420) — your mutation base

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

- **Composite score**: 0.420
- **task_score** (E): 0.336
- **fitness_score**: 0.550  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.130

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1777 |
| align_to_entrance | 1.00 | 1.00 | 0.1276 |
| push_through_channel | 0.00 | 1.00 | 0.0003 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.089, 0.165) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.545 | 3.954 |
| align_to_entrance | align | 1.00 / step_budget | (0.505, 0.089, 0.165)→(0.502, 0.111, 0.044) | (0.502, 0.081, 0.034)→(0.502, 0.076, 0.037) | 0.162→0.156 | 1.00 / 1.333 | 1.017 | 260.458 |
| push_through_channel | push | 0.00 / guard_failure | (0.497, -0.052, 0.036)→(0.497, -0.052, 0.036) | (0.502, 0.076, 0.037)→(0.506, -0.080, 0.037) | 0.156→0.007 | 1.00 / 2.667 | 3.655 | 43.905 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.548
- phase_score: 0.695
- phase_breakdown.push_to_goal_score: 0.953
- phase_breakdown.align_at_entrance_score: 0.093

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.637
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.548
- **Median Q (composite search score)**: 0.403
- **K-run variance**: 0.0042
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 11.0
- **Final σ (mean)**: 0.156


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7563,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_entrance.lateral_offset":0.01594,"push_through_channel.push_speed":0.07003},"optimized_scores":{"best_composite_score":0.35008,"best_fitness_score":0.48008,"best_task_score":0.16209},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.5251,0.09076,0.05998],"force_p95":477.39365,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":479.88511,"mean_force":346.64029,"phase_index":1.0,"phase_name":"align_to_entrance","phase_type":"align","tcp_position_centroid":[0.51104,0.09128,0.04788]},{"body_a":"peg","body_b":"channel_base_body","contact_count":518.0,"contact_point_centroid":[0.49693,0.06094,0.00923],"force_p95":142.55137,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":151.98779,"mean_force":22.7088,"phase_index":1.0,"phase_name":"align_to_entrance","phase_type":"align","tcp_position_centroid":[0.4856,0.07793,0.09872]},{"body_a":"attachment","body_b":"peg","contact_count":105.0,"contact_point_centroid":[0.50742,0.07679,0.05498],"force_p95":148.06047,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":151.56274,"mean_force":109.4499,"phase_index":1.0,"phase_name":"align_to_entrance","phase_type":"align","tcp_position_centroid":[0.50456,0.08719,0.05358]},{"body_a":"attachment","body_b":"peg","contact_count":123.0,"contact_point_centroid":[0.50006,0.01072,0.0443],"force_p95":24.6937,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.48876,"mean_force":6.86208,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50281,0.02172,0.03859]},{"body_a":"peg","body_b":"channel_base_body","contact_count":18.0,"contact_point_centroid":[0.50409,-0.10061,0.05676],"force_p95":28.30611,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.68767,"mean_force":4.9433,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49857,-0.04313,0.03631]},{"body_a":"peg","body_b":"channel_base_body","contact_count":211.0,"contact_point_centroid":[0.49643,-0.01659,0.00957],"force_p95":20.84518,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.40204,"mean_force":3.89722,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50304,0.0217,0.03895]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":161.0,"contact_point_centroid":[0.47462,0.01093,0.03211],"force_p95":8.10417,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.59997,"mean_force":1.56208,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50418,0.04014,0.03949]},{"body_a":"peg","body_b":"channel_base_body","contact_count":603.0,"contact_point_centroid":[0.49428,0.05897,0.00936],"force_p95":0.56357,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.57047,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48177,0.13116,0.22803]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49884,0.19714,0.29666]}],"total_contact_groups":9},"final_pose_error":0.03361,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50486,-0.07613,0.03851],"final_tcp_position":[0.49833,-0.04665,0.03617],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":479.88511,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":632.0,"n_steps_budget":1000.0,"object_pos_end":[0.49414,0.05883,0.03388],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13908,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54311,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":638.0,"raw_peak_contact_force":4.20518,"subtask_id":"align_at_entrance","tcp_end":[0.46629,0.06766,0.16484],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13418,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":518.0,"n_steps_budget":870.0,"object_pos_end":[0.49546,0.05258,0.03577],"object_pos_start":[0.49414,0.05883,0.03388],"object_to_goal_dist_end":0.13273,"object_to_goal_dist_start":0.13908,"object_z_max":0.03658,"peak_contact_force":2.24125,"phase_name":"align_to_entrance","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":639.0,"raw_peak_contact_force":479.88511,"subtask_id":"align_at_entrance","tcp_end":[0.51022,0.09184,0.04495],"tcp_start":[0.46629,0.06766,0.16484],"tcp_to_object_dist_end":0.04294,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":345.0,"n_steps_budget":1000.0,"object_pos_end":[0.50485,-0.07617,0.03849],"object_pos_start":[0.49546,0.05258,0.03577],"object_to_goal_dist_end":0.00636,"object_to_goal_dist_start":0.13273,"object_z_max":0.03912,"peak_contact_force":3.11461,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":513.0,"raw_peak_contact_force":44.48876,"subtask_id":"push_to_goal","tcp_end":[0.49833,-0.04665,0.03617],"tcp_start":[0.49837,-0.0464,0.03621],"tcp_to_object_dist_end":0.03032,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88991,"average_solve_count":109.0,"average_success_count":109.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_entrance.lateral_offset":-0.01416,"push_through_channel.push_speed":0.09587},"optimized_scores":{"best_composite_score":0.40307,"best_fitness_score":0.53307,"best_task_score":0.29697},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":392.0,"contact_point_centroid":[0.50627,0.08058,0.00932],"force_p95":95.45998,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":139.24474,"mean_force":8.44771,"phase_index":1.0,"phase_name":"align_to_entrance","phase_type":"align","tcp_position_centroid":[0.51047,0.09776,0.10207]},{"body_a":"attachment","body_b":"peg","contact_count":37.0,"contact_point_centroid":[0.50627,0.09869,0.05702],"force_p95":135.47364,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":138.7167,"mean_force":83.79903,"phase_index":1.0,"phase_name":"align_to_entrance","phase_type":"align","tcp_position_centroid":[0.49778,0.10582,0.05799]},{"body_a":"peg","body_b":"channel_base_body","contact_count":9.0,"contact_point_centroid":[0.5073,-0.10056,0.06136],"force_p95":41.92365,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.9319,"mean_force":11.89226,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49531,-0.05288,0.03564]},{"body_a":"attachment","body_b":"peg","contact_count":235.0,"contact_point_centroid":[0.49964,0.00805,0.04384],"force_p95":18.46091,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.56612,"mean_force":3.07421,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49298,0.01878,0.03729]},{"body_a":"peg","body_b":"channel_base_body","contact_count":146.0,"contact_point_centroid":[0.50633,0.00152,0.00964],"force_p95":18.97343,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.16674,"mean_force":4.36614,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49255,0.04203,0.03825]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":185.0,"contact_point_centroid":[0.5253,0.00303,0.02984],"force_p95":4.90139,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.59446,"mean_force":1.29031,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4927,0.02913,0.0376]},{"body_a":"peg","body_b":"channel_base_body","contact_count":582.0,"contact_point_centroid":[0.5057,0.0809,0.00936],"force_p95":0.55708,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57299,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51481,0.14157,0.22731]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50013,0.19736,0.29642]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.5251,0.07455,0.05847],"force_p95":0.97339,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.02571,"mean_force":0.58342,"phase_index":1.0,"phase_name":"align_to_entrance","phase_type":"align","tcp_position_centroid":[0.49703,0.10727,0.05299]}],"total_contact_groups":9},"final_pose_error":0.02607,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50616,-0.08308,0.03644],"final_tcp_position":[0.49533,-0.05474,0.03556],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":139.24474,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":611.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.55007,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":618.0,"raw_peak_contact_force":4.32595,"subtask_id":"align_at_entrance","tcp_end":[0.53006,0.08827,0.16393],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13256,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":392.0,"n_steps_budget":870.0,"object_pos_end":[0.50424,0.07423,0.03831],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.1543,"object_to_goal_dist_start":0.16112,"object_z_max":0.03828,"peak_contact_force":0.43274,"phase_name":"align_to_entrance","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":435.0,"raw_peak_contact_force":139.24474,"subtask_id":"align_at_entrance","tcp_end":[0.49325,0.10832,0.04329],"tcp_start":[0.53006,0.08827,0.16393],"tcp_to_object_dist_end":0.03616,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":399.0,"n_steps_budget":1000.0,"object_pos_end":[0.50622,-0.08283,0.03663],"object_pos_start":[0.50424,0.07423,0.03831],"object_to_goal_dist_end":0.00762,"object_to_goal_dist_start":0.1543,"object_z_max":0.04025,"peak_contact_force":1.23568,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":575.0,"raw_peak_contact_force":44.9319,"subtask_id":"push_to_goal","tcp_end":[0.49533,-0.05474,0.03556],"tcp_start":[0.49536,-0.05447,0.03559],"tcp_to_object_dist_end":0.03015,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38571,"average_solve_count":140.0,"average_success_count":140.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_entrance.lateral_offset":-0.00525,"push_through_channel.push_speed":0.05649},"optimized_scores":{"best_composite_score":0.50652,"best_fitness_score":0.63652,"best_task_score":0.54834},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":404.0,"contact_point_centroid":[0.50674,0.10547,0.00925],"force_p95":125.74085,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":162.24375,"mean_force":13.57671,"phase_index":1.0,"phase_name":"align_to_entrance","phase_type":"align","tcp_position_centroid":[0.50868,0.12135,0.10181]},{"body_a":"attachment","body_b":"peg","contact_count":56.0,"contact_point_centroid":[0.51088,0.12262,0.05616],"force_p95":134.72472,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":161.6951,"mean_force":94.08894,"phase_index":1.0,"phase_name":"align_to_entrance","phase_type":"align","tcp_position_centroid":[0.50308,0.13046,0.05626]},{"body_a":"peg","body_b":"channel_base_body","contact_count":7.0,"contact_point_centroid":[0.50738,-0.1005,0.05994],"force_p95":41.2905,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.29493,"mean_force":30.01479,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49646,-0.05313,0.03567]},{"body_a":"attachment","body_b":"peg","contact_count":327.0,"contact_point_centroid":[0.50215,0.02034,0.04221],"force_p95":22.17599,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.67285,"mean_force":5.67745,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49719,0.0316,0.03742]},{"body_a":"peg","body_b":"channel_base_body","contact_count":193.0,"contact_point_centroid":[0.5052,0.00334,0.00982],"force_p95":21.64929,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.17103,"mean_force":7.83792,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49749,0.04728,0.03796]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":351.0,"contact_point_centroid":[0.52517,0.00806,0.02894],"force_p95":7.90955,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.94373,"mean_force":1.94837,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49721,0.03584,0.03748]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52505,0.10167,0.05716],"force_p95":4.67996,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.55519,"mean_force":1.793,"phase_index":1.0,"phase_name":"align_to_entrance","phase_type":"align","tcp_position_centroid":[0.50372,0.13252,0.051]},{"body_a":"peg","body_b":"channel_base_body","contact_count":505.0,"contact_point_centroid":[0.5056,0.10471,0.00937],"force_p95":0.57748,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56875,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50937,0.15373,0.22847]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49996,0.19792,0.29673]}],"total_contact_groups":9},"final_pose_error":0.02632,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50738,-0.08205,0.0363],"final_tcp_position":[0.49636,-0.05432,0.03554],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":162.24375,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":532.0,"n_steps_budget":1000.0,"object_pos_end":[0.506,0.10464,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.5424,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":537.0,"raw_peak_contact_force":3.33087,"subtask_id":"align_at_entrance","tcp_end":[0.51968,0.11123,0.16543],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13247,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":404.0,"n_steps_budget":840.0,"object_pos_end":[0.5058,0.10025,0.03595],"object_pos_start":[0.506,0.10464,0.03384],"object_to_goal_dist_end":0.18039,"object_to_goal_dist_start":0.18484,"object_z_max":0.03586,"peak_contact_force":0.37837,"phase_name":"align_to_entrance","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":465.0,"raw_peak_contact_force":162.24375,"subtask_id":"align_at_entrance","tcp_end":[0.50132,0.13281,0.04364],"tcp_start":[0.51968,0.11123,0.16543],"tcp_to_object_dist_end":0.03375,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":485.0,"n_steps_budget":1000.0,"object_pos_end":[0.50736,-0.08184,0.03637],"object_pos_start":[0.5058,0.10025,0.03595],"object_to_goal_dist_end":0.00841,"object_to_goal_dist_start":0.18039,"object_z_max":0.03827,"peak_contact_force":6.61618,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":878.0,"raw_peak_contact_force":42.29493,"subtask_id":"push_to_goal","tcp_end":[0.49636,-0.05432,0.03554],"tcp_start":[0.49641,-0.05409,0.03559],"tcp_to_object_dist_end":0.02965,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```