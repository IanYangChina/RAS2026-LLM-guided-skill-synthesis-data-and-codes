## Search State

- **Seed**: 8
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → align → contact → push | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | -0.2880 | 0.00 | ❌ rejected |
| 11 | approach → align → descend → push | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 12 | -0.5518 | 0.00 | ❌ rejected |
| 10 | approach → align → descend → push | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 12 | -0.2013 | 0.30 | ✅ accepted |
| 9 | approach → align → descend → push | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 12 | -0.3108 | 0.18 | ❌ rejected |
| 8 | approach → align → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 10 | -0.5354 | 0.00 | ❌ rejected |

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

## Current Skill (Q=-0.288) — your mutation base

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
- id: descend_to_peg
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.02
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    descend_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
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
      - 25.0
      - 40.0
      default: 35.0
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
    threshold: 35.0
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
- **descend_to_peg** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.02, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
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
    - id=push_force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=35.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.005, 0.0]

## Design Metrics

- **Composite score**: -0.288
- **task_score** (E): 0.004
- **fitness_score**: 0.222  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_prepush | 1.00 | 1.00 | 0.1883 |
| align_tool | 1.00 | 1.00 | 0.0249 |
| contact_peg | 0.00 | 1.00 | 0.0247 |
| push_channel | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_prepush | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.133, 0.127) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.528 | 3.526 |
| align_tool | align | 1.00 / step_budget | (0.513, 0.133, 0.127)→(0.503, 0.156, 0.122) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.541 | 0.586 |
| contact_peg | contact | 0.00 / guard_failure | (0.495, 0.122, 0.082)→(0.499, 0.107, 0.062) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.667 | 6.837 | 17.696 |
| push_channel | push | 0.00 / guard_failure | (0.498, 0.101, 0.061)→(0.498, 0.101, 0.061) | (0.503, 0.080, 0.034)→(0.503, 0.079, 0.034) | 0.160→0.159 | 1.00 / 2.000 | 20.681 | 42.764 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.011
- alignment_error: None
- force_efficiency: 0.189
- terminal_score: 0.008
- phase_score: 0.383
- phase_breakdown.contact_peg_score: 1.000
- phase_breakdown.pre_contact_score: 0.595
- phase_breakdown.push_progress_score: 0.009

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.233
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.008
- **Median Q (composite search score)**: -0.293
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.487


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.61475,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_tool.align_speed":0.20257,"approach_prepush.approach_speed":0.24594,"approach_prepush.approach_tolerance":0.00923,"contact_peg.contact_force_threshold":6.40783,"contact_peg.contact_speed":0.02008,"push_channel.push_distance":0.17466,"push_channel.push_force_guard_threshold":39.83792,"push_channel.push_pose_tolerance":0.01724,"push_channel.push_speed":0.02173},"optimized_scores":{"best_composite_score":-0.27699,"best_fitness_score":0.23301,"best_task_score":0.00829},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":53.0,"contact_point_centroid":[0.49516,0.11395,0.00946],"force_p95":39.06999,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.53571,"mean_force":10.26756,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4814,0.14035,0.06428]},{"body_a":"attachment","body_b":"peg","contact_count":17.0,"contact_point_centroid":[0.4917,0.13485,0.0589],"force_p95":39.40201,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.16094,"mean_force":30.47122,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48073,0.1337,0.06336]},{"body_a":"peg","body_b":"channel_base_body","contact_count":430.0,"contact_point_centroid":[0.49623,0.11907,0.00939],"force_p95":0.60821,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56068,"phase_index":0.0,"phase_name":"approach_prepush","phase_type":"approach","tcp_position_centroid":[0.4912,0.18436,0.21036]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_prepush","phase_type":"approach","tcp_position_centroid":[0.49941,0.19915,0.29671]},{"body_a":"peg","body_b":"channel_base_body","contact_count":309.0,"contact_point_centroid":[0.49629,0.11904,0.00945],"force_p95":0.60231,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63982,"mean_force":0.54027,"phase_index":1.0,"phase_name":"align_tool","phase_type":"align","tcp_position_centroid":[0.47712,0.18102,0.12534]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.496,0.11904,0.00945],"force_p95":0.60345,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63584,"mean_force":0.53976,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.47796,0.16331,0.08656]}],"total_contact_groups":6},"final_pose_error":0.15826,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49614,0.11728,0.03421],"final_tcp_position":[0.4807,0.13082,0.06329],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":40.53571,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.49603,0.11914,0.03389],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19928,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.49422,"phase_name":"approach_prepush","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":454.0,"raw_peak_contact_force":2.24822,"subtask_id":"pre_contact","tcp_end":[0.48425,0.17044,0.12969],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1093,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":309.0,"n_steps_budget":600.0,"object_pos_end":[0.49605,0.11913,0.03384],"object_pos_start":[0.49603,0.11914,0.03389],"object_to_goal_dist_end":0.19926,"object_to_goal_dist_start":0.19928,"object_z_max":0.03416,"peak_contact_force":0.52116,"phase_name":"align_tool","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":309.0,"raw_peak_contact_force":0.63982,"subtask_id":"pre_contact","tcp_end":[0.47285,0.19077,0.12468],"tcp_start":[0.48425,0.17044,0.12969],"tcp_to_object_dist_end":0.118,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11913,0.03401],"object_pos_start":[0.49605,0.11913,0.03384],"object_to_goal_dist_end":0.19926,"object_to_goal_dist_start":0.19926,"object_z_max":0.03415,"peak_contact_force":0.52229,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.63584,"subtask_id":"contact_peg","tcp_end":[0.48278,0.14725,0.06598],"tcp_start":[0.47285,0.19077,0.12468],"tcp_to_object_dist_end":0.04458,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":53.0,"n_steps_budget":1000.0,"object_pos_end":[0.49604,0.11742,0.03423],"object_pos_start":[0.49602,0.11913,0.03401],"object_to_goal_dist_end":0.19754,"object_to_goal_dist_start":0.19926,"object_z_max":0.03423,"peak_contact_force":3.51269,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":70.0,"raw_peak_contact_force":40.53571,"subtask_id":"push_progress","tcp_end":[0.4807,0.13082,0.06329],"tcp_start":[0.48069,0.13098,0.06333],"tcp_to_object_dist_end":0.03549,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82979,"average_solve_count":47.0,"average_success_count":47.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_tool.align_speed":0.11604,"approach_prepush.approach_speed":0.48375,"approach_prepush.approach_tolerance":0.01293,"contact_peg.contact_force_threshold":7.8874,"contact_peg.contact_speed":0.13655,"push_channel.push_distance":0.18872,"push_channel.push_force_guard_threshold":39.43244,"push_channel.push_pose_tolerance":0.00675,"push_channel.push_speed":0.02916},"optimized_scores":{"best_composite_score":-0.29287,"best_fitness_score":0.21713,"best_task_score":0.00154},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":11.0,"contact_point_centroid":[0.49182,0.05632,0.00938],"force_p95":39.37067,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.79652,"mean_force":29.62594,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50499,0.09,0.05976]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.51065,0.07974,0.05841],"force_p95":39.02812,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.45443,"mean_force":29.20987,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50499,0.09,0.05976]},{"body_a":"peg","body_b":"channel_base_body","contact_count":383.0,"contact_point_centroid":[0.50608,0.0629,0.00938],"force_p95":0.55271,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.05546,"mean_force":0.64876,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50897,0.11644,0.08986]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.51095,0.08016,0.05871],"force_p95":25.05815,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.6502,"mean_force":19.72971,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50536,0.09058,0.06039]},{"body_a":"peg","body_b":"channel_base_body","contact_count":502.0,"contact_point_centroid":[0.50575,0.06294,0.00935],"force_p95":0.57324,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.57352,"phase_index":0.0,"phase_name":"approach_prepush","phase_type":"approach","tcp_position_centroid":[0.5119,0.15706,0.20809]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_prepush","phase_type":"approach","tcp_position_centroid":[0.50008,0.19787,0.29551]},{"body_a":"peg","body_b":"channel_base_body","contact_count":326.0,"contact_point_centroid":[0.50592,0.06314,0.00938],"force_p95":0.55159,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55501,"mean_force":0.54656,"phase_index":1.0,"phase_name":"align_tool","phase_type":"align","tcp_position_centroid":[0.51811,0.13033,0.1218]}],"total_contact_groups":7},"final_pose_error":0.1878,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50554,0.0623,0.03386],"final_tcp_position":[0.5048,0.08946,0.05946],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":40.79652,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":530.0,"n_steps_budget":600.0,"object_pos_end":[0.50594,0.06297,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14322,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54333,"phase_name":"approach_prepush","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":536.0,"raw_peak_contact_force":3.88411,"subtask_id":"pre_contact","tcp_end":[0.52432,0.11796,0.12656],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10938,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":326.0,"n_steps_budget":600.0,"object_pos_end":[0.50603,0.06298,0.03381],"object_pos_start":[0.50594,0.06297,0.03381],"object_to_goal_dist_end":0.14324,"object_to_goal_dist_start":0.14322,"object_z_max":0.03381,"peak_contact_force":0.54199,"phase_name":"align_tool","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":326.0,"raw_peak_contact_force":0.55501,"subtask_id":"pre_contact","tcp_end":[0.51488,0.14093,0.12108],"tcp_start":[0.52432,0.11796,0.12656],"tcp_to_object_dist_end":0.11735,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":383.0,"n_steps_budget":600.0,"object_pos_end":[0.506,0.06292,0.03381],"object_pos_start":[0.50603,0.06298,0.03381],"object_to_goal_dist_end":0.14318,"object_to_goal_dist_start":0.14324,"object_z_max":0.03381,"peak_contact_force":14.17706,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":385.0,"raw_peak_contact_force":26.05546,"subtask_id":"contact_peg","tcp_end":[0.50527,0.09039,0.06018],"tcp_start":[0.50535,0.09051,0.06031],"tcp_to_object_dist_end":0.03809,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":11.0,"n_steps_budget":1000.0,"object_pos_end":[0.50559,0.06246,0.03387],"object_pos_start":[0.50594,0.06288,0.0338],"object_to_goal_dist_end":0.1427,"object_to_goal_dist_start":0.14314,"object_z_max":0.03387,"peak_contact_force":29.174,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":22.0,"raw_peak_contact_force":40.79652,"subtask_id":"push_progress","tcp_end":[0.5048,0.08946,0.05946],"tcp_start":[0.50482,0.08953,0.05951],"tcp_to_object_dist_end":0.03722,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02041,"average_solve_count":49.0,"average_success_count":49.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_tool.align_speed":0.28067,"approach_prepush.approach_speed":0.18024,"approach_prepush.approach_tolerance":0.01074,"contact_peg.contact_force_threshold":9.38567,"contact_peg.contact_speed":0.12475,"push_channel.push_distance":0.12814,"push_channel.push_force_guard_threshold":39.82471,"push_channel.push_pose_tolerance":0.00633,"push_channel.push_speed":0.06206},"optimized_scores":{"best_composite_score":-0.29402,"best_fitness_score":0.21598,"best_task_score":0.00104},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":9.0,"contact_point_centroid":[0.49738,0.04433,0.00936],"force_p95":44.07339,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.96094,"mean_force":30.09984,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50746,0.0838,0.05953]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.51227,0.07305,0.05842],"force_p95":43.77354,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.6673,"mean_force":29.68889,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50746,0.0838,0.05953]},{"body_a":"peg","body_b":"channel_base_body","contact_count":382.0,"contact_point_centroid":[0.50611,0.05668,0.00938],"force_p95":0.55431,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.39593,"mean_force":0.62808,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51365,0.1104,0.08932]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.51248,0.07347,0.05872],"force_p95":24.95676,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.9823,"mean_force":15.72692,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50783,0.08441,0.06012]},{"body_a":"peg","body_b":"channel_base_body","contact_count":537.0,"contact_point_centroid":[0.50587,0.05657,0.00935],"force_p95":0.60162,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.57619,"phase_index":0.0,"phase_name":"approach_prepush","phase_type":"approach","tcp_position_centroid":[0.51523,0.15387,0.20774]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_prepush","phase_type":"approach","tcp_position_centroid":[0.50023,0.1976,0.29507]},{"body_a":"peg","body_b":"channel_base_body","contact_count":323.0,"contact_point_centroid":[0.5062,0.05668,0.00938],"force_p95":0.55573,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56457,"mean_force":0.54664,"phase_index":1.0,"phase_name":"align_tool","phase_type":"align","tcp_position_centroid":[0.52473,0.12436,0.12118]}],"total_contact_groups":7},"final_pose_error":0.12715,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50587,0.05602,0.03382],"final_tcp_position":[0.50726,0.08322,0.05924],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":46.96094,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":566.0,"n_steps_budget":720.0,"object_pos_end":[0.5061,0.05663,0.03379],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.5466,"phase_name":"approach_prepush","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":574.0,"raw_peak_contact_force":4.44541,"subtask_id":"pre_contact","tcp_end":[0.53079,0.11186,0.12601],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11029,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":323.0,"n_steps_budget":600.0,"object_pos_end":[0.50611,0.05659,0.03379],"object_pos_start":[0.5061,0.05663,0.03379],"object_to_goal_dist_end":0.13686,"object_to_goal_dist_start":0.1369,"object_z_max":0.03379,"peak_contact_force":0.55988,"phase_name":"align_tool","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":323.0,"raw_peak_contact_force":0.56457,"subtask_id":"pre_contact","tcp_end":[0.52162,0.13506,0.12044],"tcp_start":[0.53079,0.11186,0.12601],"tcp_to_object_dist_end":0.11793,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":382.0,"n_steps_budget":600.0,"object_pos_end":[0.50617,0.0566,0.03379],"object_pos_start":[0.50611,0.05659,0.03379],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.13686,"object_z_max":0.0338,"peak_contact_force":5.81277,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":384.0,"raw_peak_contact_force":26.39593,"subtask_id":"contact_peg","tcp_end":[0.50773,0.08421,0.0599],"tcp_start":[0.50782,0.08433,0.06004],"tcp_to_object_dist_end":0.03803,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":9.0,"n_steps_budget":1000.0,"object_pos_end":[0.50591,0.0562,0.0338],"object_pos_start":[0.50613,0.05657,0.03377],"object_to_goal_dist_end":0.13647,"object_to_goal_dist_start":0.13685,"object_z_max":0.03381,"peak_contact_force":29.35608,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":18.0,"raw_peak_contact_force":46.96094,"subtask_id":"push_progress","tcp_end":[0.50726,0.08322,0.05924],"tcp_start":[0.50728,0.0833,0.05929],"tcp_to_object_dist_end":0.03713,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```