## Search State

- **Seed**: 5
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | 0.3347 | 0.48 | ❌ rejected |
| 12 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.0664 | 0.23 | ❌ rejected |
| 11 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.1135 | 0.10 | ❌ rejected |
| 10 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.2715 | 0.39 | ❌ rejected |
| 9 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 3 | 0.3636 | 0.47 | ❌ rejected |

**Proposal policy**: task_score is 0.48 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.335) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach_peg
  anchor: object
  offset:
  - 0.0
  - 0.06
  - 0.0
  weight: 0.3
- id: push_goal
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_peg
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.06
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_y_offset:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.06
      binds_to:
      - path: target.offset.y
        mode: replace
  subtask_id: approach_peg
- id: push_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.08
      - 0.3
      default: 0.2
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
  subtask_id: push_goal
- id: retract
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
    tolerance: 0.02
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.06, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_y_offset: status=consumed; consumers=target.offset.y (replace)
- **push_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.2, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.335
- **task_score** (E): 0.478
- **fitness_score**: 0.595  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.2076 |
| descend_to_peg | 1.00 | 1.00 | 0.0813 |
| push_channel | 0.33 | 1.00 | 0.1053 |
| retract | 1.00 | 1.00 | 0.1303 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.509, 0.100, 0.119) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.667 | 0.346 | 138.721 |
| descend_to_peg | descend | 1.00 / step_budget | (0.509, 0.100, 0.119)→(0.505, 0.128, 0.043) | (0.504, 0.095, 0.034)→(0.505, 0.094, 0.033) | 0.175→0.175 | 1.00 / 2.333 | 46.401 | 50.260 |
| push_channel | push | 0.33 / guard_failure | (0.505, 0.128, 0.043)→(0.500, 0.023, 0.039) | (0.505, 0.094, 0.033)→(0.507, -0.004, 0.034) | 0.175→0.080 | 1.00 / 1.000 | 0.548 | 7.139 |
| retract | retract | 1.00 / step_budget | (0.498, -0.021, 0.036)→(0.495, -0.021, 0.166) | (0.507, -0.049, 0.036)→(0.507, -0.048, 0.034) | 0.032→0.033 | 1.00 / 1.000 | 0.529 | 2.488 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.934
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.934
- phase_score: 0.915
- phase_breakdown.push_goal_score: 0.942
- phase_breakdown.approach_peg_score: 0.854

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.923
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.934
- **Median Q (composite search score)**: 0.443
- **K-run variance**: 0.1032
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.444


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9084,"average_solve_count":131.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_z_offset":0.0714,"descend_to_peg.descend_y_offset":0.0417,"push_channel.push_speed":0.09849,"push_channel.push_target_y_offset":-0.00466},"optimized_scores":{"best_composite_score":0.44286,"best_fitness_score":0.70286,"best_task_score":0.50038},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":271.0,"contact_point_centroid":[0.50638,0.10556,0.00937],"force_p95":14.1683,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":88.94535,"mean_force":4.43581,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.5114,0.12423,0.0793]},{"body_a":"attachment","body_b":"peg","contact_count":22.0,"contact_point_centroid":[0.51061,0.12268,0.05808],"force_p95":87.69529,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":88.47211,"mean_force":47.9929,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50761,0.1337,0.05733]},{"body_a":"attachment","body_b":"peg","contact_count":795.0,"contact_point_centroid":[0.50289,0.04313,0.04295],"force_p95":8.5224,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.17005,"mean_force":2.86058,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49913,0.05477,0.03633]},{"body_a":"peg","body_b":"channel_base_body","contact_count":554.0,"contact_point_centroid":[0.50662,0.01988,0.00989],"force_p95":8.82651,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.69336,"mean_force":4.28577,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49952,0.06466,0.0366]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.52514,-0.05058,0.06],"force_p95":6.26853,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.13911,"mean_force":1.03332,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49618,-0.02095,0.04007]},{"body_a":"attachment","body_b":"peg","contact_count":24.0,"contact_point_centroid":[0.50079,-0.03208,0.06065],"force_p95":5.42267,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.37156,"mean_force":1.02511,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49505,-0.02077,0.05033]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":533.0,"contact_point_centroid":[0.52505,0.02555,0.02212],"force_p95":3.28524,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.41745,"mean_force":0.9964,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49911,0.05385,0.03632]},{"body_a":"peg","body_b":"channel_base_body","contact_count":622.0,"contact_point_centroid":[0.50565,0.1047,0.00937],"force_p95":0.57593,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56453,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50928,0.15326,0.20445]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49989,0.19822,0.2965]},{"body_a":"peg","body_b":"channel_base_body","contact_count":391.0,"contact_point_centroid":[0.50717,-0.05131,0.00953],"force_p95":0.57118,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.44526,"mean_force":0.53275,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49465,-0.02057,0.10015]}],"total_contact_groups":10},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50651,-0.04791,0.03388],"final_tcp_position":[0.4948,-0.02051,0.16614],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":88.94535,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":649.0,"n_steps_budget":1000.0,"object_pos_end":[0.506,0.10464,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.56551,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":293.0,"raw_peak_contact_force":88.94535,"subtask_id":"approach_peg","tcp_end":[0.51965,0.10992,0.11811],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08553,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":271.0,"n_steps_budget":600.0,"object_pos_end":[0.50584,0.10448,0.03393],"object_pos_start":[0.506,0.10464,0.03384],"object_to_goal_dist_end":0.18467,"object_to_goal_dist_start":0.18484,"object_z_max":0.03402,"peak_contact_force":0.59261,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1882.0,"raw_peak_contact_force":12.17005,"tcp_end":[0.50468,0.14029,0.04144],"tcp_start":[0.51965,0.10992,0.11811],"tcp_to_object_dist_end":0.03661,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50697,-0.04911,0.03579],"object_pos_start":[0.50584,0.10448,0.03393],"object_to_goal_dist_end":0.03195,"object_to_goal_dist_start":0.18467,"object_z_max":0.03623,"peak_contact_force":0.54841,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":435.0,"raw_peak_contact_force":7.13911,"subtask_id":"push_goal","tcp_end":[0.49751,-0.02057,0.03585],"tcp_start":[0.50468,0.14029,0.04144],"tcp_to_object_dist_end":0.03006,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":392.0,"n_steps_budget":930.0,"object_pos_end":[0.50651,-0.04791,0.03388],"object_pos_start":[0.50697,-0.04911,0.03579],"object_to_goal_dist_end":0.03331,"object_to_goal_dist_start":0.03195,"object_z_max":0.03596,"peak_contact_force":0.54039,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":654.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.4948,-0.02051,0.16614],"tcp_start":[0.49751,-0.02057,0.03585],"tcp_to_object_dist_end":0.13557,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91262,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_z_offset":0.07329,"descend_to_peg.descend_y_offset":0.03499,"push_channel.push_speed":0.09617,"push_channel.push_target_y_offset":-0.02439},"optimized_scores":{"best_composite_score":0.66266,"best_fitness_score":0.92266,"best_task_score":0.93362},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":295.0,"contact_point_centroid":[0.50436,0.07043,0.00919],"force_p95":131.10117,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":156.93407,"mean_force":24.56605,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49944,0.08674,0.07861]},{"body_a":"attachment","body_b":"peg","contact_count":70.0,"contact_point_centroid":[0.50855,0.08686,0.05601],"force_p95":154.64825,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":156.28494,"mean_force":101.38267,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50184,0.09579,0.05482]},{"body_a":"attachment","body_b":"peg","contact_count":720.0,"contact_point_centroid":[0.5019,0.00545,0.04246],"force_p95":10.17586,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.65716,"mean_force":3.54593,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49778,0.01691,0.0374]},{"body_a":"peg","body_b":"channel_base_body","contact_count":18.0,"contact_point_centroid":[0.50702,-0.10038,0.05994],"force_p95":28.22941,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.06184,"mean_force":18.18252,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49675,-0.05349,0.03611]},{"body_a":"peg","body_b":"channel_base_body","contact_count":567.0,"contact_point_centroid":[0.50615,-0.01841,0.00989],"force_p95":9.1592,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.75737,"mean_force":4.11444,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4981,0.02678,0.03778]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52515,0.07405,0.05797],"force_p95":7.1397,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.55842,"mean_force":5.74874,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50451,0.09856,0.05204]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":594.0,"contact_point_centroid":[0.52509,-0.0162,0.0254],"force_p95":3.7392,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.41589,"mean_force":1.20597,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49771,0.01177,0.03731]},{"body_a":"peg","body_b":"channel_base_body","contact_count":694.0,"contact_point_centroid":[0.50303,0.06748,0.00935],"force_p95":0.55487,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55905,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49904,0.13596,0.20629]}],"total_contact_groups":8},"final_pose_error":0.05026,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50689,-0.08192,0.03596],"final_tcp_position":[0.49663,-0.0544,0.03596],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":156.93407,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":710.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06748,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14765,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.47298,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":373.0,"raw_peak_contact_force":156.93407,"subtask_id":"approach_peg","tcp_end":[0.49974,0.07456,0.11928],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08584,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":295.0,"n_steps_budget":600.0,"object_pos_end":[0.50313,0.06028,0.03541],"object_pos_start":[0.50308,0.06748,0.0338],"object_to_goal_dist_end":0.14039,"object_to_goal_dist_start":0.14765,"object_z_max":0.03519,"peak_contact_force":40.65716,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1899.0,"raw_peak_contact_force":40.65716,"tcp_end":[0.50261,0.09992,0.04324],"tcp_start":[0.49974,0.07456,0.11928],"tcp_to_object_dist_end":0.04041,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":994.0,"n_steps_budget":1000.0,"object_pos_end":[0.50689,-0.08192,0.03596],"object_pos_start":[0.50313,0.06028,0.03541],"object_to_goal_dist_end":0.00821,"object_to_goal_dist_start":0.14039,"object_z_max":0.03865,"peak_contact_force":0.54731,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":694.0,"raw_peak_contact_force":2.06903,"subtask_id":"push_goal","tcp_end":[0.49663,-0.0544,0.03596],"tcp_start":[0.50261,0.09992,0.04324],"tcp_to_object_dist_end":0.02936,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85938,"average_solve_count":64.0,"average_success_count":64.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_z_offset":0.07238,"descend_to_peg.descend_y_offset":0.02982,"push_channel.push_speed":0.05988,"push_channel.push_target_y_offset":-0.0165},"optimized_scores":{"best_composite_score":-0.10148,"best_fitness_score":0.15852,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":301.0,"contact_point_centroid":[0.50662,0.11414,0.00897],"force_p95":161.00918,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":170.28317,"mean_force":40.93875,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50338,0.12866,0.07717]},{"body_a":"attachment","body_b":"peg","contact_count":102.0,"contact_point_centroid":[0.51098,0.12982,0.05289],"force_p95":166.51003,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":169.64165,"mean_force":119.24518,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50419,0.13852,0.05201]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49089,0.1187,0.00671],"force_p95":97.95272,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":97.95272,"mean_force":97.95272,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50655,0.14512,0.04526]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50996,0.13467,0.04733],"force_p95":97.60562,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":97.60562,"mean_force":97.60562,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50655,0.14512,0.04526]},{"body_a":"peg","body_b":"channel_base_body","contact_count":598.0,"contact_point_centroid":[0.50364,0.11167,0.00939],"force_p95":0.61138,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55623,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50235,0.15717,0.20609]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.4998,0.19917,0.29883]},{"body_a":"peg","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.50607,0.12622,-3e-05],"force_p95":0.49392,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49392,"mean_force":0.49392,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50655,0.14512,0.04526]}],"total_contact_groups":7},"final_pose_error":0.24188,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50606,0.11875,0.02983],"final_tcp_position":[0.50656,0.14523,0.04522],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":170.28317,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":620.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.11174,0.03405],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":403.0,"raw_peak_contact_force":170.28317,"subtask_id":"approach_peg","tcp_end":[0.5062,0.11686,0.11984],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08598,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":301.0,"n_steps_budget":600.0,"object_pos_end":[0.5061,0.11869,0.02981],"object_pos_start":[0.50372,0.11174,0.03405],"object_to_goal_dist_end":0.19904,"object_to_goal_dist_start":0.19187,"object_z_max":0.03408,"peak_contact_force":97.95272,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3.0,"raw_peak_contact_force":97.95272,"tcp_end":[0.50655,0.14512,0.04526],"tcp_start":[0.5062,0.11686,0.11984],"tcp_to_object_dist_end":0.03062,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50606,0.11875,0.02983],"object_pos_start":[0.5061,0.11869,0.02981],"object_to_goal_dist_end":0.1991,"object_to_goal_dist_start":0.19904,"object_z_max":0.02981,"peak_contact_force":0.49916,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":614.0,"raw_peak_contact_force":2.06328,"subtask_id":"push_goal","tcp_end":[0.50656,0.14523,0.04522],"tcp_start":[0.50655,0.14512,0.04526],"tcp_to_object_dist_end":0.03063,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```