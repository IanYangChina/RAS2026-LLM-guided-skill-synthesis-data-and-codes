## Search State

- **Seed**: 0
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6280 | 0.69 | ✅ accepted |

**Proposal policy**: task_score is 0.69 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.628) — your mutation base

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

- **Composite score**: 0.628
- **task_score** (E): 0.695
- **fitness_score**: 0.638  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2100 |
| contact_1 | 1.00 | 1.00 | 0.0642 |
| push_1 | 1.00 | 1.00 | 0.1617 |
| retract_1 | 1.00 | 1.00 | 0.0892 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.125, 0.106) | (0.498, 0.080, 0.040)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.534 | 2.179 |
| contact_1 | contact | 1.00 / force_exceeded | (0.495, 0.125, 0.106)→(0.495, 0.109, 0.045) | (0.500, 0.080, 0.034)→(0.500, 0.080, 0.035) | 0.161→0.160 | 1.00 / 2.000 | 8.572 | 8.572 |
| push_1 | push | 1.00 / step_budget | (0.495, 0.109, 0.045)→(0.494, -0.053, 0.042) | (0.500, 0.080, 0.035)→(0.505, -0.039, 0.029) | 0.160→0.045 | 1.00 / 2.000 | 40.285 | 94.375 |
| retract_1 | retract | 1.00 / step_budget | (0.494, -0.053, 0.042)→(0.491, -0.052, 0.131) | (0.505, -0.039, 0.029)→(0.499, -0.039, 0.027) | 0.045→0.046 | 1.00 / 1.000 | 0.622 | 124.200 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.891
- alignment_error: None
- force_efficiency: 0.539
- terminal_score: 0.887
- phase_score: 0.643
- phase_breakdown.insertion_goal_score: 0.576
- phase_breakdown.pre_contact_score: 0.799

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.741
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.887
- **Median Q (composite search score)**: 0.649
- **K-run variance**: 0.0088
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.403


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18408,"average_solve_count":201.0,"average_success_count":201.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.0432,"contact_1.contact_force":6.31394,"push_1.insertion_depth":0.16231,"push_1.push_speed":0.02901},"optimized_scores":{"best_composite_score":0.73057,"best_fitness_score":0.74057,"best_task_score":0.88739},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":206.0,"contact_point_centroid":[0.50163,0.00182,0.04887],"force_p95":15.11622,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.04232,"mean_force":3.35729,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49742,0.01322,0.03859]},{"body_a":"peg","body_b":"channel_base_body","contact_count":158.0,"contact_point_centroid":[0.50657,-0.01695,0.00952],"force_p95":16.17141,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.82627,"mean_force":4.56335,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49757,0.02686,0.03876]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":187.0,"contact_point_centroid":[0.52538,-0.01977,0.02547],"force_p95":5.59957,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.97357,"mean_force":0.99965,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49736,0.00876,0.03849]},{"body_a":"peg","body_b":"channel_base_body","contact_count":259.0,"contact_point_centroid":[0.5038,0.06072,0.00938],"force_p95":0.55606,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.25938,"mean_force":0.5943,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50282,0.0987,0.06619]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50313,0.07935,0.05698],"force_p95":7.26977,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.0579,"mean_force":3.40457,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50088,0.09138,0.04461]},{"body_a":"peg","body_b":"channel_base_body","contact_count":28.0,"contact_point_centroid":[0.50666,-0.10035,0.04096],"force_p95":4.60744,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.63818,"mean_force":1.90167,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4963,-0.05321,0.04018]},{"body_a":"attachment","body_b":"peg","contact_count":37.0,"contact_point_centroid":[0.50125,-0.0644,0.05746],"force_p95":3.23121,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.26053,"mean_force":0.75818,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49561,-0.05286,0.04317]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":12.0,"contact_point_centroid":[0.52508,-0.08245,0.04383],"force_p95":2.73085,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.14591,"mean_force":1.56954,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49687,-0.05319,0.03885]},{"body_a":"peg","body_b":"channel_base_body","contact_count":694.0,"contact_point_centroid":[0.50362,0.0616,0.00935],"force_p95":0.58234,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.5583,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50273,0.15178,0.19103]},{"body_a":"peg","body_b":"channel_base_body","contact_count":524.0,"contact_point_centroid":[0.50622,-0.08253,0.00943],"force_p95":0.61926,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.16992,"mean_force":0.55468,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49427,-0.0522,0.08411]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49977,0.19903,0.29839]}],"total_contact_groups":11},"final_pose_error":0.01132,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50587,-0.08104,0.03377],"final_tcp_position":[0.49442,-0.05216,0.12766],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":23.04232,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":717.0,"n_steps_budget":1000.0,"object_pos_end":[0.50378,0.06161,0.03379],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.1418,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.55246,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":713.0,"raw_peak_contact_force":2.17216,"subtask_id":"pre_contact","tcp_end":[0.50698,0.10652,0.09076],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07261,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":259.0,"n_steps_budget":600.0,"object_pos_end":[0.50372,0.06121,0.03416],"object_pos_start":[0.50378,0.06161,0.03379],"object_to_goal_dist_end":0.14138,"object_to_goal_dist_start":0.1418,"object_z_max":0.03411,"peak_contact_force":8.25938,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":263.0,"raw_peak_contact_force":8.25938,"tcp_end":[0.50075,0.09081,0.04299],"tcp_start":[0.50698,0.10652,0.09076],"tcp_to_object_dist_end":0.03103,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":393.0,"n_steps_budget":1000.0,"object_pos_end":[0.50701,-0.08026,0.03704],"object_pos_start":[0.50372,0.06121,0.03416],"object_to_goal_dist_end":0.00761,"object_to_goal_dist_start":0.14138,"object_z_max":0.03926,"peak_contact_force":1.79449,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":551.0,"raw_peak_contact_force":23.04232,"subtask_id":"insertion_goal","tcp_end":[0.49739,-0.05254,0.03857],"tcp_start":[0.50075,0.09081,0.04299],"tcp_to_object_dist_end":0.02938,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":545.0,"n_steps_budget":630.0,"object_pos_end":[0.50587,-0.08104,0.03377],"object_pos_start":[0.50701,-0.08026,0.03704],"object_to_goal_dist_end":0.00862,"object_to_goal_dist_start":0.00761,"object_z_max":0.0371,"peak_contact_force":0.53977,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":601.0,"raw_peak_contact_force":4.63818,"tcp_end":[0.49442,-0.05216,0.12766],"tcp_start":[0.49739,-0.05254,0.03857],"tcp_to_object_dist_end":0.0989,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.33171,"average_solve_count":205.0,"average_success_count":205.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.0402,"contact_1.contact_force":6.86927,"push_1.insertion_depth":0.19977,"push_1.push_speed":0.02768},"optimized_scores":{"best_composite_score":0.64935,"best_fitness_score":0.65935,"best_task_score":0.8618},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":470.0,"contact_point_centroid":[0.50238,0.03714,0.04273],"force_p95":100.01057,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":110.02789,"mean_force":55.46145,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49326,0.0424,0.04086]},{"body_a":"peg","body_b":"channel_base_body","contact_count":465.0,"contact_point_centroid":[0.50749,0.02149,0.00879],"force_p95":82.37676,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":88.19829,"mean_force":46.97994,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49335,0.04075,0.04103]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.49687,-0.0218,0.00817],"force_p95":0.77538,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.45196,"mean_force":1.0968,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49375,-0.03523,0.08751]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.50797,-0.03563,0.04329],"force_p95":26.63164,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":73.22375,"mean_force":5.61125,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49625,-0.03594,0.0441]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":411.0,"contact_point_centroid":[0.52579,0.03498,0.0292],"force_p95":68.66248,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":72.25631,"mean_force":32.17577,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49295,0.05122,0.04063]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":37.0,"contact_point_centroid":[0.47483,-0.02231,0.02526],"force_p95":11.60626,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.3204,"mean_force":5.45449,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49341,-0.03514,0.07126]},{"body_a":"peg","body_b":"channel_base_body","contact_count":257.0,"contact_point_centroid":[0.50079,0.11437,0.00944],"force_p95":0.64364,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.36658,"mean_force":0.62776,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49581,0.15099,0.06559]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.49912,0.13329,0.05735],"force_p95":7.86177,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.18811,"mean_force":3.13325,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49618,0.14524,0.04635]},{"body_a":"peg","body_b":"channel_base_body","contact_count":635.0,"contact_point_centroid":[0.50095,0.11605,0.00938],"force_p95":0.62835,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.5565,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49798,0.17827,0.19184]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.0034,0.02724],"force_p95":0.0,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49673,-0.03565,0.04345]}],"total_contact_groups":10},"final_pose_error":0.0112,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49896,-0.02185,0.02413],"final_tcp_position":[0.49379,-0.03516,0.13263],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":110.02789,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":651.0,"n_steps_budget":1000.0,"object_pos_end":[0.50095,0.11604,0.03389],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19614,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.50235,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":635.0,"raw_peak_contact_force":1.92055,"subtask_id":"pre_contact","tcp_end":[0.49761,0.15778,0.0892],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06936,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":257.0,"n_steps_budget":600.0,"object_pos_end":[0.50075,0.11519,0.03482],"object_pos_start":[0.50095,0.11604,0.03389],"object_to_goal_dist_end":0.19526,"object_to_goal_dist_start":0.19614,"object_z_max":0.03479,"peak_contact_force":10.36658,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":265.0,"raw_peak_contact_force":10.36658,"tcp_end":[0.49632,0.14455,0.04398],"tcp_start":[0.49761,0.15778,0.0892],"tcp_to_object_dist_end":0.03107,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":561.0,"n_steps_budget":1000.0,"object_pos_end":[0.50696,-0.02143,0.02662],"object_pos_start":[0.50075,0.11519,0.03482],"object_to_goal_dist_end":0.06049,"object_to_goal_dist_start":0.19526,"object_z_max":0.04015,"peak_contact_force":73.98187,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1346.0,"raw_peak_contact_force":110.02789,"subtask_id":"insertion_goal","tcp_end":[0.4967,-0.03546,0.04344],"tcp_start":[0.49632,0.14455,0.04398],"tcp_to_object_dist_end":0.02419,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.49896,-0.02185,0.02413],"object_pos_start":[0.50696,-0.02143,0.02662],"object_to_goal_dist_end":0.06029,"object_to_goal_dist_start":0.06049,"object_z_max":0.02664,"peak_contact_force":0.68339,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":595.0,"raw_peak_contact_force":73.45196,"tcp_end":[0.49379,-0.03516,0.13263],"tcp_start":[0.4967,-0.03546,0.04344],"tcp_to_object_dist_end":0.10944,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40104,"average_solve_count":192.0,"average_success_count":192.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09197,"contact_1.contact_force":5.27732,"push_1.insertion_depth":0.18088,"push_1.push_speed":0.03327},"optimized_scores":{"best_composite_score":0.50403,"best_fitness_score":0.51403,"best_task_score":0.33562},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":79.0,"contact_point_centroid":[0.47497,-0.06943,0.0526],"force_p95":282.4451,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":294.5091,"mean_force":159.28036,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48682,-0.06942,0.05084]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":252.0,"contact_point_centroid":[0.47499,0.0176,0.0459],"force_p95":110.84277,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":150.05591,"mean_force":71.09109,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48686,0.01761,0.04414]},{"body_a":"attachment","body_b":"peg","contact_count":235.0,"contact_point_centroid":[0.49609,0.03121,0.0469],"force_p95":59.98121,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.90375,"mean_force":36.22654,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48687,0.03785,0.04437]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":263.0,"contact_point_centroid":[0.52574,0.01557,0.03766],"force_p95":54.51481,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":57.80433,"mean_force":26.20996,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48687,0.03195,0.04439]},{"body_a":"peg","body_b":"channel_base_body","contact_count":458.0,"contact_point_centroid":[0.50585,0.00584,0.00907],"force_p95":36.46951,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.89673,"mean_force":10.58879,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48689,0.0101,0.04413]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.49545,-0.01453,0.00807],"force_p95":0.6521,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.70126,"mean_force":0.62241,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48457,-0.0692,0.0877]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":5.0,"contact_point_centroid":[0.47499,0.00047,0.02424],"force_p95":7.4677,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.23235,"mean_force":2.13754,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48373,-0.0692,0.09158]},{"body_a":"peg","body_b":"channel_base_body","contact_count":538.0,"contact_point_centroid":[0.49543,0.06249,0.00941],"force_p95":0.55217,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.08936,"mean_force":0.59,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48277,0.10055,0.09129]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.49157,0.08089,0.05885],"force_p95":6.41336,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.82067,"mean_force":2.07234,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48795,0.09263,0.05168]},{"body_a":"peg","body_b":"channel_base_body","contact_count":545.0,"contact_point_centroid":[0.49541,0.064,0.00937],"force_p95":0.58305,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56117,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4886,0.15329,0.21532]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49929,0.19831,0.29711]}],"total_contact_groups":11},"final_pose_error":0.01117,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49347,-0.0144,0.02415],"final_tcp_position":[0.48398,-0.06926,0.13277],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":294.5091,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":572.0,"n_steps_budget":1000.0,"object_pos_end":[0.49489,0.06381,0.03394],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14403,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54688,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":573.0,"raw_peak_contact_force":2.44546,"subtask_id":"pre_contact","tcp_end":[0.47938,0.11005,0.13942],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11621,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":538.0,"n_steps_budget":690.0,"object_pos_end":[0.4954,0.06296,0.03507],"object_pos_start":[0.49489,0.06381,0.03394],"object_to_goal_dist_end":0.14312,"object_to_goal_dist_start":0.14403,"object_z_max":0.03505,"peak_contact_force":7.08936,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":552.0,"raw_peak_contact_force":7.08936,"tcp_end":[0.48862,0.09169,0.0469],"tcp_start":[0.47938,0.11005,0.13942],"tcp_to_object_dist_end":0.0318,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":531.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,-0.01455,0.02415],"object_pos_start":[0.4954,0.06296,0.03507],"object_to_goal_dist_end":0.06736,"object_to_goal_dist_start":0.14312,"object_z_max":0.04111,"peak_contact_force":45.07998,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1208.0,"raw_peak_contact_force":150.05591,"subtask_id":"insertion_goal","tcp_end":[0.48687,-0.06976,0.04354],"tcp_start":[0.48862,0.09169,0.0469],"tcp_to_object_dist_end":0.0603,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.49347,-0.0144,0.02415],"object_pos_start":[0.50142,-0.01455,0.02415],"object_to_goal_dist_end":0.0678,"object_to_goal_dist_start":0.06736,"object_z_max":0.02444,"peak_contact_force":0.64358,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":627.0,"raw_peak_contact_force":294.5091,"tcp_end":[0.48398,-0.06926,0.13277],"tcp_start":[0.48687,-0.06976,0.04354],"tcp_to_object_dist_end":0.12205,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```