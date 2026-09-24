## Search State

- **Seed**: 0
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.5969 | 0.75 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.5839 | 0.64 | ❌ rejected |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.2627 | 0.59 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.1421 | 0.06 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6127 | 0.72 | ❌ rejected |

**Proposal policy**: task_score is 0.75 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`
- Frozen object start: [0.5109569349857164, 0.061582937101109625, 0.04]
- Frozen task target: [0.5109569349857164, -0.09841706289889038, 0.04]
- Goal object position: (0.5109569349857164, -0.09841706289889038, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5109569349857164, 0.061582937101109625, 0.04)
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
  frozen_object_start: [0.511, 0.0616, 0.04]
  frozen_task_target: [0.511, -0.0984, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5109569349857164, 0.061582937101109625, 0.04]}
  frozen_targets: {'channel_exit': [0.5109569349857164, -0.09841706289889038, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.781, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5109569349857164, 0.061582937101109625, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5109569349857164, -0.09841706289889038, 0.04) | final destination targets |
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

## Current Skill (Q=0.597) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.04
  - 0.06
  weight: 0.3
- id: insertion_goal
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
    entity: peg
    offset:
    - 0.0
    - 0.04
    - 0.06
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.03
      - 0.1
      default: 0.06
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: pre_contact
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.025
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
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
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: insertion_goal
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.06], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.025, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.597
- **task_score** (E): 0.751
- **fitness_score**: 0.690  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2024 |
| contact_1 | 0.67 | 1.00 | 0.0764 |
| push_1 | 1.00 | 1.00 | 0.1639 |
| retract_1 | 1.00 | 1.00 | 0.0892 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.125, 0.114) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.574 | 2.179 |
| contact_1 | contact | 0.67 / force_exceeded | (0.495, 0.125, 0.114)→(0.496, 0.108, 0.040) | (0.500, 0.081, 0.034)→(0.501, 0.078, 0.035) | 0.161→0.158 | 1.00 / 1.667 | 6.630 | 9.840 |
| push_1 | push | 1.00 / step_budget | (0.496, 0.108, 0.040)→(0.493, -0.056, 0.036) | (0.501, 0.078, 0.035)→(0.506, -0.060, 0.030) | 0.158→0.029 | 1.00 / 3.333 | 146.347 | 204.030 |
| retract_1 | retract | 1.00 / step_budget | (0.493, -0.056, 0.036)→(0.490, -0.056, 0.126) | (0.506, -0.060, 0.030)→(0.501, -0.059, 0.027) | 0.029→0.029 | 1.00 / 1.000 | 0.552 | 195.876 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.845
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.781
- phase_score: 0.907
- phase_breakdown.insertion_goal_score: 0.919
- phase_breakdown.pre_contact_score: 0.878

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.857
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.886
- **Median Q (composite search score)**: 0.598
- **K-run variance**: 0.0418
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.358


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d6915c31707ac435a9367b840736087e39a7a48adfeb36a4f94b6b3ae57cce94`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `19172182883d287409b73cab43749e937e65f1ca1d4501d52b4a913a881aad36`; realized-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51096,0.06158,0.04]},{"name":"goal","value":[0.51096,-0.09842,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51096,0.06158,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51096,-0.09842,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44324,"average_solve_count":185.0,"average_success_count":185.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05195,"contact_1.contact_force":9.72095,"push_1.insertion_depth":0.18603,"push_1.push_speed":0.03914},"optimized_scores":{"best_composite_score":0.84659,"best_fitness_score":0.85659,"best_task_score":0.78079},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":419.0,"contact_point_centroid":[0.49785,-0.02853,0.00932],"force_p95":62.60253,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.00407,"mean_force":30.73981,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49912,-0.00091,0.04082]},{"body_a":"attachment","body_b":"peg","contact_count":369.0,"contact_point_centroid":[0.49847,-0.018,0.04211],"force_p95":62.1923,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":72.81547,"mean_force":36.90829,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49921,-0.00647,0.04091]},{"body_a":"peg","body_b":"channel_base_body","contact_count":92.0,"contact_point_centroid":[0.48145,-0.10038,0.02476],"force_p95":39.05667,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.62294,"mean_force":23.50359,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50047,-0.05919,0.04197]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.49823,-0.08265,0.04208],"force_p95":27.25306,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.99626,"mean_force":8.08023,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49978,-0.07652,0.04158]},{"body_a":"peg","body_b":"channel_base_body","contact_count":544.0,"contact_point_centroid":[0.5013,-0.07212,0.00815],"force_p95":0.86573,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.45527,"mean_force":0.87764,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49706,-0.07564,0.08528]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":54.0,"contact_point_centroid":[0.47477,-0.00092,0.03117],"force_p95":16.39446,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.43575,"mean_force":3.37633,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49823,0.01098,0.03963]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":15.0,"contact_point_centroid":[0.47487,-0.04954,0.02464],"force_p95":12.92576,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.92512,"mean_force":4.2491,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49924,-0.0767,0.04245]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.50268,0.07907,0.0538],"force_p95":9.02694,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.19718,"mean_force":4.2903,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50079,0.09106,0.04585]},{"body_a":"peg","body_b":"channel_base_body","contact_count":289.0,"contact_point_centroid":[0.50378,0.06039,0.00939],"force_p95":0.55626,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.17849,"mean_force":0.65471,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50273,0.09849,0.07061]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":21.0,"contact_point_centroid":[0.525,-0.09628,0.02452],"force_p95":7.53087,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.63803,"mean_force":3.99097,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49698,-0.07554,0.11585]},{"body_a":"peg","body_b":"channel_base_body","contact_count":16.0,"contact_point_centroid":[0.48731,-0.10006,0.02548],"force_p95":2.12122,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.16591,"mean_force":0.70837,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49757,-0.07568,0.10571]},{"body_a":"peg","body_b":"channel_base_body","contact_count":671.0,"contact_point_centroid":[0.50366,0.06156,0.00935],"force_p95":0.58261,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55864,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50276,0.1519,0.19547]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49977,0.19901,0.29841]}],"total_contact_groups":13},"final_pose_error":0.01143,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50437,-0.07365,0.02438],"final_tcp_position":[0.49712,-0.07556,0.13046],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":73.00407,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":694.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.06157,0.03379],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14176,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.54833,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":690.0,"raw_peak_contact_force":2.17216,"subtask_id":"pre_contact","tcp_end":[0.50702,0.10669,0.09934],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07964,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":289.0,"n_steps_budget":600.0,"object_pos_end":[0.50337,0.06066,0.03486],"object_pos_start":[0.50372,0.06157,0.03379],"object_to_goal_dist_end":0.14079,"object_to_goal_dist_start":0.14176,"object_z_max":0.03476,"peak_contact_force":10.19718,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":297.0,"raw_peak_contact_force":10.19718,"tcp_end":[0.50068,0.09035,0.04344],"tcp_start":[0.50702,0.10669,0.09934],"tcp_to_object_dist_end":0.03102,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":481.0,"n_steps_budget":1000.0,"object_pos_end":[0.49524,-0.07385,0.02481],"object_pos_start":[0.50337,0.06066,0.03486],"object_to_goal_dist_end":0.01707,"object_to_goal_dist_start":0.14079,"object_z_max":0.04045,"peak_contact_force":62.61311,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":934.0,"raw_peak_contact_force":73.00407,"subtask_id":"insertion_goal","tcp_end":[0.50009,-0.07607,0.04148],"tcp_start":[0.50068,0.09035,0.04344],"tcp_to_object_dist_end":0.01751,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":544.0,"n_steps_budget":630.0,"object_pos_end":[0.50437,-0.07365,0.02438],"object_pos_start":[0.49524,-0.07385,0.02481],"object_to_goal_dist_end":0.01742,"object_to_goal_dist_start":0.01707,"object_z_max":0.02504,"peak_contact_force":0.60169,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":604.0,"raw_peak_contact_force":31.99626,"tcp_end":[0.49712,-0.07556,0.13046],"tcp_start":[0.50009,-0.07607,0.04148],"tcp_to_object_dist_end":0.10634,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `f24211f27d4adabdef509c8ed61621317fdbcaa86fc9ac888f85a717335bb714`; realized-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,0.11604,0.04]},{"name":"goal","value":[0.50095,-0.04396,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.11604,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50095,-0.04396,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09314,"average_solve_count":204.0,"average_success_count":204.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05404,"contact_1.contact_force":6.14051,"push_1.insertion_depth":0.16595,"push_1.push_speed":0.02299},"optimized_scores":{"best_composite_score":0.59825,"best_fitness_score":0.60825,"best_task_score":0.8861},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_left_wall","contact_count":256.0,"contact_point_centroid":[0.52549,0.02818,0.03163],"force_p95":38.79212,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.69878,"mean_force":6.29133,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49285,0.05429,0.03694]},{"body_a":"attachment","body_b":"peg","contact_count":216.0,"contact_point_centroid":[0.49926,0.05217,0.04658],"force_p95":40.81971,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.68302,"mean_force":9.41373,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49294,0.0628,0.03699]},{"body_a":"peg","body_b":"channel_base_body","contact_count":162.0,"contact_point_centroid":[0.50493,0.0351,0.00967],"force_p95":19.99748,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.998,"mean_force":5.18825,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49317,0.07655,0.03724]},{"body_a":"peg","body_b":"channel_base_body","contact_count":319.0,"contact_point_centroid":[0.50097,0.11298,0.00947],"force_p95":0.63238,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.43048,"mean_force":0.72415,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4959,0.15051,0.07185]},{"body_a":"attachment","body_b":"peg","contact_count":20.0,"contact_point_centroid":[0.49895,0.13248,0.05326],"force_p95":6.43363,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.32824,"mean_force":3.33546,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4964,0.14433,0.04632]},{"body_a":"peg","body_b":"channel_base_body","contact_count":593.0,"contact_point_centroid":[0.50098,0.116,0.00938],"force_p95":0.61232,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55729,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49804,0.17842,0.19899]},{"body_a":"peg","body_b":"channel_base_body","contact_count":545.0,"contact_point_centroid":[0.50661,-0.03246,0.00945],"force_p95":0.60693,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.67816,"mean_force":0.5479,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49015,-0.00386,0.08121]},{"body_a":"attachment","body_b":"peg","contact_count":21.0,"contact_point_centroid":[0.49865,-0.01503,0.0601],"force_p95":0.57856,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.57967,"mean_force":0.30059,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49091,-0.0043,0.04389]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":13.0,"contact_point_centroid":[0.52512,-0.03053,0.04487],"force_p95":0.36332,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38612,"mean_force":0.14595,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49151,-0.00426,0.04214]}],"total_contact_groups":9},"final_pose_error":0.01111,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50663,-0.03069,0.03386],"final_tcp_position":[0.4902,-0.00376,0.1265],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":44.69878,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":609.0,"n_steps_budget":1000.0,"object_pos_end":[0.5009,0.11608,0.03383],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19618,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.62577,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":593.0,"raw_peak_contact_force":1.92055,"subtask_id":"pre_contact","tcp_end":[0.49771,0.15805,0.10326],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08119,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":325.0,"n_steps_budget":600.0,"object_pos_end":[0.50193,0.1139,0.03511],"object_pos_start":[0.5009,0.11608,0.03383],"object_to_goal_dist_end":0.19398,"object_to_goal_dist_start":0.19618,"object_z_max":0.03567,"peak_contact_force":9.26378,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":339.0,"raw_peak_contact_force":11.43048,"tcp_end":[0.4966,0.1432,0.04154],"tcp_start":[0.49771,0.15805,0.10326],"tcp_to_object_dist_end":0.03047,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":404.0,"n_steps_budget":1000.0,"object_pos_end":[0.50728,-0.03093,0.03646],"object_pos_start":[0.50193,0.1139,0.03511],"object_to_goal_dist_end":0.04973,"object_to_goal_dist_start":0.19398,"object_z_max":0.04089,"peak_contact_force":2.22738,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":634.0,"raw_peak_contact_force":44.69878,"subtask_id":"insertion_goal","tcp_end":[0.49314,-0.00389,0.03721],"tcp_start":[0.4966,0.1432,0.04154],"tcp_to_object_dist_end":0.03052,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":545.0,"n_steps_budget":630.0,"object_pos_end":[0.50663,-0.03069,0.03386],"object_pos_start":[0.50728,-0.03093,0.03646],"object_to_goal_dist_end":0.05013,"object_to_goal_dist_start":0.04973,"object_z_max":0.03655,"peak_contact_force":0.54606,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":579.0,"raw_peak_contact_force":1.67816,"tcp_end":[0.4902,-0.00376,0.1265],"tcp_start":[0.49314,-0.00389,0.03721],"tcp_to_object_dist_end":0.09786,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d098a7862ff18c9bbe982af3446a89a0fa6bcfa8790d7d955f65b2375d67a881`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38725,"average_solve_count":204.0,"average_success_count":204.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09302,"contact_1.contact_force":9.36841,"push_1.insertion_depth":0.19721,"push_1.push_speed":0.02984},"optimized_scores":{"best_composite_score":0.34596,"best_fitness_score":0.60596,"best_task_score":0.58683},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":146.0,"contact_point_centroid":[0.47494,-0.08631,0.04437],"force_p95":397.79924,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":553.95397,"mean_force":241.90791,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48675,-0.08628,0.04256]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":23.0,"contact_point_centroid":[0.49197,-0.10031,0.065],"force_p95":487.06208,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":494.38726,"mean_force":381.07656,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48672,-0.08831,0.03064]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":11.0,"contact_point_centroid":[0.492,-0.10018,0.065],"force_p95":438.57687,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":457.35413,"mean_force":213.92089,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4868,-0.08802,0.03084]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":551.0,"contact_point_centroid":[0.47498,-0.02898,0.03399],"force_p95":164.29203,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":433.13149,"mean_force":108.57328,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48683,-0.02898,0.0322]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":856.0,"contact_point_centroid":[0.52736,-0.02905,0.02945],"force_p95":124.47914,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":134.2905,"mean_force":68.34044,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48685,-0.01954,0.03219]},{"body_a":"attachment","body_b":"peg","contact_count":842.0,"contact_point_centroid":[0.49667,-0.02314,0.03217],"force_p95":124.00427,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":131.14495,"mean_force":76.15062,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48686,-0.01973,0.03222]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":117.0,"contact_point_centroid":[0.52777,-0.08068,0.02792],"force_p95":118.07406,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":127.04821,"mean_force":53.98271,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48675,-0.08641,0.03789]},{"body_a":"attachment","body_b":"peg","contact_count":99.0,"contact_point_centroid":[0.49793,-0.08649,0.03484],"force_p95":111.37859,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":119.0062,"mean_force":57.16957,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48674,-0.08655,0.03636]},{"body_a":"peg","body_b":"channel_base_body","contact_count":717.0,"contact_point_centroid":[0.51012,-0.0247,0.00962],"force_p95":73.41601,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.62186,"mean_force":37.70524,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48691,-0.00597,0.03243]},{"body_a":"peg","body_b":"link7","contact_count":456.0,"contact_point_centroid":[0.51535,-0.02408,0.06937],"force_p95":42.89604,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.92465,"mean_force":23.61542,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48686,-0.00743,0.03277]},{"body_a":"peg","body_b":"channel_base_body","contact_count":87.0,"contact_point_centroid":[0.50986,-0.10012,0.02398],"force_p95":23.12614,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.21484,"mean_force":7.73898,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48682,-0.07929,0.03109]},{"body_a":"peg","body_b":"channel_base_body","contact_count":523.0,"contact_point_centroid":[0.49787,-0.07305,0.00852],"force_p95":29.78539,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.33482,"mean_force":4.15228,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48481,-0.08703,0.07567]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":62.0,"contact_point_centroid":[0.47488,-0.07363,0.02539],"force_p95":12.39797,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.93594,"mean_force":5.0224,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4844,-0.08712,0.07249]},{"body_a":"peg","body_b":"channel_base_body","contact_count":606.0,"contact_point_centroid":[0.49574,0.06097,0.00944],"force_p95":0.73062,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.89155,"mean_force":0.70093,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48351,0.09952,0.08631]},{"body_a":"attachment","body_b":"peg","contact_count":38.0,"contact_point_centroid":[0.49267,0.07972,0.05685],"force_p95":7.02966,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.51607,"mean_force":2.77855,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48884,0.09152,0.04564]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.49547,0.06399,0.00937],"force_p95":0.58331,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56121,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48861,0.15333,0.21588]}],"total_contact_groups":17},"final_pose_error":0.01123,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49343,-0.07272,0.02411],"final_tcp_position":[0.48378,-0.08759,0.1198],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":553.95397,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":570.0,"n_steps_budget":1000.0,"object_pos_end":[0.49489,0.06393,0.03394],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14415,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54873,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":571.0,"raw_peak_contact_force":2.44546,"subtask_id":"pre_contact","tcp_end":[0.47939,0.11006,0.14041],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11706,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":610.0,"n_steps_budget":690.0,"object_pos_end":[0.49718,0.06041,0.0351],"object_pos_start":[0.49489,0.06393,0.03394],"object_to_goal_dist_end":0.14053,"object_to_goal_dist_start":0.14415,"object_z_max":0.03568,"peak_contact_force":0.42811,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":644.0,"raw_peak_contact_force":7.89155,"tcp_end":[0.49012,0.08961,0.03587],"tcp_start":[0.47939,0.11006,0.14041],"tcp_to_object_dist_end":0.03005,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":921.0,"n_steps_budget":1000.0,"object_pos_end":[0.51409,-0.07443,0.02735],"object_pos_start":[0.49718,0.06041,0.0351],"object_to_goal_dist_end":0.01974,"object_to_goal_dist_start":0.14053,"object_z_max":0.03977,"peak_contact_force":374.20002,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3532.0,"raw_peak_contact_force":494.38726,"subtask_id":"insertion_goal","tcp_end":[0.48673,-0.08822,0.03062],"tcp_start":[0.49012,0.08961,0.03587],"tcp_to_object_dist_end":0.03081,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.49343,-0.07272,0.02411],"object_pos_start":[0.51409,-0.07443,0.02735],"object_to_goal_dist_end":0.01868,"object_to_goal_dist_start":0.01974,"object_z_max":0.0292,"peak_contact_force":0.50949,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":958.0,"raw_peak_contact_force":553.95397,"tcp_end":[0.48378,-0.08759,0.1198],"tcp_start":[0.48673,-0.08822,0.03062],"tcp_to_object_dist_end":0.09732,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```