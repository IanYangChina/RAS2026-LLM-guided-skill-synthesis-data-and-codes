## Search State

- **Seed**: 5
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 7 | 0.2810 | 0.61 | ❌ rejected |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.4484 | 0.79 | ❌ rejected |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3589 | 0.80 | ❌ rejected |
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5102 | 0.81 | ❌ rejected |
| 6 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.1186 | 0.34 | ❌ rejected |

**Proposal policy**: task_score is 0.61 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`
- Frozen object start: [0.5244002338996304, 0.1046352631789195, 0.04]
- Frozen task target: [0.5244002338996304, -0.05536473682108051, 0.04]
- Goal object position: (0.5244002338996304, -0.05536473682108051, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5244002338996304, 0.1046352631789195, 0.04)
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
  frozen_object_start: [0.5244, 0.1046, 0.04]
  frozen_task_target: [0.5244, -0.0554, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5244002338996304, 0.1046352631789195, 0.04]}
  frozen_targets: {'channel_exit': [0.5244002338996304, -0.05536473682108051, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.821, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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
| `object` | offset from object initial position (0.5244002338996304, 0.1046352631789195, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5244002338996304, -0.05536473682108051, 0.04) | final destination targets |
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

## Current Skill (Q=0.281) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: pre_push_approach
  anchor: object
  offset:
  - 0.0
  - 0.08
  - 0.0
  weight: 0.3
- id: push_channel
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_behind_high
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
    - 0.08
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_push_approach
- id: descend_to_lateral
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.08
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_push_approach
- id: push_along_channel
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
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    force_limit:
      type: scalar
      range:
      - 30.0
      - 50.0
      default: 40.0
      binds_to:
      - path: guards.force_safe.threshold
        mode: replace
    lateral_nudge:
      type: scalar
      range:
      - 0.0
      - 0.02
      default: 0.005
      binds_to:
      - path: retry.offset.x
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.14
      - 0.25
      default: 0.18
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.03
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_safe
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.0
  subtask_id: push_channel
- id: retract_upward
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.05
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.03
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind_high** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.08, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_lateral** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.08, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_along_channel** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_limit: status=consumed; consumers=guards.force_safe.threshold (replace)
    - lateral_nudge: status=consumed; consumers=retry.offset.x (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_safe, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.0, 0.0]
- **retract_upward** (`retract`)
  - target: source=yaml, anchor=task_goal, entity=peg, offset=[0.0, 0.0, 0.1], tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.281
- **task_score** (E): 0.605
- **fitness_score**: 0.661  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind_high | 1.00 | 1.00 | 0.1548 |
| descend_to_lateral | 1.00 | 1.00 | 0.1123 |
| push_along_channel | 1.00 | 1.00 | 0.1644 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.176, 0.149) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.543 | 2.488 |
| descend_to_lateral | descend | 1.00 / step_budget | (0.508, 0.176, 0.149)→(0.501, 0.173, 0.037) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.536 | 0.593 |
| push_along_channel | push | 1.00 / time_limit | (0.501, 0.173, 0.037)→(0.499, 0.009, 0.030) | (0.504, 0.095, 0.034)→(0.507, -0.020, 0.036) | 0.175→0.061 | 1.00 / 3.000 | 8.549 | 13.535 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.709
- alignment_error: None
- force_efficiency: 0.713
- terminal_score: 0.709
- phase_score: 0.803
- phase_breakdown.pre_push_approach_score: 0.897
- phase_breakdown.push_channel_score: 0.763

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.765
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.717
- **Median Q (composite search score)**: 0.303
- **K-run variance**: 0.0091
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at upper bound**: push_along_channel.push_speed
- **Final σ (mean)**: 0.485


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9b36d26f861d7a613dfb3d8c86d70470e42095a430c2befa4bd6e530468a8a7e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2af86d8f59685db6584febc0596b9044223ae39cea3120c112c665a54a1c4732`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95413,"average_solve_count":218.0,"average_success_count":218.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_high.approach_speed":0.02896,"descend_to_lateral.descend_speed":0.03497,"push_along_channel.force_limit":69.53805,"push_along_channel.lateral_nudge":0.00536,"push_along_channel.max_push_time":7.86624,"push_along_channel.push_distance":0.15087,"push_along_channel.push_speed":0.09992},"optimized_scores":{"best_composite_score":0.15457,"best_fitness_score":0.53457,"best_task_score":0.38942},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":694.0,"contact_point_centroid":[0.50599,0.06297,0.00968],"force_p95":8.86126,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.212,"mean_force":2.90856,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.5004,0.1126,0.032]},{"body_a":"attachment","body_b":"peg","contact_count":544.0,"contact_point_centroid":[0.50437,0.06575,0.04411],"force_p95":9.80997,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.75151,"mean_force":3.47392,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50058,0.07757,0.03124]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":401.0,"contact_point_centroid":[0.52509,0.05005,0.02805],"force_p95":5.0056,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.2962,"mean_force":1.25734,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50055,0.07932,0.03126]},{"body_a":"peg","body_b":"channel_base_body","contact_count":506.0,"contact_point_centroid":[0.50563,0.10471,0.00937],"force_p95":0.57747,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56868,"phase_index":0.0,"phase_name":"approach_behind_high","phase_type":"approach","tcp_position_centroid":[0.50898,0.19182,0.22082]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_behind_high","phase_type":"approach","tcp_position_centroid":[0.49983,0.19934,0.29712]},{"body_a":"peg","body_b":"channel_base_body","contact_count":555.0,"contact_point_centroid":[0.5058,0.10458,0.00939],"force_p95":0.5757,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57647,"mean_force":0.5463,"phase_index":1.0,"phase_name":"descend_to_lateral","phase_type":"descend","tcp_position_centroid":[0.51014,0.18362,0.09211]}],"total_contact_groups":6},"final_pose_error":0.06535,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50709,-0.01068,0.0353],"final_tcp_position":[0.50131,0.01894,0.03035],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":14.212,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":533.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.1046,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.1848,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.53607,"phase_name":"approach_behind_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":538.0,"raw_peak_contact_force":3.33087,"subtask_id":"pre_push_approach","tcp_end":[0.5193,0.1849,0.14855],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14065,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":555.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.10472,0.03383],"object_pos_start":[0.50599,0.1046,0.03384],"object_to_goal_dist_end":0.18492,"object_to_goal_dist_start":0.1848,"object_z_max":0.03384,"peak_contact_force":0.52963,"phase_name":"descend_to_lateral","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":555.0,"raw_peak_contact_force":0.57647,"subtask_id":"pre_push_approach","tcp_end":[0.50321,0.18326,0.03773],"tcp_start":[0.5193,0.1849,0.14855],"tcp_to_object_dist_end":0.07868,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50709,-0.01068,0.0353],"object_pos_start":[0.50593,0.10472,0.03383],"object_to_goal_dist_end":0.06984,"object_to_goal_dist_start":0.18492,"object_z_max":0.0359,"peak_contact_force":8.80262,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1639.0,"raw_peak_contact_force":14.212,"subtask_id":"push_channel","tcp_end":[0.50131,0.01894,0.03035],"tcp_start":[0.50321,0.18326,0.03773],"tcp_to_object_dist_end":0.03058,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `314cefd2153cfe84bc0d0d2dfbeb7f4daf8feaf5f2c7ce7d396802b52a157f39`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.93237,"average_solve_count":207.0,"average_success_count":207.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_high.approach_speed":0.03965,"descend_to_lateral.descend_speed":0.02786,"push_along_channel.force_limit":68.61881,"push_along_channel.lateral_nudge":0.01352,"push_along_channel.max_push_time":19.12115,"push_along_channel.push_distance":0.20508,"push_along_channel.push_speed":0.1},"optimized_scores":{"best_composite_score":0.38537,"best_fitness_score":0.76537,"best_task_score":0.70906},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":504.0,"contact_point_centroid":[0.50189,0.02652,0.04194],"force_p95":9.46671,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.34964,"mean_force":3.65307,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49669,0.03797,0.03087]},{"body_a":"peg","body_b":"channel_base_body","contact_count":692.0,"contact_point_centroid":[0.50507,0.02721,0.00968],"force_p95":9.31739,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.35023,"mean_force":2.94686,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49638,0.07649,0.03143]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":464.0,"contact_point_centroid":[0.52514,0.01063,0.02975],"force_p95":4.23268,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.14083,"mean_force":1.24172,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49668,0.03869,0.03088]},{"body_a":"peg","body_b":"channel_base_body","contact_count":514.0,"contact_point_centroid":[0.50302,0.06749,0.00934],"force_p95":0.55715,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56339,"phase_index":0.0,"phase_name":"approach_behind_high","phase_type":"approach","tcp_position_centroid":[0.4991,0.17505,0.22225]},{"body_a":"peg","body_b":"channel_base_body","contact_count":679.0,"contact_point_centroid":[0.50312,0.06742,0.00938],"force_p95":0.55058,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55092,"mean_force":0.54664,"phase_index":1.0,"phase_name":"descend_to_lateral","phase_type":"descend","tcp_position_centroid":[0.49813,0.14845,0.0908]}],"total_contact_groups":5},"final_pose_error":0.12043,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50717,-0.04599,0.03577],"final_tcp_position":[0.49748,-0.0174,0.03037],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":14.34964,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":530.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.06748,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54756,"phase_name":"approach_behind_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":514.0,"raw_peak_contact_force":2.06903,"subtask_id":"pre_push_approach","tcp_end":[0.49987,0.15107,0.14869],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14212,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":679.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50309,0.06748,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14764,"object_z_max":0.0338,"peak_contact_force":0.54766,"phase_name":"descend_to_lateral","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":679.0,"raw_peak_contact_force":0.55092,"subtask_id":"pre_push_approach","tcp_end":[0.49901,0.14661,0.03644],"tcp_start":[0.49987,0.15107,0.14869],"tcp_to_object_dist_end":0.07933,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50717,-0.04599,0.03577],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.03501,"object_to_goal_dist_start":0.14759,"object_z_max":0.0364,"peak_contact_force":9.87676,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1660.0,"raw_peak_contact_force":14.34964,"subtask_id":"push_channel","tcp_end":[0.49748,-0.0174,0.03037],"tcp_start":[0.49901,0.14661,0.03644],"tcp_to_object_dist_end":0.03067,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7acce370299b32aeef0e4239da3e97eae076cb9602edead185a6cf774ee0bc4e`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.01105,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_high.approach_speed":0.051,"descend_to_lateral.descend_speed":0.02955,"push_along_channel.force_limit":69.96611,"push_along_channel.lateral_nudge":0.00113,"push_along_channel.max_push_time":6.08808,"push_along_channel.push_distance":0.18574,"push_along_channel.push_speed":0.09997},"optimized_scores":{"best_composite_score":0.30314,"best_fitness_score":0.68314,"best_task_score":0.71737},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":559.0,"contact_point_centroid":[0.50244,0.07127,0.04199],"force_p95":9.26724,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.04451,"mean_force":3.12466,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49765,0.08282,0.03098]},{"body_a":"peg","body_b":"channel_base_body","contact_count":679.0,"contact_point_centroid":[0.50541,0.07147,0.0097],"force_p95":8.66224,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.70641,"mean_force":2.8557,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49737,0.12089,0.03157]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":452.0,"contact_point_centroid":[0.52507,0.05289,0.02649],"force_p95":3.53735,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.49923,"mean_force":1.10557,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49767,0.08123,0.03097]},{"body_a":"peg","body_b":"channel_base_body","contact_count":478.0,"contact_point_centroid":[0.50364,0.11169,0.00936],"force_p95":0.61914,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56146,"phase_index":0.0,"phase_name":"approach_behind_high","phase_type":"approach","tcp_position_centroid":[0.50233,0.19516,0.22156]},{"body_a":"peg","body_b":"channel_base_body","contact_count":625.0,"contact_point_centroid":[0.50356,0.11158,0.00942],"force_p95":0.6002,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65056,"mean_force":0.54248,"phase_index":1.0,"phase_name":"descend_to_lateral","phase_type":"descend","tcp_position_centroid":[0.50186,0.19036,0.0914]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_behind_high","phase_type":"approach","tcp_position_centroid":[0.49979,0.19957,0.29905]}],"total_contact_groups":6},"final_pose_error":0.10018,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50702,-0.003,0.03571],"final_tcp_position":[0.49845,0.02597,0.03047],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":12.04451,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":500.0,"n_steps_budget":1000.0,"object_pos_end":[0.5037,0.11174,0.03382],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.5455,"phase_name":"approach_behind_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":494.0,"raw_peak_contact_force":2.06328,"subtask_id":"pre_push_approach","tcp_end":[0.5062,0.1914,0.14914],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14018,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":625.0,"n_steps_budget":1000.0,"object_pos_end":[0.50367,0.11173,0.03391],"object_pos_start":[0.5037,0.11174,0.03382],"object_to_goal_dist_end":0.19186,"object_to_goal_dist_start":0.19187,"object_z_max":0.0341,"peak_contact_force":0.53041,"phase_name":"descend_to_lateral","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":625.0,"raw_peak_contact_force":0.65056,"subtask_id":"pre_push_approach","tcp_end":[0.50003,0.19029,0.03683],"tcp_start":[0.5062,0.1914,0.14914],"tcp_to_object_dist_end":0.07869,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50702,-0.003,0.03571],"object_pos_start":[0.50367,0.11173,0.03391],"object_to_goal_dist_end":0.07744,"object_to_goal_dist_start":0.19186,"object_z_max":0.03602,"peak_contact_force":6.96715,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1690.0,"raw_peak_contact_force":12.04451,"subtask_id":"push_channel","tcp_end":[0.49845,0.02597,0.03047],"tcp_start":[0.50003,0.19029,0.03683],"tcp_to_object_dist_end":0.03066,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```