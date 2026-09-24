## Search State

- **Seed**: 5
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7  | -0.0306 | 0.00 | ❌ rejected |
| 11 | approach → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 7  | -0.1055 | 0.07 | ❌ rejected |
| 10 | approach → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 7  | -0.0562 | 0.00 | ❌ rejected |
| 9 | approach → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 8  | -0.1272 | 0.00 | ❌ rejected |
| 8 | approach → descend → push → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | force_exceeded | pose_tolerance | 10  | 0.1396 | 0.21 | ❌ rejected |

**Proposal policy**: task_score is 0.21 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.140) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach_peg
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.015
  weight: 0.3
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.05
    - 0.08
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.04
      - 0.12
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.arc_height
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: approach_peg
- id: descend_to_contact
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
    - 0.015
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_height:
      type: scalar
      range:
      - 0.0
      - 0.04
      default: 0.015
      binds_to:
      - path: target.offset.z
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: approach_peg
- id: push_along_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
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
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_force_threshold:
      type: scalar
      range:
      - 30.0
      - 39.0
      default: 36.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: push_to_goal
- id: retract_tcp
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
  retries:
    max_attempts: 0
    strategy: repeat

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.08], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_to_contact** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.015], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_height: status=consumed; consumers=target.offset.z (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **push_along_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **retract_tcp** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: 0.140
- **task_score** (E): 0.211
- **fitness_score**: 0.300  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1908 |
| descend_to_contact | 1.00 | 1.00 | 0.0568 |
| push_along_channel | 1.00 | 1.00 | 0.0654 |
| retract_tcp | 1.00 | 1.00 | 0.0804 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.510, 0.154, 0.116) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.547 | 2.488 |
| descend_to_contact | descend | 1.00 / step_budget | (0.510, 0.154, 0.116)→(0.502, 0.145, 0.061) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.547 | 0.587 |
| push_along_channel | push | 1.00 / force_exceeded | (0.502, 0.145, 0.061)→(0.500, 0.080, 0.057) | (0.504, 0.095, 0.034)→(0.505, 0.062, 0.038) | 0.175→0.142 | 1.00 / 4.000 | 39.280 | 39.280 |
| retract_tcp | retract | 1.00 / step_budget | (0.500, 0.080, 0.057)→(0.497, 0.079, 0.137) | (0.505, 0.062, 0.038)→(0.505, 0.049, 0.027) | 0.142→0.130 | 1.00 / 1.000 | 0.517 | 266.463 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.401
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.401
- phase_score: 0.415
- phase_breakdown.approach_peg_score: 0.792
- phase_breakdown.push_to_goal_score: 0.254

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.410
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.401
- **Median Q (composite search score)**: 0.143
- **K-run variance**: 0.0083
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.231


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.83243,"average_solve_count":185.0,"average_success_count":185.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09817,"approach_1.arc_height":0.04524,"descend_to_contact.descend_height":0.01731,"descend_to_contact.descend_speed":0.01689,"push_along_channel.push_distance":0.1603,"push_along_channel.push_force_threshold":32.84297,"push_along_channel.push_speed":0.07636},"optimized_scores":{"best_composite_score":0.14283,"best_fitness_score":0.30283,"best_task_score":0.20884},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":18.0,"contact_point_centroid":[0.475,0.11995,0.05106],"force_p95":164.57255,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":171.58347,"mean_force":76.39873,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.50174,0.08002,0.06558]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.525,0.11986,0.03575],"force_p95":27.73912,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":36.98549,"mean_force":6.16425,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.50282,0.0798,0.0568]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.475,0.11995,0.04395],"force_p95":33.47665,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":34.41415,"mean_force":24.9577,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50283,0.07994,0.05674]},{"body_a":"peg","body_b":"channel_base_body","contact_count":584.0,"contact_point_centroid":[0.50593,0.0867,0.00969],"force_p95":13.38905,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.59126,"mean_force":5.18005,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50274,0.11658,0.05637]},{"body_a":"attachment","body_b":"peg","contact_count":339.0,"contact_point_centroid":[0.50479,0.10093,0.04452],"force_p95":13.89821,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.28058,"mean_force":8.14127,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50259,0.10098,0.05625]},{"body_a":"peg","body_b":"channel_base_body","contact_count":239.0,"contact_point_centroid":[0.50568,0.05484,0.00956],"force_p95":1.02472,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.95389,"mean_force":0.60235,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.50078,0.07937,0.09523]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.525,0.11992,0.03566],"force_p95":12.89659,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":13.46773,"mean_force":7.37252,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50283,0.07994,0.05674]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.5046,0.07983,0.04509],"force_p95":10.29439,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.38714,"mean_force":2.40054,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.50282,0.0798,0.0568]},{"body_a":"peg","body_b":"channel_base_body","contact_count":586.0,"contact_point_centroid":[0.50571,0.10466,0.00937],"force_p95":0.57641,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56562,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50724,0.20979,0.20443]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50507,0.21978,0.29095]},{"body_a":"peg","body_b":"channel_base_body","contact_count":262.0,"contact_point_centroid":[0.50586,0.10451,0.00939],"force_p95":0.57566,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57608,"mean_force":0.54638,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51319,0.15883,0.10043]}],"total_contact_groups":11},"final_pose_error":0.01973,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5047,0.03496,0.02365],"final_tcp_position":[0.50056,0.07873,0.13718],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":171.58347,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":613.0,"n_steps_budget":1000.0,"object_pos_end":[0.50591,0.10456,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54366,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":618.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach_peg","tcp_end":[0.52116,0.1639,0.13776],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12064,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":262.0,"n_steps_budget":1000.0,"object_pos_end":[0.50584,0.10459,0.03384],"object_pos_start":[0.50591,0.10456,0.03384],"object_to_goal_dist_end":0.18479,"object_to_goal_dist_start":0.18476,"object_z_max":0.03384,"peak_contact_force":0.55203,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":262.0,"raw_peak_contact_force":0.57608,"subtask_id":"approach_peg","tcp_end":[0.50558,0.15433,0.06089],"tcp_start":[0.52116,0.1639,0.13776],"tcp_to_object_dist_end":0.05662,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":589.0,"n_steps_budget":1000.0,"object_pos_end":[0.50629,0.06155,0.0404],"object_pos_start":[0.50584,0.10459,0.03384],"object_to_goal_dist_end":0.14169,"object_to_goal_dist_start":0.18479,"object_z_max":0.04043,"peak_contact_force":34.41415,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":929.0,"raw_peak_contact_force":34.41415,"subtask_id":"push_to_goal","tcp_end":[0.50283,0.07977,0.05675],"tcp_start":[0.50558,0.15433,0.06089],"tcp_to_object_dist_end":0.02472,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":247.0,"n_steps_budget":630.0,"object_pos_end":[0.5047,0.03496,0.02365],"object_pos_start":[0.50629,0.06155,0.0404],"object_to_goal_dist_end":0.11621,"object_to_goal_dist_start":0.14169,"object_z_max":0.04077,"peak_contact_force":0.44992,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":269.0,"raw_peak_contact_force":171.58347,"tcp_end":[0.50056,0.07873,0.13718],"tcp_start":[0.50283,0.07977,0.05675],"tcp_to_object_dist_end":0.12175,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5339,"average_solve_count":118.0,"average_success_count":118.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.06132,"approach_1.arc_height":0.05169,"descend_to_contact.descend_height":0.01537,"descend_to_contact.descend_speed":0.04322,"push_along_channel.push_distance":0.14673,"push_along_channel.push_force_threshold":36.86225,"push_along_channel.push_speed":0.03412},"optimized_scores":{"best_composite_score":0.02623,"best_fitness_score":0.18623,"best_task_score":0.02256},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.475,0.11998,0.04504],"force_p95":249.27497,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":463.72752,"mean_force":87.6921,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49535,0.08017,0.06862]},{"body_a":"world","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.4975,0.1417,-1e-05],"force_p95":346.67357,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":360.21006,"mean_force":213.71982,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49688,0.07998,0.05465]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.475,0.11997,0.0329],"force_p95":48.5186,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":49.21634,"mean_force":42.23891,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49689,0.08007,0.05465]},{"body_a":"world","body_b":"link7","contact_count":403.0,"contact_point_centroid":[0.49756,0.1586,-0.0],"force_p95":34.6711,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":36.1739,"mean_force":29.44581,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49692,0.09688,0.05466]},{"body_a":"peg","body_b":"channel_base_body","contact_count":637.0,"contact_point_centroid":[0.50306,0.0645,0.00946],"force_p95":5.63086,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.26812,"mean_force":0.99495,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49701,0.09799,0.05479]},{"body_a":"attachment","body_b":"peg","contact_count":98.0,"contact_point_centroid":[0.50262,0.08274,0.04412],"force_p95":7.72509,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.06118,"mean_force":3.11231,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.4969,0.0828,0.05466]},{"body_a":"peg","body_b":"channel_base_body","contact_count":746.0,"contact_point_centroid":[0.50303,0.06743,0.00935],"force_p95":0.55455,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55818,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49706,0.194,0.18462]},{"body_a":"peg","body_b":"channel_base_body","contact_count":244.0,"contact_point_centroid":[0.50299,0.05966,0.00958],"force_p95":0.62586,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.84317,"mean_force":0.51695,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49476,0.07967,0.09371]},{"body_a":"attachment","body_b":"peg","contact_count":23.0,"contact_point_centroid":[0.50244,0.08022,0.05217],"force_p95":0.7282,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.77999,"mean_force":0.34687,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49581,0.08024,0.06214]},{"body_a":"peg","body_b":"channel_base_body","contact_count":146.0,"contact_point_centroid":[0.50306,0.06769,0.00938],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55081,"mean_force":0.54668,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.49935,0.12251,0.08012]}],"total_contact_groups":10},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5032,0.06385,0.03391],"final_tcp_position":[0.49461,0.07898,0.13481],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":463.72752,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":762.0,"n_steps_budget":1000.0,"object_pos_end":[0.50304,0.0675,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54581,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":746.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach_peg","tcp_end":[0.50031,0.12688,0.10061],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08943,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":146.0,"n_steps_budget":780.0,"object_pos_end":[0.50308,0.06748,0.0338],"object_pos_start":[0.50304,0.0675,0.0338],"object_to_goal_dist_end":0.14765,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"peak_contact_force":0.54732,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":146.0,"raw_peak_contact_force":0.55081,"subtask_id":"approach_peg","tcp_end":[0.49941,0.11845,0.05841],"tcp_start":[0.50031,0.12688,0.10061],"tcp_to_object_dist_end":0.05672,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":637.0,"n_steps_budget":1000.0,"object_pos_end":[0.50306,0.06242,0.03599],"object_pos_start":[0.50308,0.06748,0.0338],"object_to_goal_dist_end":0.14251,"object_to_goal_dist_start":0.14765,"object_z_max":0.03598,"peak_contact_force":49.21634,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1140.0,"raw_peak_contact_force":49.21634,"subtask_id":"push_to_goal","tcp_end":[0.49689,0.07999,0.05465],"tcp_start":[0.49941,0.11845,0.05841],"tcp_to_object_dist_end":0.02637,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":244.0,"n_steps_budget":630.0,"object_pos_end":[0.5032,0.06385,0.03391],"object_pos_start":[0.50306,0.06242,0.03599],"object_to_goal_dist_end":0.14402,"object_to_goal_dist_start":0.14251,"object_z_max":0.036,"peak_contact_force":0.55109,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":295.0,"raw_peak_contact_force":463.72752,"tcp_end":[0.49461,0.07898,0.13481],"tcp_start":[0.49689,0.07999,0.05465],"tcp_to_object_dist_end":0.1024,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55469,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07034,"approach_1.arc_height":0.05467,"descend_to_contact.descend_height":0.01985,"descend_to_contact.descend_speed":0.03096,"push_along_channel.push_distance":0.15084,"push_along_channel.push_force_threshold":32.7736,"push_along_channel.push_speed":0.06608},"optimized_scores":{"best_composite_score":0.24959,"best_fitness_score":0.40959,"best_task_score":0.40105},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.475,0.11995,0.04914],"force_p95":154.91429,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":164.07891,"mean_force":69.83582,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49782,0.08011,0.06969]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.525,0.11989,0.0428],"force_p95":26.54052,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":35.38736,"mean_force":5.89789,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49911,0.07982,0.05935]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.475,0.11992,0.04093],"force_p95":33.82012,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":34.20931,"mean_force":30.31748,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49916,0.07996,0.05929]},{"body_a":"peg","body_b":"channel_base_body","contact_count":744.0,"contact_point_centroid":[0.50423,0.09379,0.00968],"force_p95":13.78653,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.21101,"mean_force":5.58551,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49896,0.12026,0.0587]},{"body_a":"attachment","body_b":"peg","contact_count":465.0,"contact_point_centroid":[0.50233,0.10506,0.04729],"force_p95":13.89194,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.88874,"mean_force":8.19185,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49887,0.10513,0.05867]},{"body_a":"peg","body_b":"channel_base_body","contact_count":243.0,"contact_point_centroid":[0.50636,0.05249,0.00845],"force_p95":1.29791,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.17874,"mean_force":0.92615,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49705,0.07947,0.0987]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.50196,0.0798,0.04793],"force_p95":17.40522,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.63516,"mean_force":4.20571,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.4991,0.07988,0.05938]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":13.0,"contact_point_centroid":[0.52501,0.02343,0.02515],"force_p95":9.55502,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.75754,"mean_force":4.14704,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49696,0.08027,0.078]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.525,0.11995,0.0426],"force_p95":3.69331,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.88769,"mean_force":1.94385,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49916,0.07996,0.05929]},{"body_a":"peg","body_b":"channel_base_body","contact_count":693.0,"contact_point_centroid":[0.5036,0.11167,0.00938],"force_p95":0.60176,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55566,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50023,0.21865,0.19626]},{"body_a":"peg","body_b":"channel_base_body","contact_count":157.0,"contact_point_centroid":[0.50376,0.11157,0.00939],"force_p95":0.59879,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63386,"mean_force":0.5447,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50413,0.16659,0.08766]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50399,0.20577,0.29976]}],"total_contact_groups":12},"final_pose_error":0.01974,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50639,0.04761,0.02413],"final_tcp_position":[0.49692,0.07881,0.13971],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":164.07891,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":715.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.11176,0.03381],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.55222,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":709.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach_peg","tcp_end":[0.50713,0.1712,0.11051],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0971,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":157.0,"n_steps_budget":1000.0,"object_pos_end":[0.5037,0.11172,0.03384],"object_pos_start":[0.50377,0.11176,0.03381],"object_to_goal_dist_end":0.19185,"object_to_goal_dist_start":0.19189,"object_z_max":0.03386,"peak_contact_force":0.54233,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":157.0,"raw_peak_contact_force":0.63386,"subtask_id":"approach_peg","tcp_end":[0.5018,0.16236,0.06322],"tcp_start":[0.50713,0.1712,0.11051],"tcp_to_object_dist_end":0.05858,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":744.0,"n_steps_budget":1000.0,"object_pos_end":[0.50579,0.06306,0.03792],"object_pos_start":[0.5037,0.11172,0.03384],"object_to_goal_dist_end":0.14319,"object_to_goal_dist_start":0.19185,"object_z_max":0.04048,"peak_contact_force":34.20931,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1213.0,"raw_peak_contact_force":34.20931,"subtask_id":"push_to_goal","tcp_end":[0.49916,0.07982,0.0593],"tcp_start":[0.5018,0.16236,0.06322],"tcp_to_object_dist_end":0.02796,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":247.0,"n_steps_budget":630.0,"object_pos_end":[0.50639,0.04761,0.02413],"object_pos_start":[0.50579,0.06306,0.03792],"object_to_goal_dist_end":0.12875,"object_to_goal_dist_start":0.14319,"object_z_max":0.03792,"peak_contact_force":0.55104,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":292.0,"raw_peak_contact_force":164.07891,"tcp_end":[0.49692,0.07881,0.13971],"tcp_start":[0.49916,0.07982,0.0593],"tcp_to_object_dist_end":0.12009,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```