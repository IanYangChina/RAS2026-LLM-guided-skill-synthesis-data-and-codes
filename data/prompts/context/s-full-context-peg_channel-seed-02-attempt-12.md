## Search State

- **Seed**: 2
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.1448 | 0.41 | ❌ rejected |
| 11 | approach → align → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 10 | 0.0287 | 0.26 | ❌ rejected |
| 10 | approach → align → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 9 | 0.2743 | 0.33 | ❌ rejected |
| 9 | approach → align → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | 0.2541 | 0.19 | ❌ rejected |
| 8 | approach → descend → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.1587 | 0.47 | ✅ accepted |

**Proposal policy**: task_score is 0.41 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.145) — your mutation base

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

- **Composite score**: 0.145
- **task_score** (E): 0.407
- **fitness_score**: 0.605  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.2195 |
| descend_to_contact | 1.00 | 1.00 | 0.0617 |
| lateral_align | 1.00 | 1.00 | 0.0168 |
| push_channel | 1.00 | 1.00 | 0.1400 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.492, 0.107, 0.104) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.546 | 3.659 |
| descend_to_contact | descend | 1.00 / step_budget | (0.492, 0.107, 0.104)→(0.499, 0.089, 0.048) | (0.498, 0.068, 0.034)→(0.500, 0.067, 0.032) | 0.148→0.147 | 1.00 / 2.000 | 176.958 | 448.995 |
| lateral_align | align | 1.00 / step_budget | (0.499, 0.089, 0.048)→(0.507, 0.089, 0.039) | (0.500, 0.067, 0.032)→(0.498, 0.053, 0.037) | 0.147→0.133 | 1.00 / 2.000 | 244.220 | 382.617 |
| push_channel | push | 1.00 / time_limit | (0.507, 0.089, 0.039)→(0.498, -0.050, 0.036) | (0.498, 0.053, 0.037)→(0.499, -0.081, 0.033) | 0.133→0.011 | 1.00 / 2.667 | 44.325 | 48.905 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.938
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.641
- phase_score: 0.740
- phase_breakdown.approach_peg_score: 0.297
- phase_breakdown.push_through_score: 0.930

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.701
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.641
- **Median Q (composite search score)**: 0.126
- **K-run variance**: 0.0052
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.292


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64286,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.03563,"approach_peg.approach_y_offset":0.04118,"descend_to_contact.descend_y_offset":0.02999,"lateral_align.align_x_offset":0.02591,"lateral_align.align_y_offset":0.02949,"push_channel.max_push_duration":5.9615,"push_channel.push_distance":0.13697,"push_channel.push_speed":0.09441},"optimized_scores":{"best_composite_score":0.24063,"best_fitness_score":0.70063,"best_task_score":0.64091},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":138.0,"contact_point_centroid":[0.47498,0.10045,0.05987],"force_p95":438.86127,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":466.64394,"mean_force":398.25138,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48509,0.10234,0.05812]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":67.0,"contact_point_centroid":[0.52518,0.09367,0.05997],"force_p95":380.7066,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":415.52458,"mean_force":301.80232,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.50785,0.09355,0.03118]},{"body_a":"peg","body_b":"channel_base_body","contact_count":44.0,"contact_point_centroid":[0.49368,-0.10099,0.03649],"force_p95":39.40204,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.1172,"mean_force":23.26956,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49662,-0.05459,0.03408]},{"body_a":"attachment","body_b":"peg","contact_count":720.0,"contact_point_centroid":[0.49729,0.00459,0.03107],"force_p95":14.30969,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.81206,"mean_force":2.30341,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49979,0.0162,0.03052]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52504,0.09367,0.05999],"force_p95":23.0263,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":26.37183,"mean_force":7.20321,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5069,0.09347,0.03101]},{"body_a":"peg","body_b":"channel_base_body","contact_count":709.0,"contact_point_centroid":[0.49314,-0.0134,0.00984],"force_p95":2.60225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.91942,"mean_force":1.21639,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50021,0.02345,0.03028]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":351.0,"contact_point_centroid":[0.47494,-0.01612,0.03273],"force_p95":1.06386,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.2277,"mean_force":0.48871,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49952,0.01302,0.03054]},{"body_a":"peg","body_b":"channel_base_body","contact_count":691.0,"contact_point_centroid":[0.49543,0.06393,0.00938],"force_p95":0.56583,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55786,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48828,0.15328,0.18723]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49936,0.19858,0.29698]},{"body_a":"peg","body_b":"channel_base_body","contact_count":237.0,"contact_point_centroid":[0.49506,0.06426,0.0094],"force_p95":0.55081,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55315,"mean_force":0.54525,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.50088,0.09452,0.03387]},{"body_a":"peg","body_b":"channel_base_body","contact_count":291.0,"contact_point_centroid":[0.49473,0.06357,0.0094],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55289,"mean_force":0.54531,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48386,0.10323,0.06121]}],"total_contact_groups":11},"final_pose_error":0.01733,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49354,-0.08613,0.03541],"final_tcp_position":[0.49658,-0.05701,0.03424],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":466.64394,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":718.0,"n_steps_budget":1000.0,"object_pos_end":[0.49494,0.06406,0.03397],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14427,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54569,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":719.0,"raw_peak_contact_force":2.44546,"subtask_id":"approach_peg","tcp_end":[0.47879,0.1098,0.08417],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06981,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":291.0,"n_steps_budget":600.0,"object_pos_end":[0.49532,0.06371,0.03401],"object_pos_start":[0.49494,0.06406,0.03397],"object_to_goal_dist_end":0.14391,"object_to_goal_dist_start":0.14427,"object_z_max":0.03401,"peak_contact_force":0.54796,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":429.0,"raw_peak_contact_force":466.64394,"subtask_id":"approach_peg","tcp_end":[0.48907,0.09723,0.04141],"tcp_start":[0.47879,0.1098,0.08417],"tcp_to_object_dist_end":0.03489,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":237.0,"n_steps_budget":600.0,"object_pos_end":[0.49495,0.06362,0.03402],"object_pos_start":[0.49532,0.06371,0.03401],"object_to_goal_dist_end":0.14383,"object_to_goal_dist_start":0.14391,"object_z_max":0.03402,"peak_contact_force":306.65685,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":304.0,"raw_peak_contact_force":415.52458,"subtask_id":"push_through","tcp_end":[0.50696,0.09352,0.03109],"tcp_start":[0.48907,0.09723,0.04141],"tcp_to_object_dist_end":0.03235,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49354,-0.08613,0.03541],"object_pos_start":[0.49495,0.06362,0.03402],"object_to_goal_dist_end":0.01002,"object_to_goal_dist_start":0.14383,"object_z_max":0.03578,"peak_contact_force":39.52458,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1829.0,"raw_peak_contact_force":41.1172,"subtask_id":"push_through","tcp_end":[0.49658,-0.05701,0.03424],"tcp_start":[0.50696,0.09352,0.03109],"tcp_to_object_dist_end":0.0293,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79508,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.07297,"approach_peg.approach_y_offset":0.03291,"descend_to_contact.descend_y_offset":0.00873,"lateral_align.align_x_offset":0.02882,"lateral_align.align_y_offset":0.01487,"push_channel.max_push_duration":3.65625,"push_channel.push_distance":0.17137,"push_channel.push_speed":0.07768},"optimized_scores":{"best_composite_score":0.0679,"best_fitness_score":0.5279,"best_task_score":0.26254},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":269.0,"contact_point_centroid":[0.52514,0.0737,0.05998],"force_p95":463.5567,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":526.01018,"mean_force":375.10656,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.51068,0.07364,0.04779]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":78.0,"contact_point_centroid":[0.47498,0.06936,0.0599],"force_p95":440.90737,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":489.24445,"mean_force":365.00202,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48366,0.07707,0.05846]},{"body_a":"peg","body_b":"channel_base_body","contact_count":372.0,"contact_point_centroid":[0.49792,0.06387,0.00922],"force_p95":187.51403,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":205.07066,"mean_force":35.8926,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.47737,0.08378,0.0778]},{"body_a":"peg","body_b":"channel_base_body","contact_count":333.0,"contact_point_centroid":[0.50994,0.05287,0.00828],"force_p95":186.60879,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":204.76057,"mean_force":108.93364,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.50934,0.07346,0.04805]},{"body_a":"attachment","body_b":"peg","contact_count":136.0,"contact_point_centroid":[0.49816,0.07526,0.05637],"force_p95":200.17897,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":204.54108,"mean_force":96.74392,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48636,0.07639,0.05666]},{"body_a":"attachment","body_b":"peg","contact_count":216.0,"contact_point_centroid":[0.51598,0.06397,0.05157],"force_p95":187.58557,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":204.04958,"mean_force":167.14655,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.50923,0.0731,0.04915]},{"body_a":"attachment","body_b":"peg","contact_count":623.0,"contact_point_centroid":[0.50053,-0.01616,0.03891],"force_p95":63.82581,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.22167,"mean_force":10.06995,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50099,-0.00439,0.03814]},{"body_a":"peg","body_b":"channel_base_body","contact_count":118.0,"contact_point_centroid":[0.50796,-0.10079,0.03532],"force_p95":79.19238,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.44959,"mean_force":47.1604,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49925,-0.04037,0.03737]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52504,0.07443,0.05999],"force_p95":31.7866,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":34.7608,"mean_force":11.15869,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50841,0.07424,0.04409]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":44.0,"contact_point_centroid":[0.52523,0.04167,0.05568],"force_p95":13.94107,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.06168,"mean_force":3.83019,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.5104,0.07355,0.04762]},{"body_a":"peg","body_b":"channel_base_body","contact_count":940.0,"contact_point_centroid":[0.4957,-0.0302,0.0094],"force_p95":3.71962,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.96321,"mean_force":1.19235,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50202,0.01422,0.03866]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":126.0,"contact_point_centroid":[0.47499,-0.04637,0.02747],"force_p95":4.36084,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.19723,"mean_force":2.57767,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50151,0.00658,0.03835]},{"body_a":"peg","body_b":"channel_base_body","contact_count":617.0,"contact_point_centroid":[0.49431,0.05903,0.00936],"force_p95":0.56286,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56992,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48164,0.14699,0.20535]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49891,0.19782,0.2961]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47464,0.04053,0.05819],"force_p95":1.59369,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.72049,"mean_force":0.80762,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.51063,0.07366,0.04834]}],"total_contact_groups":15},"final_pose_error":0.10384,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49546,-0.07783,0.028],"final_tcp_position":[0.499,-0.04362,0.03694],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":526.01018,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":646.0,"n_steps_budget":1000.0,"object_pos_end":[0.49402,0.05887,0.03388],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13913,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54907,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":652.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach_peg","tcp_end":[0.46596,0.09802,0.12047],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09908,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":372.0,"n_steps_budget":630.0,"object_pos_end":[0.50049,0.05668,0.02981],"object_pos_start":[0.49402,0.05887,0.03388],"object_to_goal_dist_end":0.13706,"object_to_goal_dist_start":0.13913,"object_z_max":0.03391,"peak_contact_force":205.03075,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":586.0,"raw_peak_contact_force":489.24445,"subtask_id":"approach_peg","tcp_end":[0.49581,0.07319,0.04905],"tcp_start":[0.46596,0.09802,0.12047],"tcp_to_object_dist_end":0.02578,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":336.0,"n_steps_budget":600.0,"object_pos_end":[0.50195,0.02394,0.03884],"object_pos_start":[0.50049,0.05668,0.02981],"object_to_goal_dist_end":0.10396,"object_to_goal_dist_start":0.13706,"object_z_max":0.0408,"peak_contact_force":406.41391,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":870.0,"raw_peak_contact_force":526.01018,"subtask_id":"push_through","tcp_end":[0.50848,0.07426,0.04419],"tcp_start":[0.49581,0.07319,0.04905],"tcp_to_object_dist_end":0.05103,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49546,-0.07783,0.028],"object_pos_start":[0.50195,0.02394,0.03884],"object_to_goal_dist_end":0.01301,"object_to_goal_dist_start":0.10396,"object_z_max":0.03884,"peak_contact_force":83.16585,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1812.0,"raw_peak_contact_force":83.22167,"subtask_id":"push_through","tcp_end":[0.499,-0.04362,0.03694],"tcp_start":[0.50848,0.07426,0.04419],"tcp_to_object_dist_end":0.03554,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72131,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.05978,"approach_peg.approach_y_offset":0.02861,"descend_to_contact.descend_y_offset":0.00582,"lateral_align.align_x_offset":-0.00373,"lateral_align.align_y_offset":0.02239,"push_channel.max_push_duration":4.60328,"push_channel.push_distance":0.17268,"push_channel.push_speed":0.09249},"optimized_scores":{"best_composite_score":0.12592,"best_fitness_score":0.58592,"best_task_score":0.31705},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":122.0,"contact_point_centroid":[0.52508,0.09678,0.05999],"force_p95":350.27581,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":391.09696,"mean_force":302.88036,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51246,0.09685,0.05514]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":105.0,"contact_point_centroid":[0.52502,0.09804,0.06],"force_p95":108.19506,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":206.31682,"mean_force":66.16815,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.51212,0.0981,0.0515]},{"body_a":"peg","body_b":"channel_base_body","contact_count":157.0,"contact_point_centroid":[0.50791,0.08181,0.00819],"force_p95":150.68088,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":155.62177,"mean_force":100.73741,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.51115,0.09842,0.04996]},{"body_a":"attachment","body_b":"peg","contact_count":128.0,"contact_point_centroid":[0.51529,0.08735,0.05293],"force_p95":153.18445,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":155.15684,"mean_force":122.9645,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.51185,0.09819,0.05107]},{"body_a":"peg","body_b":"channel_base_body","contact_count":284.0,"contact_point_centroid":[0.51116,0.08352,0.00904],"force_p95":109.37469,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":112.92109,"mean_force":42.53384,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51714,0.10192,0.0704]},{"body_a":"attachment","body_b":"peg","contact_count":131.0,"contact_point_centroid":[0.52053,0.08809,0.05574],"force_p95":111.23299,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":112.44338,"mean_force":91.09939,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51244,0.09686,0.05531]},{"body_a":"peg","body_b":"channel_base_body","contact_count":653.0,"contact_point_centroid":[0.49608,-0.01508,0.00985],"force_p95":8.32459,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.37589,"mean_force":2.44016,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49931,0.02481,0.03584]},{"body_a":"attachment","body_b":"peg","contact_count":675.0,"contact_point_centroid":[0.49844,0.01393,0.03857],"force_p95":8.72079,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.22791,"mean_force":2.32326,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49937,0.02554,0.03589]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":13.0,"contact_point_centroid":[0.47444,0.07123,0.05689],"force_p95":8.24072,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.10311,"mean_force":1.95487,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.5098,0.09935,0.04728]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":100.0,"contact_point_centroid":[0.52525,-0.06965,0.03317],"force_p95":8.35402,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.21439,"mean_force":2.09205,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49767,-0.04139,0.0356]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":320.0,"contact_point_centroid":[0.47493,0.01316,0.02931],"force_p95":3.91884,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.72831,"mean_force":0.81787,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49966,0.04215,0.0358]},{"body_a":"peg","body_b":"channel_base_body","contact_count":655.0,"contact_point_centroid":[0.50575,0.08091,0.00936],"force_p95":0.55552,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57006,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51462,0.15533,0.19819]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50007,0.19813,0.29586]}],"total_contact_groups":13},"final_pose_error":0.05132,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50751,-0.07876,0.03547],"final_tcp_position":[0.49753,-0.05066,0.03563],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":391.09696,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":684.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54458,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":691.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach_peg","tcp_end":[0.5299,0.11415,0.10635],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08335,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":284.0,"n_steps_budget":600.0,"object_pos_end":[0.50274,0.07915,0.03212],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.15937,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":325.29452,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":537.0,"raw_peak_contact_force":391.09696,"subtask_id":"approach_peg","tcp_end":[0.5124,0.09697,0.05366],"tcp_start":[0.5299,0.11415,0.10635],"tcp_to_object_dist_end":0.02958,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":157.0,"n_steps_budget":600.0,"object_pos_end":[0.49782,0.07096,0.03822],"object_pos_start":[0.50274,0.07915,0.03212],"object_to_goal_dist_end":0.15098,"object_to_goal_dist_start":0.15937,"object_z_max":0.03819,"peak_contact_force":19.58911,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":403.0,"raw_peak_contact_force":206.31682,"subtask_id":"push_through","tcp_end":[0.50453,0.0997,0.04023],"tcp_start":[0.5124,0.09697,0.05366],"tcp_to_object_dist_end":0.02958,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50751,-0.07876,0.03547],"object_pos_start":[0.49782,0.07096,0.03822],"object_to_goal_dist_end":0.00886,"object_to_goal_dist_start":0.15098,"object_z_max":0.03889,"peak_contact_force":10.28368,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1748.0,"raw_peak_contact_force":22.37589,"subtask_id":"push_through","tcp_end":[0.49753,-0.05066,0.03563],"tcp_start":[0.50453,0.0997,0.04023],"tcp_to_object_dist_end":0.02982,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```