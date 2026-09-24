## Search State

- **Seed**: 3
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.4195 | 0.12 | ✅ accepted |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 6 | -0.0583 | 0.00 | ❌ rejected |
| 2 | approach → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.0214 | 0.02 | ❌ rejected |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.4166 | 0.12 | ✅ accepted |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.4151 | 0.11 | ✅ accepted |

**Proposal policy**: task_score is 0.12 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`
- Frozen object start: [0.46685193337148995, 0.058944840527687975, 0.04]
- Frozen task target: [0.46685193337148995, -0.10105515947231203, 0.04]
- Goal object position: (0.46685193337148995, -0.10105515947231203, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.46685193337148995, 0.058944840527687975, 0.04)
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
  frozen_object_start: [0.4669, 0.0589, 0.04]
  frozen_task_target: [0.4669, -0.1011, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.46685193337148995, 0.058944840527687975, 0.04]}
  frozen_targets: {'channel_exit': [0.46685193337148995, -0.10105515947231203, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834

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
| `object` | offset from object initial position (0.46685193337148995, 0.058944840527687975, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.46685193337148995, -0.10105515947231203, 0.04) | final destination targets |
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

## Current Skill (Q=0.419) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.025
  - 0.1
  weight: 0.3
- id: goal_push
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
    - 0.025
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_contact
- id: descend_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
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
      - 1.0
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
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.14
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
  subtask_id: goal_push
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
    tolerance: 0.02
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.025, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.025, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.419
- **task_score** (E): 0.121
- **fitness_score**: 0.479  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1825 |
| descend_1 | 1.00 | 1.00 | 0.0836 |
| push_1 | 1.00 | 1.00 | 0.1619 |
| retract_1 | 1.00 | 1.00 | 0.0805 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.117, 0.141) | (0.509, 0.081, 0.040)→(0.502, 0.082, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.543 | 3.954 |
| descend_1 | contact | 1.00 / force_exceeded | (0.505, 0.117, 0.141)→(0.500, 0.109, 0.059) | (0.502, 0.082, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.162 | 1.00 / 2.000 | 46.202 | 46.202 |
| push_1 | push | 1.00 / step_budget | (0.500, 0.109, 0.059)→(0.498, -0.053, 0.056) | (0.502, 0.081, 0.034)→(0.498, 0.009, 0.024) | 0.162→0.090 | 1.00 / 1.333 | 40.267 | 94.715 |
| retract_1 | retract | 1.00 / step_budget | (0.498, -0.053, 0.056)→(0.495, -0.053, 0.137) | (0.498, 0.009, 0.024)→(0.498, 0.009, 0.024) | 0.090→0.090 | 1.00 / 1.000 | 0.591 | 27.037 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.532
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.161
- phase_score: 0.748
- phase_breakdown.pre_contact_score: 0.802
- phase_breakdown.goal_push_score: 0.724

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.513
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.161
- **Median Q (composite search score)**: 0.435
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.352


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `cc7283febf3c95cef1fde4c5a16cbcb134186cb6faf3a169717a9aa53375931d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `178d67757a065da6e29d31070e25f6065dc7e42bdbf58dfbff0deec513214033`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.89324,"average_solve_count":281.0,"average_success_count":281.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08998,"approach_1.approach_speed":0.03509,"descend_1.contact_force":6.46879,"push_1.push_distance":0.16189,"push_1.push_speed":0.01103},"optimized_scores":{"best_composite_score":0.37088,"best_fitness_score":0.43088,"best_task_score":0.07768},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":411.0,"contact_point_centroid":[0.475,0.00918,0.05998],"force_p95":132.04645,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":143.42754,"mean_force":113.52018,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48486,0.01576,0.0586]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47499,0.07882,0.05993],"force_p95":99.33497,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":99.33497,"mean_force":99.33497,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.48385,0.08674,0.05861]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.475,-0.06066,0.06],"force_p95":63.53704,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":63.57156,"mean_force":63.22643,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48569,-0.05542,0.0585]},{"body_a":"attachment","body_b":"peg","contact_count":19.0,"contact_point_centroid":[0.48953,0.07101,0.05893],"force_p95":23.12472,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.11989,"mean_force":5.30705,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48429,0.08144,0.05863]},{"body_a":"peg","body_b":"channel_base_body","contact_count":580.0,"contact_point_centroid":[0.50025,0.0214,0.00852],"force_p95":0.75113,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.93331,"mean_force":0.75153,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48488,0.01501,0.05861]},{"body_a":"peg","body_b":"channel_base_body","contact_count":359.0,"contact_point_centroid":[0.49457,0.05887,0.00934],"force_p95":0.60751,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.58696,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48287,0.14601,0.21765]},{"body_a":"peg","body_b":"channel_base_body","contact_count":514.0,"contact_point_centroid":[0.49414,0.05885,0.00939],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.17562,"mean_force":0.55895,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.4747,0.09142,0.10038]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.48807,0.07562,0.05898],"force_p95":3.58028,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.77131,"mean_force":2.41917,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.48376,0.08677,0.05899]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49877,0.19732,0.29578]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47499,0.0355,0.02758],"force_p95":1.00111,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.03593,"mean_force":0.78081,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48453,0.04706,0.05868]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52504,0.02069,0.0455],"force_p95":0.85797,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.92238,"mean_force":0.51942,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48468,0.0309,0.0586]},{"body_a":"peg","body_b":"channel_base_body","contact_count":240.0,"contact_point_centroid":[0.49982,0.01452,0.00804],"force_p95":0.68344,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68368,"mean_force":0.6059,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48315,-0.05522,0.09791]}],"total_contact_groups":12},"final_pose_error":0.01972,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49745,0.01424,0.02413],"final_tcp_position":[0.48288,-0.05508,0.13898],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":143.42754,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":388.0,"n_steps_budget":1000.0,"object_pos_end":[0.4942,0.05903,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13929,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54657,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":394.0,"raw_peak_contact_force":4.20518,"subtask_id":"pre_contact","tcp_end":[0.4682,0.09665,0.14504],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12023,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":514.0,"n_steps_budget":720.0,"object_pos_end":[0.49413,0.05862,0.03398],"object_pos_start":[0.4942,0.05903,0.03385],"object_to_goal_dist_end":0.13888,"object_to_goal_dist_start":0.13929,"object_z_max":0.03394,"peak_contact_force":99.33497,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":518.0,"raw_peak_contact_force":99.33497,"tcp_end":[0.4839,0.08672,0.05845],"tcp_start":[0.4682,0.09665,0.14504],"tcp_to_object_dist_end":0.03864,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":592.0,"n_steps_budget":1000.0,"object_pos_end":[0.50217,0.01484,0.02413],"object_pos_start":[0.49413,0.05862,0.03398],"object_to_goal_dist_end":0.09618,"object_to_goal_dist_start":0.13888,"object_z_max":0.04081,"peak_contact_force":119.71069,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1022.0,"raw_peak_contact_force":143.42754,"subtask_id":"goal_push","tcp_end":[0.48568,-0.05535,0.0585],"tcp_start":[0.4839,0.08672,0.05845],"tcp_to_object_dist_end":0.07987,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":240.0,"n_steps_budget":630.0,"object_pos_end":[0.49745,0.01424,0.02413],"object_pos_start":[0.50217,0.01484,0.02413],"object_to_goal_dist_end":0.0956,"object_to_goal_dist_start":0.09618,"object_z_max":0.02413,"peak_contact_force":0.60164,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":242.0,"raw_peak_contact_force":63.57156,"tcp_end":[0.48288,-0.05508,0.13898],"tcp_start":[0.48568,-0.05535,0.0585],"tcp_to_object_dist_end":0.13494,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1ee374347cb6f80436633ebcb956aaa73ea8a10685d65b21d5c3814cf0c53498`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11741,"average_solve_count":247.0,"average_success_count":247.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08665,"approach_1.approach_speed":0.03991,"descend_1.contact_force":4.58008,"push_1.push_distance":0.18181,"push_1.push_speed":0.03533},"optimized_scores":{"best_composite_score":0.43458,"best_fitness_score":0.49458,"best_task_score":0.12351},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":467.0,"contact_point_centroid":[0.50785,0.03097,0.00936],"force_p95":70.22539,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":71.43918,"mean_force":46.21228,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50879,0.03359,0.05871]},{"body_a":"attachment","body_b":"peg","contact_count":385.0,"contact_point_centroid":[0.51462,0.05181,0.05959],"force_p95":69.91382,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":70.9979,"mean_force":55.49358,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50932,0.04851,0.05936]},{"body_a":"peg","body_b":"channel_base_body","contact_count":353.0,"contact_point_centroid":[0.50602,0.08085,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.99436,"mean_force":0.60187,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.51769,0.11207,0.10006]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51353,0.09717,0.05877],"force_p95":19.58785,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.58785,"mean_force":19.58785,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.50872,0.10813,0.05953]},{"body_a":"peg","body_b":"channel_base_body","contact_count":247.0,"contact_point_centroid":[0.49726,-0.00798,0.00811],"force_p95":0.71211,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.33185,"mean_force":0.63356,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50272,-0.05454,0.09398]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47495,0.01611,0.02438],"force_p95":5.41627,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.05375,"mean_force":1.32884,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50336,-0.05511,0.06276]},{"body_a":"peg","body_b":"channel_base_body","contact_count":347.0,"contact_point_centroid":[0.5055,0.08086,0.00934],"force_p95":0.56732,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.59073,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51418,0.15614,0.21588]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5003,0.19758,0.29529]}],"total_contact_groups":8},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50051,-0.00738,0.02415],"final_tcp_position":[0.50254,-0.05429,0.13522],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":71.43918,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":376.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54539,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":383.0,"raw_peak_contact_force":4.32595,"subtask_id":"pre_contact","tcp_end":[0.52847,0.1165,0.14206],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11619,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":353.0,"n_steps_budget":720.0,"object_pos_end":[0.50595,0.08088,0.03377],"object_pos_start":[0.50598,0.0809,0.03378],"object_to_goal_dist_end":0.16111,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":19.99436,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":354.0,"raw_peak_contact_force":19.99436,"tcp_end":[0.50867,0.10812,0.05931],"tcp_start":[0.52847,0.1165,0.14206],"tcp_to_object_dist_end":0.03744,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":473.0,"n_steps_budget":1000.0,"object_pos_end":[0.49628,-0.00744,0.02398],"object_pos_start":[0.50595,0.08088,0.03377],"object_to_goal_dist_end":0.0744,"object_to_goal_dist_start":0.16111,"object_z_max":0.04012,"peak_contact_force":0.53367,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":852.0,"raw_peak_contact_force":71.43918,"subtask_id":"goal_push","tcp_end":[0.50551,-0.05454,0.05484],"tcp_start":[0.50867,0.10812,0.05931],"tcp_to_object_dist_end":0.05706,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":247.0,"n_steps_budget":630.0,"object_pos_end":[0.50051,-0.00738,0.02415],"object_pos_start":[0.49628,-0.00744,0.02398],"object_to_goal_dist_end":0.07433,"object_to_goal_dist_start":0.0744,"object_z_max":0.02472,"peak_contact_force":0.56827,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":255.0,"raw_peak_contact_force":8.33185,"tcp_end":[0.50254,-0.05429,0.13522],"tcp_start":[0.50551,-0.05454,0.05484],"tcp_to_object_dist_end":0.12058,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e082b57d1be6744ae6d3993c25b90215f3fc56dc7131af62e0630c4f325e4b04`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.1129,"average_solve_count":248.0,"average_success_count":248.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07757,"approach_1.approach_speed":0.0337,"descend_1.contact_force":6.02474,"push_1.push_distance":0.19966,"push_1.push_speed":0.04509},"optimized_scores":{"best_composite_score":0.45289,"best_fitness_score":0.51289,"best_task_score":0.16081},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":506.0,"contact_point_centroid":[0.50659,0.05218,0.00922],"force_p95":68.19768,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":69.27787,"mean_force":40.21064,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50582,0.04732,0.0585]},{"body_a":"attachment","body_b":"peg","contact_count":370.0,"contact_point_centroid":[0.51343,0.0767,0.05955],"force_p95":67.95583,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.83871,"mean_force":54.33654,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50668,0.07276,0.05957]},{"body_a":"peg","body_b":"channel_base_body","contact_count":329.0,"contact_point_centroid":[0.50585,0.10447,0.00939],"force_p95":0.57554,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.27576,"mean_force":0.60328,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.51142,0.13402,0.09647]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51279,0.12111,0.05883],"force_p95":18.86918,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.86918,"mean_force":18.86918,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.50624,0.1311,0.05979]},{"body_a":"peg","body_b":"channel_base_body","contact_count":247.0,"contact_point_centroid":[0.49473,0.0193,0.00808],"force_p95":0.69041,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.20872,"mean_force":0.67199,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50008,-0.04959,0.09412]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47497,0.04361,0.02425],"force_p95":8.7136,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.81815,"mean_force":2.44734,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50089,-0.05025,0.06117]},{"body_a":"peg","body_b":"channel_base_body","contact_count":338.0,"contact_point_centroid":[0.50555,0.10471,0.00936],"force_p95":0.59965,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57978,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50901,0.1674,0.21297]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49998,0.19844,0.29617]}],"total_contact_groups":8},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49546,0.01947,0.02413],"final_tcp_position":[0.49989,-0.04935,0.13537],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":69.27787,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":365.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.10458,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18478,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.53815,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":370.0,"raw_peak_contact_force":3.33087,"subtask_id":"pre_contact","tcp_end":[0.51866,0.13756,0.13494],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1071,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":329.0,"n_steps_budget":660.0,"object_pos_end":[0.50582,0.10462,0.03383],"object_pos_start":[0.50596,0.10458,0.03383],"object_to_goal_dist_end":0.18481,"object_to_goal_dist_start":0.18478,"object_z_max":0.03384,"peak_contact_force":19.27576,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":330.0,"raw_peak_contact_force":19.27576,"tcp_end":[0.50621,0.13109,0.05957],"tcp_start":[0.51866,0.13756,0.13494],"tcp_to_object_dist_end":0.03693,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":512.0,"n_steps_budget":1000.0,"object_pos_end":[0.49486,0.01921,0.02413],"object_pos_start":[0.50582,0.10462,0.03383],"object_to_goal_dist_end":0.1006,"object_to_goal_dist_start":0.18481,"object_z_max":0.04015,"peak_contact_force":0.55796,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":876.0,"raw_peak_contact_force":69.27787,"subtask_id":"goal_push","tcp_end":[0.50284,-0.04957,0.05493],"tcp_start":[0.50621,0.13109,0.05957],"tcp_to_object_dist_end":0.07579,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":247.0,"n_steps_budget":630.0,"object_pos_end":[0.49546,0.01947,0.02413],"object_pos_start":[0.49486,0.01921,0.02413],"object_to_goal_dist_end":0.10083,"object_to_goal_dist_start":0.1006,"object_z_max":0.02467,"peak_contact_force":0.60162,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":255.0,"raw_peak_contact_force":9.20872,"tcp_end":[0.49989,-0.04935,0.13537],"tcp_start":[0.50284,-0.04957,0.05493],"tcp_to_object_dist_end":0.13088,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```