## Search State

- **Seed**: 2
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → align → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 9 | 0.2743 | 0.33 | ❌ rejected |
| 9 | approach → align → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | 0.2541 | 0.19 | ❌ rejected |
| 8 | approach → descend → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.1587 | 0.47 | ✅ accepted |
| 7 | approach → descend → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | 0.0610 | 0.41 | ✅ accepted |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 8 | 0.1209 | 0.27 | ❌ rejected |

**Proposal policy**: task_score is 0.33 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.274) — your mutation base

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

- **Composite score**: 0.274
- **task_score** (E): 0.333
- **fitness_score**: 0.562  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.222
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.2168 |
| align_orientation | 1.00 | 0.67 | 0.0785 |
| descend_to_peg | 0.67 | 1.00 | 0.0136 |
| push_channel | 1.00 | 1.00 | 0.1263 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.491, 0.096, 0.112) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.544 | 3.659 |
| align_orientation | align | 1.00 / step_budget | (0.491, 0.096, 0.112)→(0.508, 0.094, 0.043) | (0.498, 0.068, 0.034)→(0.499, 0.056, 0.036) | 0.148→0.137 | 0.67 / 1.000 | 138.056 | 327.320 |
| descend_to_peg | descend | 0.67 / force_exceeded | (0.508, 0.094, 0.043)→(0.505, 0.082, 0.039) | (0.499, 0.056, 0.036)→(0.498, 0.036, 0.035) | 0.137→0.117 | 1.00 / 1.667 | 11.927 | 9.993 |
| push_channel | push | 1.00 / time_limit | (0.505, 0.082, 0.039)→(0.498, -0.044, 0.036) | (0.498, 0.036, 0.035)→(0.501, -0.073, 0.035) | 0.117→0.010 | 1.00 / 2.000 | 3.859 | 33.885 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.849
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.473
- phase_score: 0.734
- phase_breakdown.approach_peg_score: 0.279
- phase_breakdown.push_through_score: 0.929

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.630
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.473
- **Median Q (composite search score)**: 0.337
- **K-run variance**: 0.0313
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.315


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85965,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_orientation.align_x_offset":0.01595,"align_orientation.align_y_offset":0.02474,"approach_peg.approach_height":0.05424,"approach_peg.approach_y_offset":0.01254,"descend_to_peg.descend_force_threshold":11.35142,"descend_to_peg.descend_y_offset":0.00349,"push_channel.max_push_duration":4.98683,"push_channel.push_distance":0.20325,"push_channel.push_speed":0.07724},"optimized_scores":{"best_composite_score":0.45291,"best_fitness_score":0.62957,"best_task_score":0.47257},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":307.0,"contact_point_centroid":[0.50089,0.06694,0.00903],"force_p95":165.78321,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":173.26257,"mean_force":44.99613,"phase_index":1.0,"phase_name":"align_orientation","phase_type":"align","tcp_position_centroid":[0.49275,0.0837,0.06932]},{"body_a":"attachment","body_b":"peg","contact_count":118.0,"contact_point_centroid":[0.50681,0.07787,0.05548],"force_p95":165.82285,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":172.45411,"mean_force":115.70149,"phase_index":1.0,"phase_name":"align_orientation","phase_type":"align","tcp_position_centroid":[0.50318,0.08773,0.05349]},{"body_a":"peg","body_b":"channel_base_body","contact_count":41.0,"contact_point_centroid":[0.49021,0.04355,0.00915],"force_p95":5.30664,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.63276,"mean_force":0.94016,"phase_index":2.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50806,0.0874,0.04117]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.50297,0.07385,0.0396],"force_p95":6.24012,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.41333,"mean_force":2.27133,"phase_index":2.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50604,0.08491,0.03916]},{"body_a":"peg","body_b":"channel_base_body","contact_count":825.0,"contact_point_centroid":[0.49517,-0.0169,0.00986],"force_p95":3.12604,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.28753,"mean_force":1.22206,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50065,0.02099,0.03519]},{"body_a":"attachment","body_b":"peg","contact_count":658.0,"contact_point_centroid":[0.49915,0.0076,0.03555],"force_p95":2.74311,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.90565,"mean_force":1.03961,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50059,0.0194,0.03517]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":20.0,"contact_point_centroid":[0.47475,0.05039,0.05918],"force_p95":2.5981,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.92801,"mean_force":0.63837,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50355,0.07989,0.0364]},{"body_a":"peg","body_b":"channel_base_body","contact_count":700.0,"contact_point_centroid":[0.49526,0.06389,0.00938],"force_p95":0.56539,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55771,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48828,0.13927,0.19577]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":14.0,"contact_point_centroid":[0.47464,0.05152,0.05831],"force_p95":1.22536,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.39824,"mean_force":0.38224,"phase_index":2.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50864,0.08819,0.04174]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49934,0.19828,0.29717]}],"total_contact_groups":10},"final_pose_error":0.10444,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49766,-0.07204,0.03498],"final_tcp_position":[0.49922,-0.04205,0.03586],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":173.26257,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":727.0,"n_steps_budget":1000.0,"object_pos_end":[0.49511,0.06363,0.03398],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14384,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54155,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":728.0,"raw_peak_contact_force":2.44546,"subtask_id":"approach_peg","tcp_end":[0.47885,0.08281,0.10143],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07199,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":307.0,"n_steps_budget":600.0,"object_pos_end":[0.49724,0.05672,0.03333],"object_pos_start":[0.49511,0.06363,0.03398],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.14384,"object_z_max":0.03465,"peak_contact_force":1.06157,"phase_name":"align_orientation","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":425.0,"raw_peak_contact_force":173.26257,"subtask_id":"approach_peg","tcp_end":[0.51036,0.08935,0.04372],"tcp_start":[0.47885,0.08281,0.10143],"tcp_to_object_dist_end":0.03667,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":47.0,"n_steps_budget":600.0,"object_pos_end":[0.49795,0.05685,0.03605],"object_pos_start":[0.49724,0.05672,0.03333],"object_to_goal_dist_end":0.13692,"object_to_goal_dist_start":0.13691,"object_z_max":0.03669,"peak_contact_force":15.49073,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":64.0,"raw_peak_contact_force":6.63276,"subtask_id":"push_through","tcp_end":[0.50565,0.08435,0.03879],"tcp_start":[0.51036,0.08935,0.04372],"tcp_to_object_dist_end":0.02869,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49766,-0.07204,0.03498],"object_pos_start":[0.49795,0.05685,0.03605],"object_to_goal_dist_end":0.0097,"object_to_goal_dist_start":0.13692,"object_z_max":0.0367,"peak_contact_force":0.02532,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1503.0,"raw_peak_contact_force":5.28753,"subtask_id":"push_through","tcp_end":[0.49922,-0.04205,0.03586],"tcp_start":[0.50565,0.08435,0.03879],"tcp_to_object_dist_end":0.03004,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91818,"average_solve_count":110.0,"average_success_count":110.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_orientation.align_x_offset":0.0389,"align_orientation.align_y_offset":0.03273,"approach_peg.approach_height":0.04671,"approach_peg.approach_y_offset":0.02659,"descend_to_peg.descend_force_threshold":16.41314,"descend_to_peg.descend_y_offset":-0.00013,"push_channel.max_push_duration":4.69312,"push_channel.push_distance":0.14311,"push_channel.push_speed":0.08081},"optimized_scores":{"best_composite_score":0.33691,"best_fitness_score":0.51357,"best_task_score":0.22084},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":104.0,"contact_point_centroid":[0.52524,0.09193,0.05996],"force_p95":572.27142,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":616.34339,"mean_force":417.04474,"phase_index":1.0,"phase_name":"align_orientation","phase_type":"align","tcp_position_centroid":[0.50985,0.09174,0.04293]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52502,0.09245,0.05999],"force_p95":83.60662,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":84.56286,"mean_force":75.00048,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50761,0.09205,0.04098]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.5251,0.09259,0.05997],"force_p95":15.79395,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":19.74244,"mean_force":3.94849,"phase_index":2.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50787,0.09218,0.04122]},{"body_a":"attachment","body_b":"peg","contact_count":667.0,"contact_point_centroid":[0.49791,0.01167,0.03682],"force_p95":4.59828,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.5095,"mean_force":1.50023,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50081,0.02319,0.036]},{"body_a":"peg","body_b":"channel_base_body","contact_count":719.0,"contact_point_centroid":[0.4935,-0.01153,0.00988],"force_p95":4.50757,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.3746,"mean_force":1.62757,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50113,0.02697,0.03621]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":584.0,"contact_point_centroid":[0.47494,0.00629,0.03155],"force_p95":1.79513,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.33846,"mean_force":0.58105,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50133,0.03493,0.03606]},{"body_a":"peg","body_b":"channel_base_body","contact_count":697.0,"contact_point_centroid":[0.49439,0.05899,0.00936],"force_p95":0.55981,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56718,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48145,0.14362,0.19213]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49898,0.19791,0.29603]},{"body_a":"peg","body_b":"channel_base_body","contact_count":432.0,"contact_point_centroid":[0.49408,0.05879,0.00939],"force_p95":0.55013,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54585,"phase_index":1.0,"phase_name":"align_orientation","phase_type":"align","tcp_position_centroid":[0.49307,0.08996,0.0621]},{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.4992,0.07452,0.0094],"force_p95":0.54795,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54826,"mean_force":0.54487,"phase_index":2.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50787,0.09218,0.04122]}],"total_contact_groups":10},"final_pose_error":0.04463,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49763,-0.06927,0.03479],"final_tcp_position":[0.49803,-0.03936,0.03563],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":616.34339,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":726.0,"n_steps_budget":1000.0,"object_pos_end":[0.49405,0.05908,0.03389],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13934,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.543,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":732.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach_peg","tcp_end":[0.46559,0.09135,0.09452],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07434,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":432.0,"n_steps_budget":600.0,"object_pos_end":[0.49429,0.05909,0.03395],"object_pos_start":[0.49405,0.05908,0.03389],"object_to_goal_dist_end":0.13934,"object_to_goal_dist_start":0.13934,"object_z_max":0.03395,"peak_contact_force":413.10716,"phase_name":"align_orientation","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":536.0,"raw_peak_contact_force":616.34339,"subtask_id":"approach_peg","tcp_end":[0.50798,0.09222,0.04131],"tcp_start":[0.46559,0.09135,0.09452],"tcp_to_object_dist_end":0.0366,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":5.0,"n_steps_budget":600.0,"object_pos_end":[0.49401,0.05913,0.03395],"object_pos_start":[0.49429,0.05909,0.03395],"object_to_goal_dist_end":0.13939,"object_to_goal_dist_start":0.13934,"object_z_max":0.03395,"peak_contact_force":19.74244,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10.0,"raw_peak_contact_force":19.74244,"subtask_id":"push_through","tcp_end":[0.50766,0.09207,0.04102],"tcp_start":[0.50798,0.09222,0.04131],"tcp_to_object_dist_end":0.03635,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49763,-0.06927,0.03479],"object_pos_start":[0.49401,0.05913,0.03395],"object_to_goal_dist_end":0.01217,"object_to_goal_dist_start":0.13939,"object_z_max":0.03548,"peak_contact_force":4.22682,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1972.0,"raw_peak_contact_force":84.56286,"subtask_id":"push_through","tcp_end":[0.49803,-0.03936,0.03563],"tcp_start":[0.50766,0.09207,0.04102],"tcp_to_object_dist_end":0.02992,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.775,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_orientation.align_x_offset":-0.00429,"align_orientation.align_y_offset":0.01874,"approach_peg.approach_height":0.09385,"approach_peg.approach_y_offset":0.0286,"descend_to_peg.descend_force_threshold":11.13267,"descend_to_peg.descend_y_offset":0.01502,"push_channel.max_push_duration":3.2109,"push_channel.push_distance":0.14322,"push_channel.push_speed":0.07352},"optimized_scores":{"best_composite_score":0.03314,"best_fitness_score":0.54314,"best_task_score":0.30621},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":339.0,"contact_point_centroid":[0.50834,0.08268,0.0091],"force_p95":162.22207,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":192.35443,"mean_force":31.20619,"phase_index":1.0,"phase_name":"align_orientation","phase_type":"align","tcp_position_centroid":[0.51518,0.10646,0.08684]},{"body_a":"attachment","body_b":"peg","contact_count":84.0,"contact_point_centroid":[0.5157,0.09474,0.05437],"force_p95":186.85096,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":191.989,"mean_force":123.86605,"phase_index":1.0,"phase_name":"align_orientation","phase_type":"align","tcp_position_centroid":[0.50777,0.10292,0.05356]},{"body_a":"attachment","body_b":"peg","contact_count":472.0,"contact_point_centroid":[0.50092,-0.02614,0.0416],"force_p95":7.897,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.80595,"mean_force":2.86459,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49627,-0.01484,0.03618]},{"body_a":"peg","body_b":"channel_base_body","contact_count":773.0,"contact_point_centroid":[0.5036,-0.03078,0.00964],"force_p95":6.71901,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.7802,"mean_force":2.0354,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49678,0.01863,0.03515]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":356.0,"contact_point_centroid":[0.52509,-0.04622,0.02666],"force_p95":3.6399,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.69218,"mean_force":1.34541,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49624,-0.01882,0.03634]},{"body_a":"peg","body_b":"channel_base_body","contact_count":567.0,"contact_point_centroid":[0.50574,0.08087,0.00936],"force_p95":0.55737,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57368,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51464,0.15568,0.21527]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50015,0.19792,0.29599]},{"body_a":"peg","body_b":"channel_base_body","contact_count":451.0,"contact_point_centroid":[0.50097,-0.00771,0.00939],"force_p95":0.95071,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.60388,"mean_force":0.57381,"phase_index":2.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50137,0.08383,0.03779]}],"total_contact_groups":8},"final_pose_error":0.10022,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50696,-0.07763,0.03577],"final_tcp_position":[0.496,-0.04984,0.03751],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":192.35443,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":596.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54818,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":603.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach_peg","tcp_end":[0.52985,0.11504,0.13994],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11406,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":344.0,"n_steps_budget":720.0,"object_pos_end":[0.50469,0.05354,0.04221],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.13365,"object_to_goal_dist_start":0.1611,"object_z_max":0.04199,"peak_contact_force":0.0,"phase_name":"align_orientation","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":423.0,"raw_peak_contact_force":192.35443,"subtask_id":"approach_peg","tcp_end":[0.50555,0.10169,0.04252],"tcp_start":[0.52985,0.11504,0.13994],"tcp_to_object_dist_end":0.04815,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":486.0,"n_steps_budget":600.0,"object_pos_end":[0.50105,-0.00697,0.03383],"object_pos_start":[0.50469,0.05354,0.04221],"object_to_goal_dist_end":0.0733,"object_to_goal_dist_start":0.13365,"object_z_max":0.04272,"peak_contact_force":0.54699,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":451.0,"raw_peak_contact_force":3.60388,"subtask_id":"push_through","tcp_end":[0.50084,0.07059,0.03747],"tcp_start":[0.50555,0.10169,0.04252],"tcp_to_object_dist_end":0.07765,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50696,-0.07763,0.03577],"object_pos_start":[0.50105,-0.00697,0.03383],"object_to_goal_dist_end":0.00848,"object_to_goal_dist_start":0.0733,"object_z_max":0.03622,"peak_contact_force":7.32391,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1601.0,"raw_peak_contact_force":11.80595,"subtask_id":"push_through","tcp_end":[0.496,-0.04984,0.03751],"tcp_start":[0.50084,0.07059,0.03747],"tcp_to_object_dist_end":0.02992,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```