## Search State

- **Seed**: 8
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → align → descend → push | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 12 | -0.3108 | 0.18 | ❌ rejected |
| 8 | approach → align → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 10 | -0.5354 | 0.00 | ❌ rejected |
| 7 | approach → align → contact → push | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | -0.1385 | 0.01 | ❌ rejected |
| 6 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 11 | -0.1959 | 0.00 | ❌ rejected |
| 5 | approach → align → contact → push | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 12 | -0.1377 | 0.12 | ❌ rejected |

**Proposal policy**: task_score is 0.18 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.311) — your mutation base

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

- **Composite score**: -0.311
- **task_score** (E): 0.177
- **fitness_score**: 0.349  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.660

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_prepush | 1.00 | 1.00 | 0.1959 |
| align_tool | 1.00 | 1.00 | 0.0247 |
| descend_to_peg | 1.00 | 1.00 | 0.0882 |
| push_channel | 0.00 | 1.00 | 0.0002 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_prepush | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.115, 0.127) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.533 | 3.526 |
| align_tool | align | 1.00 / step_budget | (0.513, 0.115, 0.127)→(0.504, 0.137, 0.122) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.554 | 0.587 |
| descend_to_peg | descend | 1.00 / step_budget | (0.504, 0.137, 0.122)→(0.504, 0.097, 0.045) | (0.503, 0.080, 0.034)→(0.501, 0.056, 0.033) | 0.160→0.136 | 1.00 / 1.667 | 81.460 | 344.225 |
| push_channel | push | 0.00 / guard_failure | (0.501, 0.020, 0.042)→(0.501, 0.020, 0.042) | (0.501, 0.056, 0.033)→(0.502, -0.011, 0.028) | 0.136→0.075 | 1.00 / 3.000 | 46.090 | 62.016 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.874
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.362
- phase_score: 0.669
- phase_breakdown.pre_contact_score: 0.204
- phase_breakdown.push_progress_score: 0.868

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.546
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.362
- **Median Q (composite search score)**: -0.202
- **K-run variance**: 0.0481
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.287


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.09091,"average_solve_count":44.0,"average_success_count":44.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_tool.align_speed":0.21931,"approach_prepush.approach_speed":0.223,"approach_prepush.approach_tolerance":0.01231,"descend_to_peg.descend_speed":0.1115,"descend_to_peg.descend_tolerance":0.01656,"push_channel.push_distance":0.16559,"push_channel.push_force_guard_threshold":27.99054,"push_channel.push_pose_tolerance":0.02124,"push_channel.push_speed":0.07402,"push_channel.retry_offset_x":0.00424,"push_channel.retry_offset_y":-0.01294,"push_channel.retry_offset_z":-0.00044},"optimized_scores":{"best_composite_score":-0.61695,"best_fitness_score":0.04305,"best_task_score":0.01061},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":77.0,"contact_point_centroid":[0.50026,0.13525,0.05027],"force_p95":246.18589,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":254.70394,"mean_force":161.55422,"phase_index":2.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49002,0.13942,0.05196]},{"body_a":"peg","body_b":"channel_base_body","contact_count":218.0,"contact_point_centroid":[0.49888,0.11918,0.0086],"force_p95":199.34871,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":217.04878,"mean_force":51.84756,"phase_index":2.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.4823,0.15175,0.0794]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50605,0.13243,0.04507],"force_p95":117.80134,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":117.88892,"mean_force":116.6444,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4965,0.13769,0.04474]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49589,0.11886,0.00566],"force_p95":100.36732,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":100.54501,"mean_force":92.89457,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4965,0.13769,0.04474]},{"body_a":"peg","body_b":"world","contact_count":28.0,"contact_point_centroid":[0.50025,0.12814,-0.00041],"force_p95":65.96929,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":67.95356,"mean_force":47.51492,"phase_index":2.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49402,0.13806,0.04644]},{"body_a":"peg","body_b":"world","contact_count":3.0,"contact_point_centroid":[0.50078,0.12717,-0.00057],"force_p95":40.16842,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.33377,"mean_force":27.53198,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4965,0.13769,0.04474]},{"body_a":"peg","body_b":"channel_base_body","contact_count":442.0,"contact_point_centroid":[0.49629,0.11912,0.0094],"force_p95":0.61955,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55895,"phase_index":0.0,"phase_name":"approach_prepush","phase_type":"approach","tcp_position_centroid":[0.49115,0.17488,0.21011]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_prepush","phase_type":"approach","tcp_position_centroid":[0.49939,0.19885,0.2967]},{"body_a":"peg","body_b":"channel_base_body","contact_count":307.0,"contact_point_centroid":[0.49598,0.11921,0.00946],"force_p95":0.59987,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64701,"mean_force":0.53871,"phase_index":1.0,"phase_name":"align_tool","phase_type":"align","tcp_position_centroid":[0.47751,0.16271,0.12504]}],"total_contact_groups":9},"final_pose_error":0.16562,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50102,0.1162,0.02773],"final_tcp_position":[0.49663,0.13773,0.04477],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":254.70394,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":467.0,"n_steps_budget":600.0,"object_pos_end":[0.49604,0.11913,0.03395],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19926,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.51129,"phase_name":"approach_prepush","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":466.0,"raw_peak_contact_force":2.24822,"subtask_id":"pre_contact","tcp_end":[0.4842,0.15204,0.1293],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10157,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":307.0,"n_steps_budget":600.0,"object_pos_end":[0.49606,0.11915,0.03392],"object_pos_start":[0.49604,0.11913,0.03395],"object_to_goal_dist_end":0.19929,"object_to_goal_dist_start":0.19926,"object_z_max":0.03408,"peak_contact_force":0.57166,"phase_name":"align_tool","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":307.0,"raw_peak_contact_force":0.64701,"subtask_id":"pre_contact","tcp_end":[0.47361,0.17247,0.12438],"tcp_start":[0.4842,0.15204,0.1293],"tcp_to_object_dist_end":0.10737,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":218.0,"n_steps_budget":630.0,"object_pos_end":[0.50114,0.11623,0.02765],"object_pos_start":[0.49606,0.11915,0.03392],"object_to_goal_dist_end":0.19662,"object_to_goal_dist_start":0.19929,"object_z_max":0.03402,"peak_contact_force":244.37879,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":323.0,"raw_peak_contact_force":254.70394,"subtask_id":"pre_contact","tcp_end":[0.49645,0.1377,0.04476],"tcp_start":[0.47361,0.17247,0.12438],"tcp_to_object_dist_end":0.02785,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50107,0.11621,0.02765],"object_pos_start":[0.50114,0.11623,0.02765],"object_to_goal_dist_end":0.1966,"object_to_goal_dist_start":0.19662,"object_z_max":0.02767,"peak_contact_force":117.88892,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":117.88892,"subtask_id":"push_progress","tcp_end":[0.49663,0.13773,0.04477],"tcp_start":[0.49655,0.1377,0.04473],"tcp_to_object_dist_end":0.02786,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47414,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_tool.align_speed":0.29592,"approach_prepush.approach_speed":0.4559,"approach_prepush.approach_tolerance":0.01287,"descend_to_peg.descend_speed":0.07751,"descend_to_peg.descend_tolerance":0.01685,"push_channel.push_distance":0.17683,"push_channel.push_force_guard_threshold":33.42675,"push_channel.push_pose_tolerance":0.01929,"push_channel.push_speed":0.04377,"push_channel.retry_offset_x":-0.0032,"push_channel.retry_offset_y":-0.0044,"push_channel.retry_offset_z":0.00428},"optimized_scores":{"best_composite_score":-0.11402,"best_fitness_score":0.54598,"best_task_score":0.3617},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52503,0.08034,0.05999],"force_p95":325.7497,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":330.38984,"mean_force":273.98078,"phase_index":2.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50733,0.08009,0.04566]},{"body_a":"peg","body_b":"channel_base_body","contact_count":187.0,"contact_point_centroid":[0.50721,0.06151,0.00909],"force_p95":140.4255,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":175.75753,"mean_force":20.96273,"phase_index":2.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51017,0.10103,0.08189]},{"body_a":"attachment","body_b":"peg","contact_count":36.0,"contact_point_centroid":[0.51283,0.07622,0.05484],"force_p95":172.22077,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":175.3589,"mean_force":106.27923,"phase_index":2.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50746,0.08582,0.05526]},{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.51183,-0.10063,0.01032],"force_p95":34.71771,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.57191,"mean_force":22.47809,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50336,-0.03892,0.03996]},{"body_a":"attachment","body_b":"peg","contact_count":15.0,"contact_point_centroid":[0.50317,-0.04847,0.04018],"force_p95":31.70072,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.78375,"mean_force":9.77492,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50335,-0.03674,0.03995]},{"body_a":"peg","body_b":"channel_base_body","contact_count":265.0,"contact_point_centroid":[0.5007,-0.06019,0.00837],"force_p95":2.27297,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.13963,"mean_force":0.81054,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50362,0.0127,0.0403]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52503,-0.0469,0.02427],"force_p95":6.66616,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.72125,"mean_force":1.78066,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50335,-0.02322,0.03995]},{"body_a":"peg","body_b":"channel_base_body","contact_count":520.0,"contact_point_centroid":[0.50578,0.063,0.00936],"force_p95":0.56846,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.57257,"phase_index":0.0,"phase_name":"approach_prepush","phase_type":"approach","tcp_position_centroid":[0.51179,0.14782,0.20877]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_prepush","phase_type":"approach","tcp_position_centroid":[0.50003,0.19759,0.29572]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.47496,-0.06645,0.05655],"force_p95":1.0037,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.01355,"mean_force":0.91502,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5038,0.04537,0.04053]},{"body_a":"peg","body_b":"channel_base_body","contact_count":321.0,"contact_point_centroid":[0.50598,0.06292,0.00938],"force_p95":0.55136,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55501,"mean_force":0.54657,"phase_index":1.0,"phase_name":"align_tool","phase_type":"align","tcp_position_centroid":[0.51863,0.11164,0.12181]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52504,0.07975,0.05999],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.507,0.07948,0.04468]}],"total_contact_groups":12},"final_pose_error":0.05785,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50697,-0.0769,0.02688],"final_tcp_position":[0.50332,-0.0397,0.03991],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":330.38984,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":548.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.06294,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54018,"phase_name":"approach_prepush","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":554.0,"raw_peak_contact_force":3.88411,"subtask_id":"pre_contact","tcp_end":[0.52434,0.09934,0.12651],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10127,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":321.0,"n_steps_budget":600.0,"object_pos_end":[0.50595,0.06295,0.03381],"object_pos_start":[0.50599,0.06294,0.03381],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.1432,"object_z_max":0.03381,"peak_contact_force":0.54576,"phase_name":"align_tool","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":321.0,"raw_peak_contact_force":0.55501,"subtask_id":"pre_contact","tcp_end":[0.51579,0.12221,0.12109],"tcp_start":[0.52434,0.09934,0.12651],"tcp_to_object_dist_end":0.10596,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":187.0,"n_steps_budget":870.0,"object_pos_end":[0.50294,0.03752,0.04051],"object_pos_start":[0.50595,0.06295,0.03381],"object_to_goal_dist_end":0.11756,"object_to_goal_dist_start":0.14321,"object_z_max":0.04005,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":227.0,"raw_peak_contact_force":330.38984,"subtask_id":"pre_contact","tcp_end":[0.50713,0.07962,0.04488],"tcp_start":[0.51579,0.12221,0.12109],"tcp_to_object_dist_end":0.04253,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":312.0,"n_steps_budget":1000.0,"object_pos_end":[0.50692,-0.07642,0.0266],"object_pos_start":[0.50294,0.03752,0.04051],"object_to_goal_dist_end":0.0155,"object_to_goal_dist_start":0.11756,"object_z_max":0.04298,"peak_contact_force":19.72002,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":296.0,"raw_peak_contact_force":35.57191,"subtask_id":"push_progress","tcp_end":[0.50332,-0.0397,0.03991],"tcp_start":[0.50335,-0.03953,0.03995],"tcp_to_object_dist_end":0.03922,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58586,"average_solve_count":99.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_tool.align_speed":0.22061,"approach_prepush.approach_speed":0.20676,"approach_prepush.approach_tolerance":0.01433,"descend_to_peg.descend_speed":0.08246,"descend_to_peg.descend_tolerance":0.01828,"push_channel.push_distance":0.14355,"push_channel.push_force_guard_threshold":28.94638,"push_channel.push_pose_tolerance":0.01814,"push_channel.push_speed":0.05643,"push_channel.retry_offset_x":0.00228,"push_channel.retry_offset_y":-0.00037,"push_channel.retry_offset_z":-0.00843},"optimized_scores":{"best_composite_score":-0.20153,"best_fitness_score":0.45847,"best_task_score":0.15749},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":74.0,"contact_point_centroid":[0.52512,0.07591,0.05996],"force_p95":426.22421,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":447.58153,"mean_force":383.11082,"phase_index":2.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50896,0.07575,0.04931]},{"body_a":"peg","body_b":"channel_base_body","contact_count":229.0,"contact_point_centroid":[0.50553,0.05108,0.00929],"force_p95":130.99183,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":151.85479,"mean_force":14.70559,"phase_index":2.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51324,0.09121,0.07506]},{"body_a":"attachment","body_b":"peg","contact_count":34.0,"contact_point_centroid":[0.51377,0.06953,0.05544],"force_p95":145.56235,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":151.55866,"mean_force":95.73512,"phase_index":2.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50978,0.07988,0.05545]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.5124,-0.1003,0.0294],"force_p95":31.72362,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.58753,"mean_force":18.1267,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50385,-0.03707,0.04082]},{"body_a":"attachment","body_b":"peg","contact_count":117.0,"contact_point_centroid":[0.50242,-0.00739,0.04176],"force_p95":24.22174,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.77615,"mean_force":4.69125,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.504,0.00418,0.04105]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":38.0,"contact_point_centroid":[0.47463,-0.0487,0.02749],"force_p95":18.18223,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.93771,"mean_force":7.16657,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50401,0.00879,0.04107]},{"body_a":"peg","body_b":"channel_base_body","contact_count":232.0,"contact_point_centroid":[0.49947,-0.02276,0.0091],"force_p95":8.31014,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.97642,"mean_force":2.17053,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50444,0.02138,0.04165]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":31.0,"contact_point_centroid":[0.52516,0.0239,0.02568],"force_p95":6.34193,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.32249,"mean_force":1.50235,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50491,0.0491,0.04229]},{"body_a":"peg","body_b":"channel_base_body","contact_count":558.0,"contact_point_centroid":[0.50586,0.05664,0.00935],"force_p95":0.6021,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.57508,"phase_index":0.0,"phase_name":"approach_prepush","phase_type":"approach","tcp_position_centroid":[0.51535,0.14378,0.20708]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_prepush","phase_type":"approach","tcp_position_centroid":[0.50021,0.19718,0.29516]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52503,0.07332,0.05999],"force_p95":2.64093,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.10697,"mean_force":0.77674,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50739,0.07311,0.04548]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47495,0.00958,0.05095],"force_p95":1.37171,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.40958,"mean_force":1.07228,"phase_index":2.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50828,0.0747,0.04777]},{"body_a":"peg","body_b":"channel_base_body","contact_count":324.0,"contact_point_centroid":[0.5062,0.05651,0.00938],"force_p95":0.55672,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55937,"mean_force":0.54655,"phase_index":1.0,"phase_name":"align_tool","phase_type":"align","tcp_position_centroid":[0.5253,0.10539,0.12052]}],"total_contact_groups":13},"final_pose_error":0.03322,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49861,-0.07376,0.02823],"final_tcp_position":[0.50379,-0.03768,0.04076],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":447.58153,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":587.0,"n_steps_budget":660.0,"object_pos_end":[0.50616,0.05663,0.03379],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.54628,"phase_name":"approach_prepush","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":595.0,"raw_peak_contact_force":4.44541,"subtask_id":"pre_contact","tcp_end":[0.5309,0.09276,0.12529],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10143,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":324.0,"n_steps_budget":600.0,"object_pos_end":[0.5061,0.0566,0.03379],"object_pos_start":[0.50616,0.05663,0.03379],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.1369,"object_z_max":0.03379,"peak_contact_force":0.54555,"phase_name":"align_tool","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":324.0,"raw_peak_contact_force":0.55937,"subtask_id":"pre_contact","tcp_end":[0.52257,0.11614,0.11977],"tcp_start":[0.5309,0.09276,0.12529],"tcp_to_object_dist_end":0.10587,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":239.0,"n_steps_budget":840.0,"object_pos_end":[0.49953,0.01413,0.03218],"object_pos_start":[0.5061,0.0566,0.03379],"object_to_goal_dist_end":0.09446,"object_to_goal_dist_start":0.13688,"object_z_max":0.04076,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":341.0,"raw_peak_contact_force":447.58153,"subtask_id":"pre_contact","tcp_end":[0.50751,0.07322,0.04567],"tcp_start":[0.52257,0.11614,0.11977],"tcp_to_object_dist_end":0.06113,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":291.0,"n_steps_budget":1000.0,"object_pos_end":[0.4985,-0.07334,0.0283],"object_pos_start":[0.49953,0.01413,0.03218],"object_to_goal_dist_end":0.01354,"object_to_goal_dist_start":0.09446,"object_z_max":0.03218,"peak_contact_force":0.66231,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":426.0,"raw_peak_contact_force":32.58753,"subtask_id":"push_progress","tcp_end":[0.50379,-0.03768,0.04076],"tcp_start":[0.50383,-0.03751,0.0408],"tcp_to_object_dist_end":0.03814,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```