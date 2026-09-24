## Search State

- **Seed**: 2
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.1587 | 0.47 | ✅ accepted |
| 7 | approach → descend → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | 0.0610 | 0.41 | ✅ accepted |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 8 | 0.1209 | 0.27 | ❌ rejected |
| 5 | approach → descend → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.0672 | 0.34 | ✅ accepted |
| 4 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 6 | 0.2158 | 0.27 | ❌ rejected |

**Proposal policy**: task_score is 0.47 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.159) — your mutation base

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

- **Composite score**: 0.159
- **task_score** (E): 0.472
- **fitness_score**: 0.619  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.2061 |
| descend_to_contact | 1.00 | 1.00 | 0.0754 |
| lateral_align | 1.00 | 1.00 | 0.0269 |
| push_channel | 1.00 | 1.00 | 0.1311 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.492, 0.111, 0.117) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.546 | 3.659 |
| descend_to_contact | descend | 1.00 / step_budget | (0.492, 0.111, 0.117)→(0.493, 0.091, 0.047) | (0.498, 0.068, 0.034)→(0.499, 0.061, 0.037) | 0.148→0.141 | 1.00 / 1.667 | 130.757 | 211.559 |
| lateral_align | align | 1.00 / step_budget | (0.493, 0.091, 0.047)→(0.499, 0.078, 0.035) | (0.499, 0.061, 0.037)→(0.501, 0.047, 0.036) | 0.141→0.127 | 1.00 / 2.667 | 137.954 | 339.494 |
| push_channel | push | 1.00 / time_limit | (0.499, 0.078, 0.035)→(0.494, -0.053, 0.033) | (0.501, 0.047, 0.036)→(0.501, -0.076, 0.033) | 0.127→0.015 | 1.00 / 2.333 | 14.297 | 81.695 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.939
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.648
- phase_score: 0.730
- phase_breakdown.approach_peg_score: 0.307
- phase_breakdown.push_through_score: 0.912

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.697
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.648
- **Median Q (composite search score)**: 0.121
- **K-run variance**: 0.0031
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.330


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.08521,"approach_peg.approach_y_offset":0.03672,"descend_to_contact.descend_y_offset":0.02316,"lateral_align.align_x_offset":0.04322,"lateral_align.align_y_offset":-0.009,"push_channel.max_push_duration":4.30371,"push_channel.push_distance":0.17149,"push_channel.push_speed":0.07783},"optimized_scores":{"best_composite_score":0.23739,"best_fitness_score":0.69739,"best_task_score":0.64815},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":260.0,"contact_point_centroid":[0.52513,0.07009,0.05997],"force_p95":482.9167,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":531.96365,"mean_force":349.54197,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.50603,0.0699,0.03266]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":46.0,"contact_point_centroid":[0.54465,0.06524,0.05989],"force_p95":497.71911,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":512.55005,"mean_force":432.73699,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.50263,0.06816,0.0318]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":482.0,"contact_point_centroid":[0.54241,0.02884,0.05999],"force_p95":85.83067,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":95.67993,"mean_force":63.80751,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49996,0.03259,0.03277]},{"body_a":"peg","body_b":"channel_base_body","contact_count":309.0,"contact_point_centroid":[0.49597,0.06163,0.00943],"force_p95":0.69064,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":75.40197,"mean_force":1.5646,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48317,0.09787,0.08774]},{"body_a":"attachment","body_b":"peg","contact_count":27.0,"contact_point_centroid":[0.49272,0.07914,0.05719],"force_p95":67.56525,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":75.03482,"mean_force":11.95374,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48851,0.09026,0.0493]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":23.0,"contact_point_centroid":[0.52507,0.06831,0.05997],"force_p95":66.20508,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":66.74316,"mean_force":40.30652,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50245,0.06801,0.03255]},{"body_a":"peg","body_b":"channel_base_body","contact_count":64.0,"contact_point_centroid":[0.49334,-0.10096,0.03712],"force_p95":39.81641,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.32352,"mean_force":21.23766,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49499,-0.05424,0.03394]},{"body_a":"attachment","body_b":"peg","contact_count":477.0,"contact_point_centroid":[0.49756,-0.01286,0.03494],"force_p95":26.4536,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.67777,"mean_force":4.10353,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49792,-0.00111,0.03307]},{"body_a":"attachment","body_b":"peg","contact_count":216.0,"contact_point_centroid":[0.50467,0.06393,0.0422],"force_p95":19.55539,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.79373,"mean_force":4.20963,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.50219,0.07566,0.0347]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":182.0,"contact_point_centroid":[0.52523,0.04463,0.03605],"force_p95":14.14414,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.43234,"mean_force":3.43847,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.50316,0.07438,0.03398]},{"body_a":"peg","body_b":"channel_base_body","contact_count":783.0,"contact_point_centroid":[0.49774,-0.02559,0.00969],"force_p95":3.76869,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.09195,"mean_force":1.169,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49867,0.01151,0.03293]},{"body_a":"peg","body_b":"channel_base_body","contact_count":418.0,"contact_point_centroid":[0.50501,0.03636,0.00965],"force_p95":9.32253,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.74872,"mean_force":1.7701,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.50328,0.0734,0.03393]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":274.0,"contact_point_centroid":[0.47483,-0.02512,0.03417],"force_p95":1.96392,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.73134,"mean_force":0.6339,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49833,0.00479,0.03299]},{"body_a":"peg","body_b":"channel_base_body","contact_count":570.0,"contact_point_centroid":[0.4953,0.06391,0.00937],"force_p95":0.58008,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56048,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48855,0.15164,0.21195]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.4993,0.19833,0.29713]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":30.0,"contact_point_centroid":[0.52513,0.03623,0.02836],"force_p95":0.46354,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47301,"mean_force":0.2628,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50193,0.06614,0.03261]}],"total_contact_groups":16},"final_pose_error":0.07674,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49335,-0.08643,0.03519],"final_tcp_position":[0.49495,-0.05721,0.03408],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":531.96365,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":597.0,"n_steps_budget":1000.0,"object_pos_end":[0.49508,0.06366,0.03395],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14387,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54286,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":598.0,"raw_peak_contact_force":2.44546,"subtask_id":"approach_peg","tcp_end":[0.47928,0.10671,0.13264],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10883,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":316.0,"n_steps_budget":660.0,"object_pos_end":[0.49896,0.05925,0.03424],"object_pos_start":[0.49508,0.06366,0.03395],"object_to_goal_dist_end":0.13937,"object_to_goal_dist_start":0.14387,"object_z_max":0.03667,"peak_contact_force":0.70956,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":336.0,"raw_peak_contact_force":75.40197,"subtask_id":"approach_peg","tcp_end":[0.48958,0.08877,0.0418],"tcp_start":[0.47928,0.10671,0.13264],"tcp_to_object_dist_end":0.03189,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":462.0,"n_steps_budget":600.0,"object_pos_end":[0.5069,0.03754,0.03397],"object_pos_start":[0.49896,0.05925,0.03424],"object_to_goal_dist_end":0.11789,"object_to_goal_dist_start":0.13937,"object_z_max":0.03611,"peak_contact_force":404.34525,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1122.0,"raw_peak_contact_force":531.96365,"subtask_id":"push_through","tcp_end":[0.50236,0.06804,0.03241],"tcp_start":[0.48958,0.08877,0.0418],"tcp_to_object_dist_end":0.03088,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49335,-0.08643,0.03519],"object_pos_start":[0.5069,0.03754,0.03397],"object_to_goal_dist_end":0.01042,"object_to_goal_dist_start":0.11789,"object_z_max":0.03686,"peak_contact_force":39.98714,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2133.0,"raw_peak_contact_force":95.67993,"subtask_id":"push_through","tcp_end":[0.49495,-0.05721,0.03408],"tcp_start":[0.50236,0.06804,0.03241],"tcp_to_object_dist_end":0.02929,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79032,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.05936,"approach_peg.approach_y_offset":0.03009,"descend_to_contact.descend_y_offset":0.01653,"lateral_align.align_x_offset":0.02085,"lateral_align.align_y_offset":0.01794,"push_channel.max_push_duration":3.44954,"push_channel.push_distance":0.19255,"push_channel.push_speed":0.07559},"optimized_scores":{"best_composite_score":0.12104,"best_fitness_score":0.58104,"best_task_score":0.29617},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":150.0,"contact_point_centroid":[0.47499,0.08446,0.05992],"force_p95":442.14197,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":474.65007,"mean_force":398.21075,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48188,0.08291,0.05861]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":66.0,"contact_point_centroid":[0.47498,0.08617,0.05992],"force_p95":411.13425,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":457.49729,"mean_force":365.34194,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.48559,0.08162,0.05734]},{"body_a":"peg","body_b":"channel_base_body","contact_count":342.0,"contact_point_centroid":[0.49662,0.05749,0.00949],"force_p95":41.6475,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.08374,"mean_force":8.51763,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.4761,0.08629,0.07219]},{"body_a":"attachment","body_b":"peg","contact_count":120.0,"contact_point_centroid":[0.48945,0.0743,0.05918],"force_p95":42.1889,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.60374,"mean_force":22.85612,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48159,0.08291,0.05868]},{"body_a":"attachment","body_b":"peg","contact_count":113.0,"contact_point_centroid":[0.49543,0.06773,0.0486],"force_p95":12.77748,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.18107,"mean_force":4.39602,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.49345,0.07923,0.04807]},{"body_a":"peg","body_b":"channel_base_body","contact_count":226.0,"contact_point_centroid":[0.50062,0.0399,0.00983],"force_p95":12.11038,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.10038,"mean_force":2.62843,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.49325,0.07928,0.04852]},{"body_a":"attachment","body_b":"peg","contact_count":698.0,"contact_point_centroid":[0.49851,0.00114,0.03351],"force_p95":2.2108,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.56542,"mean_force":0.95155,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5013,0.01271,0.03282]},{"body_a":"peg","body_b":"channel_base_body","contact_count":786.0,"contact_point_centroid":[0.49347,-0.02221,0.00987],"force_p95":2.57449,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.44031,"mean_force":1.15041,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50147,0.01575,0.03279]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52503,0.07533,0.05999],"force_p95":4.4171,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5.19659,"mean_force":1.29915,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50698,0.07528,0.03498]},{"body_a":"peg","body_b":"channel_base_body","contact_count":657.0,"contact_point_centroid":[0.49431,0.05889,0.00936],"force_p95":0.56089,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56846,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48155,0.1455,0.19859]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49895,0.19787,0.29606]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":322.0,"contact_point_centroid":[0.47493,-0.02138,0.03421],"force_p95":1.0967,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.37453,"mean_force":0.43543,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5011,0.00738,0.03297]}],"total_contact_groups":12},"final_pose_error":0.09829,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49295,-0.07711,0.0351],"final_tcp_position":[0.49938,-0.0479,0.03491],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":474.65007,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":686.0,"n_steps_budget":1000.0,"object_pos_end":[0.49426,0.05895,0.03389],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.1392,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54784,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":692.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach_peg","tcp_end":[0.46579,0.09504,0.10716],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0865,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":342.0,"n_steps_budget":600.0,"object_pos_end":[0.49606,0.0564,0.03569],"object_pos_start":[0.49426,0.05895,0.03389],"object_to_goal_dist_end":0.13653,"object_to_goal_dist_start":0.1392,"object_z_max":0.03586,"peak_contact_force":391.07655,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":612.0,"raw_peak_contact_force":474.65007,"subtask_id":"approach_peg","tcp_end":[0.48392,0.08288,0.05813],"tcp_start":[0.46579,0.09504,0.10716],"tcp_to_object_dist_end":0.03677,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":239.0,"n_steps_budget":600.0,"object_pos_end":[0.49905,0.04648,0.03374],"object_pos_start":[0.49606,0.0564,0.03569],"object_to_goal_dist_end":0.12664,"object_to_goal_dist_start":0.13653,"object_z_max":0.03769,"peak_contact_force":9.35327,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":405.0,"raw_peak_contact_force":457.49729,"subtask_id":"push_through","tcp_end":[0.507,0.07535,0.0351],"tcp_start":[0.48392,0.08288,0.05813],"tcp_to_object_dist_end":0.02998,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49295,-0.07711,0.0351],"object_pos_start":[0.49905,0.04648,0.03374],"object_to_goal_dist_end":0.00906,"object_to_goal_dist_start":0.12664,"object_z_max":0.03568,"peak_contact_force":1.41319,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1810.0,"raw_peak_contact_force":6.56542,"subtask_id":"push_through","tcp_end":[0.49938,-0.0479,0.03491],"tcp_start":[0.507,0.07535,0.0351],"tcp_to_object_dist_end":0.02991,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80833,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.0637,"approach_peg.approach_y_offset":0.04803,"descend_to_contact.descend_y_offset":0.01504,"lateral_align.align_x_offset":-0.02016,"lateral_align.align_y_offset":0.0184,"push_channel.max_push_duration":3.11795,"push_channel.push_distance":0.13714,"push_channel.push_speed":0.08978},"optimized_scores":{"best_composite_score":0.11753,"best_fitness_score":0.57753,"best_task_score":0.47237},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":951.0,"contact_point_centroid":[0.49588,0.0176,0.03178],"force_p95":128.91823,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":142.83912,"mean_force":73.67697,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48687,0.02205,0.03295]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":880.0,"contact_point_centroid":[0.52652,0.00543,0.02679],"force_p95":125.37545,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":135.3494,"mean_force":70.3616,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48686,0.01698,0.03276]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":442.0,"contact_point_centroid":[0.47499,0.02445,0.03503],"force_p95":96.51126,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":115.35946,"mean_force":53.82483,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48681,0.02446,0.03298]},{"body_a":"peg","body_b":"channel_base_body","contact_count":233.0,"contact_point_centroid":[0.50502,0.07697,0.00945],"force_p95":0.56059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.62533,"mean_force":1.84895,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.5177,0.11751,0.07632]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.51123,0.09738,0.05804],"force_p95":84.03566,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":84.17387,"mean_force":34.44858,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51158,0.109,0.05786]},{"body_a":"peg","body_b":"channel_base_body","contact_count":941.0,"contact_point_centroid":[0.50657,0.00535,0.00953],"force_p95":49.68946,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":57.2275,"mean_force":27.63041,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48686,0.02596,0.03309]},{"body_a":"attachment","body_b":"peg","contact_count":48.0,"contact_point_centroid":[0.49874,0.08411,0.038],"force_p95":27.95485,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.02242,"mean_force":14.12191,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.49547,0.09534,0.03839]},{"body_a":"peg","body_b":"channel_base_body","contact_count":81.0,"contact_point_centroid":[0.4993,0.06183,0.00995],"force_p95":21.22245,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.186,"mean_force":7.59356,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.49755,0.09638,0.03889]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":26.0,"contact_point_centroid":[0.47463,0.04877,0.05706],"force_p95":18.00612,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.3457,"mean_force":10.12609,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.49481,0.09507,0.03831]},{"body_a":"peg","body_b":"channel_base_body","contact_count":614.0,"contact_point_centroid":[0.50576,0.0809,0.00936],"force_p95":0.55691,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57162,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51458,0.16485,0.20052]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50011,0.19839,0.29578]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":29.0,"contact_point_centroid":[0.47495,0.04033,0.05687],"force_p95":1.84991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.9463,"mean_force":0.43785,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48706,0.08565,0.03556]}],"total_contact_groups":12},"final_pose_error":0.0312,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.51736,-0.06446,0.02802],"final_tcp_position":[0.48776,-0.0531,0.03097],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":142.83912,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":643.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54612,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":650.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach_peg","tcp_end":[0.52981,0.13264,0.11088],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09588,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":234.0,"n_steps_budget":600.0,"object_pos_end":[0.50176,0.06623,0.04061],"object_pos_start":[0.50597,0.08086,0.03378],"object_to_goal_dist_end":0.14624,"object_to_goal_dist_start":0.16109,"object_z_max":0.04059,"peak_contact_force":0.48478,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":242.0,"raw_peak_contact_force":84.62533,"subtask_id":"approach_peg","tcp_end":[0.50642,0.10136,0.04181],"tcp_start":[0.52981,0.13264,0.11088],"tcp_to_object_dist_end":0.03546,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":84.0,"n_steps_budget":600.0,"object_pos_end":[0.49734,0.05678,0.04079],"object_pos_start":[0.50176,0.06623,0.04061],"object_to_goal_dist_end":0.13681,"object_to_goal_dist_start":0.14624,"object_z_max":0.04083,"peak_contact_force":0.16331,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":155.0,"raw_peak_contact_force":29.02242,"subtask_id":"push_through","tcp_end":[0.48828,0.09119,0.03748],"tcp_start":[0.50642,0.10136,0.04181],"tcp_to_object_dist_end":0.03573,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51736,-0.06446,0.02802],"object_pos_start":[0.49734,0.05678,0.04079],"object_to_goal_dist_end":0.0262,"object_to_goal_dist_start":0.13681,"object_z_max":0.04089,"peak_contact_force":1.48998,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3243.0,"raw_peak_contact_force":142.83912,"subtask_id":"push_through","tcp_end":[0.48776,-0.0531,0.03097],"tcp_start":[0.48828,0.09119,0.03748],"tcp_to_object_dist_end":0.03185,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```