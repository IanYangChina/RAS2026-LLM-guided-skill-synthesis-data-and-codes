## Search State

- **Seed**: 0
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.2491 | 0.65 | ❌ rejected |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.3533 | 0.22 | ❌ rejected |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | -0.2268 | 0.17 | ❌ rejected |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3092 | 0.78 | ✅ accepted |
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.1413 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.65 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.249) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.08
  - 0.1
  weight: 0.3
- id: push_channel
  metric: goal_progress
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
    - 0.08
    - 0.1
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.08
    - 0.0
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    force_threshold:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: push_1
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
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.12
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_channel
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.08
    - 0.1
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.08, 0.1], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.08, 0.0], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.08, 0.1], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.249
- **task_score** (E): 0.652
- **fitness_score**: 0.609  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1478 |
| descend_1 | 0.00 | 1.00 | 0.1217 |
| push_1 | 1.00 | 1.00 | 0.1705 |
| retract_1 | 1.00 | 1.00 | 0.0930 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.165, 0.159) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.541 | 2.179 |
| descend_1 | descend | 0.00 / step_budget | (0.495, 0.165, 0.159)→(0.496, 0.160, 0.037) | (0.500, 0.081, 0.034)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.561 | 0.603 |
| push_1 | push | 1.00 / step_budget | (0.496, 0.160, 0.037)→(0.496, -0.011, 0.037) | (0.500, 0.081, 0.034)→(0.507, -0.043, 0.038) | 0.161→0.038 | 1.00 / 3.000 | 78.909 | 147.247 |
| retract_1 | retract | 1.00 / step_budget | (0.496, -0.011, 0.037)→(0.502, 0.031, 0.120) | (0.507, -0.043, 0.038)→(0.501, -0.046, 0.033) | 0.038→0.036 | 1.00 / 1.667 | 0.493 | 69.078 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.829
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.829
- phase_score: 0.511
- phase_breakdown.push_channel_score: 0.675
- phase_breakdown.reach_object_score: 0.128

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.638
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.829
- **Median Q (composite search score)**: 0.259
- **K-run variance**: 0.0008
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.335


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40642,"average_solve_count":187.0,"average_success_count":187.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0752,"descend_1.force_threshold":18.53255,"descend_1.speed":0.14241,"push_1.push_distance":0.18259,"push_1.push_speed":0.03771,"retract_1.retract_speed":0.11039},"optimized_scores":{"best_composite_score":0.25902,"best_fitness_score":0.61902,"best_task_score":0.63052},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":417.0,"contact_point_centroid":[0.54444,0.05071,0.05999],"force_p95":125.28628,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":132.21266,"mean_force":109.5478,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49952,0.05302,0.03653]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54513,-0.0275,0.05998],"force_p95":61.89557,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":62.35035,"mean_force":57.80254,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5006,-0.02194,0.03664]},{"body_a":"peg","body_b":"channel_base_body","contact_count":516.0,"contact_point_centroid":[0.50161,0.01796,0.00951],"force_p95":6.58822,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.92893,"mean_force":1.92363,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49939,0.06241,0.03646]},{"body_a":"attachment","body_b":"peg","contact_count":171.0,"contact_point_centroid":[0.50113,0.0309,0.041],"force_p95":31.18412,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.72487,"mean_force":4.35311,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49974,0.04247,0.03672]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":129.0,"contact_point_centroid":[0.47473,-0.00688,0.02799],"force_p95":3.2063,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.48485,"mean_force":0.95553,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5001,0.02231,0.03682]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5252,0.03721,0.02685],"force_p95":6.02549,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.81237,"mean_force":1.31654,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49931,0.06694,0.03663]},{"body_a":"peg","body_b":"channel_base_body","contact_count":272.0,"contact_point_centroid":[0.50347,0.06161,0.00931],"force_p95":0.68094,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.57626,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50298,0.1733,0.22461]},{"body_a":"peg","body_b":"channel_base_body","contact_count":281.0,"contact_point_centroid":[0.50409,-0.04891,0.00955],"force_p95":0.80134,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.08022,"mean_force":0.53626,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50029,-0.00148,0.0774]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52538,-0.05527,0.05996],"force_p95":0.53943,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72995,"mean_force":0.14408,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49971,-0.01722,0.04587]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49984,0.19904,0.29796]},{"body_a":"peg","body_b":"channel_base_body","contact_count":535.0,"contact_point_centroid":[0.50376,0.06163,0.00938],"force_p95":0.59241,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60891,"mean_force":0.54656,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50214,0.1447,0.09588]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.50226,-0.02349,0.05806],"force_p95":0.32279,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34772,"mean_force":0.11418,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49908,-0.01178,0.05539]}],"total_contact_groups":12},"final_pose_error":0.01972,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5043,-0.04801,0.03435],"final_tcp_position":[0.50254,0.0185,0.11998],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":132.21266,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":295.0,"n_steps_budget":1000.0,"object_pos_end":[0.5038,0.06158,0.03377],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14176,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.56261,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":291.0,"raw_peak_contact_force":2.17216,"subtask_id":"reach_object","tcp_end":[0.50682,0.14914,0.15775],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15181,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":535.0,"n_steps_budget":600.0,"object_pos_end":[0.5038,0.06158,0.0338],"object_pos_start":[0.5038,0.06158,0.03377],"object_to_goal_dist_end":0.14176,"object_to_goal_dist_start":0.14176,"object_z_max":0.0338,"peak_contact_force":0.54199,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":535.0,"raw_peak_contact_force":0.60891,"subtask_id":"reach_object","tcp_end":[0.49987,0.141,0.03724],"tcp_start":[0.50682,0.14914,0.15775],"tcp_to_object_dist_end":0.07959,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":663.0,"n_steps_budget":1000.0,"object_pos_end":[0.50649,-0.05526,0.03826],"object_pos_start":[0.5038,0.06158,0.0338],"object_to_goal_dist_end":0.02564,"object_to_goal_dist_start":0.14176,"object_z_max":0.03829,"peak_contact_force":0.89351,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1269.0,"raw_peak_contact_force":132.21266,"subtask_id":"push_channel","tcp_end":[0.50064,-0.0217,0.03667],"tcp_start":[0.49987,0.141,0.03724],"tcp_to_object_dist_end":0.0341,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":281.0,"n_steps_budget":660.0,"object_pos_end":[0.5043,-0.04801,0.03435],"object_pos_start":[0.50649,-0.05526,0.03826],"object_to_goal_dist_end":0.03276,"object_to_goal_dist_start":0.02564,"object_z_max":0.03897,"peak_contact_force":0.55291,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":323.0,"raw_peak_contact_force":62.35035,"tcp_end":[0.50254,0.0185,0.11998],"tcp_start":[0.50064,-0.0217,0.03667],"tcp_to_object_dist_end":0.10844,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9058,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08585,"descend_1.force_threshold":8.92211,"descend_1.speed":0.17665,"push_1.push_distance":0.19975,"push_1.push_speed":0.07232,"retract_1.retract_speed":0.11016},"optimized_scores":{"best_composite_score":0.2781,"best_fitness_score":0.6381,"best_task_score":0.82936},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":355.0,"contact_point_centroid":[0.54235,0.07771,0.05999],"force_p95":131.41613,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":139.34713,"mean_force":110.1202,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49592,0.08338,0.0364]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.5423,0.01108,0.05999],"force_p95":83.5766,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":86.81504,"mean_force":61.77972,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49732,0.01455,0.03713]},{"body_a":"peg","body_b":"channel_base_body","contact_count":429.0,"contact_point_centroid":[0.50258,0.06185,0.00956],"force_p95":15.31549,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.48186,"mean_force":2.65618,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49552,0.10694,0.0359]},{"body_a":"attachment","body_b":"peg","contact_count":189.0,"contact_point_centroid":[0.50096,0.074,0.0406],"force_p95":27.61709,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.37715,"mean_force":5.1187,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49589,0.08527,0.03646]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":215.0,"contact_point_centroid":[0.52533,0.03778,0.0321],"force_p95":5.05336,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.67466,"mean_force":1.1597,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49633,0.06693,0.03681]},{"body_a":"peg","body_b":"channel_base_body","contact_count":256.0,"contact_point_centroid":[0.50113,0.11602,0.00931],"force_p95":0.75548,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.57717,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49865,0.19742,0.22722]},{"body_a":"peg","body_b":"channel_base_body","contact_count":280.0,"contact_point_centroid":[0.50364,-0.01707,0.00951],"force_p95":0.62764,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72092,"mean_force":0.54502,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49837,0.0357,0.07681]},{"body_a":"peg","body_b":"channel_base_body","contact_count":542.0,"contact_point_centroid":[0.50086,0.11604,0.00942],"force_p95":0.60155,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64822,"mean_force":0.5428,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49627,0.1947,0.09711]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":13.0,"contact_point_centroid":[0.52521,-0.01678,0.05922],"force_p95":0.29112,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34766,"mean_force":0.07375,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49669,0.02064,0.04787]}],"total_contact_groups":9},"final_pose_error":0.01974,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50342,-0.01666,0.0347],"final_tcp_position":[0.50189,0.05663,0.11828],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":139.34713,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":272.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,0.11623,0.03388],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19632,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.51402,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":256.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_object","tcp_end":[0.49833,0.19562,0.15948],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14861,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.50095,0.11603,0.03383],"object_pos_start":[0.50092,0.11623,0.03388],"object_to_goal_dist_end":0.19613,"object_to_goal_dist_start":0.19632,"object_z_max":0.03405,"peak_contact_force":0.58968,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":542.0,"raw_peak_contact_force":0.64822,"subtask_id":"reach_object","tcp_end":[0.4967,0.19471,0.03726],"tcp_start":[0.49833,0.19562,0.15948],"tcp_to_object_dist_end":0.07887,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":636.0,"n_steps_budget":1000.0,"object_pos_end":[0.50626,-0.0166,0.03631],"object_pos_start":[0.50095,0.11603,0.03383],"object_to_goal_dist_end":0.06382,"object_to_goal_dist_start":0.19613,"object_z_max":0.03954,"peak_contact_force":118.52063,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1188.0,"raw_peak_contact_force":139.34713,"subtask_id":"push_channel","tcp_end":[0.49734,0.01474,0.03713],"tcp_start":[0.4967,0.19471,0.03726],"tcp_to_object_dist_end":0.0326,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":280.0,"n_steps_budget":660.0,"object_pos_end":[0.50342,-0.01666,0.0347],"object_pos_start":[0.50626,-0.0166,0.03631],"object_to_goal_dist_end":0.06365,"object_to_goal_dist_start":0.06382,"object_z_max":0.03631,"peak_contact_force":0.53956,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":296.0,"raw_peak_contact_force":86.81504,"tcp_end":[0.50189,0.05663,0.11828],"tcp_start":[0.49734,0.01474,0.03713],"tcp_to_object_dist_end":0.11118,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89516,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.12414,"descend_1.force_threshold":21.56919,"descend_1.speed":0.13158,"push_1.push_distance":0.18964,"push_1.push_speed":0.0764,"retract_1.retract_speed":0.10469},"optimized_scores":{"best_composite_score":0.21011,"best_fitness_score":0.57011,"best_task_score":0.49597},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":647.0,"contact_point_centroid":[0.53559,0.03733,0.05999],"force_p95":140.50339,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":170.18113,"mean_force":124.06139,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49019,0.04026,0.03748]},{"body_a":"attachment","body_b":"peg","contact_count":596.0,"contact_point_centroid":[0.49795,0.00725,0.03574],"force_p95":87.35012,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":96.97342,"mean_force":43.69969,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4905,0.01519,0.03771]},{"body_a":"peg","body_b":"channel_base_body","contact_count":852.0,"contact_point_centroid":[0.50366,0.00632,0.00965],"force_p95":63.81977,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":80.06901,"mean_force":17.55207,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49016,0.04288,0.03745]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.53588,-0.03157,0.05999],"force_p95":57.51543,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":58.06897,"mean_force":52.02715,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49091,-0.02578,0.0376]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":562.0,"contact_point_centroid":[0.52546,-0.00576,0.02376],"force_p95":47.02403,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.60496,"mean_force":31.46476,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49054,0.01118,0.03773]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.49849,-0.03262,0.03471],"force_p95":15.74163,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.65259,"mean_force":3.17257,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49063,-0.02551,0.03844]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.52531,-0.04736,0.02954],"force_p95":2.01938,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.84882,"mean_force":1.46881,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49058,-0.02366,0.04158]},{"body_a":"peg","body_b":"channel_base_body","contact_count":269.0,"contact_point_centroid":[0.50349,-0.05215,0.00996],"force_p95":1.10923,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.88699,"mean_force":0.6195,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49558,-0.00438,0.07866]},{"body_a":"peg","body_b":"link7","contact_count":18.0,"contact_point_centroid":[0.51718,-0.00211,0.06958],"force_p95":9.21656,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.06388,"mean_force":4.90452,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49046,0.02487,0.03777]},{"body_a":"peg","body_b":"channel_base_body","contact_count":253.0,"contact_point_centroid":[0.49564,0.06405,0.00934],"force_p95":0.68673,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.57889,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48956,0.17383,0.22341]},{"body_a":"peg","body_b":"channel_base_body","contact_count":136.0,"contact_point_centroid":[0.50513,-0.10009,0.0247],"force_p95":0.69213,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.49243,"mean_force":0.33227,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49847,0.00505,0.09751]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4991,0.19824,0.29539]},{"body_a":"peg","body_b":"channel_base_body","contact_count":573.0,"contact_point_centroid":[0.49528,0.06382,0.0094],"force_p95":0.55039,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55295,"mean_force":0.54565,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48431,0.1468,0.09672]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":62.0,"contact_point_centroid":[0.47497,-0.09328,0.03447],"force_p95":0.44825,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54001,"mean_force":0.17215,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50065,0.0111,0.11014]}],"total_contact_groups":14},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49667,-0.07192,0.03085],"final_tcp_position":[0.50272,0.01667,0.12181],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":170.18113,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":280.0,"n_steps_budget":870.0,"object_pos_end":[0.49501,0.06373,0.03391],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14395,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54537,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":281.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_object","tcp_end":[0.48122,0.15116,0.15833],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15269,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":573.0,"n_steps_budget":630.0,"object_pos_end":[0.49504,0.06413,0.03399],"object_pos_start":[0.49501,0.06373,0.03391],"object_to_goal_dist_end":0.14434,"object_to_goal_dist_start":0.14395,"object_z_max":0.03399,"peak_contact_force":0.55067,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":573.0,"raw_peak_contact_force":0.55295,"subtask_id":"reach_object","tcp_end":[0.49002,0.14311,0.03716],"tcp_start":[0.48122,0.15116,0.15833],"tcp_to_object_dist_end":0.0792,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":909.0,"n_steps_budget":1000.0,"object_pos_end":[0.50811,-0.05695,0.03985],"object_pos_start":[0.49504,0.06413,0.03399],"object_to_goal_dist_end":0.02444,"object_to_goal_dist_start":0.14434,"object_z_max":0.04066,"peak_contact_force":117.31369,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2675.0,"raw_peak_contact_force":170.18113,"subtask_id":"push_channel","tcp_end":[0.49091,-0.0257,0.0376],"tcp_start":[0.49002,0.14311,0.03716],"tcp_to_object_dist_end":0.03574,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":291.0,"n_steps_budget":690.0,"object_pos_end":[0.49667,-0.07192,0.03085],"object_pos_start":[0.50811,-0.05695,0.03985],"object_to_goal_dist_end":0.01265,"object_to_goal_dist_start":0.02444,"object_z_max":0.04065,"peak_contact_force":0.3868,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":521.0,"raw_peak_contact_force":58.06897,"tcp_end":[0.50272,0.01667,0.12181],"tcp_start":[0.49091,-0.0257,0.0376],"tcp_to_object_dist_end":0.12712,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```