## Search State

- **Seed**: 8
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.0101 | 0.16 | ❌ rejected |
| 5 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0207 | 0.32 | ❌ rejected |
| 4 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.3826 | 0.47 | ❌ rejected |
| 3 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3295 | 0.32 | ❌ rejected |
| 2 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.0664 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.16 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.010) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.025
  - 0.0
  weight: 0.3
- id: push_complete
  offset:
  - 0.0
  - 0.025
  - 0.0
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.05
    - 0.06
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_contact
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.025
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  subtask_id: pre_contact
- id: push_1
  type: push
  generator: impedance_motion
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
      distance: 0.16
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
      - 0.09
      - 0.18
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_complete
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.06], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.025, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.010
- **task_score** (E): 0.165
- **fitness_score**: 0.270  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2276 |
| descend_1 | 1.00 | 1.00 | 0.0517 |
| push_1 | 1.00 | 1.00 | 0.1145 |
| retract_1 | 1.00 | 1.00 | 0.1386 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.086, 0.106) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.539 | 3.526 |
| descend_1 | descend | 1.00 / step_budget | (0.513, 0.086, 0.106)→(0.502, 0.080, 0.058) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.033) | 0.160→0.160 | 1.00 / 2.000 | 55.427 | 68.597 |
| push_1 | push | 1.00 / step_budget | (0.502, 0.080, 0.058)→(0.499, -0.034, 0.054) | (0.503, 0.080, 0.033)→(0.498, 0.029, 0.024) | 0.160→0.110 | 1.00 / 1.000 | 0.642 | 74.561 |
| retract_1 | retract | 1.00 / step_budget | (0.499, -0.034, 0.054)→(0.496, -0.034, 0.192) | (0.498, 0.029, 0.024)→(0.503, 0.029, 0.024) | 0.110→0.110 | 1.00 / 1.333 | 3.333 | 9.660 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.316
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.273
- phase_score: 0.303
- phase_breakdown.pre_contact_score: 0.423
- phase_breakdown.push_complete_score: 0.252

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.291
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.273
- **Median Q (composite search score)**: 0.005
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.462


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.93023,"average_solve_count":215.0,"average_success_count":215.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.1012,"push_1.guard_force_threshold":140.62656,"push_1.push_distance":0.13344,"push_1.push_speed":0.01619},"optimized_scores":{"best_composite_score":0.03147,"best_fitness_score":0.29147,"best_task_score":0.27344},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":381.0,"contact_point_centroid":[0.49748,0.11923,0.00944],"force_p95":50.84275,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.4422,"mean_force":6.29542,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48635,0.12086,0.08019]},{"body_a":"attachment","body_b":"peg","contact_count":41.0,"contact_point_centroid":[0.50299,0.11873,0.05802],"force_p95":71.15272,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":81.86749,"mean_force":53.56582,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49113,0.11927,0.05904]},{"body_a":"peg","body_b":"channel_base_body","contact_count":315.0,"contact_point_centroid":[0.49777,0.08861,0.009],"force_p95":78.31833,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":78.97416,"mean_force":34.9929,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49215,0.06705,0.0563]},{"body_a":"attachment","body_b":"peg","contact_count":193.0,"contact_point_centroid":[0.49968,0.0989,0.05813],"force_p95":78.07755,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":78.49239,"mean_force":56.27793,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49344,0.09059,0.05785]},{"body_a":"peg","body_b":"channel_base_body","contact_count":845.0,"contact_point_centroid":[0.5004,0.06794,0.00807],"force_p95":0.68337,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.749,"mean_force":0.61494,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48636,0.00479,0.12181]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52502,0.092,0.02428],"force_p95":6.40581,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.38498,"mean_force":1.70693,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48603,0.00483,0.08558]},{"body_a":"peg","body_b":"channel_base_body","contact_count":604.0,"contact_point_centroid":[0.49626,0.11907,0.00942],"force_p95":0.62307,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55384,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49098,0.16046,0.20009]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47499,0.05583,0.04569],"force_p95":1.19509,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.19509,"mean_force":1.19509,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49065,0.04501,0.05442]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49949,0.19881,0.29758]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.475,0.04395,0.02418],"force_p95":0.39015,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39237,"mean_force":0.37016,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48661,0.00486,0.19015]}],"total_contact_groups":10},"final_pose_error":0.01151,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49407,0.06838,0.02426],"final_tcp_position":[0.48667,0.00487,0.19196],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":82.4422,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":629.0,"n_steps_budget":1000.0,"object_pos_end":[0.49603,0.1192,0.03386],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19934,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.51956,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":628.0,"raw_peak_contact_force":2.24822,"subtask_id":"pre_contact","tcp_end":[0.48396,0.12354,0.10862],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07585,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":381.0,"n_steps_budget":600.0,"object_pos_end":[0.49737,0.11915,0.03297],"object_pos_start":[0.49603,0.1192,0.03386],"object_to_goal_dist_end":0.19929,"object_to_goal_dist_start":0.19934,"object_z_max":0.03409,"peak_contact_force":69.63481,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":422.0,"raw_peak_contact_force":82.4422,"subtask_id":"pre_contact","tcp_end":[0.49264,0.11935,0.05745],"tcp_start":[0.48396,0.12354,0.10862],"tcp_to_object_dist_end":0.02493,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":321.0,"n_steps_budget":1000.0,"object_pos_end":[0.4979,0.06813,0.02409],"object_pos_start":[0.49737,0.11915,0.03297],"object_to_goal_dist_end":0.14899,"object_to_goal_dist_start":0.19929,"object_z_max":0.04021,"peak_contact_force":0.64268,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":509.0,"raw_peak_contact_force":78.97416,"subtask_id":"push_complete","tcp_end":[0.4894,0.0049,0.05315],"tcp_start":[0.49264,0.11935,0.05745],"tcp_to_object_dist_end":0.0701,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":845.0,"n_steps_budget":930.0,"object_pos_end":[0.49407,0.06838,0.02426],"object_pos_start":[0.4979,0.06813,0.02409],"object_to_goal_dist_end":0.14933,"object_to_goal_dist_start":0.14899,"object_z_max":0.02457,"peak_contact_force":0.63997,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":853.0,"raw_peak_contact_force":8.749,"tcp_end":[0.48667,0.00487,0.19196],"tcp_start":[0.4894,0.0049,0.05315],"tcp_to_object_dist_end":0.17948,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.96581,"average_solve_count":234.0,"average_success_count":234.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.0541,"push_1.guard_force_threshold":130.45502,"push_1.push_distance":0.13264,"push_1.push_speed":0.0298},"optimized_scores":{"best_composite_score":0.00514,"best_fitness_score":0.26514,"best_task_score":0.12764},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":189.0,"contact_point_centroid":[0.51184,0.04292,0.05871],"force_p95":71.97711,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":72.79665,"mean_force":49.01263,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50653,0.03396,0.0585]},{"body_a":"peg","body_b":"channel_base_body","contact_count":310.0,"contact_point_centroid":[0.50528,0.03347,0.0091],"force_p95":70.34494,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":70.75047,"mean_force":30.19141,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5053,0.01086,0.05705]},{"body_a":"peg","body_b":"channel_base_body","contact_count":231.0,"contact_point_centroid":[0.50627,0.06288,0.00938],"force_p95":14.60979,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.33785,"mean_force":2.86236,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51468,0.06665,0.08184]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.51804,0.0635,0.05821],"force_p95":57.8831,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.86843,"mean_force":44.68564,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50618,0.06386,0.05949]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":30.0,"contact_point_centroid":[0.52501,0.05042,0.05947],"force_p95":11.05553,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.10089,"mean_force":9.58467,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50701,0.04445,0.0591]},{"body_a":"peg","body_b":"channel_base_body","contact_count":845.0,"contact_point_centroid":[0.49803,0.01276,0.00819],"force_p95":8.49183,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.38465,"mean_force":1.39218,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4996,-0.04982,0.12242]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":115.0,"contact_point_centroid":[0.47486,0.01362,0.02541],"force_p95":9.33749,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.0481,"mean_force":6.06896,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49926,-0.04976,0.08505]},{"body_a":"peg","body_b":"channel_base_body","contact_count":821.0,"contact_point_centroid":[0.50586,0.06298,0.00937],"force_p95":0.55609,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56305,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51175,0.13257,0.19789]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49976,0.19805,0.29689]}],"total_contact_groups":9},"final_pose_error":0.01181,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50666,0.01281,0.02415],"final_tcp_position":[0.49995,-0.04978,0.19257],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":72.79665,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":849.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.06294,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.55021,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":855.0,"raw_peak_contact_force":3.88411,"subtask_id":"pre_contact","tcp_end":[0.52463,0.0697,0.10542],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07432,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":231.0,"n_steps_budget":600.0,"object_pos_end":[0.5058,0.06287,0.03346],"object_pos_start":[0.50596,0.06294,0.03381],"object_to_goal_dist_end":0.14313,"object_to_goal_dist_start":0.1432,"object_z_max":0.03381,"peak_contact_force":57.54128,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":243.0,"raw_peak_contact_force":59.33785,"subtask_id":"pre_contact","tcp_end":[0.50608,0.06376,0.05867],"tcp_start":[0.52463,0.0697,0.10542],"tcp_to_object_dist_end":0.02522,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":316.0,"n_steps_budget":1000.0,"object_pos_end":[0.49781,0.01248,0.02408],"object_pos_start":[0.5058,0.06287,0.03346],"object_to_goal_dist_end":0.09386,"object_to_goal_dist_start":0.14313,"object_z_max":0.04028,"peak_contact_force":0.61605,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":529.0,"raw_peak_contact_force":72.79665,"subtask_id":"push_complete","tcp_end":[0.50272,-0.05002,0.05405],"tcp_start":[0.50608,0.06376,0.05867],"tcp_to_object_dist_end":0.06948,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":845.0,"n_steps_budget":930.0,"object_pos_end":[0.50666,0.01281,0.02415],"object_pos_start":[0.49781,0.01248,0.02408],"object_to_goal_dist_end":0.09439,"object_to_goal_dist_start":0.09386,"object_z_max":0.02609,"peak_contact_force":0.64358,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":960.0,"raw_peak_contact_force":10.38465,"tcp_end":[0.49995,-0.04978,0.19257],"tcp_start":[0.50272,-0.05002,0.05405],"tcp_to_object_dist_end":0.1798,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.06608,"average_solve_count":227.0,"average_success_count":227.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.08713,"push_1.guard_force_threshold":135.9725,"push_1.push_distance":0.13385,"push_1.push_speed":0.02315},"optimized_scores":{"best_composite_score":-0.00625,"best_fitness_score":0.25375,"best_task_score":0.09378},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":191.0,"contact_point_centroid":[0.51331,0.03725,0.05855],"force_p95":71.20251,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":71.91194,"mean_force":49.27247,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50788,0.02854,0.05836]},{"body_a":"peg","body_b":"channel_base_body","contact_count":319.0,"contact_point_centroid":[0.50553,0.02699,0.00909],"force_p95":69.21826,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":69.90806,"mean_force":29.72068,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50661,0.00436,0.05685]},{"body_a":"peg","body_b":"channel_base_body","contact_count":228.0,"contact_point_centroid":[0.50644,0.05661,0.00938],"force_p95":26.81674,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":64.01167,"mean_force":3.24154,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5188,0.06036,0.08144]},{"body_a":"attachment","body_b":"peg","contact_count":13.0,"contact_point_centroid":[0.51955,0.057,0.05816],"force_p95":61.91238,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.53982,"mean_force":47.37662,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5077,0.05756,0.05942]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":43.0,"contact_point_centroid":[0.52501,0.0451,0.05936],"force_p95":11.61376,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.03356,"mean_force":10.70076,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5083,0.03912,0.05889]},{"body_a":"peg","body_b":"channel_base_body","contact_count":845.0,"contact_point_centroid":[0.49982,0.00631,0.00804],"force_p95":0.72553,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.84619,"mean_force":0.69456,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50092,-0.0572,0.12219]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":15.0,"contact_point_centroid":[0.525,-0.019,0.02439],"force_p95":9.15477,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.35646,"mean_force":4.82879,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50119,-0.05715,0.18793]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.47498,0.03088,0.02429],"force_p95":6.81556,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.92599,"mean_force":1.80468,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50099,-0.0574,0.06535]},{"body_a":"peg","body_b":"channel_base_body","contact_count":787.0,"contact_point_centroid":[0.50596,0.05658,0.00936],"force_p95":0.60085,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56671,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51522,0.12904,0.19718]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49997,0.1976,0.29626]}],"total_contact_groups":10},"final_pose_error":0.01185,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50686,0.00522,0.02464],"final_tcp_position":[0.50127,-0.05716,0.19235],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":71.91194,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":816.0,"n_steps_budget":1000.0,"object_pos_end":[0.5061,0.05661,0.03379],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.54644,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":824.0,"raw_peak_contact_force":4.44541,"subtask_id":"pre_contact","tcp_end":[0.53117,0.06339,0.10482],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07563,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":228.0,"n_steps_budget":600.0,"object_pos_end":[0.50587,0.05654,0.03339],"object_pos_start":[0.5061,0.05661,0.03379],"object_to_goal_dist_end":0.13683,"object_to_goal_dist_start":0.13688,"object_z_max":0.03379,"peak_contact_force":39.10519,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":241.0,"raw_peak_contact_force":64.01167,"subtask_id":"pre_contact","tcp_end":[0.50743,0.05744,0.05853],"tcp_start":[0.53117,0.06339,0.10482],"tcp_to_object_dist_end":0.02521,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":325.0,"n_steps_budget":1000.0,"object_pos_end":[0.49711,0.00619,0.02411],"object_pos_start":[0.50587,0.05654,0.03339],"object_to_goal_dist_end":0.08769,"object_to_goal_dist_start":0.13683,"object_z_max":0.04031,"peak_contact_force":0.66864,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":553.0,"raw_peak_contact_force":71.91194,"subtask_id":"push_complete","tcp_end":[0.50404,-0.05743,0.05387],"tcp_start":[0.50743,0.05744,0.05853],"tcp_to_object_dist_end":0.07057,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":845.0,"n_steps_budget":930.0,"object_pos_end":[0.50686,0.00522,0.02464],"object_pos_start":[0.49711,0.00619,0.02411],"object_to_goal_dist_end":0.08687,"object_to_goal_dist_start":0.08769,"object_z_max":0.02471,"peak_contact_force":8.71561,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":866.0,"raw_peak_contact_force":9.84619,"tcp_end":[0.50127,-0.05716,0.19235],"tcp_start":[0.50404,-0.05743,0.05387],"tcp_to_object_dist_end":0.17902,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```