## Search State

- **Seed**: 8
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.4029 | 0.50 | ✅ accepted |

**Proposal policy**: task_score is 0.50 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.403) — your mutation base

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

- **Composite score**: 0.403
- **task_score** (E): 0.499
- **fitness_score**: 0.613  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2067 |
| descend_1 | 1.00 | 1.00 | 0.0782 |
| push_1 | 1.00 | 1.00 | 0.1451 |
| retract_1 | 1.00 | 1.00 | 0.1387 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.133, 0.108) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.561 | 3.526 |
| descend_1 | descend | 1.00 / step_budget | (0.513, 0.133, 0.108)→(0.500, 0.107, 0.037) | (0.503, 0.080, 0.034)→(0.501, 0.077, 0.034) | 0.160→0.157 | 1.00 / 1.333 | 1.416 | 109.985 |
| push_1 | push | 1.00 / step_budget | (0.500, 0.107, 0.037)→(0.497, -0.038, 0.032) | (0.501, 0.077, 0.034)→(0.498, -0.067, 0.036) | 0.157→0.020 | 1.00 / 1.667 | 2.609 | 32.283 |
| retract_1 | retract | 1.00 / step_budget | (0.497, -0.038, 0.032)→(0.494, -0.038, 0.171) | (0.498, -0.067, 0.036)→(0.502, -0.063, 0.034) | 0.020→0.022 | 1.00 / 1.000 | 0.546 | 99.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.906
- phase_score: 0.527
- phase_breakdown.pre_contact_score: 0.864
- phase_breakdown.push_complete_score: 0.382

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.678
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.906
- **Median Q (composite search score)**: 0.401
- **K-run variance**: 0.0028
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.443


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4881,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.05545,"push_1.push_distance":0.17325,"push_1.push_speed":0.08542},"optimized_scores":{"best_composite_score":0.46832,"best_fitness_score":0.67832,"best_task_score":0.90587},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":130.0,"contact_point_centroid":[0.47498,-0.00964,0.04641],"force_p95":189.84441,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":261.76865,"mean_force":120.74748,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48681,-0.00964,0.04448]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":54.0,"contact_point_centroid":[0.47485,0.06229,0.038],"force_p95":25.94543,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.01813,"mean_force":6.29114,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48898,0.09216,0.03194]},{"body_a":"attachment","body_b":"peg","contact_count":255.0,"contact_point_centroid":[0.49263,0.05605,0.05191],"force_p95":16.81796,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.95667,"mean_force":2.59787,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48834,0.06748,0.03106]},{"body_a":"peg","body_b":"channel_base_body","contact_count":167.0,"contact_point_centroid":[0.49703,0.02662,0.00941],"force_p95":8.0936,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.96227,"mean_force":2.78607,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48835,0.06787,0.03106]},{"body_a":"peg","body_b":"channel_base_body","contact_count":451.0,"contact_point_centroid":[0.49607,0.11698,0.00946],"force_p95":0.7229,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.7519,"mean_force":0.65638,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48635,0.15723,0.07071]},{"body_a":"attachment","body_b":"peg","contact_count":23.0,"contact_point_centroid":[0.49312,0.1352,0.04946],"force_p95":5.2274,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.55021,"mean_force":2.57211,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49045,0.14709,0.04104]},{"body_a":"peg","body_b":"channel_base_body","contact_count":601.0,"contact_point_centroid":[0.49617,0.11905,0.00939],"force_p95":0.60009,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55613,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.491,0.18431,0.2011]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47483,0.11529,0.05847],"force_p95":1.25257,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.27323,"mean_force":0.43495,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49118,0.14547,0.03629]},{"body_a":"peg","body_b":"channel_base_body","contact_count":836.0,"contact_point_centroid":[0.49394,-0.04397,0.00943],"force_p95":0.61864,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.98361,"mean_force":0.54616,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48521,-0.0094,0.10004]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49951,0.19933,0.29793]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.49319,-0.02174,0.06037],"force_p95":0.42437,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.57207,"mean_force":0.12142,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48759,-0.01003,0.03061]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":204.0,"contact_point_centroid":[0.47496,-0.04351,0.05387],"force_p95":0.38601,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48844,"mean_force":0.08004,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48558,-0.00949,0.08812]}],"total_contact_groups":12},"final_pose_error":0.01148,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49313,-0.04335,0.03381],"final_tcp_position":[0.48503,-0.00934,0.16943],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":261.76865,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":626.0,"n_steps_budget":1000.0,"object_pos_end":[0.49609,0.11899,0.03384],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19913,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.59462,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":625.0,"raw_peak_contact_force":2.24822,"subtask_id":"pre_contact","tcp_end":[0.48403,0.17013,0.10962],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09222,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":459.0,"n_steps_budget":600.0,"object_pos_end":[0.49366,0.11516,0.03387],"object_pos_start":[0.49609,0.11899,0.03384],"object_to_goal_dist_end":0.19536,"object_to_goal_dist_start":0.19913,"object_z_max":0.03587,"peak_contact_force":3.23673,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":482.0,"raw_peak_contact_force":8.7519,"subtask_id":"pre_contact","tcp_end":[0.49133,0.14498,0.03494],"tcp_start":[0.48403,0.17013,0.10962],"tcp_to_object_dist_end":0.02993,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":372.0,"n_steps_budget":1000.0,"object_pos_end":[0.49387,-0.03816,0.03528],"object_pos_start":[0.49366,0.11516,0.03387],"object_to_goal_dist_end":0.04255,"object_to_goal_dist_start":0.19536,"object_z_max":0.03842,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":476.0,"raw_peak_contact_force":29.01813,"subtask_id":"push_complete","tcp_end":[0.4879,-0.0094,0.03054],"tcp_start":[0.49133,0.14498,0.03494],"tcp_to_object_dist_end":0.02975,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":845.0,"n_steps_budget":930.0,"object_pos_end":[0.49313,-0.04335,0.03381],"object_pos_start":[0.49387,-0.03816,0.03528],"object_to_goal_dist_end":0.0378,"object_to_goal_dist_start":0.04255,"object_z_max":0.03634,"peak_contact_force":0.54321,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1178.0,"raw_peak_contact_force":261.76865,"tcp_end":[0.48503,-0.00934,0.16943],"tcp_start":[0.4879,-0.0094,0.03054],"tcp_to_object_dist_end":0.14005,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.92884,"average_solve_count":267.0,"average_success_count":267.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.04645,"push_1.push_distance":0.16048,"push_1.push_speed":0.01786},"optimized_scores":{"best_composite_score":0.40091,"best_fitness_score":0.61091,"best_task_score":0.37122},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":151.0,"contact_point_centroid":[0.5046,-0.0142,0.00985],"force_p95":17.35286,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.26189,"mean_force":5.99154,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50126,0.02942,0.03364]},{"body_a":"attachment","body_b":"peg","contact_count":268.0,"contact_point_centroid":[0.50434,0.00688,0.04552],"force_p95":17.47934,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.73639,"mean_force":4.27832,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50092,0.0187,0.0332]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":218.0,"contact_point_centroid":[0.52516,-0.01808,0.03009],"force_p95":13.79019,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.14358,"mean_force":2.29554,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50072,0.01119,0.03293]},{"body_a":"peg","body_b":"channel_base_body","contact_count":336.0,"contact_point_centroid":[0.50582,0.06206,0.0094],"force_p95":0.55398,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.82824,"mean_force":0.77434,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5135,0.1044,0.07169]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.50594,0.08008,0.04782],"force_p95":13.91894,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.52084,"mean_force":5.85525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50507,0.09208,0.04055]},{"body_a":"peg","body_b":"channel_base_body","contact_count":705.0,"contact_point_centroid":[0.50576,0.06297,0.00936],"force_p95":0.55958,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56576,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5116,0.15737,0.19925]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49983,0.19853,0.29675]},{"body_a":"peg","body_b":"channel_base_body","contact_count":845.0,"contact_point_centroid":[0.50669,-0.08139,0.00941],"force_p95":0.55604,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73607,"mean_force":0.54437,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49743,-0.05047,0.1012]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":228.0,"contact_point_centroid":[0.52501,-0.08097,0.055],"force_p95":0.26416,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4986,"mean_force":0.03023,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49758,-0.05053,0.09642]},{"body_a":"peg","body_b":"channel_base_body","contact_count":18.0,"contact_point_centroid":[0.50654,-0.1004,0.05974],"force_p95":0.44895,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46645,"mean_force":0.10588,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49958,-0.05153,0.03381]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.50429,-0.0632,0.05979],"force_p95":0.40307,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41406,"mean_force":0.18083,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49878,-0.05129,0.03628]}],"total_contact_groups":11},"final_pose_error":0.01177,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50692,-0.08099,0.03379],"final_tcp_position":[0.49776,-0.05042,0.17136],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":23.26189,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":733.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.06304,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1433,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54531,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":739.0,"raw_peak_contact_force":3.88411,"subtask_id":"pre_contact","tcp_end":[0.52442,0.11757,0.10711],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0932,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":336.0,"n_steps_budget":600.0,"object_pos_end":[0.50484,0.06053,0.03498],"object_pos_start":[0.50598,0.06304,0.03381],"object_to_goal_dist_end":0.14071,"object_to_goal_dist_start":0.1433,"object_z_max":0.03501,"peak_contact_force":0.37837,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":350.0,"raw_peak_contact_force":15.82824,"subtask_id":"pre_contact","tcp_end":[0.50426,0.09087,0.03744],"tcp_start":[0.52442,0.11757,0.10711],"tcp_to_object_dist_end":0.03044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":387.0,"n_steps_budget":1000.0,"object_pos_end":[0.50667,-0.0806,0.03538],"object_pos_start":[0.50484,0.06053,0.03498],"object_to_goal_dist_end":0.00813,"object_to_goal_dist_start":0.14071,"object_z_max":0.03684,"peak_contact_force":0.77141,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":637.0,"raw_peak_contact_force":23.26189,"subtask_id":"push_complete","tcp_end":[0.50066,-0.05068,0.03276],"tcp_start":[0.50426,0.09087,0.03744],"tcp_to_object_dist_end":0.03063,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":845.0,"n_steps_budget":930.0,"object_pos_end":[0.50692,-0.08099,0.03379],"object_pos_start":[0.50667,-0.0806,0.03538],"object_to_goal_dist_end":0.00935,"object_to_goal_dist_start":0.00813,"object_z_max":0.03554,"peak_contact_force":0.54684,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1100.0,"raw_peak_contact_force":0.73607,"tcp_end":[0.49776,-0.05042,0.17136],"tcp_start":[0.50066,-0.05068,0.03276],"tcp_to_object_dist_end":0.14122,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.62651,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06167,"push_1.push_distance":0.15844,"push_1.push_speed":0.08105},"optimized_scores":{"best_composite_score":0.33943,"best_fitness_score":0.54943,"best_task_score":0.21938},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52523,0.09402,0.05995],"force_p95":304.91991,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":305.3738,"mean_force":200.08555,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51335,0.09413,0.06085]},{"body_a":"attachment","body_b":"peg","contact_count":234.0,"contact_point_centroid":[0.50089,0.00355,0.04615],"force_p95":37.33784,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.56923,"mean_force":6.38677,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50224,0.01475,0.03364]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":113.0,"contact_point_centroid":[0.47468,-0.04406,0.03969],"force_p95":41.65333,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.26152,"mean_force":10.99683,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50211,-0.01595,0.03332]},{"body_a":"attachment","body_b":"peg","contact_count":245.0,"contact_point_centroid":[0.49814,-0.06425,0.055],"force_p95":20.64102,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.86562,"mean_force":13.3553,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49969,-0.05266,0.05465]},{"body_a":"peg","body_b":"channel_base_body","contact_count":269.0,"contact_point_centroid":[0.49315,-0.10046,0.06007],"force_p95":19.53699,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.80509,"mean_force":12.07676,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49983,-0.05282,0.05408]},{"body_a":"peg","body_b":"channel_base_body","contact_count":145.0,"contact_point_centroid":[0.49711,-0.01493,0.0094],"force_p95":7.07853,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.90346,"mean_force":2.54998,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50225,0.02352,0.03378]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":89.0,"contact_point_centroid":[0.47486,-0.08183,0.05825],"force_p95":8.7845,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.14637,"mean_force":2.20156,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49988,-0.05284,0.04764]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.49171,-0.10038,0.06314],"force_p95":16.4657,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.96093,"mean_force":12.00867,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50304,-0.05383,0.03384]},{"body_a":"peg","body_b":"channel_base_body","contact_count":339.0,"contact_point_centroid":[0.50609,0.0558,0.00939],"force_p95":0.56273,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.85658,"mean_force":0.67465,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51722,0.0982,0.07124]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.50665,0.07383,0.04617],"force_p95":12.2659,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.32739,"mean_force":4.32308,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50624,0.08581,0.04054]},{"body_a":"peg","body_b":"channel_base_body","contact_count":708.0,"contact_point_centroid":[0.50597,0.0566,0.00936],"force_p95":0.6009,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56905,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51498,0.15405,0.19855]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49997,0.19826,0.29624]},{"body_a":"peg","body_b":"channel_base_body","contact_count":551.0,"contact_point_centroid":[0.50318,-0.0632,0.0095],"force_p95":0.72281,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.29687,"mean_force":0.55757,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49973,-0.05404,0.12653]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":196.0,"contact_point_centroid":[0.52507,-0.06376,0.04363],"force_p95":0.63817,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.38224,"mean_force":0.20524,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49966,-0.054,0.11669]}],"total_contact_groups":14},"final_pose_error":0.01182,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50686,-0.0636,0.0338],"final_tcp_position":[0.5001,-0.05412,0.17235],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":305.3738,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":737.0,"n_steps_budget":1000.0,"object_pos_end":[0.5061,0.05659,0.03379],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.54244,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":745.0,"raw_peak_contact_force":4.44541,"subtask_id":"pre_contact","tcp_end":[0.5309,0.11142,0.1065],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09438,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":339.0,"n_steps_budget":600.0,"object_pos_end":[0.50531,0.05451,0.0344],"object_pos_start":[0.5061,0.05659,0.03379],"object_to_goal_dist_end":0.13473,"object_to_goal_dist_start":0.13687,"object_z_max":0.03444,"peak_contact_force":0.63439,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":366.0,"raw_peak_contact_force":305.3738,"subtask_id":"pre_contact","tcp_end":[0.50521,0.08463,0.03764],"tcp_start":[0.5309,0.11142,0.1065],"tcp_to_object_dist_end":0.03029,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":348.0,"n_steps_budget":1000.0,"object_pos_end":[0.49227,-0.08288,0.03845],"object_pos_start":[0.50531,0.05451,0.0344],"object_to_goal_dist_end":0.00839,"object_to_goal_dist_start":0.13473,"object_z_max":0.04019,"peak_contact_force":7.0564,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":494.0,"raw_peak_contact_force":44.56923,"subtask_id":"push_complete","tcp_end":[0.503,-0.0544,0.03381],"tcp_start":[0.50521,0.08463,0.03764],"tcp_to_object_dist_end":0.03078,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":846.0,"n_steps_budget":930.0,"object_pos_end":[0.50686,-0.0636,0.0338],"object_pos_start":[0.49227,-0.08288,0.03845],"object_to_goal_dist_end":0.01882,"object_to_goal_dist_start":0.00839,"object_z_max":0.05529,"peak_contact_force":0.54745,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1350.0,"raw_peak_contact_force":34.86562,"tcp_end":[0.5001,-0.05412,0.17235],"tcp_start":[0.503,-0.0544,0.03381],"tcp_to_object_dist_end":0.13904,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```