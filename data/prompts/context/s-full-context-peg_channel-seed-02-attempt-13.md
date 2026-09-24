## Search State

- **Seed**: 2
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.1589 | 0.44 | ❌ rejected |
| 12 | approach → descend → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.1448 | 0.41 | ❌ rejected |
| 11 | approach → align → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 10 | 0.0287 | 0.26 | ❌ rejected |
| 10 | approach → align → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 9 | 0.2743 | 0.33 | ❌ rejected |
| 9 | approach → align → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | 0.2541 | 0.19 | ❌ rejected |

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
- **task_score** (E): 0.439
- **fitness_score**: 0.619  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1959 |
| descend_to_contact | 1.00 | 1.00 | 0.0855 |
| lateral_align | 1.00 | 1.00 | 0.0217 |
| push_channel | 1.00 | 1.00 | 0.1486 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.492, 0.110, 0.129) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.547 | 3.659 |
| descend_to_contact | descend | 1.00 / step_budget | (0.492, 0.110, 0.129)→(0.503, 0.088, 0.050) | (0.498, 0.068, 0.034)→(0.502, 0.065, 0.031) | 0.148→0.146 | 1.00 / 2.333 | 235.517 | 334.607 |
| lateral_align | align | 1.00 / step_budget | (0.503, 0.088, 0.050)→(0.503, 0.091, 0.036) | (0.502, 0.065, 0.031)→(0.503, 0.056, 0.037) | 0.146→0.136 | 1.00 / 2.000 | 320.358 | 449.675 |
| push_channel | push | 1.00 / time_limit | (0.503, 0.091, 0.036)→(0.495, -0.057, 0.034) | (0.503, 0.056, 0.037)→(0.500, -0.081, 0.037) | 0.136→0.012 | 1.00 / 3.000 | 1381.714 | 74.729 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.923
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.625
- phase_score: 0.756
- phase_breakdown.approach_peg_score: 0.329
- phase_breakdown.push_through_score: 0.940

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.704
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.625
- **Median Q (composite search score)**: 0.126
- **K-run variance**: 0.0037
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.356


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.74167,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.0753,"approach_peg.approach_y_offset":0.03236,"descend_to_contact.descend_y_offset":0.01677,"lateral_align.align_x_offset":0.01922,"lateral_align.align_y_offset":0.03084,"push_channel.max_push_duration":3.12004,"push_channel.push_distance":0.18758,"push_channel.push_speed":0.0931},"optimized_scores":{"best_composite_score":0.24403,"best_fitness_score":0.70403,"best_task_score":0.6255},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":116.0,"contact_point_centroid":[0.52515,0.09259,0.05998],"force_p95":556.98046,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":563.84763,"mean_force":438.15466,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.51092,0.09265,0.04059]},{"body_a":"peg","body_b":"channel_base_body","contact_count":331.0,"contact_point_centroid":[0.49918,0.06815,0.00904],"force_p95":198.93626,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":201.39031,"mean_force":51.37706,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48562,0.09213,0.07856]},{"body_a":"attachment","body_b":"peg","contact_count":111.0,"contact_point_centroid":[0.50342,0.08003,0.05422],"force_p95":198.7485,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":200.90514,"mean_force":151.63872,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.49345,0.08631,0.05308]},{"body_a":"peg","body_b":"channel_base_body","contact_count":173.0,"contact_point_centroid":[0.50482,0.06077,0.00871],"force_p95":182.79163,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":191.97034,"mean_force":52.38619,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.50966,0.09088,0.04297]},{"body_a":"attachment","body_b":"peg","contact_count":63.0,"contact_point_centroid":[0.50946,0.07654,0.05256],"force_p95":186.97061,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":191.3977,"mean_force":142.30597,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.50772,0.08717,0.0484]},{"body_a":"peg","body_b":"channel_base_body","contact_count":28.0,"contact_point_centroid":[0.49332,-0.10039,0.04822],"force_p95":23.01664,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.95116,"mean_force":14.57623,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49849,-0.05291,0.03506]},{"body_a":"attachment","body_b":"peg","contact_count":551.0,"contact_point_centroid":[0.4991,0.00221,0.03414],"force_p95":9.37717,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.59271,"mean_force":1.95075,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50176,0.01371,0.03338]},{"body_a":"peg","body_b":"channel_base_body","contact_count":721.0,"contact_point_centroid":[0.49687,-0.01276,0.00975],"force_p95":3.94638,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.22916,"mean_force":1.22323,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5024,0.02379,0.03329]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52507,0.06667,0.05596],"force_p95":6.83081,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.9529,"mean_force":3.85799,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.51176,0.08871,0.04847]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":426.0,"contact_point_centroid":[0.47489,-0.00939,0.02997],"force_p95":1.76994,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.3465,"mean_force":0.62168,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50195,0.01913,0.03313]},{"body_a":"peg","body_b":"channel_base_body","contact_count":603.0,"contact_point_centroid":[0.49549,0.06391,0.00937],"force_p95":0.5719,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55966,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48848,0.14938,0.2069]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49932,0.19833,0.29712]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.09472,0.06],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50941,0.09465,0.03581]}],"total_contact_groups":13},"final_pose_error":0.07458,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49371,-0.08378,0.03598],"final_tcp_position":[0.49839,-0.05466,0.03507],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":563.84763,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":630.0,"n_steps_budget":1000.0,"object_pos_end":[0.49502,0.06408,0.03396],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14429,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54436,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":631.0,"raw_peak_contact_force":2.44546,"subtask_id":"approach_peg","tcp_end":[0.47916,0.10236,0.12289],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09812,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":331.0,"n_steps_budget":600.0,"object_pos_end":[0.50125,0.06155,0.03117],"object_pos_start":[0.49502,0.06408,0.03396],"object_to_goal_dist_end":0.14184,"object_to_goal_dist_start":0.14429,"object_z_max":0.03405,"peak_contact_force":198.27956,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":442.0,"raw_peak_contact_force":201.39031,"subtask_id":"approach_peg","tcp_end":[0.50102,0.08506,0.04816],"tcp_start":[0.47916,0.10236,0.12289],"tcp_to_object_dist_end":0.029,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":173.0,"n_steps_budget":600.0,"object_pos_end":[0.50333,0.05845,0.03486],"object_pos_start":[0.50125,0.06155,0.03117],"object_to_goal_dist_end":0.13859,"object_to_goal_dist_start":0.14184,"object_z_max":0.03627,"peak_contact_force":491.52964,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":360.0,"raw_peak_contact_force":563.84763,"subtask_id":"push_through","tcp_end":[0.50941,0.09465,0.03581],"tcp_start":[0.50102,0.08506,0.04816],"tcp_to_object_dist_end":0.03672,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49371,-0.08378,0.03598],"object_pos_start":[0.50333,0.05845,0.03486],"object_to_goal_dist_end":0.00837,"object_to_goal_dist_start":0.13859,"object_z_max":0.0364,"peak_contact_force":23.95116,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1727.0,"raw_peak_contact_force":23.95116,"subtask_id":"push_through","tcp_end":[0.49839,-0.05466,0.03507],"tcp_start":[0.50941,0.09465,0.03581],"tcp_to_object_dist_end":0.02951,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79508,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.0858,"approach_peg.approach_y_offset":0.03369,"descend_to_contact.descend_y_offset":0.01555,"lateral_align.align_x_offset":0.01954,"lateral_align.align_y_offset":0.0249,"push_channel.max_push_duration":2.0145,"push_channel.push_distance":0.18434,"push_channel.push_speed":0.09065},"optimized_scores":{"best_composite_score":0.1063,"best_fitness_score":0.5663,"best_task_score":0.31299},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":92.0,"contact_point_centroid":[0.52515,0.08386,0.05998],"force_p95":540.71867,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":556.80288,"mean_force":436.61632,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.51056,0.08389,0.0414]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":77.0,"contact_point_centroid":[0.47498,0.07571,0.05989],"force_p95":429.86531,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":447.2191,"mean_force":370.57856,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.4852,0.08122,0.05822]},{"body_a":"peg","body_b":"channel_base_body","contact_count":399.0,"contact_point_centroid":[0.49687,0.06359,0.00927],"force_p95":180.04118,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":196.93755,"mean_force":29.7544,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.47733,0.08744,0.08391]},{"body_a":"attachment","body_b":"peg","contact_count":126.0,"contact_point_centroid":[0.49792,0.07674,0.05663],"force_p95":191.5036,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":196.44048,"mean_force":92.5555,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48688,0.08106,0.05692]},{"body_a":"peg","body_b":"channel_base_body","contact_count":185.0,"contact_point_centroid":[0.50568,0.05937,0.00847],"force_p95":177.4892,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":185.23757,"mean_force":76.41443,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.50772,0.08264,0.04521]},{"body_a":"attachment","body_b":"peg","contact_count":94.0,"contact_point_centroid":[0.50892,0.07119,0.05286],"force_p95":179.76751,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":184.65536,"mean_force":149.32247,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.50512,0.08136,0.04944]},{"body_a":"attachment","body_b":"peg","contact_count":627.0,"contact_point_centroid":[0.49885,-0.00289,0.03567],"force_p95":34.02006,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.38368,"mean_force":4.41392,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50208,0.00849,0.03509]},{"body_a":"peg","body_b":"channel_base_body","contact_count":65.0,"contact_point_centroid":[0.49373,-0.10168,0.03589],"force_p95":47.40081,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.15109,"mean_force":29.82531,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49895,-0.05635,0.03617]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52507,0.08467,0.05999],"force_p95":20.16166,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":21.7239,"mean_force":7.12732,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50935,0.08462,0.03814]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":537.0,"contact_point_centroid":[0.47488,-0.01471,0.03056],"force_p95":1.86349,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.63379,"mean_force":0.6631,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50221,0.01367,0.03486]},{"body_a":"peg","body_b":"channel_base_body","contact_count":666.0,"contact_point_centroid":[0.49556,-0.02028,0.00983],"force_p95":4.76442,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.615,"mean_force":1.4828,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50259,0.01683,0.03508]},{"body_a":"peg","body_b":"channel_base_body","contact_count":584.0,"contact_point_centroid":[0.49432,0.05903,0.00936],"force_p95":0.56559,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.57126,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48176,0.1476,0.21192]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":11.0,"contact_point_centroid":[0.52503,0.06033,0.05584],"force_p95":3.29159,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.4601,"mean_force":1.58659,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.51148,0.08266,0.04886]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49888,0.19775,0.29617]}],"total_contact_groups":14},"final_pose_error":0.07085,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49342,-0.08828,0.03544],"final_tcp_position":[0.49889,-0.0596,0.0362],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":556.80288,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":613.0,"n_steps_budget":1000.0,"object_pos_end":[0.49403,0.05886,0.03388],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13913,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.5499,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":619.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach_peg","tcp_end":[0.46618,0.09919,0.13319],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11074,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":399.0,"n_steps_budget":690.0,"object_pos_end":[0.49939,0.0573,0.03159],"object_pos_start":[0.49403,0.05886,0.03388],"object_to_goal_dist_end":0.13756,"object_to_goal_dist_start":0.13913,"object_z_max":0.03395,"peak_contact_force":196.54904,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":602.0,"raw_peak_contact_force":447.2191,"subtask_id":"approach_peg","tcp_end":[0.49495,0.07975,0.05002],"tcp_start":[0.46618,0.09919,0.13319],"tcp_to_object_dist_end":0.02939,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":185.0,"n_steps_budget":600.0,"object_pos_end":[0.50189,0.05396,0.03407],"object_pos_start":[0.49939,0.0573,0.03159],"object_to_goal_dist_end":0.1341,"object_to_goal_dist_start":0.13756,"object_z_max":0.03537,"peak_contact_force":468.99524,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":382.0,"raw_peak_contact_force":556.80288,"subtask_id":"push_through","tcp_end":[0.50945,0.08466,0.03823],"tcp_start":[0.49495,0.07975,0.05002],"tcp_to_object_dist_end":0.0319,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49342,-0.08828,0.03544],"object_pos_start":[0.50189,0.05396,0.03407],"object_to_goal_dist_end":0.01152,"object_to_goal_dist_start":0.1341,"object_z_max":0.03599,"peak_contact_force":49.38368,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1900.0,"raw_peak_contact_force":49.38368,"subtask_id":"push_through","tcp_end":[0.49889,-0.0596,0.0362],"tcp_start":[0.50945,0.08466,0.03823],"tcp_to_object_dist_end":0.02921,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80833,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.08401,"approach_peg.approach_y_offset":0.04279,"descend_to_contact.descend_y_offset":0.01012,"lateral_align.align_x_offset":-0.02329,"lateral_align.align_y_offset":0.01583,"push_channel.max_push_duration":4.52302,"push_channel.push_distance":0.15382,"push_channel.push_speed":0.09964},"optimized_scores":{"best_composite_score":0.12631,"best_fitness_score":0.58631,"best_task_score":0.37887},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":59.0,"contact_point_centroid":[0.52516,0.09875,0.05998],"force_p95":332.8622,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":355.21032,"mean_force":267.89264,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51218,0.09886,0.05153]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52505,0.09878,0.05999],"force_p95":192.39333,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":228.37424,"mean_force":68.11809,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.51197,0.09888,0.051]},{"body_a":"peg","body_b":"channel_base_body","contact_count":339.0,"contact_point_centroid":[0.50964,0.08302,0.009],"force_p95":143.43296,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":156.97241,"mean_force":40.83699,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51687,0.11031,0.0816]},{"body_a":"attachment","body_b":"peg","contact_count":112.0,"contact_point_centroid":[0.5191,0.09044,0.05441],"force_p95":145.00979,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":156.06472,"mean_force":122.01279,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.5115,0.09957,0.05342]},{"body_a":"attachment","body_b":"peg","contact_count":942.0,"contact_point_centroid":[0.49614,0.00818,0.03061],"force_p95":125.18246,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":150.85085,"mean_force":64.90558,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48775,0.01446,0.03142]},{"body_a":"attachment","body_b":"peg","contact_count":66.0,"contact_point_centroid":[0.51414,0.0878,0.05281],"force_p95":141.42415,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":147.33803,"mean_force":114.21788,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.5109,0.09856,0.05096]},{"body_a":"peg","body_b":"channel_base_body","contact_count":139.0,"contact_point_centroid":[0.50332,0.07076,0.00871],"force_p95":139.60249,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":147.17653,"mean_force":54.66545,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.50483,0.09761,0.04624]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":817.0,"contact_point_centroid":[0.52604,-0.00918,0.02442],"force_p95":114.59901,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":128.04474,"mean_force":59.50838,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48781,0.005,0.03142]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":68.0,"contact_point_centroid":[0.47498,-0.04984,0.03226],"force_p95":99.10209,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":102.23319,"mean_force":74.71612,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48681,-0.04982,0.03036]},{"body_a":"peg","body_b":"channel_base_body","contact_count":83.0,"contact_point_centroid":[0.5116,-0.10072,0.03965],"force_p95":72.08721,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":81.18692,"mean_force":46.25236,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48683,-0.05165,0.0303]},{"body_a":"peg","body_b":"channel_base_body","contact_count":963.0,"contact_point_centroid":[0.5061,-0.00996,0.00973],"force_p95":54.86063,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":76.32248,"mean_force":28.74587,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48775,0.01611,0.03144]},{"body_a":"peg","body_b":"link7","contact_count":650.0,"contact_point_centroid":[0.50672,-0.02196,0.07031],"force_p95":24.60914,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.84333,"mean_force":5.37986,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48769,0.00981,0.03132]},{"body_a":"peg","body_b":"channel_base_body","contact_count":567.0,"contact_point_centroid":[0.50574,0.08087,0.00936],"force_p95":0.55737,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57368,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.5146,0.1625,0.21063]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50015,0.19821,0.2959]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.47481,0.0628,0.05774],"force_p95":1.33049,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.42382,"mean_force":0.72592,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.50669,0.09803,0.04789]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52515,0.04207,0.05765],"force_p95":0.44283,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45869,"mean_force":0.33282,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.49043,0.09515,0.03525]}],"total_contact_groups":16},"final_pose_error":0.04505,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.51202,-0.07142,0.0384],"final_tcp_position":[0.48686,-0.05634,0.03017],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":4071.80599,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":596.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54818,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":603.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach_peg","tcp_end":[0.52979,0.12817,0.13076],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11051,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":339.0,"n_steps_budget":690.0,"object_pos_end":[0.50415,0.07754,0.03057],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.15788,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":311.72118,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":510.0,"raw_peak_contact_force":355.21032,"subtask_id":"approach_peg","tcp_end":[0.5121,0.099,0.05109],"tcp_start":[0.52979,0.12817,0.13076],"tcp_to_object_dist_end":0.03073,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":140.0,"n_steps_budget":600.0,"object_pos_end":[0.50357,0.0553,0.04061],"object_pos_start":[0.50415,0.07754,0.03057],"object_to_goal_dist_end":0.13535,"object_to_goal_dist_start":0.15788,"object_z_max":0.04079,"peak_contact_force":0.54974,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":223.0,"raw_peak_contact_force":228.37424,"subtask_id":"push_through","tcp_end":[0.48966,0.095,0.0347],"tcp_start":[0.5121,0.099,0.05109],"tcp_to_object_dist_end":0.04248,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51202,-0.07142,0.0384],"object_pos_start":[0.50357,0.0553,0.04061],"object_to_goal_dist_end":0.01485,"object_to_goal_dist_start":0.13535,"object_z_max":0.04132,"peak_contact_force":4071.80599,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3523.0,"raw_peak_contact_force":150.85085,"subtask_id":"push_through","tcp_end":[0.48686,-0.05634,0.03017],"tcp_start":[0.48966,0.095,0.0347],"tcp_to_object_dist_end":0.03046,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```