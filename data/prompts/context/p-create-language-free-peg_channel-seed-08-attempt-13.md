## Search State

- **Seed**: 8
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → push → retract | linear_cartesian | arc_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.1134 | 0.17 | ❌ rejected |
| 12 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.1875 | 0.10 | ❌ rejected |
| 11 | approach → align → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.1580 | 0.29 | ❌ rejected |
| 10 | descend → align → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1612 | 0.43 | ❌ rejected |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | -0.0476 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.17 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.113) — your mutation base

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

- **Composite score**: 0.113
- **task_score** (E): 0.173
- **fitness_score**: 0.390  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.083
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2067 |
| descend_1 | 1.00 | 1.00 | 0.0799 |
| push_1 | 0.67 | 1.00 | 0.0791 |
| retract_1 | 1.00 | 1.00 | 0.1388 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.133, 0.108) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.563 | 3.526 |
| descend_1 | descend | 1.00 / step_budget | (0.513, 0.133, 0.108)→(0.501, 0.107, 0.035) | (0.503, 0.080, 0.034)→(0.502, 0.076, 0.035) | 0.160→0.156 | 1.00 / 1.333 | 0.720 | 77.697 |
| push_1 | push | 0.67 / step_budget | (0.501, 0.107, 0.035)→(0.497, 0.028, 0.030) | (0.502, 0.076, 0.035)→(0.504, -0.001, 0.033) | 0.156→0.080 | 1.00 / 2.667 | 1311.585 | 18.407 |
| retract_1 | retract | 1.00 / step_budget | (0.497, 0.028, 0.030)→(0.494, 0.028, 0.169) | (0.504, -0.001, 0.033)→(0.503, -0.002, 0.031) | 0.080→0.080 | 1.00 / 1.000 | 0.566 | 99.952 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.688
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.334
- phase_score: 0.634
- phase_breakdown.pre_contact_score: 0.807
- phase_breakdown.push_complete_score: 0.561

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.514
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.334
- **Median Q (composite search score)**: 0.116
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at upper bound**: push_1.push_speed
- **Final σ (mean)**: 0.390


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51829,"average_solve_count":164.0,"average_success_count":164.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.05684,"descend_1.descend_arc_height":0.08624,"descend_1.descend_speed":0.07048,"push_1.force_threshold":39.95434,"push_1.push_distance":0.13479,"push_1.push_speed":0.07467},"optimized_scores":{"best_composite_score":0.15409,"best_fitness_score":0.51409,"best_task_score":0.33364},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":157.0,"contact_point_centroid":[0.47496,0.02842,0.04443],"force_p95":278.39634,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":291.49373,"mean_force":151.72341,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48678,0.02841,0.04253]},{"body_a":"attachment","body_b":"peg","contact_count":918.0,"contact_point_centroid":[0.49713,0.07443,0.0493],"force_p95":24.31979,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.98997,"mean_force":13.22929,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48759,0.08431,0.02716]},{"body_a":"peg","body_b":"channel_base_body","contact_count":831.0,"contact_point_centroid":[0.50674,0.00437,0.00955],"force_p95":0.6093,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.83582,"mean_force":0.61231,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48473,0.02877,0.09676]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":749.0,"contact_point_centroid":[0.52522,0.04877,0.05339],"force_p95":19.75226,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.06496,"mean_force":12.35363,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48735,0.07348,0.02701]},{"body_a":"peg","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.51969,0.0166,0.06277],"force_p95":18.56208,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.53075,"mean_force":5.05923,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48688,0.0289,0.02711]},{"body_a":"peg","body_b":"channel_base_body","contact_count":843.0,"contact_point_centroid":[0.5065,0.04702,0.00994],"force_p95":14.01449,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.35545,"mean_force":8.61348,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48765,0.08637,0.02721]},{"body_a":"attachment","body_b":"peg","contact_count":112.0,"contact_point_centroid":[0.49651,0.01884,0.06056],"force_p95":16.09331,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.09573,"mean_force":2.76498,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48674,0.02844,0.04386]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":122.0,"contact_point_centroid":[0.52506,0.00519,0.0454],"force_p95":16.59367,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.8074,"mean_force":2.5533,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48679,0.02847,0.04021]},{"body_a":"peg","body_b":"link7","contact_count":624.0,"contact_point_centroid":[0.51993,0.05832,0.06273],"force_p95":7.92453,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.50843,"mean_force":5.50403,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48733,0.07093,0.02702]},{"body_a":"peg","body_b":"channel_base_body","contact_count":583.0,"contact_point_centroid":[0.49609,0.11876,0.00945],"force_p95":0.61749,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.08585,"mean_force":0.57662,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48707,0.16826,0.06515]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.49474,0.13657,0.04725],"force_p95":5.79288,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.59707,"mean_force":1.91739,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4917,0.14842,0.03202]},{"body_a":"peg","body_b":"channel_base_body","contact_count":599.0,"contact_point_centroid":[0.49622,0.11919,0.00943],"force_p95":0.61679,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55289,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49101,0.18432,0.20118]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49953,0.19935,0.29793]}],"total_contact_groups":13},"final_pose_error":0.01147,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50563,0.00891,0.03386],"final_tcp_position":[0.48428,0.02894,0.16589],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":291.49373,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":624.0,"n_steps_budget":1000.0,"object_pos_end":[0.49604,0.11909,0.03399],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19922,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.55419,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":623.0,"raw_peak_contact_force":2.24822,"subtask_id":"pre_contact","tcp_end":[0.48403,0.17013,0.10966],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09206,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":583.0,"n_steps_budget":720.0,"object_pos_end":[0.49563,0.11798,0.03473],"object_pos_start":[0.49604,0.11909,0.03399],"object_to_goal_dist_end":0.1981,"object_to_goal_dist_start":0.19922,"object_z_max":0.03463,"peak_contact_force":1.33163,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":595.0,"raw_peak_contact_force":7.08585,"subtask_id":"pre_contact","tcp_end":[0.49177,0.14763,0.0316],"tcp_start":[0.48403,0.17013,0.10966],"tcp_to_object_dist_end":0.03007,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50755,0.00666,0.03672],"object_pos_start":[0.49563,0.11798,0.03473],"object_to_goal_dist_end":0.08705,"object_to_goal_dist_start":0.1981,"object_z_max":0.03681,"peak_contact_force":22.30837,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3134.0,"raw_peak_contact_force":28.98997,"subtask_id":"push_complete","tcp_end":[0.48716,0.02911,0.027],"tcp_start":[0.49177,0.14763,0.0316],"tcp_to_object_dist_end":0.03184,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":844.0,"n_steps_budget":930.0,"object_pos_end":[0.50563,0.00891,0.03386],"object_pos_start":[0.50755,0.00666,0.03672],"object_to_goal_dist_end":0.0893,"object_to_goal_dist_start":0.08705,"object_z_max":0.03687,"peak_contact_force":0.54814,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1230.0,"raw_peak_contact_force":291.49373,"tcp_end":[0.48428,0.02894,0.16589],"tcp_start":[0.48716,0.02911,0.027],"tcp_to_object_dist_end":0.13524,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.22632,"average_solve_count":190.0,"average_success_count":190.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.01054,"descend_1.descend_arc_height":0.02078,"descend_1.descend_speed":0.05393,"push_1.force_threshold":24.42508,"push_1.push_distance":0.10395,"push_1.push_speed":0.1},"optimized_scores":{"best_composite_score":0.06979,"best_fitness_score":0.17979,"best_task_score":0.05615},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":107.0,"contact_point_centroid":[0.50454,0.06971,0.04808],"force_p95":13.63868,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.62323,"mean_force":4.66824,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49981,0.08143,0.02742]},{"body_a":"peg","body_b":"channel_base_body","contact_count":79.0,"contact_point_centroid":[0.50435,0.03856,0.00987],"force_p95":11.9767,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.65004,"mean_force":4.56452,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50005,0.08255,0.0277]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":81.0,"contact_point_centroid":[0.52519,0.05091,0.03623],"force_p95":9.63157,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.4561,"mean_force":2.88538,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49938,0.08014,0.02692]},{"body_a":"peg","body_b":"channel_base_body","contact_count":534.0,"contact_point_centroid":[0.50598,0.06245,0.00939],"force_p95":0.55343,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.97059,"mean_force":0.68982,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51034,0.11299,0.06012]},{"body_a":"attachment","body_b":"peg","contact_count":15.0,"contact_point_centroid":[0.5053,0.08045,0.04696],"force_p95":8.47938,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.49395,"mean_force":5.28207,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50253,0.09232,0.03084]},{"body_a":"peg","body_b":"channel_base_body","contact_count":708.0,"contact_point_centroid":[0.50579,0.06303,0.00936],"force_p95":0.55948,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56567,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51161,0.15734,0.19918]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49978,0.19858,0.29684]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.5043,0.05972,0.05014],"force_p95":2.12271,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.34528,"mean_force":0.82162,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4987,0.07146,0.02618]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.5251,0.04162,0.0131],"force_p95":0.53481,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.84964,"mean_force":0.37373,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49796,0.07104,0.02694]},{"body_a":"peg","body_b":"channel_base_body","contact_count":838.0,"contact_point_centroid":[0.50654,0.04062,0.00941],"force_p95":0.55396,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.78172,"mean_force":0.54662,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49548,0.07109,0.09523]}],"total_contact_groups":10},"final_pose_error":0.01176,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5067,0.04094,0.03384],"final_tcp_position":[0.49581,0.07119,0.16482],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":3912.28033,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":736.0,"n_steps_budget":1000.0,"object_pos_end":[0.50603,0.06298,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14324,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54147,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":742.0,"raw_peak_contact_force":3.88411,"subtask_id":"pre_contact","tcp_end":[0.52442,0.11755,0.1071],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09321,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":534.0,"n_steps_budget":960.0,"object_pos_end":[0.50587,0.06163,0.03488],"object_pos_start":[0.50603,0.06298,0.03381],"object_to_goal_dist_end":0.14185,"object_to_goal_dist_start":0.14324,"object_z_max":0.03483,"peak_contact_force":0.39402,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":549.0,"raw_peak_contact_force":8.97059,"subtask_id":"pre_contact","tcp_end":[0.50248,0.09153,0.03055],"tcp_start":[0.52442,0.11755,0.1071],"tcp_to_object_dist_end":0.0304,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":131.0,"n_steps_budget":660.0,"object_pos_end":[0.50699,0.04249,0.03541],"object_pos_start":[0.50587,0.06163,0.03488],"object_to_goal_dist_end":0.12278,"object_to_goal_dist_start":0.14185,"object_z_max":0.03583,"peak_contact_force":3912.28033,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":267.0,"raw_peak_contact_force":16.62323,"subtask_id":"push_complete","tcp_end":[0.49874,0.0716,0.02621],"tcp_start":[0.50248,0.09153,0.03055],"tcp_to_object_dist_end":0.03163,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":845.0,"n_steps_budget":930.0,"object_pos_end":[0.5067,0.04094,0.03384],"object_pos_start":[0.50699,0.04249,0.03541],"object_to_goal_dist_end":0.12128,"object_to_goal_dist_start":0.12278,"object_z_max":0.03546,"peak_contact_force":0.54678,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":860.0,"raw_peak_contact_force":2.34528,"tcp_end":[0.49581,0.07119,0.16482],"tcp_start":[0.49874,0.0716,0.02621],"tcp_to_object_dist_end":0.13487,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30508,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.0553,"descend_1.descend_arc_height":0.06915,"descend_1.descend_speed":0.0651,"push_1.force_threshold":24.00557,"push_1.push_distance":0.14177,"push_1.push_speed":0.05975},"optimized_scores":{"best_composite_score":0.11623,"best_fitness_score":0.47623,"best_task_score":0.12848},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":177.0,"contact_point_centroid":[0.51423,0.0725,0.05438],"force_p95":199.59763,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":217.03394,"mean_force":128.40726,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50468,0.07795,0.05313]},{"body_a":"peg","body_b":"channel_base_body","contact_count":539.0,"contact_point_centroid":[0.50845,0.06088,0.00903],"force_p95":179.03443,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":204.78417,"mean_force":41.36599,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50949,0.08698,0.07638]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":147.0,"contact_point_centroid":[0.52535,0.05788,0.05705],"force_p95":41.75228,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":63.83963,"mean_force":17.70363,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50523,0.07805,0.05262]},{"body_a":"peg","body_b":"channel_base_body","contact_count":982.0,"contact_point_centroid":[0.49651,-0.01216,0.00931],"force_p95":2.51768,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.60893,"mean_force":0.87555,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50499,0.03192,0.0379]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":165.0,"contact_point_centroid":[0.47499,-0.04219,0.02747],"force_p95":3.74147,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.18644,"mean_force":2.38035,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50485,0.01685,0.03774]},{"body_a":"peg","body_b":"channel_base_body","contact_count":873.0,"contact_point_centroid":[0.49965,-0.05325,0.00815],"force_p95":0.72691,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.01579,"mean_force":0.70011,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50165,-0.01661,0.10637]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":11.0,"contact_point_centroid":[0.52501,-0.03291,0.02435],"force_p95":5.68164,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.87744,"mean_force":3.14676,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50132,-0.01661,0.06163]},{"body_a":"attachment","body_b":"peg","contact_count":543.0,"contact_point_centroid":[0.50341,0.00269,0.03792],"force_p95":4.04349,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.64039,"mean_force":1.21141,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50485,0.01455,0.03774]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":23.0,"contact_point_centroid":[0.47499,-0.07448,0.02521],"force_p95":5.55684,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.60846,"mean_force":2.80174,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50244,-0.0167,0.11621]},{"body_a":"peg","body_b":"channel_base_body","contact_count":722.0,"contact_point_centroid":[0.50596,0.05662,0.00936],"force_p95":0.60125,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56867,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51498,0.15404,0.19852]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49993,0.19831,0.29629]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.5027,-0.02847,0.038],"force_p95":1.26507,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.2874,"mean_force":1.06413,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50485,-0.0167,0.03774]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52501,0.02712,0.06],"force_p95":0.58908,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60038,"mean_force":0.49031,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50706,0.0794,0.04044]}],"total_contact_groups":13},"final_pose_error":0.01158,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49774,-0.05445,0.02413],"final_tcp_position":[0.50198,-0.01659,0.17654],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":217.03394,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":751.0,"n_steps_budget":1000.0,"object_pos_end":[0.50609,0.0566,0.03376],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.5939,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":759.0,"raw_peak_contact_force":4.44541,"subtask_id":"pre_contact","tcp_end":[0.5309,0.11142,0.10651],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09441,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":539.0,"n_steps_budget":810.0,"object_pos_end":[0.50452,0.04763,0.03481],"object_pos_start":[0.50609,0.0566,0.03376],"object_to_goal_dist_end":0.12781,"object_to_goal_dist_start":0.13688,"object_z_max":0.0344,"peak_contact_force":0.43416,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":863.0,"raw_peak_contact_force":217.03394,"subtask_id":"pre_contact","tcp_end":[0.50872,0.08097,0.04243],"tcp_start":[0.5309,0.11142,0.10651],"tcp_to_object_dist_end":0.03446,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49759,-0.05286,0.0277],"object_pos_start":[0.50452,0.04763,0.03481],"object_to_goal_dist_end":0.0299,"object_to_goal_dist_start":0.12781,"object_z_max":0.04073,"peak_contact_force":0.16582,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1693.0,"raw_peak_contact_force":9.60893,"subtask_id":"push_complete","tcp_end":[0.50486,-0.01667,0.03775],"tcp_start":[0.50872,0.08097,0.04243],"tcp_to_object_dist_end":0.03826,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":873.0,"n_steps_budget":960.0,"object_pos_end":[0.49774,-0.05445,0.02413],"object_pos_start":[0.49759,-0.05286,0.0277],"object_to_goal_dist_end":0.03016,"object_to_goal_dist_start":0.0299,"object_z_max":0.0277,"peak_contact_force":0.60183,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":909.0,"raw_peak_contact_force":6.01579,"tcp_end":[0.50198,-0.01659,0.17654],"tcp_start":[0.50486,-0.01667,0.03775],"tcp_to_object_dist_end":0.15709,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```