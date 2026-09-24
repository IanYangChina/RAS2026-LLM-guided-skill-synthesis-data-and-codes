## Search State

- **Seed**: 3
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.1421 | 0.28 | ❌ rejected |
| 13 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 10 | -0.4253 | 0.05 | ❌ rejected |
| 12 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.2344 | 0.03 | ❌ rejected |
| 11 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.1404 | 0.11 | ❌ rejected |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.3360 | 0.32 | ❌ rejected |

**Proposal policy**: task_score is 0.28 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.142) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_peg
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.05
  weight: 0.3
- id: push_progress
  target_entity: object
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
    entity: peg
    offset:
    - 0.0
    - 0.05
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
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_peg
- id: descend_1
  type: descend
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_peg
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: continue
  subtask_id: reach_peg
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: channel_exit
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.12
      - 0.18
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_safe
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
  retries:
    max_attempts: 1
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push_progress
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
  parameters:
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_peg, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=1.0
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, entity=channel_exit, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_safe, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
  - retries: max_attempts=1, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.142
- **task_score** (E): 0.283
- **fitness_score**: 0.502  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1310 |
| descend_1 | 1.00 | 1.00 | 0.1476 |
| push_1 | 0.00 | 1.00 | 0.1218 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.142, 0.187) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.547 | 3.954 |
| descend_1 | descend | 1.00 / step_budget | (0.505, 0.142, 0.187)→(0.517, 0.133, 0.042) | (0.502, 0.081, 0.034)→(0.502, 0.082, 0.034) | 0.162→0.162 | 1.00 / 1.333 | 133.154 | 207.817 |
| push_1 | push | 0.00 / guard_failure | (0.517, 0.133, 0.042)→(0.511, 0.011, 0.038) | (0.502, 0.082, 0.034)→(0.502, -0.025, 0.037) | 0.162→0.059 | 1.00 / 2.333 | 48.527 | 48.527 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.187
- terminal_score: 0.542
- phase_score: 0.871
- phase_breakdown.reach_peg_score: 0.681
- phase_breakdown.push_progress_score: 0.953

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.740
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.542
- **Median Q (composite search score)**: 0.236
- **K-run variance**: 0.0583
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.260


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.97101,"average_solve_count":276.0,"average_success_count":276.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1279,"approach_1.speed":0.03115,"descend_1.lateral_offset_x":0.02657,"descend_1.speed":0.03868,"push_1.speed":0.04537,"retract_1.speed":0.08238},"optimized_scores":{"best_composite_score":0.23571,"best_fitness_score":0.59571,"best_task_score":0.3058},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":89.0,"contact_point_centroid":[0.5252,0.1109,0.05997],"force_p95":536.75757,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":562.25806,"mean_force":418.65697,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51028,0.11092,0.0421]},{"body_a":"attachment","body_b":"peg","contact_count":143.0,"contact_point_centroid":[0.49899,0.00081,0.0416],"force_p95":31.02742,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.12517,"mean_force":7.50281,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50175,0.01192,0.0352]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.52517,0.1116,0.05997],"force_p95":33.9887,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":37.93817,"mean_force":10.67341,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50927,0.11154,0.03869]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":158.0,"contact_point_centroid":[0.47477,-0.0122,0.03739],"force_p95":30.61364,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.73069,"mean_force":4.96632,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50196,0.01613,0.03518]},{"body_a":"peg","body_b":"channel_base_body","contact_count":143.0,"contact_point_centroid":[0.49372,0.01815,0.00961],"force_p95":13.78999,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.73815,"mean_force":3.05198,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50429,0.05376,0.0359]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49317,-0.10009,0.01468],"force_p95":7.7288,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.7288,"mean_force":7.7288,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49895,-0.04999,0.03554]},{"body_a":"peg","body_b":"channel_base_body","contact_count":268.0,"contact_point_centroid":[0.49454,0.05907,0.00932],"force_p95":0.65931,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.60076,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48349,0.1587,0.23686]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49863,0.19745,0.29601]},{"body_a":"peg","body_b":"channel_base_body","contact_count":662.0,"contact_point_centroid":[0.49423,0.05886,0.00939],"force_p95":0.5503,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54611,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4919,0.11479,0.10356]}],"total_contact_groups":9},"final_pose_error":0.02984,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49272,-0.07998,0.03761],"final_tcp_position":[0.49897,-0.05051,0.03557],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":562.25806,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":297.0,"n_steps_budget":1000.0,"object_pos_end":[0.49407,0.05888,0.03384],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13914,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.5481,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":303.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_peg","tcp_end":[0.46956,0.12171,0.18281],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16352,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":662.0,"n_steps_budget":1000.0,"object_pos_end":[0.49421,0.05912,0.03392],"object_pos_start":[0.49407,0.05888,0.03384],"object_to_goal_dist_end":0.13937,"object_to_goal_dist_start":0.13914,"object_z_max":0.03392,"peak_contact_force":398.37338,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":751.0,"raw_peak_contact_force":562.25806,"subtask_id":"reach_peg","tcp_end":[0.50955,0.11173,0.03903],"tcp_start":[0.46956,0.12171,0.18281],"tcp_to_object_dist_end":0.05504,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":283.0,"n_steps_budget":1000.0,"object_pos_end":[0.49272,-0.07998,0.03761],"object_pos_start":[0.49421,0.05912,0.03392],"object_to_goal_dist_end":0.00766,"object_to_goal_dist_start":0.13937,"object_z_max":0.03765,"peak_contact_force":41.12517,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":454.0,"raw_peak_contact_force":41.12517,"subtask_id":"push_progress","tcp_end":[0.49897,-0.05051,0.03557],"tcp_start":[0.50955,0.11173,0.03903],"tcp_to_object_dist_end":0.03019,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.25472,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14371,"approach_1.speed":0.08534,"descend_1.lateral_offset_x":0.03425,"descend_1.speed":0.04777,"push_1.speed":0.04299,"retract_1.speed":0.05958},"optimized_scores":{"best_composite_score":-0.18922,"best_fitness_score":0.17078,"best_task_score":7e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.53811,0.12,0.06],"force_p95":63.78363,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":63.78363,"mean_force":63.78363,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53547,0.13209,0.04212]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.53628,0.12,0.06],"force_p95":60.19824,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":60.61271,"mean_force":52.6065,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53484,0.13204,0.05025]},{"body_a":"peg","body_b":"channel_base_body","contact_count":214.0,"contact_point_centroid":[0.50528,0.08081,0.00932],"force_p95":0.70082,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.61806,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51419,0.16838,0.24344]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50106,0.19698,0.29452]},{"body_a":"peg","body_b":"channel_base_body","contact_count":525.0,"contact_point_centroid":[0.50598,0.08094,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55079,"mean_force":0.54677,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53006,0.13608,0.11898]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.51358,0.06754,0.00938],"force_p95":0.54809,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54819,"mean_force":0.54715,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53552,0.1321,0.04223]}],"total_contact_groups":6},"final_pose_error":0.21502,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50596,0.08087,0.03378],"final_tcp_position":[0.53537,0.13208,0.04196],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":63.78363,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":243.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54584,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":250.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_peg","tcp_end":[0.52717,0.14174,0.19771],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.17614,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":525.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.54458,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":541.0,"raw_peak_contact_force":60.61271,"subtask_id":"reach_peg","tcp_end":[0.53558,0.13211,0.04235],"tcp_start":[0.52717,0.14174,0.19771],"tcp_to_object_dist_end":0.05979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":63.78363,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":63.78363,"subtask_id":"push_progress","tcp_end":[0.53537,0.13208,0.04196],"tcp_start":[0.53558,0.13211,0.04235],"tcp_to_object_dist_end":0.05962,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.89209,"average_solve_count":278.0,"average_success_count":278.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12247,"approach_1.speed":0.07859,"descend_1.lateral_offset_x":0.00239,"descend_1.speed":0.02317,"push_1.speed":0.03191,"retract_1.speed":0.06888},"optimized_scores":{"best_composite_score":0.37969,"best_fitness_score":0.73969,"best_task_score":0.54221},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_left_wall","contact_count":80.0,"contact_point_centroid":[0.52538,0.0158,0.03398],"force_p95":24.82017,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.67081,"mean_force":2.71251,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50007,0.04646,0.03739]},{"body_a":"attachment","body_b":"peg","contact_count":163.0,"contact_point_centroid":[0.50178,0.02969,0.04512],"force_p95":25.72349,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.59411,"mean_force":4.81367,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49995,0.0411,0.03729]},{"body_a":"peg","body_b":"channel_base_body","contact_count":150.0,"contact_point_centroid":[0.50338,0.03256,0.00948],"force_p95":25.94846,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.69124,"mean_force":4.68175,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50104,0.073,0.03838]},{"body_a":"peg","body_b":"channel_base_body","contact_count":224.0,"contact_point_centroid":[0.50536,0.10453,0.00935],"force_p95":0.65943,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.59685,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50914,0.17914,0.23464]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5005,0.19827,0.29497]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":23.0,"contact_point_centroid":[0.47448,0.02909,0.02755],"force_p95":1.10251,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.18913,"mean_force":0.47255,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50033,0.05947,0.03737]},{"body_a":"peg","body_b":"channel_base_body","contact_count":459.0,"contact_point_centroid":[0.50576,0.10466,0.00939],"force_p95":0.5755,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57958,"mean_force":0.54631,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51078,0.15738,0.11126]}],"total_contact_groups":7},"final_pose_error":0.03249,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50716,-0.07531,0.03823],"final_tcp_position":[0.49768,-0.04787,0.03581],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":40.67081,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":251.0,"n_steps_budget":1000.0,"object_pos_end":[0.50584,0.1046,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18479,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54737,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":256.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_peg","tcp_end":[0.51796,0.16124,0.17972],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15697,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":459.0,"n_steps_budget":1000.0,"object_pos_end":[0.50589,0.10472,0.03384],"object_pos_start":[0.50584,0.1046,0.03383],"object_to_goal_dist_end":0.18491,"object_to_goal_dist_start":0.18479,"object_z_max":0.03384,"peak_contact_force":0.54276,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":459.0,"raw_peak_contact_force":0.57958,"subtask_id":"reach_peg","tcp_end":[0.5055,0.15414,0.04324],"tcp_start":[0.51796,0.16124,0.17972],"tcp_to_object_dist_end":0.05031,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":348.0,"n_steps_budget":1000.0,"object_pos_end":[0.50716,-0.07531,0.03823],"object_pos_start":[0.50589,0.10472,0.03384],"object_to_goal_dist_end":0.00874,"object_to_goal_dist_start":0.18491,"object_z_max":0.0407,"peak_contact_force":40.67081,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":416.0,"raw_peak_contact_force":40.67081,"subtask_id":"push_progress","tcp_end":[0.49768,-0.04787,0.03581],"tcp_start":[0.5055,0.15414,0.04324],"tcp_to_object_dist_end":0.02913,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```