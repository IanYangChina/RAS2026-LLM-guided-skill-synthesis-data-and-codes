## Search State

- **Seed**: 6
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 13 | -0.2290 | 0.44 | ❌ rejected |
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | -0.0302 | 0.22 | ❌ rejected |
| 10 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 11 | -0.0749 | 0.14 | ❌ rejected |
| 9 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 9 | 0.0239 | 0.10 | ❌ rejected |
| 8 | approach → descend → align → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 16 | -0.6792 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.44 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.229) — your mutation base

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

- **Composite score**: -0.229
- **task_score** (E): 0.438
- **fitness_score**: 0.481  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.710

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.0616 |
| descend | 1.00 | 1.00 | 0.1866 |
| seating | 0.67 | 1.00 | 0.0415 |
| push | 1.00 | 1.00 | 0.0676 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.498, 0.163, 0.253) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.565 | 2.127 |
| descend | descend | 1.00 / step_budget | (0.498, 0.163, 0.253)→(0.497, 0.150, 0.067) | (0.501, 0.099, 0.034)→(0.501, 0.100, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.513 | 0.618 |
| seating | contact | 0.67 / step_budget | (0.497, 0.150, 0.067)→(0.495, 0.114, 0.047) | (0.501, 0.100, 0.034)→(0.502, 0.086, 0.038) | 0.180→0.166 | 1.00 / 2.000 | 2.993 | 4.179 |
| push | push | 1.00 / time_limit | (0.495, 0.114, 0.047)→(0.494, 0.047, 0.038) | (0.502, 0.086, 0.038)→(0.506, 0.014, 0.040) | 0.166→0.094 | 1.00 / 3.000 | 13.186 | 16.491 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.513
- alignment_error: None
- force_efficiency: 0.667
- terminal_score: 0.513
- phase_score: 0.566
- phase_breakdown.behind_peg_score: 0.671
- phase_breakdown.insertion_progress_score: 0.521

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.545
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.513
- **Median Q (composite search score)**: -0.218
- **K-run variance**: 0.0033
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.352


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.83962,"average_solve_count":212.0,"average_success_count":212.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.13334,"approach.approach_tolerance":0.0128,"descend.descend_speed":0.02844,"descend.descend_tolerance":0.0056,"descend.descend_z_offset":0.01347,"push.push_distance":0.12501,"push.push_max_time":5.63766,"push.push_speed":0.03991,"push.retry_offset_x":0.00696,"push.retry_offset_y":0.00927,"seating.seating_distance":0.02671,"seating.seating_force_threshold":4.34068,"seating.seating_speed":0.01827},"optimized_scores":{"best_composite_score":-0.16496,"best_fitness_score":0.54504,"best_task_score":0.51334},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":997.0,"contact_point_centroid":[0.49949,0.04031,0.03809],"force_p95":14.16144,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.63182,"mean_force":8.22786,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49445,0.05067,0.04042]},{"body_a":"peg","body_b":"channel_base_body","contact_count":990.0,"contact_point_centroid":[0.50461,0.0141,0.00994],"force_p95":10.15212,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.42503,"mean_force":6.93495,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49446,0.0507,0.04044]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":514.0,"contact_point_centroid":[0.52511,0.01352,0.02306],"force_p95":8.39108,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.62459,"mean_force":6.02437,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49496,0.03502,0.03918]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50405,0.05848,0.00963],"force_p95":2.62222,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.37848,"mean_force":1.16921,"phase_index":2.0,"phase_name":"seating","phase_type":"contact","tcp_position_centroid":[0.49608,0.09925,0.05304]},{"body_a":"attachment","body_b":"peg","contact_count":396.0,"contact_point_centroid":[0.50022,0.07908,0.05186],"force_p95":2.53463,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.0393,"mean_force":1.74972,"phase_index":2.0,"phase_name":"seating","phase_type":"contact","tcp_position_centroid":[0.49634,0.09074,0.04938]},{"body_a":"peg","body_b":"channel_base_body","contact_count":153.0,"contact_point_centroid":[0.50316,0.06759,0.00923],"force_p95":0.98843,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.60293,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49979,0.16595,0.27183]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50302,0.06745,0.00938],"force_p95":0.55079,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56003,"mean_force":0.54664,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49867,0.12661,0.15438]}],"total_contact_groups":7},"final_pose_error":0.08642,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50728,-0.01467,0.04058],"final_tcp_position":[0.49573,0.01824,0.03805],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":16.63182,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":169.0,"n_steps_budget":600.0,"object_pos_end":[0.50307,0.06742,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.5484,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":153.0,"raw_peak_contact_force":2.06903,"subtask_id":"behind_peg","tcp_end":[0.50052,0.13535,0.24849],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.22519,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06748,0.0338],"object_pos_start":[0.50307,0.06742,0.0338],"object_to_goal_dist_end":0.14765,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.54355,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.56003,"tcp_end":[0.4989,0.11861,0.06536],"tcp_start":[0.50052,0.13535,0.24849],"tcp_to_object_dist_end":0.06023,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50396,0.05723,0.03713],"object_pos_start":[0.50308,0.06748,0.0338],"object_to_goal_dist_end":0.13732,"object_to_goal_dist_start":0.14765,"object_z_max":0.03712,"peak_contact_force":2.3279,"phase_name":"seating","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1396.0,"raw_peak_contact_force":3.37848,"tcp_end":[0.49664,0.08516,0.0471],"tcp_start":[0.4989,0.11861,0.06536],"tcp_to_object_dist_end":0.03055,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50728,-0.01467,0.04058],"object_pos_start":[0.50396,0.05723,0.03713],"object_to_goal_dist_end":0.06574,"object_to_goal_dist_start":0.13732,"object_z_max":0.04059,"peak_contact_force":12.46287,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2501.0,"raw_peak_contact_force":16.63182,"subtask_id":"insertion_progress","tcp_end":[0.49573,0.01824,0.03805],"tcp_start":[0.49664,0.08516,0.0471],"tcp_to_object_dist_end":0.03497,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.83099,"average_solve_count":213.0,"average_success_count":213.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.07769,"approach.approach_tolerance":0.01022,"descend.descend_speed":0.01591,"descend.descend_tolerance":0.00505,"descend.descend_z_offset":0.01106,"push.push_distance":0.10867,"push.push_max_time":4.82972,"push.push_speed":0.03986,"push.retry_offset_x":0.00419,"push.retry_offset_y":0.01971,"seating.seating_distance":0.02768,"seating.seating_force_threshold":4.27945,"seating.seating_speed":0.01605},"optimized_scores":{"best_composite_score":-0.21823,"best_fitness_score":0.49177,"best_task_score":0.51026},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":994.0,"contact_point_centroid":[0.50024,0.08541,0.03771],"force_p95":13.72163,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.05655,"mean_force":8.54208,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49536,0.0959,0.03984]},{"body_a":"peg","body_b":"channel_base_body","contact_count":987.0,"contact_point_centroid":[0.50529,0.05847,0.00995],"force_p95":9.92743,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.0317,"mean_force":6.9696,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49538,0.0959,0.03987]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":636.0,"contact_point_centroid":[0.52513,0.06186,0.02289],"force_p95":8.16211,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.50857,"mean_force":5.81023,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49572,0.08427,0.03879]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50453,0.10274,0.00965],"force_p95":2.33944,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.27566,"mean_force":1.09733,"phase_index":2.0,"phase_name":"seating","phase_type":"contact","tcp_position_centroid":[0.4971,0.14338,0.05194]},{"body_a":"attachment","body_b":"peg","contact_count":407.0,"contact_point_centroid":[0.50107,0.1241,0.05203],"force_p95":2.17938,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.72037,"mean_force":1.53334,"phase_index":2.0,"phase_name":"seating","phase_type":"contact","tcp_position_centroid":[0.49725,0.13581,0.04885]},{"body_a":"peg","body_b":"channel_base_body","contact_count":86.0,"contact_point_centroid":[0.50294,0.1118,0.00916],"force_p95":1.18746,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.63988,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50257,0.18502,0.27394]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50372,0.11167,0.00941],"force_p95":0.59525,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63779,"mean_force":0.54364,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50159,0.16735,0.1565]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49991,0.19897,0.29871]}],"total_contact_groups":8},"final_pose_error":0.07004,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50722,0.03014,0.0406],"final_tcp_position":[0.49675,0.0635,0.03727],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":15.05655,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":108.0,"n_steps_budget":600.0,"object_pos_end":[0.50379,0.11175,0.03378],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.57526,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":102.0,"raw_peak_contact_force":2.06328,"subtask_id":"behind_peg","tcp_end":[0.50511,0.17358,0.25494],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.22964,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50369,0.11175,0.03381],"object_pos_start":[0.50379,0.11175,0.03378],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19189,"object_z_max":0.034,"peak_contact_force":0.50585,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.63779,"tcp_end":[0.50009,0.16193,0.06358],"tcp_start":[0.50511,0.17358,0.25494],"tcp_to_object_dist_end":0.05846,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50443,0.10256,0.03684],"object_pos_start":[0.50369,0.11175,0.03381],"object_to_goal_dist_end":0.18264,"object_to_goal_dist_start":0.19189,"object_z_max":0.03684,"peak_contact_force":1.88965,"phase_name":"seating","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1407.0,"raw_peak_contact_force":3.27566,"tcp_end":[0.49748,0.13071,0.0469],"tcp_start":[0.50009,0.16193,0.06358],"tcp_to_object_dist_end":0.03069,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50722,0.03014,0.0406],"object_pos_start":[0.50443,0.10256,0.03684],"object_to_goal_dist_end":0.11037,"object_to_goal_dist_start":0.18264,"object_z_max":0.0406,"peak_contact_force":11.04846,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2617.0,"raw_peak_contact_force":15.05655,"subtask_id":"insertion_progress","tcp_end":[0.49675,0.0635,0.03727],"tcp_start":[0.49748,0.13071,0.0469],"tcp_to_object_dist_end":0.03513,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.935,"average_solve_count":200.0,"average_success_count":200.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.08336,"approach.approach_tolerance":0.01651,"descend.descend_speed":0.03768,"descend.descend_tolerance":0.00507,"descend.descend_z_offset":0.01057,"push.push_distance":0.14279,"push.push_max_time":4.51742,"push.push_speed":0.03985,"push.retry_offset_x":0.01975,"push.retry_offset_y":-0.00161,"seating.seating_distance":0.02817,"seating.seating_force_threshold":7.11488,"seating.seating_speed":0.02503},"optimized_scores":{"best_composite_score":-0.30372,"best_fitness_score":0.40628,"best_task_score":0.29101},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":1000.0,"contact_point_centroid":[0.49401,0.08156,0.03783],"force_p95":14.22267,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.7834,"mean_force":6.48423,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48793,0.09116,0.04063]},{"body_a":"peg","body_b":"channel_base_body","contact_count":994.0,"contact_point_centroid":[0.49997,0.05802,0.00996],"force_p95":10.22185,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.31745,"mean_force":6.30013,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48792,0.09127,0.04064]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":138.0,"contact_point_centroid":[0.52512,0.0461,0.02349],"force_p95":10.30282,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.48989,"mean_force":7.32655,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48899,0.06312,0.03908]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.4983,0.10523,0.00974],"force_p95":4.25819,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.88182,"mean_force":1.97824,"phase_index":2.0,"phase_name":"seating","phase_type":"contact","tcp_position_centroid":[0.489,0.14466,0.05603]},{"body_a":"attachment","body_b":"peg","contact_count":549.0,"contact_point_centroid":[0.49308,0.12484,0.0511],"force_p95":4.21773,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.54745,"mean_force":2.7782,"phase_index":2.0,"phase_name":"seating","phase_type":"contact","tcp_position_centroid":[0.48932,0.1362,0.05164]},{"body_a":"peg","body_b":"channel_base_body","contact_count":74.0,"contact_point_centroid":[0.49763,0.11897,0.00925],"force_p95":1.27539,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.64613,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49351,0.18758,0.27385]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49896,0.19831,0.29697]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49606,0.11912,0.00944],"force_p95":0.61016,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65544,"mean_force":0.54046,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.48933,0.17384,0.16175]}],"total_contact_groups":8},"final_pose_error":0.10367,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50476,0.02706,0.04023],"final_tcp_position":[0.48907,0.05903,0.03889],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":17.7834,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":99.0,"n_steps_budget":600.0,"object_pos_end":[0.49601,0.11912,0.0339],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19926,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.57162,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":98.0,"raw_peak_contact_force":2.24822,"subtask_id":"behind_peg","tcp_end":[0.4894,0.17902,0.25639],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.23051,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49601,0.11952,0.03395],"object_pos_start":[0.49601,0.11912,0.0339],"object_to_goal_dist_end":0.19965,"object_to_goal_dist_start":0.19926,"object_z_max":0.0342,"peak_contact_force":0.48877,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.65544,"tcp_end":[0.49126,0.16949,0.07261],"tcp_start":[0.4894,0.17902,0.25639],"tcp_to_object_dist_end":0.06335,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49866,0.0986,0.03881],"object_pos_start":[0.49601,0.11952,0.03395],"object_to_goal_dist_end":0.17861,"object_to_goal_dist_start":0.19965,"object_z_max":0.0388,"peak_contact_force":4.76207,"phase_name":"seating","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1549.0,"raw_peak_contact_force":5.88182,"tcp_end":[0.48993,0.12596,0.04658],"tcp_start":[0.49126,0.16949,0.07261],"tcp_to_object_dist_end":0.02976,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50476,0.02706,0.04023],"object_pos_start":[0.49866,0.0986,0.03881],"object_to_goal_dist_end":0.10717,"object_to_goal_dist_start":0.17861,"object_z_max":0.04081,"peak_contact_force":16.04653,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2132.0,"raw_peak_contact_force":17.7834,"subtask_id":"insertion_progress","tcp_end":[0.48907,0.05903,0.03889],"tcp_start":[0.48993,0.12596,0.04658],"tcp_to_object_dist_end":0.03564,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```