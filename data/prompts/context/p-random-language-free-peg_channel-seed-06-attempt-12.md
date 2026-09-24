## Search State

- **Seed**: 6
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → push | linear_cartesian | linear_cartesian | impedance_control | impedance_control | pose_tolerance | pose_tolerance | 8 | -0.2201 | 0.04 | ❌ rejected |
| 11 | approach → push | linear_cartesian | linear_cartesian | impedance_control | impedance_control | pose_tolerance | time_limit | 8 | 0.0712 | 0.42 | ✅ accepted |
| 10 | approach → push | linear_cartesian | linear_cartesian | impedance_control | impedance_control | pose_tolerance | time_limit | 8 | 0.0693 | 0.42 | ✅ accepted |
| 9 | approach → push | linear_cartesian | linear_cartesian | impedance_control | impedance_control | pose_tolerance | time_limit | 6 | 0.1970 | 0.41 | ✅ accepted |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | -0.2914 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.04 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.220) — your mutation base

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
    target_x_offset:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.x
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
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
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
      - 5.0
      - 10.0
      default: 7.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 39.5
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
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.0], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 1.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - target_x_offset: status=consumed; consumers=target.offset.x (replace)
    - target_y_offset: status=consumed; consumers=target.offset.y (replace)
  - guards:
    - id=contact_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=30.0
  - retries: max_attempts=2, strategy=reduce_speed
- **push_channel** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=replace_offset_projection, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, 1.0, 0.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (replace)
    - lateral_retry_x: status=consumed; consumers=retry.offset.x (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_duration: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=39.5
  - retries: max_attempts=3, strategy=offset_target, offset=[0.005, 0.0, 0.0]

## Design Metrics

- **Composite score**: -0.220
- **task_score** (E): 0.035
- **fitness_score**: 0.180  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.400

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.2622 |
| push_channel | 0.00 | 1.00 | 0.0002 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.499, 0.131, 0.049) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.179 | 1.00 / 1.000 | 0.533 | 4.371 |
| push_channel | push | 0.00 / guard_failure | (0.497, 0.116, 0.044)→(0.497, 0.116, 0.044) | (0.501, 0.099, 0.034)→(0.503, 0.091, 0.037) | 0.179→0.171 | 1.00 / 2.333 | 16.949 | 31.922 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.084
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.039
- phase_score: 0.294
- phase_breakdown.approach_peg_score: 0.816
- phase_breakdown.push_through_score: 0.070

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.192
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.042
- **Median Q (composite search score)**: -0.219
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.289


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91176,"average_solve_count":68.0,"average_success_count":68.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.09987,"approach_behind.target_x_offset":-0.00216,"approach_behind.target_y_offset":0.02846,"push_channel.force_threshold":8.91266,"push_channel.lateral_offset_x":-0.00201,"push_channel.lateral_retry_x":0.0129,"push_channel.push_distance":0.15575,"push_channel.push_speed":0.10156},"optimized_scores":{"best_composite_score":-0.21872,"best_fitness_score":0.18128,"best_task_score":0.04213},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":40.0,"contact_point_centroid":[0.50444,0.05531,0.00948],"force_p95":8.6582,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.22793,"mean_force":2.37307,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49598,0.09484,0.04589]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.49974,0.08143,0.05223],"force_p95":23.81082,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.07143,"mean_force":8.55674,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4957,0.09294,0.04536]},{"body_a":"peg","body_b":"channel_base_body","contact_count":829.0,"contact_point_centroid":[0.50303,0.06748,0.00935],"force_p95":0.55323,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55703,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.4978,0.14893,0.17016]}],"total_contact_groups":3},"final_pose_error":0.17717,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50344,0.06072,0.03834],"final_tcp_position":[0.49524,0.08849,0.04426],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":26.22793,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":845.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.06748,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54725,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":829.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach_peg","tcp_end":[0.49722,0.10029,0.04799],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.03623,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":40.0,"n_steps_budget":1000.0,"object_pos_end":[0.50338,0.0613,0.03809],"object_pos_start":[0.50309,0.06748,0.0338],"object_to_goal_dist_end":0.14135,"object_to_goal_dist_start":0.14764,"object_z_max":0.03827,"peak_contact_force":3.1471,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":49.0,"raw_peak_contact_force":26.22793,"subtask_id":"push_through","tcp_end":[0.49524,0.08849,0.04426],"tcp_start":[0.49528,0.08863,0.04434],"tcp_to_object_dist_end":0.02905,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.03279,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.04827,"approach_behind.target_x_offset":0.00851,"approach_behind.target_y_offset":0.02456,"push_channel.force_threshold":12.16745,"push_channel.lateral_offset_x":-0.00458,"push_channel.lateral_retry_x":0.01246,"push_channel.push_distance":0.1634,"push_channel.push_speed":0.08959},"optimized_scores":{"best_composite_score":-0.23322,"best_fitness_score":0.16678,"best_task_score":0.02441},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":28.0,"contact_point_centroid":[0.4983,0.0966,0.0096],"force_p95":12.19472,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.00847,"mean_force":2.77608,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5125,0.13542,0.04665]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.50811,0.12385,0.04744],"force_p95":14.60057,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.6966,"mean_force":8.27164,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51244,0.13488,0.04653]},{"body_a":"peg","body_b":"channel_base_body","contact_count":854.0,"contact_point_centroid":[0.50343,0.11138,0.00938],"force_p95":0.6117,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.79448,"mean_force":0.57843,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50621,0.16833,0.1701]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50967,0.12834,0.0529],"force_p95":8.37686,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.40599,"mean_force":5.79822,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.51365,0.13959,0.05209]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.4999,0.19978,0.29907]}],"total_contact_groups":5},"final_pose_error":0.18466,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49826,0.1063,0.03845],"final_tcp_position":[0.51146,0.13112,0.04527],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":16.00847,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":876.0,"n_steps_budget":1000.0,"object_pos_end":[0.50403,0.11055,0.03487],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19066,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.49769,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":874.0,"raw_peak_contact_force":8.79448,"subtask_id":"approach_peg","tcp_end":[0.5139,0.1387,0.04834],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.03273,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":28.0,"n_steps_budget":1000.0,"object_pos_end":[0.49855,0.10666,0.03815],"object_pos_start":[0.50403,0.11055,0.03487],"object_to_goal_dist_end":0.18668,"object_to_goal_dist_start":0.19066,"object_z_max":0.03836,"peak_contact_force":10.55752,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":36.0,"raw_peak_contact_force":16.00847,"subtask_id":"push_through","tcp_end":[0.51146,0.13112,0.04527],"tcp_start":[0.51149,0.13126,0.04536],"tcp_to_object_dist_end":0.02856,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.05303,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.03219,"approach_behind.target_x_offset":0.00242,"approach_behind.target_y_offset":0.03289,"push_channel.force_threshold":14.18981,"push_channel.lateral_offset_x":-0.00178,"push_channel.lateral_retry_x":0.00852,"push_channel.push_distance":0.16464,"push_channel.push_speed":0.10739},"optimized_scores":{"best_composite_score":-0.20822,"best_fitness_score":0.19178,"best_task_score":0.039},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.4749,0.11992,0.04528],"force_p95":52.05793,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":53.5295,"mean_force":34.24382,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48384,0.1275,0.0434]},{"body_a":"peg","body_b":"channel_base_body","contact_count":61.0,"contact_point_centroid":[0.50117,0.106,0.00939],"force_p95":9.03301,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.44763,"mean_force":1.52851,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48427,0.1423,0.04597]},{"body_a":"attachment","body_b":"peg","contact_count":25.0,"contact_point_centroid":[0.49159,0.12818,0.05716],"force_p95":12.21334,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.91083,"mean_force":2.29962,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48395,0.13871,0.04508]},{"body_a":"peg","body_b":"channel_base_body","contact_count":822.0,"contact_point_centroid":[0.49617,0.11911,0.00942],"force_p95":0.60334,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55085,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49186,0.17572,0.17008]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49968,0.19963,0.29792]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52518,0.10307,0.05922],"force_p95":0.63724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65164,"mean_force":0.51524,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48384,0.12738,0.04338]}],"total_contact_groups":6},"final_pose_error":0.17289,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50643,0.10559,0.03529],"final_tcp_position":[0.48383,0.12711,0.04327],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":216.9848,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":847.0,"n_steps_budget":1000.0,"object_pos_end":[0.49599,0.11942,0.03386],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19955,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.55336,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":846.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach_peg","tcp_end":[0.48569,0.1534,0.04918],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.03868,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":82.0,"n_steps_budget":1000.0,"object_pos_end":[0.50606,0.10543,0.03519],"object_pos_start":[0.49599,0.11942,0.03386],"object_to_goal_dist_end":0.18559,"object_to_goal_dist_start":0.19955,"object_z_max":0.03892,"peak_contact_force":37.14352,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":93.0,"raw_peak_contact_force":53.5295,"subtask_id":"push_through","tcp_end":[0.48383,0.12711,0.04327],"tcp_start":[0.48384,0.12722,0.04332],"tcp_to_object_dist_end":0.03208,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```