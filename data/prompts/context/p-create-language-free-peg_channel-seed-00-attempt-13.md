## Search State

- **Seed**: 0
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.4167 | 0.51 | ❌ rejected |
| 12 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.4533 | 0.62 | ❌ rejected |
| 11 | approach → contact → push → push → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.1528 | 0.00 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.5969 | 0.75 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.5839 | 0.64 | ❌ rejected |

**Proposal policy**: task_score is 0.51 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.417) — your mutation base

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

- **Composite score**: 0.417
- **task_score** (E): 0.510
- **fitness_score**: 0.557  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.390

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 1.00 | 1.00 | 0.1236 |
| descend_1 | 1.00 | 1.00 | 0.1064 |
| contact_1 | 1.00 | 1.00 | 0.0513 |
| push_1 | 1.00 | 1.00 | 0.0757 |
| retract_1 | 1.00 | 1.00 | 0.0894 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.496, 0.130, 0.200) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.564 | 2.179 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.130, 0.200)→(0.496, 0.121, 0.095) | (0.500, 0.081, 0.034)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.567 | 0.592 |
| contact_1 | contact | 1.00 / force_exceeded | (0.496, 0.121, 0.095)→(0.495, 0.109, 0.045) | (0.500, 0.081, 0.034)→(0.500, 0.080, 0.035) | 0.161→0.160 | 1.00 / 2.000 | 8.604 | 7.603 |
| push_1 | push | 1.00 / time_limit | (0.495, 0.109, 0.045)→(0.492, 0.033, 0.041) | (0.500, 0.080, 0.035)→(0.508, 0.003, 0.038) | 0.160→0.084 | 1.00 / 3.000 | 26.055 | 45.464 |
| retract_1 | retract | 1.00 / step_budget | (0.492, 0.033, 0.041)→(0.489, 0.033, 0.131) | (0.508, 0.003, 0.038)→(0.501, -0.010, 0.024) | 0.084→0.072 | 1.00 / 1.000 | 0.628 | 152.227 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.623
- alignment_error: None
- force_efficiency: 0.118
- terminal_score: 0.610
- phase_score: 0.623
- phase_breakdown.insertion_goal_score: 0.557
- phase_breakdown.pre_contact_score: 0.775

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.617
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.610
- **Median Q (composite search score)**: 0.429
- **K-run variance**: 0.0031
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.299


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65574,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_speed":0.1501,"contact_1.contact_force":8.26077,"descend_1.approach_height":0.04902,"push_1.insertion_depth":0.18554,"push_1.max_time":3045.00118,"push_1.push_speed":0.04768},"optimized_scores":{"best_composite_score":0.47743,"best_fitness_score":0.61743,"best_task_score":0.60983},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.50183,0.00478,0.04151],"force_p95":17.49137,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.10792,"mean_force":3.63177,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49546,0.01459,0.04233]},{"body_a":"peg","body_b":"channel_base_body","contact_count":566.0,"contact_point_centroid":[0.50589,-0.03422,0.00835],"force_p95":0.88104,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.39686,"mean_force":0.71062,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49292,0.01473,0.0863]},{"body_a":"attachment","body_b":"peg","contact_count":944.0,"contact_point_centroid":[0.50105,0.0404,0.04233],"force_p95":27.53392,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.18601,"mean_force":14.04145,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49553,0.05088,0.04111]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.50784,0.01715,0.00984],"force_p95":23.86319,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.88283,"mean_force":11.22413,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49558,0.05228,0.04114]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":939.0,"contact_point_centroid":[0.52519,0.02635,0.03169],"force_p95":11.93139,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.08852,"mean_force":6.91933,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49552,0.05064,0.0411]},{"body_a":"peg","body_b":"channel_base_body","contact_count":270.0,"contact_point_centroid":[0.50362,0.05998,0.0094],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.692,"mean_force":0.63426,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49886,0.09622,0.06771]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.5017,0.07894,0.05597],"force_p95":8.18654,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.50552,"mean_force":3.87833,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49909,0.09088,0.04747]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":28.0,"contact_point_centroid":[0.52508,-0.00387,0.02681],"force_p95":3.48772,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.10052,"mean_force":1.21076,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49506,0.01458,0.04336]},{"body_a":"peg","body_b":"channel_base_body","contact_count":290.0,"contact_point_centroid":[0.50358,0.06159,0.00931],"force_p95":0.65414,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.57437,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.50317,0.15431,0.24524]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49985,0.19822,0.29809]},{"body_a":"peg","body_b":"channel_base_body","contact_count":329.0,"contact_point_centroid":[0.50363,0.06162,0.00938],"force_p95":0.57465,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58651,"mean_force":0.54659,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50327,0.10762,0.14544]}],"total_contact_groups":11},"final_pose_error":0.01091,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50554,-0.03805,0.02413],"final_tcp_position":[0.493,0.01474,0.13128],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":44.10792,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":313.0,"n_steps_budget":630.0,"object_pos_end":[0.50374,0.06158,0.03376],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14177,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.51932,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":309.0,"raw_peak_contact_force":2.17216,"tcp_end":[0.50722,0.11314,0.19853],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.17268,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":329.0,"n_steps_budget":750.0,"object_pos_end":[0.50377,0.0616,0.03378],"object_pos_start":[0.50374,0.06158,0.03376],"object_to_goal_dist_end":0.14178,"object_to_goal_dist_start":0.14177,"object_z_max":0.03379,"peak_contact_force":0.55102,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":329.0,"raw_peak_contact_force":0.58651,"subtask_id":"pre_contact","tcp_end":[0.50088,0.10233,0.09226],"tcp_start":[0.50722,0.11314,0.19853],"tcp_to_object_dist_end":0.07133,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":270.0,"n_steps_budget":600.0,"object_pos_end":[0.50382,0.0609,0.03481],"object_pos_start":[0.50377,0.0616,0.03378],"object_to_goal_dist_end":0.14104,"object_to_goal_dist_start":0.14178,"object_z_max":0.03482,"peak_contact_force":9.692,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":277.0,"raw_peak_contact_force":9.692,"tcp_end":[0.49919,0.09029,0.04522],"tcp_start":[0.50088,0.10233,0.09226],"tcp_to_object_dist_end":0.03153,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5075,-0.01798,0.03938],"object_pos_start":[0.50382,0.0609,0.03481],"object_to_goal_dist_end":0.06248,"object_to_goal_dist_start":0.14104,"object_z_max":0.04041,"peak_contact_force":31.83082,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2856.0,"raw_peak_contact_force":32.18601,"subtask_id":"insertion_goal","tcp_end":[0.49597,0.01473,0.04178],"tcp_start":[0.49919,0.09029,0.04522],"tcp_to_object_dist_end":0.03477,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.50554,-0.03805,0.02413],"object_pos_start":[0.5075,-0.01798,0.03938],"object_to_goal_dist_end":0.0452,"object_to_goal_dist_start":0.06248,"object_z_max":0.04002,"peak_contact_force":0.68339,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":608.0,"raw_peak_contact_force":44.10792,"tcp_end":[0.493,0.01474,0.13128],"tcp_start":[0.49597,0.01473,0.04178],"tcp_to_object_dist_end":0.1201,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56667,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_speed":0.16528,"contact_1.contact_force":8.53813,"descend_1.approach_height":0.05364,"push_1.insertion_depth":0.17688,"push_1.max_time":4170.83621,"push_1.push_speed":0.04842},"optimized_scores":{"best_composite_score":0.42946,"best_fitness_score":0.56946,"best_task_score":0.59916},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":19.0,"contact_point_centroid":[0.5001,0.06022,0.04138],"force_p95":13.49781,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.01445,"mean_force":5.0391,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49203,0.0685,0.04234]},{"body_a":"peg","body_b":"channel_base_body","contact_count":536.0,"contact_point_centroid":[0.50513,0.02422,0.00837],"force_p95":1.10235,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.02183,"mean_force":0.78306,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48975,0.06838,0.08588]},{"body_a":"attachment","body_b":"peg","contact_count":916.0,"contact_point_centroid":[0.49923,0.09345,0.04083],"force_p95":39.7475,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.3844,"mean_force":16.78296,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49259,0.10311,0.04049]},{"body_a":"peg","body_b":"channel_base_body","contact_count":957.0,"contact_point_centroid":[0.50761,0.07176,0.00983],"force_p95":32.27805,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.50257,"mean_force":12.8496,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49263,0.10512,0.04049]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":870.0,"contact_point_centroid":[0.52526,0.07894,0.02941],"force_p95":22.09238,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.61389,"mean_force":9.73836,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49259,0.10122,0.04053]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":45.0,"contact_point_centroid":[0.52516,0.04983,0.02956],"force_p95":6.11752,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.90648,"mean_force":1.83728,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49141,0.06847,0.04434]},{"body_a":"peg","body_b":"channel_base_body","contact_count":287.0,"contact_point_centroid":[0.50141,0.11295,0.00948],"force_p95":3.30741,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.13556,"mean_force":0.8558,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49567,0.14967,0.06976]},{"body_a":"attachment","body_b":"peg","contact_count":19.0,"contact_point_centroid":[0.49863,0.13291,0.05369],"force_p95":7.78863,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.88803,"mean_force":5.1591,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49615,0.14476,0.04857]},{"body_a":"peg","body_b":"channel_base_body","contact_count":222.0,"contact_point_centroid":[0.50108,0.11592,0.0093],"force_p95":0.8374,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.58242,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49881,0.18059,0.24915]},{"body_a":"peg","body_b":"channel_base_body","contact_count":329.0,"contact_point_centroid":[0.50084,0.11605,0.00942],"force_p95":0.60747,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63685,"mean_force":0.54248,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49714,0.15896,0.1499]}],"total_contact_groups":10},"final_pose_error":0.01114,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50368,0.02017,0.02415],"final_tcp_position":[0.48982,0.06839,0.13062],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":63.01445,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":238.0,"n_steps_budget":600.0,"object_pos_end":[0.50087,0.11609,0.0338],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19618,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.6213,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":222.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.4986,0.16251,0.20316],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.17561,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":329.0,"n_steps_budget":750.0,"object_pos_end":[0.50098,0.11616,0.03381],"object_pos_start":[0.50087,0.11609,0.0338],"object_to_goal_dist_end":0.19626,"object_to_goal_dist_start":0.19618,"object_z_max":0.03397,"peak_contact_force":0.61084,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":329.0,"raw_peak_contact_force":0.63685,"subtask_id":"pre_contact","tcp_end":[0.49739,0.15589,0.09679],"tcp_start":[0.4986,0.16251,0.20316],"tcp_to_object_dist_end":0.07455,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":288.0,"n_steps_budget":600.0,"object_pos_end":[0.5012,0.1146,0.03534],"object_pos_start":[0.50098,0.11616,0.03381],"object_to_goal_dist_end":0.19466,"object_to_goal_dist_start":0.19626,"object_z_max":0.03543,"peak_contact_force":11.1375,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":306.0,"raw_peak_contact_force":8.13556,"tcp_end":[0.49638,0.14391,0.04459],"tcp_start":[0.49739,0.15589,0.09679],"tcp_to_object_dist_end":0.03111,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50783,0.03733,0.03845],"object_pos_start":[0.5012,0.1146,0.03534],"object_to_goal_dist_end":0.11761,"object_to_goal_dist_start":0.19466,"object_z_max":0.04038,"peak_contact_force":46.3341,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2743.0,"raw_peak_contact_force":46.3844,"subtask_id":"insertion_goal","tcp_end":[0.49273,0.06869,0.04137],"tcp_start":[0.49638,0.14391,0.04459],"tcp_to_object_dist_end":0.03493,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.50368,0.02017,0.02415],"object_pos_start":[0.50783,0.03733,0.03845],"object_to_goal_dist_end":0.10148,"object_to_goal_dist_start":0.11761,"object_z_max":0.03939,"peak_contact_force":0.55614,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":600.0,"raw_peak_contact_force":63.01445,"tcp_end":[0.48982,0.06839,0.13062],"tcp_start":[0.49273,0.06869,0.04137],"tcp_to_object_dist_end":0.11769,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_speed":0.15071,"contact_1.contact_force":4.76677,"descend_1.approach_height":0.05199,"push_1.insertion_depth":0.14684,"push_1.max_time":4280.09673,"push_1.push_speed":0.04907},"optimized_scores":{"best_composite_score":0.34328,"best_fitness_score":0.48328,"best_task_score":0.32096},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":87.0,"contact_point_centroid":[0.47498,0.0156,0.05109],"force_p95":325.69048,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":349.55754,"mean_force":177.28034,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48681,0.01565,0.04918]},{"body_a":"attachment","body_b":"peg","contact_count":31.0,"contact_point_centroid":[0.49755,0.0119,0.04158],"force_p95":49.77109,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.5608,"mean_force":27.41086,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48681,0.01593,0.043]},{"body_a":"peg","body_b":"channel_base_body","contact_count":519.0,"contact_point_centroid":[0.49518,-0.01087,0.00822],"force_p95":5.66787,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":62.86613,"mean_force":1.33051,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48449,0.01612,0.08733]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":473.0,"contact_point_centroid":[0.475,0.0486,0.04254],"force_p95":35.3893,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":57.82035,"mean_force":21.72867,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48684,0.04861,0.04064]},{"body_a":"attachment","body_b":"peg","contact_count":855.0,"contact_point_centroid":[0.49557,0.04166,0.04239],"force_p95":47.38982,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.8822,"mean_force":18.18327,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48686,0.04951,0.04064]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":42.0,"contact_point_centroid":[0.5258,0.00624,0.03013],"force_p95":48.12558,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.46268,"mean_force":19.42798,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48681,0.01586,0.04383]},{"body_a":"peg","body_b":"channel_base_body","contact_count":929.0,"contact_point_centroid":[0.50753,0.0237,0.00984],"force_p95":34.05599,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.78008,"mean_force":11.59035,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4869,0.053,0.04062]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":708.0,"contact_point_centroid":[0.52544,0.02592,0.03242],"force_p95":37.21215,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.24702,"mean_force":15.9762,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48685,0.04313,0.04073]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":32.0,"contact_point_centroid":[0.47493,-0.03588,0.02463],"force_p95":9.03048,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.36455,"mean_force":3.32916,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48474,0.016,0.06854]},{"body_a":"peg","body_b":"channel_base_body","contact_count":297.0,"contact_point_centroid":[0.49482,0.06211,0.00941],"force_p95":0.59966,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.98109,"mean_force":0.59218,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48908,0.09828,0.06836]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.4928,0.08131,0.0567],"force_p95":3.57554,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.83565,"mean_force":1.46566,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48992,0.09321,0.0482]},{"body_a":"peg","body_b":"channel_base_body","contact_count":278.0,"contact_point_centroid":[0.49571,0.06372,0.00935],"force_p95":0.66362,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.57591,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.48945,0.15494,0.24493]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49907,0.19715,0.29651]},{"body_a":"peg","body_b":"channel_base_body","contact_count":345.0,"contact_point_centroid":[0.49529,0.06399,0.0094],"force_p95":0.55022,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55295,"mean_force":0.54576,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48473,0.10983,0.14665]}],"total_contact_groups":14},"final_pose_error":0.01103,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49387,-0.01251,0.02415],"final_tcp_position":[0.48395,0.01631,0.13059],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":349.55754,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":305.0,"n_steps_budget":630.0,"object_pos_end":[0.49526,0.06388,0.03391],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14409,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.55059,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":306.0,"raw_peak_contact_force":2.44546,"tcp_end":[0.48111,0.11537,0.19918],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.17368,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":345.0,"n_steps_budget":720.0,"object_pos_end":[0.49511,0.0641,0.03396],"object_pos_start":[0.49526,0.06388,0.03391],"object_to_goal_dist_end":0.14431,"object_to_goal_dist_start":0.14409,"object_z_max":0.03396,"peak_contact_force":0.53934,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":345.0,"raw_peak_contact_force":0.55295,"subtask_id":"pre_contact","tcp_end":[0.49038,0.10456,0.09458],"tcp_start":[0.48111,0.11537,0.19918],"tcp_to_object_dist_end":0.07304,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":297.0,"n_steps_budget":600.0,"object_pos_end":[0.49586,0.06316,0.0349],"object_pos_start":[0.49511,0.0641,0.03396],"object_to_goal_dist_end":0.14331,"object_to_goal_dist_start":0.14431,"object_z_max":0.03487,"peak_contact_force":4.98109,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":309.0,"raw_peak_contact_force":4.98109,"tcp_end":[0.49022,0.09225,0.04435],"tcp_start":[0.49038,0.10456,0.09458],"tcp_to_object_dist_end":0.0311,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50852,-0.00907,0.03549],"object_pos_start":[0.49586,0.06316,0.0349],"object_to_goal_dist_end":0.07158,"object_to_goal_dist_start":0.14331,"object_z_max":0.04049,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2965.0,"raw_peak_contact_force":57.82035,"subtask_id":"insertion_goal","tcp_end":[0.48686,0.01629,0.04123],"tcp_start":[0.49022,0.09225,0.04435],"tcp_to_object_dist_end":0.03384,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.49387,-0.01251,0.02415],"object_pos_start":[0.50852,-0.00907,0.03549],"object_to_goal_dist_end":0.0696,"object_to_goal_dist_start":0.07158,"object_z_max":0.03612,"peak_contact_force":0.64358,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":711.0,"raw_peak_contact_force":349.55754,"tcp_end":[0.48395,0.01631,0.13059],"tcp_start":[0.48686,0.01629,0.04123],"tcp_to_object_dist_end":0.11071,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```