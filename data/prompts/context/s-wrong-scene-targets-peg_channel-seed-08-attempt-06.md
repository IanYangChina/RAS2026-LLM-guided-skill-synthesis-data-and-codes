## Search State

- **Seed**: 8
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 11 | -0.1959 | 0.00 | ❌ rejected |
| 5 | approach → align → contact → push | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 12 | -0.1377 | 0.12 | ❌ rejected |
| 4 | approach → align → contact → push | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 12 | -0.0189 | 0.22 | ✅ accepted |
| 3 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 0.4630 | 0.18 | ✅ accepted |
| 2 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 0.0326 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`
- Frozen object start: [0.48615778212844485, -0.04101785253296597, 0.04]
- Frozen task target: [0.5, 0.2, 0.3]
- Goal object position: (0.5, 0.2, 0.3)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48615778212844485, -0.04101785253296597, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.48615778212844485, 0.11898214746703403, 0.04)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.48615778212844485, 0.11898214746703403, 0.04]
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
  frozen_object_starts: {'peg': [0.48615778212844485, -0.04101785253296597, 0.04]}
  frozen_targets: {'channel_exit': [0.5, 0.2, 0.3]}
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
| `object` | offset from object initial position (0.48615778212844485, -0.04101785253296597, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.2, 0.3) | final destination targets |
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

## Current Skill (Q=-0.196) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.08
  weight: 0.3
- id: push_progress
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_prepush
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.08
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: pre_contact
- id: align_tool
  type: align
  generator: joint_interpolation
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_contact
- id: contact_engage
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.02
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 2.0
      - 15.0
      default: 6.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_contact
- id: push_channel
  type: push
  generator: linear_cartesian
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
      distance: 0.18
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.12
      - 0.2
      default: 0.18
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_force_guard_threshold:
      type: scalar
      range:
      - 20.0
      - 35.0
      default: 30.0
      binds_to:
      - path: guards.push_force_limit.threshold
        mode: replace
    push_pose_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.12
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    retry_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: retry.offset.x
        mode: replace
    retry_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.0
      default: -0.005
      binds_to:
      - path: retry.offset.y
        mode: replace
    retry_offset_z:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: retry.offset.z
        mode: replace
  guards:
  - id: push_force_limit
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - -0.005
    - 0.0
  subtask_id: push_progress

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_prepush** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.08], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **align_tool** (`align`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
- **contact_engage** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.02, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.18, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_force_guard_threshold: status=consumed; consumers=guards.push_force_limit.threshold (replace)
    - push_pose_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - retry_offset_x: status=consumed; consumers=retry.offset.x (replace)
    - retry_offset_y: status=consumed; consumers=retry.offset.y (replace)
    - retry_offset_z: status=consumed; consumers=retry.offset.z (replace)
  - guards:
    - id=push_force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=30.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.005, 0.0]

## Design Metrics

- **Composite score**: -0.196
- **task_score** (E): 0.000
- **fitness_score**: 0.051  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_precontact | 1.00 | 1.00 | 0.1848 |
| contact_make | 1.00 | 1.00 | 0.0775 |
| push_channel | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_precontact | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.514, 0.142, 0.128) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.542 | 3.526 |
| contact_make | contact | 1.00 / force_exceeded | (0.514, 0.142, 0.128)→(0.502, 0.111, 0.059) | (0.503, 0.080, 0.034)→(0.503, 0.087, 0.032) | 0.160→0.168 | 1.00 / 2.000 | 68.760 | 44.073 |
| push_channel | push | 0.00 / guard_failure | (0.502, 0.111, 0.059)→(0.502, 0.111, 0.059) | (0.503, 0.087, 0.032)→(0.503, 0.088, 0.032) | 0.168→0.168 | 1.00 / 2.000 | 29.856 | 56.923 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.105
- phase_breakdown.pre_contact_score: 0.351
- phase_breakdown.push_progress_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.063
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.201
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 5.3
- **Final σ (mean)**: 0.294


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
{"anchors":[{"name":"object","value":[0.48616,-0.04102,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,-0.04102,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.16456,"average_solve_count":79.0,"average_success_count":79.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_precontact.approach_speed":0.23816,"approach_precontact.approach_tolerance":0.01127,"contact_make.contact_force_threshold":11.40383,"contact_make.contact_speed":0.02741,"push_channel.push_distance":0.16149,"push_channel.push_force_guard_threshold":35.05553,"push_channel.push_pose_tolerance":0.01987,"push_channel.push_speed":0.11048,"push_channel.retry_offset_x":0.00419,"push_channel.retry_offset_y":-0.01673,"push_channel.retry_offset_z":-0.00658},"optimized_scores":{"best_composite_score":-0.18351,"best_fitness_score":0.06316,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"world","contact_count":5.0,"contact_point_centroid":[0.49594,0.13352,-6e-05],"force_p95":33.69018,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.11312,"mean_force":16.68189,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48843,0.15311,0.0676]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.48886,0.15346,0.05597],"force_p95":32.95782,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.95705,"mean_force":13.86467,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48843,0.15313,0.06761]},{"body_a":"peg","body_b":"channel_base_body","contact_count":407.0,"contact_point_centroid":[0.49628,0.11912,0.00942],"force_p95":0.62607,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55888,"phase_index":0.0,"phase_name":"approach_precontact","phase_type":"approach","tcp_position_centroid":[0.48653,0.19484,0.19946]},{"body_a":"peg","body_b":"world","contact_count":23.0,"contact_point_centroid":[0.49596,0.13356,-0.00019],"force_p95":0.93378,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.05554,"mean_force":0.54444,"phase_index":1.0,"phase_name":"contact_make","phase_type":"contact","tcp_position_centroid":[0.48834,0.1542,0.06975]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_precontact","phase_type":"approach","tcp_position_centroid":[0.50462,0.21212,0.29582]},{"body_a":"peg","body_b":"channel_base_body","contact_count":356.0,"contact_point_centroid":[0.49572,0.11939,0.00944],"force_p95":0.5998,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63807,"mean_force":0.52675,"phase_index":1.0,"phase_name":"contact_make","phase_type":"contact","tcp_position_centroid":[0.48559,0.1666,0.09927]}],"total_contact_groups":6},"final_pose_error":0.16084,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4955,0.1434,0.02886],"final_tcp_position":[0.48839,0.15276,0.0673],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":75.11664,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":432.0,"n_steps_budget":600.0,"object_pos_end":[0.49601,0.11897,0.03393],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.1991,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.53403,"phase_name":"approach_precontact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":431.0,"raw_peak_contact_force":2.24822,"subtask_id":"pre_contact","tcp_end":[0.485,0.17905,0.12971],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1136,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":373.0,"n_steps_budget":1000.0,"object_pos_end":[0.49586,0.14241,0.02944],"object_pos_start":[0.49601,0.11897,0.03393],"object_to_goal_dist_end":0.2227,"object_to_goal_dist_start":0.1991,"object_z_max":0.03399,"peak_contact_force":75.11664,"phase_name":"contact_make","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":379.0,"raw_peak_contact_force":1.05554,"subtask_id":"pre_contact","tcp_end":[0.48854,0.15341,0.06788],"tcp_start":[0.485,0.17905,0.12971],"tcp_to_object_dist_end":0.04065,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":6.0,"n_steps_budget":930.0,"object_pos_end":[0.49557,0.14326,0.02905],"object_pos_start":[0.49586,0.14241,0.02944],"object_to_goal_dist_end":0.22358,"object_to_goal_dist_start":0.2227,"object_z_max":0.02944,"peak_contact_force":10.08267,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":11.0,"raw_peak_contact_force":36.11312,"subtask_id":"push_progress","tcp_end":[0.48839,0.15276,0.0673],"tcp_start":[0.48839,0.15284,0.06737],"tcp_to_object_dist_end":0.04006,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0a7722137b05abd45e72adac5a0a8f18d70c24ddc36cf4c70c52ed7e5618005d`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,-0.09705,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,-0.09705,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.63158,"average_solve_count":57.0,"average_success_count":57.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_precontact.approach_speed":0.35151,"approach_precontact.approach_tolerance":0.01113,"contact_make.contact_force_threshold":11.61595,"contact_make.contact_speed":0.05264,"push_channel.push_distance":0.15166,"push_channel.push_force_guard_threshold":34.64081,"push_channel.push_pose_tolerance":0.01767,"push_channel.push_speed":0.07509,"push_channel.retry_offset_x":0.00036,"push_channel.retry_offset_y":-0.0101,"push_channel.retry_offset_z":-0.00063},"optimized_scores":{"best_composite_score":-0.20139,"best_fitness_score":0.04528,"best_task_score":1e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.50909,0.15517,-0.00013],"force_p95":66.52608,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":68.15451,"mean_force":53.89526,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50788,0.09337,0.05432]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50916,0.15532,-0.0],"force_p95":60.06229,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":60.06229,"mean_force":60.06229,"phase_index":1.0,"phase_name":"contact_make","phase_type":"contact","tcp_position_centroid":[0.50795,0.09351,0.05455]},{"body_a":"peg","body_b":"channel_base_body","contact_count":491.0,"contact_point_centroid":[0.50577,0.06297,0.00935],"force_p95":0.57586,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.57412,"phase_index":0.0,"phase_name":"approach_precontact","phase_type":"approach","tcp_position_centroid":[0.50707,0.16824,0.20228]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_precontact","phase_type":"approach","tcp_position_centroid":[0.50345,0.2203,0.2887]},{"body_a":"peg","body_b":"channel_base_body","contact_count":377.0,"contact_point_centroid":[0.50591,0.06309,0.00938],"force_p95":0.55144,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55501,"mean_force":0.54656,"phase_index":1.0,"phase_name":"contact_make","phase_type":"contact","tcp_position_centroid":[0.51578,0.11043,0.09052]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.51575,0.05119,0.00938],"force_p95":0.55249,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55286,"mean_force":0.5493,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50788,0.09337,0.05432]}],"total_contact_groups":6},"final_pose_error":0.15147,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50596,0.06294,0.03381],"final_tcp_position":[0.50783,0.09326,0.05418],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":68.15451,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":519.0,"n_steps_budget":600.0,"object_pos_end":[0.50596,0.06295,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54802,"phase_name":"approach_precontact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":525.0,"raw_peak_contact_force":3.88411,"subtask_id":"pre_contact","tcp_end":[0.52492,0.12704,0.1275],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11509,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":377.0,"n_steps_budget":1000.0,"object_pos_end":[0.50603,0.06298,0.03381],"object_pos_start":[0.50596,0.06295,0.03381],"object_to_goal_dist_end":0.14324,"object_to_goal_dist_start":0.1432,"object_z_max":0.03381,"peak_contact_force":60.06229,"phase_name":"contact_make","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":378.0,"raw_peak_contact_force":60.06229,"subtask_id":"pre_contact","tcp_end":[0.50792,0.09344,0.05439],"tcp_start":[0.52492,0.12704,0.1275],"tcp_to_object_dist_end":0.03682,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50602,0.06295,0.03381],"object_pos_start":[0.50603,0.06298,0.03381],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14324,"object_z_max":0.03381,"peak_contact_force":41.66111,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":68.15451,"subtask_id":"push_progress","tcp_end":[0.50783,0.09326,0.05418],"tcp_start":[0.50785,0.09331,0.05424],"tcp_to_object_dist_end":0.03657,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `bf9c239495ea25cc1b534d0795871edaef0fee72244885088104a44eb548c1a2`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,-0.10339,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,-0.10339,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.3,"average_solve_count":40.0,"average_success_count":40.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_precontact.approach_speed":0.29636,"approach_precontact.approach_tolerance":0.01603,"contact_make.contact_force_threshold":9.42121,"contact_make.contact_speed":0.12117,"push_channel.push_distance":0.1634,"push_channel.push_force_guard_threshold":30.58421,"push_channel.push_pose_tolerance":0.01887,"push_channel.push_speed":0.06292,"push_channel.retry_offset_x":-0.01007,"push_channel.retry_offset_y":-0.01692,"push_channel.retry_offset_z":0.00325},"optimized_scores":{"best_composite_score":-0.20291,"best_fitness_score":0.04376,"best_task_score":0.00011},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.51119,0.14923,-1e-05],"force_p95":71.10223,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":71.10223,"mean_force":71.10223,"phase_index":1.0,"phase_name":"contact_make","phase_type":"contact","tcp_position_centroid":[0.50989,0.0874,0.0545]},{"body_a":"world","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.51107,0.14905,-0.00017],"force_p95":64.62081,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":66.50185,"mean_force":50.67232,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50978,0.08723,0.05422]},{"body_a":"peg","body_b":"channel_base_body","contact_count":502.0,"contact_point_centroid":[0.50581,0.05662,0.00935],"force_p95":0.60132,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.57824,"phase_index":0.0,"phase_name":"approach_precontact","phase_type":"approach","tcp_position_centroid":[0.51037,0.16495,0.20204]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_precontact","phase_type":"approach","tcp_position_centroid":[0.50277,0.22234,0.28632]},{"body_a":"peg","body_b":"channel_base_body","contact_count":328.0,"contact_point_centroid":[0.50612,0.05667,0.00938],"force_p95":0.55348,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55957,"mean_force":0.54653,"phase_index":1.0,"phase_name":"contact_make","phase_type":"contact","tcp_position_centroid":[0.52009,0.10444,0.09038]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.52232,0.05868,0.00939],"force_p95":0.54649,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54683,"mean_force":0.54408,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50978,0.08723,0.05422]}],"total_contact_groups":6},"final_pose_error":0.16319,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50617,0.05655,0.03383],"final_tcp_position":[0.5097,0.0871,0.05404],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":71.10223,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":531.0,"n_steps_budget":600.0,"object_pos_end":[0.50614,0.05664,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13692,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.54498,"phase_name":"approach_precontact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":539.0,"raw_peak_contact_force":4.44541,"subtask_id":"pre_contact","tcp_end":[0.53131,0.12111,0.12718],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11625,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":328.0,"n_steps_budget":600.0,"object_pos_end":[0.50619,0.05666,0.03383],"object_pos_start":[0.50614,0.05664,0.03378],"object_to_goal_dist_end":0.13694,"object_to_goal_dist_start":0.13692,"object_z_max":0.03383,"peak_contact_force":71.10223,"phase_name":"contact_make","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":329.0,"raw_peak_contact_force":71.10223,"subtask_id":"pre_contact","tcp_end":[0.50984,0.08731,0.05431],"tcp_start":[0.53131,0.12111,0.12718],"tcp_to_object_dist_end":0.03705,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.5062,0.05662,0.03383],"object_pos_start":[0.50619,0.05666,0.03383],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.13694,"object_z_max":0.03383,"peak_contact_force":37.8236,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":66.50185,"subtask_id":"push_progress","tcp_end":[0.5097,0.0871,0.05404],"tcp_start":[0.50973,0.08715,0.05412],"tcp_to_object_dist_end":0.03674,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```