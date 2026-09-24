## Search State

- **Seed**: 2
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → align → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | 0.2541 | 0.19 | ❌ rejected |
| 8 | approach → descend → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.1587 | 0.47 | ✅ accepted |
| 7 | approach → descend → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | 0.0610 | 0.41 | ✅ accepted |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 8 | 0.1209 | 0.27 | ❌ rejected |
| 5 | approach → descend → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.0672 | 0.34 | ✅ accepted |

**Proposal policy**: task_score is 0.19 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`
- Frozen object start: [0.48092897073994534, 0.06387929147312987, 0.04]
- Frozen task target: [0.48092897073994534, -0.09612070852687013, 0.04]
- Goal object position: (0.48092897073994534, -0.09612070852687013, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48092897073994534, 0.06387929147312987, 0.04)
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
  frozen_object_start: [0.4809, 0.0639, 0.04]
  frozen_task_target: [0.4809, -0.0961, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48092897073994534, 0.06387929147312987, 0.04]}
  frozen_targets: {'channel_exit': [0.48092897073994534, -0.09612070852687013, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7

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
| `object` | offset from object initial position (0.48092897073994534, 0.06387929147312987, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.48092897073994534, -0.09612070852687013, 0.04) | final destination targets |
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

## Current Skill (Q=0.254) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach_peg
  anchor: object
  offset:
  - 0.0
  - 0.02
  - 0.06
  weight: 0.3
- id: push_through
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_peg
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.02
    - 0.06
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.03
      - 0.1
      default: 0.06
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_y_offset:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.y
        mode: replace
  subtask_id: approach_peg
- id: descend_to_contact
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.01
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    descend_y_offset:
      type: scalar
      range:
      - -0.02
      - 0.03
      default: 0.01
      binds_to:
      - path: target.offset.y
        mode: replace
  subtask_id: approach_peg
- id: lateral_align
  type: align
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.01
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - -1.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    align_x_offset:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    align_y_offset:
      type: scalar
      range:
      - -0.01
      - 0.04
      default: 0.01
      binds_to:
      - path: target.offset.y
        mode: replace
  subtask_id: push_through
- id: push_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.18
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - -1.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    max_push_duration:
      type: scalar
      range:
      - 2.0
      - 6.0
      default: 5.0
      binds_to:
      - path: duration.max_time
        mode: replace
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
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_through

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.02, 0.06]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_y_offset: status=consumed; consumers=target.offset.y (replace)
- **descend_to_contact** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.01, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_y_offset: status=consumed; consumers=target.offset.y (replace)
- **lateral_align** (`align`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.01, 0.0]
  - orientation: mode=align_axis, axis=[0.0, -1.0, 0.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - align_x_offset: status=consumed; consumers=target.offset.x (replace)
    - align_y_offset: status=consumed; consumers=target.offset.y (replace)
- **push_channel** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.18, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, -1.0, 0.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - max_push_duration: status=consumed; consumers=duration.max_time (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.254
- **task_score** (E): 0.189
- **fitness_score**: 0.381  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.2105 |
| align_orientation | 1.00 | 1.00 | 0.0283 |
| descend_center | 1.00 | 1.00 | 0.0366 |
| push_channel | 1.00 | 1.00 | 0.1543 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.492, 0.100, 0.118) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.547 | 3.659 |
| align_orientation | align | 1.00 / step_budget | (0.492, 0.100, 0.118)→(0.496, 0.091, 0.096) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.000 | 0.546 | 0.552 |
| descend_center | descend | 1.00 / force_exceeded | (0.496, 0.091, 0.096)→(0.493, 0.093, 0.060) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 2.000 | 28.083 | 28.083 |
| push_channel | push | 1.00 / time_limit | (0.493, 0.093, 0.060)→(0.495, -0.060, 0.043) | (0.498, 0.068, 0.034)→(0.495, -0.016, 0.025) | 0.148→0.066 | 1.00 / 1.000 | 0.686 | 103.181 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.490
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.291
- phase_score: 0.507
- phase_breakdown.approach_peg_score: 0.451
- phase_breakdown.push_through_score: 0.531

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.421
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.291
- **Median Q (composite search score)**: 0.266
- **K-run variance**: 0.0014
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.369


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `6269840a353345700ffa70ea476a3ad730b138bf2ec3c52304c054f0e194e023`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a2936262b79fcd5a49fda15d77b54223f43c58bfee2e71dc505f8a2f79369706`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77193,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.06904,"approach_peg.approach_y_offset":0.03216,"descend_center.center_x_offset":-0.0048,"descend_center.center_y_offset":0.02023,"descend_center.contact_force_threshold":15.32505,"push_channel.max_push_duration":4.20344,"push_channel.push_distance":0.17522,"push_channel.push_speed":0.09379},"optimized_scores":{"best_composite_score":0.29396,"best_fitness_score":0.42063,"best_task_score":0.29077},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":996.0,"contact_point_centroid":[0.50083,0.02005,0.00879],"force_p95":107.46973,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":110.01838,"mean_force":56.0121,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49153,0.01293,0.05307]},{"body_a":"attachment","body_b":"peg","contact_count":840.0,"contact_point_centroid":[0.50067,0.02799,0.05468],"force_p95":107.19562,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":109.48542,"mean_force":65.86045,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49124,0.02496,0.05492]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":40.0,"contact_point_centroid":[0.475,0.06921,0.06],"force_p95":78.10008,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":79.46762,"mean_force":62.57847,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48588,0.07339,0.05825]},{"body_a":"peg","body_b":"channel_base_body","contact_count":202.0,"contact_point_centroid":[0.49457,0.06379,0.0094],"force_p95":0.55038,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.93799,"mean_force":0.69525,"phase_index":2.0,"phase_name":"descend_center","phase_type":"descend","tcp_position_centroid":[0.48536,0.0875,0.07813]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.49615,0.08135,0.05908],"force_p95":16.38965,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.51417,"mean_force":15.26897,"phase_index":2.0,"phase_name":"descend_center","phase_type":"descend","tcp_position_centroid":[0.48531,0.08619,0.06072]},{"body_a":"peg","body_b":"channel_base_body","contact_count":620.0,"contact_point_centroid":[0.49543,0.0638,0.00937],"force_p95":0.56835,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55929,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48845,0.14924,0.20384]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49932,0.19836,0.2971]},{"body_a":"peg","body_b":"channel_base_body","contact_count":112.0,"contact_point_centroid":[0.49532,0.06406,0.0094],"force_p95":0.55066,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5516,"mean_force":0.5455,"phase_index":1.0,"phase_name":"align_orientation","phase_type":"align","tcp_position_centroid":[0.48198,0.09581,0.10559]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.475,-0.03574,0.03221],"force_p95":0.34597,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34597,"mean_force":0.34597,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49268,-0.04851,0.04328]}],"total_contact_groups":9},"final_pose_error":0.04605,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49638,-0.01456,0.02415],"final_tcp_position":[0.4938,-0.06583,0.04122],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":110.01838,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":647.0,"n_steps_budget":1000.0,"object_pos_end":[0.49527,0.06401,0.03396],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14422,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54509,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":648.0,"raw_peak_contact_force":2.44546,"subtask_id":"approach_peg","tcp_end":[0.47909,0.10197,0.1167],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09246,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":112.0,"n_steps_budget":600.0,"object_pos_end":[0.49519,0.0641,0.03398],"object_pos_start":[0.49527,0.06401,0.03396],"object_to_goal_dist_end":0.14431,"object_to_goal_dist_start":0.14422,"object_z_max":0.03398,"peak_contact_force":0.54792,"phase_name":"align_orientation","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":112.0,"raw_peak_contact_force":0.5516,"subtask_id":"approach_peg","tcp_end":[0.4871,0.08904,0.09651],"tcp_start":[0.47909,0.10197,0.1167],"tcp_to_object_dist_end":0.06781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":202.0,"n_steps_budget":600.0,"object_pos_end":[0.49529,0.06366,0.034],"object_pos_start":[0.49519,0.0641,0.03398],"object_to_goal_dist_end":0.14386,"object_to_goal_dist_start":0.14431,"object_z_max":0.03401,"peak_contact_force":16.93799,"phase_name":"descend_center","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":204.0,"raw_peak_contact_force":16.93799,"subtask_id":"approach_peg","tcp_end":[0.48532,0.08618,0.06049],"tcp_start":[0.4871,0.08904,0.09651],"tcp_to_object_dist_end":0.03618,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49638,-0.01456,0.02415],"object_pos_start":[0.49529,0.06366,0.034],"object_to_goal_dist_end":0.06743,"object_to_goal_dist_start":0.14386,"object_z_max":0.04014,"peak_contact_force":0.7051,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1877.0,"raw_peak_contact_force":110.01838,"subtask_id":"push_through","tcp_end":[0.4938,-0.06583,0.04122],"tcp_start":[0.48532,0.08618,0.06049],"tcp_to_object_dist_end":0.0541,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `78f29ebb38dd2df9149fb0cd7c7c33d55e802bb94eee599b284bb0b197a04fb7`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76991,"average_solve_count":113.0,"average_success_count":113.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.08646,"approach_peg.approach_y_offset":0.02306,"descend_center.center_x_offset":0.00211,"descend_center.center_y_offset":0.03062,"descend_center.contact_force_threshold":29.81348,"push_channel.max_push_duration":4.85885,"push_channel.push_distance":0.21814,"push_channel.push_speed":0.092},"optimized_scores":{"best_composite_score":0.26559,"best_fitness_score":0.39225,"best_task_score":0.17911},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":995.0,"contact_point_centroid":[0.50059,0.01678,0.00891],"force_p95":94.89958,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":97.06111,"mean_force":58.65606,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49307,0.01293,0.05457]},{"body_a":"attachment","body_b":"peg","contact_count":910.0,"contact_point_centroid":[0.50184,0.02192,0.05513],"force_p95":94.50963,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":96.53342,"mean_force":63.61268,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49301,0.01904,0.05531]},{"body_a":"peg","body_b":"channel_base_body","contact_count":248.0,"contact_point_centroid":[0.49381,0.05952,0.00939],"force_p95":0.55071,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.16781,"mean_force":1.3012,"phase_index":2.0,"phase_name":"descend_center","phase_type":"descend","tcp_position_centroid":[0.48551,0.08258,0.07729]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.49634,0.07674,0.05867],"force_p95":33.46893,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.66172,"mean_force":20.87012,"phase_index":2.0,"phase_name":"descend_center","phase_type":"descend","tcp_position_centroid":[0.48765,0.08486,0.0598]},{"body_a":"peg","body_b":"channel_base_body","contact_count":608.0,"contact_point_centroid":[0.49437,0.05889,0.00936],"force_p95":0.56331,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.57027,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48168,0.14227,0.21188]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49889,0.19762,0.29624]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":17.0,"contact_point_centroid":[0.475,0.01265,0.02281],"force_p95":2.72888,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.03779,"mean_force":1.62106,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49465,-0.04302,0.04904]},{"body_a":"peg","body_b":"channel_base_body","contact_count":187.0,"contact_point_centroid":[0.4939,0.05896,0.00939],"force_p95":0.55012,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54598,"phase_index":1.0,"phase_name":"align_orientation","phase_type":"align","tcp_position_centroid":[0.47434,0.08504,0.11427]}],"total_contact_groups":8},"final_pose_error":0.09511,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49343,-0.02536,0.02664],"final_tcp_position":[0.4938,-0.06421,0.04516],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":97.06111,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":637.0,"n_steps_budget":1000.0,"object_pos_end":[0.49425,0.05902,0.03388],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13927,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54859,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":643.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach_peg","tcp_end":[0.46607,0.08899,0.13332],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10761,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":187.0,"n_steps_budget":600.0,"object_pos_end":[0.49427,0.0589,0.0339],"object_pos_start":[0.49425,0.05902,0.03388],"object_to_goal_dist_end":0.13915,"object_to_goal_dist_start":0.13927,"object_z_max":0.0339,"peak_contact_force":0.54495,"phase_name":"align_orientation","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":187.0,"raw_peak_contact_force":0.55382,"subtask_id":"approach_peg","tcp_end":[0.48528,0.08063,0.09769],"tcp_start":[0.46607,0.08899,0.13332],"tcp_to_object_dist_end":0.06798,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":248.0,"n_steps_budget":600.0,"object_pos_end":[0.49399,0.05891,0.03394],"object_pos_start":[0.49427,0.0589,0.0339],"object_to_goal_dist_end":0.13918,"object_to_goal_dist_start":0.13915,"object_z_max":0.03395,"peak_contact_force":37.16781,"phase_name":"descend_center","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":257.0,"raw_peak_contact_force":37.16781,"subtask_id":"approach_peg","tcp_end":[0.48787,0.08499,0.05936],"tcp_start":[0.48528,0.08063,0.09769],"tcp_to_object_dist_end":0.03693,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49343,-0.02536,0.02664],"object_pos_start":[0.49399,0.05891,0.03394],"object_to_goal_dist_end":0.05663,"object_to_goal_dist_start":0.13918,"object_z_max":0.0403,"peak_contact_force":0.53753,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1922.0,"raw_peak_contact_force":97.06111,"subtask_id":"push_through","tcp_end":[0.4938,-0.06421,0.04516],"tcp_start":[0.48787,0.08499,0.05936],"tcp_to_object_dist_end":0.04304,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ecba62e37d233197bb248f7fe6e722b45204af5e83240a6f27138a89bcccfe42`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72414,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.05608,"approach_peg.approach_y_offset":0.02326,"descend_center.center_x_offset":-0.00341,"descend_center.center_y_offset":0.03185,"descend_center.contact_force_threshold":17.85154,"push_channel.max_push_duration":4.41191,"push_channel.push_distance":0.21765,"push_channel.push_speed":0.09958},"optimized_scores":{"best_composite_score":0.20285,"best_fitness_score":0.32951,"best_task_score":0.09839},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":996.0,"contact_point_centroid":[0.51085,0.03508,0.00889],"force_p95":100.26309,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":102.46416,"mean_force":60.30426,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50366,0.03179,0.05415]},{"body_a":"attachment","body_b":"peg","contact_count":888.0,"contact_point_centroid":[0.51319,0.04239,0.05508],"force_p95":99.9396,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":101.941,"mean_force":67.1436,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50436,0.04044,0.05522]},{"body_a":"peg","body_b":"channel_base_body","contact_count":167.0,"contact_point_centroid":[0.50616,0.08098,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.1423,"mean_force":0.82498,"phase_index":2.0,"phase_name":"descend_center","phase_type":"descend","tcp_position_centroid":[0.50993,0.10529,0.0764]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.51236,0.09768,0.05873],"force_p95":28.95017,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.58324,"mean_force":23.25259,"phase_index":2.0,"phase_name":"descend_center","phase_type":"descend","tcp_position_centroid":[0.50559,0.10751,0.05982]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":41.0,"contact_point_centroid":[0.52501,0.0608,0.05309],"force_p95":10.12704,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.59975,"mean_force":3.72275,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50467,0.0746,0.05698]},{"body_a":"peg","body_b":"channel_base_body","contact_count":674.0,"contact_point_centroid":[0.50578,0.08089,0.00936],"force_p95":0.55526,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.5694,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51461,0.15271,0.19631]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50005,0.19808,0.29587]},{"body_a":"peg","body_b":"channel_base_body","contact_count":56.0,"contact_point_centroid":[0.5057,0.08039,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54679,"phase_index":1.0,"phase_name":"align_orientation","phase_type":"align","tcp_position_centroid":[0.5229,0.10725,0.09718]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47498,-0.02856,0.03127],"force_p95":0.34336,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34973,"mean_force":0.24756,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49746,-0.04184,0.04473]}],"total_contact_groups":9},"final_pose_error":0.08554,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49606,-0.00696,0.0242],"final_tcp_position":[0.49699,-0.05095,0.04387],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":102.46416,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":703.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54611,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":710.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach_peg","tcp_end":[0.52991,0.10905,0.10268],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0782,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":56.0,"n_steps_budget":600.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.50597,0.08086,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16109,"object_z_max":0.03378,"peak_contact_force":0.5464,"phase_name":"align_orientation","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":56.0,"raw_peak_contact_force":0.55006,"subtask_id":"approach_peg","tcp_end":[0.51527,0.10398,0.09308],"tcp_start":[0.52991,0.10905,0.10268],"tcp_to_object_dist_end":0.06432,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":167.0,"n_steps_budget":600.0,"object_pos_end":[0.50601,0.08087,0.03378],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":30.1423,"phase_name":"descend_center","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":169.0,"raw_peak_contact_force":30.1423,"subtask_id":"approach_peg","tcp_end":[0.50554,0.10758,0.05956],"tcp_start":[0.51527,0.10398,0.09308],"tcp_to_object_dist_end":0.03712,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49606,-0.00696,0.0242],"object_pos_start":[0.50601,0.08087,0.03378],"object_to_goal_dist_end":0.07483,"object_to_goal_dist_start":0.1611,"object_z_max":0.04018,"peak_contact_force":0.81531,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1929.0,"raw_peak_contact_force":102.46416,"subtask_id":"push_through","tcp_end":[0.49699,-0.05095,0.04387],"tcp_start":[0.50554,0.10758,0.05956],"tcp_to_object_dist_end":0.04819,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```