## Search State

- **Seed**: 5
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 9 | -0.2084 | 0.00 | ❌ rejected |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1666 | 0.22 | ✅ accepted |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`
- Frozen object start: [0.5244002338996304, 0.1046352631789195, 0.04]
- Frozen task target: [0.5244002338996304, -0.05536473682108051, 0.04]
- Goal object position: (0.5244002338996304, -0.05536473682108051, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5244002338996304, 0.1046352631789195, 0.04)
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
  frozen_object_start: [0.5244, 0.1046, 0.04]
  frozen_task_target: [0.5244, -0.0554, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5244002338996304, 0.1046352631789195, 0.04]}
  frozen_targets: {'channel_exit': [0.5244002338996304, -0.05536473682108051, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e

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
| `object` | offset from object initial position (0.5244002338996304, 0.1046352631789195, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5244002338996304, -0.05536473682108051, 0.04) | final destination targets |
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

## Current Skill (Q=-0.208) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach_contact
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.0
  weight: 0.4
- id: push_complete
  weight: 0.6
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
    - 0.05
    - 0.0
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_contact
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.04
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_contact
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
    tolerance: 0.015
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
  parameters:
    insert_depth:
      type: scalar
      range:
      - 0.14
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
    anchor: world
    offset:
    - 0.5
    - 0.2
    - 0.3
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.0], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.04, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.015
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis
  - parameter_bindings:
    - insert_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.2, 0.3], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.208
- **task_score** (E): 0.000
- **fitness_score**: 0.132  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 1.00 | 1.00 | 0.1649 |
| descend_contact | 1.00 | 1.00 | 0.0836 |
| contact_peg | 1.00 | 1.00 | 0.0002 |
| push_into_channel | 0.00 | 1.00 | 0.0002 |
| retract_home | 1.00 | 1.00 | 0.2265 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.510, 0.189, 0.137) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.531 | 2.488 |
| descend_contact | approach | 1.00 / step_budget | (0.510, 0.189, 0.137)→(0.502, 0.177, 0.055) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 2.000 | 215.511 | 306.603 |
| contact_peg | contact | 1.00 / force_exceeded | (0.502, 0.177, 0.055)→(0.502, 0.177, 0.055) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 2.000 | 137.021 | 137.021 |
| push_into_channel | push | 0.00 / guard_failure | (0.502, 0.177, 0.055)→(0.502, 0.177, 0.056) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 2.000 | 152.467 | 152.467 |
| retract_home | retract | 1.00 / step_budget | (0.502, 0.177, 0.056)→(0.499, 0.198, 0.280) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.543 | 259.958 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.237
- phase_breakdown.push_goal_score: 0.000
- phase_breakdown.reach_peg_score: 0.790

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.142
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.204
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.362


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9b36d26f861d7a613dfb3d8c86d70470e42095a430c2befa4bd6e530468a8a7e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2af86d8f59685db6584febc0596b9044223ae39cea3120c112c665a54a1c4732`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9708,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.arc_height":0.07954,"approach_high.speed":0.06952,"contact_peg.contact_force":17.6707,"contact_peg.speed":0.02896,"descend_contact.speed":0.09969,"push_into_channel.insert_depth":0.17187,"push_into_channel.max_force":20.83382,"push_into_channel.push_speed":0.02972,"retract_home.speed":0.07769},"optimized_scores":{"best_composite_score":-0.22344,"best_fitness_score":0.11656,"best_task_score":0.00023},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":33.0,"contact_point_centroid":[0.50735,0.2475,-0.00054],"force_p95":245.25245,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":272.83817,"mean_force":209.45575,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"approach","tcp_position_centroid":[0.50575,0.18602,0.05384]},{"body_a":"world","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.50716,0.2472,-8e-05],"force_p95":244.5377,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":265.18381,"mean_force":115.18003,"phase_index":4.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.50495,0.18649,0.05558]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50741,0.24747,-0.00024],"force_p95":213.61398,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":213.61398,"mean_force":213.61398,"phase_index":3.0,"phase_name":"push_into_channel","phase_type":"push","tcp_position_centroid":[0.50521,0.18666,0.05516]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50751,0.24755,-0.00029],"force_p95":136.35016,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":136.35016,"mean_force":136.35016,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50529,0.18672,0.05504]},{"body_a":"peg","body_b":"channel_base_body","contact_count":348.0,"contact_point_centroid":[0.50541,0.10472,0.00936],"force_p95":0.59383,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57887,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.51144,0.24752,0.17728]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.50709,0.2215,0.29194]},{"body_a":"peg","body_b":"channel_base_body","contact_count":273.0,"contact_point_centroid":[0.5059,0.10464,0.00939],"force_p95":0.5755,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57865,"mean_force":0.54634,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"approach","tcp_position_centroid":[0.51293,0.19131,0.09084]},{"body_a":"peg","body_b":"channel_base_body","contact_count":731.0,"contact_point_centroid":[0.50593,0.10458,0.00939],"force_p95":0.5757,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57608,"mean_force":0.54633,"phase_index":4.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.50084,0.19162,0.16683]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52198,0.11274,0.00939],"force_p95":0.54039,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54039,"mean_force":0.54039,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50529,0.18672,0.05504]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52389,0.10544,0.00939],"force_p95":0.53561,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53561,"mean_force":0.53561,"phase_index":3.0,"phase_name":"push_into_channel","phase_type":"push","tcp_position_centroid":[0.50521,0.18666,0.05516]}],"total_contact_groups":10},"final_pose_error":0.01971,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50587,0.10456,0.03384],"final_tcp_position":[0.49925,0.19833,0.28037],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":272.83817,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":375.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.10468,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18488,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54412,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":380.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_peg","tcp_end":[0.52173,0.19889,0.13626],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14005,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":273.0,"n_steps_budget":660.0,"object_pos_end":[0.50599,0.10468,0.03384],"object_pos_start":[0.50599,0.10468,0.03384],"object_to_goal_dist_end":0.18488,"object_to_goal_dist_start":0.18488,"object_z_max":0.03384,"peak_contact_force":206.21452,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":306.0,"raw_peak_contact_force":272.83817,"subtask_id":"reach_peg","tcp_end":[0.50529,0.18672,0.05504],"tcp_start":[0.52173,0.19889,0.13626],"tcp_to_object_dist_end":0.08474,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":870.0,"object_pos_end":[0.506,0.10464,0.03384],"object_pos_start":[0.50599,0.10468,0.03384],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18488,"object_z_max":0.03384,"peak_contact_force":136.35016,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":136.35016,"subtask_id":"reach_peg","tcp_end":[0.50521,0.18666,0.05516],"tcp_start":[0.50529,0.18672,0.05504],"tcp_to_object_dist_end":0.08475,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.1046,0.03384],"object_pos_start":[0.506,0.10464,0.03384],"object_to_goal_dist_end":0.1848,"object_to_goal_dist_start":0.18484,"object_z_max":0.03384,"peak_contact_force":213.61398,"phase_name":"push_into_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":213.61398,"subtask_id":"push_goal","tcp_end":[0.50512,0.18658,0.05532],"tcp_start":[0.50521,0.18666,0.05516],"tcp_to_object_dist_end":0.08475,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":731.0,"n_steps_budget":1000.0,"object_pos_end":[0.50587,0.10456,0.03384],"object_pos_start":[0.50598,0.1046,0.03384],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.1848,"object_z_max":0.03384,"peak_contact_force":0.55164,"phase_name":"retract_home","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":735.0,"raw_peak_contact_force":265.18381,"tcp_end":[0.49925,0.19833,0.28037],"tcp_start":[0.50512,0.18658,0.05532],"tcp_to_object_dist_end":0.26385,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `314cefd2153cfe84bc0d0d2dfbeb7f4daf8feaf5f2c7ce7d396802b52a157f39`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36458,"average_solve_count":192.0,"average_success_count":192.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.arc_height":0.12091,"approach_high.speed":0.07306,"contact_peg.contact_force":13.36174,"contact_peg.speed":0.03085,"descend_contact.speed":0.09803,"push_into_channel.insert_depth":0.1648,"push_into_channel.max_force":36.47584,"push_into_channel.push_speed":0.04035,"retract_home.speed":0.03938},"optimized_scores":{"best_composite_score":-0.19755,"best_fitness_score":0.14245,"best_task_score":0.0002},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":35.0,"contact_point_centroid":[0.50107,0.21047,-0.00051],"force_p95":297.75262,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":343.70893,"mean_force":235.06711,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"approach","tcp_position_centroid":[0.4994,0.14915,0.05407]},{"body_a":"world","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.50107,0.21023,-7e-05],"force_p95":220.6438,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":238.07019,"mean_force":106.63311,"phase_index":4.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.49881,0.14997,0.05609]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50135,0.21053,-0.00026],"force_p95":136.96511,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":136.96511,"mean_force":136.96511,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49911,0.15016,0.05559]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50127,0.21046,-0.00021],"force_p95":102.67071,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":102.67071,"mean_force":102.67071,"phase_index":3.0,"phase_name":"push_into_channel","phase_type":"push","tcp_position_centroid":[0.49903,0.15011,0.05572]},{"body_a":"peg","body_b":"channel_base_body","contact_count":489.0,"contact_point_centroid":[0.50308,0.06751,0.00933],"force_p95":0.55983,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56424,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49654,0.21576,0.20319]},{"body_a":"peg","body_b":"channel_base_body","contact_count":294.0,"contact_point_centroid":[0.50292,0.06737,0.00938],"force_p95":0.5506,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55098,"mean_force":0.54666,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"approach","tcp_position_centroid":[0.49958,0.15429,0.09164]},{"body_a":"peg","body_b":"channel_base_body","contact_count":793.0,"contact_point_centroid":[0.50308,0.06745,0.00938],"force_p95":0.55057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55079,"mean_force":0.54665,"phase_index":4.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.49759,0.17252,0.16708]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.5093,0.08428,0.00938],"force_p95":0.54722,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54722,"mean_force":0.54722,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49911,0.15016,0.05559]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51817,0.07721,0.00938],"force_p95":0.54364,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54364,"mean_force":0.54364,"phase_index":3.0,"phase_name":"push_into_channel","phase_type":"push","tcp_position_centroid":[0.49903,0.15011,0.05572]}],"total_contact_groups":9},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50307,0.06743,0.0338],"final_tcp_position":[0.49887,0.19623,0.28043],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":343.70893,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":505.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54595,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":489.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_peg","tcp_end":[0.50083,0.16199,0.13849],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14109,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":294.0,"n_steps_budget":660.0,"object_pos_end":[0.50306,0.0675,0.0338],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":229.20932,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":329.0,"raw_peak_contact_force":343.70893,"subtask_id":"reach_peg","tcp_end":[0.49911,0.15016,0.05559],"tcp_start":[0.50083,0.16199,0.13849],"tcp_to_object_dist_end":0.08558,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":810.0,"object_pos_end":[0.50309,0.06748,0.0338],"object_pos_start":[0.50306,0.0675,0.0338],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"peak_contact_force":136.96511,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":136.96511,"subtask_id":"reach_peg","tcp_end":[0.49903,0.15011,0.05572],"tcp_start":[0.49911,0.15016,0.05559],"tcp_to_object_dist_end":0.08559,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50309,0.06748,0.0338],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14764,"object_z_max":0.0338,"peak_contact_force":102.67071,"phase_name":"push_into_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":102.67071,"subtask_id":"push_goal","tcp_end":[0.49897,0.15004,0.05585],"tcp_start":[0.49903,0.15011,0.05572],"tcp_to_object_dist_end":0.08558,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":793.0,"n_steps_budget":1000.0,"object_pos_end":[0.50307,0.06743,0.0338],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14762,"object_z_max":0.0338,"peak_contact_force":0.54562,"phase_name":"retract_home","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":798.0,"raw_peak_contact_force":238.07019,"tcp_end":[0.49887,0.19623,0.28043],"tcp_start":[0.49897,0.15004,0.05585],"tcp_to_object_dist_end":0.27827,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7acce370299b32aeef0e4239da3e97eae076cb9602edead185a6cf774ee0bc4e`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64151,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.arc_height":0.07675,"approach_high.speed":0.06157,"contact_peg.contact_force":7.09959,"contact_peg.speed":0.01505,"descend_contact.speed":0.09925,"push_into_channel.insert_depth":0.15737,"push_into_channel.max_force":28.74406,"push_into_channel.push_speed":0.05942,"retract_home.speed":0.06173},"optimized_scores":{"best_composite_score":-0.20415,"best_fitness_score":0.13585,"best_task_score":0.00025},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":34.0,"contact_point_centroid":[0.50267,0.2546,-0.00052],"force_p95":262.99442,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":303.26044,"mean_force":215.29216,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"approach","tcp_position_centroid":[0.50119,0.19321,0.05397]},{"body_a":"world","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.50255,0.25435,-8e-05],"force_p95":248.48857,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":276.62007,"mean_force":104.61912,"phase_index":4.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.50042,0.19383,0.0558]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50283,0.25461,-0.00022],"force_p95":141.11766,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":141.11766,"mean_force":141.11766,"phase_index":3.0,"phase_name":"push_into_channel","phase_type":"push","tcp_position_centroid":[0.50075,0.19399,0.05541]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50291,0.25468,-0.00027],"force_p95":137.74662,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":137.74662,"mean_force":137.74662,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50082,0.19405,0.05529]},{"body_a":"peg","body_b":"channel_base_body","contact_count":296.0,"contact_point_centroid":[0.50341,0.11171,0.00934],"force_p95":0.6856,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.57162,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.50168,0.2484,0.1775]},{"body_a":"peg","body_b":"channel_base_body","contact_count":760.0,"contact_point_centroid":[0.50371,0.11168,0.00941],"force_p95":0.60255,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64425,"mean_force":0.54389,"phase_index":4.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.49849,0.19543,0.1668]},{"body_a":"peg","body_b":"channel_base_body","contact_count":281.0,"contact_point_centroid":[0.50367,0.11162,0.0094],"force_p95":0.60665,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64028,"mean_force":0.54399,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"approach","tcp_position_centroid":[0.50369,0.19845,0.09129]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51955,0.12,0.00944],"force_p95":0.62588,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62588,"mean_force":0.62588,"phase_index":3.0,"phase_name":"push_into_channel","phase_type":"push","tcp_position_centroid":[0.50075,0.19399,0.05541]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.50433,0.20595,0.30003]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49087,0.09924,0.00946],"force_p95":0.48273,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48273,"mean_force":0.48273,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50082,0.19405,0.05529]}],"total_contact_groups":10},"final_pose_error":0.01984,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5037,0.11173,0.03379],"final_tcp_position":[0.49897,0.19873,0.28023],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":303.26044,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":318.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.11177,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.50337,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":312.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_peg","tcp_end":[0.50741,0.20617,0.13758],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14033,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":281.0,"n_steps_budget":660.0,"object_pos_end":[0.50371,0.11175,0.03393],"object_pos_start":[0.50375,0.11177,0.0338],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19191,"object_z_max":0.03401,"peak_contact_force":211.10915,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":315.0,"raw_peak_contact_force":303.26044,"subtask_id":"reach_peg","tcp_end":[0.50082,0.19405,0.05529],"tcp_start":[0.50741,0.20617,0.13758],"tcp_to_object_dist_end":0.08508,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.11178,0.03392],"object_pos_start":[0.50371,0.11175,0.03393],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.19188,"object_z_max":0.03393,"peak_contact_force":137.74662,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":137.74662,"subtask_id":"reach_peg","tcp_end":[0.50075,0.19399,0.05541],"tcp_start":[0.50082,0.19405,0.05529],"tcp_to_object_dist_end":0.08503,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.1118,0.03391],"object_pos_start":[0.50375,0.11178,0.03392],"object_to_goal_dist_end":0.19193,"object_to_goal_dist_start":0.19191,"object_z_max":0.03392,"peak_contact_force":141.11766,"phase_name":"push_into_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":141.11766,"subtask_id":"push_goal","tcp_end":[0.50064,0.19391,0.05553],"tcp_start":[0.50075,0.19399,0.05541],"tcp_to_object_dist_end":0.08497,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":760.0,"n_steps_budget":1000.0,"object_pos_end":[0.5037,0.11173,0.03379],"object_pos_start":[0.50377,0.1118,0.03391],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19193,"object_z_max":0.03406,"peak_contact_force":0.53135,"phase_name":"retract_home","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":765.0,"raw_peak_contact_force":276.62007,"tcp_end":[0.49897,0.19873,0.28023],"tcp_start":[0.50064,0.19391,0.05553],"tcp_to_object_dist_end":0.26139,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```