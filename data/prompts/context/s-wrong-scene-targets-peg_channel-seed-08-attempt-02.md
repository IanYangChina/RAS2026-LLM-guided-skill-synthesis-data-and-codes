## Search State

- **Seed**: 8
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 0.0326 | 0.00 | ❌ rejected |
| 1 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | -0.0488 | 0.15 | ✅ accepted |
| 0 | pull → insert → descend → contact | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_control | impedance_control | position_control | impedance_control | time_limit | pose_tolerance | contact_detected | force_exceeded | 5 | 0.2633 | 0.00 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`
- Frozen object start: [0.48615778212844485, -0.04101785253296597, 0.04]
- Frozen task target: [0.5, 0.2, 0.3]
- Goal object position: (0.5, 0.2, 0.3)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48615778212844485, -0.04101785253296597, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.48615778212844485, 0.11898214746703403, 0.04)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.48615778212844485, 0.11898214746703403, 0.04]
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
  frozen_object_start: [0.4862, 0.119, 0.04]
  frozen_task_target: [0.4862, -0.041, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48615778212844485, -0.04101785253296597, 0.04]}
  frozen_targets: {'channel_exit': [0.5, 0.2, 0.3]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e

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
| `object` | offset from object initial position (0.48615778212844485, -0.04101785253296597, 0.04) | approach/contact targets near object start |
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

## Current Skill (Q=0.033) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.06
  - 0.02
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
    offset:
    - 0.0
    - 0.06
    - 0.05
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: pre_contact
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.06
    - 0.02
    orientation:
      mode: none
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 2.0
      - 15.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_contact
- id: push_1
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
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    max_push_time:
      type: scalar
      range:
      - 1.0
      - 5.0
      default: 3.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_progress

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.06, 0.05], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.06, 0.02]
  - orientation: mode=none
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - max_push_time: status=consumed; consumers=duration.max_time (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.033
- **task_score** (E): 0.000
- **fitness_score**: 0.079  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2235 |
| descend_contact | 0.67 | 1.00 | 0.0521 |
| push_1 | 1.00 | 1.00 | 0.1449 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.105, 0.098) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.538 | 3.526 |
| descend_contact | contact | 0.67 / force_exceeded | (0.497, 0.105, 0.098)→(0.495, 0.075, 0.055) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.667 | 8.933 | 8.970 |
| push_1 | push | 1.00 / time_limit | (0.495, 0.075, 0.055)→(0.485, -0.004, 0.175) | (0.503, 0.080, 0.034)→(0.498, 0.105, 0.028) | 0.160→0.185 | 1.00 / 2.000 | 161.612 | 731.495 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.157
- phase_breakdown.pre_contact_score: 0.523
- phase_breakdown.push_progress_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.094
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: 0.212
- **K-run variance**: 0.0652
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.348


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a8ce855c7f52ba2d198de8387bdd2f3b869655c206850d620daaec6ac6f298cd`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `79b30dd7102e96fb2fa0880d3932c959e04a6f943c7e87b878f77a0e54f87a94`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,-0.04102,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,-0.04102,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.23684,"average_solve_count":76.0,"average_success_count":76.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.24155,"approach_1.approach_tolerance":0.01256,"descend_contact.contact_force_threshold":14.58682,"descend_contact.contact_speed":0.13232,"push_1.max_push_time":3.47956,"push_1.push_distance":0.19603,"push_1.push_speed":0.08229},"optimized_scores":{"best_composite_score":-0.32843,"best_fitness_score":0.05157,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":544.0,"contact_point_centroid":[0.53903,-0.02263,0.05988],"force_p95":394.75602,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":737.69361,"mean_force":254.82844,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52256,0.02323,0.14635]},{"body_a":"channel_base_body","body_b":"link6","contact_count":575.0,"contact_point_centroid":[0.51862,-0.11995,0.06491],"force_p95":293.29044,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":316.44876,"mean_force":248.46018,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49975,-0.02104,0.1721]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":51.0,"contact_point_centroid":[0.47498,-0.04271,0.05984],"force_p95":114.08276,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":117.58176,"mean_force":42.21804,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48775,-0.01546,0.16663]},{"body_a":"peg","body_b":"channel_base_body","contact_count":554.0,"contact_point_centroid":[0.49627,0.11906,0.00941],"force_p95":0.61256,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55533,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49753,0.15136,0.19501]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49958,0.19859,0.29732]},{"body_a":"peg","body_b":"channel_base_body","contact_count":495.0,"contact_point_centroid":[0.49598,0.1191,0.00943],"force_p95":0.60464,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65929,"mean_force":0.54182,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.49466,0.08299,0.06569]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49602,0.11912,0.00943],"force_p95":0.5997,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65085,"mean_force":0.54164,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50869,0.00286,0.15684]}],"total_contact_groups":7},"final_pose_error":0.16942,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49606,0.11903,0.03389],"final_tcp_position":[0.48908,-0.06268,0.19296],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":737.69361,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":579.0,"n_steps_budget":630.0,"object_pos_end":[0.49602,0.119,0.03385],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19914,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.51235,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":578.0,"raw_peak_contact_force":2.24822,"subtask_id":"pre_contact","tcp_end":[0.49655,0.1055,0.09821],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06576,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":495.0,"n_steps_budget":600.0,"object_pos_end":[0.49607,0.1194,0.03386],"object_pos_start":[0.49602,0.119,0.03385],"object_to_goal_dist_end":0.19954,"object_to_goal_dist_start":0.19914,"object_z_max":0.03403,"peak_contact_force":0.54856,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":495.0,"raw_peak_contact_force":0.65929,"subtask_id":"pre_contact","tcp_end":[0.49558,0.06262,0.03915],"tcp_start":[0.49655,0.1055,0.09821],"tcp_to_object_dist_end":0.05704,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49606,0.11903,0.03389],"object_pos_start":[0.49607,0.1194,0.03386],"object_to_goal_dist_end":0.19917,"object_to_goal_dist_start":0.19954,"object_z_max":0.03406,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2170.0,"raw_peak_contact_force":737.69361,"subtask_id":"push_progress","tcp_end":[0.48908,-0.06268,0.19296],"tcp_start":[0.49558,0.06262,0.03915],"tcp_to_object_dist_end":0.24161,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0a7722137b05abd45e72adac5a0a8f18d70c24ddc36cf4c70c52ed7e5618005d`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,-0.09705,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,-0.09705,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9125,"average_solve_count":80.0,"average_success_count":80.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.15404,"approach_1.approach_tolerance":0.00624,"descend_contact.contact_force_threshold":9.22998,"descend_contact.contact_speed":0.13638,"push_1.max_push_time":4.15993,"push_1.push_distance":0.24176,"push_1.push_speed":0.03229},"optimized_scores":{"best_composite_score":0.21416,"best_fitness_score":0.09416,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":913.0,"contact_point_centroid":[0.52979,0.00621,0.0599],"force_p95":346.97501,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":740.50666,"mean_force":223.47134,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51543,0.05171,0.15486]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":11.0,"contact_point_centroid":[0.47445,0.09577,0.0594],"force_p95":398.49739,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":403.63566,"mean_force":193.91527,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48164,0.10453,0.05635]},{"body_a":"channel_base_body","body_b":"link6","contact_count":467.0,"contact_point_centroid":[0.51766,-0.11998,0.06492],"force_p95":326.47834,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":347.20385,"mean_force":232.37561,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51727,0.03803,0.16398]},{"body_a":"attachment","body_b":"peg","contact_count":31.0,"contact_point_centroid":[0.49617,0.0905,0.05459],"force_p95":204.861,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":205.04383,"mean_force":121.5188,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48799,0.09627,0.05923]},{"body_a":"peg","body_b":"channel_base_body","contact_count":988.0,"contact_point_centroid":[0.49907,0.09556,0.00868],"force_p95":1.13635,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":204.89484,"mean_force":4.49438,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51423,0.05235,0.15244]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":29.0,"contact_point_centroid":[0.47498,-0.00837,0.05983],"force_p95":147.32861,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":149.9425,"mean_force":110.56449,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49201,0.03197,0.16221]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":29.0,"contact_point_centroid":[0.47421,0.09446,0.04719],"force_p95":22.3746,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.51138,"mean_force":4.87386,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4883,0.08898,0.08595]},{"body_a":"peg","body_b":"channel_base_body","contact_count":250.0,"contact_point_centroid":[0.50599,0.06297,0.00938],"force_p95":0.55144,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.22846,"mean_force":0.59329,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.49432,0.09308,0.07884]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50519,0.08086,0.05883],"force_p95":11.77548,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.77548,"mean_force":11.77548,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.49434,0.08192,0.06385]},{"body_a":"peg","body_b":"channel_base_body","contact_count":611.0,"contact_point_centroid":[0.50581,0.06298,0.00936],"force_p95":0.56203,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56871,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49743,0.15085,0.19393]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49943,0.19803,0.29588]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52504,0.06801,0.02571],"force_p95":2.11887,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.27425,"mean_force":1.0979,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50127,0.09558,0.11815]}],"total_contact_groups":12},"final_pose_error":0.2154,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49468,0.1007,0.02506],"final_tcp_position":[0.49132,0.0314,0.16272],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":740.50666,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":639.0,"n_steps_budget":960.0,"object_pos_end":[0.50596,0.06294,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.55501,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":645.0,"raw_peak_contact_force":3.88411,"subtask_id":"pre_contact","tcp_end":[0.49653,0.10521,0.09756],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07707,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":250.0,"n_steps_budget":600.0,"object_pos_end":[0.50596,0.06293,0.03381],"object_pos_start":[0.50596,0.06294,0.03381],"object_to_goal_dist_end":0.14319,"object_to_goal_dist_start":0.1432,"object_z_max":0.03381,"peak_contact_force":12.22846,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":251.0,"raw_peak_contact_force":12.22846,"subtask_id":"pre_contact","tcp_end":[0.49435,0.08185,0.06376],"tcp_start":[0.49653,0.10521,0.09756],"tcp_to_object_dist_end":0.03729,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49468,0.1007,0.02506],"object_pos_start":[0.50596,0.06293,0.03381],"object_to_goal_dist_end":0.1814,"object_to_goal_dist_start":0.14319,"object_z_max":0.04018,"peak_contact_force":179.64524,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2487.0,"raw_peak_contact_force":740.50666,"subtask_id":"push_progress","tcp_end":[0.49132,0.0314,0.16272],"tcp_start":[0.49435,0.08185,0.06376],"tcp_to_object_dist_end":0.15415,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `bf9c239495ea25cc1b534d0795871edaef0fee72244885088104a44eb548c1a2`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,-0.10339,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,-0.10339,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.85294,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.05101,"approach_1.approach_tolerance":0.00697,"descend_contact.contact_force_threshold":9.87035,"descend_contact.contact_speed":0.02171,"push_1.max_push_time":3.95429,"push_1.push_distance":0.16239,"push_1.push_speed":0.05346},"optimized_scores":{"best_composite_score":0.21207,"best_fitness_score":0.09207,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":668.0,"contact_point_centroid":[0.52735,0.00659,0.05989],"force_p95":368.64184,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":716.28474,"mean_force":235.36731,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51335,0.05332,0.15225]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":13.0,"contact_point_centroid":[0.47412,0.09699,0.05911],"force_p95":494.04881,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":517.91234,"mean_force":195.63144,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48179,0.10458,0.05493]},{"body_a":"channel_base_body","body_b":"link6","contact_count":560.0,"contact_point_centroid":[0.51961,-0.11998,0.06494],"force_p95":323.548,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":352.5474,"mean_force":265.77519,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50109,0.03223,0.16462]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":71.0,"contact_point_centroid":[0.475,-0.00947,0.05996],"force_p95":138.81008,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":222.70629,"mean_force":108.23696,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4884,0.03066,0.16291]},{"body_a":"attachment","body_b":"peg","contact_count":26.0,"contact_point_centroid":[0.4965,0.08703,0.05385],"force_p95":188.97226,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":192.19544,"mean_force":110.28403,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4887,0.09443,0.05825]},{"body_a":"peg","body_b":"channel_base_body","contact_count":990.0,"contact_point_centroid":[0.50062,0.09157,0.00824],"force_p95":1.142,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":191.82112,"mean_force":3.57092,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5044,0.0471,0.15331]},{"body_a":"peg","body_b":"channel_base_body","contact_count":331.0,"contact_point_centroid":[0.50612,0.05667,0.00938],"force_p95":0.55203,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.02155,"mean_force":0.58727,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.49415,0.09255,0.07795]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50328,0.0743,0.05885],"force_p95":13.53413,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.53413,"mean_force":13.53413,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.49437,0.08123,0.06291]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":31.0,"contact_point_centroid":[0.47431,0.08983,0.04676],"force_p95":11.18318,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.97732,"mean_force":2.66545,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48926,0.088,0.08691]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.52503,0.06503,0.02537],"force_p95":5.67984,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.98019,"mean_force":1.61591,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49666,0.07868,0.12928]},{"body_a":"peg","body_b":"channel_base_body","contact_count":726.0,"contact_point_centroid":[0.50597,0.05662,0.00936],"force_p95":0.60038,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.5685,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49734,0.151,0.19426]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49937,0.19822,0.29624]}],"total_contact_groups":12},"final_pose_error":0.14879,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50274,0.09501,0.02421],"final_tcp_position":[0.47524,0.01987,0.17033],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":716.28474,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":755.0,"n_steps_budget":1000.0,"object_pos_end":[0.50613,0.05658,0.0338],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13685,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.54566,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":763.0,"raw_peak_contact_force":4.44541,"subtask_id":"pre_contact","tcp_end":[0.4965,0.10519,0.09749],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0807,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":331.0,"n_steps_budget":1000.0,"object_pos_end":[0.50618,0.05655,0.03382],"object_pos_start":[0.50613,0.05658,0.0338],"object_to_goal_dist_end":0.13683,"object_to_goal_dist_start":0.13685,"object_z_max":0.03382,"peak_contact_force":14.02155,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":332.0,"raw_peak_contact_force":14.02155,"subtask_id":"pre_contact","tcp_end":[0.49437,0.08118,0.06284],"tcp_start":[0.4965,0.10519,0.09749],"tcp_to_object_dist_end":0.03985,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50274,0.09501,0.02421],"object_pos_start":[0.50618,0.05655,0.03382],"object_to_goal_dist_end":0.17574,"object_to_goal_dist_start":0.13683,"object_z_max":0.04038,"peak_contact_force":305.19055,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2379.0,"raw_peak_contact_force":716.28474,"subtask_id":"push_progress","tcp_end":[0.47524,0.01987,0.17033],"tcp_start":[0.49437,0.08118,0.06284],"tcp_to_object_dist_end":0.16659,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```