## Search State

- **Seed**: 8
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → align → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.1580 | 0.29 | ❌ rejected |
| 10 | descend → align → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1612 | 0.43 | ❌ rejected |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | -0.0476 | 0.00 | ❌ rejected |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.0242 | 0.26 | ❌ rejected |
| 7 | approach → descend → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1268 | 0.30 | ❌ rejected |

**Proposal policy**: task_score is 0.29 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.158) — your mutation base

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

- **Composite score**: 0.158
- **task_score** (E): 0.290
- **fitness_score**: 0.418  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2067 |
| align_1 | 1.00 | 1.00 | 0.0781 |
| push_1 | 0.33 | 1.00 | 0.0386 |
| retract_1 | 1.00 | 1.00 | 0.1391 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.133, 0.108) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.549 | 3.526 |
| align_1 | align | 1.00 / step_budget | (0.513, 0.133, 0.108)→(0.500, 0.107, 0.037) | (0.503, 0.080, 0.034)→(0.502, 0.077, 0.035) | 0.160→0.157 | 1.00 / 1.000 | 0.403 | 75.582 |
| push_1 | push | 0.33 / guard_failure | (0.498, 0.012, 0.034)→(0.497, -0.027, 0.032) | (0.502, 0.077, 0.035)→(0.502, -0.053, 0.037) | 0.157→0.034 | 1.00 / 2.667 | 11.609 | 41.734 |
| retract_1 | retract | 1.00 / step_budget | (0.497, -0.027, 0.032)→(0.494, -0.027, 0.171) | (0.502, -0.054, 0.037)→(0.506, -0.040, 0.034) | 0.034→0.042 | 1.00 / 1.000 | 0.546 | 122.412 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.817
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.318
- phase_score: 0.604
- phase_breakdown.pre_contact_score: 0.600
- phase_breakdown.push_complete_score: 0.606

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.490
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.338
- **Median Q (composite search score)**: 0.167
- **K-run variance**: 0.0039
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.272


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57059,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.06238,"approach_1.approach_speed":0.07209,"push_1.push_distance":0.13466,"push_1.push_speed":0.05158},"optimized_scores":{"best_composite_score":0.0769,"best_fitness_score":0.3369,"best_task_score":0.33801},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":121.0,"contact_point_centroid":[0.47498,0.02881,0.04675],"force_p95":224.0419,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":309.00716,"mean_force":118.84908,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48681,0.02883,0.04482]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":91.0,"contact_point_centroid":[0.47466,0.09579,0.03625],"force_p95":28.20072,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.37793,"mean_force":8.63519,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48946,0.12574,0.0327]},{"body_a":"attachment","body_b":"peg","contact_count":233.0,"contact_point_centroid":[0.49366,0.07819,0.05029],"force_p95":24.642,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.11499,"mean_force":4.57648,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48866,0.08931,0.03166]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":104.0,"contact_point_centroid":[0.52507,0.00477,0.05199],"force_p95":15.79025,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.03996,"mean_force":2.63251,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48684,0.02885,0.04386]},{"body_a":"attachment","body_b":"peg","contact_count":91.0,"contact_point_centroid":[0.49611,0.01939,0.06174],"force_p95":12.98375,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.76154,"mean_force":2.67598,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48674,0.0289,0.04899]},{"body_a":"peg","body_b":"channel_base_body","contact_count":112.0,"contact_point_centroid":[0.4976,0.05017,0.00969],"force_p95":6.16139,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.33115,"mean_force":2.61393,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4887,0.09086,0.03169]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":38.0,"contact_point_centroid":[0.52517,0.01927,0.01846],"force_p95":11.30272,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.45021,"mean_force":2.53179,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.488,0.04172,0.03088]},{"body_a":"peg","body_b":"channel_base_body","contact_count":484.0,"contact_point_centroid":[0.49643,0.11686,0.00948],"force_p95":0.68843,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.49124,"mean_force":0.64578,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48627,0.15719,0.07005]},{"body_a":"attachment","body_b":"peg","contact_count":28.0,"contact_point_centroid":[0.4935,0.13535,0.05212],"force_p95":6.08803,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.19126,"mean_force":2.08996,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49053,0.14719,0.04104]},{"body_a":"peg","body_b":"channel_base_body","contact_count":833.0,"contact_point_centroid":[0.50617,0.00587,0.00953],"force_p95":0.61405,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.94145,"mean_force":0.57676,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48535,0.02941,0.10062]},{"body_a":"peg","body_b":"channel_base_body","contact_count":571.0,"contact_point_centroid":[0.49622,0.11907,0.00943],"force_p95":0.61394,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55326,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49114,0.18433,0.20101]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49954,0.19931,0.29773]}],"total_contact_groups":12},"final_pose_error":0.01107,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50515,0.01013,0.03379],"final_tcp_position":[0.48523,0.02959,0.17013],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":309.00716,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":596.0,"n_steps_budget":1000.0,"object_pos_end":[0.49601,0.119,0.03383],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19913,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.55153,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":595.0,"raw_peak_contact_force":2.24822,"subtask_id":"pre_contact","tcp_end":[0.48399,0.1701,0.10949],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09209,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":489.0,"n_steps_budget":810.0,"object_pos_end":[0.49363,0.11523,0.03465],"object_pos_start":[0.49601,0.119,0.03383],"object_to_goal_dist_end":0.1954,"object_to_goal_dist_start":0.19913,"object_z_max":0.03553,"peak_contact_force":0.417,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":512.0,"raw_peak_contact_force":7.49124,"subtask_id":"pre_contact","tcp_end":[0.49136,0.14515,0.03515],"tcp_start":[0.48399,0.1701,0.10949],"tcp_to_object_dist_end":0.03001,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":297.0,"n_steps_budget":1000.0,"object_pos_end":[0.50684,0.00522,0.03763],"object_pos_start":[0.49363,0.11523,0.03465],"object_to_goal_dist_end":0.08553,"object_to_goal_dist_start":0.1954,"object_z_max":0.03882,"peak_contact_force":11.14706,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":474.0,"raw_peak_contact_force":30.37793,"subtask_id":"push_complete","tcp_end":[0.48793,0.02968,0.03086],"tcp_start":[0.49136,0.14515,0.03515],"tcp_to_object_dist_end":0.03165,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":845.0,"n_steps_budget":930.0,"object_pos_end":[0.50515,0.01013,0.03379],"object_pos_start":[0.50684,0.00522,0.03763],"object_to_goal_dist_end":0.09049,"object_to_goal_dist_start":0.08553,"object_z_max":0.03765,"peak_contact_force":0.5468,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1149.0,"raw_peak_contact_force":309.00716,"tcp_end":[0.48523,0.02959,0.17013],"tcp_start":[0.48793,0.02968,0.03086],"tcp_to_object_dist_end":0.13916,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34783,"average_solve_count":184.0,"average_success_count":184.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.05101,"approach_1.approach_speed":0.05986,"push_1.push_distance":0.17282,"push_1.push_speed":0.08311},"optimized_scores":{"best_composite_score":0.22985,"best_fitness_score":0.48985,"best_task_score":0.31813},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":235.0,"contact_point_centroid":[0.50263,0.01725,0.04739],"force_p95":27.63619,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.47088,"mean_force":5.37789,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50134,0.02878,0.03369]},{"body_a":"peg","body_b":"channel_base_body","contact_count":8.0,"contact_point_centroid":[0.49264,-0.10064,0.01352],"force_p95":48.67131,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.54323,"mean_force":23.80512,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50112,-0.05488,0.03307]},{"body_a":"peg","body_b":"channel_base_body","contact_count":291.0,"contact_point_centroid":[0.49277,-0.10052,0.06195],"force_p95":24.3729,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.23352,"mean_force":16.28109,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49802,-0.05363,0.05522]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.5253,0.04382,0.04936],"force_p95":32.18543,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.78084,"mean_force":17.19763,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50164,0.07378,0.0344]},{"body_a":"attachment","body_b":"peg","contact_count":281.0,"contact_point_centroid":[0.49668,-0.0652,0.0546],"force_p95":24.38786,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.471,"mean_force":16.56075,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49803,-0.0536,0.05438]},{"body_a":"peg","body_b":"channel_base_body","contact_count":168.0,"contact_point_centroid":[0.50025,-0.02106,0.00951],"force_p95":8.99253,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.11212,"mean_force":2.77336,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50129,0.01725,0.03355]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":144.0,"contact_point_centroid":[0.47482,-0.08259,0.05336],"force_p95":15.5897,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.2924,"mean_force":3.70142,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4983,-0.05416,0.04593]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":81.0,"contact_point_centroid":[0.4748,-0.05671,0.04031],"force_p95":14.89727,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.87779,"mean_force":2.28431,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.501,-0.02583,0.03303]},{"body_a":"peg","body_b":"channel_base_body","contact_count":361.0,"contact_point_centroid":[0.50627,0.06206,0.00939],"force_p95":0.55405,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.56119,"mean_force":0.64438,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51307,0.104,0.07034]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.50598,0.08032,0.0454],"force_p95":10.69185,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.13642,"mean_force":3.9251,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50533,0.09227,0.04118]},{"body_a":"peg","body_b":"channel_base_body","contact_count":699.0,"contact_point_centroid":[0.50582,0.06302,0.00936],"force_p95":0.55974,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56592,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51162,0.15727,0.19902]},{"body_a":"peg","body_b":"channel_base_body","contact_count":528.0,"contact_point_centroid":[0.50499,-0.06825,0.00937],"force_p95":0.75832,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.09186,"mean_force":0.57451,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49805,-0.05553,0.12803]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49984,0.19848,0.29663]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.52539,-0.0683,0.05859],"force_p95":0.65431,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.83776,"mean_force":0.21124,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49783,-0.05535,0.09648]}],"total_contact_groups":14},"final_pose_error":0.01144,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50576,-0.06777,0.03407],"final_tcp_position":[0.4984,-0.05564,0.17196],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":59.47088,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":727.0,"n_steps_budget":1000.0,"object_pos_end":[0.50602,0.06295,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.55021,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":733.0,"raw_peak_contact_force":3.88411,"subtask_id":"pre_contact","tcp_end":[0.52442,0.11752,0.10701],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09315,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":361.0,"n_steps_budget":990.0,"object_pos_end":[0.50634,0.06087,0.03455],"object_pos_start":[0.50602,0.06295,0.0338],"object_to_goal_dist_end":0.14112,"object_to_goal_dist_start":0.14321,"object_z_max":0.03453,"peak_contact_force":0.43148,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":371.0,"raw_peak_contact_force":11.56119,"subtask_id":"pre_contact","tcp_end":[0.50438,0.09082,0.03752],"tcp_start":[0.52442,0.11752,0.10701],"tcp_to_object_dist_end":0.03016,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":369.0,"n_steps_budget":1000.0,"object_pos_end":[0.49248,-0.08246,0.03768],"object_pos_start":[0.50634,0.06087,0.03455],"object_to_goal_dist_end":0.00825,"object_to_goal_dist_start":0.14112,"object_z_max":0.041,"peak_contact_force":19.6288,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":529.0,"raw_peak_contact_force":59.47088,"subtask_id":"push_complete","tcp_end":[0.50116,-0.05597,0.03306],"tcp_start":[0.50118,-0.05586,0.03309],"tcp_to_object_dist_end":0.02825,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":846.0,"n_steps_budget":930.0,"object_pos_end":[0.50576,-0.06777,0.03407],"object_pos_start":[0.49202,-0.08313,0.0379],"object_to_goal_dist_end":0.01476,"object_to_goal_dist_start":0.00883,"object_z_max":0.05824,"peak_contact_force":0.54812,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1281.0,"raw_peak_contact_force":36.23352,"tcp_end":[0.4984,-0.05564,0.17196],"tcp_start":[0.50116,-0.05597,0.03306],"tcp_to_object_dist_end":0.13862,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29293,"average_solve_count":198.0,"average_success_count":198.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.06527,"approach_1.approach_speed":0.05101,"push_1.push_distance":0.15787,"push_1.push_speed":0.06758},"optimized_scores":{"best_composite_score":0.16727,"best_fitness_score":0.42727,"best_task_score":0.21322},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":17.0,"contact_point_centroid":[0.52524,0.09411,0.05995],"force_p95":207.62246,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":207.6926,"mean_force":162.98985,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51336,0.0941,0.06083]},{"body_a":"attachment","body_b":"peg","contact_count":245.0,"contact_point_centroid":[0.50521,-0.0023,0.0484],"force_p95":22.94655,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.35411,"mean_force":5.87435,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50199,0.00935,0.03345]},{"body_a":"peg","body_b":"channel_base_body","contact_count":8.0,"contact_point_centroid":[0.50677,-0.10055,0.05969],"force_p95":29.263,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.09636,"mean_force":7.57886,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50173,-0.05309,0.03299]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":157.0,"contact_point_centroid":[0.52517,-0.0278,0.03624],"force_p95":22.93753,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.11442,"mean_force":5.95459,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50182,0.00169,0.03322]},{"body_a":"peg","body_b":"channel_base_body","contact_count":145.0,"contact_point_centroid":[0.50531,-0.01942,0.00957],"force_p95":17.9271,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.1583,"mean_force":4.40416,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50231,0.02208,0.03385]},{"body_a":"attachment","body_b":"peg","contact_count":248.0,"contact_point_centroid":[0.50103,-0.06412,0.05234],"force_p95":19.16989,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.99592,"mean_force":11.73631,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49812,-0.05266,0.05122]},{"body_a":"peg","body_b":"channel_base_body","contact_count":254.0,"contact_point_centroid":[0.5073,-0.1003,0.06279],"force_p95":19.30663,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.68863,"mean_force":10.49239,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49812,-0.05266,0.05172]},{"body_a":"peg","body_b":"channel_base_body","contact_count":351.0,"contact_point_centroid":[0.50608,0.056,0.00939],"force_p95":0.55404,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.71796,"mean_force":0.60864,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51671,0.09787,0.06998]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.50599,0.07377,0.04111],"force_p95":7.45916,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.24521,"mean_force":2.88483,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50622,0.08571,0.04028]},{"body_a":"peg","body_b":"channel_base_body","contact_count":581.0,"contact_point_centroid":[0.50532,-0.06182,0.00941],"force_p95":0.92649,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.69818,"mean_force":0.64018,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49853,-0.05384,0.12267]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":219.0,"contact_point_centroid":[0.52512,-0.07625,0.0582],"force_p95":5.62442,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.8801,"mean_force":3.07832,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49787,-0.0528,0.06349]},{"body_a":"peg","body_b":"channel_base_body","contact_count":724.0,"contact_point_centroid":[0.50595,0.05665,0.00936],"force_p95":0.60041,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56853,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51496,0.15411,0.19869]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49993,0.19828,0.29629]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":20.0,"contact_point_centroid":[0.47495,-0.0739,0.02859],"force_p95":2.88379,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.90692,"mean_force":2.13811,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49744,-0.05205,0.06094]}],"total_contact_groups":14},"final_pose_error":0.01145,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50663,-0.06159,0.03388],"final_tcp_position":[0.49887,-0.05394,0.17177],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":207.6926,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":753.0,"n_steps_budget":1000.0,"object_pos_end":[0.50616,0.05658,0.0338],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13686,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.54661,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":761.0,"raw_peak_contact_force":4.44541,"subtask_id":"pre_contact","tcp_end":[0.53088,0.1115,0.10667],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09453,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":351.0,"n_steps_budget":810.0,"object_pos_end":[0.50486,0.05444,0.03462],"object_pos_start":[0.50616,0.05658,0.0338],"object_to_goal_dist_end":0.13463,"object_to_goal_dist_start":0.13686,"object_z_max":0.03456,"peak_contact_force":0.36129,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":377.0,"raw_peak_contact_force":207.6926,"subtask_id":"pre_contact","tcp_end":[0.50529,0.08462,0.03763],"tcp_start":[0.53088,0.1115,0.10667],"tcp_to_object_dist_end":0.03034,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":362.0,"n_steps_budget":1000.0,"object_pos_end":[0.50665,-0.08308,0.03486],"object_pos_start":[0.50486,0.05444,0.03462],"object_to_goal_dist_end":0.00895,"object_to_goal_dist_start":0.13463,"object_z_max":0.04072,"peak_contact_force":4.04982,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":555.0,"raw_peak_contact_force":35.35411,"subtask_id":"push_complete","tcp_end":[0.50164,-0.05427,0.03287],"tcp_start":[0.50168,-0.05414,0.03293],"tcp_to_object_dist_end":0.02932,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":846.0,"n_steps_budget":930.0,"object_pos_end":[0.50663,-0.06159,0.03388],"object_pos_start":[0.50655,-0.08338,0.03475],"object_to_goal_dist_end":0.0205,"object_to_goal_dist_start":0.00905,"object_z_max":0.05068,"peak_contact_force":0.54358,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1322.0,"raw_peak_contact_force":21.99592,"tcp_end":[0.49887,-0.05394,0.17177],"tcp_start":[0.50164,-0.05427,0.03287],"tcp_to_object_dist_end":0.13832,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```