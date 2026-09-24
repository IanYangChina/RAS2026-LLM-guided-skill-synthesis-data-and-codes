## Search State

- **Seed**: 9
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.0634 | 0.17 | ✅ accepted |
| 10 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.2612 | 0.04 | ❌ rejected |
| 9 | approach → descend → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 7 | -0.1072 | 0.00 | ❌ rejected |
| 8 | approach → descend → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 7 | -0.0269 | 0.00 | ❌ rejected |
| 7 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 0.0693 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.17 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`
- Frozen object start: [0.5296199363176067, -0.09705462327299558, 0.04]
- Frozen task target: [0.5, 0.2, 0.3]
- Goal object position: (0.5, 0.2, 0.3)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5296199363176067, -0.09705462327299558, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5296199363176067, 0.06294537672700443, 0.04)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5296199363176067, 0.06294537672700443, 0.04]
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
  frozen_object_start: [0.5296, 0.0629, 0.04]
  frozen_task_target: [0.5296, -0.0971, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5296199363176067, -0.09705462327299558, 0.04]}
  frozen_targets: {'channel_exit': [0.5, 0.2, 0.3]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9

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
| `object` | offset from object initial position (0.5296199363176067, -0.09705462327299558, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.2, 0.3) | final destination targets |
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

## Current Skill (Q=0.063) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.0
  weight: 0.3
- id: push_along_channel
  anchor: fixture
  target_entity: object
  metric: goal_progress
  offset:
  - 0.0
  - -0.16
  - 0.0
  weight: 0.7
phases:
- id: approach_to_peg
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.05
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: approach_pose
    when: after_phase
    predicate: pose_within_tolerance
    threshold: 0.008
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: reach_pre_contact
- id: contact_peg
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - -0.02
    - 0.0
    offset_along_axis:
      distance: 0.03
      axis: channel_axis
      mode: replace_offset_projection
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 20.0
      default: 10.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_success
    when: after_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
  subtask_id: push_along_channel
- id: push_through_channel
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
    duration_max_time:
      type: scalar
      range:
      - 2.0
      - 6.0
      default: 4.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.18
      binds_to:
      - path: target.offset_along_axis.distance
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
  guards:
  - id: push_force
    when: during_phase
    predicate: force_below
    threshold: 35.0
    on_failure: abort
  subtask_id: push_along_channel
- id: retract_after_push
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.05
    - 0.04
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_to_peg** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=approach_pose, when=after_phase, predicate=pose_within_tolerance, on_failure=retry, threshold=0.008
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **contact_peg** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, -0.02, 0.0], offset_along_axis={axis=channel_axis, distance=0.03, mode=replace_offset_projection, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_success, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **push_through_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.2, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - duration_max_time: status=consumed; consumers=duration.max_time (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=push_force, when=during_phase, predicate=force_below, on_failure=abort, threshold=35.0
- **retract_after_push** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.05, 0.04]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.063
- **task_score** (E): 0.174
- **fitness_score**: 0.423  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_peg | 0.00 | 1.00 | 0.0704 |
| contact_peg | 0.00 | 1.00 | 0.0212 |
| push_through_channel | 1.00 | 1.00 | 0.0889 |
| retract_after_push | 1.00 | 1.00 | 0.0552 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_peg | approach | 0.00 / step_budget | (0.505, 0.137, 0.101)→(0.499, 0.118, 0.036) | (0.512, 0.067, 0.040)→(0.502, 0.067, 0.034) | 0.150→0.147 | 1.00 / 1.000 | 0.550 | 4.034 |
| contact_peg | contact | 0.00 / step_budget | (0.499, 0.118, 0.036)→(0.498, 0.098, 0.029) | (0.502, 0.067, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 1.000 | 0.543 | 0.553 |
| push_through_channel | push | 1.00 / time_limit | (0.498, 0.098, 0.029)→(0.495, 0.009, 0.025) | (0.502, 0.067, 0.034)→(0.506, -0.019, 0.036) | 0.147→0.062 | 1.00 / 3.000 | 16.407 | 34.331 |
| retract_after_push | retract | 1.00 / step_budget | (0.495, 0.009, 0.025)→(0.492, 0.054, 0.058) | (0.506, -0.019, 0.036)→(0.506, -0.018, 0.034) | 0.062→0.063 | 1.00 / 1.667 | 1.683 | 110.005 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.611
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.253
- phase_score: 0.654
- phase_breakdown.push_along_channel_score: 0.680
- phase_breakdown.reach_pre_contact_score: 0.593

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.494
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.253
- **Median Q (composite search score)**: 0.108
- **K-run variance**: 0.0067
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.325


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `bf8103833c1e96f48e87b3ce39b3b3bf17e268470bd7b5c037546fb78b5150b8`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `98954a34ee744fa939070f7dadee8a411de43cdcfeddcf3b4bfc5c3a4c536020`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,-0.09705,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,-0.09705,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42336,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_peg.approach_speed":0.10667,"contact_peg.contact_force_threshold":11.9705,"contact_peg.contact_speed":0.02538,"push_through_channel.duration_max_time":3.72488,"push_through_channel.push_distance":0.15497,"push_through_channel.push_speed":0.06094},"optimized_scores":{"best_composite_score":0.13369,"best_fitness_score":0.49369,"best_task_score":0.25301},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.53476,0.00061,0.05999],"force_p95":81.86998,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":85.36766,"mean_force":58.10373,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49846,-0.00592,0.02538]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":391.0,"contact_point_centroid":[0.53469,0.04796,0.06],"force_p95":30.67939,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":34.06633,"mean_force":24.24547,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4984,0.0414,0.0254]},{"body_a":"attachment","body_b":"peg","contact_count":779.0,"contact_point_centroid":[0.50372,0.0313,0.04383],"force_p95":8.24797,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.12716,"mean_force":3.07329,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49846,0.0431,0.02546]},{"body_a":"peg","body_b":"channel_base_body","contact_count":710.0,"contact_point_centroid":[0.50613,-0.0006,0.00991],"force_p95":8.37876,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.13049,"mean_force":3.5523,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49855,0.04511,0.02556]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":459.0,"contact_point_centroid":[0.52507,0.01813,0.02537],"force_p95":2.95846,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.76878,"mean_force":0.92153,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49845,0.04703,0.02545]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1281.0,"contact_point_centroid":[0.5059,0.06298,0.00937],"force_p95":0.55399,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.55713,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.50898,0.15585,0.16533]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.49968,0.19886,0.2971]},{"body_a":"peg","body_b":"channel_base_body","contact_count":422.0,"contact_point_centroid":[0.50603,-0.03521,0.00944],"force_p95":0.58935,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.48396,"mean_force":0.54534,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.4951,0.01812,0.0407]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50378,-0.01775,0.04391],"force_p95":0.84216,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.90843,"mean_force":0.38474,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49846,-0.00592,0.02538]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":124.0,"contact_point_centroid":[0.52502,-0.03472,0.05227],"force_p95":0.25301,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58312,"mean_force":0.06456,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49546,0.0151,0.03875]},{"body_a":"peg","body_b":"channel_base_body","contact_count":422.0,"contact_point_centroid":[0.50599,0.06305,0.00938],"force_p95":0.55156,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55493,"mean_force":0.54648,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50129,0.10286,0.03139]}],"total_contact_groups":11},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50699,-0.03482,0.03378],"final_tcp_position":[0.49477,0.03956,0.05735],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":85.36766,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1309.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06297,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.55256,"phase_name":"approach_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1315.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_pre_contact","tcp_end":[0.50364,0.11489,0.03775],"tcp_start":[0.51838,0.13472,0.1028],"tcp_to_object_dist_end":0.05212,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":422.0,"n_steps_budget":600.0,"object_pos_end":[0.50602,0.06291,0.03384],"object_pos_start":[0.50596,0.06294,0.03381],"object_to_goal_dist_end":0.14317,"object_to_goal_dist_start":0.1432,"object_z_max":0.03384,"peak_contact_force":0.5438,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":422.0,"raw_peak_contact_force":0.55493,"subtask_id":"push_along_channel","tcp_end":[0.50176,0.09417,0.02932],"tcp_start":[0.50364,0.11489,0.03775],"tcp_to_object_dist_end":0.03188,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.507,-0.03501,0.03563],"object_pos_start":[0.50602,0.06291,0.03384],"object_to_goal_dist_end":0.04574,"object_to_goal_dist_start":0.14317,"object_z_max":0.03594,"peak_contact_force":20.08341,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2339.0,"raw_peak_contact_force":34.06633,"subtask_id":"push_along_channel","tcp_end":[0.49847,-0.00587,0.02539],"tcp_start":[0.50176,0.09417,0.02932],"tcp_to_object_dist_end":0.03204,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":423.0,"n_steps_budget":600.0,"object_pos_end":[0.50699,-0.03482,0.03378],"object_pos_start":[0.507,-0.03501,0.03563],"object_to_goal_dist_end":0.04614,"object_to_goal_dist_start":0.04574,"object_z_max":0.03563,"peak_contact_force":2.26172,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":552.0,"raw_peak_contact_force":85.36766,"tcp_end":[0.49477,0.03956,0.05735],"tcp_start":[0.49847,-0.00587,0.02539],"tcp_to_object_dist_end":0.07897,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `cae0d95026bac46aa2e5d95cffd531753a79751757c4f25fa56c1ec6e19c2175`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,-0.10339,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,-0.10339,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44681,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_peg.approach_speed":0.09295,"contact_peg.contact_force_threshold":10.47426,"contact_peg.contact_speed":0.03024,"push_through_channel.duration_max_time":3.32921,"push_through_channel.push_distance":0.1566,"push_through_channel.push_speed":0.06167},"optimized_scores":{"best_composite_score":0.10789,"best_fitness_score":0.46789,"best_task_score":0.18082},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.53501,-0.00653,0.05998],"force_p95":52.7058,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":52.98711,"mean_force":46.97687,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.4987,-0.01304,0.02537]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":383.0,"contact_point_centroid":[0.53495,0.04029,0.06],"force_p95":31.3451,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":34.28711,"mean_force":24.55299,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49865,0.03374,0.02541]},{"body_a":"peg","body_b":"channel_base_body","contact_count":712.0,"contact_point_centroid":[0.50556,-0.00667,0.0099],"force_p95":8.35197,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.52872,"mean_force":3.45407,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4988,0.03914,0.02558]},{"body_a":"attachment","body_b":"peg","contact_count":760.0,"contact_point_centroid":[0.50362,0.02512,0.04331],"force_p95":8.29077,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.26535,"mean_force":3.00366,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49871,0.03696,0.02548]},{"body_a":"peg","body_b":"channel_base_body","contact_count":422.0,"contact_point_centroid":[0.50665,-0.04248,0.00942],"force_p95":0.59822,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.99262,"mean_force":0.56561,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49537,0.01102,0.04068]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50386,-0.02488,0.04419],"force_p95":8.33006,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.76268,"mean_force":4.43653,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49872,-0.01297,0.02539]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":413.0,"contact_point_centroid":[0.52505,-0.00072,0.02826],"force_p95":2.67887,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.62331,"mean_force":0.89675,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49865,0.02836,0.02541]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1319.0,"contact_point_centroid":[0.50601,0.05664,0.00937],"force_p95":0.60412,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.55861,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.51105,0.15338,0.16699]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.49972,0.19874,0.29685]},{"body_a":"peg","body_b":"channel_base_body","contact_count":423.0,"contact_point_centroid":[0.5061,0.05649,0.00939],"force_p95":0.55133,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55483,"mean_force":0.54638,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50159,0.0967,0.03138]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":86.0,"contact_point_centroid":[0.52501,-0.04195,0.05883],"force_p95":0.07128,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21824,"mean_force":0.01695,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49532,0.01241,0.04172]}],"total_contact_groups":11},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50696,-0.04199,0.03382],"final_tcp_position":[0.49503,0.03254,0.05737],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":52.98711,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1348.0,"n_steps_budget":1000.0,"object_pos_end":[0.5061,0.05659,0.0338],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.54752,"phase_name":"approach_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1356.0,"raw_peak_contact_force":4.44541,"subtask_id":"reach_pre_contact","tcp_end":[0.50402,0.10877,0.03768],"tcp_start":[0.52215,0.13336,0.11195],"tcp_to_object_dist_end":0.05236,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":423.0,"n_steps_budget":600.0,"object_pos_end":[0.5061,0.0567,0.03385],"object_pos_start":[0.5062,0.05664,0.03383],"object_to_goal_dist_end":0.13698,"object_to_goal_dist_start":0.13692,"object_z_max":0.03385,"peak_contact_force":0.54582,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":423.0,"raw_peak_contact_force":0.55483,"subtask_id":"push_along_channel","tcp_end":[0.50201,0.08794,0.02935],"tcp_start":[0.50402,0.10877,0.03768],"tcp_to_object_dist_end":0.03182,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5067,-0.04233,0.03534],"object_pos_start":[0.5061,0.0567,0.03385],"object_to_goal_dist_end":0.03855,"object_to_goal_dist_start":0.13698,"object_z_max":0.03582,"peak_contact_force":5.95844,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2268.0,"raw_peak_contact_force":34.28711,"subtask_id":"push_along_channel","tcp_end":[0.49873,-0.01293,0.0254],"tcp_start":[0.50201,0.08794,0.02935],"tcp_to_object_dist_end":0.03204,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":422.0,"n_steps_budget":600.0,"object_pos_end":[0.50696,-0.04199,0.03382],"object_pos_start":[0.5067,-0.04233,0.03534],"object_to_goal_dist_end":0.03913,"object_to_goal_dist_start":0.03855,"object_z_max":0.03543,"peak_contact_force":2.23895,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":513.0,"raw_peak_contact_force":52.98711,"tcp_end":[0.49503,0.03254,0.05737],"tcp_start":[0.49873,-0.01293,0.0254],"tcp_to_object_dist_end":0.07907,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `fd7ada9a67242f1adcdb6e23860d1223cdc8a17daf859e94e1687ff0564d9575`; realized-scene SHA-256: `8df62a5afc1e0110114ab6e06b493b5783d0c746729f7f7f1f2cb046babeda91`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47029,-0.08006,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.47029,0.07994,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.47029,-0.08006,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32278,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_peg.approach_speed":0.07628,"contact_peg.contact_force_threshold":14.8976,"contact_peg.contact_speed":0.04552,"push_through_channel.duration_max_time":2.16584,"push_through_channel.push_distance":0.13982,"push_through_channel.push_speed":0.03887},"optimized_scores":{"best_composite_score":-0.05129,"best_fitness_score":0.30871,"best_task_score":0.08706},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":398.0,"contact_point_centroid":[0.47498,0.0661,0.04386],"force_p95":148.07682,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":191.66064,"mean_force":84.59005,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.48679,0.0661,0.04187]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":632.0,"contact_point_centroid":[0.475,0.07761,0.02751],"force_p95":30.42617,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":34.63852,"mean_force":22.22025,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48683,0.07762,0.02555]},{"body_a":"peg","body_b":"channel_base_body","contact_count":479.0,"contact_point_centroid":[0.50465,0.02085,0.00946],"force_p95":0.5747,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.77982,"mean_force":0.61009,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.48678,0.06678,0.04241]},{"body_a":"peg","body_b":"channel_base_body","contact_count":959.0,"contact_point_centroid":[0.50689,0.03601,0.00992],"force_p95":12.73531,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.50159,"mean_force":5.87806,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4869,0.07714,0.02565]},{"body_a":"peg","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.51917,0.03152,0.06116],"force_p95":12.74186,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.83656,"mean_force":2.8146,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.4868,0.04594,0.02566]},{"body_a":"peg","body_b":"link7","contact_count":684.0,"contact_point_centroid":[0.51793,0.05221,0.06131],"force_p95":11.0457,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.7488,"mean_force":5.4223,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48684,0.06789,0.02556]},{"body_a":"attachment","body_b":"peg","contact_count":905.0,"contact_point_centroid":[0.49476,0.06495,0.04325],"force_p95":5.98688,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.43263,"mean_force":3.62735,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48686,0.07571,0.0256]},{"body_a":"attachment","body_b":"peg","contact_count":31.0,"contact_point_centroid":[0.49711,0.03685,0.05747],"force_p95":3.38174,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.76032,"mean_force":0.6565,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.48678,0.04768,0.02705]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1688.0,"contact_point_centroid":[0.4939,0.07995,0.00938],"force_p95":0.55795,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.55421,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.48349,0.1554,0.13217]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46907,0.07994,0.03235],"force_p95":1.18295,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.45938,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.49922,0.199,0.2972]},{"body_a":"peg","body_b":"channel_base_body","contact_count":434.0,"contact_point_centroid":[0.49386,0.07989,0.00938],"force_p95":0.55021,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55021,"mean_force":0.54668,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48798,0.1189,0.02836]}],"total_contact_groups":11},"final_pose_error":0.00992,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50371,0.02225,0.03379],"final_tcp_position":[0.48584,0.0886,0.05885],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":191.66064,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1716.0,"n_steps_budget":1000.0,"object_pos_end":[0.4938,0.07996,0.03378],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.1602,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.55021,"phase_name":"approach_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1723.0,"raw_peak_contact_force":3.77147,"subtask_id":"reach_pre_contact","tcp_end":[0.48907,0.12947,0.03124],"tcp_start":[0.473,0.14323,0.0887],"tcp_to_object_dist_end":0.0498,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":434.0,"n_steps_budget":600.0,"object_pos_end":[0.49382,0.07997,0.03378],"object_pos_start":[0.49381,0.07993,0.03378],"object_to_goal_dist_end":0.16021,"object_to_goal_dist_start":0.16017,"object_z_max":0.03378,"peak_contact_force":0.54035,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":434.0,"raw_peak_contact_force":0.55021,"subtask_id":"push_along_channel","tcp_end":[0.4894,0.11115,0.02883],"tcp_start":[0.48907,0.12947,0.03124],"tcp_to_object_dist_end":0.03188,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50499,0.0209,0.03626],"object_pos_start":[0.49382,0.07997,0.03378],"object_to_goal_dist_end":0.10109,"object_to_goal_dist_start":0.16021,"object_z_max":0.03628,"peak_contact_force":23.17819,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3180.0,"raw_peak_contact_force":34.63852,"subtask_id":"push_along_channel","tcp_end":[0.48683,0.04584,0.02557],"tcp_start":[0.4894,0.11115,0.02883],"tcp_to_object_dist_end":0.03265,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":479.0,"n_steps_budget":600.0,"object_pos_end":[0.50371,0.02225,0.03379],"object_pos_start":[0.50499,0.0209,0.03626],"object_to_goal_dist_end":0.10251,"object_to_goal_dist_start":0.10109,"object_z_max":0.03626,"peak_contact_force":0.54945,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":920.0,"raw_peak_contact_force":191.66064,"tcp_end":[0.48584,0.0886,0.05885],"tcp_start":[0.48683,0.04584,0.02557],"tcp_to_object_dist_end":0.07314,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```