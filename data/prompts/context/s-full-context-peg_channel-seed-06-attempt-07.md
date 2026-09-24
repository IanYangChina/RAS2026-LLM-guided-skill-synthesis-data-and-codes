## Search State

- **Seed**: 6
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → align → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 17 | -0.6617 | 0.04 | ❌ rejected |
| 6 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 10 | 0.0600 | 0.36 | ❌ rejected |
| 5 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 13 | -0.1303 | 0.39 | ❌ rejected |
| 4 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 13 | -0.3173 | 0.15 | ❌ rejected |
| 3 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 9 | 0.1374 | 0.49 | ✅ accepted |

**Proposal policy**: task_score is 0.04 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.662) — your mutation base

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

- **Composite score**: -0.662
- **task_score** (E): 0.037
- **fitness_score**: 0.078  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.940

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.1355 |
| descend | 0.00 | 1.00 | 0.0474 |
| align | 0.67 | 1.00 | 0.0496 |
| seat_entrance | 1.00 | 1.00 | 0.0300 |
| push | 0.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.496, 0.161, 0.172) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.541 | 2.127 |
| descend | descend | 0.00 / step_budget | (0.496, 0.161, 0.172)→(0.494, 0.156, 0.125) | (0.501, 0.099, 0.034)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.539 | 0.613 |
| align | align | 0.67 / step_budget | (0.494, 0.156, 0.125)→(0.493, 0.152, 0.075) | (0.501, 0.099, 0.034)→(0.501, 0.100, 0.034) | 0.180→0.180 | 1.00 / 1.333 | 76.476 | 81.428 |
| seat_entrance | contact | 1.00 / force_exceeded | (0.493, 0.152, 0.075)→(0.494, 0.127, 0.058) | (0.501, 0.100, 0.034)→(0.501, 0.098, 0.035) | 0.180→0.178 | 1.00 / 2.000 | 31.641 | 31.641 |
| push | push | 0.00 / guard_failure | (0.493, 0.122, 0.055)→(0.493, 0.122, 0.055) | (0.501, 0.098, 0.035)→(0.501, 0.092, 0.036) | 0.178→0.173 | 1.00 / 3.000 | 34.848 | 56.064 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.100
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.080
- phase_score: 0.144
- phase_breakdown.behind_peg_score: 0.332
- phase_breakdown.insertion_progress_score: 0.063

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.118
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.080
- **Median Q (composite search score)**: -0.658
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at upper bound**: push.push_speed
- **Final σ (mean)**: 0.332


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.55801,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align.align_speed":0.02292,"align.align_tolerance":0.00249,"approach.approach_speed":0.06858,"approach.approach_tolerance":0.00312,"descend.descend_speed":0.03002,"descend.descend_tolerance":0.00226,"descend.descend_z_offset":0.00433,"push.guard_threshold":32.14896,"push.push_distance":0.18842,"push.push_max_time":2.88231,"push.push_speed":0.04,"push.retry_offset_x":0.00425,"push.retry_offset_y":0.00066,"push.retry_offset_z":-0.00364,"seat_entrance.seat_force_threshold":5.21609,"seat_entrance.seat_offset_y":-0.01876,"seat_entrance.seat_speed":0.01646},"optimized_scores":{"best_composite_score":-0.65787,"best_fitness_score":0.08213,"best_task_score":0.03067},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.475,0.11993,0.03204],"force_p95":40.10669,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":41.1502,"mean_force":28.79516,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49472,0.08004,0.05496]},{"body_a":"peg","body_b":"channel_base_body","contact_count":50.0,"contact_point_centroid":[0.5023,0.04845,0.00972],"force_p95":12.05445,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.86533,"mean_force":7.61288,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49539,0.08259,0.05631]},{"body_a":"attachment","body_b":"peg","contact_count":42.0,"contact_point_centroid":[0.50207,0.08215,0.04621],"force_p95":11.82792,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.56121,"mean_force":8.63233,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49527,0.08222,0.05608]},{"body_a":"peg","body_b":"channel_base_body","contact_count":418.0,"contact_point_centroid":[0.50295,0.06735,0.00938],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.31994,"mean_force":0.57217,"phase_index":3.0,"phase_name":"seat_entrance","phase_type":"contact","tcp_position_centroid":[0.49542,0.10382,0.06849]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50283,0.08533,0.04812],"force_p95":8.16432,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.89655,"mean_force":3.79955,"phase_index":3.0,"phase_name":"seat_entrance","phase_type":"contact","tcp_position_centroid":[0.49626,0.08537,0.05811]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50307,0.06748,0.00936],"force_p95":0.55225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55539,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49866,0.1682,0.23542]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50307,0.06744,0.00938],"force_p95":0.55056,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55071,"mean_force":0.54665,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49686,0.13569,0.15021]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50305,0.06744,0.00938],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55058,"mean_force":0.54665,"phase_index":2.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.49313,0.1271,0.09706]}],"total_contact_groups":8},"final_pose_error":0.20228,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50273,0.06255,0.03618],"final_tcp_position":[0.49465,0.07991,0.05487],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":41.1502,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54571,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":984.0,"raw_peak_contact_force":2.06903,"subtask_id":"behind_peg","tcp_end":[0.49917,0.1409,0.18213],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16558,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50304,0.06742,0.0338],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.54781,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55071,"subtask_id":"behind_peg","tcp_end":[0.49716,0.1316,0.1253],"tcp_start":[0.49917,0.1409,0.18213],"tcp_to_object_dist_end":0.11192,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50301,0.06743,0.0338],"object_pos_start":[0.50304,0.06742,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14758,"object_z_max":0.0338,"peak_contact_force":0.54737,"phase_name":"align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55058,"subtask_id":"behind_peg","tcp_end":[0.49672,0.12411,0.08278],"tcp_start":[0.49716,0.1316,0.1253],"tcp_to_object_dist_end":0.07518,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":418.0,"n_steps_budget":1000.0,"object_pos_end":[0.50307,0.06733,0.03383],"object_pos_start":[0.50301,0.06743,0.0338],"object_to_goal_dist_end":0.14749,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":9.31994,"phase_name":"seat_entrance","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":421.0,"raw_peak_contact_force":9.31994,"tcp_end":[0.49628,0.08521,0.05802],"tcp_start":[0.49672,0.12411,0.08278],"tcp_to_object_dist_end":0.03083,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":1000.0,"object_pos_end":[0.50273,0.06272,0.03616],"object_pos_start":[0.50307,0.06733,0.03383],"object_to_goal_dist_end":0.14279,"object_to_goal_dist_start":0.14749,"object_z_max":0.03618,"peak_contact_force":29.17575,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":96.0,"raw_peak_contact_force":41.1502,"subtask_id":"insertion_progress","tcp_end":[0.49465,0.07991,0.05487],"tcp_start":[0.49468,0.07995,0.0549],"tcp_to_object_dist_end":0.02667,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.36181,"average_solve_count":199.0,"average_success_count":199.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align.align_speed":0.01754,"align.align_tolerance":0.00893,"approach.approach_speed":0.06607,"approach.approach_tolerance":0.00251,"descend.descend_speed":0.02445,"descend.descend_tolerance":0.00151,"descend.descend_z_offset":0.00374,"push.guard_threshold":36.56284,"push.push_distance":0.10455,"push.push_max_time":6.62917,"push.push_speed":0.02721,"push.retry_offset_x":-0.00885,"push.retry_offset_y":0.00191,"push.retry_offset_z":0.00077,"seat_entrance.seat_force_threshold":4.12595,"seat_entrance.seat_offset_y":-0.01473,"seat_entrance.seat_speed":0.02679},"optimized_scores":{"best_composite_score":-0.7054,"best_fitness_score":0.0346,"best_task_score":0.00078},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":364.0,"contact_point_centroid":[0.49123,0.22353,-0.0001],"force_p95":228.34551,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":243.08289,"mean_force":206.70985,"phase_index":2.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.49924,0.16398,0.05623]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.492,0.22316,-7e-05],"force_p95":75.54994,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":75.54994,"mean_force":75.54994,"phase_index":3.0,"phase_name":"seat_entrance","phase_type":"contact","tcp_position_centroid":[0.49889,0.16494,0.05784]},{"body_a":"world","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.492,0.22316,-6e-05],"force_p95":71.73234,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":71.76019,"mean_force":71.4328,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.4989,0.16495,0.05786]},{"body_a":"peg","body_b":"channel_base_body","contact_count":978.0,"contact_point_centroid":[0.50363,0.11164,0.00939],"force_p95":0.60742,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55161,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50116,0.18509,0.23714]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50367,0.11161,0.00942],"force_p95":0.59481,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63735,"mean_force":0.54356,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50099,0.16995,0.15773]},{"body_a":"peg","body_b":"channel_base_body","contact_count":840.0,"contact_point_centroid":[0.50366,0.11162,0.00941],"force_p95":0.59287,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63105,"mean_force":0.54418,"phase_index":2.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.49676,0.16477,0.07796]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51948,0.12,0.00938],"force_p95":0.59406,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59406,"mean_force":0.59406,"phase_index":3.0,"phase_name":"seat_entrance","phase_type":"contact","tcp_position_centroid":[0.49889,0.16494,0.05784]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.5164,0.10703,0.00938],"force_p95":0.55466,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55606,"mean_force":0.53957,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.4989,0.16495,0.05786]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49966,0.19951,0.29951]}],"total_contact_groups":9},"final_pose_error":0.15973,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50369,0.11164,0.03379],"final_tcp_position":[0.49891,0.16496,0.05787],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":243.08289,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.11174,0.03394],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.51891,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":994.0,"raw_peak_contact_force":2.06328,"subtask_id":"behind_peg","tcp_end":[0.50398,0.17246,0.18397],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16186,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.11169,0.03382],"object_pos_start":[0.50371,0.11174,0.03394],"object_to_goal_dist_end":0.19182,"object_to_goal_dist_start":0.19188,"object_z_max":0.03407,"peak_contact_force":0.56232,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.63735,"subtask_id":"behind_peg","tcp_end":[0.50062,0.16835,0.13691],"tcp_start":[0.50398,0.17246,0.18397],"tcp_to_object_dist_end":0.11767,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":840.0,"n_steps_budget":1000.0,"object_pos_end":[0.50374,0.11169,0.03379],"object_pos_start":[0.50375,0.11169,0.03382],"object_to_goal_dist_end":0.19183,"object_to_goal_dist_start":0.19182,"object_z_max":0.03399,"peak_contact_force":228.25064,"phase_name":"align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1204.0,"raw_peak_contact_force":243.08289,"subtask_id":"behind_peg","tcp_end":[0.49889,0.16494,0.05784],"tcp_start":[0.50062,0.16835,0.13691],"tcp_to_object_dist_end":0.05863,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.11168,0.03379],"object_pos_start":[0.50374,0.11169,0.03379],"object_to_goal_dist_end":0.19182,"object_to_goal_dist_start":0.19183,"object_z_max":0.03379,"peak_contact_force":75.54994,"phase_name":"seat_entrance","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":75.54994,"tcp_end":[0.4989,0.16494,0.05785],"tcp_start":[0.49889,0.16494,0.05784],"tcp_to_object_dist_end":0.05864,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.11166,0.03379],"object_pos_start":[0.50377,0.11168,0.03379],"object_to_goal_dist_end":0.1918,"object_to_goal_dist_start":0.19182,"object_z_max":0.03379,"peak_contact_force":71.57454,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":8.0,"raw_peak_contact_force":71.76019,"subtask_id":"insertion_progress","tcp_end":[0.49891,0.16496,0.05787],"tcp_start":[0.49891,0.16496,0.05786],"tcp_to_object_dist_end":0.05869,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.36255,"average_solve_count":251.0,"average_success_count":251.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align.align_speed":0.01106,"align.align_tolerance":0.00223,"approach.approach_speed":0.02903,"approach.approach_tolerance":0.00921,"descend.descend_speed":0.01982,"descend.descend_tolerance":0.00117,"descend.descend_z_offset":-0.00094,"push.guard_threshold":32.75512,"push.push_distance":0.1269,"push.push_max_time":4.18203,"push.push_speed":0.02004,"push.retry_offset_x":-0.00593,"push.retry_offset_y":-0.00045,"push.retry_offset_z":-0.00097,"seat_entrance.seat_force_threshold":8.30479,"seat_entrance.seat_offset_y":-0.01629,"seat_entrance.seat_speed":0.02087},"optimized_scores":{"best_composite_score":-0.62171,"best_fitness_score":0.11829,"best_task_score":0.07971},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":17.0,"contact_point_centroid":[0.475,0.1199,0.04603],"force_p95":40.43795,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":55.28026,"mean_force":27.89447,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.4847,0.11995,0.05306]},{"body_a":"peg","body_b":"channel_base_body","contact_count":143.0,"contact_point_centroid":[0.49416,0.09526,0.00994],"force_p95":10.28953,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.16622,"mean_force":6.46781,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48515,0.12507,0.05495]},{"body_a":"attachment","body_b":"peg","contact_count":140.0,"contact_point_centroid":[0.49272,0.12487,0.04562],"force_p95":9.94708,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.90639,"mean_force":6.21686,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48513,0.12495,0.05489]},{"body_a":"peg","body_b":"channel_base_body","contact_count":351.0,"contact_point_centroid":[0.4965,0.11667,0.00948],"force_p95":5.39203,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.05223,"mean_force":0.8881,"phase_index":3.0,"phase_name":"seat_entrance","phase_type":"contact","tcp_position_centroid":[0.48463,0.14901,0.07009]},{"body_a":"attachment","body_b":"peg","contact_count":23.0,"contact_point_centroid":[0.49498,0.13409,0.05189],"force_p95":7.68813,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.7329,"mean_force":5.65394,"phase_index":3.0,"phase_name":"seat_entrance","phase_type":"contact","tcp_position_centroid":[0.48627,0.13416,0.06008]},{"body_a":"peg","body_b":"channel_base_body","contact_count":517.0,"contact_point_centroid":[0.49622,0.11906,0.00945],"force_p95":0.60805,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55305,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49126,0.18468,0.22155]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49944,0.19932,0.29826]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49605,0.11941,0.00943],"force_p95":0.59636,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65229,"mean_force":0.54162,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.48281,0.16938,0.12795]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49602,0.1192,0.00946],"force_p95":0.60147,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.652,"mean_force":0.53919,"phase_index":2.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.48122,0.1672,0.09115]}],"total_contact_groups":9},"final_pose_error":0.13295,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4956,0.10305,0.03842],"final_tcp_position":[0.48468,0.11995,0.05295],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":55.28026,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":1000.0,"object_pos_end":[0.496,0.11924,0.0339],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19937,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.55981,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":541.0,"raw_peak_contact_force":2.24822,"subtask_id":"behind_peg","tcp_end":[0.48436,0.17061,0.1487],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12631,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49608,0.11937,0.03385],"object_pos_start":[0.496,0.11924,0.0339],"object_to_goal_dist_end":0.1995,"object_to_goal_dist_start":0.19937,"object_z_max":0.03414,"peak_contact_force":0.50743,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.65229,"subtask_id":"behind_peg","tcp_end":[0.48417,0.16911,0.11139],"tcp_start":[0.48436,0.17061,0.1487],"tcp_to_object_dist_end":0.09288,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49605,0.11948,0.03389],"object_pos_start":[0.49608,0.11937,0.03385],"object_to_goal_dist_end":0.19961,"object_to_goal_dist_start":0.1995,"object_z_max":0.03414,"peak_contact_force":0.63042,"phase_name":"align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.652,"subtask_id":"behind_peg","tcp_end":[0.48471,0.16729,0.08495],"tcp_start":[0.48417,0.16911,0.11139],"tcp_to_object_dist_end":0.07086,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":351.0,"n_steps_budget":1000.0,"object_pos_end":[0.49627,0.11541,0.03664],"object_pos_start":[0.49605,0.11948,0.03389],"object_to_goal_dist_end":0.19547,"object_to_goal_dist_start":0.19961,"object_z_max":0.03663,"peak_contact_force":10.05223,"phase_name":"seat_entrance","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":374.0,"raw_peak_contact_force":10.05223,"tcp_end":[0.48659,0.13204,0.05871],"tcp_start":[0.48471,0.16729,0.08495],"tcp_to_object_dist_end":0.02928,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":143.0,"n_steps_budget":1000.0,"object_pos_end":[0.49561,0.10303,0.03843],"object_pos_start":[0.49627,0.11541,0.03664],"object_to_goal_dist_end":0.18309,"object_to_goal_dist_start":0.19547,"object_z_max":0.03843,"peak_contact_force":3.79323,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":300.0,"raw_peak_contact_force":55.28026,"subtask_id":"insertion_progress","tcp_end":[0.48468,0.11995,0.05295],"tcp_start":[0.4847,0.11993,0.05298],"tcp_to_object_dist_end":0.02483,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```