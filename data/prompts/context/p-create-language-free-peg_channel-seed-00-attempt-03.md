## Search State

- **Seed**: 0
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1747 | 0.56 | ❌ rejected |
| 2 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1109 | 0.54 | ❌ rejected |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6757 | 0.65 | ❌ rejected |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6280 | 0.69 | ✅ accepted |

**Proposal policy**: task_score is 0.56 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.175) — your mutation base

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

- **Composite score**: 0.175
- **task_score** (E): 0.564
- **fitness_score**: 0.431  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.133
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.390

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2145 |
| descend_1 | 1.00 | 1.00 | 0.0147 |
| contact_1 | 1.00 | 1.00 | 0.0516 |
| push_1 | 0.00 | 1.00 | 0.0003 |
| retract_1 | 1.00 | 1.00 | 0.0894 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.125, 0.101) | (0.498, 0.080, 0.040)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.545 | 2.179 |
| descend_1 | descend | 1.00 / step_budget | (0.495, 0.125, 0.101)→(0.497, 0.122, 0.087) | (0.500, 0.080, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.538 | 0.578 |
| contact_1 | contact | 1.00 / force_exceeded | (0.497, 0.122, 0.087)→(0.496, 0.108, 0.038) | (0.500, 0.080, 0.034)→(0.500, 0.078, 0.035) | 0.161→0.158 | 1.00 / 2.000 | 6.049 | 7.028 |
| push_1 | push | 0.00 / guard_failure | (0.493, 0.019, 0.033)→(0.493, 0.019, 0.033) | (0.500, 0.078, 0.035)→(0.502, -0.010, 0.037) | 0.158→0.071 | 1.00 / 2.333 | 8.629 | 44.107 |
| retract_1 | retract | 1.00 / step_budget | (0.493, 0.019, 0.033)→(0.490, 0.019, 0.122) | (0.503, -0.010, 0.038)→(0.503, -0.019, 0.034) | 0.071→0.062 | 1.00 / 1.000 | 0.542 | 112.392 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.731
- alignment_error: None
- force_efficiency: 0.392
- terminal_score: 0.731
- phase_score: 0.404
- phase_breakdown.insertion_goal_score: 0.315
- phase_breakdown.pre_contact_score: 0.611

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.535
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.731
- **Median Q (composite search score)**: 0.277
- **K-run variance**: 0.0378
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.240


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95633,"average_solve_count":229.0,"average_success_count":229.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.03191,"contact_1.contact_force":5.23393,"descend_1.descend_height":0.03526,"push_1.insertion_depth":0.14828,"push_1.push_force_threshold":29.46722,"push_1.push_speed":0.01828},"optimized_scores":{"best_composite_score":0.34476,"best_fitness_score":0.53476,"best_task_score":0.73083},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":88.0,"contact_point_centroid":[0.50164,0.02092,0.04225],"force_p95":27.45368,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.41454,"mean_force":6.83992,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4973,0.03226,0.03609]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":121.0,"contact_point_centroid":[0.52539,-0.00432,0.03484],"force_p95":24.83743,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.3798,"mean_force":3.01724,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49721,0.02416,0.03592]},{"body_a":"peg","body_b":"channel_base_body","contact_count":79.0,"contact_point_centroid":[0.50401,0.01093,0.00966],"force_p95":17.04663,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.67232,"mean_force":4.23801,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49764,0.05407,0.03666]},{"body_a":"peg","body_b":"channel_base_body","contact_count":214.0,"contact_point_centroid":[0.50384,0.06079,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.89267,"mean_force":0.60897,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50181,0.09814,0.05776]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50317,0.07931,0.05708],"force_p95":7.44796,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.67268,"mean_force":4.81007,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5004,0.09136,0.04156]},{"body_a":"peg","body_b":"channel_base_body","contact_count":725.0,"contact_point_centroid":[0.50365,0.06161,0.00935],"force_p95":0.58217,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55784,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5027,0.15166,0.18533]},{"body_a":"peg","body_b":"channel_base_body","contact_count":572.0,"contact_point_centroid":[0.50593,-0.05576,0.00944],"force_p95":0.614,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.20894,"mean_force":0.54266,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49394,-0.02239,0.07999]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":194.0,"contact_point_centroid":[0.52504,-0.0554,0.04637],"force_p95":0.32761,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69671,"mean_force":0.10517,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49426,-0.02254,0.07148]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49977,0.19905,0.29837]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.50455,0.06029,0.00938],"force_p95":0.55009,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55026,"mean_force":0.5468,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50612,0.10571,0.0781]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50351,-0.03431,0.05993],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49701,-0.02267,0.03581]}],"total_contact_groups":11},"final_pose_error":0.01096,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50694,-0.05535,0.03379],"final_tcp_position":[0.49404,-0.02232,0.12531],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":30.41454,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":748.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.06157,0.03378],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14176,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.54516,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":744.0,"raw_peak_contact_force":2.17216,"subtask_id":"pre_contact","tcp_end":[0.50693,0.10628,0.0796],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0641,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50374,0.06157,0.03378],"object_pos_start":[0.50377,0.06157,0.03378],"object_to_goal_dist_end":0.14176,"object_to_goal_dist_start":0.14176,"object_z_max":0.03378,"peak_contact_force":0.54878,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":20.0,"raw_peak_contact_force":0.55026,"subtask_id":"pre_contact","tcp_end":[0.50527,0.10515,0.07627],"tcp_start":[0.50693,0.10628,0.0796],"tcp_to_object_dist_end":0.06088,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":214.0,"n_steps_budget":600.0,"object_pos_end":[0.50379,0.06119,0.03429],"object_pos_start":[0.50374,0.06157,0.03378],"object_to_goal_dist_end":0.14136,"object_to_goal_dist_start":0.14176,"object_z_max":0.03422,"peak_contact_force":7.89267,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":217.0,"raw_peak_contact_force":7.89267,"tcp_end":[0.50034,0.09093,0.04057],"tcp_start":[0.50527,0.10515,0.07627],"tcp_to_object_dist_end":0.03059,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":214.0,"n_steps_budget":1000.0,"object_pos_end":[0.50734,-0.05066,0.03527],"object_pos_start":[0.50379,0.06119,0.03429],"object_to_goal_dist_end":0.03061,"object_to_goal_dist_start":0.14136,"object_z_max":0.04129,"peak_contact_force":2.67034,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":288.0,"raw_peak_contact_force":30.41454,"subtask_id":"insertion_goal","tcp_end":[0.49704,-0.02254,0.03585],"tcp_start":[0.4971,-0.02221,0.03592],"tcp_to_object_dist_end":0.02995,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.50694,-0.05535,0.03379],"object_pos_start":[0.50742,-0.0517,0.03513],"object_to_goal_dist_end":0.02635,"object_to_goal_dist_start":0.02966,"object_z_max":0.03521,"peak_contact_force":0.54629,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":768.0,"raw_peak_contact_force":1.20894,"tcp_end":[0.49404,-0.02232,0.12531],"tcp_start":[0.49704,-0.02254,0.03585],"tcp_to_object_dist_end":0.09815,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.99524,"average_solve_count":210.0,"average_success_count":210.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05221,"contact_1.contact_force":7.24315,"descend_1.descend_height":0.05085,"push_1.insertion_depth":0.1458,"push_1.push_force_threshold":31.67211,"push_1.push_speed":0.02274},"optimized_scores":{"best_composite_score":0.27688,"best_fitness_score":0.46688,"best_task_score":0.69589},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":77.0,"contact_point_centroid":[0.49692,0.09533,0.04552],"force_p95":30.27832,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":72.36923,"mean_force":9.15734,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49356,0.10682,0.03275]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":12.0,"contact_point_centroid":[0.52576,0.01961,0.04792],"force_p95":33.07867,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.27325,"mean_force":10.99911,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49374,0.0498,0.03287]},{"body_a":"peg","body_b":"channel_base_body","contact_count":96.0,"contact_point_centroid":[0.50161,0.06264,0.0093],"force_p95":19.51227,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.75087,"mean_force":4.12602,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49384,0.10047,0.03324]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":32.0,"contact_point_centroid":[0.47454,0.07092,0.04611],"force_p95":30.95675,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.65599,"mean_force":10.32392,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49353,0.10052,0.03243]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.49958,0.03551,0.04205],"force_p95":7.26786,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.98839,"mean_force":2.27307,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49297,0.04599,0.03354]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":44.0,"contact_point_centroid":[0.52543,0.00884,0.05766],"force_p95":3.41654,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.31895,"mean_force":0.56129,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49164,0.04598,0.04237]},{"body_a":"peg","body_b":"link7","contact_count":33.0,"contact_point_centroid":[0.50853,0.06188,0.07151],"force_p95":4.69176,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.02307,"mean_force":1.03035,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49358,0.09025,0.03255]},{"body_a":"peg","body_b":"channel_base_body","contact_count":314.0,"contact_point_centroid":[0.50155,0.11217,0.0095],"force_p95":2.41234,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.04216,"mean_force":0.75792,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49558,0.14944,0.06485]},{"body_a":"attachment","body_b":"peg","contact_count":29.0,"contact_point_centroid":[0.49927,0.13196,0.0523],"force_p95":6.21046,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.74875,"mean_force":2.66231,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49627,0.14382,0.04335]},{"body_a":"peg","body_b":"channel_base_body","contact_count":599.0,"contact_point_centroid":[0.50087,0.11603,0.00938],"force_p95":0.61732,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55704,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49803,0.17838,0.19791]},{"body_a":"peg","body_b":"channel_base_body","contact_count":528.0,"contact_point_centroid":[0.50458,0.0053,0.00947],"force_p95":0.70174,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.0824,"mean_force":0.54306,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49051,0.04623,0.07812]},{"body_a":"peg","body_b":"channel_base_body","contact_count":32.0,"contact_point_centroid":[0.50213,0.11536,0.00941],"force_p95":0.59996,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63075,"mean_force":0.54323,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49713,0.15739,0.09795]}],"total_contact_groups":12},"final_pose_error":0.01115,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50448,0.00469,0.03445],"final_tcp_position":[0.49066,0.04629,0.12201],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":72.36923,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":615.0,"n_steps_budget":1000.0,"object_pos_end":[0.50098,0.116,0.03381],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.1961,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.54583,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":599.0,"raw_peak_contact_force":1.92055,"subtask_id":"pre_contact","tcp_end":[0.49768,0.15796,0.10119],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07945,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":32.0,"n_steps_budget":600.0,"object_pos_end":[0.50093,0.11605,0.03388],"object_pos_start":[0.50098,0.116,0.03381],"object_to_goal_dist_end":0.19614,"object_to_goal_dist_start":0.1961,"object_z_max":0.03388,"peak_contact_force":0.52268,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":32.0,"raw_peak_contact_force":0.63075,"subtask_id":"pre_contact","tcp_end":[0.49708,0.15685,0.09376],"tcp_start":[0.49768,0.15796,0.10119],"tcp_to_object_dist_end":0.07256,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":320.0,"n_steps_budget":600.0,"object_pos_end":[0.50216,0.11263,0.0353],"object_pos_start":[0.50093,0.11605,0.03388],"object_to_goal_dist_end":0.1927,"object_to_goal_dist_start":0.19614,"object_z_max":0.0355,"peak_contact_force":7.45178,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":343.0,"raw_peak_contact_force":7.04216,"tcp_end":[0.49661,0.14226,0.03727],"tcp_start":[0.49708,0.15685,0.09376],"tcp_to_object_dist_end":0.03021,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":180.0,"n_steps_budget":1000.0,"object_pos_end":[0.5073,0.02105,0.03742],"object_pos_start":[0.50216,0.11263,0.0353],"object_to_goal_dist_end":0.10134,"object_to_goal_dist_start":0.1927,"object_z_max":0.04495,"peak_contact_force":20.8575,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":250.0,"raw_peak_contact_force":72.36923,"subtask_id":"insertion_goal","tcp_end":[0.49363,0.04646,0.03276],"tcp_start":[0.49366,0.04677,0.03282],"tcp_to_object_dist_end":0.02923,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":547.0,"n_steps_budget":630.0,"object_pos_end":[0.50448,0.00469,0.03445],"object_pos_start":[0.50739,0.02053,0.03818],"object_to_goal_dist_end":0.08499,"object_to_goal_dist_start":0.10082,"object_z_max":0.0393,"peak_contact_force":0.53515,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":580.0,"raw_peak_contact_force":8.98839,"tcp_end":[0.49066,0.04629,0.12201],"tcp_start":[0.49363,0.04646,0.03276],"tcp_to_object_dist_end":0.09792,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.23121,"average_solve_count":173.0,"average_success_count":173.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07441,"contact_1.contact_force":7.30221,"descend_1.descend_height":0.05067,"push_1.insertion_depth":0.15358,"push_1.push_force_threshold":28.72448,"push_1.push_speed":0.0127},"optimized_scores":{"best_composite_score":-0.09762,"best_fitness_score":0.29238,"best_task_score":0.26413},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":132.0,"contact_point_centroid":[0.47498,0.03221,0.04628],"force_p95":259.49848,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":326.97843,"mean_force":139.65817,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4868,0.03224,0.04429]},{"body_a":"peg","body_b":"channel_base_body","contact_count":527.0,"contact_point_centroid":[0.49676,-0.00717,0.00943],"force_p95":0.71708,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":57.2774,"mean_force":0.66647,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48511,0.03287,0.07633]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.48999,0.02178,0.03035],"force_p95":40.00132,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.74708,"mean_force":10.75307,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48716,0.03293,0.03071]},{"body_a":"peg","body_b":"channel_base_body","contact_count":71.0,"contact_point_centroid":[0.49956,0.02764,0.00928],"force_p95":10.20923,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.5361,"mean_force":2.21524,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48772,0.06527,0.03166]},{"body_a":"attachment","body_b":"peg","contact_count":45.0,"contact_point_centroid":[0.49216,0.06294,0.0473],"force_p95":13.33478,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.42144,"mean_force":3.2486,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48748,0.07459,0.03136]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":25.0,"contact_point_centroid":[0.47466,0.01836,0.04867],"force_p95":12.3818,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.23725,"mean_force":2.83465,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48728,0.05327,0.03093]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":17.0,"contact_point_centroid":[0.47463,-0.0078,0.05594],"force_p95":6.58175,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.91039,"mean_force":1.34738,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48687,0.03235,0.04094]},{"body_a":"peg","body_b":"channel_base_body","contact_count":354.0,"contact_point_centroid":[0.49595,0.05959,0.00947],"force_p95":2.6588,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.14799,"mean_force":0.74687,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4876,0.09708,0.06201]},{"body_a":"attachment","body_b":"peg","contact_count":37.0,"contact_point_centroid":[0.49269,0.07976,0.05225],"force_p95":5.20639,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.88591,"mean_force":2.19593,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48952,0.09161,0.04218]},{"body_a":"peg","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50864,0.04016,0.06755],"force_p95":3.44565,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.44565,"mean_force":3.44565,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48707,0.06485,0.0306]},{"body_a":"peg","body_b":"channel_base_body","contact_count":589.0,"contact_point_centroid":[0.49532,0.06396,0.00937],"force_p95":0.57632,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56001,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4885,0.15314,0.20667]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49932,0.1984,0.29706]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.52532,-0.00035,0.05724],"force_p95":0.71702,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.76476,"mean_force":0.24924,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48681,0.03223,0.03464]},{"body_a":"peg","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.50269,0.00932,0.06877],"force_p95":0.58183,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.58989,"mean_force":0.5093,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48703,0.03266,0.03069]},{"body_a":"peg","body_b":"channel_base_body","contact_count":131.0,"contact_point_centroid":[0.49505,0.06387,0.0094],"force_p95":0.55092,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5516,"mean_force":0.54554,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48248,0.10711,0.10658]}],"total_contact_groups":15},"final_pose_error":0.01112,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49631,-0.00714,0.03425],"final_tcp_position":[0.48428,0.03328,0.12006],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":326.97843,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":616.0,"n_steps_budget":1000.0,"object_pos_end":[0.49496,0.0637,0.03395],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14391,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54433,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":617.0,"raw_peak_contact_force":2.44546,"subtask_id":"pre_contact","tcp_end":[0.4792,0.10964,0.12239],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10089,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":131.0,"n_steps_budget":600.0,"object_pos_end":[0.49495,0.06367,0.03398],"object_pos_start":[0.49496,0.0637,0.03395],"object_to_goal_dist_end":0.14388,"object_to_goal_dist_start":0.14391,"object_z_max":0.03398,"peak_contact_force":0.54363,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":131.0,"raw_peak_contact_force":0.5516,"subtask_id":"pre_contact","tcp_end":[0.48743,0.10474,0.09104],"tcp_start":[0.4792,0.10964,0.12239],"tcp_to_object_dist_end":0.07071,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":361.0,"n_steps_budget":600.0,"object_pos_end":[0.49369,0.0601,0.03497],"object_pos_start":[0.49495,0.06367,0.03398],"object_to_goal_dist_end":0.14033,"object_to_goal_dist_start":0.14388,"object_z_max":0.03573,"peak_contact_force":2.80276,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":391.0,"raw_peak_contact_force":6.14799,"tcp_end":[0.49033,0.08974,0.0354],"tcp_start":[0.48743,0.10474,0.09104],"tcp_to_object_dist_end":0.02984,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":114.0,"n_steps_budget":1000.0,"object_pos_end":[0.49231,0.00083,0.03879],"object_pos_start":[0.49369,0.0601,0.03497],"object_to_goal_dist_end":0.0812,"object_to_goal_dist_start":0.14033,"object_z_max":0.04062,"peak_contact_force":2.35826,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":142.0,"raw_peak_contact_force":29.5361,"subtask_id":"insertion_goal","tcp_end":[0.48728,0.03336,0.03077],"tcp_start":[0.48726,0.03369,0.03081],"tcp_to_object_dist_end":0.03389,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":546.0,"n_steps_budget":630.0,"object_pos_end":[0.49631,-0.00714,0.03425],"object_pos_start":[0.4928,0.00076,0.03933],"object_to_goal_dist_end":0.07318,"object_to_goal_dist_start":0.08108,"object_z_max":0.041,"peak_contact_force":0.54365,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":697.0,"raw_peak_contact_force":326.97843,"tcp_end":[0.48428,0.03328,0.12006],"tcp_start":[0.48728,0.03336,0.03077],"tcp_to_object_dist_end":0.09561,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```