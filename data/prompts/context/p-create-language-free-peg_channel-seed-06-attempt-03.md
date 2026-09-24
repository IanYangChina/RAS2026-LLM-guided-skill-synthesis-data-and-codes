## Search State

- **Seed**: 6
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.1566 | 0.32 | ❌ rejected |
| 2 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.5883 | 0.66 | ❌ rejected |
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 2 | 0.6156 | 0.82 | ✅ accepted |
| 0 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 2 | 0.2471 | 0.31 | ✅ accepted |

**Proposal policy**: task_score is 0.32 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.822, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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

## Current Skill (Q=0.157) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_contact
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.0
  weight: 0.3
- id: goal_progress
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
    - 0.08
    - 0.12
    tolerance: 0.01
    orientation:
      mode: keep_current
  subtask_id: reach_contact
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.04
    - 0.0
    tolerance: 0.008
    orientation:
      mode: keep_current
  subtask_id: reach_contact
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.1
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
  guards:
  - id: force_safety
    when: during_phase
    predicate: force_below
    threshold: 50.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: goal_progress
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
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.08, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.0], tolerance=0.008
  - orientation: mode=keep_current
  - parameter_bindings: none
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_safety, when=during_phase, predicate=force_below, on_failure=retry, threshold=50.0
  - retries: max_attempts=2, strategy=reduce_speed
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.157
- **task_score** (E): 0.316
- **fitness_score**: 0.363  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.133
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.340

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1346 |
| descend_1 | 1.00 | 0.67 | 0.1394 |
| contact_1 | 0.67 | 1.00 | 0.0065 |
| push_1 | 0.33 | 1.00 | 0.0341 |
| retract_1 | 1.00 | 1.00 | 0.0804 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.180, 0.169) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.518 | 2.127 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.180, 0.169)→(0.504, 0.117, 0.045) | (0.501, 0.099, 0.034)→(0.503, 0.087, 0.033) | 0.180→0.167 | 0.67 / 2.000 | 132.902 | 191.313 |
| contact_1 | contact | 0.67 / force_exceeded | (0.504, 0.117, 0.045)→(0.503, 0.111, 0.044) | (0.503, 0.087, 0.033)→(0.504, 0.080, 0.028) | 0.167→0.161 | 1.00 / 2.333 | 73.688 | 76.220 |
| push_1 | push | 0.33 / guard_failure | (0.503, 0.111, 0.044)→(0.502, 0.077, 0.042) | (0.504, 0.080, 0.028)→(0.504, 0.050, 0.029) | 0.161→0.133 | 1.00 / 2.667 | 96.449 | 99.709 |
| retract_1 | retract | 1.00 / step_budget | (0.502, 0.077, 0.042)→(0.499, 0.076, 0.122) | (0.504, 0.050, 0.029)→(0.501, 0.048, 0.031) | 0.133→0.132 | 1.00 / 1.000 | 0.595 | 84.440 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.887
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.887
- phase_score: 0.749
- phase_breakdown.reach_contact_score: 0.517
- phase_breakdown.goal_progress_score: 0.848

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.804
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.887
- **Median Q (composite search score)**: 0.008
- **K-run variance**: 0.0473
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 4.3
- **Final σ (mean)**: 0.384


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37255,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force_threshold":17.80399,"push_1.force_safety_threshold":69.96124,"push_1.insertion_depth":0.10991,"push_1.push_speed":0.04776,"push_1.retry_x_offset":0.00265},"optimized_scores":{"best_composite_score":0.46408,"best_fitness_score":0.80408,"best_task_score":0.88705},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":496.0,"contact_point_centroid":[0.50464,0.0674,0.00919],"force_p95":139.70765,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":169.83391,"mean_force":17.25641,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49921,0.1161,0.1009]},{"body_a":"attachment","body_b":"peg","contact_count":79.0,"contact_point_centroid":[0.50962,0.08168,0.05496],"force_p95":165.76961,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":169.39516,"mean_force":105.1007,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50204,0.0902,0.05428]},{"body_a":"attachment","body_b":"peg","contact_count":451.0,"contact_point_centroid":[0.49706,-0.00569,0.0435],"force_p95":8.97914,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.65208,"mean_force":1.81852,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49481,0.00629,0.03272]},{"body_a":"peg","body_b":"channel_base_body","contact_count":470.0,"contact_point_centroid":[0.50586,-0.02983,0.00962],"force_p95":5.82207,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.52741,"mean_force":1.71082,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49511,0.01637,0.03308]},{"body_a":"peg","body_b":"channel_base_body","contact_count":393.0,"contact_point_centroid":[0.50265,0.01545,0.0079],"force_p95":0.84504,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.19336,"mean_force":0.67589,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49886,0.07201,0.03748]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.525,0.03921,0.02416],"force_p95":7.76271,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.92556,"mean_force":3.27245,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49858,0.06635,0.03716]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":160.0,"contact_point_centroid":[0.52502,-0.05932,0.02793],"force_p95":5.79497,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.31927,"mean_force":2.04528,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49474,0.00135,0.03265]},{"body_a":"peg","body_b":"channel_base_body","contact_count":241.0,"contact_point_centroid":[0.50417,-0.07262,0.00842],"force_p95":0.74471,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.29221,"mean_force":0.60876,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49185,-0.03712,0.07199]},{"body_a":"peg","body_b":"channel_base_body","contact_count":412.0,"contact_point_centroid":[0.50304,0.0674,0.00933],"force_p95":0.57772,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56752,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49926,0.17525,0.23185]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.49698,-0.0493,0.04391],"force_p95":1.92864,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.02161,"mean_force":1.09192,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49469,-0.03725,0.03257]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52503,-0.09896,0.02794],"force_p95":1.81684,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.98361,"mean_force":0.66888,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49353,-0.03747,0.0351]},{"body_a":"peg","body_b":"channel_base_body","contact_count":59.0,"contact_point_centroid":[0.48781,-0.10009,0.02654],"force_p95":0.91194,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.9325,"mean_force":0.27827,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49225,-0.03723,0.06193]}],"total_contact_groups":12},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49954,-0.07447,0.02415],"final_tcp_position":[0.49164,-0.03701,0.11286],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":169.83391,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":428.0,"n_steps_budget":930.0,"object_pos_end":[0.50302,0.06748,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54513,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":412.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_contact","tcp_end":[0.50001,0.15159,0.16827],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15864,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":498.0,"n_steps_budget":960.0,"object_pos_end":[0.50155,0.03671,0.03998],"object_pos_start":[0.50302,0.06748,0.0338],"object_to_goal_dist_end":0.11672,"object_to_goal_dist_start":0.14764,"object_z_max":0.04016,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":575.0,"raw_peak_contact_force":169.83391,"subtask_id":"reach_contact","tcp_end":[0.50249,0.08331,0.04186],"tcp_start":[0.50001,0.15159,0.16827],"tcp_to_object_dist_end":0.04665,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":413.0,"n_steps_budget":600.0,"object_pos_end":[0.50452,0.01628,0.02423],"object_pos_start":[0.50155,0.03671,0.03998],"object_to_goal_dist_end":0.09767,"object_to_goal_dist_start":0.11672,"object_z_max":0.03998,"peak_contact_force":0.59762,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":398.0,"raw_peak_contact_force":8.19336,"subtask_id":"reach_contact","tcp_end":[0.49858,0.06486,0.03717],"tcp_start":[0.50249,0.08331,0.04186],"tcp_to_object_dist_end":0.05062,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":605.0,"n_steps_budget":1000.0,"object_pos_end":[0.50623,-0.07391,0.02802],"object_pos_start":[0.50452,0.01628,0.02423],"object_to_goal_dist_end":0.01482,"object_to_goal_dist_start":0.09767,"object_z_max":0.02817,"peak_contact_force":1.87313,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1081.0,"raw_peak_contact_force":11.65208,"subtask_id":"goal_progress","tcp_end":[0.4947,-0.03719,0.03259],"tcp_start":[0.49858,0.06486,0.03717],"tcp_to_object_dist_end":0.03875,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":243.0,"n_steps_budget":660.0,"object_pos_end":[0.49954,-0.07447,0.02415],"object_pos_start":[0.50623,-0.07391,0.02802],"object_to_goal_dist_end":0.01679,"object_to_goal_dist_start":0.01482,"object_z_max":0.02808,"peak_contact_force":0.6759,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":321.0,"raw_peak_contact_force":2.29221,"tcp_end":[0.49164,-0.03701,0.11286],"tcp_start":[0.4947,-0.03719,0.03259],"tcp_to_object_dist_end":0.09662,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75862,"average_solve_count":87.0,"average_success_count":87.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force_threshold":23.51945,"push_1.force_safety_threshold":63.23937,"push_1.insertion_depth":0.12977,"push_1.push_speed":0.02869,"push_1.retry_x_offset":0.00566},"optimized_scores":{"best_composite_score":0.00784,"best_fitness_score":0.14784,"best_task_score":0.03457},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":123.0,"contact_point_centroid":[0.51478,0.1254,0.05386],"force_p95":196.43363,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":196.86172,"mean_force":143.74013,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5056,0.13293,0.05274]},{"body_a":"peg","body_b":"channel_base_body","contact_count":499.0,"contact_point_centroid":[0.50675,0.11367,0.0091],"force_p95":191.62456,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":194.78611,"mean_force":35.80064,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50333,0.15687,0.09898]},{"body_a":"peg","body_b":"channel_base_body","contact_count":245.0,"contact_point_centroid":[0.50507,0.10778,0.00924],"force_p95":18.19152,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":144.93116,"mean_force":3.47402,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5092,0.12894,0.08845]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.518,0.11995,0.0075],"force_p95":141.04038,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":141.04652,"mean_force":137.90848,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51148,0.12961,0.04833]},{"body_a":"attachment","body_b":"peg","contact_count":36.0,"contact_point_centroid":[0.51851,0.12008,0.05491],"force_p95":91.00564,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":136.93863,"mean_force":19.78947,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51111,0.12937,0.05371]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.51992,0.12123,0.05114],"force_p95":132.99947,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":133.12912,"mean_force":130.10172,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51148,0.12961,0.04833]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51807,0.11995,0.00748],"force_p95":115.77109,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":115.77109,"mean_force":115.77109,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51134,0.12966,0.04829]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51989,0.1214,0.05108],"force_p95":115.17711,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":115.17711,"mean_force":115.17711,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51134,0.12966,0.04829]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52533,0.10845,0.05542],"force_p95":25.38033,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.86125,"mean_force":15.70557,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51148,0.12961,0.04833]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52522,0.10836,0.05561],"force_p95":19.69367,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.61709,"mean_force":4.92342,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51169,0.1296,0.04866]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":26.0,"contact_point_centroid":[0.52527,0.10889,0.05557],"force_p95":19.45912,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.96812,"mean_force":14.10272,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51001,0.13027,0.04895]},{"body_a":"peg","body_b":"channel_base_body","contact_count":379.0,"contact_point_centroid":[0.50355,0.11171,0.00936],"force_p95":0.62508,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56511,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50247,0.19523,0.23127]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49988,0.19958,0.29877]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52536,0.10853,0.05538],"force_p95":0.0,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51134,0.12966,0.04829]}],"total_contact_groups":14},"final_pose_error":0.01973,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50568,0.10625,0.03381],"final_tcp_position":[0.50867,0.12883,0.12894],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":196.86172,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":401.0,"n_steps_budget":900.0,"object_pos_end":[0.50371,0.11182,0.03382],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19196,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.53999,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":395.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_contact","tcp_end":[0.50626,0.19154,0.16903],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15697,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":499.0,"n_steps_budget":960.0,"object_pos_end":[0.5071,0.10735,0.03087],"object_pos_start":[0.50371,0.11182,0.03382],"object_to_goal_dist_end":0.18771,"object_to_goal_dist_start":0.19196,"object_z_max":0.03399,"peak_contact_force":196.86172,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":648.0,"raw_peak_contact_force":196.86172,"subtask_id":"reach_contact","tcp_end":[0.51134,0.12966,0.04829],"tcp_start":[0.50626,0.19154,0.16903],"tcp_to_object_dist_end":0.02862,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50708,0.10732,0.03087],"object_pos_start":[0.5071,0.10735,0.03087],"object_to_goal_dist_end":0.18768,"object_to_goal_dist_start":0.18771,"object_z_max":0.03087,"peak_contact_force":115.77109,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":115.77109,"subtask_id":"reach_contact","tcp_end":[0.51142,0.12963,0.04829],"tcp_start":[0.51134,0.12966,0.04829],"tcp_to_object_dist_end":0.02864,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50705,0.1073,0.03089],"object_pos_start":[0.50708,0.10732,0.03087],"object_to_goal_dist_end":0.18765,"object_to_goal_dist_start":0.18768,"object_z_max":0.03091,"peak_contact_force":141.04652,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":141.04652,"subtask_id":"goal_progress","tcp_end":[0.51161,0.1296,0.04844],"tcp_start":[0.51155,0.1296,0.04838],"tcp_to_object_dist_end":0.02874,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":245.0,"n_steps_budget":630.0,"object_pos_end":[0.50568,0.10625,0.03381],"object_pos_start":[0.50701,0.10727,0.03095],"object_to_goal_dist_end":0.18644,"object_to_goal_dist_start":0.18762,"object_z_max":0.03388,"peak_contact_force":0.51584,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":286.0,"raw_peak_contact_force":144.93116,"tcp_end":[0.50867,0.12883,0.12894],"tcp_start":[0.51161,0.1296,0.04844],"tcp_to_object_dist_end":0.09782,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75862,"average_solve_count":87.0,"average_success_count":87.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force_threshold":23.22474,"push_1.force_safety_threshold":58.28095,"push_1.insertion_depth":0.14364,"push_1.push_speed":0.01238,"push_1.retry_x_offset":-0.00198},"optimized_scores":{"best_composite_score":-0.00225,"best_fitness_score":0.13775,"best_task_score":0.02694},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":123.0,"contact_point_centroid":[0.50231,0.13251,0.05223],"force_p95":198.44992,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":207.24345,"mean_force":119.48787,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49441,0.1408,0.05149]},{"body_a":"peg","body_b":"channel_base_body","contact_count":515.0,"contact_point_centroid":[0.49785,0.11915,0.00901],"force_p95":157.67047,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":197.73743,"mean_force":28.69773,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48833,0.16395,0.0994]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50477,0.12849,0.04766],"force_p95":145.38488,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":146.42853,"mean_force":124.88567,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49896,0.13829,0.04525]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50462,0.11918,0.00602],"force_p95":138.69683,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":139.87482,"mean_force":116.81607,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49896,0.13829,0.04525]},{"body_a":"attachment","body_b":"peg","contact_count":39.0,"contact_point_centroid":[0.50503,0.12873,0.05242],"force_p95":78.05595,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":106.09594,"mean_force":22.49119,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49865,0.13848,0.05149]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50466,0.12849,0.0476],"force_p95":104.69658,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":104.69658,"mean_force":104.69658,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49885,0.13829,0.04522]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.48319,0.11917,0.00599],"force_p95":99.07312,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":99.07312,"mean_force":99.07312,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49885,0.13829,0.04522]},{"body_a":"peg","body_b":"channel_base_body","contact_count":240.0,"contact_point_centroid":[0.49764,0.11408,0.00915],"force_p95":31.75967,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":98.05855,"mean_force":4.10055,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49677,0.1378,0.08544]},{"body_a":"peg","body_b":"world","contact_count":12.0,"contact_point_centroid":[0.49905,0.12919,-0.0001],"force_p95":23.00205,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.75083,"mean_force":18.28183,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49839,0.13851,0.04559]},{"body_a":"peg","body_b":"world","contact_count":2.0,"contact_point_centroid":[0.49926,0.12912,-3e-05],"force_p95":11.96653,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.04626,"mean_force":11.24898,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49912,0.13838,0.04538]},{"body_a":"peg","body_b":"world","contact_count":3.0,"contact_point_centroid":[0.4992,0.12912,-9e-05],"force_p95":11.38704,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.48997,"mean_force":10.24315,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49896,0.13829,0.04525]},{"body_a":"peg","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.49919,0.12911,-0.00013],"force_p95":6.90698,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.90698,"mean_force":6.90698,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49885,0.13829,0.04522]},{"body_a":"peg","body_b":"channel_base_body","contact_count":366.0,"contact_point_centroid":[0.49639,0.11912,0.00944],"force_p95":0.62218,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55843,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49157,0.1985,0.2312]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49947,0.19956,0.2975]}],"total_contact_groups":14},"final_pose_error":0.01991,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4982,0.11285,0.03384],"final_tcp_position":[0.49618,0.13754,0.12566],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":207.24345,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":391.0,"n_steps_budget":900.0,"object_pos_end":[0.49602,0.11907,0.03413],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.1992,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.46818,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":390.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_contact","tcp_end":[0.48497,0.19798,0.16969],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15724,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":515.0,"n_steps_budget":960.0,"object_pos_end":[0.49936,0.11657,0.02788],"object_pos_start":[0.49602,0.11907,0.03413],"object_to_goal_dist_end":0.19694,"object_to_goal_dist_start":0.1992,"object_z_max":0.03415,"peak_contact_force":201.84545,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":650.0,"raw_peak_contact_force":207.24345,"subtask_id":"reach_contact","tcp_end":[0.49885,0.13829,0.04522],"tcp_start":[0.48497,0.19798,0.16969],"tcp_to_object_dist_end":0.0278,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49937,0.11656,0.02791],"object_pos_start":[0.49936,0.11657,0.02788],"object_to_goal_dist_end":0.19693,"object_to_goal_dist_start":0.19694,"object_z_max":0.02788,"peak_contact_force":104.69658,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":104.69658,"subtask_id":"reach_contact","tcp_end":[0.49891,0.13827,0.04522],"tcp_start":[0.49885,0.13829,0.04522],"tcp_to_object_dist_end":0.02777,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49935,0.11656,0.02795],"object_pos_start":[0.49937,0.11656,0.02791],"object_to_goal_dist_end":0.19693,"object_to_goal_dist_start":0.19693,"object_z_max":0.028,"peak_contact_force":146.42853,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":146.42853,"subtask_id":"goal_progress","tcp_end":[0.49908,0.13835,0.04535],"tcp_start":[0.49902,0.13831,0.04529],"tcp_to_object_dist_end":0.02789,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":240.0,"n_steps_budget":630.0,"object_pos_end":[0.4982,0.11285,0.03384],"object_pos_start":[0.49935,0.11659,0.02805],"object_to_goal_dist_end":0.19296,"object_to_goal_dist_start":0.19695,"object_z_max":0.03446,"peak_contact_force":0.59413,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":281.0,"raw_peak_contact_force":106.09594,"tcp_end":[0.49618,0.13754,0.12566],"tcp_start":[0.49908,0.13835,0.04535],"tcp_to_object_dist_end":0.09511,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```