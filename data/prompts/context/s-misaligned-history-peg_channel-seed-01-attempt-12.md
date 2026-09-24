## Search State

- **Seed**: 1
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7  | 0.0454 | 0.35 | ✅ accepted |
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 6  | 0.1121 | 0.31 | ❌ rejected |
| 10 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3  | -0.0363 | 0.00 | ❌ rejected |
| 9 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5  | 0.0461 | 0.00 | ❌ rejected |
| 8 | approach → descend → contact → push | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5  | -0.2814 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`
- Frozen object start: [0.5009457299760205, 0.11603709570607482, 0.04]
- Frozen task target: [0.5009457299760205, -0.04396290429392519, 0.04]
- Goal object position: (0.5009457299760205, -0.04396290429392519, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5009457299760205, 0.11603709570607482, 0.04)
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
  frozen_object_start: [0.5009, 0.116, 0.04]
  frozen_task_target: [0.5009, -0.044, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5009457299760205, 0.11603709570607482, 0.04]}
  frozen_targets: {'channel_exit': [0.5009457299760205, -0.04396290429392519, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a

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
| `object` | offset from object initial position (0.5009457299760205, 0.11603709570607482, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5009457299760205, -0.04396290429392519, 0.04) | final destination targets |
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

## Current Skill (Q=-0.281) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_contact
  anchor: object
  offset:
  - -0.001
  - 0.03
  - 0.0
  weight: 0.3
- id: reach_goal
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
    offset:
    - 0.0
    - 0.05
    - 0.12
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.03
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_contact
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.0
  parameters:
    descend_tolerance:
      type: scalar
      range:
      - 0.003
      - 0.01
      default: 0.005
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
  subtask_id: reach_contact
- id: push_1
  type: push
  generator: linear_cartesian
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
      distance: 0.18
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.12
      - 0.22
      default: 0.18
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: guard_force_limit
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.12]
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.0]
  - parameter_bindings:
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - lateral_offset_x: status=consumed; consumers=target.offset.x (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.18, mode=replace_offset_projection, sign=positive}
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=guard_force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: -0.281
- **task_score** (E): 0.000
- **fitness_score**: 0.129  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1524 |
| descend_1 | 1.00 | 1.00 | 0.1096 |
| align_1 | 1.00 | 1.00 | 0.0338 |
| push_1 | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.144, 0.158) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.565 | 2.857 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.144, 0.158)→(0.497, 0.141, 0.049) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.033) | 0.160→0.160 | 1.00 / 1.333 | 30.815 | 47.159 |
| align_1 | align | 1.00 / step_budget | (0.497, 0.141, 0.049)→(0.491, 0.117, 0.038) | (0.497, 0.080, 0.033)→(0.496, 0.082, 0.033) | 0.160→0.162 | 1.00 / 2.000 | 137.597 | 155.555 |
| push_1 | push | 0.00 / guard_failure | (0.491, 0.117, 0.038)→(0.491, 0.117, 0.038) | (0.496, 0.082, 0.033)→(0.496, 0.082, 0.033) | 0.162→0.162 | 1.00 / 2.000 | 103.492 | 105.038 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.001
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.001
- phase_score: 0.230
- phase_breakdown.reach_contact_score: 0.703
- phase_breakdown.reach_goal_score: 0.027

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.138
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.001
- **Median Q (composite search score)**: -0.282
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.373


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a904e23429ae963dd2788b3e8d0575d9ce341e1daddfe013fbb1224c3e0c850e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `6bee39a4c127c6d39ee1365e3969a50bb09484f7e2580b1a3dc4d8c4ae20213b`; realized-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,0.11604,0.04]},{"name":"goal","value":[0.50095,-0.04396,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.11604,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50095,-0.04396,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38554,"average_solve_count":83.0,"average_success_count":83.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_tolerance":0.00908,"align_1.lateral_offset_x":-0.0044,"approach_1.approach_speed":0.0967,"descend_1.descend_tolerance":0.00999,"push_1.push_distance":0.16175,"push_1.push_speed":0.06725,"push_1.push_tolerance":0.01698},"optimized_scores":{"best_composite_score":-0.28179,"best_fitness_score":0.12821,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":339.0,"contact_point_centroid":[0.50564,0.14275,0.04351],"force_p95":176.56067,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":184.91513,"mean_force":141.12334,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50007,0.15152,0.04366]},{"body_a":"peg","body_b":"channel_base_body","contact_count":339.0,"contact_point_centroid":[0.50407,0.11812,0.00723],"force_p95":172.04482,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":181.64258,"mean_force":135.94877,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50007,0.15152,0.04366]},{"body_a":"peg","body_b":"channel_base_body","contact_count":369.0,"contact_point_centroid":[0.50205,0.11665,0.00919],"force_p95":130.24389,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":140.37199,"mean_force":19.69437,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49582,0.14208,0.0999]},{"body_a":"attachment","body_b":"peg","contact_count":71.0,"contact_point_centroid":[0.50688,0.13592,0.05316],"force_p95":136.17212,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":139.77915,"mean_force":99.5711,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49772,0.14228,0.05556]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.51321,0.11747,0.00711],"force_p95":118.94955,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":119.54615,"mean_force":110.13982,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4999,0.15453,0.03916]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50427,0.1456,0.03966],"force_p95":118.22932,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":118.83559,"mean_force":109.33532,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4999,0.15453,0.03916]},{"body_a":"peg","body_b":"world","contact_count":177.0,"contact_point_centroid":[0.5,0.12154,-2e-05],"force_p95":20.47245,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.11416,"mean_force":13.71625,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50007,0.15298,0.04184]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.50104,0.11607,0.00937],"force_p95":0.62136,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.56131,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49774,0.17168,0.22686]}],"total_contact_groups":8},"final_pose_error":0.162,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49962,0.123,0.03072],"final_tcp_position":[0.49987,0.15472,0.03917],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":184.91513,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":466.0,"n_steps_budget":1000.0,"object_pos_end":[0.50088,0.11611,0.03391],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19621,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.60705,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":450.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_contact","tcp_end":[0.49706,0.14449,0.1583],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12765,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":369.0,"n_steps_budget":750.0,"object_pos_end":[0.50176,0.11767,0.03105],"object_pos_start":[0.50088,0.11611,0.03391],"object_to_goal_dist_end":0.19788,"object_to_goal_dist_start":0.19621,"object_z_max":0.03397,"peak_contact_force":91.35591,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":440.0,"raw_peak_contact_force":140.37199,"subtask_id":"reach_contact","tcp_end":[0.49973,0.14509,0.04981],"tcp_start":[0.49706,0.14449,0.1583],"tcp_to_object_dist_end":0.03329,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":339.0,"n_steps_budget":600.0,"object_pos_end":[0.49968,0.12281,0.03066],"object_pos_start":[0.50176,0.11767,0.03105],"object_to_goal_dist_end":0.20302,"object_to_goal_dist_start":0.19788,"object_z_max":0.03163,"peak_contact_force":143.82734,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":855.0,"raw_peak_contact_force":184.91513,"subtask_id":"reach_contact","tcp_end":[0.4999,0.15448,0.03916],"tcp_start":[0.49973,0.14509,0.04981],"tcp_to_object_dist_end":0.03279,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49967,0.12284,0.03067],"object_pos_start":[0.49968,0.12281,0.03066],"object_to_goal_dist_end":0.20305,"object_to_goal_dist_start":0.20302,"object_z_max":0.03069,"peak_contact_force":119.54615,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":119.54615,"subtask_id":"reach_goal","tcp_end":[0.49987,0.15472,0.03917],"tcp_start":[0.49989,0.1546,0.03916],"tcp_to_object_dist_end":0.033,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8416ac3bebb4dbec2abbf751596843a33db171fd8d70765023f3b940d846bd0c`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.16822,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_tolerance":0.00608,"align_1.lateral_offset_x":-0.00979,"approach_1.approach_speed":0.05595,"descend_1.descend_tolerance":0.00934,"push_1.push_distance":0.12741,"push_1.push_speed":0.04683,"push_1.push_tolerance":0.00531},"optimized_scores":{"best_composite_score":-0.27183,"best_fitness_score":0.13817,"best_task_score":0.00086},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":255.0,"contact_point_centroid":[0.53219,0.10888,0.05998],"force_p95":134.86203,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":136.74179,"mean_force":83.88531,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48699,0.10725,0.03735]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.5322,0.10154,0.05996],"force_p95":96.86799,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":97.05405,"mean_force":95.29243,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48693,0.10024,0.03743]},{"body_a":"peg","body_b":"channel_base_body","contact_count":476.0,"contact_point_centroid":[0.49555,0.0638,0.00937],"force_p95":0.59639,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56339,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49767,0.17117,0.22552]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4995,0.19882,0.29743]},{"body_a":"peg","body_b":"channel_base_body","contact_count":478.0,"contact_point_centroid":[0.49522,0.06394,0.0094],"force_p95":0.55088,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55403,"mean_force":0.5452,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48833,0.1152,0.03892]},{"body_a":"peg","body_b":"channel_base_body","contact_count":359.0,"contact_point_centroid":[0.49483,0.06409,0.0094],"force_p95":0.55053,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5516,"mean_force":0.54555,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49538,0.14174,0.10308]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.47819,0.05912,0.0094],"force_p95":0.54863,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54896,"mean_force":0.54599,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48693,0.10024,0.03743]}],"total_contact_groups":7},"final_pose_error":0.12737,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49488,0.06366,0.03403],"final_tcp_position":[0.48693,0.10021,0.03744],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":136.74179,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":503.0,"n_steps_budget":1000.0,"object_pos_end":[0.49521,0.06403,0.03394],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14424,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54559,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":504.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_contact","tcp_end":[0.49704,0.14452,0.15836],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1482,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":359.0,"n_steps_budget":750.0,"object_pos_end":[0.49498,0.06364,0.034],"object_pos_start":[0.49521,0.06403,0.03394],"object_to_goal_dist_end":0.14385,"object_to_goal_dist_start":0.14424,"object_z_max":0.034,"peak_contact_force":0.54415,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":359.0,"raw_peak_contact_force":0.5516,"subtask_id":"reach_contact","tcp_end":[0.4958,0.13948,0.04825],"tcp_start":[0.49704,0.14452,0.15836],"tcp_to_object_dist_end":0.07717,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":478.0,"n_steps_budget":600.0,"object_pos_end":[0.4948,0.06387,0.03402],"object_pos_start":[0.49498,0.06364,0.034],"object_to_goal_dist_end":0.14409,"object_to_goal_dist_start":0.14385,"object_z_max":0.03403,"peak_contact_force":134.86146,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":733.0,"raw_peak_contact_force":136.74179,"subtask_id":"reach_contact","tcp_end":[0.48693,0.10026,0.03742],"tcp_start":[0.4958,0.13948,0.04825],"tcp_to_object_dist_end":0.03739,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49481,0.06379,0.03403],"object_pos_start":[0.4948,0.06387,0.03402],"object_to_goal_dist_end":0.14401,"object_to_goal_dist_start":0.14409,"object_z_max":0.03403,"peak_contact_force":93.62983,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":97.05405,"subtask_id":"reach_goal","tcp_end":[0.48693,0.10021,0.03744],"tcp_start":[0.48693,0.10022,0.03743],"tcp_to_object_dist_end":0.03742,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0188121de1b8142d5ff7a7406b62c43adf6da5520b986a997e46ef53b7d11bf9`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68539,"average_solve_count":89.0,"average_success_count":89.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_tolerance":0.00432,"align_1.lateral_offset_x":-0.01,"approach_1.approach_speed":0.08216,"descend_1.descend_tolerance":0.00932,"push_1.push_distance":0.15014,"push_1.push_speed":0.02844,"push_1.push_tolerance":0.01467},"optimized_scores":{"best_composite_score":-0.29068,"best_fitness_score":0.11932,"best_task_score":0.00049},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":259.0,"contact_point_centroid":[0.5316,0.1061,0.05998],"force_p95":140.48244,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":145.00919,"mean_force":87.20522,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48634,0.10458,0.03746]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.5314,0.09744,0.05993],"force_p95":98.44101,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":98.51272,"mean_force":97.86968,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48605,0.09632,0.03751]},{"body_a":"peg","body_b":"channel_base_body","contact_count":445.0,"contact_point_centroid":[0.49436,0.05891,0.00935],"force_p95":0.5919,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.57909,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49769,0.17094,0.22493]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49942,0.19838,0.29613]},{"body_a":"peg","body_b":"channel_base_body","contact_count":359.0,"contact_point_centroid":[0.4943,0.05914,0.00939],"force_p95":0.55039,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54609,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49538,0.1417,0.10298]},{"body_a":"peg","body_b":"channel_base_body","contact_count":532.0,"contact_point_centroid":[0.49401,0.05897,0.0094],"force_p95":0.55029,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55169,"mean_force":0.54572,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48802,0.11457,0.03915]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.48386,0.04474,0.0094],"force_p95":0.54406,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54423,"mean_force":0.54291,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48605,0.09632,0.03751]}],"total_contact_groups":7},"final_pose_error":0.15,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4941,0.05871,0.03399],"final_tcp_position":[0.48603,0.09623,0.03749],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":145.00919,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":474.0,"n_steps_budget":1000.0,"object_pos_end":[0.49421,0.05888,0.03386],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13913,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54289,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":480.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_contact","tcp_end":[0.49706,0.14445,0.1582],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15097,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":359.0,"n_steps_budget":750.0,"object_pos_end":[0.49398,0.05902,0.0339],"object_pos_start":[0.49421,0.05888,0.03386],"object_to_goal_dist_end":0.13929,"object_to_goal_dist_start":0.13913,"object_z_max":0.0339,"peak_contact_force":0.54477,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":359.0,"raw_peak_contact_force":0.55382,"subtask_id":"reach_contact","tcp_end":[0.4958,0.13947,0.04823],"tcp_start":[0.49706,0.14445,0.1582],"tcp_to_object_dist_end":0.08174,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":532.0,"n_steps_budget":600.0,"object_pos_end":[0.49392,0.0588,0.03399],"object_pos_start":[0.49398,0.05902,0.0339],"object_to_goal_dist_end":0.13906,"object_to_goal_dist_start":0.13929,"object_z_max":0.03398,"peak_contact_force":134.10076,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":791.0,"raw_peak_contact_force":145.00919,"subtask_id":"reach_contact","tcp_end":[0.48606,0.09637,0.03752],"tcp_start":[0.4958,0.13947,0.04823],"tcp_to_object_dist_end":0.03855,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49397,0.05875,0.03399],"object_pos_start":[0.49392,0.0588,0.03399],"object_to_goal_dist_end":0.13901,"object_to_goal_dist_start":0.13906,"object_z_max":0.03399,"peak_contact_force":97.30073,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":98.51272,"subtask_id":"reach_goal","tcp_end":[0.48603,0.09623,0.03749],"tcp_start":[0.48604,0.09627,0.0375],"tcp_to_object_dist_end":0.03847,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```