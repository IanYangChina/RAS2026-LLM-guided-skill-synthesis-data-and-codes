## Search State

- **Seed**: 6
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 10 | -0.1189 | 0.23 | ❌ rejected |
| 13 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 11 | -0.0929 | 0.13 | ❌ rejected |
| 12 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 13 | -0.2290 | 0.44 | ❌ rejected |
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | -0.0302 | 0.22 | ❌ rejected |
| 10 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 11 | -0.0749 | 0.14 | ❌ rejected |

**Proposal policy**: task_score is 0.23 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`
- Frozen object start: [0.5030531481177555, 0.06746166958506708, 0.04]
- Frozen task target: [0.5030531481177555, -0.09253833041493292, 0.04]
- Goal object position: (0.5030531481177555, -0.09253833041493292, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5030531481177555, 0.06746166958506708, 0.04)
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
  frozen_object_start: [0.5031, 0.0675, 0.04]
  frozen_task_target: [0.5031, -0.0925, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5030531481177555, 0.06746166958506708, 0.04]}
  frozen_targets: {'channel_exit': [0.5030531481177555, -0.09253833041493292, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de

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
| `object` | offset from object initial position (0.5030531481177555, 0.06746166958506708, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5030531481177555, -0.09253833041493292, 0.04) | final destination targets |
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

## Current Skill (Q=-0.119) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: behind_peg
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.1
  weight: 0.3
- id: insertion_progress
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach
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
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.001
      - 0.01
      default: 0.005
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: behind_peg
- id: descend
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
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    descend_tolerance:
      type: scalar
      range:
      - 0.001
      - 0.01
      default: 0.005
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    descend_z_offset:
      type: scalar
      range:
      - -0.01
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: add
- id: contact_seating
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    entity: channel_exit
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.015
      binds_to:
      - path: generator.speed
        mode: replace
- id: push
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    entity: channel_exit
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    push_max_time:
      type: scalar
      range:
      - 2.0
      - 8.0
      default: 5.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.005
      - 0.04
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 39.0
    on_failure: retry
  retries:
    max_attempts: 3
    strategy: reduce_speed
  subtask_id: insertion_progress

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.1]
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.0]
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - descend_z_offset: status=consumed; consumers=target.offset.z (add)
- **contact_seating** (`contact`)
  - target: source=yaml, anchor=task_goal, entity=channel_exit, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push** (`push`)
  - target: source=yaml, anchor=task_goal, entity=channel_exit, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - push_max_time: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=39.0
  - retries: max_attempts=3, strategy=reduce_speed

## Design Metrics

- **Composite score**: -0.119
- **task_score** (E): 0.226
- **fitness_score**: 0.219  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.222
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.560

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.1654 |
| descend | 1.00 | 1.00 | 0.0909 |
| engage_peg | 0.67 | 1.00 | 0.0163 |
| push_along_channel | 1.00 | 1.00 | 0.0550 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.151, 0.144) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.533 | 2.127 |
| descend | descend | 1.00 / step_budget | (0.497, 0.151, 0.144)→(0.497, 0.149, 0.053) | (0.501, 0.099, 0.034)→(0.501, 0.102, 0.033) | 0.180→0.183 | 1.00 / 1.000 | 0.532 | 2.538 |
| engage_peg | contact | 0.67 / force_exceeded | (0.497, 0.149, 0.053)→(0.495, 0.138, 0.042) | (0.501, 0.102, 0.033)→(0.501, 0.100, 0.034) | 0.183→0.180 | 1.00 / 2.000 | 8.244 | 8.644 |
| push_along_channel | push | 1.00 / time_limit | (0.495, 0.138, 0.042)→(0.502, 0.084, 0.049) | (0.501, 0.100, 0.034)→(0.501, 0.056, 0.029) | 0.180→0.137 | 1.00 / 2.667 | 267.721 | 761.238 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.372
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.273
- phase_score: 0.269
- phase_breakdown.behind_peg_score: 0.134
- phase_breakdown.insertion_progress_score: 0.327

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.337
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.378
- **Median Q (composite search score)**: -0.178
- **K-run variance**: 0.0136
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.425


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `080f370e6b427cbdf66706e7036a0e474f3967ccfc94f129756881a980a10a27`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `1f3f20d8b9dd2cb87de5d9f0723b4addbc88cdcf096cd2177633d23c0fa32881`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34545,"average_solve_count":110.0,"average_success_count":110.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.15076,"approach.approach_tolerance":0.00517,"descend.descend_speed":0.0594,"descend.descend_tolerance":0.00776,"engage_peg.contact_force_threshold":4.77025,"engage_peg.contact_forward_distance":0.05995,"engage_peg.contact_speed":0.0191,"push_along_channel.push_distance":0.17481,"push_along_channel.push_speed":0.05428,"push_along_channel.push_time_limit":8.71515},"optimized_scores":{"best_composite_score":-0.1781,"best_fitness_score":0.04857,"best_task_score":0.02782},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":36.0,"contact_point_centroid":[0.54209,0.11779,0.05996],"force_p95":638.63384,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":817.03807,"mean_force":429.16885,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49691,0.10518,0.04048]},{"body_a":"world","body_b":"link7","contact_count":894.0,"contact_point_centroid":[0.48971,0.16068,-8e-05],"force_p95":309.92356,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":412.0622,"mean_force":269.1661,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50391,0.09605,0.04866]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52506,0.10992,0.05997],"force_p95":313.2779,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":319.31094,"mean_force":227.4271,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50074,0.10576,0.03928]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.47195,0.11997,0.06],"force_p95":219.4249,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":267.70466,"mean_force":131.0474,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50494,0.08338,0.04933]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.47494,0.10096,0.0308],"force_p95":112.82305,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":112.95796,"mean_force":106.19968,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48652,0.09822,0.02976]},{"body_a":"attachment","body_b":"peg","contact_count":64.0,"contact_point_centroid":[0.50152,0.08444,0.06013],"force_p95":2.46493,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.02066,"mean_force":1.47909,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50499,0.0853,0.04944]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50318,0.06566,0.00943],"force_p95":1.28119,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.01217,"mean_force":0.62681,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50298,0.09673,0.04771]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54079,0.11456,0.05999],"force_p95":18.88876,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":18.88876,"mean_force":18.88876,"phase_index":2.0,"phase_name":"engage_peg","phase_type":"contact","tcp_position_centroid":[0.49611,0.11299,0.03635]},{"body_a":"peg","body_b":"channel_base_body","contact_count":688.0,"contact_point_centroid":[0.50309,0.06747,0.00935],"force_p95":0.55488,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55915,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49897,0.16014,0.21973]},{"body_a":"peg","body_b":"channel_base_body","contact_count":422.0,"contact_point_centroid":[0.50303,0.06749,0.00938],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55083,"mean_force":0.54664,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49796,0.11868,0.09124]},{"body_a":"peg","body_b":"channel_base_body","contact_count":50.0,"contact_point_centroid":[0.50238,0.06664,0.00938],"force_p95":0.55051,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55068,"mean_force":0.54664,"phase_index":2.0,"phase_name":"engage_peg","phase_type":"contact","tcp_position_centroid":[0.49707,0.11496,0.03784]}],"total_contact_groups":11},"final_pose_error":0.1461,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50282,0.06301,0.03734],"final_tcp_position":[0.50493,0.08337,0.04934],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":817.03807,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":704.0,"n_steps_budget":750.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54794,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":688.0,"raw_peak_contact_force":2.06903,"subtask_id":"behind_peg","tcp_end":[0.49968,0.12098,0.14327],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12192,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":422.0,"n_steps_budget":1000.0,"object_pos_end":[0.50307,0.06743,0.0338],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14758,"object_z_max":0.0338,"peak_contact_force":0.54552,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":422.0,"raw_peak_contact_force":0.55083,"subtask_id":"behind_peg","tcp_end":[0.49867,0.11688,0.0401],"tcp_start":[0.49968,0.12098,0.14327],"tcp_to_object_dist_end":0.05005,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":1000.0,"object_pos_end":[0.50303,0.0675,0.0338],"object_pos_start":[0.50307,0.06743,0.0338],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":18.88876,"phase_name":"engage_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":51.0,"raw_peak_contact_force":18.88876,"tcp_end":[0.49609,0.11293,0.03631],"tcp_start":[0.49867,0.11688,0.0401],"tcp_to_object_dist_end":0.04603,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50282,0.06301,0.03734],"object_pos_start":[0.50303,0.0675,0.0338],"object_to_goal_dist_end":0.14306,"object_to_goal_dist_start":0.14766,"object_z_max":0.03738,"peak_contact_force":267.70466,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2015.0,"raw_peak_contact_force":817.03807,"subtask_id":"insertion_progress","tcp_end":[0.50493,0.08337,0.04934],"tcp_start":[0.49609,0.11293,0.03631],"tcp_to_object_dist_end":0.02373,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `625c03a21403c0f6267b643060335ee3d751a26340ace08db5429afcee4c5ccf`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95181,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.13522,"approach.approach_tolerance":0.00501,"descend.descend_speed":0.03342,"descend.descend_tolerance":0.0024,"engage_peg.contact_force_threshold":4.88119,"engage_peg.contact_forward_distance":0.05163,"engage_peg.contact_speed":0.01107,"push_along_channel.push_distance":0.13578,"push_along_channel.push_speed":0.07618,"push_along_channel.push_time_limit":8.03914},"optimized_scores":{"best_composite_score":-0.22274,"best_fitness_score":0.33726,"best_task_score":0.37761},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.55446,0.1197,0.05915],"force_p95":724.09959,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":737.43463,"mean_force":461.11985,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50212,0.13276,0.02926]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.5254,0.11956,0.05987],"force_p95":659.34052,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":698.7369,"mean_force":356.99824,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.5091,0.12559,0.04243]},{"body_a":"world","body_b":"link7","contact_count":505.0,"contact_point_centroid":[0.48549,0.16555,-4e-05],"force_p95":228.43674,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":529.63608,"mean_force":146.42463,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49945,0.1011,0.04834]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":463.0,"contact_point_centroid":[0.46916,0.11991,0.05968],"force_p95":258.09866,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":503.93036,"mean_force":229.19289,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50173,0.0824,0.05038]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":20.0,"contact_point_centroid":[0.47473,0.11968,0.02768],"force_p95":248.82208,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":423.81657,"mean_force":132.15094,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48322,0.12076,0.01967]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50267,0.11994,0.04977],"force_p95":130.87654,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.93718,"mean_force":106.79818,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50055,0.1316,0.0496]},{"body_a":"peg","body_b":"channel_base_body","contact_count":965.0,"contact_point_centroid":[0.50083,0.04512,0.00811],"force_p95":0.72856,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":128.86117,"mean_force":1.08945,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49988,0.09579,0.04807]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.52508,0.08064,0.0318],"force_p95":7.15524,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.33722,"mean_force":2.04393,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50425,0.10807,0.04459]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":5.0,"contact_point_centroid":[0.47498,0.02218,0.0242],"force_p95":5.80633,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.1453,"mean_force":1.73213,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49896,0.11948,0.04847]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50496,0.10013,0.00972],"force_p95":1.86875,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.59016,"mean_force":1.07327,"phase_index":2.0,"phase_name":"engage_peg","phase_type":"contact","tcp_position_centroid":[0.49831,0.1417,0.05804]},{"body_a":"attachment","body_b":"peg","contact_count":515.0,"contact_point_centroid":[0.50184,0.12529,0.05787],"force_p95":1.62425,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.17436,"mean_force":1.19012,"phase_index":2.0,"phase_name":"engage_peg","phase_type":"contact","tcp_position_centroid":[0.49833,0.13713,0.05374]},{"body_a":"peg","body_b":"channel_base_body","contact_count":681.0,"contact_point_centroid":[0.50357,0.11167,0.00938],"force_p95":0.61302,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55573,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50232,0.18059,0.21809]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50368,0.11162,0.00941],"force_p95":0.59497,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64684,"mean_force":0.54351,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50217,0.16146,0.10751]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.4997,0.19947,0.29925]}],"total_contact_groups":14},"final_pose_error":0.08734,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50302,0.04503,0.02415],"final_tcp_position":[0.50249,0.08476,0.04948],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":737.43463,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":703.0,"n_steps_budget":780.0,"object_pos_end":[0.50372,0.11177,0.03381],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.52467,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":697.0,"raw_peak_contact_force":2.06328,"subtask_id":"behind_peg","tcp_end":[0.50625,0.16278,0.14317],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1207,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.11171,0.03396],"object_pos_start":[0.50372,0.11177,0.03381],"object_to_goal_dist_end":0.19184,"object_to_goal_dist_start":0.1919,"object_z_max":0.03397,"peak_contact_force":0.50484,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.64684,"subtask_id":"behind_peg","tcp_end":[0.50112,0.16109,0.07937],"tcp_start":[0.50625,0.16278,0.14317],"tcp_to_object_dist_end":0.06714,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50425,0.10464,0.03597],"object_pos_start":[0.50372,0.11171,0.03396],"object_to_goal_dist_end":0.18473,"object_to_goal_dist_start":0.19184,"object_z_max":0.03597,"peak_contact_force":1.39106,"phase_name":"engage_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1515.0,"raw_peak_contact_force":2.59016,"tcp_end":[0.49849,0.13329,0.0503],"tcp_start":[0.50112,0.16109,0.07937],"tcp_to_object_dist_end":0.03255,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.04503,0.02415],"object_pos_start":[0.50425,0.10464,0.03597],"object_to_goal_dist_end":0.12607,"object_to_goal_dist_start":0.18473,"object_z_max":0.04123,"peak_contact_force":247.81941,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2002.0,"raw_peak_contact_force":737.43463,"subtask_id":"insertion_progress","tcp_end":[0.50249,0.08476,0.04948],"tcp_start":[0.49849,0.13329,0.0503],"tcp_to_object_dist_end":0.04711,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `abe38b4b57ac37a91047e57d04e408cb1fd05583a47670bcb186dc9505a3f021`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67826,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.09211,"approach.approach_tolerance":0.00558,"descend.descend_speed":0.06099,"descend.descend_tolerance":0.00308,"engage_peg.contact_force_threshold":2.60965,"engage_peg.contact_forward_distance":0.0522,"engage_peg.contact_speed":0.02763,"push_along_channel.push_distance":0.21074,"push_along_channel.push_speed":0.07783,"push_along_channel.push_time_limit":9.7051},"optimized_scores":{"best_composite_score":0.04407,"best_fitness_score":0.27074,"best_task_score":0.27297},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.55494,0.11994,0.05979],"force_p95":692.57587,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":729.24263,"mean_force":439.61086,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50429,0.15544,0.02483]},{"body_a":"attachment","body_b":"world","contact_count":20.0,"contact_point_centroid":[0.50289,0.16303,-0.00102],"force_p95":500.44057,"geom_a":"pusher_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":502.29585,"mean_force":302.60243,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49881,0.1557,0.00642]},{"body_a":"world","body_b":"link7","contact_count":883.0,"contact_point_centroid":[0.48315,0.18954,-0.0001],"force_p95":310.29741,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":383.89027,"mean_force":265.54187,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49826,0.1248,0.04724]},{"body_a":"attachment","body_b":"peg","contact_count":109.0,"contact_point_centroid":[0.5036,0.09251,0.04483],"force_p95":3.61363,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.5924,"mean_force":2.37013,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49792,0.09218,0.04887]},{"body_a":"peg","body_b":"channel_base_body","contact_count":975.0,"contact_point_centroid":[0.5044,0.07207,0.00836],"force_p95":1.86113,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":55.37316,"mean_force":0.89286,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49842,0.1266,0.04594]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":69.0,"contact_point_centroid":[0.52502,0.04445,0.02619],"force_p95":8.0756,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.67404,"mean_force":2.45275,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49895,0.11543,0.04826]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.49434,0.15625,0.04687],"force_p95":6.26657,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.41498,"mean_force":4.33826,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49069,0.16794,0.0412]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49599,0.1192,0.00944],"force_p95":0.6078,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.28128,"mean_force":0.57136,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.48593,0.1684,0.09015]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49504,0.15478,0.04819],"force_p95":4.45306,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.45306,"mean_force":4.45306,"phase_index":2.0,"phase_name":"engage_peg","phase_type":"contact","tcp_position_centroid":[0.48982,0.16662,0.03803]},{"body_a":"peg","body_b":"channel_base_body","contact_count":17.0,"contact_point_centroid":[0.49474,0.11975,0.00939],"force_p95":1.34833,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.41928,"mean_force":0.73514,"phase_index":2.0,"phase_name":"engage_peg","phase_type":"contact","tcp_position_centroid":[0.4903,0.16743,0.03884]},{"body_a":"peg","body_b":"channel_base_body","contact_count":628.0,"contact_point_centroid":[0.49622,0.11905,0.0094],"force_p95":0.6084,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55502,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49098,0.18421,0.21919]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47495,0.09191,0.06],"force_p95":1.2161,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.25165,"mean_force":0.93495,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50703,0.15443,0.01893]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49943,0.19931,0.2982]}],"total_contact_groups":13},"final_pose_error":0.1299,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49734,0.0595,0.02407],"final_tcp_position":[0.49813,0.08494,0.04891],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":729.24263,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":653.0,"n_steps_budget":1000.0,"object_pos_end":[0.49605,0.1191,0.03381],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19924,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.52613,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":652.0,"raw_peak_contact_force":2.24822,"subtask_id":"behind_peg","tcp_end":[0.48392,0.16986,0.14494],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12277,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49607,0.12812,0.03218],"object_pos_start":[0.49605,0.1191,0.03381],"object_to_goal_dist_end":0.2083,"object_to_goal_dist_start":0.19924,"object_z_max":0.03417,"peak_contact_force":0.54426,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1008.0,"raw_peak_contact_force":6.41498,"subtask_id":"behind_peg","tcp_end":[0.4908,0.16796,0.03963],"tcp_start":[0.48392,0.16986,0.14494],"tcp_to_object_dist_end":0.04087,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":17.0,"n_steps_budget":990.0,"object_pos_end":[0.49606,0.12853,0.03219],"object_pos_start":[0.49607,0.12812,0.03218],"object_to_goal_dist_end":0.20872,"object_to_goal_dist_start":0.2083,"object_z_max":0.03231,"peak_contact_force":4.45306,"phase_name":"engage_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":18.0,"raw_peak_contact_force":4.45306,"tcp_end":[0.48977,0.16651,0.03793],"tcp_start":[0.4908,0.16796,0.03963],"tcp_to_object_dist_end":0.03892,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49734,0.0595,0.02407],"object_pos_start":[0.49606,0.12853,0.03219],"object_to_goal_dist_end":0.14043,"object_to_goal_dist_start":0.20872,"object_z_max":0.04118,"peak_contact_force":287.6398,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2073.0,"raw_peak_contact_force":729.24263,"subtask_id":"insertion_progress","tcp_end":[0.49813,0.08494,0.04891],"tcp_start":[0.48977,0.16651,0.03793],"tcp_to_object_dist_end":0.03557,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```