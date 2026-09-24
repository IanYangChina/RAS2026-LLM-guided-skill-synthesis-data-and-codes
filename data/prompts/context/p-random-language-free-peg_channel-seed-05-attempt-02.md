## Search State

- **Seed**: 5
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | -0.0477 | 0.49 | ✅ accepted |
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | -0.1612 | 0.00 | ✅ accepted |
| 0 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.2993 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.49 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.048) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: pre_push_approach
  anchor: object
  offset:
  - 0.0
  - 0.08
  - 0.0
  weight: 0.3
- id: push_channel
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_behind_high
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_push_approach
- id: descend_to_lateral
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
    - 0.08
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_push_approach
- id: push_along_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    force_limit:
      type: scalar
      range:
      - 30.0
      - 50.0
      default: 40.0
      binds_to:
      - path: guards.force_safe.threshold
        mode: replace
    lateral_nudge:
      type: scalar
      range:
      - 0.0
      - 0.02
      default: 0.005
      binds_to:
      - path: retry.offset.x
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.12
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_max_time:
      type: scalar
      range:
      - 1.0
      - 5.0
      default: 3.0
      binds_to:
      - path: duration.max_time
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
  - id: force_safe
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.0
  subtask_id: push_channel
- id: retract_upward
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind_high** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.08, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_lateral** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.08, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_along_channel** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_limit: status=consumed; consumers=guards.force_safe.threshold (replace)
    - lateral_nudge: status=consumed; consumers=retry.offset.x (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_max_time: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_safe, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.0, 0.0]
- **retract_upward** (`retract`)
  - target: source=yaml, anchor=task_goal, entity=peg, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.048
- **task_score** (E): 0.488
- **fitness_score**: 0.412  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind_high | 1.00 | 1.00 | 0.1549 |
| descend_to_lateral | 1.00 | 1.00 | 0.1122 |
| push_along_channel | 1.00 | 1.00 | 0.0812 |
| retract_upward | 0.00 | 1.00 | 0.1314 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.176, 0.149) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.547 | 2.488 |
| descend_to_lateral | descend | 1.00 / step_budget | (0.508, 0.176, 0.149)→(0.501, 0.173, 0.037) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.552 | 0.588 |
| push_along_channel | push | 1.00 / time_limit | (0.501, 0.173, 0.037)→(0.498, 0.092, 0.031) | (0.504, 0.095, 0.034)→(0.507, 0.064, 0.036) | 0.175→0.144 | 1.00 / 2.333 | 1.684 | 6.375 |
| retract_upward | retract | 0.00 / step_budget | (0.498, 0.092, 0.031)→(0.496, -0.020, 0.098) | (0.507, 0.064, 0.036)→(0.506, 0.000, 0.024) | 0.144→0.082 | 1.00 / 1.000 | 0.569 | 7.502 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.560
- alignment_error: None
- force_efficiency: 0.864
- terminal_score: 0.560
- phase_score: 0.425
- phase_breakdown.pre_push_approach_score: 0.896
- phase_breakdown.push_channel_score: 0.223

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.479
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.588
- **Median Q (composite search score)**: -0.015
- **K-run variance**: 0.0052
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.391


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95928,"average_solve_count":221.0,"average_success_count":221.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_high.approach_speed":0.05056,"descend_to_lateral.descend_speed":0.03551,"push_along_channel.force_limit":46.60298,"push_along_channel.lateral_nudge":0.00154,"push_along_channel.push_distance":0.19956,"push_along_channel.push_max_time":4.23403,"push_along_channel.push_speed":0.01208,"retract_upward.retract_speed":0.05714},"optimized_scores":{"best_composite_score":-0.14732,"best_fitness_score":0.31268,"best_task_score":0.31519},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":279.0,"contact_point_centroid":[0.50116,0.06878,0.04201],"force_p95":4.94712,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.03987,"mean_force":1.89664,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49675,0.07991,0.04159]},{"body_a":"peg","body_b":"channel_base_body","contact_count":914.0,"contact_point_centroid":[0.50618,0.02056,0.00888],"force_p95":3.35,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.60466,"mean_force":1.0439,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.4965,0.03901,0.06532]},{"body_a":"attachment","body_b":"peg","contact_count":353.0,"contact_point_centroid":[0.50371,0.10705,0.04226],"force_p95":4.6524,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.05128,"mean_force":2.51491,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49993,0.11881,0.03205]},{"body_a":"peg","body_b":"channel_base_body","contact_count":907.0,"contact_point_centroid":[0.50599,0.09399,0.00957],"force_p95":4.25118,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.64518,"mean_force":1.42589,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49985,0.14479,0.03248]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":168.0,"contact_point_centroid":[0.52503,0.05374,0.02777],"force_p95":3.65791,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.75641,"mean_force":1.28507,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49658,0.07885,0.04198]},{"body_a":"peg","body_b":"channel_base_body","contact_count":491.0,"contact_point_centroid":[0.50555,0.1047,0.00937],"force_p95":0.57756,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.5694,"phase_index":0.0,"phase_name":"approach_behind_high","phase_type":"approach","tcp_position_centroid":[0.50906,0.19179,0.22043]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":176.0,"contact_point_centroid":[0.52502,0.09002,0.0216],"force_p95":1.65194,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.15401,"mean_force":0.82557,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49993,0.11886,0.03206]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_behind_high","phase_type":"approach","tcp_position_centroid":[0.49992,0.19932,0.29678]},{"body_a":"peg","body_b":"channel_base_body","contact_count":555.0,"contact_point_centroid":[0.5059,0.10454,0.00939],"force_p95":0.57569,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57647,"mean_force":0.54631,"phase_index":1.0,"phase_name":"descend_to_lateral","phase_type":"descend","tcp_position_centroid":[0.51016,0.18365,0.09208]}],"total_contact_groups":9},"final_pose_error":0.07896,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50634,0.00772,0.02412],"final_tcp_position":[0.49655,-0.01411,0.09663],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":10.03987,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":518.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.10468,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18488,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54961,"phase_name":"approach_behind_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":523.0,"raw_peak_contact_force":3.33087,"subtask_id":"pre_push_approach","tcp_end":[0.51931,0.18489,0.14842],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":555.0,"n_steps_budget":1000.0,"object_pos_end":[0.50585,0.1047,0.03384],"object_pos_start":[0.50599,0.10468,0.03384],"object_to_goal_dist_end":0.18489,"object_to_goal_dist_start":0.18488,"object_z_max":0.03384,"peak_contact_force":0.54306,"phase_name":"descend_to_lateral","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":555.0,"raw_peak_contact_force":0.57647,"subtask_id":"pre_push_approach","tcp_end":[0.50322,0.18332,0.03774],"tcp_start":[0.51931,0.18489,0.14842],"tcp_to_object_dist_end":0.07877,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50701,0.07423,0.03548],"object_pos_start":[0.50585,0.1047,0.03384],"object_to_goal_dist_end":0.15446,"object_to_goal_dist_start":0.18489,"object_z_max":0.0356,"peak_contact_force":4.3289,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1436.0,"raw_peak_contact_force":6.05128,"subtask_id":"push_channel","tcp_end":[0.50006,0.10357,0.03189],"tcp_start":[0.50322,0.18332,0.03774],"tcp_to_object_dist_end":0.03036,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50634,0.00772,0.02412],"object_pos_start":[0.50701,0.07423,0.03548],"object_to_goal_dist_end":0.08937,"object_to_goal_dist_start":0.15446,"object_z_max":0.04077,"peak_contact_force":0.55659,"phase_name":"retract_upward","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1361.0,"raw_peak_contact_force":10.03987,"tcp_end":[0.49655,-0.01411,0.09663],"tcp_start":[0.50006,0.10357,0.03189],"tcp_to_object_dist_end":0.07635,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.78926,"average_solve_count":242.0,"average_success_count":242.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_high.approach_speed":0.05296,"descend_to_lateral.descend_speed":0.02721,"push_along_channel.force_limit":46.63353,"push_along_channel.lateral_nudge":0.0148,"push_along_channel.push_distance":0.18361,"push_along_channel.push_max_time":3.51369,"push_along_channel.push_speed":0.04962,"retract_upward.retract_speed":0.05064},"optimized_scores":{"best_composite_score":0.019,"best_fitness_score":0.479,"best_task_score":0.55999},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":371.0,"contact_point_centroid":[0.50118,0.0682,0.04129],"force_p95":5.60965,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.77794,"mean_force":2.42794,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49609,0.07966,0.03118]},{"body_a":"peg","body_b":"channel_base_body","contact_count":888.0,"contact_point_centroid":[0.50397,0.0564,0.00958],"force_p95":4.77953,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.92567,"mean_force":1.44102,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49584,0.10698,0.03157]},{"body_a":"attachment","body_b":"peg","contact_count":233.0,"contact_point_centroid":[0.4993,0.03498,0.04027],"force_p95":3.95713,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.93018,"mean_force":1.49508,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49357,0.04553,0.04021]},{"body_a":"peg","body_b":"channel_base_body","contact_count":930.0,"contact_point_centroid":[0.50616,-0.01044,0.00885],"force_p95":2.44296,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.79824,"mean_force":0.84753,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49424,0.00779,0.06854]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":189.0,"contact_point_centroid":[0.52502,0.02011,0.02535],"force_p95":3.34394,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.71338,"mean_force":1.18257,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49339,0.04197,0.04258]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":170.0,"contact_point_centroid":[0.52503,0.04812,0.02096],"force_p95":2.45739,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.52376,"mean_force":1.09022,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49616,0.07553,0.03115]},{"body_a":"peg","body_b":"channel_base_body","contact_count":510.0,"contact_point_centroid":[0.50308,0.06742,0.00934],"force_p95":0.55789,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56352,"phase_index":0.0,"phase_name":"approach_behind_high","phase_type":"approach","tcp_position_centroid":[0.49909,0.175,0.22212]},{"body_a":"peg","body_b":"channel_base_body","contact_count":678.0,"contact_point_centroid":[0.503,0.06749,0.00938],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55092,"mean_force":0.54665,"phase_index":1.0,"phase_name":"descend_to_lateral","phase_type":"descend","tcp_position_centroid":[0.49809,0.14843,0.09076]}],"total_contact_groups":8},"final_pose_error":0.05554,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50622,-0.02214,0.02415],"final_tcp_position":[0.49552,-0.03824,0.10367],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":6.77794,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":526.0,"n_steps_budget":1000.0,"object_pos_end":[0.50301,0.06745,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14761,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54651,"phase_name":"approach_behind_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":510.0,"raw_peak_contact_force":2.06903,"subtask_id":"pre_push_approach","tcp_end":[0.49986,0.15105,0.14864],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14208,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":678.0,"n_steps_budget":1000.0,"object_pos_end":[0.50306,0.0675,0.0338],"object_pos_start":[0.50301,0.06745,0.0338],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14761,"object_z_max":0.0338,"peak_contact_force":0.55064,"phase_name":"descend_to_lateral","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":678.0,"raw_peak_contact_force":0.55092,"subtask_id":"pre_push_approach","tcp_end":[0.49894,0.14658,0.03647],"tcp_start":[0.49986,0.15105,0.14864],"tcp_to_object_dist_end":0.07923,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50702,0.03442,0.03599],"object_pos_start":[0.50306,0.0675,0.0338],"object_to_goal_dist_end":0.11471,"object_to_goal_dist_start":0.14766,"object_z_max":0.03608,"peak_contact_force":0.3807,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1429.0,"raw_peak_contact_force":6.77794,"subtask_id":"push_channel","tcp_end":[0.49636,0.06273,0.03105],"tcp_start":[0.49894,0.14658,0.03647],"tcp_to_object_dist_end":0.03065,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50622,-0.02214,0.02415],"object_pos_start":[0.50702,0.03442,0.03599],"object_to_goal_dist_end":0.06031,"object_to_goal_dist_start":0.11471,"object_z_max":0.04078,"peak_contact_force":0.58201,"phase_name":"retract_upward","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1352.0,"raw_peak_contact_force":4.93018,"tcp_end":[0.49552,-0.03824,0.10367],"tcp_start":[0.49636,0.06273,0.03105],"tcp_to_object_dist_end":0.08183,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.6566,"average_solve_count":265.0,"average_success_count":265.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_high.approach_speed":0.05071,"descend_to_lateral.descend_speed":0.02103,"push_along_channel.force_limit":38.24839,"push_along_channel.lateral_nudge":0.01121,"push_along_channel.push_distance":0.19709,"push_along_channel.push_max_time":2.28358,"push_along_channel.push_speed":0.02169,"retract_upward.retract_speed":0.05752},"optimized_scores":{"best_composite_score":-0.01487,"best_fitness_score":0.44513,"best_task_score":0.58842},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":289.0,"contact_point_centroid":[0.49978,0.07596,0.04218],"force_p95":5.81075,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.53595,"mean_force":2.42161,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49424,0.08663,0.04098]},{"body_a":"peg","body_b":"channel_base_body","contact_count":905.0,"contact_point_centroid":[0.50615,0.02776,0.00883],"force_p95":4.00211,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.03992,"mean_force":1.19806,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49463,0.04511,0.06424]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":265.0,"contact_point_centroid":[0.52508,0.06222,0.02526],"force_p95":4.03309,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.64137,"mean_force":1.55408,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.4941,0.0858,0.04125]},{"body_a":"attachment","body_b":"peg","contact_count":354.0,"contact_point_centroid":[0.50164,0.1149,0.0413],"force_p95":5.1831,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.29568,"mean_force":2.45682,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49701,0.12646,0.0314]},{"body_a":"peg","body_b":"channel_base_body","contact_count":906.0,"contact_point_centroid":[0.50418,0.10154,0.00957],"force_p95":4.53303,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.23407,"mean_force":1.40547,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49684,0.15202,0.03176]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":143.0,"contact_point_centroid":[0.52503,0.09289,0.0205],"force_p95":2.163,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.75751,"mean_force":0.98734,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49708,0.12073,0.03137]},{"body_a":"peg","body_b":"channel_base_body","contact_count":478.0,"contact_point_centroid":[0.50364,0.11169,0.00936],"force_p95":0.61914,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56146,"phase_index":0.0,"phase_name":"approach_behind_high","phase_type":"approach","tcp_position_centroid":[0.50233,0.19516,0.22156]},{"body_a":"peg","body_b":"channel_base_body","contact_count":647.0,"contact_point_centroid":[0.50362,0.11174,0.00938],"force_p95":0.60172,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6362,"mean_force":0.54607,"phase_index":1.0,"phase_name":"descend_to_lateral","phase_type":"descend","tcp_position_centroid":[0.50185,0.19036,0.09146]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_behind_high","phase_type":"approach","tcp_position_centroid":[0.49979,0.19957,0.29905]}],"total_contact_groups":9},"final_pose_error":0.08457,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50456,0.01549,0.02415],"final_tcp_position":[0.49548,-0.00864,0.09484],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":7.53595,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":500.0,"n_steps_budget":1000.0,"object_pos_end":[0.5037,0.11174,0.03382],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.5455,"phase_name":"approach_behind_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":494.0,"raw_peak_contact_force":2.06328,"subtask_id":"pre_push_approach","tcp_end":[0.5062,0.1914,0.14914],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14018,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":647.0,"n_steps_budget":1000.0,"object_pos_end":[0.50374,0.11178,0.03381],"object_pos_start":[0.5037,0.11174,0.03382],"object_to_goal_dist_end":0.19192,"object_to_goal_dist_start":0.19187,"object_z_max":0.03391,"peak_contact_force":0.56316,"phase_name":"descend_to_lateral","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":647.0,"raw_peak_contact_force":0.6362,"subtask_id":"pre_push_approach","tcp_end":[0.50005,0.19029,0.03688],"tcp_start":[0.5062,0.1914,0.14914],"tcp_to_object_dist_end":0.07866,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50698,0.08248,0.03583],"object_pos_start":[0.50374,0.11178,0.03381],"object_to_goal_dist_end":0.16268,"object_to_goal_dist_start":0.19192,"object_z_max":0.03593,"peak_contact_force":0.34378,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1403.0,"raw_peak_contact_force":6.29568,"subtask_id":"push_channel","tcp_end":[0.49721,0.11106,0.0313],"tcp_start":[0.50005,0.19029,0.03688],"tcp_to_object_dist_end":0.03054,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50456,0.01549,0.02415],"object_pos_start":[0.50698,0.08248,0.03583],"object_to_goal_dist_end":0.0969,"object_to_goal_dist_start":0.16268,"object_z_max":0.04077,"peak_contact_force":0.56826,"phase_name":"retract_upward","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1459.0,"raw_peak_contact_force":7.53595,"tcp_end":[0.49548,-0.00864,0.09484],"tcp_start":[0.49721,0.11106,0.0313],"tcp_to_object_dist_end":0.07524,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```