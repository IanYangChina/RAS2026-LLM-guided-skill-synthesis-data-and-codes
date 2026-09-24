## Search State

- **Seed**: 6
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 2 | 0.6156 | 0.82 | ✅ accepted |
| 0 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 2 | 0.2471 | 0.31 | ✅ accepted |

**Proposal policy**: task_score is 0.82 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.616) — your mutation base

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

- **Composite score**: 0.616
- **task_score** (E): 0.822
- **fitness_score**: 0.776  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.160

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1346 |
| descend_1 | 1.00 | 1.00 | 0.1346 |
| push_1 | 1.00 | 1.00 | 0.1469 |
| retract_1 | 1.00 | 1.00 | 0.0805 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.180, 0.169) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.518 | 2.127 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.180, 0.169)→(0.497, 0.142, 0.040) | (0.501, 0.099, 0.034)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.550 | 0.617 |
| push_1 | push | 1.00 / step_budget | (0.497, 0.142, 0.040)→(0.493, -0.005, 0.036) | (0.501, 0.099, 0.034)→(0.507, -0.033, 0.037) | 0.180→0.050 | 1.00 / 2.667 | 1324.853 | 29.505 |
| retract_1 | retract | 1.00 / step_budget | (0.493, -0.005, 0.036)→(0.490, -0.005, 0.116) | (0.507, -0.033, 0.037)→(0.503, -0.040, 0.031) | 0.050→0.044 | 1.00 / 1.000 | 0.516 | 121.290 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.931
- alignment_error: None
- force_efficiency: 0.512
- terminal_score: 0.931
- phase_score: 0.892
- phase_breakdown.reach_contact_score: 0.765
- phase_breakdown.goal_progress_score: 0.946

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.908
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.717
- **K-run variance**: 0.0275
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 11.0
- **Final σ (mean)**: 0.241


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37634,"average_solve_count":186.0,"average_success_count":186.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"push_1.insertion_depth":0.19999,"push_1.push_speed":0.02887},"optimized_scores":{"best_composite_score":0.74774,"best_fitness_score":0.90774,"best_task_score":0.93137},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":27.0,"contact_point_centroid":[0.49992,-0.06493,0.05095],"force_p95":24.32315,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.39772,"mean_force":11.19753,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49362,-0.05395,0.03849]},{"body_a":"peg","body_b":"channel_base_body","contact_count":30.0,"contact_point_centroid":[0.50635,-0.1003,0.06036],"force_p95":23.69857,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.75903,"mean_force":10.26696,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49357,-0.05391,0.03825]},{"body_a":"attachment","body_b":"peg","contact_count":768.0,"contact_point_centroid":[0.50052,0.00656,0.04133],"force_p95":11.21085,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.72283,"mean_force":3.88657,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49514,0.01766,0.03536]},{"body_a":"peg","body_b":"channel_base_body","contact_count":13.0,"contact_point_centroid":[0.5065,-0.10027,0.05981],"force_p95":22.64261,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.61388,"mean_force":14.03476,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49512,-0.05327,0.03528]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":657.0,"contact_point_centroid":[0.52515,-0.00995,0.02767],"force_p95":6.74846,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.298,"mean_force":2.09304,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49512,0.01695,0.03535]},{"body_a":"peg","body_b":"channel_base_body","contact_count":558.0,"contact_point_centroid":[0.50604,-0.01289,0.00984],"force_p95":9.13369,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.75053,"mean_force":4.52671,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49539,0.02999,0.03564]},{"body_a":"peg","body_b":"channel_base_body","contact_count":412.0,"contact_point_centroid":[0.50304,0.0674,0.00933],"force_p95":0.57772,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56752,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49926,0.17525,0.23185]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.52511,-0.08134,0.03233],"force_p95":1.78377,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.89448,"mean_force":0.52931,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49249,-0.05354,0.04737]},{"body_a":"peg","body_b":"channel_base_body","contact_count":210.0,"contact_point_centroid":[0.50579,-0.08182,0.00945],"force_p95":0.62609,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.99638,"mean_force":0.5467,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49199,-0.05372,0.0802]},{"body_a":"peg","body_b":"channel_base_body","contact_count":491.0,"contact_point_centroid":[0.50309,0.06755,0.00938],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55115,"mean_force":0.54664,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49841,0.131,0.10338]}],"total_contact_groups":10},"final_pose_error":0.01973,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50683,-0.08156,0.03379],"final_tcp_position":[0.49204,-0.0538,0.11572],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":24.39772,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":428.0,"n_steps_budget":930.0,"object_pos_end":[0.50302,0.06748,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54513,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":412.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_contact","tcp_end":[0.50001,0.15159,0.16827],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15864,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":491.0,"n_steps_budget":900.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50302,0.06748,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14764,"object_z_max":0.0338,"peak_contact_force":0.54531,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":491.0,"raw_peak_contact_force":0.55115,"subtask_id":"reach_contact","tcp_end":[0.49897,0.11022,0.03989],"tcp_start":[0.50001,0.15159,0.16827],"tcp_to_object_dist_end":0.04342,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50673,-0.08138,0.03608],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.00791,"object_to_goal_dist_start":0.14759,"object_z_max":0.03725,"peak_contact_force":23.72283,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1996.0,"raw_peak_contact_force":23.72283,"subtask_id":"goal_progress","tcp_end":[0.49507,-0.05408,0.03522],"tcp_start":[0.49897,0.11022,0.03989],"tcp_to_object_dist_end":0.02969,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":245.0,"n_steps_budget":630.0,"object_pos_end":[0.50683,-0.08156,0.03379],"object_pos_start":[0.50673,-0.08138,0.03608],"object_to_goal_dist_end":0.00936,"object_to_goal_dist_start":0.00791,"object_z_max":0.03742,"peak_contact_force":0.55667,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":304.0,"raw_peak_contact_force":24.39772,"tcp_end":[0.49204,-0.0538,0.11572],"tcp_start":[0.49507,-0.05408,0.03522],"tcp_to_object_dist_end":0.08776,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44025,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"push_1.insertion_depth":0.19331,"push_1.push_speed":0.04751},"optimized_scores":{"best_composite_score":0.71701,"best_fitness_score":0.87701,"best_task_score":0.99984},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":749.0,"contact_point_centroid":[0.50113,0.04537,0.04117],"force_p95":9.99915,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.8811,"mean_force":3.22238,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49637,0.05666,0.03587]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.50587,0.02871,0.00986],"force_p95":8.96683,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.5524,"mean_force":4.37961,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49661,0.07214,0.03613]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":661.0,"contact_point_centroid":[0.52508,0.03278,0.02514],"force_p95":4.03215,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.54593,"mean_force":1.32281,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49637,0.06019,0.03586]},{"body_a":"peg","body_b":"channel_base_body","contact_count":379.0,"contact_point_centroid":[0.50355,0.11171,0.00936],"force_p95":0.62508,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56511,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50247,0.19523,0.23127]},{"body_a":"peg","body_b":"channel_base_body","contact_count":235.0,"contact_point_centroid":[0.50635,-0.04892,0.00943],"force_p95":0.64183,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.99804,"mean_force":0.55531,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49346,-0.01887,0.07642]},{"body_a":"peg","body_b":"channel_base_body","contact_count":467.0,"contact_point_centroid":[0.5036,0.11162,0.00943],"force_p95":0.59848,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63572,"mean_force":0.54232,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50221,0.1729,0.10421]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52504,-0.04675,0.02329],"force_p95":0.48797,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57587,"mean_force":0.2708,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49554,-0.01906,0.03963]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49988,0.19958,0.29877]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.50175,-0.03062,0.05582],"force_p95":0.42824,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.46942,"mean_force":0.17178,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49562,-0.01906,0.03799]}],"total_contact_groups":9},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50651,-0.0482,0.03383],"final_tcp_position":[0.49332,-0.01878,0.11632],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":3908.96087,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":401.0,"n_steps_budget":900.0,"object_pos_end":[0.50371,0.11182,0.03382],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19196,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.53999,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":395.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_contact","tcp_end":[0.50626,0.19154,0.16903],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15697,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":467.0,"n_steps_budget":900.0,"object_pos_end":[0.50375,0.11176,0.03385],"object_pos_start":[0.50371,0.11182,0.03382],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19196,"object_z_max":0.03402,"peak_contact_force":0.58496,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":467.0,"raw_peak_contact_force":0.63572,"subtask_id":"reach_contact","tcp_end":[0.50015,0.1541,0.04043],"tcp_start":[0.50626,0.19154,0.16903],"tcp_to_object_dist_end":0.043,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50662,-0.04698,0.03608],"object_pos_start":[0.50375,0.11176,0.03385],"object_to_goal_dist_end":0.0339,"object_to_goal_dist_start":0.19189,"object_z_max":0.03677,"peak_contact_force":3908.96087,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1953.0,"raw_peak_contact_force":14.8811,"subtask_id":"goal_progress","tcp_end":[0.49633,-0.01885,0.03589],"tcp_start":[0.50015,0.1541,0.04043],"tcp_to_object_dist_end":0.02996,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":243.0,"n_steps_budget":630.0,"object_pos_end":[0.50651,-0.0482,0.03383],"object_pos_start":[0.50662,-0.04698,0.03608],"object_to_goal_dist_end":0.03304,"object_to_goal_dist_start":0.0339,"object_z_max":0.03613,"peak_contact_force":0.54975,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":249.0,"raw_peak_contact_force":0.99804,"tcp_end":[0.49332,-0.01878,0.11632],"tcp_start":[0.49633,-0.01885,0.03589],"tcp_to_object_dist_end":0.08857,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.75879,"average_solve_count":199.0,"average_success_count":199.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"push_1.insertion_depth":0.11337,"push_1.push_speed":0.01124},"optimized_scores":{"best_composite_score":0.38191,"best_fitness_score":0.54191,"best_task_score":0.53363},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":52.0,"contact_point_centroid":[0.47498,0.05726,0.04699],"force_p95":333.3232,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":338.4747,"mean_force":202.78052,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48681,0.05726,0.04511]},{"body_a":"attachment","body_b":"peg","contact_count":19.0,"contact_point_centroid":[0.49654,0.05203,0.03563],"force_p95":54.72914,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.68757,"mean_force":27.29161,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48682,0.05775,0.03688]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":62.0,"contact_point_centroid":[0.52568,0.03846,0.03086],"force_p95":46.92452,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.26419,"mean_force":8.31942,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48683,0.05731,0.04341]},{"body_a":"attachment","body_b":"peg","contact_count":877.0,"contact_point_centroid":[0.49597,0.08343,0.03678],"force_p95":48.17687,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.90993,"mean_force":32.54754,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48705,0.0905,0.03596]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":810.0,"contact_point_centroid":[0.52566,0.07129,0.02625],"force_p95":41.92341,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.75059,"mean_force":28.11293,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48697,0.0865,0.03597]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":307.0,"contact_point_centroid":[0.475,0.07395,0.03802],"force_p95":31.76383,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":36.69111,"mean_force":25.40024,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48685,0.07395,0.03613]},{"body_a":"peg","body_b":"channel_base_body","contact_count":946.0,"contact_point_centroid":[0.50713,0.06718,0.00976],"force_p95":29.78514,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.39948,"mean_force":16.40824,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48723,0.09554,0.03609]},{"body_a":"peg","body_b":"channel_base_body","contact_count":225.0,"contact_point_centroid":[0.50236,0.02281,0.00905],"force_p95":3.33828,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.3475,"mean_force":1.37445,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48524,0.05733,0.07627]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":5.0,"contact_point_centroid":[0.47498,-0.01303,0.02422],"force_p95":6.78582,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.84548,"mean_force":2.92608,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48394,0.05762,0.11482]},{"body_a":"peg","body_b":"channel_base_body","contact_count":366.0,"contact_point_centroid":[0.49639,0.11912,0.00944],"force_p95":0.62218,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55843,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49157,0.1985,0.2312]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49947,0.19956,0.2975]},{"body_a":"peg","body_b":"channel_base_body","contact_count":495.0,"contact_point_centroid":[0.49603,0.11909,0.00943],"force_p95":0.61368,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66491,"mean_force":0.54197,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48706,0.17946,0.10418]}],"total_contact_groups":12},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49619,0.00919,0.02431],"final_tcp_position":[0.48399,0.05764,0.11646],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":338.4747,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":391.0,"n_steps_budget":900.0,"object_pos_end":[0.49602,0.11907,0.03413],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.1992,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.46818,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":390.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_contact","tcp_end":[0.48497,0.19798,0.16969],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15724,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":495.0,"n_steps_budget":900.0,"object_pos_end":[0.49605,0.11922,0.03385],"object_pos_start":[0.49602,0.11907,0.03413],"object_to_goal_dist_end":0.19935,"object_to_goal_dist_start":0.1992,"object_z_max":0.03415,"peak_contact_force":0.51993,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":495.0,"raw_peak_contact_force":0.66491,"subtask_id":"reach_contact","tcp_end":[0.4914,0.16101,0.04014],"tcp_start":[0.48497,0.19798,0.16969],"tcp_to_object_dist_end":0.04252,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50857,0.02883,0.03921],"object_pos_start":[0.49605,0.11922,0.03385],"object_to_goal_dist_end":0.10917,"object_to_goal_dist_start":0.19935,"object_z_max":0.04043,"peak_contact_force":41.87415,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2940.0,"raw_peak_contact_force":49.90993,"subtask_id":"goal_progress","tcp_end":[0.48684,0.05802,0.03618],"tcp_start":[0.4914,0.16101,0.04014],"tcp_to_object_dist_end":0.03651,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":243.0,"n_steps_budget":630.0,"object_pos_end":[0.49619,0.00919,0.02431],"object_pos_start":[0.50857,0.02883,0.03921],"object_to_goal_dist_end":0.09064,"object_to_goal_dist_start":0.10917,"object_z_max":0.04029,"peak_contact_force":0.44013,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":363.0,"raw_peak_contact_force":338.4747,"tcp_end":[0.48399,0.05764,0.11646],"tcp_start":[0.48684,0.05802,0.03618],"tcp_to_object_dist_end":0.10482,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```