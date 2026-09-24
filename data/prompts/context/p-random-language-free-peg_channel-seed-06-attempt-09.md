## Search State

- **Seed**: 6
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → push | linear_cartesian | linear_cartesian | impedance_control | impedance_control | pose_tolerance | time_limit | 6 | 0.1970 | 0.41 | ✅ accepted |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | -0.2914 | 0.00 | ❌ rejected |
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | -0.1774 | 0.15 | ❌ rejected |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 0.5757 | 0.41 | ✅ accepted |
| 5 | approach → push | linear_cartesian | impedance_motion | position_control | impedance_control | pose_tolerance | pose_tolerance | 4 | -0.1992 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.41 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`
- Frozen object start: [0.5030531481177555, 0.06746166958506708, 0.04]
- Frozen task target: [0.5030531481177555, -0.09253833041493292, 0.04]
- Goal object position: (0.5030531481177555, -0.09253833041493292, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5030531481177555, 0.06746166958506708, 0.04)
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
  frozen_object_start: [0.5031, 0.0675, 0.04]
  frozen_task_target: [0.5031, -0.0925, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5030531481177555, 0.06746166958506708, 0.04]}
  frozen_targets: {'channel_exit': [0.5030531481177555, -0.09253833041493292, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de

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
| `object` | offset from object initial position (0.5030531481177555, 0.06746166958506708, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5030531481177555, -0.09253833041493292, 0.04) | final destination targets |
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

## Current Skill (Q=0.197) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_peg
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.0
  weight: 0.3
- id: push_through
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_behind
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: ''
    offset:
    - 0.0
    - 0.03
    - 0.0
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 1.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    target_y_offset:
      type: scalar
      range:
      - 0.02
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.y
        mode: replace
  guards:
  - id: contact_guard
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: approach_peg
- id: push_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    entity: ''
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 1.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    lateral_retry_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.005
      binds_to:
      - path: retry.offset.x
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.14
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_duration:
      type: scalar
      range:
      - 3.0
      - 8.0
      default: 5.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 38.0
    on_failure: retry
  retries:
    max_attempts: 3
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.0
  subtask_id: push_through

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, entity=, offset=[0.0, 0.03, 0.0], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 1.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - target_y_offset: status=consumed; consumers=target.offset.y (replace)
  - guards:
    - id=contact_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=30.0
  - retries: max_attempts=2, strategy=reduce_speed
- **push_channel** (`push`)
  - target: source=yaml, anchor=task_object, entity=, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=replace_offset_projection, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, 1.0, 0.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - lateral_retry_x: status=consumed; consumers=retry.offset.x (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_duration: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=38.0
  - retries: max_attempts=3, strategy=offset_target, offset=[0.005, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.197
- **task_score** (E): 0.411
- **fitness_score**: 0.497  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.300

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.2628 |
| push_channel | 0.67 | 1.00 | 0.0644 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.496, 0.129, 0.049) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.035) | 0.180→0.179 | 1.00 / 1.333 | 5.728 | 10.457 |
| push_channel | push | 0.67 / time_limit | (0.496, 0.121, 0.046)→(0.494, 0.057, 0.040) | (0.501, 0.099, 0.035)→(0.503, 0.026, 0.039) | 0.179→0.106 | 1.00 / 2.667 | 23.221 | 26.872 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.675
- alignment_error: None
- force_efficiency: 0.428
- terminal_score: 0.675
- phase_score: 0.751
- phase_breakdown.approach_peg_score: 0.818
- phase_breakdown.push_through_score: 0.722

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.720
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.675
- **Median Q (composite search score)**: 0.279
- **K-run variance**: 0.0500
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.359


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `080f370e6b427cbdf66706e7036a0e474f3967ccfc94f129756881a980a10a27`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `1f3f20d8b9dd2cb87de5d9f0723b4addbc88cdcf096cd2177633d23c0fa32881`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.03788,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.06002,"approach_behind.target_y_offset":0.02007,"push_channel.lateral_retry_x":-0.00992,"push_channel.push_distance":0.17779,"push_channel.push_duration":6.13329,"push_channel.push_speed":0.06},"optimized_scores":{"best_composite_score":0.4204,"best_fitness_score":0.7204,"best_task_score":0.67487},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":1000.0,"contact_point_centroid":[0.50111,0.03269,0.04057],"force_p95":25.67508,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.5792,"mean_force":13.19453,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49708,0.04365,0.04126]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50418,0.0092,0.00987],"force_p95":21.37205,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.39555,"mean_force":12.42868,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49708,0.04365,0.04126]},{"body_a":"peg","body_b":"channel_base_body","contact_count":918.0,"contact_point_centroid":[0.50316,0.06671,0.00937],"force_p95":0.55498,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.6488,"mean_force":0.66919,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49879,0.14494,0.17019]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.50115,0.08257,0.05219],"force_p95":16.334,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.36687,"mean_force":10.96925,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49928,0.09436,0.05252]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":289.0,"contact_point_centroid":[0.52508,-0.01383,0.02723],"force_p95":10.90222,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.62815,"mean_force":8.1082,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49774,0.00934,0.03936]}],"total_contact_groups":5},"final_pose_error":0.10915,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5072,-0.04052,0.04007],"final_tcp_position":[0.49805,-0.00465,0.0386],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":28.5792,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":934.0,"n_steps_budget":1000.0,"object_pos_end":[0.50348,0.06415,0.03648],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14423,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":16.6488,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":928.0,"raw_peak_contact_force":16.6488,"subtask_id":"approach_peg","tcp_end":[0.49931,0.09239,0.04778],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.03071,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5072,-0.04052,0.04007],"object_pos_start":[0.50348,0.06415,0.03648],"object_to_goal_dist_end":0.04013,"object_to_goal_dist_start":0.14423,"object_z_max":0.04056,"peak_contact_force":23.46648,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2289.0,"raw_peak_contact_force":28.5792,"subtask_id":"push_through","tcp_end":[0.49805,-0.00465,0.0386],"tcp_start":[0.49931,0.09239,0.04778],"tcp_to_object_dist_end":0.03705,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `625c03a21403c0f6267b643060335ee3d751a26340ace08db5429afcee4c5ccf`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69725,"average_solve_count":109.0,"average_success_count":109.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.07507,"approach_behind.target_y_offset":0.02691,"push_channel.lateral_retry_x":0.00563,"push_channel.push_distance":0.188,"push_channel.push_duration":4.73806,"push_channel.push_speed":0.05771},"optimized_scores":{"best_composite_score":0.2793,"best_fitness_score":0.5793,"best_task_score":0.51678},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":999.0,"contact_point_centroid":[0.50126,0.05641,0.0099],"force_p95":13.31604,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.95967,"mean_force":9.63363,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50213,0.09315,0.04158]},{"body_a":"attachment","body_b":"peg","contact_count":993.0,"contact_point_centroid":[0.50272,0.08107,0.04153],"force_p95":12.92842,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.61194,"mean_force":9.30112,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50211,0.09286,0.04153]},{"body_a":"peg","body_b":"channel_base_body","contact_count":794.0,"contact_point_centroid":[0.50359,0.11145,0.00939],"force_p95":0.61504,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.47293,"mean_force":0.57799,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50216,0.16942,0.17003]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50499,0.12954,0.05113],"force_p95":11.48597,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.30498,"mean_force":5.22046,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50585,0.14149,0.05094]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49988,0.19974,0.29892]}],"total_contact_groups":5},"final_pose_error":0.12274,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50068,0.00914,0.04047],"final_tcp_position":[0.50161,0.04594,0.03843],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":13.95967,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":816.0,"n_steps_budget":1000.0,"object_pos_end":[0.50348,0.11129,0.03413],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19141,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.02516,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":814.0,"raw_peak_contact_force":12.47293,"subtask_id":"approach_peg","tcp_end":[0.50591,0.141,0.04878],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.03322,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50068,0.00914,0.04047],"object_pos_start":[0.50348,0.11129,0.03413],"object_to_goal_dist_end":0.08915,"object_to_goal_dist_start":0.19141,"object_z_max":0.04056,"peak_contact_force":10.05789,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1992.0,"raw_peak_contact_force":13.95967,"subtask_id":"push_through","tcp_end":[0.50161,0.04594,0.03843],"tcp_start":[0.50591,0.141,0.04878],"tcp_to_object_dist_end":0.03687,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `abe38b4b57ac37a91047e57d04e408cb1fd05583a47670bcb186dc9505a3f021`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67778,"average_solve_count":90.0,"average_success_count":90.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.08043,"approach_behind.target_y_offset":0.03392,"push_channel.lateral_retry_x":0.00439,"push_channel.push_distance":0.14486,"push_channel.push_duration":5.32158,"push_channel.push_speed":0.02756},"optimized_scores":{"best_composite_score":-0.10861,"best_fitness_score":0.19139,"best_task_score":0.04114},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47495,0.11993,0.04407],"force_p95":37.73164,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":38.07742,"mean_force":25.74844,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48142,0.12985,0.04271]},{"body_a":"peg","body_b":"channel_base_body","contact_count":429.0,"contact_point_centroid":[0.50215,0.10286,0.00983],"force_p95":3.16756,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.95276,"mean_force":1.64624,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48104,0.14032,0.04401]},{"body_a":"attachment","body_b":"peg","contact_count":304.0,"contact_point_centroid":[0.4892,0.12778,0.05082],"force_p95":2.91247,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.57134,"mean_force":1.73012,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48102,0.13771,0.04355]},{"body_a":"peg","body_b":"channel_base_body","contact_count":765.0,"contact_point_centroid":[0.49621,0.11938,0.00941],"force_p95":0.60125,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55222,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49069,0.17617,0.16984]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49962,0.19958,0.29761]}],"total_contact_groups":5},"final_pose_error":0.15303,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50133,0.10803,0.03725],"final_tcp_position":[0.48145,0.12991,0.04268],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":38.07742,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":790.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.1227,0.03372],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.20284,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.50974,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":789.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach_peg","tcp_end":[0.48342,0.15438,0.04925],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.03747,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":445.0,"n_steps_budget":1000.0,"object_pos_end":[0.50128,0.10801,0.03726],"object_pos_start":[0.49602,0.1227,0.03372],"object_to_goal_dist_end":0.18804,"object_to_goal_dist_start":0.20284,"object_z_max":0.03735,"peak_contact_force":36.13769,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":761.0,"raw_peak_contact_force":38.07742,"subtask_id":"push_through","tcp_end":[0.48145,0.12991,0.04268],"tcp_start":[0.48145,0.12987,0.04269],"tcp_to_object_dist_end":0.03003,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```